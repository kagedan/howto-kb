"""
crawl_x.py - Grok API (xAI) 経由で X (Twitter) から新規記事を検出する。

使い方:
    python scripts/crawl_x.py

処理:
    1. config/x_queries.yaml から検索クエリ一覧を読み込む
    2. 各クエリで xAI Responses API (x_search ツール) を呼び出し、X投稿を検索
    3. user_timelines のユーザーのリポスト（RT）を収集
    4. index.json の既存URLと照合し、新規記事のみ抽出
    5. 新規記事の情報をJSON形式で標準出力に出力

環境変数:
    XAI_API_KEY - xAI APIキー（必須）

依存パッケージ:
    pip install pyyaml
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
QUERIES_PATH = REPO_ROOT / "config" / "x_queries.yaml"
INDEX_PATH = REPO_ROOT / "index.json"

JST = timezone(timedelta(hours=9))

# xAI Responses API（x_search は grok-4-1-fast 以降のモデルで対応）
API_ENDPOINT = "https://api.x.ai/v1/responses"
MODEL = "grok-4-1-fast-non-reasoning"
API_TIMEOUT = 300


def load_existing_urls() -> set[str]:
    """index.json から登録済みURLの集合を返す。"""
    if not INDEX_PATH.exists():
        return set()
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return {a["url"] for a in data.get("articles", []) if a.get("url")}


def load_queries() -> tuple[list[dict], dict, list[dict]]:
    """x_queries.yaml からクエリ一覧、検索設定、ユーザータイムライン設定を読み込む。"""
    data = yaml.safe_load(QUERIES_PATH.read_text(encoding="utf-8"))
    queries = data.get("queries", [])
    settings = data.get("search_settings", {})
    user_timelines = data.get("user_timelines", [])
    return queries, settings, user_timelines


def call_xai_api(input_text: str, api_key: str) -> dict:
    """xAI Responses API を呼び出して結果を返す。"""
    payload = {
        "model": MODEL,
        "input": input_text,
        "tools": [{"type": "x_search"}],
        "temperature": 0,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_ENDPOINT,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "howto-kb-crawler/1.0",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  API Error {e.code}: {body[:500]}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"  Error calling xAI API: {e}", file=sys.stderr)
        return {}


def search_x(query: str, api_key: str, max_results: int = 10, lang: str = "ja", min_likes: int = 0) -> list[dict]:
    """xAI Responses API の x_search ツールで X 投稿を検索する。"""
    lang_note = f" (in {lang} language)" if lang else ""

    input_text = (
        f"Search X for: {query}{lang_note}\n"
        "Prioritize posts that contain specific how-to steps, "
        "configuration examples, code snippets, or practical tips. "
        "Exclude simple announcements, retweets of official news, "
        "and posts that only say 'I tried X' without details.\n"
        "If a post is part of a thread (self-replies by the same author), "
        "include the full thread text combined.\n"
        f"Return up to {max_results} results. "
        f"Only include posts with {min_likes} or more likes. "
        "For each post, include: the post URL (https://x.com/username/status/ID format), "
        "author username, full post text, date (YYYY-MM-DD), likes count. "
        "Return ONLY a JSON array, no other text."
    )

    result = call_xai_api(input_text, api_key)
    if not result:
        return []
    return parse_responses_output(result)


def fetch_user_timeline(username: str, api_key: str, max_results: int | None = None) -> list[dict]:
    """ユーザーのリポスト（RT）を収集する。RTの元投稿のURL・テキストを取得する。"""
    limit_note = f"up to {max_results}" if max_results else "all available"

    input_text = (
        f"Search X for retweets/reposts by @{username}. "
        f"Return {limit_note} results. "
        "For each repost, return the ORIGINAL post (not the retweet itself). "
        "If the original post is part of a thread (self-replies by the same author), "
        "include the full thread text combined.\n"
        "Include: the original post URL (https://x.com/username/status/ID format), "
        "original author username, full post text, date (YYYY-MM-DD), likes count. "
        "Return ONLY a JSON array, no other text."
    )

    result = call_xai_api(input_text, api_key)
    if not result:
        return []
    return parse_responses_output(result)


def parse_responses_output(result: dict) -> list[dict]:
    """xAI Responses APIのレスポンスから検索結果を抽出する。

    レスポンス構造:
    - output[]: x_search ツール呼び出し結果とテキスト出力
    - output[].content[].text: モデルの回答テキスト
    - output[].content[].annotations[]: url_citation（投稿URL）
    """
    entries = []
    annotations_urls = set()

    # output 配列からテキスト出力を探す
    for item in result.get("output", []):
        content_list = item.get("content", [])
        if not isinstance(content_list, list):
            continue

        for content in content_list:
            if content.get("type") != "output_text":
                continue

            text = content.get("text", "")

            # annotations から X 投稿 URL を収集
            for ann in content.get("annotations", []):
                if ann.get("type") == "url_citation":
                    url = ann.get("url", "")
                    if url and ("x.com" in url or "twitter.com" in url):
                        annotations_urls.add(url)

            # テキスト本文からJSON配列をパース
            parsed = try_parse_json_results(text)
            if parsed:
                entries = parsed
                break

            # JSON パース失敗時はテキストからURLを抽出
            url_entries = extract_urls_from_content(text)
            if url_entries:
                entries = url_entries
                break

    # annotations の URL で補完（パースで取れなかった場合）
    if not entries and annotations_urls:
        for url in annotations_urls:
            entries.append({
                "title": "",
                "url": url,
                "date_published": "",
                "description": "",
            })

    return entries


def try_parse_json_results(content: str) -> list[dict]:
    """テキストからJSON配列を抽出してパースする。"""
    # ```json ... ``` ブロックまたは [ ... ] を検出
    json_match = re.search(r'```(?:json)?\s*(\[[\s\S]*?\])\s*```', content)
    if not json_match:
        json_match = re.search(r'(\[[\s\S]*\])', content)
    if not json_match:
        return []

    try:
        items = json.loads(json_match.group(1))
    except json.JSONDecodeError:
        return []

    entries = []
    for item in items:
        if not isinstance(item, dict):
            continue
        url = item.get("url", "")
        if not url or ("x.com" not in url and "twitter.com" not in url):
            continue

        text = item.get("text", item.get("content", ""))
        author = item.get("author", item.get("username", ""))
        date = item.get("date", item.get("published_date", ""))
        title = item.get("title", "")

        if not title and author and text:
            title = f"@{author}: {text[:60]}"
        elif not title and text:
            title = text[:80]

        entries.append({
            "title": title,
            "url": url,
            "date_published": parse_date(date) if date else "",
            "description": text[:500] if text else "",
        })

    return entries


def extract_urls_from_content(content: str) -> list[dict]:
    """テキストコンテンツから X/Twitter の URLを抽出する。"""
    url_pattern = re.compile(r'https?://(?:x\.com|twitter\.com)/\w+/status/\d+')
    urls = list(dict.fromkeys(url_pattern.findall(content)))  # 重複除去・順序維持

    entries = []
    for url in urls:
        entries.append({
            "title": "",
            "url": url,
            "date_published": "",
            "description": "",
        })
    return entries


def parse_date(date_str: str) -> str:
    """日付文字列を YYYY-MM-DD に正規化する。"""
    if not date_str:
        return ""
    for fmt in [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]:
        try:
            return datetime.strptime(
                date_str[: len("2026-03-15T10:00:00+09:00")], fmt
            ).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # "Mar 5, 2026" などの英語日付
    for fmt in ["%b %d, %Y", "%B %d, %Y"]:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str[:10] if len(date_str) >= 10 else date_str


def main():
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("Error: XAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    existing_urls = load_existing_urls()
    queries, settings, user_timelines = load_queries()
    today = datetime.now(JST).strftime("%Y-%m-%d")
    max_results = settings.get("max_results_per_query", 10)
    min_likes = settings.get("min_likes", 0)

    all_new = []

    # --- 検索クエリ ---
    for q in queries:
        query_text = q.get("query", "")
        category = q.get("category", "ai-workflow")
        lang = q.get("lang", "ja")

        if not query_text:
            continue

        print(f'Searching X: "{query_text}" (lang={lang})', file=sys.stderr)
        entries = search_x(query_text, api_key, max_results=max_results, lang=lang, min_likes=min_likes)
        print(f"  Found {len(entries)} results", file=sys.stderr)

        for entry in entries:
            if entry["url"] in existing_urls:
                continue

            entry["source"] = "x"
            entry["default_category"] = category
            entry["date_collected"] = today
            entry["query"] = query_text
            all_new.append(entry)
            existing_urls.add(entry["url"])

    # --- ユーザータイムライン（RT収集） ---
    for ut in user_timelines:
        username = ut.get("username", "")
        if not username:
            continue

        include_retweets = ut.get("include_retweets", True)
        if not include_retweets:
            continue

        category_default = ut.get("category_default", "ai-workflow")

        # 初回実行時（既存URLが少ない＝index.jsonにX投稿がほぼない）は件数制限なし
        x_urls_in_index = sum(1 for u in existing_urls if "x.com" in u or "twitter.com" in u)
        is_first_run = x_urls_in_index == 0
        timeline_max = None if is_first_run else max_results

        limit_label = "全件" if timeline_max is None else f"最大{timeline_max}件"
        print(f'Fetching RT: @{username} ({limit_label})', file=sys.stderr)
        entries = fetch_user_timeline(username, api_key, max_results=timeline_max)
        print(f"  Found {len(entries)} results", file=sys.stderr)

        for entry in entries:
            if entry["url"] in existing_urls:
                continue

            entry["source"] = "x"
            entry["default_category"] = category_default
            entry["date_collected"] = today
            entry["query"] = f"RT @{username}"
            all_new.append(entry)
            existing_urls.add(entry["url"])

    print(f"\nTotal new X posts: {len(all_new)}", file=sys.stderr)

    output = json.dumps(all_new, ensure_ascii=False, indent=2)
    sys.stdout.buffer.write(output.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
