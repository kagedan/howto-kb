"""
inventory_fetch.py - ショートリスト [x] の本文を実取得し、採点バッチも生成する。

棚卸し新フロー Step ①:
  - howto-kb の本文は要約のみで内容判断に使えない（有料記事の無料部分のみのことも）
  - ショートリストの [x] はかげだんが「明らかに不要なもの」を除外しただけの精査候補
  - vault に入れて良いかは、本文を取得した上で改めて Claude が採点する必要がある
  - このスクリプトは「実本文の取得」と「採点用バッチ生成」までを行う

処理:
  - web 記事 (source != x): 元URLを readability で取得
  - X 投稿 (source == x): KB本文の t.co を解決
      - リンクが外部記事 → readability で取得
      - リンクなし / SNS・動画のみ / 取得失敗 → ツイート本文を採点対象として使う
  - 結果（取得成否・本文）を fetched JSON に保存
  - 採点用バッチ (本文を 2500 文字以内に切り詰めたもの) を batches に出力

使い方:
    python scripts/inventory_fetch.py --md scripts/_inventory/shortlist-construction-2026-06-16.md \
        --scores scripts/_inventory/scores-construction-2026-06-16.json --tag construction
    オプション:
        --limit N         先頭N件だけ取得（テスト用）
        --batch-size N    1バッチの最大件数（既定 10）
        --snippet N       採点用本文の最大文字数（既定 2500）
        --timeout SEC     1リクエスト上限秒（既定 20）
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
INV_DIR = Path(__file__).resolve().parent / "_inventory"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from export_clippings import fetch_article_markdown  # noqa: E402
from inventory_import import (  # noqa: E402
    extract_tco_urls,
    is_article_url,
    kb_body,
    normalize_url,
    parse_checked,
    resolve_tco,
)

JST = timezone(timedelta(hours=9))


def fetch_web(url: str) -> dict:
    """web記事を取得して {status, body, title, fetch_url} を返す。"""
    try:
        fetched = fetch_article_markdown(url)
    except Exception as e:  # noqa: BLE001
        return {"status": "fetch_failed", "body": "", "title": "", "fetch_url": url,
                "error": f"{type(e).__name__}: {e}"[:200]}
    if not fetched:
        return {"status": "fetch_failed", "body": "", "title": "", "fetch_url": url}
    body = (fetched.get("body") or "").strip()
    title = (fetched.get("title") or "").strip()
    if not body:
        return {"status": "empty", "body": "", "title": title, "fetch_url": url}
    return {"status": "ok", "body": body, "title": title, "fetch_url": url}


def fetch_x_link(body_tweet: str) -> dict:
    """ツイート本文の t.co を解決し、リンク先記事を取得する。

    返り値: {status, body, title, fetch_url, link_status}
      - status: ok / fallback_tweet / empty
        - ok          : リンク先記事を取得できた
        - fallback_tweet: 記事リンクなし or 取得失敗 → ツイート本文を使う
      - link_status: no_link / sns_only / resolve_failed / fetch_failed / ok
    """
    tcos = extract_tco_urls(body_tweet or "")
    if not tcos:
        return {"status": "fallback_tweet", "body": "", "title": "",
                "fetch_url": "", "link_status": "no_link"}
    any_resolved = False
    article_url = ""
    for tco in tcos:
        resolved = resolve_tco(tco)
        if not resolved:
            continue
        any_resolved = True
        if is_article_url(resolved):
            article_url = resolved
            break
    if not article_url:
        link_status = "sns_only" if any_resolved else "resolve_failed"
        return {"status": "fallback_tweet", "body": "", "title": "",
                "fetch_url": "", "link_status": link_status}
    web = fetch_web(article_url)
    if web["status"] != "ok":
        return {"status": "fallback_tweet", "body": "", "title": "",
                "fetch_url": article_url, "link_status": "fetch_failed"}
    return {"status": "ok", "body": web["body"], "title": web["title"],
            "fetch_url": article_url, "link_status": "ok"}


def compress_body(body: str, limit: int) -> str:
    if not body:
        return ""
    out = re.sub(r"\n{3,}", "\n\n", body).strip()
    if len(out) > limit:
        out = out[:limit].rstrip() + "\n\n[…(snippet truncated)]"
    return out


def write_review_batches(items: list[dict], tag: str, batch_size: int, snippet_limit: int) -> Path:
    out_dir = INV_DIR / "review_batches" / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("batch_*.json"):
        old.unlink()
    reviewable = [it for it in items if it["body"]]
    n = (len(reviewable) + batch_size - 1) // batch_size
    for bi in range(n):
        chunk = reviewable[bi * batch_size:(bi + 1) * batch_size]
        batch_items = [{
            "id": it["id"],
            "title": it.get("review_title") or it["title"],
            "url": it["fetch_url"] or it["url"],
            "source": it["source"],
            "category": it["category"],
            "body": compress_body(it["body"], snippet_limit),
        } for it in chunk]
        (out_dir / f"batch_{bi + 1:03d}.json").write_text(
            json.dumps({"tag": tag, "batch": bi + 1, "n_batches": n,
                        "items": batch_items}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
    return out_dir


def main():
    p = argparse.ArgumentParser(description="ショートリスト [x] の本文取得＋採点バッチ準備")
    p.add_argument("--md", required=True, help="shortlist md")
    p.add_argument("--scores", required=True, help="scores json")
    p.add_argument("--tag", required=True, help="出力ファイルのタグ (例: construction)")
    p.add_argument("--limit", type=int, default=0, help="先頭N件だけ取得")
    p.add_argument("--batch-size", type=int, default=10, help="採点バッチの件数")
    p.add_argument("--snippet", type=int, default=2500, help="採点用本文の最大文字数")
    p.add_argument("--timeout", type=float, default=20.0, help="未使用（reservation）")
    args = p.parse_args()

    INV_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(JST).strftime("%Y-%m-%d")

    checked = parse_checked(Path(args.md))
    if not checked:
        print("[x] の付いた項目がありません。")
        return
    if args.limit:
        checked = checked[: args.limit]

    scores = json.loads(Path(args.scores).read_text(encoding="utf-8"))["items"]
    meta_by_url = {normalize_url(m["url"]): m for m in scores}

    print(f"[x] 選択: {len(checked)}件 / tag={args.tag}")
    results = []
    counts = {"ok": 0, "fallback_tweet": 0, "empty": 0, "fetch_failed": 0,
              "no_link": 0, "sns_only": 0, "resolve_failed": 0, "link_fetch_failed": 0,
              "no_meta": 0}
    for idx, c in enumerate(checked, 1):
        nurl = normalize_url(c.get("url", ""))
        m = meta_by_url.get(nurl)
        if not m:
            print(f"  [{idx:3}/{len(checked)}] FAIL(meta未一致): {c.get('title','')[:40]}")
            counts["no_meta"] += 1
            results.append({
                "id": "",
                "title": c.get("title", ""),
                "url": c.get("url", ""),
                "source": c.get("source", ""),
                "category": args.tag,
                "fetch_url": "",
                "fetch_status": "no_meta",
                "review_title": "",
                "body": "",
                "link_status": "",
                "kb_file_path": "",
            })
            continue

        is_x = m.get("source") == "x"
        base = {
            "id": m["id"],
            "title": m.get("title", ""),
            "url": m.get("url", ""),
            "source": m.get("source", ""),
            "category": m.get("category", args.tag),
            "kb_file_path": m.get("file_path", ""),
        }

        if not is_x:
            res = fetch_web(c["url"])
            entry = {**base,
                     "fetch_url": res["fetch_url"],
                     "fetch_status": res["status"],
                     "review_title": res["title"] or base["title"],
                     "body": res["body"],
                     "link_status": ""}
            tag_disp = "web"
            mark = res["status"]
        else:
            kb = kb_body(m.get("file_path", ""))
            x_res = fetch_x_link(kb)
            if x_res["status"] == "ok":
                entry = {**base,
                         "fetch_url": x_res["fetch_url"],
                         "fetch_status": "ok",
                         "review_title": x_res["title"] or base["title"],
                         "body": x_res["body"],
                         "link_status": x_res["link_status"]}
                tag_disp = "X→link"
                mark = "ok"
            else:
                # ツイート本文を採点対象に
                entry = {**base,
                         "fetch_url": x_res["fetch_url"],
                         "fetch_status": "fallback_tweet",
                         "review_title": base["title"],
                         "body": kb,
                         "link_status": x_res["link_status"]}
                tag_disp = "X→tweet"
                mark = f"fallback_tweet({x_res['link_status']})"

        results.append(entry)
        counts[entry["fetch_status"]] = counts.get(entry["fetch_status"], 0) + 1
        if entry.get("link_status") in counts and entry["fetch_status"] == "fallback_tweet":
            counts[entry["link_status"]] += 1
        if entry["fetch_status"] == "fallback_tweet" and entry.get("link_status") == "fetch_failed":
            counts["link_fetch_failed"] += 1
        body_len = len(entry["body"])
        print(f"  [{idx:3}/{len(checked)}] [{tag_disp:8}] {mark:30} ({body_len:6}字) {entry['title'][:35]}")

    fetched_path = INV_DIR / f"fetched-{args.tag}-{today}.json"
    fetched_path.write_text(json.dumps({
        "tag": args.tag, "generated_at": today,
        "shortlist": str(Path(args.md).name),
        "scores": str(Path(args.scores).name),
        "total": len(results), "counts": counts,
        "items": results,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    batches_dir = write_review_batches(results, args.tag, args.batch_size, args.snippet)

    print("\n--- 取得サマリ ---")
    print(f"  ok={counts['ok']} / fallback_tweet={counts['fallback_tweet']}"
          f" / empty={counts['empty']} / fetch_failed={counts['fetch_failed']}"
          f" / no_meta={counts['no_meta']}")
    if counts["fallback_tweet"]:
        print(f"    内訳: no_link={counts['no_link']} sns_only={counts['sns_only']}"
              f" resolve_failed={counts['resolve_failed']} link_fetch_failed={counts['link_fetch_failed']}")
    print(f"保存: {fetched_path.name}")
    print(f"採点バッチ: {batches_dir}")
    print("次: Workflow で採点 → inventory_review.py でマージ")


if __name__ == "__main__":
    main()
