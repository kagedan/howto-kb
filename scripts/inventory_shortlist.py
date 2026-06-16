"""
inventory_shortlist.py - 採点結果(workflow出力)を保存し、ショートリストを作る。

採点ワークフローが返した JSON（scores 配列）を candidates のメタ情報と結合して、
  - scores-<tag>-YYYY-MM-DD.json  … 全採点結果（永続化・再実行回避）
  - shortlist-<tag>-YYYY-MM-DD.md … 承認用チェックリスト（score>=min）
を出力する。LLM は使わない（純粋なデータ整形）。

使い方:
    python scripts/inventory_shortlist.py --scores <workflow出力JSON> --tag construction
    python scripts/inventory_shortlist.py --scores ... --tag construction --min 4
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

INV_DIR = Path(__file__).resolve().parent / "_inventory"
JST = timezone(timedelta(hours=9))


def latest_candidates() -> Path | None:
    files = sorted(glob.glob(str(INV_DIR / "candidates-*.json")))
    return Path(files[-1]) if files else None


def load_result_json(path: Path) -> dict:
    """workflow出力ファイルを読む。純粋JSONでなければ最初の{〜最後の}を試す。"""
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        i, j = text.find("{"), text.rfind("}")
        if i >= 0 and j > i:
            return json.loads(text[i:j + 1])
        raise


def main():
    p = argparse.ArgumentParser(description="採点結果を保存しショートリストを作る")
    p.add_argument("--scores", required=True, help="採点ワークフローの出力JSON")
    p.add_argument("--candidates", help="candidates JSON（省略時は最新）")
    p.add_argument("--tag", default="construction")
    p.add_argument("--min", type=int, default=4, help="ショートリストに載せる最小スコア")
    args = p.parse_args()

    result = load_result_json(Path(args.scores))
    # タスクのエンベロープ（summary/result/logs...）なら result を剥がす
    if "scores" not in result and isinstance(result.get("result"), dict):
        result = result["result"]
    scores = result.get("scores", [])
    score_by_id = {}
    for s in scores:
        sid = s.get("id", "")
        if sid and sid not in score_by_id:
            score_by_id[sid] = s

    cand_path = Path(args.candidates) if args.candidates else latest_candidates()
    cand = json.loads(cand_path.read_text(encoding="utf-8"))
    meta_by_id = {c["id"]: c for c in cand["candidates"]}

    # 結合（採点された候補のみ）
    merged = []
    for sid, s in score_by_id.items():
        m = meta_by_id.get(sid)
        if not m or m.get("category") != args.tag and args.tag != "all":
            # tag フィルタ（candidates 側 category と一致するもの）
            if m is None:
                continue
        if m is None:
            continue
        merged.append({
            "id": sid,
            "score": s.get("score", 0),
            "useful": s.get("useful", False),
            "reason": s.get("reason", ""),
            "tags": s.get("tags", []),
            "title": m.get("title", ""),
            "url": m.get("url", ""),
            "source": m.get("source", ""),
            "category": m.get("category", ""),
            "date_collected": m.get("date_collected", ""),
            "file_path": m.get("file_path", ""),
        })

    merged.sort(key=lambda x: (-x["score"], x.get("date_collected", "")), reverse=False)
    # 上は score 降順 / 日付昇順になってしまうので作り直し
    merged.sort(key=lambda x: (x["score"], x.get("date_collected", "")), reverse=True)

    today = datetime.now(JST).strftime("%Y-%m-%d")
    scored_total = len(merged)
    cand_total = sum(1 for c in cand["candidates"]
                     if c.get("category") == args.tag or args.tag == "all")
    not_scored = cand_total - scored_total

    dist = {k: 0 for k in range(1, 6)}
    for m in merged:
        v = m["score"]
        if v in dist:
            dist[v] += 1

    # 永続化: scores json
    scores_path = INV_DIR / f"scores-{args.tag}-{today}.json"
    scores_path.write_text(json.dumps({
        "tag": args.tag, "generated_at": today,
        "scored_total": scored_total, "not_scored": not_scored,
        "dist": dist, "items": merged,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ショートリスト md
    lines = []
    lines.append(f"# 棚卸しショートリスト: {args.tag}（{today}）")
    lines.append("")
    lines.append(f"- 採点: {scored_total}件（未採点 {not_scored}件） / "
                 f"score5={dist[5]} score4={dist[4]} score3={dist[3]} "
                 f"score2={dist[2]} score1={dist[1]}")
    lines.append("- **取り込むものの `[ ]` を `[x]` にして保存してください。**")
    lines.append("- 取り込み対象 = vault の sources/web に「元URL再取得→マークダウン化」で保存します。")
    lines.append("")

    def emit(score, heading):
        rows = [m for m in merged if m["score"] == score]
        if not rows:
            return
        lines.append(f"## スコア{score}（{heading}）{len(rows)}件")
        lines.append("")
        for m in rows:
            tg = " ".join(f"#{t}" for t in (m.get("tags") or [])[:3])
            lines.append(f"- [ ] **{m['title']}** （{m['source']}）")
            lines.append(f"  - {m['reason']}　{tg}")
            lines.append(f"  - {m['url']}")
        lines.append("")

    emit(5, "保存必須級")
    if args.min <= 4:
        emit(4, "有益")
    if args.min <= 3:
        emit(3, "関連はするが一般的")

    md_path = INV_DIR / f"shortlist-{args.tag}-{today}.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"採点結果: {scored_total}件（未採点 {not_scored}件）")
    print(f"分布: score5={dist[5]} score4={dist[4]} score3={dist[3]} score2={dist[2]} score1={dist[1]}")
    print(f"保存: {scores_path.name}")
    print(f"ショートリスト: {md_path}")


if __name__ == "__main__":
    main()
