"""
_generate_rss_mds.py - crawl_rss.py の JSON 出力から MD ファイルを生成する。
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"

CATEGORY_RULES = [
    ("claude-code", [
        "claude code", "claude.md", "claude-code", "handover",
        "コンテキスト管理", "context window", "mcp server", "hooks", "subagent",
    ]),
    ("cowork", ["cowork", "desktop automation", "デスクトップ自動化"]),
    ("antigravity", ["antigravity", "vscode拡張", "vscode extension"]),
    ("construction", [
        "土木", "建設", "施工", "工事", "配管", "水道", "下水", "公共工事",
        "construction", "civil engineering", "infrastructure",
    ]),
]

TAG_MAP = {
    "claude code": "claude-code",
    "claude.md": "CLAUDE-md",
    "mcp": "MCP",
    "api": "API",
    "agent": "AI-agent",
    "llm": "LLM",
    "土木": "civil-engineering",
    "建設": "construction",
    "配管": "piping",
    "水道": "waterworks",
    "施工": "construction-mgmt",
}


def detect_category(title, desc, default_cat):
    text = (title + " " + desc).lower()
    for cat, kws in CATEGORY_RULES:
        if any(k.lower() in text for k in kws):
            return cat
    return default_cat


def extract_tags(title, desc, source, category):
    tags = []
    text = (title + " " + desc).lower()
    for kw, tag in TAG_MAP.items():
        if kw.lower() in text and tag not in tags:
            tags.append(tag)
    if source and source not in ("", "unknown"):
        tags.append(source)
    return tags[:6]


def sanitize_title(t):
    t = t.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").replace("\t", " ")
    t = t.replace('\\"', "")
    t = t.replace('"', "")
    t = t.replace("\\", "")
    return re.sub(r"\s+", " ", t).strip()


def slugify(t):
    s = t.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")[:50].rstrip("-") or "article"


def main():
    sys.stdin.reconfigure(encoding='utf-8')
    data = json.load(sys.stdin)
    counter_map = defaultdict(int)
    written = 0

    for art in data:
        date = art.get("date_published") or art.get("date_collected", "2026-04-08")
        title = art.get("title", "untitled")
        desc = art.get("description", "")
        source = art.get("source", "rss")
        default_cat = art.get("default_category", "ai-workflow")
        feed_name = art.get("feed_name", source or "RSS")

        category = detect_category(title, desc, default_cat)
        tags = extract_tags(title, desc, source, category)
        slug = slugify(title)
        key = f"{date}-{slug}"
        counter_map[key] += 1
        article_id = f"{date}-{slug}-{counter_map[key]:02d}"

        clean_title = sanitize_title(title)
        summary = desc.strip() or f"{feed_name} より収集。詳細は URL を参照。"
        tags_str = "[" + ", ".join(f'"{t}"' for t in tags) + "]"

        content = f"""---
id: "{article_id}"
title: "{clean_title}"
url: "{art.get('url', '')}"
source: "{source}"
category: "{category}"
tags: {tags_str}
date_published: "{date}"
date_collected: "{art.get('date_collected', date)}"
summary_by: "auto-rss"
---

{summary}
"""
        out_path = ARTICLES_DIR / category / f"{article_id}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8", errors="replace")
        written += 1
        print(f"Written: {out_path.name}")

    print(f"Total RSS MD written: {written}")


if __name__ == "__main__":
    main()
