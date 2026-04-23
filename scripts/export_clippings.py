"""
export_clippings.py - RT記事からObsidian clippings用のMarkdownを生成する。

使い方:
    echo '[...JSON...]' | python scripts/export_clippings.py

処理:
    1. stdinからcrawl_x.py形式のJSONを受け取る
    2. RT記事（is_retweet == True）のみ処理
    3. 外部リンクあり → readabilityで全文取得 → Web記事フォーマットで出力
    4. 外部リンクなし → Clipperフォーマット（X投稿用）で出力
    5. D:\\Obsidian\\kagedan-work\\clippings\\ にMDファイルを保存

出力先:
    D:\\Obsidian\\kagedan-work\\clippings\\

依存パッケージ:
    pip install readability-lxml markdownify pyyaml
"""

import html
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

# Windows環境でのcp932文字化け対策
os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")
if sys.stdin and hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

CLIPPINGS_DIR = Path(r"D:\Obsidian\kagedan-work\clippings")
SOURCES_WEB_DIR = Path(r"D:\Obsidian\kagedan-work\sources\web")

# Windows ファイル名禁止文字
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


# --- HTML取得 ---

def fetch_html(url: str) -> str | None:
    """URLからHTMLを取得（UTF-8で）。"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ja,en;q=0.5",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            charset = resp.headers.get_content_charset()
            if charset:
                return raw.decode(charset, errors="replace")
            partial = raw[:2000].decode("ascii", errors="replace")
            m = re.search(r'charset=["\']?([^"\';\s>]+)', partial, re.IGNORECASE)
            if m:
                return raw.decode(m.group(1), errors="replace")
            return raw.decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  HTML fetch failed ({url}): {e}", file=sys.stderr)
        return None


def extract_og_tags(html_text: str) -> dict:
    """HTMLからOGタグ（og:title, og:description）を抽出。"""
    result = {}
    m = re.search(
        r'<meta\s+(?:[^>]*?\s+)?(?:property|name)=["\']og:title["\']\s+content=["\']([^"\']*)["\']',
        html_text, re.IGNORECASE)
    if not m:
        m = re.search(
            r'<meta\s+content=["\']([^"\']*?)["\']\s+(?:property|name)=["\']og:title["\']',
            html_text, re.IGNORECASE)
    if m:
        result["title"] = html.unescape(m.group(1))

    m = re.search(
        r'<meta\s+(?:[^>]*?\s+)?(?:property|name)=["\']og:description["\']\s+content=["\']([^"\']*)["\']',
        html_text, re.IGNORECASE)
    if not m:
        m = re.search(
            r'<meta\s+content=["\']([^"\']*?)["\']\s+(?:property|name)=["\']og:description["\']',
            html_text, re.IGNORECASE)
    if m:
        result["description"] = html.unescape(m.group(1))

    if "title" not in result:
        m = re.search(r'<title[^>]*>([^<]+)</title>', html_text, re.IGNORECASE)
        if m:
            result["title"] = html.unescape(m.group(1).strip())

    if "description" not in result:
        m = re.search(
            r'<meta\s+(?:[^>]*?\s+)?name=["\']description["\']\s+content=["\']([^"\']*)["\']',
            html_text, re.IGNORECASE)
        if not m:
            m = re.search(
                r'<meta\s+content=["\']([^"\']*?)["\']\s+name=["\']description["\']',
                html_text, re.IGNORECASE)
        if m:
            result["description"] = html.unescape(m.group(1))

    return result


# --- 全文取得 ---

def fetch_article_markdown(url: str) -> dict | None:
    """外部URLからreadabilityで本文を取得しMarkdownに変換する。

    Returns:
        {"title": str, "body": str, "description": str} or None
    """
    from readability import Document
    from markdownify import markdownify as md

    html_text = fetch_html(url)
    if not html_text:
        return None

    try:
        doc = Document(html_text)
        title = doc.short_title() or ""
        content_html = doc.summary()
    except Exception as e:
        print(f"  readability failed ({url}): {e}", file=sys.stderr)
        # OGタグにフォールバック
        og = extract_og_tags(html_text)
        if og.get("title"):
            desc = og.get("description", "")
            return {
                "title": og["title"],
                "body": f"{desc}\n\n元記事: {url}",
                "description": desc[:120] if desc else og["title"][:120],
            }
        return None

    # HTML → Markdown 変換
    body = md(content_html, heading_style="ATX", strip=["script", "style"])
    # 過剰な空行を正規化
    body = re.sub(r"\n{3,}", "\n\n", body).strip()

    if not body or len(body) < 30:
        # 本文が短すぎる場合OGタグフォールバック
        og = extract_og_tags(html_text)
        if og.get("title"):
            title = title or og["title"]
        desc = og.get("description", "")
        if desc:
            body = f"{desc}\n\n元記事: {url}"

    if not title:
        og = extract_og_tags(html_text)
        title = og.get("title", "")

    description = re.sub(r"\s+", " ", body[:120]).strip() if body else ""

    return {"title": title, "body": body, "description": description}


# --- ファイル名生成 ---

def sanitize_filename(name: str, max_len: int = 200) -> str:
    """Windowsで安全なファイル名を生成する。"""
    name = INVALID_FILENAME_CHARS.sub("", name)
    name = name.replace("\n", " ").replace("\r", "")
    name = re.sub(r"\s+", " ", name).strip()
    name = name.strip(". ")
    if len(name) > max_len:
        name = name[:max_len].rstrip(". ")
    return name or "untitled"


# --- 重複チェック ---

def load_existing_sources(dirs: list[Path]) -> set[str]:
    """既存MDファイルのfrontmatterからsource URLを収集する。"""
    urls = set()
    for d in dirs:
        if not d.exists():
            continue
        for md_file in d.glob("*.md"):
            try:
                text = md_file.read_text(encoding="utf-8", errors="replace")
                # frontmatter の source: を抽出
                m = re.search(r'^source:\s*"?([^"\n]+)"?\s*$', text, re.MULTILINE)
                if m:
                    urls.add(m.group(1).strip())
            except Exception:
                continue
    return urls


# --- frontmatter 生成 ---

def escape_yaml_str(s: str) -> str:
    """YAML double-quoted value 内で安全に使える文字列にする。"""
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    s = s.replace("\n", " ").replace("\r", "").replace("\t", " ")
    return re.sub(r"\s+", " ", s).strip()


def make_description(text: str) -> str:
    """descriptionを生成する（必ず何か返す）。"""
    desc = re.sub(r"\s+", " ", text).strip()
    desc = desc[:120]
    return desc if desc else "(内容なし)"


# --- パターンA: Web記事フォーマット ---

def write_web_article(article: dict, fetched: dict, today: str) -> Path | None:
    """外部記事をWeb記事フォーマットで出力する。"""
    title = fetched["title"] or sanitize_filename(article.get("title", "untitled"))
    author = article.get("title", "").split(":")[0].strip("@ ") if article.get("title") else ""
    published = article.get("date_published", "")
    description = escape_yaml_str(fetched["description"])
    source_url = article["external_urls"][0]

    filename = sanitize_filename(title) + ".md"
    out_path = CLIPPINGS_DIR / filename

    if out_path.exists():
        return None

    content = f'''---
title: "{escape_yaml_str(title)}"
source: "{source_url}"
author:
  - "[[@{author}]]"
published: {published}
created: {today}
description: "{description}"
tags:
  - "clippings"
---

{fetched["body"]}
'''
    out_path.write_text(content, encoding="utf-8")
    return out_path


# --- パターンC: X Article（長文記事） ---

def write_x_article(article: dict, today: str) -> Path | None:
    """X の Article 投稿を Web記事フォーマットで出力する。

    source は X のツイートURL、author は投稿者。cover_url があれば本文先頭に配置。
    """
    art_info = article.get("article") or {}
    title = art_info.get("title") or ""
    body_md = art_info.get("body_markdown") or ""
    cover_url = art_info.get("cover_url") or ""
    preview = art_info.get("preview_text") or ""

    if not title and not body_md:
        return None

    author = ""
    m = re.match(r"@(\w+):", article.get("title", ""))
    if m:
        author = m.group(1)

    tweet_url = article.get("url", "")
    published = article.get("date_published", "")
    desc_source = preview or body_md
    description = escape_yaml_str(make_description(desc_source))

    filename = sanitize_filename(title or f"{author}_article") + ".md"
    out_path = CLIPPINGS_DIR / filename

    if out_path.exists():
        return None

    body_parts = []
    if cover_url:
        body_parts.append(f"![cover]({cover_url})")
        body_parts.append("")
    if body_md:
        body_parts.append(body_md)

    body = "\n".join(body_parts).strip()

    content = f'''---
title: "{escape_yaml_str(title)}"
source: "{tweet_url}"
author:
  - "[[@{author}]]"
published: {published}
created: {today}
description: "{description}"
tags:
  - "clippings"
---

{body}
'''
    out_path.write_text(content, encoding="utf-8")
    return out_path


# --- パターンB: X投稿 Clipperフォーマット ---

def write_x_post(article: dict, today: str) -> Path | None:
    """X投稿をClipperフォーマットで出力する。"""
    tweet_url = article.get("url", "")
    description_text = article.get("description", "")

    # 投稿者名を抽出
    author = ""
    m = re.match(r"@(\w+):", article.get("title", ""))
    if m:
        author = m.group(1)

    # 日時のパース（tweet_datetime から HH:mm を取得）
    tweet_dt = article.get("tweet_datetime", "")
    dt_display = ""
    if tweet_dt:
        try:
            # "Wed Mar 25 07:44:00 +0000 2026" 形式のパース
            parsed = datetime.strptime(tweet_dt, "%a %b %d %H:%M:%S %z %Y")
            dt_display = parsed.strftime("%Y-%m-%d %H%M")
        except (ValueError, TypeError):
            pass
    if not dt_display:
        pub = article.get("date_published", today)
        dt_display = f"{pub} 0000"

    title = f"{author}({dt_display})"
    published = article.get("date_published", "")
    description = escape_yaml_str(make_description(description_text))

    # 画像
    image_urls = article.get("image_urls", [])
    image_line = f'\nimage: "{image_urls[0]}"' if image_urls else ""

    filename = sanitize_filename(title) + ".md"
    out_path = CLIPPINGS_DIR / filename

    if out_path.exists():
        return None

    # twitframe URL（twitter.com 形式に変換）
    twitframe_url = tweet_url.replace("x.com", "twitter.com")

    # 本文組み立て
    body_parts = []
    body_parts.append(
        f"<iframe border=0 frameborder=0 width='400px' height='600px' "
        f"src='https://twitframe.com/show?url={twitframe_url}'></iframe>"
    )
    for img in image_urls:
        body_parts.append(f"\n![画像]({img})")
    body_parts.append(f"\n{description_text}")

    body = "\n".join(body_parts)

    content = f'''---
title: "{escape_yaml_str(title)}"
source: "{tweet_url}"
author:
  - "{author}"
published: {published}
created: {today}
description: "{description}"{image_line}
tags:
  - "clippings"
---
{body}
'''
    out_path.write_text(content, encoding="utf-8")
    return out_path


# --- メイン ---

def main():
    # stdin から JSON を読み込む（バイナリモードで読みUTF-8デコード）
    raw = sys.stdin.buffer.read().decode("utf-8")
    if not raw.strip():
        print("No input.", file=sys.stderr)
        return

    try:
        articles = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(articles, list):
        print("Input must be a JSON array.", file=sys.stderr)
        sys.exit(1)

    # RT記事のみフィルタ
    rt_articles = [a for a in articles if a.get("is_retweet")]
    if not rt_articles:
        print("No RT articles to process.", file=sys.stderr)
        return

    # 出力先の存在確認
    CLIPPINGS_DIR.mkdir(parents=True, exist_ok=True)

    # 重複チェック用: clippings/ と sources/web/ の既存source URLを収集
    existing_sources = load_existing_sources([CLIPPINGS_DIR, SOURCES_WEB_DIR])

    today = datetime.now().strftime("%Y-%m-%d")
    written = 0
    skipped = 0
    errors = 0

    for art in rt_articles:
        tweet_url = art.get("url", "")
        external_urls = art.get("external_urls", [])
        has_article = bool((art.get("article") or {}).get("body_markdown"))

        # 重複チェック（ツイートURL and 外部URL）
        if tweet_url in existing_sources:
            skipped += 1
            continue
        if external_urls and external_urls[0] in existing_sources:
            skipped += 1
            continue

        if has_article:
            # パターンC: X Article（長文記事）を Web記事フォーマットで出力
            result = write_x_article(art, today)
            if result:
                print(f"  -> {result.name}", file=sys.stderr)
                written += 1
            else:
                # 出力失敗 → X投稿フォーマットにフォールバック
                result = write_x_post(art, today)
                if result:
                    print(f"  -> {result.name} (fallback)", file=sys.stderr)
                    written += 1
                else:
                    skipped += 1
        elif external_urls:
            # パターンA: 外部記事の全文取得
            ext_url = external_urls[0]
            print(f"  Fetching: {ext_url}", file=sys.stderr)
            fetched = fetch_article_markdown(ext_url)

            if fetched and fetched.get("body"):
                result = write_web_article(art, fetched, today)
                if result:
                    print(f"  -> {result.name}", file=sys.stderr)
                    written += 1
                else:
                    skipped += 1
            else:
                # フォールバック: X投稿本文で保存
                print(f"  Fallback to X post format: {ext_url}", file=sys.stderr)
                result = write_x_post(art, today)
                if result:
                    print(f"  -> {result.name}", file=sys.stderr)
                    written += 1
                else:
                    errors += 1
        else:
            # パターンB: X投稿のClipperフォーマット
            result = write_x_post(art, today)
            if result:
                print(f"  -> {result.name}", file=sys.stderr)
                written += 1
            else:
                skipped += 1

    print(f"\nClippings: {written} written, {skipped} skipped, {errors} errors",
          file=sys.stderr)


if __name__ == "__main__":
    main()
