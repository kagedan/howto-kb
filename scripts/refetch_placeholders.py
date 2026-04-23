"""refetch_placeholders.py - 本文がプレースホルダのままのX投稿MDを再取得して書き直す。

対象:
    articles/ 配下で本文が「X (Twitter) より収集。詳細は URL を参照。」のみのMD。
    2026-04-06 以前のクロールパイプラインで本文取得に失敗した残骸 (約484件)。

使い方:
    python scripts/refetch_placeholders.py              # 全件
    python scripts/refetch_placeholders.py --limit 5    # 動作確認
    python scripts/refetch_placeholders.py --dry-run    # 取得のみ、書込なし

仕組み:
    1. プレースホルダMDを抽出 → URL から tweet_id を取り出す
    2. SocialData API で statuses/show → enrich_and_format() で深掘り
    3. 元MDの id/category/file_path は維持し、title/url/date_published/description/tags を更新
    4. 取得失敗 (404/削除等) は失敗ログに残し、MDはそのまま

環境変数:
    SOCIALDATA_API_KEY (必須)
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"
PLACEHOLDER_TEXT = "X (Twitter) より収集。詳細は URL を参照。"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from crawl_x import (  # noqa: E402
    fetch_quoted_tweet,
    enrich_and_format,
    normalize_to_thread_root,
)
from _generate_mds import (  # noqa: E402
    detect_category,
    extract_tags,
    sanitize_title,
)


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
TWEET_ID_RE = re.compile(r"/status/(\d+)")


def parse_md(path: Path) -> tuple[dict, str] | None:
    """MDをfrontmatter dictと本文に分解する。"""
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    fm_text, body = m.group(1), m.group(2)
    fm: dict = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        fm[k.strip()] = v
    return fm, body


def find_placeholders() -> list[Path]:
    targets: list[Path] = []
    for md in ARTICLES_DIR.rglob("*.md"):
        try:
            text = md.read_text(encoding="utf-8")
        except OSError:
            continue
        if PLACEHOLDER_TEXT not in text:
            continue
        targets.append(md)
    return targets


def extract_tweet_id(url: str) -> str:
    m = TWEET_ID_RE.search(url or "")
    return m.group(1) if m else ""


def write_updated_md(path: Path, fm: dict, art: dict, category: str, tags: list[str]) -> None:
    """既存MDを enrich 結果で上書きする。id・category・file pathは維持。"""
    title = sanitize_title(art.get("title", ""))
    summary = art.get("description", "").strip() or PLACEHOLDER_TEXT
    tags_str = "[" + ", ".join(f'"{t}"' for t in tags) + "]"
    article_id = fm.get("id", path.stem)
    query = fm.get("query", "")

    content = f"""---
id: "{article_id}"
title: "{title}"
url: "{art.get('url', fm.get('url', ''))}"
source: "x"
category: "{category}"
tags: {tags_str}
date_published: "{art.get('date_published', '')}"
date_collected: "{fm.get('date_collected', '')}"
summary_by: "auto-x"
query: "{query}"
---

{summary}
"""
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="先頭N件のみ処理")
    parser.add_argument("--dry-run", action="store_true", help="MD書込をスキップ")
    args = parser.parse_args()

    if not os.environ.get("SOCIALDATA_API_KEY"):
        print("Error: SOCIALDATA_API_KEY is not set.", file=sys.stderr)
        return 1

    targets = find_placeholders()
    print(f"Placeholders found: {len(targets)}", file=sys.stderr)
    if args.limit > 0:
        targets = targets[: args.limit]
        print(f"  Limited to: {len(targets)}", file=sys.stderr)

    ok = 0
    not_found = 0
    no_id = 0
    errors: list[tuple[str, str]] = []

    for i, md in enumerate(targets, 1):
        parsed = parse_md(md)
        if not parsed:
            errors.append((str(md), "parse_failed"))
            continue
        fm, _body = parsed
        tweet_id = extract_tweet_id(fm.get("url", ""))
        if not tweet_id:
            no_id += 1
            errors.append((str(md), "no_tweet_id"))
            continue

        try:
            tweet = fetch_quoted_tweet(tweet_id)  # /twitter/statuses/show
        except (urllib.request.HTTPError, urllib.request.URLError, OSError) as e:
            errors.append((str(md), f"fetch_error: {e}"))
            continue

        if not tweet or not tweet.get("id_str"):
            not_found += 1
            errors.append((str(md), "tweet_not_found"))
            print(f"  [{i}/{len(targets)}] NOT FOUND id={tweet_id} ({md.name})", file=sys.stderr)
            continue

        target = normalize_to_thread_root(tweet)
        art = enrich_and_format(target)
        art["date_collected"] = fm.get("date_collected", "")

        # default_category は元MDのカテゴリを維持しつつ、本文判定で必要に応じ昇格
        original_cat = fm.get("category", "ai-workflow")
        category = detect_category(
            art.get("title", ""), art.get("description", ""), original_cat
        )
        tags = extract_tags(
            art.get("title", ""), art.get("description", ""), "x", category
        )

        if not args.dry_run:
            # カテゴリが変わった場合、新カテゴリのフォルダに書く（古い方を削除）。
            # ただし新カテゴリに同名ファイルが既にある場合は衝突回避のため
            # 元カテゴリのままで上書きする（既存記事を上書きしない）。
            if category != original_cat:
                new_path = ARTICLES_DIR / category / md.name
                if new_path.exists():
                    category = original_cat  # 衝突回避
                    write_updated_md(md, fm, art, category, tags)
                else:
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    write_updated_md(new_path, fm, art, category, tags)
                    md.unlink()
                    md = new_path
            else:
                write_updated_md(md, fm, art, category, tags)

        ok += 1
        if i % 25 == 0 or i == len(targets):
            print(
                f"  [{i}/{len(targets)}] ok={ok} not_found={not_found} no_id={no_id}",
                file=sys.stderr,
            )

    print(
        f"\nDone. ok={ok} not_found={not_found} no_id={no_id} errors={len(errors)}",
        file=sys.stderr,
    )

    if errors:
        log_path = REPO_ROOT / "_progress" / "refetch_placeholders_errors.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Errors logged to: {log_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
