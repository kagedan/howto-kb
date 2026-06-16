"""score=3 (pending_review) を全カテゴリ集約してバッチ化（Workflow 投入用）。"""
import json
from pathlib import Path

INV = Path("scripts/_inventory")
BATCH_DIR = INV / "method_d_batches"
BATCH_DIR.mkdir(exist_ok=True)

for f in BATCH_DIR.glob("*.json"):
    f.unlink()

BATCH_SIZE = 5
BODY_CAP = 5000

TAGS = ["antigravity", "construction", "cowork", "ai-workflow", "claude-code"]

all_batches = []
totals = {}

for tag in TAGS:
    rpath = INV / f"reviewed-{tag}-2026-06-16.json"
    reviewed = json.load(open(rpath, encoding="utf-8"))
    pending = reviewed["pending_review"]
    totals[tag] = len(pending)

    items = []
    for it in pending:
        body = (it.get("body") or "")[:BODY_CAP]
        items.append({
            "id": it["id"],
            "tag": tag,
            "title": it.get("review_title") or it.get("title") or "",
            "url": it.get("url") or "",
            "source": it.get("source") or "",
            "body": body,
        })

    for i in range(0, len(items), BATCH_SIZE):
        batch = items[i:i + BATCH_SIZE]
        idx = len(all_batches)
        bpath = BATCH_DIR / f"batch_{idx:03d}.json"
        bpath.write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8")
        all_batches.append(bpath.name)

list_path = INV / "method_d_batch_list.json"
list_path.write_text(json.dumps(all_batches, ensure_ascii=False, indent=2), encoding="utf-8")

print("=== totals ===")
for t, n in totals.items():
    print(f"  {t}: {n}")
print(f"  total: {sum(totals.values())}")
print(f"=== batches: {len(all_batches)} (size={BATCH_SIZE}) ===")
print(f"list -> {list_path}")
