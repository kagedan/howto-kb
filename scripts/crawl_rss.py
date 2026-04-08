"""
crawl_rss.py - feeds.yaml のRSSフィードから新規記事を検出する。

使い方:
    python scripts/crawl_rss.py

処理:
    1. config/feeds.yaml からフィードURL一覧を読み込む
    2. 各フィードをRSS/Atom形式で取得・パース
    3. index.json の既存URLと照合し、新規記事のみ抽出
    4. 新規記事の情報をJSON形式で標準出力に出力

出力 (stdout):
    新規記事のリスト (JSON)。Claude Code Desktop スケジュールタスクが
    この出力を受け取り、要約・カテゴリ判定・タグ付与・MD生成を行う。

依存パッケージ:
    pip install pyyaml
"""

import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
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
FEEDS_PATH = REPO_ROOT / "config" / "feeds.yaml"
INDEX_PATH = REPO_ROOT / "index.json"

JST = timezone(timedelta(hours=9))

# RSSフィードの取得タイムアウト（秒）
FETCH_TIMEOUT = 30


def load_existing_urls() -> set[str]:
    """index.json から登録済みURLの集合を返す。"""
    if not INDEX_PATH.exists():
        return set()
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return {a["url"] for a in data.get("articles", []) if a.get("url")}


def load_feeds() -> list[dict]:
    """feeds.yaml からフィード一覧を読み込む。"""
    data = yaml.safe_load(FEEDS_PATH.read_text(encoding="utf-8"))
    feeds = []
    for key in ["ai_feeds", "construction_feeds"]:
        section = data.get(key, [])
        if isinstance(section, list):
            feeds.extend(section)
    return feeds


def fetch_feed(url: str) -> ET.Element | None:
    """URLからRSS/Atomフィードを取得してXML Elementを返す。"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "howto-kb-crawler/1.0"})
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            return ET.fromstring(resp.read())
    except Exception as e:
        print(f"  Warning: Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def parse_rss_entries(root: ET.Element) -> list[dict]:
    """RSS 2.0 の <item> をパースする。"""
    entries = []
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub_date = item.findtext("pubDate", "").strip()
        description = item.findtext("description", "").strip()

        date_str = parse_date(pub_date) if pub_date else ""

        if link:
            entries.append({
                "title": title,
                "url": link,
                "date_published": date_str,
                "description": description[:500],  # 長すぎる場合は切り詰め
            })
    return entries


def parse_atom_entries(root: ET.Element) -> list[dict]:
    """Atom フィードの <entry> をパースする。"""
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = []
    for entry in root.findall("atom:entry", ns):
        title = entry.findtext("atom:title", "", ns).strip()

        # link は href 属性
        link_elem = entry.find("atom:link[@rel='alternate']", ns)
        if link_elem is None:
            link_elem = entry.find("atom:link", ns)
        link = link_elem.get("href", "").strip() if link_elem is not None else ""

        updated = entry.findtext("atom:updated", "", ns).strip()
        published = entry.findtext("atom:published", "", ns).strip()
        summary = entry.findtext("atom:summary", "", ns).strip()
        content = entry.findtext("atom:content", "", ns).strip()

        date_str = parse_date(published or updated) if (published or updated) else ""

        if link:
            entries.append({
                "title": title,
                "url": link,
                "date_published": date_str,
                "description": (summary or content)[:500],
            })
    return entries


def parse_entries(root: ET.Element) -> list[dict]:
    """RSS 2.0 / Atom を自動判別してエントリを返す。"""
    # Atom: ルートタグが {http://www.w3.org/2005/Atom}feed
    if "Atom" in root.tag or root.tag.endswith("feed"):
        return parse_atom_entries(root)
    # RSS 2.0: <rss> > <channel> > <item>
    return parse_rss_entries(root)


def parse_date(date_str: str) -> str:
    """各種日付文字列を YYYY-MM-DD に正規化する。ベストエフォート。"""
    # ISO 8601: 2026-03-15T10:00:00+09:00
    for fmt in [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]:
        try:
            return datetime.strptime(date_str[:len("2026-03-15T10:00:00+09:00")], fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # RFC 2822: Mon, 15 Mar 2026 10:00:00 +0900
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str).strftime("%Y-%m-%d")
    except Exception:
        pass

    return date_str[:10] if len(date_str) >= 10 else date_str


def detect_paywall(content: str, source: str) -> bool:
    """有料記事かどうかを判定する。"""
    paywall_markers = [
        "この記事は有料です",
        "続きを読むにはログインが必要",
        "メンバーシップ限定",
        "有料マガジン",
        "この続きをみるには",
        "購入して続きを読む",
        "有料記事のため",
        "ここから先は有料です",
    ]

    # 本文が短すぎる（導入部分だけの可能性）
    if len(content.strip()) < 200:
        return True

    # 有料記事の定型文を検出
    for marker in paywall_markers:
        if marker in content:
            return True

    return False


def detect_source(url: str, feed_name: str) -> str:
    """URLからソースを判定する。"""
    if "zenn.dev" in url:
        return "zenn"
    if "qiita.com" in url:
        return "qiita"
    if "note.com" in url:
        return "note"
    if "anthropic.com" in url:
        return "anthropic"
    if feed_name and "anthropic" in feed_name.lower():
        return "anthropic"
    return "rss"


def load_qiita_feeds() -> list[dict]:
    """feeds.yaml から Qiita API 設定を読み込む。"""
    data = yaml.safe_load(FEEDS_PATH.read_text(encoding="utf-8"))
    return data.get("qiita_api", []) or []


def fetch_qiita_articles(tag: str, per_page: int = 20) -> list[dict]:
    """Qiita API v2 でタグ指定の記事一覧を取得する。"""
    url = f"https://qiita.com/api/v2/tags/{tag}/items?page=1&per_page={per_page}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "howto-kb-crawler/1.0"})
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            items = json.loads(resp.read())
    except Exception as e:
        print(f"  Warning: Failed to fetch Qiita tag={tag}: {e}", file=sys.stderr)
        return []

    entries = []
    for item in items:
        entry_url = item.get("url", "")
        if not entry_url:
            continue
        created = item.get("created_at", "")
        date_str = parse_date(created) if created else ""
        # body先頭を description として使う
        body = item.get("body", "")
        entries.append({
            "title": item.get("title", ""),
            "url": entry_url,
            "date_published": date_str,
            "description": body[:500],
        })
    return entries


def main():
    existing_urls = load_existing_urls()
    feeds = load_feeds()
    today = datetime.now(JST).strftime("%Y-%m-%d")

    all_new = []

    # --- RSS/Atom フィード ---
    for feed_info in feeds:
        name = feed_info.get("name", "")
        url = feed_info.get("url", "")
        default_category = feed_info.get("default_category", "ai-workflow")

        if not url:
            continue

        print(f"Fetching: {name} ({url})", file=sys.stderr)
        root = fetch_feed(url)
        if root is None:
            continue

        entries = parse_entries(root)
        print(f"  Found {len(entries)} entries", file=sys.stderr)

        for entry in entries:
            if entry["url"] in existing_urls:
                continue

            entry["source"] = detect_source(entry["url"], name)
            entry["default_category"] = default_category
            entry["date_collected"] = today
            entry["feed_name"] = name
            entry["is_paywall"] = detect_paywall(entry.get("description", ""), entry["source"])
            all_new.append(entry)
            existing_urls.add(entry["url"])  # 同じURL が複数フィードに出る場合の重複防止

    # --- Qiita API v2 ---
    qiita_feeds = load_qiita_feeds()
    for qf in qiita_feeds:
        tag = qf.get("tag", "")
        name = qf.get("name", f"Qiita - {tag}")
        default_category = qf.get("default_category", "ai-workflow")
        per_page = qf.get("per_page", 20)

        if not tag:
            continue

        print(f"Fetching: {name} (Qiita API tag={tag})", file=sys.stderr)
        entries = fetch_qiita_articles(tag, per_page)
        print(f"  Found {len(entries)} entries", file=sys.stderr)

        for entry in entries:
            if entry["url"] in existing_urls:
                continue

            entry["source"] = "qiita"
            entry["default_category"] = default_category
            entry["date_collected"] = today
            entry["feed_name"] = name
            entry["is_paywall"] = detect_paywall(entry.get("description", ""), entry["source"])
            all_new.append(entry)
            existing_urls.add(entry["url"])

    print(f"\nTotal new articles: {len(all_new)}", file=sys.stderr)

    # 新規記事をJSON形式で標準出力（Windows cp932対策）
    output = json.dumps(all_new, ensure_ascii=False, indent=2)
    sys.stdout.buffer.write(output.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
