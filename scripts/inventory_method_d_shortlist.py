"""method_d_decisions.json から adopt 分の shortlist md を生成（user 確認用）。"""
import json
from pathlib import Path

INV = Path("scripts/_inventory")
decisions = json.load(open(INV / "method_d_decisions.json", encoding="utf-8"))

TAGS = ["antigravity", "construction", "cowork", "ai-workflow", "claude-code"]

# id -> 元アイテム参照（title/url/source 取得用）
item_lookup = {}
for tag in TAGS:
    rd = json.load(open(INV / f"reviewed-{tag}-2026-06-16.json", encoding="utf-8"))
    for it in rd["pending_review"]:
        item_lookup[it["id"]] = it

adopt_by_tag = {t: [] for t in TAGS}
for d in decisions:
    if d["decision"] != "adopt":
        continue
    tag = d["id"].split("/")[0]
    if tag not in adopt_by_tag:
        continue
    it = item_lookup.get(d["id"])
    if not it:
        continue
    adopt_by_tag[tag].append({
        "id": d["id"],
        "title": it.get("review_title") or it.get("title") or "",
        "url": it.get("url") or "",
        "source": it.get("source") or "",
        "confidence": d["confidence"],
        "reason": d["reason"],
    })

out_md = INV / "method_d_adopt-2026-06-16.md"
lines = [
    "# 方法D 採用候補（Sonnet 厳しめ判定）2026-06-16",
    "",
    "score=3 (658件) を Sonnet で本文ベース再判定。**adopt 70件**を以下に列挙。",
    "",
    "- `[x]` のまま残すと採用、`[ ]` に戻すと除外。デフォルト全件 `[x]`。",
    "- 確認後、`inventory_import.py` で vault に投入する。",
    "",
]

for tag in TAGS:
    items = adopt_by_tag[tag]
    if not items:
        continue
    lines.append(f"## {tag}（{len(items)} 件）\n")
    items.sort(key=lambda x: -x["confidence"])
    for it in items:
        lines.append(f"- [x] **{it['title']}** （{it['source']}, conf={it['confidence']:.2f}）")
        lines.append(f"  - {it['reason']}")
        lines.append(f"  - {it['url']}")
    lines.append("")

out_md.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote -> {out_md}")
print(f"adopt total: {sum(len(v) for v in adopt_by_tag.values())}")
for t, v in adopt_by_tag.items():
    print(f"  {t}: {len(v)}")
