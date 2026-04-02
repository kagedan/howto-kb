"""
build_index.py - articles/ 配下の全Markdownからfrontmatterを抽出し index.json を生成する。

使い方:
    python scripts/build_index.py

出力:
    index.json          — 全件（Claude Code / Coworkでの全文検索用）
    index-latest.json   — 直近30日分（Claude.aiからの日常参照用）
    index-YYYY-MM.json  — 月別アーカイブ（特定月の記事を調べたいとき）
"""

import json
import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"
INDEX_PATH = REPO_ROOT / "index.json"
INDEX_LATEST_PATH = REPO_ROOT / "index-latest.json"

# 直近何日分を index-latest.json に含めるか
LATEST_DAYS = 30

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

        # 配列値の処理: ["tag1", "tag2"] — 値全体が[...]形式の場合のみ
        list_match = LIST_VALUE_RE.match(value) if value.startswith('[') else None
        if list_match and value.endswith(']'):
            items = list_match.group(1)
            data[key] = [
                s.strip().strip('"').strip("'")
                for s in items.split(",")
                if s.strip()
            ]
        else:
            # クォートを除去
            val = value.strip('"').strip("'")
            # 防御的処理: \" (バックスラッシュ+クォート) のアンエスケープ
            val = val.replace('\\"', '"')
            # 残存バックスラッシュの除去（ファイルパス由来等のアーティファクト）
            if key == "title":
                val = val.replace("\\", "")
            data[key] = val

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

        # IDにカテゴリをプレフィックスとして付与し、異カテゴリ間の重複を防ぐ
        category = fm.get("category", "")
        raw_id = fm.get("id", "")
        unique_id = f"{category}/{raw_id}" if category else raw_id

        articles.append({
            "id": unique_id,
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


def write_index(path: Path, articles: list[dict], now: str):
    """indexファイルを書き出す共通関数。"""
    data = {
        "last_updated": now,
        "total_count": len(articles),
        "articles": articles,
    }
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_latest_index(articles: list[dict]) -> list[dict]:
    """直近30日分の記事を抽出する。"""
    cutoff = (datetime.now(JST) - timedelta(days=LATEST_DAYS)).strftime("%Y-%m-%d")
    return [a for a in articles if a.get("date_collected", "") >= cutoff]


def build_monthly_indexes(articles: list[dict]) -> dict[str, list[dict]]:
    """記事を年月別に分類する。キーは 'YYYY-MM' 形式。"""
    monthly: dict[str, list[dict]] = {}
    for a in articles:
        dc = a.get("date_collected", "")
        if len(dc) >= 7:
            ym = dc[:7]  # "YYYY-MM"
            monthly.setdefault(ym, []).append(a)
    return monthly


def main():
    index = build_index()
    now = index["last_updated"]
    articles = index["articles"]

    # 1. index.json（全件）
    INDEX_PATH.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"index.json updated: {index['total_count']} articles")

    # 2. index-latest.json（直近30日分）
    latest = build_latest_index(articles)
    write_index(INDEX_LATEST_PATH, latest, now)
    print(f"index-latest.json updated: {len(latest)} articles (last {LATEST_DAYS} days)")

    # 3. index-YYYY-MM.json（月別アーカイブ）
    monthly = build_monthly_indexes(articles)
    for ym, month_articles in sorted(monthly.items()):
        month_path = REPO_ROOT / f"index-{ym}.json"
        write_index(month_path, month_articles, now)
        print(f"index-{ym}.json updated: {len(month_articles)} articles")


    # Supabase同期（失敗してもindex生成には影響させない）
    try:
        from sync_supabase import sync_to_supabase
        sync_to_supabase(articles)
        print("Supabase同期完了")
    except Exception as e:
        print(f"Supabase同期エラー（続行）: {e}")


if __name__ == "__main__":
    main()
