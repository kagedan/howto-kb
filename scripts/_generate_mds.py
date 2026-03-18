"""
_generate_mds.py - crawl_rss.py の JSON 出力から MD ファイルを一括生成する。
このスクリプトは scheduled task から自動実行される一時的なヘルパーです。
"""

import json
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
    if not summary or summary == article["title"]:
        summary = f"{article['feed_name']} より収集。詳細は URL を参照。"

    content = f"""---
id: "{article_id}"
title: "{title}"
url: "{article['url']}"
source: "{article.get('source', '')}"
category: "{category}"
tags: {tags_str}
date_published: "{article.get('date_published', '')}"
date_collected: "{article.get('date_collected', '')}"
summary_by: "auto-rss"
---

{summary}
"""
    out_path = ARTICLES_DIR / category / f"{article_id}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return out_path


def main():
    # crawl_rss.py を実行して JSON を取得
    print("Running crawl_rss.py ...", flush=True)
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "crawl_rss.py")],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print("ERROR: crawl_rss.py failed:", result.stderr, file=sys.stderr)
        sys.exit(1)

    # stderr は情報ログとして出力
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    # JSON パース
    try:
        articles = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON parse failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not articles:
        print("No new articles.")
        return

    print(f"Processing {len(articles)} new articles ...", flush=True)

    # 同一 date+slug の連番管理
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

        out_path = write_md(art, article_id, category, tags)
        written += 1

    print(f"Done. {written} MD files written.")


if __name__ == "__main__":
    main()
