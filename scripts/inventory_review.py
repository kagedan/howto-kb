"""
inventory_review.py - 採点 Workflow の結果を fetched.json とマージして reviewed.json を作る。

棚卸し新フロー Step ②:
  - inventory_fetch.py が出した本文を Workflow が採点する
  - その採点結果 JSON（または複数）と fetched.json を id でマージ
  - score4-5 を vault 取り込み確定（後続 inventory_import.py が処理）
  - score3 は別レポート pending-review-{tag}-{date}.md に「予備プール」として出す
  - score 1-2 / 取得失敗は除外（理由付きで記録）

採点 Workflow の出力フォーマット:
    {"scores": [{"id": "...", "score": 4, "useful": true,
                  "reason": "...", "tags": ["..."]}, ...]}

使い方:
    python scripts/inventory_review.py --fetched scripts/_inventory/fetched-construction-2026-06-16.json \
        --scores workflow_scores_1.json workflow_scores_2.json ... --tag construction
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

INV_DIR = Path(__file__).resolve().parent / "_inventory"
JST = timezone(timedelta(hours=9))


def load_scores(paths: list[Path]) -> dict[str, dict]:
    """採点 Workflow の出力（1個以上）を id => score dict に集約。"""
    out: dict[str, dict] = {}
    for p in paths:
        text = p.read_text(encoding="utf-8")
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            i, j = text.find("{"), text.rfind("}")
            if i < 0 or j <= i:
                raise
            data = json.loads(text[i:j + 1])
        if "scores" not in data and isinstance(data.get("result"), dict):
            data = data["result"]
        for s in data.get("scores", []):
            sid = s.get("id", "")
            if sid and sid not in out:
                out[sid] = s
    return out


def main():
    p = argparse.ArgumentParser(description="採点結果と fetched をマージ")
    p.add_argument("--fetched", required=True, help="inventory_fetch.py 出力 JSON")
    p.add_argument("--scores", nargs="+", required=True, help="Workflow 採点出力 JSON（複数可）")
    p.add_argument("--tag", required=True)
    p.add_argument("--min-import", type=int, default=4, help="この点以上を vault 取り込み対象に")
    p.add_argument("--min-pending", type=int, default=3, help="この点を予備プールに（既定: 3）")
    args = p.parse_args()

    INV_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(JST).strftime("%Y-%m-%d")

    fetched = json.loads(Path(args.fetched).read_text(encoding="utf-8"))
    items = fetched["items"]
    scores_by_id = load_scores([Path(p) for p in args.scores])

    reviewed = []
    pending = []
    excluded = []
    dist = {k: 0 for k in range(0, 6)}
    not_reviewed = []
    for it in items:
        sid = it.get("id", "")
        fetch_status = it.get("fetch_status", "")
        if fetch_status != "ok" and fetch_status != "fallback_tweet":
            excluded.append({**it, "score": 0, "reason_excluded": f"fetch:{fetch_status}"})
            dist[0] += 1
            continue
        if not it.get("body"):
            excluded.append({**it, "score": 0, "reason_excluded": "body_empty"})
            dist[0] += 1
            continue
        sc = scores_by_id.get(sid)
        if not sc:
            not_reviewed.append(sid)
            continue
        score = int(sc.get("score", 0))
        dist[score] = dist.get(score, 0) + 1
        record = {
            **it,
            "score": score,
            "useful": bool(sc.get("useful", False)),
            "review_reason": sc.get("reason", ""),
            "review_tags": sc.get("tags", []),
        }
        if score >= args.min_import:
            reviewed.append(record)
        elif score >= args.min_pending:
            pending.append(record)
        else:
            excluded.append({**record, "reason_excluded": f"score:{score}"})

    reviewed.sort(key=lambda x: (-x["score"], -len(x["body"])))
    pending.sort(key=lambda x: (-x["score"], -len(x["body"])))

    reviewed_path = INV_DIR / f"reviewed-{args.tag}-{today}.json"
    reviewed_path.write_text(json.dumps({
        "tag": args.tag, "generated_at": today,
        "fetched": Path(args.fetched).name,
        "min_import": args.min_import, "min_pending": args.min_pending,
        "dist": dist,
        "reviewed_for_import": reviewed,
        "pending_review": pending,
        "excluded": excluded,
        "not_reviewed_ids": not_reviewed,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    pending_md_lines = [
        f"# 予備プール（score={args.min_pending} 以上 {args.min_import} 未満）: {args.tag}（{today}）",
        "",
        f"- 件数: {len(pending)} 件 / vault 取り込みする場合は手動で判断してください",
        "- 出典: 本文を Claude が採点した上での「業界事例・トレンド寄り」記事",
        "",
    ]
    for r in pending:
        pending_md_lines.append(f"- **{r.get('review_title') or r['title']}** （{r['source']}, score={r['score']}）")
        pending_md_lines.append(f"  - {r.get('review_reason','')}")
        pending_md_lines.append(f"  - {r.get('fetch_url') or r['url']}")
    pending_md_path = INV_DIR / f"pending-review-{args.tag}-{today}.md"
    pending_md_path.write_text("\n".join(pending_md_lines) + "\n", encoding="utf-8")

    print("--- 採点結果サマリ ---")
    print(f"  分布: " + " / ".join(f"score{k}={dist.get(k,0)}" for k in (5, 4, 3, 2, 1, 0)))
    print(f"  vault 取り込み確定: {len(reviewed)} 件")
    print(f"  予備プール: {len(pending)} 件 -> {pending_md_path.name}")
    print(f"  除外: {len(excluded)} 件")
    if not_reviewed:
        print(f"  ⚠ 未採点 id: {len(not_reviewed)} 件（Workflow 採点漏れの可能性）")
        for sid in not_reviewed[:5]:
            print(f"    - {sid}")
    print(f"保存: {reviewed_path.name}")
    print("次: python scripts/inventory_import.py --reviewed {} --apply".format(reviewed_path.name))


if __name__ == "__main__":
    main()
