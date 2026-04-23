"""refetch_rss_fulltext.py - RSS系記事の本文を readability で再取得して書き直す。

対象:
    index.json で source != "x" の記事 (note/zenn/qiita/rss/anthropic 等)。
    既存MDの本文がフィード由来の要約 (50〜500文字) しかないものを、記事URLから
    readability で本文抽出して上書きする。

使い方:
    python scripts/refetch_rss_fulltext.py --dry-run --limit 10                 # 動作確認
    python scripts/refetch_rss_fulltext.py --dry-run --sources zenn,qiita -l 5  # ソース絞り
    python scripts/refetch_rss_fulltext.py                                       # 全件本実行
    python scripts/refetch_rss_fulltext.py --sources note                        # noteのみ

オプション:
    --limit N       先頭N件のみ
    --sources       カンマ区切り (note,zenn,qiita,rss,anthropic)
    --dry-run       書き込まず取得結果のサマリのみ出力
    --min-len N     本文N文字未満の場合は更新スキップ (デフォルト 100)

依存:
    pip install readability-lxml markdownify
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "index.json"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from export_clippings import fetch_article_markdown  # noqa: E402

FRONTMATTER_RE = re.compile(r"^(---\n.*?\n---\n)(.*)$", re.DOTALL)
EXCLUDE_SOURCES = {"x", "notebooklm"}

RATE_LIMIT_SEC = 1.0
_last_request = 0.0


def rate_limit() -> None:
    global _last_request
    elapsed = time.time() - _last_request
    if elapsed < RATE_LIMIT_SEC:
        time.sleep(RATE_LIMIT_SEC - elapsed)
    _last_request = time.time()


def split_md(text: str) -> tuple[str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return "", text
    return m.group(1), m.group(2)


def replace_body(path: Path, new_body: str) -> None:
    text = path.read_text(encoding="utf-8")
    fm, _ = split_md(text)
    if not fm:
        return
    path.write_text(fm + "\n" + new_body.strip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", "-l", type=int, default=0)
    parser.add_argument("--sources", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--min-len", type=int, default=100,
                        help="新規取得した本文がこの文字数未満ならスキップ")
    parser.add_argument("--skip-existing", type=int, default=1000,
                        help="既存MDの本文がこの文字数以上ならAPIコールせずスキップ (idempotent)")
    args = parser.parse_args()

    sources_filter: set[str] = set()
    if args.sources:
        sources_filter = {s.strip() for s in args.sources.split(",") if s.strip()}

    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    targets: list[dict] = []
    for a in data["articles"]:
        src = a.get("source", "")
        if src in EXCLUDE_SOURCES:
            continue
        if sources_filter and src not in sources_filter:
            continue
        if not a.get("url") or not a.get("file_path"):
            continue
        targets.append(a)

    if args.limit > 0:
        targets = targets[: args.limit]

    print(f"Targets: {len(targets)}", file=sys.stderr)

    ok = 0
    too_short = 0
    fetch_failed = 0
    skipped = 0
    summary_rows: list[dict] = []

    for i, a in enumerate(targets, 1):
        url = a["url"]
        path = REPO_ROOT / a["file_path"]
        if not path.exists():
            continue

        # 既存本文が十分に長ければスキップ (idempotent)
        existing = path.read_text(encoding="utf-8")
        _, existing_body = split_md(existing)
        if len(existing_body.strip()) >= args.skip_existing:
            skipped += 1
            continue

        rate_limit()
        try:
            result = fetch_article_markdown(url)
        except Exception as e:
            fetch_failed += 1
            summary_rows.append({"i": i, "url": url, "src": a.get("source"),
                                  "result": f"exception: {e}"})
            print(f"  [{i}/{len(targets)}] EXC {a.get('source')}: {e}", file=sys.stderr)
            continue

        if not result:
            fetch_failed += 1
            summary_rows.append({"i": i, "url": url, "src": a.get("source"),
                                  "result": "fetch_failed"})
            print(f"  [{i}/{len(targets)}] FAIL {a.get('source')}: {url}", file=sys.stderr)
            continue

        body = (result.get("body") or "").strip()
        body_len = len(body)

        if body_len < args.min_len:
            too_short += 1
            summary_rows.append({"i": i, "url": url, "src": a.get("source"),
                                  "result": f"too_short ({body_len})",
                                  "title": (result.get("title") or "")[:60]})
            print(f"  [{i}/{len(targets)}] SHORT {a.get('source')}: {body_len}文字", file=sys.stderr)
            continue

        if not args.dry_run:
            replace_body(path, body)

        ok += 1
        summary_rows.append({"i": i, "url": url, "src": a.get("source"),
                              "result": f"ok ({body_len})",
                              "title": (result.get("title") or "")[:60]})
        if i % 25 == 0 or i == len(targets):
            print(f"  [{i}/{len(targets)}] ok={ok} short={too_short} fail={fetch_failed} skip={skipped}",
                  file=sys.stderr)

    print(f"\nDone. ok={ok} too_short={too_short} fetch_failed={fetch_failed} skipped={skipped}",
          file=sys.stderr)

    log_path = REPO_ROOT / "_progress" / "refetch_rss_summary.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(summary_rows, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(f"Summary: {log_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
