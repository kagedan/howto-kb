"""
inventory_prep_batches.py - 採点(Track A-2)用のバッチを用意する。

candidates-*.json から指定カテゴリを抜き出し、各記事の「タイトル＋本文スニペット」
を埋め込んだバッチファイルを作る。採点エージェントはこのバッチファイル1つを読むだけで
スコアを付けられるため、各エージェントが大量のファイルを開かずに済む
（＝サブエージェントの負荷・ロックリスクを抑える）。

使い方:
    python scripts/inventory_prep_batches.py --category construction
    python scripts/inventory_prep_batches.py --category construction --batch-size 40 --snippet 1500

出力:
    scripts/_inventory/batches/<tag>/batch_001.json ...
    （items: id/title/url/source/date_collected/snippet）
"""

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
INV_DIR = Path(__file__).resolve().parent / "_inventory"
FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


def latest_candidates() -> Path | None:
    files = sorted(glob.glob(str(INV_DIR / "candidates-*.json")))
    return Path(files[-1]) if files else None


def snippet_of(file_path: str, limit: int) -> str:
    md = REPO_ROOT / file_path
    if not md.exists():
        return ""
    try:
        text = md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""
    body = FRONTMATTER_RE.sub("", text, count=1).strip()
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body[:limit]


def main():
    p = argparse.ArgumentParser(description="採点用バッチを用意する")
    p.add_argument("--candidates", help="candidates JSON（省略時は最新を使う）")
    p.add_argument("--category", action="append", default=[],
                   help="対象カテゴリ（複数可）。省略時は全カテゴリ")
    p.add_argument("--scores", help="採点済みscores json（再採点の絞り込み用）")
    p.add_argument("--min-score", type=int, default=0,
                   help="--scores 指定時、このスコア以上のidだけを対象にする")
    p.add_argument("--batch-size", type=int, default=40)
    p.add_argument("--snippet", type=int, default=1500, help="本文スニペットの最大文字数")
    p.add_argument("--tag", help="出力サブフォルダ名（省略時はカテゴリ名から）")
    args = p.parse_args()

    cand_path = Path(args.candidates) if args.candidates else latest_candidates()
    if not cand_path or not cand_path.exists():
        print("candidates JSON が見つかりません。先に inventory_select.py を実行してください。")
        sys.exit(1)

    data = json.loads(cand_path.read_text(encoding="utf-8"))
    items = data["candidates"]
    if args.category:
        cats = set(args.category)
        items = [c for c in items if c.get("category") in cats]
    if args.scores and args.min_score:
        sc = json.loads(Path(args.scores).read_text(encoding="utf-8"))
        keep = {s["id"] for s in sc.get("items", []) if s.get("score", 0) >= args.min_score}
        before = len(items)
        items = [c for c in items if c.get("id") in keep]
        print(f"score>={args.min_score} で絞り込み: {before} -> {len(items)}件")

    tag = args.tag or ("-".join(args.category) if args.category else "all")
    out_dir = INV_DIR / "batches" / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    # 既存バッチを掃除（同タグの作り直しに対応）
    for old in out_dir.glob("batch_*.json"):
        old.unlink()

    print(f"candidates: {cand_path.name} / 対象 {len(items)}件 / tag={tag}")

    bs = args.batch_size
    n_batches = (len(items) + bs - 1) // bs
    for bi in range(n_batches):
        chunk = items[bi * bs:(bi + 1) * bs]
        batch_items = []
        for c in chunk:
            batch_items.append({
                "id": c.get("id", ""),
                "title": c.get("title", ""),
                "url": c.get("url", ""),
                "source": c.get("source", ""),
                "category": c.get("category", ""),
                "date_collected": c.get("date_collected", ""),
                "snippet": snippet_of(c.get("file_path", ""), args.snippet),
            })
        out_path = out_dir / f"batch_{bi + 1:03d}.json"
        out_path.write_text(
            json.dumps({"tag": tag, "batch": bi + 1, "n_batches": n_batches,
                        "items": batch_items}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")

    print(f"バッチ作成: {n_batches}個（1バッチ最大{bs}件） -> {out_dir}")


if __name__ == "__main__":
    main()
