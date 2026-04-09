"""
fix_garbled.py - 文字化け記事を元URLから再取得して修正する。

使い方:
    python scripts/fix_garbled.py              # dry-run（確認のみ）
    python scripts/fix_garbled.py --apply      # 実際に修正

処理:
    1. _garbled_articles.json から文字化け記事リストを読み込む
    2. X記事: SocialData API でツイート本文を再取得
    3. zenn/qiita/note/rss: HTTP GETでHTMLを取得、OGタグからタイトル・説明を抽出
    4. MDファイルを正しいテキストで上書き再生成
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# Windows環境でのcp932文字化け対策
os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"
GARBLED_PATH = REPO_ROOT / "_garbled_articles.json"

SOCIALDATA_BASE_URL = "https://api.socialdata.tools"
RATE_LIMIT_INTERVAL = 0.6
_last_request_time = 0.0

# --- カテゴリ・タグ判定（_generate_mds.py と同じ） ---

CATEGORY_RULES = [
    ("claude-code", [
        "claude code", "claude.md", "claude-code", "handover", "コンテキスト管理",
        "context window", "mcp server", "hooks", "subagent", "claude_code",
    ]),
    ("cowork", [
        "cowork", "desktop automation", "デスクトップ自動化",
    ]),
    ("antigravity", [
        "antigravity", "vscode拡張", "vscode extension",
    ]),
    ("construction", [
        "土木", "建設", "施工", "工事", "配管", "水道", "下水", "公共工事",
        "construction", "civil engineering", "infrastructure",
    ]),
]


def detect_category(title: str, description: str, default_category: str) -> str:
    text = (title + " " + description).lower()
    for cat, keywords in CATEGORY_RULES:
        if any(kw.lower() in text for kw in keywords):
            return cat
    return default_category


def extract_tags(title: str, description: str, source: str, category: str) -> list[str]:
    tags = []
    text = (title + " " + description).lower()
    tag_map = {
        "claude code": "claude-code", "claude.md": "CLAUDE-md", "mcp": "MCP",
        "prompt": "prompt-engineering", "api": "API", "agent": "AI-agent",
        "llm": "LLM", "openai": "OpenAI", "gemini": "Gemini", "gpt": "GPT",
        "cowork": "cowork", "antigravity": "antigravity", "vscode": "VSCode",
        "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
        "土木": "civil-engineering", "建設": "construction",
        "配管": "piping", "水道": "waterworks", "施工": "construction-mgmt",
    }
    for keyword, tag in tag_map.items():
        if keyword.lower() in text and tag not in tags:
            tags.append(tag)
    if source and source not in ("", "unknown"):
        tags.append(source)
    return tags[:6]


def sanitize_title(title: str) -> str:
    title = title.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").replace("\t", " ")
    title = title.replace('\\"', "")
    title = title.replace('"', "")
    title = title.replace("\\", "")
    title = re.sub(r"\s+", " ", title).strip()
    return title


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug[:50].rstrip("-") or "article"


# --- SocialData API ---

def socialdata_get(endpoint: str, params: dict = None) -> dict:
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < RATE_LIMIT_INTERVAL:
        time.sleep(RATE_LIMIT_INTERVAL - elapsed)

    api_key = os.environ.get("SOCIALDATA_API_KEY", "")
    url = f"{SOCIALDATA_BASE_URL}{endpoint}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "howto-kb-fix/1.0",
    }, method="GET")

    _last_request_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  API Error {e.code}: {body[:300]}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"  SocialData API error: {e}", file=sys.stderr)
        return {}


def fetch_tweet_by_id(tweet_id: str) -> dict | None:
    """ツイートIDからツイート詳細を取得。"""
    data = socialdata_get("/twitter/statuses/show", {"id": tweet_id})
    if data and data.get("id_str"):
        return data
    return None


def fetch_thread(tweet_id: str) -> list[dict]:
    try:
        data = socialdata_get(f"/twitter/thread/{tweet_id}")
        return data.get("tweets", [])
    except:
        return []


def fetch_article(tweet_id: str) -> dict | None:
    try:
        return socialdata_get(f"/twitter/tweets/{tweet_id}/article")
    except:
        return None


# --- HTML取得・OGタグ抽出 ---

def fetch_html(url: str) -> str | None:
    """URLからHTMLを取得（UTF-8で）。"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ja,en;q=0.5",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            # エンコーディング検出
            charset = resp.headers.get_content_charset()
            if charset:
                return raw.decode(charset, errors="replace")
            # HTMLから charset を探す
            partial = raw[:2000].decode("ascii", errors="replace")
            m = re.search(r'charset=["\']?([^"\';\s>]+)', partial, re.IGNORECASE)
            if m:
                return raw.decode(m.group(1), errors="replace")
            return raw.decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  HTML fetch failed ({url}): {e}", file=sys.stderr)
        return None


def extract_og_tags(html: str) -> dict:
    """HTMLからOGタグ（og:title, og:description）を抽出。"""
    result = {}
    # og:title
    m = re.search(r'<meta\s+(?:[^>]*?\s+)?(?:property|name)=["\']og:title["\']\s+content=["\']([^"\']*)["\']', html, re.IGNORECASE)
    if not m:
        m = re.search(r'<meta\s+content=["\']([^"\']*?)["\']\s+(?:property|name)=["\']og:title["\']', html, re.IGNORECASE)
    if m:
        result["title"] = unescape_html(m.group(1))

    # og:description
    m = re.search(r'<meta\s+(?:[^>]*?\s+)?(?:property|name)=["\']og:description["\']\s+content=["\']([^"\']*)["\']', html, re.IGNORECASE)
    if not m:
        m = re.search(r'<meta\s+content=["\']([^"\']*?)["\']\s+(?:property|name)=["\']og:description["\']', html, re.IGNORECASE)
    if m:
        result["description"] = unescape_html(m.group(1))

    # fallback: <title> tag
    if "title" not in result:
        m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if m:
            result["title"] = unescape_html(m.group(1).strip())

    # fallback: meta description
    if "description" not in result:
        m = re.search(r'<meta\s+(?:[^>]*?\s+)?name=["\']description["\']\s+content=["\']([^"\']*)["\']', html, re.IGNORECASE)
        if not m:
            m = re.search(r'<meta\s+content=["\']([^"\']*?)["\']\s+name=["\']description["\']', html, re.IGNORECASE)
        if m:
            result["description"] = unescape_html(m.group(1))

    return result


def unescape_html(text: str) -> str:
    """HTML entities をデコード。"""
    import html
    return html.unescape(text)


# --- X記事の再取得 ---

def refetch_x_article(article: dict) -> dict | None:
    """X記事のURLからツイートIDを取得し、SocialData APIで再取得。"""
    url = article["url"]
    # URLからtweet IDを抽出
    m = re.search(r'/status/(\d+)', url)
    if not m:
        print(f"  Cannot extract tweet ID from: {url}", file=sys.stderr)
        return None

    tweet_id = m.group(1)
    tweet = fetch_tweet_by_id(tweet_id)
    if not tweet:
        print(f"  Tweet not found: {tweet_id}", file=sys.stderr)
        return None

    author = tweet.get("user", {}).get("screen_name", "")
    full_text = tweet.get("full_text", "")

    description_parts = [full_text]

    # スレッド深掘り
    in_reply_to = tweet.get("in_reply_to_user_id_str")
    user_id = tweet.get("user", {}).get("id_str")
    if in_reply_to and in_reply_to == user_id:
        conv_id = tweet.get("conversation_id_str", tweet_id)
        thread = fetch_thread(conv_id)
        if len(thread) > 1:
            description_parts = [t.get("full_text", "") for t in thread]

    # 引用ツイート
    quoted_id = tweet.get("quoted_status_id_str")
    if quoted_id:
        quoted = tweet.get("quoted_status")
        if not quoted:
            quoted = fetch_tweet_by_id(quoted_id)
        if quoted:
            qa = quoted.get("user", {}).get("screen_name", "")
            qt = quoted.get("full_text", "")
            description_parts.append(f"\n--- 引用元 @{qa} ---\n{qt}")

    # Article
    entities = tweet.get("entities", {})
    for url_entity in entities.get("urls", []):
        expanded = url_entity.get("expanded_url", "")
        if ("x.com" in expanded or "twitter.com" in expanded) and "/i/article" in expanded:
            art = fetch_article(tweet_id)
            if art and art.get("text"):
                description_parts.append(f"\n--- Article ---\n{art['text']}")
            break

    description = "\n\n".join(description_parts).strip()
    title_preview = full_text[:60].replace("\n", " ")
    title = f"@{author}: {title_preview}"

    # 日付
    date_str = tweet.get("tweet_created_at", "")
    date_published = article.get("date_published", "")
    if date_str:
        for fmt in ["%a %b %d %H:%M:%S %z %Y"]:
            try:
                date_published = __import__("datetime").datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                pass

    return {
        "title": title,
        "url": url,
        "description": description[:2000],
        "source": "x",
        "date_published": date_published,
        "date_collected": article.get("date_collected", ""),
        "query": article.get("query", ""),
    }


# --- RSS/zenn/qiita/note記事の再取得 ---

def refetch_web_article(article: dict) -> dict | None:
    """WebページからOGタグを取得して記事情報を再構成。"""
    url = article["url"]
    html = fetch_html(url)
    if not html:
        return None

    og = extract_og_tags(html)
    if not og.get("title"):
        print(f"  No title found: {url}", file=sys.stderr)
        return None

    return {
        "title": og["title"],
        "url": url,
        "description": og.get("description", ""),
        "source": article["source"],
        "date_published": article.get("date_published", ""),
        "date_collected": article.get("date_collected", ""),
        "query": article.get("query", ""),
    }


# --- MD生成 ---

def write_md(article: dict, category: str, old_file_path: str) -> Path | None:
    """記事情報からMDファイルを生成。古いファイルがあれば削除して新しいパスに書く。"""
    title = sanitize_title(article["title"])
    source = article.get("source", "")
    summary = article.get("description", "").strip()
    date_published = article.get("date_published", "")
    date_collected = article.get("date_collected", "")
    query = article.get("query", "")

    if source == "x":
        summary_by = "auto-x"
        if not summary or summary == article["title"]:
            summary = "X (Twitter) より収集。詳細は URL を参照。"
    else:
        summary_by = "auto-rss"
        if not summary or summary == article["title"]:
            summary = f"{source} より収集。詳細は URL を参照。"

    tags = extract_tags(title, summary, source, category)
    tags_str = "[" + ", ".join(f'"{t}"' for t in tags) + "]"

    slug = slugify(title)
    article_id = f"{date_published}-{slug}-01"

    content = f"""---
id: "{article_id}"
title: "{title}"
url: "{article['url']}"
source: "{source}"
category: "{category}"
tags: {tags_str}
date_published: "{date_published}"
date_collected: "{date_collected}"
summary_by: "{summary_by}"
query: "{query}"
---

{summary}
"""

    new_path = ARTICLES_DIR / category / f"{article_id}.md"
    new_path.parent.mkdir(parents=True, exist_ok=True)

    # 古いファイルを削除（パスが異なる場合）
    old_path = Path(old_file_path)
    if old_path.exists() and old_path.resolve() != new_path.resolve():
        old_path.unlink()

    new_path.write_text(content, encoding="utf-8")
    return new_path


# --- メイン処理 ---

def main():
    apply = "--apply" in sys.argv

    if not GARBLED_PATH.exists():
        print("Error: _garbled_articles.json not found. Run detection first.", file=sys.stderr)
        sys.exit(1)

    garbled = json.loads(GARBLED_PATH.read_text(encoding="utf-8"))
    print(f"Found {len(garbled)} garbled articles to fix.")

    if not apply:
        print("Dry-run mode. Use --apply to actually fix files.")
        print()

    x_articles = [a for a in garbled if a["source"] == "x"]
    web_articles = [a for a in garbled if a["source"] != "x"]

    fixed = 0
    failed = 0
    failed_list = []

    # --- X記事 ---
    print(f"\n=== X articles ({len(x_articles)}) ===")
    for i, art in enumerate(x_articles, 1):
        print(f"  [{i}/{len(x_articles)}] {art['url']}", end=" ... ", flush=True)
        result = refetch_x_article(art)
        if result:
            new_title = sanitize_title(result["title"])
            print(f"OK: {new_title[:50]}")
            if apply:
                category = detect_category(new_title, result.get("description", ""), art["category"])
                write_md(result, category, art["file_path"])
            fixed += 1
        else:
            print("FAILED")
            failed += 1
            failed_list.append(art)

    # --- Web記事 (zenn/qiita/note/rss) ---
    print(f"\n=== Web articles ({len(web_articles)}) ===")
    for i, art in enumerate(web_articles, 1):
        print(f"  [{i}/{len(web_articles)}] {art['url']}", end=" ... ", flush=True)
        result = refetch_web_article(art)
        if result:
            new_title = sanitize_title(result["title"])
            print(f"OK: {new_title[:50]}")
            if apply:
                category = detect_category(new_title, result.get("description", ""), art["category"])
                write_md(result, category, art["file_path"])
            fixed += 1
        else:
            print("FAILED")
            failed += 1
            failed_list.append(art)
        # Web記事は少し間隔を空ける
        time.sleep(0.3)

    print(f"\n=== Summary ===")
    print(f"Fixed: {fixed}")
    print(f"Failed: {failed}")
    if failed_list:
        print("\nFailed URLs:")
        for a in failed_list:
            print(f"  [{a['source']}] {a['url']}")

    if failed_list and apply:
        with open(REPO_ROOT / "_garbled_failed.json", "w", encoding="utf-8") as f:
            json.dump(failed_list, f, ensure_ascii=False, indent=2)
        print(f"\nFailed articles saved to _garbled_failed.json")

    if not apply:
        print(f"\nDry-run complete. Use --apply to actually fix {fixed} files.")


if __name__ == "__main__":
    main()
