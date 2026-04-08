"""
_filter_x_posts.py - X (Twitter) 投稿をフィルタリングして MD ファイルを生成する。
有益な技術情報のみを保存し、重複・低品質投稿を除外する。
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"

# 有益な技術情報と判断したインデックス（手動フィルタリング済み）
KEEP_INDICES = {
    0, 2, 5, 7, 8, 13, 16, 17, 21, 25, 27, 28, 30, 31, 32, 33, 34,
    35, 36, 37, 39, 41, 43, 44, 48, 49, 50, 51, 52, 53, 54, 57, 58,
    61, 64, 67, 69, 70, 73, 74, 75, 76, 77, 78, 79, 81, 85, 87, 90,
}

CATEGORY_RULES = [
    ("claude-code", [
        "claude code", "claude.md", "claude-code", "handover",
        "コンテキスト管理", "context window", "hooks", "subagent",
        "claude_code", "スケジュールタスク", "claude codeのweb",
        "claude codeで", "claude codeを",
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
        "ict施工", "施工管理", "建設現場",
    ]),
]

TAG_MAP = {
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
    "ict": "ICT",
    "hooks": "hooks",
    "schedule": "schedule",
}


def detect_category(title: str, description: str, default_category: str) -> str:
    text = (title + " " + description).lower()
    for cat, keywords in CATEGORY_RULES:
        if any(kw.lower() in text for kw in keywords):
            return cat
    return default_category


def extract_tags(title: str, description: str, source: str, category: str) -> list:
    tags = []
    text = (title + " " + description).lower()
    for keyword, tag in TAG_MAP.items():
        if keyword.lower() in text and tag not in tags:
            tags.append(tag)
    if source and source not in ("", "unknown"):
        tags.append(source)
    return tags[:6]


def sanitize_title(title: str) -> str:
    title = title.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").replace("\t", " ")
    title = title.replace('\\"', "")
    title = title.replace('"', "")
    title = title.replace("\\", "")
    return re.sub(r"\s+", " ", title).strip()


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:50].rstrip("-") or "article"


def main():
    data = json.load(sys.stdin)
    counter_map = defaultdict(int)
    written = 0
    skipped = 0
    seen_urls: set = set()

    for i, art in enumerate(data):
        if i not in KEEP_INDICES:
            skipped += 1
            continue

        url = art.get("url", "")
        if url in seen_urls:
            skipped += 1
            continue
        seen_urls.add(url)

        date = art.get("date_published") or art.get("date_collected", "2026-04-08")
        title = art.get("title", "untitled")
        desc = art.get("description", "")
        source = art.get("source", "x")
        default_cat = art.get("default_category", "ai-workflow")

        category = detect_category(title, desc, default_cat)
        tags = extract_tags(title, desc, source, category)
        slug = slugify(title)
        key = f"{date}-{slug}"
        counter_map[key] += 1
        article_id = f"{date}-{slug}-{counter_map[key]:02d}"

        tags_str = "[" + ", ".join(f'"{t}"' for t in tags) + "]"
        clean_title = sanitize_title(title)
        summary = desc.strip() or "X (Twitter) より収集。詳細は URL を参照。"

        content = f"""---
id: "{article_id}"
title: "{clean_title}"
url: "{url}"
source: "{source}"
category: "{category}"
tags: {tags_str}
date_published: "{date}"
date_collected: "{art.get('date_collected', date)}"
summary_by: "auto-x"
---

{summary}
"""
        out_path = ARTICLES_DIR / category / f"{article_id}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # サロゲート文字が含まれる場合はエラー無視で書き込む
        out_path.write_text(content, encoding="utf-8", errors="replace")
        written += 1

    print(f"Written: {written}, Skipped (filtered): {skipped}")


if __name__ == "__main__":
    main()
