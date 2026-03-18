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

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"

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


def write_md(article: dict, article_id: str, category: str, tags: list[str]) -> Path:
    tags_str = "[" + ", ".join(f'"{t}"' for t in tags) + "]"
    title = article["title"].replace('"', '\\"')
    summary = article.get("description", "").strip()
    source = article.get("source", "")

    # summary_by を source に応じて設定
    if source == "x":
        summary_by = "auto-x"
        if not summary or summary == article["title"]:
            summary = "X (Twitter) より収集。詳細は URL を参照。"
    else:
        summary_by = "auto-rss"
        if not summary or summary == article["title"]:
            feed_name = article.get("feed_name", source or "RSS")
            summary = f"{feed_name} より収集。詳細は URL を参照。"

    content = f"""---
id: "{article_id}"
title: "{title}"
url: "{article['url']}"
source: "{source}"
category: "{category}"
tags: {tags_str}
date_published: "{article.get('date_published', '')}"
date_collected: "{article.get('date_collected', '')}"
summary_by: "{summary_by}"
---

{summary}
"""
    out_path = ARTICLES_DIR / category / f"{article_id}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return out_path


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


def process_articles(articles: list[dict]) -> int:
    """記事リストからMDファイルを生成し、書き込み件数を返す。"""
    counter_map: dict[str, int] = defaultdict(int)
    written = 0

    for art in articles:
        date = art.get("date_published") or art.get("date_collected", "2026-01-01")
        title = art.get("title", "untitled")
        description = art.get("description", "")
        source = art.get("source", "")
        default_cat = art.get("default_category", "ai-workflow")

        category = detect_category(title, description, default_cat)
        tags = extract_tags(title, description, source, category)
        slug = slugify(title)
        key = f"{date}-{slug}"
        counter_map[key] += 1
        article_id = make_id(date, slug, counter_map[key])

        write_md(art, article_id, category, tags)
        written += 1

    return written


def main():
    all_articles: list[dict] = []

    # 1. RSS / Qiita
    rss_articles = run_crawler("crawl_rss.py")
    print(f"  RSS: {len(rss_articles)} new articles", flush=True)
    all_articles.extend(rss_articles)

    # 2. X (Twitter) — XAI_API_KEY が未設定ならスキップ
    if os.environ.get("XAI_API_KEY"):
        x_articles = run_crawler("crawl_x.py")
        print(f"  X: {len(x_articles)} new posts", flush=True)
        all_articles.extend(x_articles)
    else:
        print("  X: skipped (XAI_API_KEY not set)", flush=True)

    if not all_articles:
        print("No new articles.")
        return

    print(f"\nProcessing {len(all_articles)} articles ...", flush=True)
    written = process_articles(all_articles)
    print(f"MD files written: {written}", flush=True)

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

    print(f"\nDone. {written} articles processed.")


if __name__ == "__main__":
    main()
