---
id: "2026-05-31-amazon-bedrock-ナレッジベースで-line-世界旅行-bot-を作る-rag-対応版-01"
title: "Amazon Bedrock ナレッジベースで LINE 世界旅行 Bot を作る — RAG 対応版"
url: "https://qiita.com/shun8747/items/03542d68ea32922ef4db"
source: "qiita"
category: "construction"
tags: ["prompt-engineering", "API", "AI-agent", "Python", "construction", "qiita"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

# Amazon Bedrock ナレッジベースで LINE 世界旅行 Bot を作る — RAG 対応版

> **前提記事**: [Amazon Bedrock で LINE Chat Bot を構築する](https://qiita.com/shun8747/items/f7e84fc9cc20c530acb3)  
> **本記事で追加する機能**: Bedrock Knowledge Base（RAG）を組み込み、世界各国の旅行ガイドデータに基づいた回答を生成する旅行アシスタント Bot に拡張する

---

## 概要

前回の記事では、Amazon Bedrock と LINE を連携して汎用的なチャットボットを構築しました。今回はそこに **Bedrock Knowledge Base（ナレッジベース）** を追加し、S3 にアップロードした世界各国の旅行ガイドデータを基に回答を生成する **RAG（Retrieval-Augmented Generation）対応の世界旅行アシスタント Bot** に拡張します！

「バルセロナのおすすめ観光スポットは？」「3泊5日でイタリアを回るモデルコースを教えて」といった質問に、登録済みの旅行ガイドデータから回答してくれるボットを目指します。

### 拡張前後の構成比較

```
【前回（基本構成）】
LINE → API Gateway → Lambda → Bedrock (Claude) → 応答生成

【今回（ナレッジベース拡張版）】
LINE → API Gateway → Lambda → Bedrock Knowledge Base → 応答生成
                                      ↑
                               S3（旅行ガイドデータ）
                                      ↑
                               OpenSearch Serverless（ベクトルDB）
```

### アーキテクチャ図

![bedrock-kb-architecture.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3998881/450b8966-6cc3-417b-b1cf-528f585163cd.png)



---

## 手順の概要

1. S3 バケットの作成とドキュメントのアップロード
2. Bedrock ナレッジベースの作成
3. ナレッジベースの同期とテスト
4. Lambda の IAM ロール更新
5. Lambda コードの修正（RetrieveAndGenerate API 対応）
6. 動作確認

> **前提**: 前回の記事で構築した LINE Bot（Lambda + API Gateway + LINE Messaging API）が動作していること

---

## 1. S3 バケットの作成とドキュメントのアップロード

### ① S3 バケットを作成

- AWS マネジメントコンソール → S3 を開く
- 「バケットを作成」をクリック
  - バケット名: `bedrock-kb-documents-{your-account-id}`（グローバルで一意にする）
  - リージョン: `ap-northeast-1（東京）`
  - その他はデフォルトのまま
- 「バケットを作成」をクリック

![スクリーンショット 2026-05-31 12.16.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3998881/85d6069c-12bb-491c-ab84-9e9a94a6dcea.png)


ナレッジベースに読み込ませる旅行ガイドデータをアップロードします。

**対応フォーマット:**
- PDF（`.pdf`）
- Markdown（`.md`）
- テキスト（`.txt`）
- HTML（`.html`）
- Word（`.docx`）
- CSV（`.csv`）

**旅行ガイドデータの準備例（Markdown）:**

```markdown
# バルセロナ（スペイン）

## 基本情報
- ベストシーズン: 4月〜6月、9月〜10月
- 通貨: ユーロ（EUR）
- 言語: スペイン語・カタルーニャ語（英語観光地OK）
- 時差: 日本 -8時間

## おすすめ観光スポット
1. **サグラダ・ファミリア** — ガウディの未完成傑作。2026年現在も建設中。午前中が空いている
2. **グエル公園** — ガウディのモザイクベンチが有名。午後の散歩に最適
3. **ランブラス通り** — バルセロナのメインストリート。大道芸人やカフェが並ぶ

## モデルコース（3泊4日）
- Day 1: サグラダ・ファミリア → ゴシック地区散策
- Day 2: グエル公園 → カサ・バトリョ → モンジュイックの丘
- Day 3: ボケリア市場 → ランブラス通り → バルセロネータビーチ
- Day 4: モンセラット（郊外日帰り）

## グルメ
- **パエリア** — シーフードパエリア。ボケリア市場周辺がおすすめ
- **ピンチョス** — 小皿料理。バルで気軽に楽しめる
- **クレマカタラーナ** — カタルーニャ名物のクリームブリュレ

## 注意事項
- スリに注意（特にランブラス通り）
- チップは飲食店で約10%が目安
```

**S3 のフォルダ構成:**

```
bedrock-kb-documents-123456789012/
├── docs/
│   ├── europe/
│   │   ├── スペイン.md
│   │   ├── イタリア.md
│   │   ├── フランス.md
│   │   └── イギリス.md
│   ├── asia/
│   │   ├── タイ.md
│   │   ├── 台湾.md
│   │   └── 韓国.md
│   ├── americas/
│   │   ├── アメリカ.md
│   │   └── メキシコ.md
│   └── tips/
│       ├── 海外旅行の持ち物リスト.md
│       └── 空港・乗り継ぎテクニック.md
```

> **ポイント**: エリア別にフォルダを分けておくと、後からメタデータフィルタリングで「ヨーロッパだけ検索」なども可能になります。

![スクリーンショット 2026-05-31 12.18.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3998881/d36e46c7-0618-47a7-8869-fcfb97fde9d6.png)


---

## 2. Bedrock ナレッジベースの作成

### ① Bedrock コンソールでナレッジベースを作成

1. AWS マネジメントコンソール → **Amazon Bedrock** を開く
2. 左メニューから **「ナレッジベース」** を選択
3. **「ナレッジベースを作成」** をクリック

### ② 基本設定

| 項目 | 設定値 |
|------|--------|
| ナレッジベース名 | `travel-chatbot-kb` |
| 説明（任意） | LINE 世界旅行アシスタント用ナレッジベース |
| IAM ロール | 「新しいサービスロールを作成して使用」を選択 |

### ③ データソースの設定

| 項目 | 設定値 |
|------|--------|
| データソース名 | `s3-documents` |
| S3 URI | `s3://bedrock-kb-documents-{your-account-id}/docs/` |

### ④ 埋め込みモデルの選択

| 項目 | 設定値 |
|------|--------|
| 埋め込みモデル | **Titan Embeddings G1 - Text v1.2** |
| ベクトルデータベース | 「新しいベクトルストアをクイック作成」を選択 |

> **補足**: 「新しいベクトルストアをクイック作成」を選ぶと、OpenSearch Serverless のコレクションが自動で作成されます。手動設定は不要です。

### ⑤ チャンキング戦略の選択

| 戦略 | 説明 | おすすめ |
|------|------|---------|
| デフォルト | 300トークンごとに分割 | 初めての場合はこちら |
| 固定サイズ | 指定トークン数で分割 | ドキュメントの構造が均一な場合 |
| 階層的 | 親子チャンクを作成 | 長い文書で文脈を保持したい場合 |
| セマンティック | 意味的な区切りで分割 | 品質重視の場合 |
| なし | チャンキングしない | 既に前処理済みの場合 |

**おすすめ**: まずは **デフォルト** で始めて、回答品質を見ながら調整する。

### ⑥ 作成を完了

「ナレッジベースを作成」をクリック。作成完了まで数分かかります。

---

## 3. ナレッジベースの同期とテスト

### ① データソースを同期

1. 作成したナレッジベースの詳細ページを開く
2. データソースセクションで **「同期」** をクリック
3. ステータスが「利用可能」になるまで待つ（ドキュメント量に依存、通常数分）

![スクリーンショット 2026-05-31 12.30.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3998881/fbd33c50-21a7-48bc-bc7f-f0baa7968eb2.png)

### ② コンソールでテスト

1. ナレッジベース詳細ページの右側に **「テスト」** パネルがある
2. 「モデルを選択」で **Claude 4.5 Haiku** を選択
3. テスト質問を入力して動作確認

```
テスト質問例:
「バルセロナのおすすめ観光スポットは？」
「3泊5日でイタリアを回るプランを教えて」
「タイのおすすめグルメは？」
```

応答に旅行ガイドデータからの引用（ソース）が含まれていれば成功です。

### ③ ナレッジベース ID をメモ

ナレッジベース詳細ページの上部に表示される **ナレッジベース ID**（例: `XXXXXXXXXX`）を控えておきます。Lambda コードで使用します。

---

## 4. Lambda の IAM ロール更新

前回作成した Lambda 関数の実行ロールに、ナレッジベースへのアクセス権限を追加します。

### ① IAM コンソールで Lambda のロールを編集

1. IAM コンソール → ロール → `BedrockLineBot` のロールを選択
2. 「許可を追加」→「インラインポリシーを作成」

### ② ポリシー JSON

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:RetrieveAndGenerate",
                "bedrock:Retrieve",
                "bedrock:InvokeModel",
                "bedrock:GetInferenceProfile"
            ],
            "Resource": "*"
        }
    ]
}
```

ポリシー名: `BedrockKnowledgeBaseAccess`

> **注意**: 本番環境では `Resource` を特定の ARN に絞ることを推奨します。

---

## 5. Lambda コードの修正（RetrieveAndGenerate API 対応）

前回のコードを以下に置き換えます。

### 変更ポイント

| 項目 | 前回 | 今回 |
|------|------|------|
| API | `invoke_model` | `retrieve_and_generate` |
| クライアント | `bedrock-runtime` | `bedrock-agent-runtime` |
| 応答根拠 | なし（モデルの一般知識） | 旅行ガイドデータからの引用付き |
| プロンプト | なし | 旅行アシスタント用プロンプトテンプレート |

### Lambda コード（拡張版）

```python
import boto3
import json
import os
import urllib.request

# Bedrock Agent Runtime クライアント（東京リージョン）
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name="ap-northeast-1")

# 環境変数から取得（Lambda の設定 → 環境変数で設定）
LINE_ACCESS_TOKEN = os.environ["LINE_ACCESS_TOKEN"]
KNOWLEDGE_BASE_ID = os.environ["KNOWLEDGE_BASE_ID"]
MODEL_ARN = os.environ["MODEL_ARN"]

# プロンプトテンプレート（旅行アシスタントのキャラ設定）
PROMPT_TEMPLATE = """あなたは「たびナビ」という名前の親しみやすい世界旅行アシスタントです。
以下のルールに従って回答してください：

- 検索結果の旅行ガイド情報を基に、わかりやすく回答する
- 観光スポット・モデルコース・グルメ情報は箇条書きで見やすく整理する
- 旅行のコツや穴場情報があれば一言添える
- 日数が指定された場合は、その日数に合ったモデルコースを提案する
- ベストシーズンや注意事項（治安・チップ・マナー等）も併せて伝える
- 検索結果に該当する情報がない場合は、正直に「登録されているガイドにはありませんでした」と伝える
- 絵文字を適度に使って、旅行のワクワク感が伝わる雰囲気で回答する

$search_results$

ユーザーの質問: $query$
"""


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        events = body.get("events", [])

        if not events:
            return {"statusCode": 200, "body": "No events"}

        user_message = events[0]["message"]["text"]
        reply_token = events[0]["replyToken"]

        # Bedrock Knowledge Base に問い合わせ（RetrieveAndGenerate + プロンプトテンプレート）
        response = bedrock_agent.retrieve_and_generate(
            input={"text": user_message},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "modelArn": MODEL_ARN,
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": 5
                        }
                    },
                    "generationConfiguration": {
                        "promptTemplate": {
                            "textPromptTemplate": PROMPT_TEMPLATE
                        },
                        "inferenceConfig": {
                            "textInferenceConfig": {
                                "maxTokens": 500,
                                "temperature": 0.7
                            }
                        }
                    }
                }
            }
        )

        # 応答テキストを取得
        ai_reply = response["output"]["text"]

        # ソース情報を追加（任意）
        citations = response.get("citations", [])
        if citations:
            sources = set()
            for citation in citations:
                for ref in citation.get("retrievedReferences", []):
                    location = ref.get("location", {})
                    s3_uri = location.get("s3Location", {}).get("uri", "")
                    if s3_uri:
                        # ファイル名だけ取得
                        filename = s3_uri.split("/")[-1]
                        sources.add(filename)
            if sources:
                ai_reply += f"\n\n🌍 参照ガイド: {', '.join(sources)}"

        # LINE に返信
        send_line_message(reply_token, ai_reply)

        return {"statusCode": 200, "body": json.dumps({"message": "Success"})}

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


def send_line_message(reply_token, text):
    """LINE Messaging API で返信する"""
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    # LINE メッセージの上限は 5000 文字
    if len(text) > 4900:
        text = text[:4900] + "\n\n（文字数上限のため省略）"

    data = json.dumps({
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    })

    req = urllib.request.Request(url, data=data.encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req) as res:
        res.read()
```

### 環境変数の設定

Lambda コンソール → 設定 → 環境変数 で以下を追加:

| キー | 値 |
|------|-----|
| `LINE_ACCESS_TOKEN` | LINE Developers で取得したアクセストークン |
| `KNOWLEDGE_BASE_ID` | 手順3で控えたナレッジベース ID |
| `MODEL_ARN` | `arn:aws:bedrock:ap-northeast-1::inference-profile/jp.anthropic.claude-haiku-4-5-20251001-v1:0` |

> **改善ポイント（前回からの変更）**:
> - `requests` ライブラリを `urllib.request` に変更 → **Lambda レイヤー不要**に
> - アクセストークンをコードから環境変数に移動 → **セキュリティ向上**
> - ソース情報の付与 → ユーザーが根拠を確認できる
> - **プロンプトテンプレート追加** → Claude の回答スタイルを旅行アシスタントとしてカスタマイズ

### Lambda のタイムアウト設定

ナレッジベースの検索+生成は時間がかかるため、タイムアウトを延長します。

- Lambda コンソール → 設定 → 一般設定 → 編集
- タイムアウト: **30秒**（デフォルトの3秒では足りない）

---

## 6. 動作確認

### ① Lambda のテスト

Lambda コンソールのテスト機能で、以下のテストイベントを使用:

```json
{
  "body": "{\"events\":[{\"message\":{\"text\":\"バルセロナのおすすめ観光スポット教えて\"},\"replyToken\":\"test-token-123\"}]}"
}
```

> **注意**: `replyToken` がテスト値のため LINE への送信は失敗しますが、ナレッジベースからの応答取得を確認できます。CloudWatch Logs で応答内容を確認してください。

### ② LINE から実際にテスト

LINE アプリでボットに質問を送信:

![F39F85CD-3EA1-4055-8D93-484D2DAEEDD0.jpg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3998881/cef98e9e-abba-4cc1-83e8-c0780e3a8f18.jpeg)

---
