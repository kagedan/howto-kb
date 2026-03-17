"""
add_manual.py - 手動でナレッジベースに記事を登録するヘルパー。

使い方（Claude Code / Antigravity から）:
    python scripts/add_manual.py --title "記事タイトル" --url "https://..." --category claude-code --tags tag1,tag2,tag3

    または対話モード:
    python scripts/add_manual.py

生成されるもの:
    - articles/{category}/{id}.md （frontmatter + 空の本文）
    - index.json の再生成（build_index.py を自動呼び出し）

本文（要約）は生成後にClaude Code等で記述してください。
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"
BUILD_INDEX = REPO_ROOT / "scripts" / "build_index.py"

JST = timezone(timedelta(hours=9))

VALID_CATEGORIES = ["claude-code", "cowork", "antigravity", "ai-workflow", "construction"]
VALID_SOURCES = ["x", "zenn", "qiita", "note", "anthropic", "notebooklm", "chat", "manual"]


def slugify(text: str, max_len: int = 50) -> str:
    """タイトルからslugを生成する。日本語はローマ字化せず短縮キーワードを使う。"""
    # ASCII文字のみ抽出してslug化
    ascii_part = re.sub(r"[^a-zA-Z0-9\s-]", "", text)
    if ascii_part.strip():
        slug = re.sub(r"[\s]+", "-", ascii_part.strip().lower())
    else:
        # 日本語のみの場合は generic slug
        slug = "article"
    return slug[:max_len].rstrip("-")


def find_next_seq(category: str, date_str: str, slug: str) -> str:
    """同日・同slugの記事がある場合の連番を決定する。"""
    cat_dir = ARTICLES_DIR / category
    prefix = f"{date_str}-{slug}"
    existing = list(cat_dir.glob(f"{prefix}-*.md"))
    return f"{len(existing) + 1:02d}"


def prompt_input(label: str, default: str = "", choices: list[str] | None = None) -> str:
    """対話モード用の入力プロンプト。"""
    hint = ""
    if choices:
        hint = f" [{'/'.join(choices)}]"
    if default:
        hint += f" (default: {default})"
    sys.stdout.reconfigure(encoding="utf-8")
    val = input(f"{label}{hint}: ").strip()
    if not val and default:
        return default
    if choices and val not in choices:
        print(f"  Invalid choice. Must be one of: {', '.join(choices)}")
        return prompt_input(label, default, choices)
    return val


def main():
    parser = argparse.ArgumentParser(description="手動でナレッジDBに記事を登録")
    parser.add_argument("--title", help="記事タイトル")
    parser.add_argument("--url", default="", help="元記事のURL")
    parser.add_argument("--source", default="manual", help=f"ソース ({', '.join(VALID_SOURCES)})")
    parser.add_argument("--category", help=f"カテゴリ ({', '.join(VALID_CATEGORIES)})")
    parser.add_argument("--tags", default="", help="タグ（カンマ区切り、英語）")
    parser.add_argument("--date-published", default="", help="公開日 (YYYY-MM-DD)")
    parser.add_argument("--summary", default="", help="要約テキスト（200〜300字）")
    args = parser.parse_args()

    # CLIから全引数が揃っているかで対話モード判定
    interactive = args.title is None or args.category is None

    title = args.title or prompt_input("タイトル")
    url = args.url if not interactive else (args.url or prompt_input("URL (空欄可)"))
    source = args.source if not interactive else prompt_input("ソース", args.source, VALID_SOURCES)
    category = args.category or prompt_input("カテゴリ", "", VALID_CATEGORIES)
    tags_str = args.tags if not interactive else (args.tags or prompt_input("タグ (カンマ区切り、英語)"))
    date_published = args.date_published if not interactive else (args.date_published or prompt_input("公開日 (YYYY-MM-DD, 空欄可)"))
    summary = args.summary if not interactive else (args.summary or prompt_input("要約 (空欄の場合は後で記述)"))

    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    today = datetime.now(JST).strftime("%Y-%m-%d")
    slug = slugify(title)
    seq = find_next_seq(category, today, slug)
    article_id = f"{today}-{slug}-{seq}"

    # frontmatter生成
    tags_yaml = json_list_to_yaml(tags)
    frontmatter = f'''---
id: "{article_id}"
title: "{title}"
url: "{url}"
source: "{source}"
category: "{category}"
tags: {tags_yaml}
date_published: "{date_published}"
date_collected: "{today}"
summary_by: "manual"
---

{summary}
'''

    # ファイル書き出し
    cat_dir = ARTICLES_DIR / category
    cat_dir.mkdir(parents=True, exist_ok=True)
    md_path = cat_dir / f"{article_id}.md"
    md_path.write_text(frontmatter, encoding="utf-8")

    print(f"\nCreated: {md_path.relative_to(REPO_ROOT)}")

    # index.json 再生成
    subprocess.run([sys.executable, str(BUILD_INDEX)], check=True)

    print(f"\nDone. Remember to commit & push:")
    print(f"  git add articles/{category}/{article_id}.md index.json")
    print(f"  git commit -m 'Add: {title[:50]}'")
    print(f"  git push")


def json_list_to_yaml(items: list[str]) -> str:
    """Python list を YAML の inline list 形式に変換する。"""
    quoted = [f'"{item}"' for item in items]
    return f"[{', '.join(quoted)}]"


if __name__ == "__main__":
    main()
