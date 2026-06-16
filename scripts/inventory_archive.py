"""
inventory_archive.py - ショートリストで [x] を付けた記事を archive/ へ退避する。

棚卸し新フロー Step ④（容量整理）:
  - かげだんが [x] を付けた / 全採用した記事は「処理を終えた」とみなす
  - vault 取り込み成否に関わらず、articles/{cat}/{file}.md を archive/{cat}/{file}.md へ移動
  - archive/ は .gitignore で除外済み（git 管理外＝ローカル退避）
  - 次回以降のクロールで articles/ には新しいものだけが残る

使い方:
    python scripts/inventory_archive.py --md scripts/_inventory/shortlist-construction-2026-06-16.md \
        --scores scripts/_inventory/scores-construction-2026-06-16.json --tag construction
    python scripts/inventory_archive.py --md ... --scores ... --tag ... --apply
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from inventory_import import normalize_url, parse_checked  # noqa: E402

ARCHIVE_DIR = REPO_ROOT / "archive"


def unique_dst(base_dir: Path, filename: str) -> Path:
    dst = base_dir / filename
    if not dst.exists():
        return dst
    stem, suf = dst.stem, dst.suffix
    i = 2
    while (base_dir / f"{stem}_{i}{suf}").exists():
        i += 1
    return base_dir / f"{stem}_{i}{suf}"


def main():
    p = argparse.ArgumentParser(description="[x] 付き記事を archive/ へ移動")
    p.add_argument("--md", required=True, help="shortlist md")
    p.add_argument("--scores", required=True, help="scores json（file_path 特定用）")
    p.add_argument("--tag", required=True, help="カテゴリ名（archive/{tag}/ に移動）")
    p.add_argument("--apply", action="store_true", help="実際に移動")
    p.add_argument("--limit", type=int, default=0)
    args = p.parse_args()

    checked = parse_checked(Path(args.md))
    if not checked:
        print("[x] の付いた項目がありません。")
        return
    if args.limit:
        checked = checked[: args.limit]

    scores = json.loads(Path(args.scores).read_text(encoding="utf-8"))["items"]
    meta_by_url = {normalize_url(m["url"]): m for m in scores}

    target_dir = ARCHIVE_DIR / args.tag
    if args.apply:
        target_dir.mkdir(parents=True, exist_ok=True)

    print(f"[x] 選択: {len(checked)} 件 / tag={args.tag} / モード: {'APPLY' if args.apply else 'dry-run'}")
    moved = skip_no_meta = skip_missing = skip_already = 0
    for idx, c in enumerate(checked, 1):
        nurl = normalize_url(c.get("url", ""))
        m = meta_by_url.get(nurl)
        if not m or not m.get("file_path"):
            skip_no_meta += 1
            continue
        rel = m["file_path"]
        src = REPO_ROOT / rel
        if not src.exists():
            skip_missing += 1
            continue
        dst_candidate = target_dir / src.name
        if dst_candidate.exists():
            skip_already += 1
            if not args.apply:
                continue
            # apply時は重複名で連番化
            dst = unique_dst(target_dir, src.name)
        else:
            dst = dst_candidate

        if not args.apply:
            moved += 1
            if moved <= 5 or moved % 500 == 0:
                print(f"  [{idx:4}/{len(checked)}] move: {rel} -> archive/{args.tag}/{src.name}")
            continue
        shutil.move(str(src), str(dst))
        moved += 1
        if moved <= 5 or moved % 500 == 0:
            print(f"  [{idx:4}/{len(checked)}] moved: {src.name}")

    print("\n--- 結果 ---")
    print(f"  移動{'予定' if not args.apply else ''}: {moved} 件")
    print(f"  skip(既に archive側): {skip_already}")
    print(f"  skip(meta未一致): {skip_no_meta}")
    print(f"  skip(本体ファイル無し): {skip_missing}")
    if args.apply:
        print(f"  移動先: {target_dir}")
    else:
        print("  問題なければ --apply を付けて再実行してください。")


if __name__ == "__main__":
    main()
