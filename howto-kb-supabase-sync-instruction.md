# howto-kb Supabase同期 実装指示書

## 概要

index.jsonのメタデータをSupabaseにも同期する仕組みを追加する。
GitHubのMarkdown＋index.jsonはそのまま維持し、Supabaseは検索・参照用APIとして併用する。

## 背景

- index.jsonが1,500件超に肥大化し、Claude.aiのweb fetchで全件取得が困難
- raw.githubusercontent.com のCDNキャッシュが数日更新されない問題
- Supabaseに同期することで、URLにクエリパラメータを付けるだけで絞り込み参照が可能になる

## Supabase環境情報

- プロジェクト名: howto-kb
- リージョン: Northeast Asia (Tokyo)
- Project URL: `https://gryrgjnfekwptyngbmao.supabase.co`
- anon key: `sb_publishable_How0RxnjdME_nNlnAhJ9Vg_Y982jDum`

### テーブル定義（作成済み）

```sql
CREATE TABLE articles (
  id TEXT PRIMARY KEY,
  title TEXT,
  url TEXT,
  source TEXT,
  category TEXT,
  tags TEXT[],
  date_published DATE,
  date_collected DATE,
  file_path TEXT
);
```

RLS設定済み（匿名ユーザーに読み取り許可）。
テスト用に5件のデータが入っている。

## 実装タスク

### タスク1: sync_supabase.py を新規作成

`scripts/sync_supabase.py` として作成する。

**機能:**
- index.jsonを読み込み、全記事をSupabaseのarticlesテーブルにupsertする
- upsertのキーはid列（PRIMARY KEY）
- titleがリスト形式の場合は最初の要素を文字列として使用する（index.jsonに一部そういうデータがある）

**Supabase REST API でのupsert方法:**

```python
import requests
import json

SUPABASE_URL = "https://gryrgjnfekwptyngbmao.supabase.co"
SUPABASE_KEY = "sb_publishable_How0RxnjdME_nNlnAhJ9Vg_Y982jDum"

def upsert_articles(articles):
    """articlesリストをSupabaseにupsert"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    # Supabase REST APIは1リクエストで複数行をupsertできる
    # ただし大量データは500件ずつに分割して送る
    batch_size = 500
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i+batch_size]
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/articles",
            headers=headers,
            json=batch
        )
        if response.status_code not in (200, 201):
            print(f"Error: {response.status_code} - {response.text}")
        else:
            print(f"Upserted {len(batch)} articles (batch {i//batch_size + 1})")
```

**データ変換の注意点:**
- index.jsonのtitleフィールドが配列の場合がある → `title[0]` を使う
- tagsは Python リスト → そのまま JSON 配列として送れる
- date_published, date_collected は "YYYY-MM-DD" 文字列 → そのまま送れる

**実行方法:**

```bash
python scripts/sync_supabase.py
```

引数なしで実行すると、index.jsonを読み込んで全件upsertする。

### タスク2: build_index.py の末尾に Supabase同期を追加

build_index.py の処理完了後（index.json書き出し後）に、sync_supabase.pyの関数を呼び出す。

```python
# build_index.py の末尾に追加
try:
    from sync_supabase import sync_to_supabase
    sync_to_supabase(index_data["articles"])
    print("Supabase同期完了")
except Exception as e:
    print(f"Supabase同期エラー（続行）: {e}")
```

**重要:** Supabase同期が失敗しても、build_index.pyの処理自体は正常完了させる。
Supabaseはあくまで補助的な参照手段であり、GitHubが正とする。

### タスク3: 初回全件同期の実行

1. `python scripts/sync_supabase.py` を実行してindex.jsonの全件をSupabaseに投入
2. 投入後、以下のURLで件数を確認:
   ```
   https://gryrgjnfekwptyngbmao.supabase.co/rest/v1/articles?select=count&apikey=sb_publishable_How0RxnjdME_nNlnAhJ9Vg_Y982jDum
   ```
3. index.jsonのtotal_countと一致すれば成功

### タスク4: CLAUDE.md に Supabase情報を追記

CLAUDE.mdに以下を追記する:

```markdown
## Supabase（検索・参照用API）

index.jsonのメタデータはSupabaseにも同期されている。
Claude.aiからの参照はSupabase経由が推奨（CDNキャッシュ問題なし、クエリ絞り込み可能）。

- Project URL: https://gryrgjnfekwptyngbmao.supabase.co
- REST API: https://gryrgjnfekwptyngbmao.supabase.co/rest/v1/articles

### クエリ例

全件（新しい順、20件）:
?select=*&order=date_published.desc&limit=20&apikey=sb_publishable_How0RxnjdME_nNlnAhJ9Vg_Y982jDum

カテゴリ絞り込み:
?select=*&category=eq.construction&order=date_published.desc&limit=20&apikey=...

日付絞り込み:
?select=*&date_published=gte.2026-03-20&order=date_published.desc&apikey=...

タグ絞り込み:
?select=*&tags=cs.{MCP}&order=date_published.desc&apikey=...

ソース絞り込み:
?select=*&source=eq.x&order=date_published.desc&limit=20&apikey=...
```

## 実行順序

1. sync_supabase.py を作成
2. テスト用の5件を削除してから初回全件同期を実行
3. ブラウザでAPI確認（件数一致チェック）
4. build_index.py にSupabase同期呼び出しを追加
5. CLAUDE.md に Supabase情報を追記
6. Git commit & push

## 注意事項

- anon keyはRLS（読み取り専用）で保護されているため、publicリポジトリに含めても安全
- ただしwrite操作もanon keyで可能なため、本格運用時はwrite用にservice_role keyを使い、anon keyはSELECTのみに制限するRLSポリシーにする（現在はそうなっている）
- Supabase無料プランは一定期間アクセスがないとプロジェクトが一時停止する → 日次タスクで毎日同期すれば問題なし
- requestsライブラリが必要（未インストールなら `pip install requests`）
