"""method_d_decisions.json から adopt 分を抽出し、inventory_import.py 用 json を生成。"""
import json
from pathlib import Path

INV = Path("scripts/_inventory")
decisions = json.load(open(INV / "method_d_decisions.json", encoding="utf-8"))

TAGS = ["antigravity", "construction", "cowork", "ai-workflow", "claude-code"]

# id -> pending_review item
item_lookup = {}
for tag in TAGS:
    rd = json.load(open(INV / f"reviewed-{tag}-2026-06-16.json", encoding="utf-8"))
    for it in rd["pending_review"]:
        item_lookup[it["id"]] = it

adopt_items = []
for d in decisions:
    if d["decision"] != "adopt":
        continue
    src = item_lookup.get(d["id"])
    if not src:
        print(f"WARN: missing lookup for {d['id']}")
        continue

    item = dict(src)
    item["score"] = 4
    item["useful"] = True
    item["review_reason"] = f"[方法D] {d['reason']}"
    existing_tags = item.get("review_tags") or []
    if "method-d" not in existing_tags:
        existing_tags = list(existing_tags) + ["method-d"]
    item["review_tags"] = existing_tags
    adopt_items.append(item)

out = {
    "tag": "method-d-aggregate",
    "generated_at": "2026-06-16",
    "source": "method_d_decisions.json",
    "reviewed_for_import": adopt_items,
}

out_path = INV / "reviewed-method-d-2026-06-16.json"
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote -> {out_path}")
print(f"reviewed_for_import: {len(adopt_items)} items")

# カテゴリ別件数
by_tag = {}
for it in adopt_items:
    tag = it["id"].split("/")[0]
    by_tag[tag] = by_tag.get(tag, 0) + 1
for t, n in by_tag.items():
    print(f"  {t}: {n}")
