"""
_filter_x_auto.py - X投稿を自動フィルタリングして有益な技術情報のみMDを生成する。
自動実行（スケジュールタスク）用。入力はstdinからJSONを受け取る。
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"

TECH_KEYWORDS = [
    "claude", "mcp", "agent", "llm", "prompt", "api", "ai", "gpt", "gemini",
    "コード", "スクリプト", "プログラム", "自動化", "ワークフロー", "ツール", "モデル",
    "プロンプト", "エージェント", "機械学習", "深層学習", "ファインチューニング",
    "hooks", "subagent", "handover", "context", "workflow", "automation",
    "python", "javascript", "typescript", "git", "docker", "supabase",
    "rag", "vector", "embedding", "fine-tuning", "フレームワーク",
]

EXCLUDE_KEYWORDS = ["無料プレゼント", "お得情報", "募集中", "フォロバ", "相互フォロー"]

CATEGORY_RULES = [
    ("claude-code", [
        "claude code", "claude.md", "claude-code", "handover",
        "コンテキスト管理", "context window", "hooks", "subagent",
        "claude_code", "スケジュールタスク",
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
    "prompt": "prompt-engineering",
    "api": "API",
    "agent": "AI-agent",
    "llm": "LLM",
    "openai": "OpenAI",
    "gemini": "Gemini",
    "gpt": "GPT",
    "cowork": "cowork",
    "vscode": "VSCode",
    "python": "Python",
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


def is_useful(art):
    desc = art.get("description", "")
    title = art.get("title", "")
    text = (title + " " + desc).lower()

    # 除外キーワードチェック
    if any(kw in text for kw in EXCLUDE_KEYWORDS):
        return False

    # 説明文が短すぎる場合は除外
    if len(desc.strip()) < 30:
        return False

    # 技術キーワードが含まれているかチェック
    return any(kw in text for kw in TECH_KEYWORDS)


def main():
    sys.stdin.reconfigure(encoding='utf-8')
    data = json.load(sys.stdin)
    counter_map = defaultdict(int)
    written = 0
    skipped = 0
    seen_urls = set()

    for art in data:
        url = art.get("url", "")
        if url in seen_urls:
            skipped += 1
            continue

        if not is_useful(art):
            skipped += 1
            continue

        seen_urls.add(url)
        date = art.get("date_published") or art.get("date_collected", "2026-04-09")
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
        out_path.write_text(content, encoding="utf-8", errors="replace")
        written += 1

    print(f"X posts: Written={written}, Skipped (filtered)={skipped}")


if __name__ == "__main__":
    main()
