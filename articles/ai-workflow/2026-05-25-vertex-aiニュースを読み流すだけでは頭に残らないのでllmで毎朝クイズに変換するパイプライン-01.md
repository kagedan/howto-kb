---
id: "2026-05-25-vertex-aiニュースを読み流すだけでは頭に残らないのでllmで毎朝クイズに変換するパイプライン-01"
title: "【Vertex AI】ニュースを読み流すだけでは頭に残らないので、LLMで毎朝クイズに変換するパイプラインを作った"
url: "https://qiita.com/hamham/items/1c17ad408c9e2f3d98b0"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "LLM", "Python", "qiita"]
date_published: "2026-05-25"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

# はじめに

業界ニュースを日常的にキャッチアップしたいと思いつつ、ニュース記事をただ読み流すだけだとなかなか頭に残らないのが悩みでした。
そこで、LLMを使ってニュース記事を4択クイズに変換し、クイズ形式で知識を定着させるWebアプリを作っています。
こんなイメージです。

![スクリーンショット 2026-05-22 210704.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/272753/1bb43993-5b0c-44ae-85a7-1ba9f36ce1f9.png)

この記事では、その中でも**日次クイズ生成パイプライン**——つまり「どうやって毎朝ニュースが自動でクイズに変わるのか」の部分を、設計判断の背景も含めて解説します。

### こんな構成です

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/272753/6b8f574e-0d8f-4391-a455-31bd7b8d15d4.png)


Cloud Scheduler が毎朝7時に Cloud Run ジョブを起動し、**RSSフィード取得 → Vertex AI（Claude）でクイズ生成 → Firestore格納** を一気通貫で行います。

---

# なぜ「バッチ事前生成」を選んだか

LLMでコンテンツを生成する方法は、大きく2パターンあります。

| | リアルタイム生成 | バッチ事前生成 |
|---|---|---|
| レイテンシ | ユーザーリクエスト時にLLM呼び出し（数秒〜十数秒） | 事前生成済みなので即レスポンス |
| コスト予測 | トラフィックに比例して増加 | 日次固定（1日1回のみ） |
| エラー耐性 | ユーザー体験に直結 | リトライ可能、失敗しても既存データで継続 |
| 品質管理 | リアルタイムで品質担保が難しい | 生成後に検証する余地がある |

結論から言うと、**バッチ事前生成** を選びました。理由はシンプルで、

1. **クイズ表示まで数秒待たせるのはNG** — 事前生成すればFirestoreからの読み出しだけで済み、レスポンスはミリ秒単位
2. **コストが読める** — 1日4カテゴリ × 最大10問 = 固定トークン量。ユーザーが増えてもLLMコストは変わらない
3. **失敗してもリトライできる** — Cloud Run ジョブは `max_retries=2` を設定しているので、LLMの一時的な障害でも自動リカバリ

### なぜ Cloud Run ジョブなのか

Cloud Functions（第2世代）やGKE CronJobも候補でしたが、Cloud Run ジョブを選んだ決め手はこのあたりです。

- **常駐不要**: 1日1回、数十秒動けばいいタスクにフルマネージドのジョブ実行はぴったり
- **タイムアウト300秒**: 余裕あり（実際は数十秒で終わる）
- **Cloud Schedulerと相性抜群**: HTTP POSTでトリガー、OAuthトークンも自動付与
- **Dockerベース**: `feedparser` や `anthropic[vertex]` など好きなPythonライブラリを自由に入れられる

### ローテーション戦略

毎朝「古い10件を削除 → 新規10件を生成」というシンプルなローテーションです。常に最新ニュースに基づいたクイズが並ぶので、同じ問題を繰り返し見ることもありません。

```python
def _delete_oldest_quizzes(count: int):
    collection = db.collection("quizzes")
    oldest = collection.order_by("created_at").limit(count).stream()
    for doc in oldest:
        doc.reference.delete()
```

---

# Vertex AI 経由で Claude を使う

## なぜ Vertex AI 経由なのか

Anthropic APIを直接叩く選択肢もありますが、GCPで完結するプロジェクトではVertex AI経由にメリットがあります。

**1. APIキー管理不要（IAMで完結）**

Anthropic APIを直接使う場合、APIキーの発行・ローテーション・シークレット管理が必要です。
Vertex AI 経由なら、サービスアカウントのIAM権限だけで認証が完了するため、キー管理の負担がなくなります。

```
# 必要なIAMロール
roles/aiplatform.user
```

Cloud Run ジョブに紐づくサービスアカウントにこのロールを付与すれば、コード内でAPIキーを管理する必要はありません。

**2. 認証基盤が統一できる**

同じサービスアカウントで Cloud Storage への書き込み、Firestore への読み書き、Vertex AI への推論リクエストがすべて行えます。認証情報が分散しないため、運用負荷とセキュリティリスクを抑えられます。

**3. 組織ポリシーとの整合**

エンタープライズ環境だと「外部APIへの直接通信を制限する」組織ポリシーがあったりします。Vertex AI 経由ならGCP内部で完結するので、VPC Service Controls とも統合可能です。

## 実装方法

`anthropic[vertex]` SDKを使うと、通常のAnthropic SDKとほぼ同じインターフェースでVertex AI経由の呼び出しが可能です。

```python
from anthropic import AnthropicVertex

# 環境変数から設定を読み込み
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "")
REGION = os.environ.get("GCP_REGION", "asia-northeast1")
MODEL_ID = os.environ.get("VERTEX_AI_MODEL", "claude-sonnet-4-6-20250514")

# クライアント初期化 - APIキー不要、IAMで自動認証
client = AnthropicVertex(region=REGION, project_id=PROJECT_ID)

# 通常のMessages APIと同じインターフェース
response = client.messages.create(
    model=MODEL_ID,
    max_tokens=4096,
    messages=[{"role": "user", "content": prompt}],
)
```

ポイントをまとめると、

- `AnthropicVertex` クラスがIAM認証を自動処理する。Cloud Run ジョブ上では ADC（Application Default Credentials）が使われる
- `region` に `asia-northeast1`（東京）を指定してレイテンシを最小化
- APIのインターフェースは通常の `anthropic` パッケージと同一のため、ローカル開発時はAPI直接、本番はVertex AI経由、という使い分けも可能

**Tips：モデルIDは環境変数で外出しにしよう**

モデルIDをハードコードしてしまうと、新バージョンへの切り替えのたびにコード変更＋再デプロイが必要です。
環境変数にしてTerraformで管理すれば、`terraform apply` だけでモデル切り替えが完了します。

```hcl
variable "vertex_ai_model" {
  description = "Vertex AI Claude model ID"
  type        = string
  default     = "claude-sonnet-4-6-20250514"
}

resource "google_cloud_run_v2_job" "news_fetcher" {
  # ...
  template {
    template {
      containers {
        env {
          name  = "VERTEX_AI_MODEL"
          value = var.vertex_ai_model
        }
      }
    }
  }
}
```

---

# RSS → LLM → Firestore のデータフロー

ここからはパイプラインの各ステップを具体的に見ていきます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/272753/498d5a6a-5d78-4f0c-9ce7-6a22d5c30f4f.png)


## Step 1. RSSフィード取得

4つの業界カテゴリごとに、公開RSSフィードから最新ニュースを取得します。

```python
RSS_FEEDS = {
    "IT": ["https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml"],
    "金融": ["https://www.nhk.or.jp/rss/news/cat5.xml"],        # NHK経済ニュース
    "製造": ["https://rss.itmedia.co.jp/rss/2.0/monoist.xml"],   # MONOist（製造業向け）
    "小売": ["https://diamond-rm.net/feed"],                      # ダイヤモンド・リテイルメディア
}

def _fetch_rss_articles(feed_urls: list[str]) -> list[dict]:
    articles = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:  # 各フィードから上位5件
            articles.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", entry.get("description", "")),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
            })
    return articles
```

各フィードから**上位5件に絞っている**のは、LLMに大量の記事を投入しても品質が上がるわけではないのと、最終的に各カテゴリ2〜3問の生成が目標なので5記事あれば十分な素材、という判断です。

## Step 2. 生データをCloud Storageに保存

LLMに投入する前に、取得した生データをそのままCloud Storageに保存しておきます。

```python
def _save_articles_to_gcs(industry: str, articles: list[dict]):
    bucket = storage_client.bucket(NEWS_BUCKET)
    date_str = datetime.now(timezone.utc).strftime("%Y/%m/%d")
    blob = bucket.blob(f"raw/{industry}/{date_str}/articles.json")
    blob.upload_from_string(
        json.dumps(articles, ensure_ascii=False),
        content_type="application/json",
    )
```

パスは `raw/{industry}/{YYYY/MM/DD}/articles.json` という構造。「いつ、どの業界の、どんな記事を元にクイズを作ったか」が一目でわかります。

**なぜ生データを残すのか？**

- **再現性の確保**: LLMの出力は非決定的。品質に問題があったときにプロンプトを修正して再生成できる
- **プロンプト改善の素材**: 過去の生データで新旧プロンプトの出力を比較できる
- **監査証跡**: 生成クイズの正確性に疑義が出たとき、元ソースまで遡れる

**Tips：ライフサイクルでコスト最適化**

生データを残し続けるとストレージコストが積み上がるので、Terraformでライフサイクルルールを設定しています。

```hcl
lifecycle_rule {
  action { type = "SetStorageClass" storage_class = "NEARLINE" }
  condition { age = 90 }
}
lifecycle_rule {
  action { type = "Delete" }
  condition { age = 365 }
}
```

90日でNEARLINEに移行、365日で自動削除。直近データはすぐアクセスできつつ、長期のコストは抑えられます。

## Step 3. プロンプト設計とLLM呼び出し

パイプラインの核となる部分です。プロンプトの設計がクイズの品質を直接左右します。

```python
QUIZ_GENERATION_PROMPT = """あなたはニュースクイズの作成者です。
以下のニュース記事から4択クイズを生成してください。

## ニュース記事
{articles}

## 出力形式
以下のJSON配列形式で出力してください。各クイズは以下のフィールドを持ちます:
- category: カテゴリ（"企業動向", "業界トレンド", "決算・業績", "人事・組織" のいずれか）
- industry: 業種（"{industry}"）
- difficulty: 難易度（1=基本, 2=応用, 3=発展）
- question: 問題文（具体的で明確な質問）
- choices: 選択肢（4つの文字列配列）
- correct: 正解のインデックス（0-3）
- explanation: 解説（正解の根拠を簡潔に説明）

## ルール
- 1つの記事につき1問作成
- 問題文は事実に基づくこと
- 不正解の選択肢はもっともらしいが明確に誤りであること
- 解説は学習効果が高い内容にすること
- 最大{max_quizzes}問まで

## 出力
JSONのみを出力してください（マークダウンのコードブロックは不要）:
"""
```

### プロンプト設計で意識したこと

1. **「1記事1問」ルール** — 1つの記事から複数問を作らせると似た問題が出がち。1記事1問にすることで多様なトピックのクイズが得られる
2. **JSON直接出力を指示** — コードブロックで囲むなと明示。それでも稀に囲んでくるので後処理で除去する（後述）
3. **カテゴリ・難易度はLLMに判定させる** — 「この記事は企業動向か業界トレンドか」を人手でルール化するのは大変。LLMなら文脈から適切に分類してくれる
4. **解説フィールドを含める** — 「なぜそれが正解なのか」を出力させることで、ユーザーの学習効果がぐっと上がる

### LLMレスポンスの防御的パース

LLMの出力を本番データとしてそのまま使うので、「想定外の出力」への対処は必須です。

```python
content = response.content[0].text.strip()

# マークダウンコードブロックの除去（LLMが稀に付与する）
if content.startswith("```"):
    content = content.split("\n", 1)[1]
    content = content.rsplit("```", 1)[0]

quizzes = json.loads(content)
```

プロンプトで「JSONのみ出力して」と指示しても、100%守られる保証はありません。この種の防御的パースは、LLM出力を本番データに使う場合の定石です。

## Step 4. Firestoreへの格納

生成されたクイズをFirestoreに保存して、APIから配信できるようにします。

```python
def _save_quizzes(quizzes: list[dict], industry: str):
    collection = db.collection("quizzes")
    for quiz in quizzes:
        quiz_id = str(uuid.uuid4())
        item = {
            "quiz_id": quiz_id,
            "category": quiz.get("category", "業界トレンド"),
            "industry": industry,
            "difficulty": quiz.get("difficulty", 1),
            "question": quiz.get("question", ""),
            "choices": quiz.get("choices", []),
            "correct": quiz.get("correct", 0),
            "explanation": quiz.get("explanation", ""),
            "created_at": int(time.time()),
            "source": "rss_vertex_ai",
        }
        collection.document(quiz_id).set(item)
```

`source: "rss_vertex_ai"` というフィールドを入れているのは、将来的に別ソース（手動作成、別モデル等）からのクイズが追加される可能性を見据えてのことです。「Vertex AI生成クイズの正答率はどうか」みたいな分析をするとき、このフィールドでフィルタできます。

**Firestoreインデックス設計：**

```
Composite Index: quizzes(industry ASC, created_at DESC)
```

APIからの主なクエリパターンは「特定の業界の最新クイズをN件取得」なので、このComposite Indexで効率的に読み出せます。

---

# 運用で気をつけたこと

## エラーハンドリング

LLMの出力は非決定的なので、以下のケースすべてに対応しています。

- **JSONパース失敗**: LLMがJSON以外を返した場合 → 空リストを返してスキップ
- **フィールド欠損**: `.get()` にデフォルト値を設定して、LLMが一部省略しても動く
- **RSS取得失敗**: 1つのフィードが死んでも他のフィードは処理を継続

```python
try:
    quizzes = json.loads(content)
    if isinstance(quizzes, list):
        return quizzes[:max_quizzes]
    return []
except Exception as e:
    print(f"Quiz generation error ({industry}): {e}")
    return []
```

## リトライ設計

Cloud Run ジョブの設定で `max_retries=2` を指定。ジョブ全体が冪等に設計されている（最古のN件を削除→新規生成）ので、リトライしても重複生成のリスクはありません。

## コスト感

1日あたりのLLMコストを試算するとこんな感じです。

- 入力: 4カテゴリ × 2〜3記事 × 約500トークン/記事 + プロンプト ≈ 6,000 input tokens
- 出力: 合計10問 × 約300トークン/問 ≈ 3,000 output tokens
- Claude Sonnet のVertex AI料金: input 3ドル/MTok, output 15ドル/MTok
- **日次コスト: 約 0.06ドル（月額約 2ドル）**

サーバーレス構成のため、Cloud Run の実行時間（数十秒）分の料金もほぼ無視できる水準です。

---

# さいごに

この構成のポイントをまとめると、以下の3つの設計判断がうまく噛み合っています。

1. **バッチ事前生成** — コスト予測可能性とユーザー体験を両立
2. **Vertex AI経由のClaude** — GCPネイティブな認証基盤でAPIキー管理を排除
3. **生データ保存 + Firestoreへの構造化格納** — 再現性を確保しつつ低レイテンシの配信を実現

このパターンはニュースクイズに限らず、「外部データソースをLLMで加工し、構造化データとして配信する」あらゆるユースケースに応用できます。

- 業界レポートの自動要約・FAQ生成
- 技術ドキュメントからの練習問題生成
- ニュースフィードからの投資サマリー生成

LLMを「リアルタイムで対話させる」だけでなく、「裏方のバッチ処理として回す」という活用パターンの参考になれば幸いです。
