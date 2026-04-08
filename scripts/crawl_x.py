"""
crawl_x.py - SocialData API 経由で X (Twitter) から新規記事を検出する。

使い方:
    python scripts/crawl_x.py

処理:
    1. config/x_queries.yaml から検索クエリ一覧を読み込む
    2. 各クエリで SocialData API を呼び出し、X投稿を検索
    3. スレッド・引用元・Articleを深掘りして情報を結合
    4. user_timelines のユーザーのリポスト（RT）を収集
    5. index.json の既存URLと照合し、新規記事のみ抽出
    6. 新規記事の情報をJSON形式で標準出力に出力

出力 (stdout):
    新規記事のリスト (JSON)。_generate_mds.py がこの出力を受け取り、
    カテゴリ判定・タグ付与・MD生成を行う。

環境変数:
    SOCIALDATA_API_KEY - SocialData APIキー（必須）

依存パッケージ:
    pip install pyyaml（既存と同じ）
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Windows環境でのcp932文字化け対策
os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
QUERIES_PATH = REPO_ROOT / "config" / "x_queries.yaml"
INDEX_PATH = REPO_ROOT / "index.json"

JST = timezone(timedelta(hours=9))

SOCIALDATA_BASE_URL = "https://api.socialdata.tools"

# レートリミット制御: 120リクエスト/分 → 余裕を持って100リクエスト/分
RATE_LIMIT_INTERVAL = 0.6  # 秒（60秒 / 100リクエスト）
_last_request_time = 0.0


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


def socialdata_get(endpoint: str, params: dict = None) -> dict:
    """SocialData APIへのGETリクエスト共通関数。レートリミット制御付き。"""
    global _last_request_time

    # レートリミット制御
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < RATE_LIMIT_INTERVAL:
        time.sleep(RATE_LIMIT_INTERVAL - elapsed)

    api_key = os.environ.get("SOCIALDATA_API_KEY", "")
    url = f"{SOCIALDATA_BASE_URL}{endpoint}"

    if params:
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "howto-kb-crawler/2.0",
        },
        method="GET",
    )

    _last_request_time = time.time()

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  API Error {e.code}: {body[:500]}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"  Error calling SocialData API: {e}", file=sys.stderr)
        return {}


# --- 検索 ---

def search_tweets(query: str, max_results: int = 10, min_likes: int = 5,
                  exclude_retweets: bool = True) -> list[dict]:
    """SocialData APIでツイートを検索。"""
    full_query = f"{query} min_faves:{min_likes}"

    if exclude_retweets:
        full_query += " -filter:retweets"

    results = []
    cursor = None

    while len(results) < max_results:
        params = {"query": full_query}
        if cursor:
            params["cursor"] = cursor

        data = socialdata_get("/twitter/search", params)
        tweets = data.get("tweets", [])

        if not tweets:
            break

        results.extend(tweets)
        cursor = data.get("next_cursor")

        if not cursor:
            break

    return results[:max_results]


# --- 深掘り ---

def fetch_thread(tweet_id: str) -> list[dict]:
    """スレッド（セルフリプライチェーン）全体を取得。"""
    try:
        data = socialdata_get(f"/twitter/thread/{tweet_id}")
        return data.get("tweets", [])
    except Exception as e:
        print(f"  スレッド取得失敗 (tweet_id={tweet_id}): {e}", file=sys.stderr)
        return []


def fetch_article(tweet_id: str) -> dict | None:
    """Xの長文記事（Article）を取得。"""
    try:
        return socialdata_get(f"/twitter/tweets/{tweet_id}/article")
    except Exception as e:
        print(f"  Article取得失敗 (tweet_id={tweet_id}): {e}", file=sys.stderr)
        return None


def fetch_quoted_tweet(tweet_id: str) -> dict | None:
    """引用元ツイートの詳細を取得。"""
    try:
        return socialdata_get(f"/twitter/statuses/show", {"id": tweet_id})
    except Exception as e:
        print(f"  引用元取得失敗 (tweet_id={tweet_id}): {e}", file=sys.stderr)
        return None


# --- 深掘り＋出力形式変換 ---

def enrich_and_format(tweet: dict) -> dict:
    """ツイートを深掘りし、既存パイプラインの出力形式に変換する。"""
    tweet_id = tweet.get("id_str", "")
    author = tweet.get("user", {}).get("screen_name", "")
    full_text = tweet.get("full_text", "")

    description_parts = [full_text]

    # 1. スレッド判定: セルフリプライかどうか
    in_reply_to = tweet.get("in_reply_to_user_id_str")
    user_id = tweet.get("user", {}).get("id_str")
    if in_reply_to and in_reply_to == user_id:
        conv_id = tweet.get("conversation_id_str", tweet_id)
        thread = fetch_thread(conv_id)
        if len(thread) > 1:
            thread_texts = [t.get("full_text", "") for t in thread]
            description_parts = thread_texts  # スレッド全体で置き換え

    # 2. 引用ツイートの元記事を取得
    quoted_id = tweet.get("quoted_status_id_str")
    if quoted_id:
        quoted = tweet.get("quoted_status")
        if not quoted:
            quoted = fetch_quoted_tweet(quoted_id)

        if quoted:
            quoted_author = quoted.get("user", {}).get("screen_name", "")
            quoted_text = quoted.get("full_text", "")
            description_parts.append(f"\n--- 引用元 @{quoted_author} ---\n{quoted_text}")

            # 引用元がスレッドの場合も深掘り
            qt_reply_to = quoted.get("in_reply_to_user_id_str")
            qt_user_id = quoted.get("user", {}).get("id_str")
            if qt_reply_to and qt_reply_to == qt_user_id:
                qt_conv_id = quoted.get("conversation_id_str", quoted_id)
                qt_thread = fetch_thread(qt_conv_id)
                if len(qt_thread) > 1:
                    qt_texts = [t.get("full_text", "") for t in qt_thread[1:]]
                    description_parts.append("\n".join(qt_texts))

    # 3. Article（長文記事）があるか確認
    entities = tweet.get("entities", {})
    urls = entities.get("urls", [])
    for url_entity in urls:
        expanded = url_entity.get("expanded_url", "")
        if ("x.com" in expanded or "twitter.com" in expanded) and "/i/article" in expanded:
            article = fetch_article(tweet_id)
            if article and article.get("text"):
                description_parts.append(f"\n--- Article ---\n{article['text']}")
            break

    # --- 出力形式変換 ---
    description = "\n\n".join(description_parts).strip()

    title_preview = full_text[:60].replace("\n", " ")
    title = f"@{author}: {title_preview}"

    date_str = tweet.get("tweet_created_at", "")
    date_published = parse_date(date_str)

    return {
        "title": title,
        "url": f"https://x.com/{author}/status/{tweet_id}",
        "date_published": date_published,
        "description": description[:2000],
        "source": "x",
    }


# --- RT収集 ---

def fetch_user_retweets(username: str, max_results: int = 10) -> list[dict]:
    """ユーザーのリツイート（引用RT含む）を検索で取得。"""
    query = f"from:{username} filter:nativeretweets"
    return search_tweets(query, max_results=max_results, min_likes=0,
                         exclude_retweets=False)


# --- 日付パース ---

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
                date_str[:len("2026-03-15T10:00:00+09:00")], fmt
            ).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # SocialData は "Wed Oct 10 20:19:24 +0000 2018" 形式も返す
    try:
        return datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y").strftime("%Y-%m-%d")
    except ValueError:
        pass
    for fmt in ["%b %d, %Y", "%B %d, %Y"]:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str[:10] if len(date_str) >= 10 else date_str


# --- メイン処理 ---

def main():
    api_key = os.environ.get("SOCIALDATA_API_KEY")
    if not api_key:
        print("Error: SOCIALDATA_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    existing_urls = load_existing_urls()
    queries, settings, user_timelines = load_queries()
    today = datetime.now(JST).strftime("%Y-%m-%d")
    max_results = settings.get("max_results_per_query", 10)
    min_likes = settings.get("min_likes", 5)
    exclude_retweets = settings.get("exclude_retweets", True)

    all_new = []

    # --- 検索クエリ ---
    for q in queries:
        query_text = q.get("query", "")
        category = q.get("category", "ai-workflow")
        lang = q.get("lang", "ja")

        if not query_text:
            continue

        full_query = f"{query_text} lang:{lang}"

        print(f'Searching X: "{full_query}"', file=sys.stderr)
        tweets = search_tweets(full_query, max_results=max_results,
                               min_likes=min_likes, exclude_retweets=exclude_retweets)
        print(f"  Found {len(tweets)} results", file=sys.stderr)

        for tweet in tweets:
            tweet_url = f"https://x.com/{tweet.get('user', {}).get('screen_name', '')}/status/{tweet.get('id_str', '')}"

            if tweet_url in existing_urls:
                continue

            entry = enrich_and_format(tweet)
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

        # 初回実行判定（既存ロジック移植）
        x_urls_in_index = sum(1 for u in existing_urls if "x.com" in u or "twitter.com" in u)
        is_first_run = x_urls_in_index == 0
        timeline_max = None if is_first_run else max_results

        limit_label = "全件" if timeline_max is None else f"最大{timeline_max}件"
        print(f'Fetching RT: @{username} ({limit_label})', file=sys.stderr)
        tweets = fetch_user_retweets(username, max_results=timeline_max or 50)
        print(f"  Found {len(tweets)} results", file=sys.stderr)

        for tweet in tweets:
            # RTの場合、元ツイートを深掘り
            rt_source = tweet.get("retweeted_status")
            target = rt_source if rt_source else tweet

            tweet_url = f"https://x.com/{target.get('user', {}).get('screen_name', '')}/status/{target.get('id_str', '')}"

            if tweet_url in existing_urls:
                continue

            entry = enrich_and_format(target)
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
