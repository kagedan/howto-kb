"""
sync_supabase.py - index.json の記事メタデータを Supabase にupsertする。

使い方:
    python scripts/sync_supabase.py          # index.json 全件を同期
"""

import json
import os
import requests
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "index.json"


def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip().strip('"')

load_env()

SUPABASE_URL = "https://gryrgjnfekwptyngbmao.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_How0RxnjdME_nNlnAhJ9Vg_Y982jDum"
# 書き込みには service_role key が必要（.env または環境変数から取得）
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_ANON_KEY)


def upsert_articles(articles: list[dict]):
    """articlesリストをSupabaseにupsert（500件ずつバッチ処理）"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }

    batch_size = 500
    for i in range(0, len(articles), batch_size):
        batch = articles[i : i + batch_size]
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/articles",
            headers=headers,
            json=batch,
        )
        if response.status_code not in (200, 201):
            print(f"Error: {response.status_code} - {response.text}")
        else:
            print(f"Upserted {len(batch)} articles (batch {i // batch_size + 1})")


def transform_article(article: dict) -> dict:
    """index.json の記事データを Supabase テーブル形式に変換する"""
    title = article.get("title", "")
    # titleがリスト形式の場合は最初の要素を使う
    if isinstance(title, list):
        title = title[0] if title else ""

    return {
        "id": article.get("id", ""),
        "title": title,
        "url": article.get("url", ""),
        "source": article.get("source", ""),
        "category": article.get("category", ""),
        "tags": article.get("tags", []),
        "date_published": article.get("date_published", "") or None,
        "date_collected": article.get("date_collected", "") or None,
        "file_path": article.get("file_path", ""),
    }


def sync_to_supabase(articles: list[dict]):
    """記事リストを変換してSupabaseにupsertする（ID重複は先勝ちで除去）"""
    seen = set()
    transformed = []
    for a in articles:
        row = transform_article(a)
        if row["id"] not in seen:
            seen.add(row["id"])
            transformed.append(row)
    if len(articles) != len(transformed):
        print(f"ID重複を除去: {len(articles)} -> {len(transformed)}")
    upsert_articles(transformed)


def main():
    index_data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    articles = index_data["articles"]
    print(f"index.json: {len(articles)} articles")
    sync_to_supabase(articles)
    print("Supabase同期完了")


if __name__ == "__main__":
    main()
