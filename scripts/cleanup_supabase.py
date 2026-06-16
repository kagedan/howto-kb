"""
cleanup_supabase.py - Supabase の古い記事 or orphan 記事を削除する。
本体（GitHub）には残したい記事を articles/ に保持し、不要分は archive/ に退避する運用。
Supabase は「直近Nヶ月」または「index.json に同期」の2つのモードで整理する。

使い方:
    python scripts/cleanup_supabase.py          # 月数モード: 2ヶ月より前を削除（確認あり）
    python scripts/cleanup_supabase.py -m 3     # 月数モード: 3ヶ月より前を削除
    python scripts/cleanup_supabase.py --orphan # orphan モード: index.json に無い記事を削除
    python scripts/cleanup_supabase.py --force  # 確認なしで削除
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

JST = timezone(timedelta(hours=9))
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


def list_supabase_ids() -> set[str]:
    """Supabase 上の全 id を取得する。"""
    ids: set[str] = set()
    offset = 0
    page_size = 1000
    while True:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/articles",
            headers={**get_headers(), "Range": f"{offset}-{offset + page_size - 1}",
                     "Range-Unit": "items"},
            params={"select": "id"},
        )
        if r.status_code not in (200, 206):
            print(f"Error: {r.status_code} - {r.text}")
            break
        page = r.json()
        if not page:
            break
        ids.update(a["id"] for a in page)
        if len(page) < page_size:
            break
        offset += page_size
    return ids


def _delete_batch(ids: list[str]) -> int:
    """指定 id をまとめて削除。失敗時は半分割して再帰。"""
    if not ids:
        return 0
    if len(ids) == 1:
        x = ids[0]
        r = requests.delete(
            f"{SUPABASE_URL}/rest/v1/articles",
            headers=get_headers(), params={"id": f"eq.{x}"},
        )
        if r.status_code in (200, 204):
            return 1
        print(f"    NG(1件): {x[:60]} -> {r.status_code} {r.text[:80]}")
        return 0
    ids_param = "in.(" + ",".join(f'"{x}"' for x in ids) + ")"
    r = requests.delete(
        f"{SUPABASE_URL}/rest/v1/articles",
        headers=get_headers(), params={"id": ids_param},
    )
    if r.status_code in (200, 204):
        deleted = r.json() if r.text else []
        return len(deleted) if deleted else len(ids)
    mid = len(ids) // 2
    return _delete_batch(ids[:mid]) + _delete_batch(ids[mid:])


def delete_ids(ids: list[str]) -> int:
    """指定 id 群を Supabase から削除する（100件ずつ → 失敗時 分割再帰）。"""
    total = 0
    batch = 100
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        n = _delete_batch(chunk)
        total += n
        print(f"  {i + len(chunk)}/{len(ids)} 削除済み (このバッチ {n}/{len(chunk)})")
    return total


def cleanup_orphans(force: bool) -> None:
    if not INDEX_PATH.exists():
        print(f"index.json が見つかりません: {INDEX_PATH}")
        return
    idx = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    local_ids = {a["id"] for a in idx.get("articles", [])}
    print(f"index.json id 数: {len(local_ids)}")
    sb_ids = list_supabase_ids()
    print(f"Supabase id 数: {len(sb_ids)}")
    orphans = sorted(sb_ids - local_ids)
    print(f"orphan（Supabase にあって index.json に無い）: {len(orphans)} 件")
    if not orphans:
        return
    if not force:
        answer = input("削除を実行しますか？ (y/N): ").strip().lower()
        if answer != "y":
            print("中止しました。")
            return
    deleted = delete_ids(orphans)
    print(f"削除完了: {deleted}件")


def main():
    parser = argparse.ArgumentParser(description="Supabaseの古い/orphan記事を削除する")
    parser.add_argument(
        "-m", "--months", type=int, default=2,
        help="月数モード: 何ヶ月より前の記事を削除するか（デフォルト: 2）",
    )
    parser.add_argument(
        "--orphan", action="store_true",
        help="orphan モード: index.json に無い記事を Supabase から削除",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="確認なしで削除する",
    )
    args = parser.parse_args()

    if args.orphan:
        cleanup_orphans(args.force)
        return

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
