"""
inventory_import.py - ショートリストで [x] を付けた記事を vault に取り込む。

shortlist-*.md の中で `- [x]` が付いた項目だけを対象に、
  - web記事 (source != x) … 元URLを readability で再取得しマークダウン化
  - X投稿   (source == x) … KB に既にある本文(ツイート全文)を流用
vault の clippings/ にフロントマター付きで書き出す（その後 clippings-to-sources が
sources/web/ に振り分ける）。重複(URL一致)は自動でスキップ。LLM は使わない。

使い方:
    python scripts/inventory_import.py --md scripts/_inventory/shortlist-construction-2026-06-16.md \
        --scores scripts/_inventory/scores-construction-2026-06-16.json            # dry-run（何を入れるか表示）
    python scripts/inventory_import.py --md ... --scores ... --apply               # 実際に書き出す
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# web記事の本文取得は export_clippings の実績ある実装を再利用（readability+markdownify）
from export_clippings import fetch_article_markdown, sanitize_filename, escape_yaml_str  # noqa: E402

CLIPPINGS_DIR = Path(r"D:\Obsidian\kagedan-work\clippings")
SOURCES_WEB_DIR = Path(r"D:\Obsidian\kagedan-work\sources\web")
FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)
JST = timezone(timedelta(hours=9))


def normalize_url(u: str) -> str:
    if not u:
        return ""
    u = u.strip().strip('"').strip("'").strip().strip("[]")
    u = u.split("#", 1)[0]
    if u.endswith("/"):
        u = u[:-1]
    return u.lower()


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


def kb_body(file_path: str) -> str:
    md = REPO_ROOT / file_path
    if not md.exists():
        return ""
    try:
        text = md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""
    return FRONTMATTER_RE.sub("", text, count=1).strip()


def unique_path(base_dir: Path, filename: str) -> Path:
    out = base_dir / filename
    if not out.exists():
        return out
    stem, suf = out.stem, out.suffix
    i = 2
    while (base_dir / f"{stem}_{i}{suf}").exists():
        i += 1
    return base_dir / f"{stem}_{i}{suf}"


def write_clipping(title: str, source_url: str, body: str, today: str) -> Path:
    fname = sanitize_filename(title) + ".md"
    out = unique_path(CLIPPINGS_DIR, fname)
    content = (
        "---\n"
        f'title: "{escape_yaml_str(title)}"\n'
        f'source: "{source_url}"\n'
        f"created: {today}\n"
        'source-type: "web"\n'
        "tags:\n"
        '  - "clippings"\n'
        "---\n\n"
        f"{body}\n"
    )
    out.write_text(content, encoding="utf-8")
    return out


def main():
    p = argparse.ArgumentParser(description="ショートリストの[x]をvaultに取り込む")
    p.add_argument("--md", required=True, help="shortlist md")
    p.add_argument("--scores", required=True, help="scores json（id/file_path等の照合用）")
    p.add_argument("--apply", action="store_true", help="実際に clippings/ へ書き出す")
    p.add_argument("--limit", type=int, default=0, help="先頭N件だけ処理（0=全件）")
    args = p.parse_args()

    checked = parse_checked(Path(args.md))
    if not checked:
        print("[x] の付いた項目がありません。md に [x] を付けて保存してください。")
        return

    scores = json.loads(Path(args.scores).read_text(encoding="utf-8"))["items"]
    meta_by_url = {normalize_url(m["url"]): m for m in scores}

    vault_urls = load_vault_urls()
    if args.limit:
        checked = checked[: args.limit]

    print(f"[x] 選択: {len(checked)}件 / モード: {'APPLY' if args.apply else 'dry-run'}")
    today = datetime.now(JST).strftime("%Y-%m-%d")
    if args.apply:
        CLIPPINGS_DIR.mkdir(parents=True, exist_ok=True)

    done = skipped = failed = 0
    web_n = x_n = 0
    for c in checked:
        nurl = normalize_url(c.get("url", ""))
        m = meta_by_url.get(nurl)
        source = (m or {}).get("source", c.get("source", ""))
        title = (m or {}).get("title", c.get("title", ""))

        if nurl in vault_urls:
            print(f"  skip(既存): {title[:40]}")
            skipped += 1
            continue

        is_x = source == "x"
        tag = "X" if is_x else "web"
        if not args.apply:
            print(f"  [{tag}] {title[:50]}")
            (x_n := x_n + 1) if is_x else (web_n := web_n + 1)
            continue

        # 本文を用意
        if is_x:
            body = kb_body((m or {}).get("file_path", ""))
        else:
            fetched = fetch_article_markdown(c["url"])
            if fetched and fetched.get("body"):
                body = fetched["body"]
                if fetched.get("title"):
                    title = fetched["title"]
            else:
                body = kb_body((m or {}).get("file_path", ""))  # フォールバック
        if not body:
            print(f"  FAIL(本文なし): {title[:40]}")
            failed += 1
            continue

        out = write_clipping(title, c["url"], body, today)
        vault_urls.add(nurl)
        print(f"  -> [{tag}] {out.name}")
        done += 1
        x_n += 1 if is_x else 0
        web_n += 0 if is_x else 1

    print("\n--- 結果 ---")
    if args.apply:
        print(f"書き出し: {done}件（web {web_n} / X {x_n}） / 既存skip {skipped} / 失敗 {failed}")
        print(f"出力先: {CLIPPINGS_DIR}")
        print("次: vault で clippings-to-sources を実行すると sources/web/ に振り分けられます。")
    else:
        print(f"取り込み予定: {len(checked) - skipped}件（web {web_n} / X {x_n}） / 既存skip {skipped}")
        print("問題なければ --apply を付けて再実行してください。")


if __name__ == "__main__":
    main()
