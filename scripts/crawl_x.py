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


def get_catchup_multiplier() -> int:
    """index.jsonの最新date_collectedと今日の差分から取得倍率を返す。
    前日に更新がなかった場合（ギャップ2日以上）に倍率を上げる。"""
    if not INDEX_PATH.exists():
        return 1
    try:
        data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 1
    articles = data.get("articles", [])
    if not articles:
        return 1
    dates = [a.get("date_collected", "") for a in articles if a.get("date_collected")]
    if not dates:
        return 1
    latest = max(dates)
    try:
        last_date = datetime.strptime(latest, "%Y-%m-%d").date()
        today = datetime.now(JST).date()
        gap = (today - last_date).days
        if gap > 1:
            return min(gap, 5)  # 最大5倍
        return 1
    except ValueError:
        return 1


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
    """Xの長文記事（Article）を取得。

    SocialData のレスポンスはツイート全体で、本文は ``article`` キー配下。
    """
    try:
        data = socialdata_get(f"/twitter/article/{tweet_id}")
        if isinstance(data, dict):
            return data.get("article")
        return None
    except Exception as e:
        print(f"  Article取得失敗 (tweet_id={tweet_id}): {e}", file=sys.stderr)
        return None


# --- Draft.js → Markdown 変換 ---

def _apply_inline_decorations(text: str, inline_ranges: list, entity_ranges: list,
                              emap: dict) -> str:
    """inlineStyleRanges と entityRanges をテキストに反映し Markdown 化する。"""
    edits = []  # (offset, length, pre, post, replace)
    for r in inline_ranges or []:
        style = r.get("style", "")
        offset = r.get("offset", 0)
        length = r.get("length", 0)
        if style in ("Bold", "BOLD"):
            edits.append((offset, length, "**", "**", None))
        elif style in ("Italic", "ITALIC"):
            edits.append((offset, length, "*", "*", None))
        elif style in ("Code", "CODE"):
            edits.append((offset, length, "`", "`", None))
    for r in entity_ranges or []:
        offset = r.get("offset", 0)
        length = r.get("length", 0)
        entity = emap.get(str(r.get("key")), {})
        etype = entity.get("type", "")
        edata = entity.get("data") or {}
        if not isinstance(edata, dict):
            continue
        if etype == "LINK":
            url = edata.get("url", "")
            if url:
                edits.append((offset, length, "[", f"]({url})", None))
        elif etype == "MARKDOWN":
            md = edata.get("markdown", "")
            edits.append((offset, length, "", "", md))
        # TWEMOJI は元テキストの絵文字をそのまま残す

    edits.sort(key=lambda x: x[0], reverse=True)
    result = text
    for offset, length, pre, post, replace in edits:
        end = offset + length
        if offset < 0 or end > len(result):
            continue
        if replace is not None:
            result = result[:offset] + replace + result[end:]
        else:
            result = result[:offset] + pre + result[offset:end] + post + result[end:]
    return result


def _render_atomic_block(entity_ranges: list, emap: dict,
                         media_dict: dict, media_queue: list) -> str:
    """atomic block を Markdown に変換する（区切り線・画像・MD埋込）。"""
    if not entity_ranges:
        return ""
    entity = emap.get(str(entity_ranges[0].get("key")), {})
    etype = entity.get("type", "")
    edata = entity.get("data") or {}
    if not isinstance(edata, dict):
        return ""
    if etype == "DIVIDER":
        return "---"
    if etype == "MEDIA":
        items = edata.get("mediaItems", [])
        if items:
            mid = str(items[0].get("mediaId", ""))
            url = media_dict.get(mid)
            if not url and media_queue:
                url = media_queue.pop(0)
            if url:
                return f"![]({url})"
        return ""
    if etype == "MARKDOWN":
        return edata.get("markdown", "")
    return ""


def draftjs_to_markdown(content_state: dict, media_entities: list = None) -> str:
    """Draft.js content_state を Markdown 文字列に変換する。"""
    if not isinstance(content_state, dict):
        return ""
    blocks = content_state.get("blocks", []) or []
    entity_list = content_state.get("entityMap", []) or []

    if isinstance(entity_list, list):
        emap = {str(e.get("key")): (e.get("value") or {}) for e in entity_list}
    elif isinstance(entity_list, dict):
        emap = {str(k): v for k, v in entity_list.items()}
    else:
        emap = {}

    media_dict = {}
    media_queue = []
    for me in media_entities or []:
        mid = str(me.get("media_id", ""))
        url = ((me.get("media_info") or {}).get("original_img_url")
               or me.get("media_url_https") or "")
        if url:
            if mid:
                media_dict[mid] = url
            media_queue.append(url)

    lines = []
    for block in blocks:
        btype = block.get("type", "unstyled")
        text = block.get("text", "")
        inline_ranges = block.get("inlineStyleRanges", [])
        entity_ranges = block.get("entityRanges", [])

        if btype == "atomic":
            rendered = _render_atomic_block(entity_ranges, emap, media_dict, media_queue)
            if rendered:
                lines.append(rendered)
                lines.append("")
            continue

        decorated = _apply_inline_decorations(text, inline_ranges, entity_ranges, emap)

        if btype == "header-one":
            lines.append(f"# {decorated}")
        elif btype == "header-two":
            lines.append(f"## {decorated}")
        elif btype == "header-three":
            lines.append(f"### {decorated}")
        elif btype == "unordered-list-item":
            lines.append(f"- {decorated}")
        elif btype == "ordered-list-item":
            lines.append(f"1. {decorated}")
        elif btype == "blockquote":
            lines.append(f"> {decorated}")
        elif btype == "code-block":
            lines.append(f"```\n{text}\n```")
        else:
            lines.append(decorated)

        if btype not in ("unordered-list-item", "ordered-list-item"):
            lines.append("")

    result = "\n".join(lines)
    # 過剰な空行を整理
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    return result


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

    # 1. スレッド判定: ルート/途中どちらでもスレッドを取得する
    # conversation_id_str で取得し、同一ユーザーによる自己返信チェーンが
    # 2件以上あればスレッドと判定する（ルートのみの場合は len==1 なのでスキップ）。
    user_id = tweet.get("user", {}).get("id_str")
    conv_id = tweet.get("conversation_id_str", tweet_id)
    thread = fetch_thread(conv_id)
    if len(thread) > 1:
        self_thread = [t for t in thread if t.get("user", {}).get("id_str") == user_id]
        if len(self_thread) > 1:
            description_parts = [t.get("full_text", "") for t in self_thread]

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

            # 引用元がスレッドの場合も深掘り（ルート/途中どちらでも取得）
            qt_user_id = quoted.get("user", {}).get("id_str")
            qt_conv_id = quoted.get("conversation_id_str", quoted_id)
            qt_thread = fetch_thread(qt_conv_id)
            if len(qt_thread) > 1:
                qt_self = [t for t in qt_thread if t.get("user", {}).get("id_str") == qt_user_id]
                if len(qt_self) > 1:
                    # 先頭（本文と重複）を除いた残りを追加
                    qt_texts = [t.get("full_text", "") for t in qt_self[1:]]
                    description_parts.append("\n".join(qt_texts))

    # 3. Article（長文記事）があるか確認
    entities = tweet.get("entities", {})
    urls = entities.get("urls", [])
    article_info = None
    for url_entity in urls:
        expanded = url_entity.get("expanded_url", "")
        if ("x.com" in expanded or "twitter.com" in expanded) and "/i/article" in expanded:
            article = fetch_article(tweet_id)
            if article:
                body_md = draftjs_to_markdown(
                    article.get("content_state"),
                    article.get("media_entities", []),
                )
                article_info = {
                    "title": article.get("title", ""),
                    "body_markdown": body_md,
                    "cover_url": article.get("cover_url", ""),
                    "preview_text": article.get("preview_text", ""),
                }
                if body_md:
                    description_parts.append(f"\n--- Article ---\n{body_md}")
                elif article.get("preview_text"):
                    description_parts.append(
                        f"\n--- Article ---\n{article['preview_text']}"
                    )
            break

    # 4. 外部URL収集（X内部リンクを除外）
    external_urls = []
    all_url_entities = list(urls)
    if quoted_id:
        qt_entities = (tweet.get("quoted_status") or {}).get("entities", {})
        all_url_entities.extend(qt_entities.get("urls", []))
    for url_entity in all_url_entities:
        expanded = url_entity.get("expanded_url", "")
        if not expanded:
            continue
        if any(d in expanded for d in ("x.com", "twitter.com", "t.co")):
            continue
        if expanded not in external_urls:
            external_urls.append(expanded)

    # 5. 添付画像URL収集
    image_urls = []
    media_entities = entities.get("media", [])
    ext_entities = tweet.get("extended_entities", {})
    if ext_entities:
        media_entities = ext_entities.get("media", media_entities)
    for media in media_entities:
        if media.get("type") in ("photo", "animated_gif"):
            img_url = media.get("media_url_https", "")
            if img_url and img_url not in image_urls:
                image_urls.append(img_url)

    # --- 出力形式変換 ---
    description = "\n\n".join(description_parts).strip()

    title_preview = full_text[:60].replace("\n", " ")
    title = f"@{author}: {title_preview}"

    date_str = tweet.get("tweet_created_at", "")
    date_published = parse_date(date_str)

    result = {
        "title": title,
        "url": f"https://x.com/{author}/status/{tweet_id}",
        "date_published": date_published,
        "description": description[:2000],
        "source": "x",
        "external_urls": external_urls,
        "image_urls": image_urls,
        "tweet_datetime": date_str,
    }
    if article_info:
        result["article"] = article_info
    return result


# --- RT収集 ---

def get_user_id(username: str) -> str:
    """screen_name から数値ユーザーIDを解決する。"""
    data = socialdata_get(f"/twitter/user/{username}")
    return data.get("id_str", "") or str(data.get("id", ""))


def fetch_user_retweets(username: str, max_results: int = 10) -> list[dict]:
    """ユーザーのタイムラインを取得し、リツイートのみ抽出する。

    /twitter/search の filter:nativeretweets は検索インデックスの制限で
    最近のネイティブRTを拾えないため、/twitter/user/{user_id}/tweets
    エンドポイント経由でタイムラインを取得し retweeted_status を持つ
    投稿だけを返す方式に変更。
    """
    user_id = get_user_id(username)
    if not user_id:
        print(f"  ユーザーID取得失敗: @{username}", file=sys.stderr)
        return []

    results: list[dict] = []
    cursor: str | None = None
    # タイムラインは非RT投稿も混ざるため、必要件数より多めに取得して絞り込む
    page_budget = max(max_results * 4, 40)

    while len(results) < max_results:
        params = {}
        if cursor:
            params["cursor"] = cursor

        data = socialdata_get(f"/twitter/user/{user_id}/tweets", params)
        tweets = data.get("tweets", [])
        if not tweets:
            break

        for t in tweets:
            if t.get("retweeted_status"):
                results.append(t)
                if len(results) >= max_results:
                    break

        cursor = data.get("next_cursor")
        page_budget -= len(tweets)
        if not cursor or page_budget <= 0:
            break

    return results[:max_results]


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

    multiplier = get_catchup_multiplier()
    if multiplier > 1:
        max_results = max_results * 2  # X は2倍固定
        print(f"Catchup mode: {multiplier}日分のギャップを検出（X取得件数を2倍: {max_results}件/クエリ）", file=sys.stderr)

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

        # user_timelines は検索クエリと独立した上限を持つ。
        # config未指定時は50をデフォルトにする（1日分のRTを取りこぼさない値）。
        timeline_max = ut.get("max_results", 50)
        if multiplier > 1:
            timeline_max = timeline_max * 2

        print(f'Fetching RT: @{username} (最大{timeline_max}件)', file=sys.stderr)
        tweets = fetch_user_retweets(username, max_results=timeline_max)
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
            entry["is_retweet"] = True
            all_new.append(entry)
            existing_urls.add(entry["url"])

    print(f"\nTotal new X posts: {len(all_new)}", file=sys.stderr)

    output = json.dumps(all_new, ensure_ascii=False, indent=2)
    sys.stdout.buffer.write(output.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
