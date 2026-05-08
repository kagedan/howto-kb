"""
_generate_mds.py - crawl_rss.py / crawl_x.py の JSON 出力から MD ファイルを一括生成する。
このスクリプトは scheduled task から自動実行される。

処理:
    1. crawl_rss.py を実行して RSS/Qiita の新規記事 JSON を取得
    2. crawl_x.py を実行して X (Twitter) の新規投稿 JSON を取得
    3. 両方の結果をマージし、Markdown ファイル（frontmatter 付き）を生成
    4. build_index.py を実行して index.json を再生成

環境変数:
    XAI_API_KEY - xAI APIキー（crawl_x.py に必要。未設定時は X 収集をスキップ）
"""

import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Windows環境でのcp932文字化け対策
os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"

# X投稿フィルター用キーワード（_filter_x_auto.py と同期）
X_TECH_KEYWORDS = [
    "claude", "mcp", "agent", "llm", "prompt", "api", "ai", "gpt", "gemini",
    "コード", "スクリプト", "プログラム", "自動化", "ワークフロー", "ツール", "モデル",
    "プロンプト", "エージェント", "機械学習", "深層学習", "ファインチューニング",
    "hooks", "subagent", "handover", "context", "workflow", "automation",
    "python", "javascript", "typescript", "git", "docker", "supabase",
    "rag", "vector", "embedding", "fine-tuning", "フレームワーク",
]
X_EXCLUDE_KEYWORDS = ["無料プレゼント", "お得情報", "募集中", "フォロバ", "相互フォロー"]

# カテゴリ判定キーワード（タイトル・説明文を小文字で照合）
CATEGORY_RULES = [
    ("claude-code", [
        "claude code", "claude.md", "claude-code", "handover", "コンテキスト管理",
        "context window", "mcp server", "hooks", "subagent", "claude_code",
    ]),
    ("cowork", [
        "cowork", "desktop automation", "デスクトップ自動化",
    ]),
    ("antigravity", [
        "antigravity", "vscode拡張", "vscode extension",
    ]),
    ("construction", [
        "土木", "建設", "施工", "工事", "配管", "水道", "下水", "公共工事",
        "construction", "civil engineering", "infrastructure",
    ]),
]


def detect_category(title: str, description: str, default_category: str) -> str:
    text = (title + " " + description).lower()
    for cat, keywords in CATEGORY_RULES:
        if any(kw.lower() in text for kw in keywords):
            return cat
    return default_category  # fallback to RSS-provided default


def extract_tags(title: str, description: str, source: str, category: str) -> list[str]:
    tags = []
    text = (title + " " + description).lower()

    tag_map = {
        "claude code": "claude-code",
        "claude.md": "CLAUDE-md",
        "mcp": "MCP",
        "prompt": "prompt-engineering",
        "api": "API",
        "agent": "AI-agent",
        "llm": "LLM",
        "openai": "OpenAI",
        "gemini": "Gemini",
        "gpt": "GPT",
        "cowork": "cowork",
        "antigravity": "antigravity",
        "vscode": "VSCode",
        "python": "Python",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "土木": "civil-engineering",
        "建設": "construction",
        "配管": "piping",
        "水道": "waterworks",
        "施工": "construction-mgmt",
    }

    for keyword, tag in tag_map.items():
        if keyword.lower() in text and tag not in tags:
            tags.append(tag)

    # source tag
    if source and source not in ("", "unknown"):
        tags.append(source)

    return tags[:6]  # 最大6タグ


def sanitize_title(title: str) -> str:
    """タイトルを YAML frontmatter の double-quoted value に安全に使える形にする。

    - 改行・制御文字を除去してスペースに置換
    - バックスラッシュ+クォート (\\") を除去
    - ダブルクォートを除去（YAML double-quoted value 内で安全に扱えないため）
    - 連続スペースを正規化
    """
    # 改行・CR・タブをスペースに置換
    title = title.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").replace("\t", " ")
    # バックスラッシュ+クォートのペアを除去（ソースデータのアーティファクト）
    title = title.replace('\\"', "")
    # 残りのダブルクォートを除去
    title = title.replace('"', "")
    # バックスラッシュ単体も除去（ファイルパス由来等）
    title = title.replace("\\", "")
    # 連続スペースを正規化
    title = re.sub(r"\s+", " ", title).strip()
    return title


def slugify(title: str) -> str:
    """タイトルから URL フレンドリーな slug を生成する。"""
    slug = title.lower()
    # 日本語・特殊文字を除去、英数とハイフンのみ残す
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    # 長さを制限
    return slug[:50].rstrip("-") or "article"


def make_id(date: str, slug: str, counter: int) -> str:
    return f"{date}-{slug}-{counter:02d}"


def extract_body(md_content: str) -> str:
    """frontmatter ('---\\n...\\n---\\n') 後の本文を返す。"""
    if md_content.startswith("---\n"):
        end = md_content.find("\n---\n", 4)
        if end > 0:
            return md_content[end + 5:].strip()
    return md_content.strip()


def find_safe_path(base_dir: Path, date: str, slug: str, new_body: str,
                   counter_map: dict) -> tuple[Path | None, str | None]:
    """衝突を避けつつ安全な保存先パスを決める。
    - 既存ファイルと本文一致 → (None, None) でスキップを指示
    - 空きスロットを見つけたら (Path, article_id) を返す
    必ず n=1 から探索するので、同一実行内で先に書かれた -01 とも重複比較される。
    """
    key = f"{date}-{slug}"
    n = 1
    while n <= 99:
        article_id = make_id(date, slug, n)
        candidate = base_dir / f"{article_id}.md"
        if not candidate.exists():
            counter_map[key] = n
            return candidate, article_id
        existing_body = extract_body(candidate.read_text(encoding="utf-8", errors="replace"))
        if existing_body == new_body.strip():
            return None, None
        n += 1
    return None, None


def build_md_content(article: dict, article_id: str, category: str,
                     tags: list[str], summary: str) -> str:
    tags_str = "[" + ", ".join(f'"{t}"' for t in tags) + "]"
    title = sanitize_title(article["title"])
    source = article.get("source", "")
    summary_by = "auto-x" if source == "x" else "auto-rss"
    query = article.get("query", "")

    return f"""---
id: "{article_id}"
title: "{title}"
url: "{article['url']}"
source: "{source}"
category: "{category}"
tags: {tags_str}
date_published: "{article.get('date_published', '')}"
date_collected: "{article.get('date_collected', '')}"
summary_by: "{summary_by}"
query: "{query}"
---

{summary}
"""


def is_x_useful(article: dict) -> bool:
    """X投稿が技術系の有益コンテンツか判定する（_filter_x_auto.py と同期）。"""
    desc = article.get("description", "")
    title = article.get("title", "")
    text = (title + " " + desc).lower()
    if any(kw in text for kw in X_EXCLUDE_KEYWORDS):
        return False
    if len(desc.strip()) < 30:
        return False
    return any(kw in text for kw in X_TECH_KEYWORDS)


def resolve_summary(article: dict) -> str:
    summary = article.get("description", "").strip()
    source = article.get("source", "")
    if not summary or summary == article["title"]:
        if source == "x":
            return "X (Twitter) より収集。詳細は URL を参照。"
        feed_name = article.get("feed_name", source or "RSS")
        return f"{feed_name} より収集。詳細は URL を参照。"
    return summary


def run_crawler(script_name: str, env: dict | None = None) -> list[dict]:
    """指定したクローラーを実行し、JSON 出力をパースして返す。"""
    script_path = REPO_ROOT / "scripts" / script_name
    run_env = {**os.environ, **(env or {})}

    print(f"Running {script_name} ...", flush=True)
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        text=True,
        env=run_env,
    )

    # stderr は情報ログとして出力
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(f"WARNING: {script_name} exited with code {result.returncode}", file=sys.stderr)
        return []

    stdout = result.stdout.strip()
    if not stdout:
        return []

    try:
        articles = json.loads(stdout)
        return articles if isinstance(articles, list) else []
    except json.JSONDecodeError as e:
        print(f"WARNING: {script_name} JSON parse failed: {e}", file=sys.stderr)
        return []


def process_articles(articles: list[dict]) -> tuple[int, int]:
    """記事リストからMDファイルを生成し、(書き込み件数, 重複スキップ件数) を返す。"""
    counter_map: dict[str, int] = defaultdict(int)
    written = 0
    duplicates = 0

    for art in articles:
        date = art.get("date_published") or art.get("date_collected", "2026-01-01")
        title = art.get("title", "untitled")
        description = art.get("description", "")
        source = art.get("source", "")
        default_cat = art.get("default_category", "ai-workflow")

        category = detect_category(title, description, default_cat)
        tags = extract_tags(title, description, source, category)
        slug = slugify(title)
        summary = resolve_summary(art)

        target_path, article_id = find_safe_path(
            ARTICLES_DIR / category, date, slug, summary, counter_map
        )
        if target_path is None:
            duplicates += 1
            print(f"Skipped (duplicate body): {date}-{slug}", file=sys.stderr)
            continue

        target_path.parent.mkdir(parents=True, exist_ok=True)
        content = build_md_content(art, article_id, category, tags, summary)
        target_path.write_text(content, encoding="utf-8")
        written += 1

    return written, duplicates


def main():
    all_articles: list[dict] = []

    # 1. RSS / Qiita
    rss_articles = run_crawler("crawl_rss.py")
    print(f"  RSS: {len(rss_articles)} new articles", flush=True)
    all_articles.extend(rss_articles)

    # 2. X (Twitter) — SOCIALDATA_API_KEY が未設定ならスキップ
    x_raw: list[dict] = []
    x_articles: list[dict] = []
    if os.environ.get("SOCIALDATA_API_KEY"):
        x_raw = run_crawler("crawl_x.py")
        x_articles = [a for a in x_raw if is_x_useful(a)]
        x_filtered = len(x_raw) - len(x_articles)
        print(f"  X: {len(x_articles)} new posts (filtered out {x_filtered} non-tech)",
              flush=True)
        all_articles.extend(x_articles)
    else:
        print("  X: skipped (SOCIALDATA_API_KEY not set)", flush=True)

    # 2.5 RT記事からObsidian clippingsを生成（フィルター前のx_rawから抽出）
    rt_articles = [a for a in x_raw if a.get("is_retweet")]
    if rt_articles:
        print(f"\nExporting {len(rt_articles)} RT clippings ...", flush=True)
        clip_result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "export_clippings.py")],
            input=json.dumps(rt_articles, ensure_ascii=False),
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            text=True,
        )
        if clip_result.stderr:
            print(clip_result.stderr, file=sys.stderr)
        if clip_result.returncode == 0:
            print("Clippings exported.", flush=True)
        else:
            print("WARNING: export_clippings.py failed.", file=sys.stderr)

    if not all_articles:
        print("No new articles.")
        return

    print(f"\nProcessing {len(all_articles)} articles ...", flush=True)
    written, duplicates = process_articles(all_articles)
    print(f"MD files written: {written} (skipped {duplicates} duplicates)", flush=True)

    # 3. build_index.py を実行して index.json を再生成
    print("\nRunning build_index.py ...", flush=True)
    idx_result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "build_index.py")],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if idx_result.stderr:
        print(idx_result.stderr, file=sys.stderr)
    if idx_result.returncode == 0:
        print("index.json updated.", flush=True)
    else:
        print("WARNING: build_index.py failed.", file=sys.stderr)

    print(f"\nDone. {written} articles processed (skipped {duplicates} duplicates).")


if __name__ == "__main__":
    main()
