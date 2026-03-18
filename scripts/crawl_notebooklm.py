"""
crawl_notebooklm.py - NotebookLM から差分ソースを検出する。

使い方:
    python scripts/crawl_notebooklm.py

処理:
    1. config/notebooklm.yaml から対象ノートブック一覧を読み込む
    2. 各ノートブックの nlm source list を実行しソース一覧を取得
    3. config/notebooklm_last_sync.json と照合し、新規ソースのみ抽出
    4. 新規ソースの情報をJSON形式で標準出力に出力
    5. 同期済みソースIDを notebooklm_last_sync.json に保存

前提:
    - nlm コマンド (notebooklm-mcp-cli) がPATHにあること
    - nlm login 済み（認証済みプロファイル: default）
    - Windows環境では PYTHONIOENCODING=utf-8 が必要

依存パッケージ:
    pip install pyyaml
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "notebooklm.yaml"
INDEX_PATH = REPO_ROOT / "index.json"

JST = timezone(timedelta(hours=9))

# nlm コマンドのパス（Windows環境）
NLM_PATH = Path.home() / ".local" / "bin" / "nlm"


def load_config() -> dict:
    """notebooklm.yaml を読み込む。"""
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def load_sync_state(sync_state_path: Path) -> dict:
    """同期済みソースIDを読み込む。初回はファイルがないので空dictを返す。"""
    if not sync_state_path.exists():
        return {}
    return json.loads(sync_state_path.read_text(encoding="utf-8"))


def save_sync_state(sync_state_path: Path, state: dict) -> None:
    """同期済みソースIDを保存する。"""
    sync_state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_existing_urls() -> set[str]:
    """index.json から登録済みURLの集合を返す。"""
    if not INDEX_PATH.exists():
        return set()
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return {a["url"] for a in data.get("articles", []) if a.get("url")}


def run_nlm_source_list(notebook_id: str) -> list[dict]:
    """nlm source list を実行してソース一覧を取得する。"""
    nlm_cmd = str(NLM_PATH)
    if not NLM_PATH.exists():
        nlm_cmd = "nlm"

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Windows の PATH に nlm の場所を追加
    local_bin = str(Path.home() / ".local" / "bin")
    env["PATH"] = local_bin + os.pathsep + env.get("PATH", "")

    try:
        result = subprocess.run(
            [nlm_cmd, "source", "list", notebook_id],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            env=env,
        )
    except FileNotFoundError:
        print("  Error: nlm command not found. Install with: uv tool install notebooklm-mcp-cli", file=sys.stderr)
        return []
    except subprocess.TimeoutExpired:
        print(f"  Error: nlm source list timed out for {notebook_id}", file=sys.stderr)
        return []

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "AuthenticationError" in stderr or "Authentication expired" in stderr:
            print("  Error: NotebookLM authentication expired. Run: nlm login", file=sys.stderr)
        else:
            print(f"  Error: nlm source list failed: {stderr[:300]}", file=sys.stderr)
        return []

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  Error: Failed to parse nlm output: {result.stdout[:200]}", file=sys.stderr)
        return []


def decode_title(title: str) -> str:
    """URLエンコードされたタイトルをデコードする。"""
    if "%" in title:
        try:
            return unquote(title)
        except Exception:
            pass
    return title


def main():
    config = load_config()
    notebooks = config.get("notebooks", [])
    sync_state_file = config.get("sync_state_file", "config/notebooklm_last_sync.json")
    sync_state_path = REPO_ROOT / sync_state_file

    existing_urls = load_existing_urls()
    sync_state = load_sync_state(sync_state_path)
    today = datetime.now(JST).strftime("%Y-%m-%d")

    all_new = []

    for nb in notebooks:
        name = nb.get("name", "")
        notebook_id = nb.get("id", "")
        category = nb.get("category", "ai-workflow")

        if not notebook_id:
            continue

        print(f'NotebookLM: "{name}" ({notebook_id})', file=sys.stderr)
        sources = run_nlm_source_list(notebook_id)
        print(f"  Total sources: {len(sources)}", file=sys.stderr)

        # 同期済みソースIDの集合
        synced_ids = set(sync_state.get(notebook_id, []))

        new_count = 0
        current_ids = []

        for src in sources:
            src_id = src.get("id", "")
            if not src_id:
                continue

            current_ids.append(src_id)

            # 既に同期済みならスキップ
            if src_id in synced_ids:
                continue

            title = decode_title(src.get("title", ""))
            url = src.get("url") or ""
            src_type = src.get("type", "")

            # URLがある場合、index.json の既存URLと重複チェック
            if url and url in existing_urls:
                continue

            entry = {
                "title": title,
                "url": url,
                "date_published": "",
                "description": f"[NotebookLM source: {src_type}] {title}",
                "source": "notebooklm",
                "default_category": category,
                "date_collected": today,
                "notebook_name": name,
                "source_type": src_type,
                "source_id": src_id,
            }

            all_new.append(entry)
            if url:
                existing_urls.add(url)
            new_count += 1

        print(f"  New sources: {new_count}", file=sys.stderr)

        # 同期状態を更新（現在のソース全IDを記録）
        sync_state[notebook_id] = current_ids

    # 同期状態を保存
    save_sync_state(sync_state_path, sync_state)
    print(f"  Sync state saved to: {sync_state_path}", file=sys.stderr)

    print(f"\nTotal new NotebookLM sources: {len(all_new)}", file=sys.stderr)

    output = json.dumps(all_new, ensure_ascii=False, indent=2)
    sys.stdout.buffer.write(output.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
