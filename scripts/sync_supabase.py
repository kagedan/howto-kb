"""
sync_supabase.py - index.json の記事メタデータを Supabase にupsertする。

差分同期: 前回送信した内容の指紋（ハッシュ）を scripts/.sync_state.json に記録し、
新着・変更があった記事だけを送る。タイムアウト等で失敗したバッチは state に
反映されないため、次回実行時に自動で再送される。

使い方:
    python scripts/sync_supabase.py          # 差分同期（新着・変更分のみ）
    python scripts/sync_supabase.py --full   # 状態を無視して全件を送り直す
"""

import hashlib
import json
import os
import re
import sys
import requests
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "index.json"
STATE_PATH = Path(__file__).resolve().parent / ".sync_state.json"


def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip().strip('"')

load_env()

FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)

SUPABASE_URL = "https://gryrgjnfekwptyngbmao.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_How0RxnjdME_nNlnAhJ9Vg_Y982jDum"
# 書き込みには service_role key が必要（.env または環境変数から取得）
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_ANON_KEY)


def row_hash(row: dict) -> str:
    """upsert対象の行データから安定したハッシュ（指紋）を計算する。
    キー順に依存しないよう sort_keys=True で正規化する。"""
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_state() -> dict:
    """前回同期した {記事ID: ハッシュ} の状態を読み込む。無い/壊れていれば空。"""
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            print("警告: .sync_state.json を読めませんでした。全件同期として扱います。")
            return {}
    return {}


def save_state(state: dict):
    """同期状態を保存する。"""
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")


def upsert_articles(rows: list[dict], hashes: dict, state: dict):
    """変更のあった rows を Supabase に upsert（250件ずつバッチ処理）。
    成功したバッチに含まれる記事だけ state に指紋を反映する。
    失敗したバッチは反映しないので、次回実行時に自動で再送される。"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }

    batch_size = 250
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        batch_no = i // batch_size + 1
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/articles",
                headers=headers,
                json=batch,
            )
        except requests.RequestException as e:
            print(f"Error (batch {batch_no}): {e} - 次回再送します")
            continue
        if response.status_code not in (200, 201):
            print(f"Error: {response.status_code} - {response.text} (batch {batch_no}) - 次回再送します")
            continue
        # 成功したバッチのぶんだけ state を更新
        for r in batch:
            state[r["id"]] = hashes[r["id"]]
        print(f"Upserted {len(batch)} articles (batch {batch_no})")


def strip_nulls(value):
    """Postgres text型が拒否する \\u0000（null文字）を文字列から除去する。
    list は要素ごとに再帰、それ以外は素通し。
    """
    if isinstance(value, str):
        return value.replace("\x00", "")
    if isinstance(value, list):
        return [strip_nulls(v) for v in value]
    return value


def read_content(file_path: str) -> str:
    """Markdownファイルからfrontmatterを除去した本文を返す。"""
    md_path = REPO_ROOT / file_path
    if not md_path.exists():
        return ""
    text = md_path.read_text(encoding="utf-8")
    body = FRONTMATTER_RE.sub("", text, count=1).strip()
    return body


def transform_article(article: dict) -> dict:
    """index.json の記事データを Supabase テーブル形式に変換する"""
    title = article.get("title", "")
    # titleがリスト形式の場合は最初の要素を使う
    if isinstance(title, list):
        title = title[0] if title else ""

    # date_published が空の場合、IDから日付（YYYY-MM-DD）を抽出してフォールバックに使う
    # ID形式: "category/YYYY-MM-DD-slug-連番" または "YYYY-MM-DD-slug-連番"
    date_published = article.get("date_published", "")
    if not date_published:
        article_id = article.get("id", "")
        # カテゴリプレフィックスがあればスラッシュ以降を使う
        id_part = article_id.split("/")[-1] if "/" in article_id else article_id
        if len(id_part) >= 10:
            date_published = id_part[:10]

    # Markdownファイルから本文を読み取る
    file_path = article.get("file_path", "")
    content = read_content(file_path) if file_path else ""

    row = {
        "id": article.get("id", ""),
        "title": title,
        "url": article.get("url", ""),
        "source": article.get("source", ""),
        "category": article.get("category", ""),
        "tags": article.get("tags", []),
        "date_published": date_published or None,
        "date_collected": article.get("date_collected", "") or None,
        "file_path": file_path,
        "content": content or None,
    }
    # Postgres text 型が拒否する (null文字) を全フィールドから除去
    return {k: strip_nulls(v) for k, v in row.items()}


def sync_to_supabase(articles: list[dict], full: bool = False):
    """記事リストを変換し、前回から変更のあった分だけ Supabase に upsert する。
    full=True のときは state を無視して全件を対象にする。"""
    state = {} if full else load_state()

    seen = set()
    changed = []        # 送信対象（新着・変更分）
    hashes = {}         # {id: 現在のハッシュ}
    current_ids = set() # index.json に現存する全ID

    for a in articles:
        row = transform_article(a)
        rid = row["id"]
        if rid in seen:
            continue
        seen.add(rid)
        current_ids.add(rid)
        h = row_hash(row)
        hashes[rid] = h
        # 新着、または前回送信時から指紋が変わった記事だけ送る
        if state.get(rid) != h:
            changed.append(row)

    if len(articles) != len(seen):
        print(f"ID重複を除去: {len(articles)} -> {len(seen)}")

    # index.json から消えた記事は state からも掃除する（Supabase側は削除しない）
    removed = [rid for rid in state if rid not in current_ids]
    for rid in removed:
        del state[rid]
    if removed:
        print(f"state から削除済み記事を {len(removed)}件 掃除")

    mode = "（--full: 全件）" if full else ""
    print(f"対象 {len(seen)}件 / 送信 {len(changed)}件 {mode}")

    if not changed:
        print("変更なし。送信をスキップ")
        save_state(state)  # removed の掃除を反映
        return

    upsert_articles(changed, hashes, state)
    save_state(state)


def main():
    full = "--full" in sys.argv
    index_data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    articles = index_data["articles"]
    print(f"index.json: {len(articles)} articles" + ("（--full モード）" if full else ""))
    sync_to_supabase(articles, full=full)
    print("Supabase同期完了")


if __name__ == "__main__":
    main()
