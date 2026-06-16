"""
inventory_select.py - 月次棚卸しの「候補抽出」。

方針（2026-06-16 確定）:
    機械的に落とすのは次の2つだけ。残りは全て LLM 採点(Track A-2)に回す。
      (1) すでに vault(sources/web)にある = 元URL一致
      (2) 明らかな宣伝・スパム = SPAM_PHRASES に一致
    本文の長短・カテゴリ・ソースでは一切落とさない。上限カットもしない。
    （短文でも有益なら採点対象。価値判断は LLM に委ねる。）

読み取り専用（index.json と一部の記事 .md を読むだけ）で、出力は
scripts/_inventory/ 以下にしか書かないため、朝のルーティンと衝突しない。

使い方:
    python scripts/inventory_select.py                      # 前回棚卸し以降（初回は全期間）
    python scripts/inventory_select.py --since 2026-06-01   # 範囲を明示
    python scripts/inventory_select.py --until 2026-04-30   # 月別バッチ用
    python scripts/inventory_select.py --no-spam            # スパム除外もしない（最も漏れない）
    python scripts/inventory_select.py --no-vault           # vault重複除外をスキップ

出力:
    scripts/_inventory/candidates-YYYY-MM-DD.json
    （survivors=採点対象の一覧 + 落とした内訳の集計・サンプル）

注意:
    .last_inventory.json（増分の起点）は棚卸し1サイクル完了後に
    --update-state を付けて更新する。本スクリプト単体では既定で更新しない。
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Windows環境でのcp932文字化け対策（build_index.py と同様）
os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "index.json"
OUT_DIR = Path(__file__).resolve().parent / "_inventory"
STATE_PATH = Path(__file__).resolve().parent / ".last_inventory.json"

# vault の web 一次資料置き場（重複チェックの突合先）
DEFAULT_VAULT_WEB = Path(r"D:\Obsidian\kagedan-work\sources\web")

JST = timezone(timedelta(hours=9))

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# 明らかな宣伝・スパムの語句（タイトルは全件、本文は X のみ走査）。
# 一般的な技術・建設記事にはまず出てこない、はっきりした販促表現に限定する。
# ※ 落とした分は必ず件数とサンプルを表示し、過剰除外がないか目視できるようにする。
SPAM_PHRASES = [
    "無料プレゼント", "無料配布", "プレゼント企画", "フォロバ", "拡散希望",
    "不労所得", "公式line", "line登録", "line@", "今だけ無料", "期間限定無料",
    "giveaway", "rt&フォロー", "フォロー&rt", "フォロー&リポスト",
    "稼ぐ方法", "副業で月", "月収", "セミナー募集", "参加者募集",
    "dmで受け取", "dmください", "limited time offer", "登録はこちら",
]


def parse_frontmatter_raw(text: str) -> dict:
    """frontmatter を key->生文字列 で返す簡易パーサ。"""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    return fm


def strip_frontmatter_body(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1).strip()


def normalize_url(u: str) -> str:
    """重複比較用に URL を正規化する（軽め）。"""
    if not u:
        return ""
    u = u.strip().strip('"').strip("'").strip().strip("[]")
    u = u.split("#", 1)[0]
    if u.endswith("/"):
        u = u[:-1]
    return u.lower()


def load_vault_urls(vault_web: Path) -> set[str]:
    """vault sources/web の全 .md から source/chat_url/url を集めて URL集合を作る。"""
    urls: set[str] = set()
    if not vault_web.exists():
        print(f"  ! vault web フォルダが見つかりません: {vault_web}（重複除外スキップ）")
        return urls
    files = list(vault_web.glob("*.md"))
    for p in files:
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fm = parse_frontmatter_raw(text)
        for key in ("source", "chat_url", "url"):
            v = fm.get(key, "")
            if v and ("http://" in v or "https://" in v):
                urls.add(normalize_url(v))
    print(f"  vault 既存URL: {len(urls)}件（{len(files)}ファイルから抽出）")
    return urls


def norm_title(t) -> str:
    if isinstance(t, list):
        t = t[0] if t else ""
    return re.sub(r"\s+", "", str(t).lower()).strip()


def resolve_since(arg_since: str | None) -> str | None:
    if arg_since:
        return arg_since
    if STATE_PATH.exists():
        try:
            st = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            last = st.get("last_inventory_date")
            if last:
                print(f"  前回棚卸し日: {last} 以降を対象")
                return last
        except (json.JSONDecodeError, OSError):
            pass
    print("  起点なし → 全期間を対象（初回想定）")
    return None


def read_body(file_path: str) -> str:
    md_path = REPO_ROOT / file_path
    if not md_path.exists():
        return ""
    try:
        return strip_frontmatter_body(md_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return ""


def find_spam(haystack: str) -> str | None:
    hl = haystack.lower()
    for ph in SPAM_PHRASES:
        if ph in hl:
            return ph
    return None


def main():
    parser = argparse.ArgumentParser(description="月次棚卸しの候補抽出（最小限の機械フィルタ）")
    parser.add_argument("--since", help="この日(date_collected)以降を対象 YYYY-MM-DD")
    parser.add_argument("--until", help="この日(date_collected)まで（任意）YYYY-MM-DD")
    parser.add_argument("--vault", default=str(DEFAULT_VAULT_WEB), help="vault sources/web パス")
    parser.add_argument("--no-vault", action="store_true", help="vault重複除外をスキップ")
    parser.add_argument("--no-spam", action="store_true", help="スパム除外もしない（最も漏れない）")
    parser.add_argument("--out", default=str(OUT_DIR), help="出力ディレクトリ")
    parser.add_argument("--update-state", action="store_true",
                        help="完了後 .last_inventory.json を今日の日付に更新する")
    args = parser.parse_args()

    print("=== inventory_select: 候補抽出（落とすのは vault既存＋スパムのみ）===")
    index_data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    articles = index_data["articles"]
    print(f"index.json: {len(articles)}件")

    since = resolve_since(args.since)
    until = args.until

    vault_urls: set[str] = set()
    if not args.no_vault:
        vault_urls = load_vault_urls(Path(args.vault))

    stat = {"scanned": 0, "out_of_range": 0, "vault_dup": 0,
            "spam": 0, "dedup": 0, "candidate": 0}
    by_source: dict[str, int] = {}
    by_category: dict[str, int] = {}
    spam_samples: list[dict] = []

    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    candidates: list[dict] = []

    for a in articles:
        dc = a.get("date_collected", "")
        if since and dc < since:
            stat["out_of_range"] += 1
            continue
        if until and dc > until:
            stat["out_of_range"] += 1
            continue
        stat["scanned"] += 1

        title = a.get("title", "")
        if isinstance(title, list):
            title = title[0] if title else ""
        source = a.get("source", "")
        category = a.get("category", "")
        nurl = normalize_url(a.get("url", ""))

        # (1) vault に既にある（URL一致）→ 落とす
        if nurl and nurl in vault_urls:
            stat["vault_dup"] += 1
            continue

        # (2) 明らかなスパム → 落とす。X(bot投稿)に限定する。
        # note/zenn/qiita 等の「記事」はタイトルに副業/不労所得等が出ても
        # 本物の記事なので落とさず LLM 採点に回す（有益さは LLM が判断）。
        if not args.no_spam and source == "x":
            hay = f"{title}\n{read_body(a.get('file_path', ''))}"
            hit = find_spam(hay)
            if hit:
                stat["spam"] += 1
                if len(spam_samples) < 25:
                    spam_samples.append({"phrase": hit, "title": title[:60],
                                         "source": source, "url": a.get("url", "")})
                continue

        # KB内の同一URL/同一タイトルの重複は1件に畳む（同じ内容の重複排除）
        if nurl and nurl in seen_urls:
            stat["dedup"] += 1
            continue
        ntitle = norm_title(title)
        if ntitle and ntitle in seen_titles:
            stat["dedup"] += 1
            continue
        if nurl:
            seen_urls.add(nurl)
        if ntitle:
            seen_titles.add(ntitle)

        candidates.append({
            "id": a.get("id", ""),
            "title": title,
            "url": a.get("url", ""),
            "source": source,
            "category": category,
            "date_published": a.get("date_published", ""),
            "date_collected": dc,
            "file_path": a.get("file_path", ""),
        })
        stat["candidate"] += 1
        by_source[source] = by_source.get(source, 0) + 1
        by_category[category] = by_category.get(category, 0) + 1

    # 採点しやすい順に: date_collected 降順（新しい順）。価値の事前判断はしない。
    candidates.sort(key=lambda c: c.get("date_collected", ""), reverse=True)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(JST).strftime("%Y-%m-%d")
    out_path = out_dir / f"candidates-{today}.json"
    payload = {
        "generated_at": datetime.now(JST).strftime("%Y-%m-%dT%H:%M:%S+09:00"),
        "since": since or "(all)",
        "until": until or "(none)",
        "policy": "drop only: vault-dup(url) + obvious-spam; everything else -> LLM scoring",
        "stat": stat,
        "spam_samples": spam_samples,
        "count": len(candidates),
        "candidates": candidates,
    }
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("\n--- 結果サマリ ---")
    print(f"対象範囲スキャン: {stat['scanned']}件（範囲外 {stat['out_of_range']}件）")
    print(f"落とした① vault既存(URL一致): {stat['vault_dup']}件")
    print(f"落とした② 明らかなスパム: {stat['spam']}件")
    print(f"KB内 同一URL/タイトルの重複畳み込み: {stat['dedup']}件")
    print(f"=> 採点対象(survivors): {len(candidates)}件")
    print("\nソース別 採点対象:")
    for s, n in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {s}: {n}")
    print("カテゴリ別 採点対象:")
    for c, n in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {c}: {n}")
    if spam_samples:
        print(f"\nスパム除外サンプル（最大25件表示, 計{stat['spam']}件）:")
        for s in spam_samples[:25]:
            print(f"  [{s['phrase']}] {s['source']:<6} | {s['title']}")
    print(f"\n出力: {out_path}")

    if args.update_state:
        STATE_PATH.write_text(
            json.dumps({"last_inventory_date": today}, ensure_ascii=False) + "\n",
            encoding="utf-8")
        print(f".last_inventory.json を {today} に更新")


if __name__ == "__main__":
    main()
