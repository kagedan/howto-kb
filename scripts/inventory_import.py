"""
inventory_import.py - reviewed.json から vault 取り込み確定分を clippings/ へ書き出す。

棚卸し新フロー Step ③:
  - reviewed-{tag}-{date}.json の "reviewed_for_import" を対象に、
    本文 (取得済み) を vault clippings/ にフロントマター付きで書き出す
  - 旧版が担っていた「[x] 拾い→本文取得→書き出し」のうち、本文取得と精査は
    inventory_fetch.py / inventory_review.py に分離した。当スクリプトは「書き出し専任」

t.co 解決系の補助関数 (extract_tco_urls / resolve_tco / is_article_url) は
inventory_fetch.py から import されているので、ここで定義したまま残す。

使い方:
    python scripts/inventory_import.py --reviewed scripts/_inventory/reviewed-construction-2026-06-16.json
    python scripts/inventory_import.py --reviewed ... --apply
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from export_clippings import sanitize_filename, escape_yaml_str  # noqa: E402

CLIPPINGS_DIR = Path(r"D:\Obsidian\kagedan-work\clippings")
SOURCES_WEB_DIR = Path(r"D:\Obsidian\kagedan-work\sources\web")
FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)
JST = timezone(timedelta(hours=9))

SNS_DOMAINS = (
    "x.com", "twitter.com", "t.co",
    "youtube.com", "youtu.be",
    "instagram.com", "facebook.com", "threads.net", "tiktok.com",
)
TCO_RE = re.compile(r"https?://t\.co/[A-Za-z0-9]+")
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def normalize_url(u: str) -> str:
    if not u:
        return ""
    u = u.strip().strip('"').strip("'").strip().strip("[]")
    u = u.split("#", 1)[0]
    if u.endswith("/"):
        u = u[:-1]
    return u.lower()


def kb_body(file_path: str) -> str:
    md = REPO_ROOT / file_path
    if not md.exists():
        return ""
    try:
        text = md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""
    return FRONTMATTER_RE.sub("", text, count=1).strip()


def parse_checked(md_path: Path) -> list[dict]:
    """shortlist md から [x] の付いた項目（title/source/url）を取り出す。"""
    checked = []
    pending = None
    head_re = re.compile(r"^- \[([ xX])\] \*\*(.*?)\*\* （(.*?)）")
    url_re = re.compile(r"^\s+- (https?://\S+)")
    for line in md_path.read_text(encoding="utf-8").splitlines():
        hm = head_re.match(line)
        if hm:
            if hm.group(1).lower() == "x":
                pending = {"title": hm.group(2), "source": hm.group(3)}
            else:
                pending = None
            continue
        if pending:
            um = url_re.match(line)
            if um:
                pending["url"] = um.group(1)
                checked.append(pending)
                pending = None
    return checked


def extract_tco_urls(body: str) -> list[str]:
    seen, out = set(), []
    for u in TCO_RE.findall(body or ""):
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def resolve_tco(tco_url: str, timeout: float = 10.0) -> str:
    try:
        r = requests.head(tco_url, allow_redirects=True, timeout=timeout, headers=HTTP_HEADERS)
        final = r.url or ""
        if final and final != tco_url and not final.startswith("https://t.co/"):
            return final
        r = requests.get(tco_url, allow_redirects=True, timeout=timeout,
                         headers=HTTP_HEADERS, stream=True)
        r.close()
        return r.url or ""
    except requests.RequestException:
        return ""


def is_article_url(url: str) -> bool:
    if not url:
        return False
    low = url.lower()
    return not any(d in low for d in SNS_DOMAINS)


def load_vault_urls() -> set[str]:
    urls = set()
    for d in (SOURCES_WEB_DIR, CLIPPINGS_DIR):
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in re.finditer(r'^(?:source|chat_url|url):\s*"?([^"\n]+)"?\s*$',
                                 text, re.MULTILINE):
                v = m.group(1).strip()
                if "http" in v:
                    urls.add(normalize_url(v))
    return urls


def unique_path(base_dir: Path, filename: str) -> Path:
    out = base_dir / filename
    if not out.exists():
        return out
    stem, suf = out.stem, out.suffix
    i = 2
    while (base_dir / f"{stem}_{i}{suf}").exists():
        i += 1
    return base_dir / f"{stem}_{i}{suf}"


def write_clipping(title: str, source_url: str, body: str, today: str,
                   review_reason: str = "", review_tags: list | None = None) -> Path:
    fname = sanitize_filename(title) + ".md"
    out = unique_path(CLIPPINGS_DIR, fname)
    tag_lines = '  - "clippings"\n  - "howto-kb-inventory"\n'
    for t in (review_tags or [])[:5]:
        tag_lines += f'  - "{escape_yaml_str(str(t))}"\n'
    reason_line = (f'review_reason: "{escape_yaml_str(review_reason)}"\n'
                   if review_reason else "")
    content = (
        "---\n"
        f'title: "{escape_yaml_str(title)}"\n'
        f'source: "{source_url}"\n'
        f"created: {today}\n"
        'source-type: "web"\n'
        f"{reason_line}"
        "tags:\n"
        f"{tag_lines}"
        "---\n\n"
        f"{body}\n"
    )
    out.write_text(content, encoding="utf-8")
    return out


def main():
    p = argparse.ArgumentParser(description="reviewed.json から vault clippings/ へ書き出し")
    p.add_argument("--reviewed", required=True, help="inventory_review.py 出力 JSON")
    p.add_argument("--apply", action="store_true", help="実際に clippings/ へ書き出す")
    p.add_argument("--limit", type=int, default=0, help="先頭N件だけ処理（0=全件）")
    args = p.parse_args()

    data = json.loads(Path(args.reviewed).read_text(encoding="utf-8"))
    items = data.get("reviewed_for_import", [])
    if args.limit:
        items = items[: args.limit]
    if not items:
        print("reviewed_for_import が空です。")
        return

    vault_urls = load_vault_urls()
    today = datetime.now(JST).strftime("%Y-%m-%d")
    if args.apply:
        CLIPPINGS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"取り込み対象: {len(items)} 件 / モード: {'APPLY' if args.apply else 'dry-run'}")
    done = skipped = failed = 0
    for it in items:
        save_url = it.get("fetch_url") or it.get("url", "")
        title = it.get("review_title") or it.get("title", "")
        body = it.get("body", "")
        n_save = normalize_url(save_url)

        if n_save and n_save in vault_urls:
            print(f"  skip(既存): score{it.get('score','?')} {title[:40]}")
            skipped += 1
            continue
        if not body:
            print(f"  FAIL(本文なし): {title[:40]}")
            failed += 1
            continue

        if not args.apply:
            print(f"  [score{it.get('score','?')}] {title[:55]} -> {save_url[:60]}")
            continue

        out = write_clipping(title, save_url, body, today,
                             review_reason=it.get("review_reason", ""),
                             review_tags=it.get("review_tags", []))
        if n_save:
            vault_urls.add(n_save)
        print(f"  -> [score{it.get('score','?')}] {out.name}")
        done += 1

    print("\n--- 結果 ---")
    if args.apply:
        print(f"書き出し: {done} 件 / 既存skip {skipped} / 失敗 {failed}")
        print(f"出力先: {CLIPPINGS_DIR}")
        print("次: vault で clippings-to-sources を実行すると sources/web/ に振り分けられます。")
    else:
        print(f"取り込み予定: {len(items) - skipped} 件 / 既存skip {skipped}")
        print("問題なければ --apply を付けて再実行してください。")


if __name__ == "__main__":
    main()
