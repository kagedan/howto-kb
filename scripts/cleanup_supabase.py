"""
cleanup_supabase.py - Supabase の古い記事を削除する。
本体（GitHub）には全記事を残し、Supabaseには当月＋前月分のみ保持する運用用。

使い方:
    python scripts/cleanup_supabase.py          # 2ヶ月より前の記事を削除（確認あり）
    python scripts/cleanup_supabase.py -m 3     # 3ヶ月より前の記事を削除（確認あり）
    python scripts/cleanup_supabase.py --force   # 確認なしで削除
"""

import argparse
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

JST = timezone(timedelta(hours=9))


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
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_ANON_KEY)


def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def count_old_articles(cutoff_date: str) -> int:
    """cutoff_date より前の記事数を取得する。"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/articles",
        headers={**get_headers(), "Prefer": "count=exact"},
        params={
            "select": "id",
            "date_published": f"lt.{cutoff_date}",
        },
    )
    # content-range ヘッダーから件数を取得（例: "0-9/42"）
    content_range = response.headers.get("content-range", "")
    if "/" in content_range:
        total = content_range.split("/")[1]
        return int(total) if total != "*" else 0
    return len(response.json())


def delete_old_articles(cutoff_date: str) -> int:
    """cutoff_date より前の記事を削除し、削除件数を返す。"""
    response = requests.delete(
        f"{SUPABASE_URL}/rest/v1/articles",
        headers=get_headers(),
        params={
            "date_published": f"lt.{cutoff_date}",
        },
    )
    if response.status_code not in (200, 204):
        print(f"Error: {response.status_code} - {response.text}")
        return 0
    deleted = response.json() if response.text else []
    return len(deleted)


def main():
    parser = argparse.ArgumentParser(description="Supabaseの古い記事を削除する")
    parser.add_argument(
        "-m", "--months", type=int, default=2,
        help="何ヶ月より前の記事を削除するか（デフォルト: 2）",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="確認なしで削除する",
    )
    args = parser.parse_args()

    now = datetime.now(JST)
    # 指定月数分さかのぼった月の1日を算出
    year = now.year
    month = now.month - args.months
    while month <= 0:
        month += 12
        year -= 1
    cutoff_date = f"{year:04d}-{month:02d}-01"

    print(f"削除対象: date_published < {cutoff_date}")

    count = count_old_articles(cutoff_date)
    if count == 0:
        print("削除対象の記事はありません。")
        return

    print(f"削除対象: {count}件")

    if not args.force:
        answer = input("削除を実行しますか？ (y/N): ").strip().lower()
        if answer != "y":
            print("中止しました。")
            return

    deleted = delete_old_articles(cutoff_date)
    print(f"削除完了: {deleted}件")


if __name__ == "__main__":
    main()
