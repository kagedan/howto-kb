---
id: "2026-06-21-毎朝discordにai厳選itニュースが届くbotをaws-lambda-claudeで作った-01"
title: "毎朝DiscordにAI厳選ITニュースが届くBotをAWS Lambda + Claudeで作った"
url: "https://zenn.dev/yu045/articles/f1dbfbffa2a578"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "OpenAI", "GPT"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

## はじめに

IT系のニュースをチェックしたいと考えたが、情報が多すぎてどれを見ればいいか迷ってしまう。そこで「AIに厳選させたニュースをさせてかつ、自身がよく使用しているDiscordに送らせればいいのでは」と思い、今回のシステムを作成しようと思い至った。

**作ったもの:**

* 6 つのニュースソースから最大 120 件の記事を自動収集
* Claude AI がエンジニア視点でトップ 5 件を厳選・日本語要約
* 毎朝 6:00 JST に Discord へ自動配信
* AWS のサーバーレス構成で **ランニングコストはほぼゼロ**  
  *↓ 毎朝こんな感じで届く*  
  ![](https://static.zenn.studio/user-upload/730de3a9e8f0-20260621.png)

## システム構成

```
EventBridge Scheduler（毎朝 6:00 JST）
         │
         ▼
  Lambda Function（Python 3.13）
         │
         ├─① SSM Parameter Store からシークレット取得
         ├─② RSS / Hacker News API から記事収集（最大 120 件）
         ├─③ Claude claude-haiku-4-5 でトップ 5 件を厳選・日本語要約
         └─④ Discord Webhook へ Embed 形式で送信
```

**使用技術スタック**

| 用途 | 採用技術 |
| --- | --- |
| 実行基盤 | AWS Lambda（Python 3.13） |
| スケジューリング | AWS EventBridge Scheduler |
| シークレット管理 | AWS SSM Parameter Store |
| AI 厳選・要約 | Anthropic Claude claude-haiku-4-5 |
| RSS 取得 | feedparser 6.0.11 |
| HTTP クライアント | httpx 0.28.1 |
| 外部ライブラリ管理 | Lambda Layer |
| 配信先 | Discord Webhook（Embed 形式） |

**ニュースソース一覧**

| ソース | 種別 | 言語 |
| --- | --- | --- |
| Hacker News | JSON API | 英語 |
| TechCrunch | RSS | 英語 |
| The Verge | RSS | 英語 |
| Zenn トレンド | RSS | 日本語 |
| Qiita トレンド | RSS | 日本語 |
| ITmedia | RSS | 日本語 |

### AWSの選定理由

私自身がAWSを触ったことがなかったこと、後述しますが今回のシステムならAWSを無料の範囲内で使用できそうだったこ。  
これらの理由からAWSを使うようにしました。

### コストについて

Lambda・EventBridge・SSM は今回の使い方（1日1回・数十秒の実行）では**すべて無料枠内**です。費用が発生するのは Claude API のみで、月あたり **$0.05〜$0.15 程度**です。

## ディレクトリ構成

```
App/
├── lambda_function.py    # Lambda エントリーポイント（オーケストレーター）
├── ssm_client.py         # SSM からシークレット取得
├── news_fetcher.py       # RSS / Hacker News 記事取得
├── ai_ranker.py          # Claude AI 厳選・要約
├── discord_notifier.py   # Discord Webhook 送信
├── models.py             # dataclass（Article, BotConfig）
├── config.py             # 定数・ニュースソース定義
├── requirements.txt      # 外部ライブラリ（Lambda Layer 用）
├── run_local.py          # ローカル実行スクリプト
```

各モジュールの責務を 1 つに絞り、`lambda_function.py` がパイプラインのように順番に呼び出す設計にしています。各モジュールは `list[Article]` か `BotConfig` のやり取りだけを知っており、互いの内部実装に依存しません。

## 実装のポイント

### 1. lambda\_function.py はただのオーケストレーター

エントリーポイントは処理の流れを読むだけで済むように、ロジックを一切持たせませんでした。例外は各モジュールから伝播させ、Lambda の失敗ログとして CloudWatch に記録します。

```
def lambda_handler(event: dict, context: object) -> dict:
    logger.info("[START] App Lambda started")

    config  = get_config()                       # ① SSM からシークレット取得
    articles = fetch_all_articles()              # ② 全ソースから記事収集
    if len(articles) == 0:
        return {"statusCode": 200, "body": "No articles"}

    ranked = rank_and_summarize(articles, config) # ③ Claude で厳選・要約
    send(ranked, config)                          # ④ Discord へ送信

    logger.info("[END] App Lambda completed successfully")
    return {"statusCode": 200, "body": json.dumps(f"Sent {len(ranked)} articles")}
```

### 2. データモデルは `@dataclass(slots=True)` で軽量に

記事 1 件を表す `Article` と設定値を束ねる `BotConfig` の 2 つだけを定義しています。`slots=True` を指定すると `__slots__` が自動生成され、通常の dataclass よりメモリ効率が良くなります。120 件分のオブジェクトを扱う今回のケースでは特に有効です。

```
@dataclass(slots=True)
class Article:
    title:   str
    url:     str
    source:  str
    color:   int        # Discord Embed のカラーコード（ソースごとに色分け）
    summary: str = ""   # Claude が後から書き込む
    rank:    int = 0    # Claude が後から書き込む
```

`summary` と `rank` の初期値を空・0 にしておき、AI 厳選フェーズで直接代入する設計です。`slots=True` の dataclass でも通常の属性代入で問題なく動きます。

### 3. ニュース取得：1 ソースが落ちても止めない

各ソースの取得を個別に `try/except` で囲み、失敗したソースは WARNING ログに記録してスキップします。全ソースが失敗した場合のみ空リストを返し、`lambda_handler` 側で Discord 送信をスキップします。

```
def fetch_all_articles() -> list[Article]:
    all_articles: list[Article] = []
    seen_urls: set[str] = set()   # URL の重複除去用

    for source in NEWS_SOURCES:
        try:
            articles = _fetch_hackernews(source) if source["type"] == "hackernews" \
                       else _fetch_rss(source)
            # 同じ URL が複数ソースに出た場合は最初の 1 件のみ追加
            for article in articles:
                if article.url not in seen_urls:
                    seen_urls.add(article.url)
                    all_articles.append(article)
        except Exception as e:
            logger.warning(f"[FETCH] {source['name']}: failed ({e}), skipping")

    return all_articles
```

RSS 取得では `feedparser` の `bozo` フラグを確認します。`bozo=True` かつ `entries` が空の場合はパース失敗として最大 2 回リトライします。

```
feed = feedparser.parse(source["url"], request_headers={"User-Agent": "App/1.0"})
if feed.bozo and len(feed.entries) == 0:
    raise ValueError(f"Feed parse error: {feed.bozo_exception}")
```

Hacker News は RSS がないため JSON API を使います。`topstories.json` でトップ ID 一覧を取得し、各記事の詳細を順次リクエストします。「Ask HN」などの URL なし投稿はスキップします。

```
resp = client.get(f"{base_url}/topstories.json")
top_ids: list[int] = resp.json()[:MAX_ARTICLES_PER_SOURCE]

for item_id in top_ids:
    item = client.get(f"{base_url}/item/{item_id}.json").json()
    if not item.get("url"):
        continue   # Ask HN などはスキップ
```

### 4. Claude へのプロンプト設計

**タイトルと URL だけを渡す**

記事本文は渡しません。タイトルだけでも重要度の判断には十分で、トークンコストを大幅に抑えられます。

**インデックスで記事を参照させる**

Claude に「元の記事リストの何番目か」を `index` として返させます。URL をそのまま返させると転記ミスが起こりやすいですが、インデックスなら間違えようがありません。

```
# ユーザープロンプトの形式
[0] TechCrunch | OpenAI announces GPT-5
    URL: https://techcrunch.com/...
[1] Zenn | Pythonで始めるLLM開発入門
    URL: https://zenn.dev/...
...（最大 120 件）
```

**JSON のみを出力させる**

前置きや説明文が混入すると後のパースが壊れるため、システムプロンプトで厳しく指定します。

```
SYSTEM_PROMPT = """あなたはIT・テクノロジー分野の優秀なニュースキュレーターです。
与えられた記事リストから、以下の基準でトップ{n}件を厳選してください。

厳選基準：
- IT・テクノロジーの重要度・インパクト
- 新規性・話題性
- エンジニアやIT従事者への関連性

必ず以下のJSON形式のみで出力してください。説明文や前置きは不要です：
[
  {{
    "index": 記事リストの0始まりインデックス（整数）,
    "rank": 順位（1が最重要）,
    "summary": "1〜2文の日本語要約。元記事が英語でも日本語で書くこと。"
  }}
]"""
```

**レスポンスの堅牢なパース**

「必ず JSON のみ」と指示しても、Claude が稀に前置き文を付けることがあります。`re.search` で JSON 配列部分だけを抽出することで対応しています。

```
json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
if not json_match:
    raise ValueError(f"Claude response does not contain JSON array: {response_text[:200]}")

ranked_data = json.loads(json_match.group())
```

### 5. Discord への送信

**5 件を 1 リクエストにまとめる**

Discord Webhook は 1 メッセージに最大 10 件の Embed を含められます。5 件をまとめて送ることで API 呼び出しは 1 回で済みます。

**Discord の文字数制限に対応する**

Embed には上限があるため、送信前にクリップします。

| フィールド | Discord の上限 | 本実装での対応 |
| --- | --- | --- |
| title | 256 文字 | `article.title[:256]` |
| description（要約） | 4,096 文字 | `article.summary[:200]`（5件×200文字でも合計1,000文字と余裕あり） |

```
def _build_payload(articles: list[Article]) -> dict:
    today = datetime.now(JST).strftime("%Y/%m/%d")
    embeds = []
    for article in articles:
        embeds.append({
            "title":       article.title[:256],
            "url":         article.url,
            "description": article.summary[:200],
            "color":       article.color,          # ソースごとに色分け
            "footer":      {"text": article.source},
        })
    return {
        "username": "IT News Bot",
        "content":  f"📰 **本日のITニュース TOP{len(articles)}（{today}）**",
        "embeds":   embeds,
    }
```

**ソースごとにカラーコードを変える**

フッターのソース名と合わせて色でも一目で出所がわかるようにしました。

```
NEWS_SOURCES = [
    {"name": "Hacker News", "color": 0xFF6600},  # オレンジ
    {"name": "TechCrunch",  "color": 0x33CC44},  # グリーン
    {"name": "The Verge",   "color": 0xFF0000},  # レッド
    {"name": "Zenn",        "color": 0x3CB7D7},  # ブルー
    {"name": "Qiita",       "color": 0x55C500},  # グリーン（濃）
    {"name": "ITmedia",     "color": 0x8B00FF},  # パープル
]
```

**429 / 5xx のみリトライする**

Discord Webhook のエラーをステータスコードで分類し、リトライ対象を絞ります。Webhook URL 自体が誤っている 401 などは即座に失敗させます。

```
if resp.status_code == 204:
    return  # 成功

if resp.status_code == 429 or resp.status_code >= 500:
    # 5 秒待機してリトライ（最大 3 回）
    raise httpx.HTTPStatusError(...)

resp.raise_for_status()  # 400 / 401 はここで即時例外
```

## ハマったポイント

### ①：Lambda Docker イメージのエントリーポイント

Lambda Layer を Docker でビルドする際、最初にこのエラーで詰まりました。

```
$ docker run --rm public.ecr.aws/lambda/python:3.13 pip install feedparser ...
entrypoint requires the handler name to be the first argument
```

`public.ecr.aws/lambda/python:3.13` は Lambda 専用の独自エントリーポイントを持っており、渡したコマンドを「Lambda ハンドラー名」として解釈しようとします。`pip` をハンドラー名として渡しても当然失敗します。

`--entrypoint ""` でエントリーポイントを無効化すれば解決します。

```
# NG
docker run --rm \
  public.ecr.aws/lambda/python:3.13 \
  pip install -r requirements.txt ...

# OK
docker run --rm \
  --entrypoint "" \                  # ← エントリーポイントを無効化
  public.ecr.aws/lambda/python:3.13 \
  pip install -r requirements.txt ...
```

### ②：AWSのサービスのリージョン違い

AWS LambdaやAWS SSM Parameter Storeなどの各サービスのリージョン設定で詰まりました。  
基本的にリージョンを東京にしていたが、AWS SSM Parameter Storeだけシドニーになっており、コマンドで登録したAWS SSM Parameter Storeの確認をした際に内容が何も表示されなくてリージョン違いを発見するまで時間がかかってしまいました。

## デプロイ手順（概要）

デプロイは以下の 7 ステップです。

1. **SSM Parameter Store** にシークレット 3 件を登録

   * `/App/anthropic_api_key`（SecureString）
   * `/App/discord_webhook_url`（SecureString）
   * `/App/discord_channel_name`（String）
2. **Lambda 関数**を作成

   * ランタイム: Python 3.13 / アーキテクチャ: x86\_64
   * タイムアウト: 5 分 / メモリ: 256 MB
3. **Lambda の IAM ロール**に SSM 読み取り権限を付与

   ```
   {
     "Action": ["ssm:GetParameter", "ssm:GetParameters"],
     "Resource": "arn:aws:ssm:ap-northeast-1:*:parameter/App/*"
   }
   ```
4. **Lambda Layer をビルド**（上述の 2 オプション必須）

   ```
   docker run --rm --entrypoint "" --platform linux/amd64 \
     public.ecr.aws/lambda/python:3.13 \
     pip install -r requirements.txt -t layer/python/lib/python3.13/site-packages/
   cd layer && zip -r ../App-layer.zip python/
   ```
5. **アプリコードを zip 化**して Lambda にアップロード

   ```
   zip App-app.zip lambda_function.py ssm_client.py news_fetcher.py \
       ai_ranker.py discord_notifier.py models.py config.py
   aws lambda update-function-code --function-name App-delivery \
       --zip-file fileb://App-app.zip --region ap-northeast-1
   ```
6. **Layer を Lambda 関数に紐付け**

   ```
   aws lambda update-function-configuration \
       --function-name App-delivery \
       --layers arn:aws:lambda:ap-northeast-1:xxxx:layer:App-dependencies:1
   ```
7. **EventBridge Scheduler** でスケジュール設定

   * Cron 式: `cron(0 21 * * ? *)` ＝ UTC 21:00 ＝ JST 翌 06:00

## おわりに

設計・実装・デプロイまで一通り作って気づいたことをまとめます。

* サーバーレス構成はスケジュール実行ユースケースに非常に相性がよく、EventBridge + Lambda で「毎朝 6 時に何かする」がほぼ設定だけで実現できます
* claude-haiku-4-5 は安価・高速で、大量の記事の中から重要なものを選ぶタスクに十分な精度を発揮しました。英語記事も日本語要約で届くのがかなり便利です
* モジュールを責務ごとに分割したことで、テストが書きやすく、後からソースを追加・変更するときも影響範囲が明確です

---
