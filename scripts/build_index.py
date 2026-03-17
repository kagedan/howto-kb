"""
build_index.py - articles/ 配下の全Markdownからfrontmatterを抽出し index.json を生成する。

使い方:
    python scripts/build_index.py

出力:
    index.json（リポジトリルート）
"""

import json
import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"
INDEX_PATH = REPO_ROOT / "index.json"

JST = timezone(timedelta(hours=9))

# frontmatter のフィールドを1行ずつパースする簡易パーサー
# PyYAML に依存しない
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
LIST_VALUE_RE = re.compile(r'\[([^\]]*)\]')


def parse_frontmatter(text: str) -> dict | None:
    """Markdownテキストからfrontmatterを辞書として返す。"""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None

    data = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        # 配列値の処理: ["tag1", "tag2"]
        list_match = LIST_VALUE_RE.search(value)
        if list_match:
            items = list_match.group(1)
            data[key] = [
                s.strip().strip('"').strip("'")
                for s in items.split(",")
                if s.strip()
            ]
        else:
            # クォートを除去
            data[key] = value.strip('"').strip("'")

    return data


def build_index() -> dict:
    """articles/ を走査し、index.json 用のデータを構築する。"""
    articles = []

    for md_path in sorted(ARTICLES_DIR.rglob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if fm is None or "id" not in fm:
            continue

        # file_path は リポジトリルートからの相対パス (forward slash)
        rel_path = md_path.relative_to(REPO_ROOT).as_posix()

        articles.append({
            "id": fm.get("id", ""),
            "title": fm.get("title", ""),
            "url": fm.get("url", ""),
            "source": fm.get("source", ""),
            "category": fm.get("category", ""),
            "tags": fm.get("tags", []),
            "date_published": fm.get("date_published", ""),
            "date_collected": fm.get("date_collected", ""),
            "file_path": rel_path,
        })

    # date_collected の降順でソート（新しい記事が先）
    articles.sort(key=lambda a: a.get("date_collected", ""), reverse=True)

    now = datetime.now(JST).strftime("%Y-%m-%dT%H:%M:%S+09:00")
    return {
        "last_updated": now,
        "total_count": len(articles),
        "articles": articles,
    }


def main():
    index = build_index()
    INDEX_PATH.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"index.json updated: {index['total_count']} articles")


if __name__ == "__main__":
    main()
