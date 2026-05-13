---
id: "2026-05-12-ここがすごいよclaude-platform-on-aws-01"
title: "ここがすごいよClaude Platform on AWS"
url: "https://qiita.com/moritalous/items/6ccba964655e83336f96"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "VSCode", "Python"]
date_published: "2026-05-12"
date_collected: "2026-05-13"
summary_by: "auto-rss"
query: ""
---

Claude Platform on AWSがGAしました。

すでに綺麗にまとまっている記事がありますので、詳細はそちらを参照ください。

https://qiita.com/nasuvitz/items/d0ad5d691790ff0eca71

https://dev.classmethod.jp/articles/claude-platform-on-aws-ga-setup/

とにかくやってみた！

:::note
Claude Platform on AWSの全貌は私も把握してないので、とりあえずのAPI呼び出しだけです。
:::

## ライブラリーをインストール

Claude Platform on AWSを呼び出すにはAnthropicのSDKを使うのが便利です。
オプションの`aws`もつけてインストールしましょう。

```shell
uv add anthropic[aws]
```

## すごポイント① Web Fetchができる！

WebFetchができます！

```python
import os

from anthropic import AnthropicAWS

client = AnthropicAWS(workspace_id=os.environ["ANTHROPIC_AWS_WORKSPACE_ID"])

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=[
        {"type": "web_fetch_20260209", "name": "web_fetch"},
    ],
    cache_control={"type": "ephemeral"},
    messages=[
        {
            "role": "user",
            "content": "このサイトの内容を要約して。https://aws.amazon.com/jp/blogs/machine-learning/introducing-claude-platform-on-aws-anthropics-native-platform-through-your-aws-account/",
        }
    ],
)

for content in response.content:
    print(content.type)

    if content.type == "text":
        print(content.text)
```

なぜかWebFetchが二回？

```text:実行結果
server_tool_use
server_tool_use
web_fetch_tool_result
code_execution_tool_result
server_tool_use
server_tool_use
web_fetch_tool_result
code_execution_tool_result
text
以下に、記事の内容を日本語で要約します。

---

## 📋 記事の要約：「Claude Platform on AWS」の一般提供開始

### 🔔 概要
2026年5月11日、AWSは **「Claude Platform on AWS」** の一般提供（GA）を発表しました。これは、**AWSアカウントを通じてAnthropicのClaudeプラットフォームにネイティブアクセスできる新サービス**で、AWSが世界初のクラウドプロバイダーとして提供します。

---

### ✅ 主な特徴

| 特徴 | 詳細 |
|---|---|
| **別途契約不要** | Anthropicとの個別の契約・認証情報・請求関係が不要 |
| **AWS IAM認証** | 既存のAWS IAM資格情報をそのまま利用可能 |
| **AWS Marketplaceで課金** | AI利用コストを他のAWSサービスと一元管理 |
| **CloudTrailで監査** | API呼び出しや利用状況をAWS CloudTrailで追跡・監査可能 |

---

### 🛠️ 利用可能な機能
- Messages API
- Claude Managed Agents（ベータ）
- Advisor Tool（ベータ）
- Web検索・Webフェッチ
- MCPコネクタ（ベータ）
- Agent Skills（ベータ）
- コード実行
- Files API（ベータ）

---

### 🚀 始め方（3ステップ）
1. **ワークスペースの作成** — プロジェクトやチームを分離しつつ、集中管理された請求・管理が可能
2. **認証設定** — IAM署名（SigV4）またはAPIキーで認証
3. **APIの呼び出し** — Anthropic SDK経由でAPIを即座に利用開始

---

### ⚠️ 注意点
- Claude Platform on AWSは**Anthropicが運用**しており、リクエストとデータは**AWSのセキュリティ境界の外**で処理されます
- 特定リージョンへのデータ所在要件がないチームに適しており、Amazon Bedrock上のClaudeモデルを**補完するサービス**として位置づけられています

---

### 🌏 対応リージョン
米国（バージニア、オハイオ、オレゴン）、カナダ、南米（サンパウロ）、欧州（各都市）、アジア太平洋（東京、ソウル、シドニー、メルボルンなど）と幅広く対応しています。

---

**要するに**、既存のAWSアカウントからAnthropicのClaudeを直接・フルスペックで利用できるようになり、認証・課金・監査をAWSに統合できる点が最大のメリットです。
```

## すごポイント② Web Searchができる！

フェッチだけじゃない！検索もできる！！

```python
import os

from anthropic import AnthropicAWS

client = AnthropicAWS(workspace_id=os.environ["ANTHROPIC_AWS_WORKSPACE_ID"])

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=[
        {"type": "web_search_20260209", "name": "web_search"},
    ],
    cache_control={"type": "ephemeral"},
    messages=[
        {"role": "user", "content": "Qiita.comでmoritalousさんの最近の投稿を調べて！"}
    ],
)

for content in response.content:
    print(content.type)

    if content.type == "text":
        print(content.text)
```

めっちゃ検索してくれる～～～

```text:実行結果
text
調べますね！少々お待ちください。
server_tool_use
server_tool_use
web_search_tool_result
code_execution_tool_result
server_tool_use
server_tool_use
web_search_tool_result
code_execution_tool_result
server_tool_use
server_tool_use
web_search_tool_result
server_tool_use
web_search_tool_result
server_tool_use
web_search_tool_result
server_tool_use
web_search_tool_result
server_tool_use
web_search_tool_result
code_execution_tool_result
text
moritalousさんの最近のQiita投稿をまとめました！最新順にご紹介します 🎉

---

## 📝 moritalous さんの最近のQiita投稿

### 1. 🆕 Strands AgentsのTypeScript版がv1.0.0に到達したのでAI SDK用のアダプターを作ってみた
**約1週間前** ｜ `#Vercel` `#TypeScript`

text
Strands AgentsのTypeScript版がv1.0.0になったことを記念し、以前からお世話になっているAI SDKと連携できるようにアダプターをバイブで作ってみた、という内容です。
text

🔗 https://qiita.com/moritalous/items/132f9e20661289f1abc9

---

### 2. 🆕 ハードウェアバディでClaudeとおともだち
**約1週間前（2026-05-05）** ｜ `#AWS` `#M5Stack` `#Bluetooth` `#Claude`

text
Claude Desktopにある「ハードウェアバディ」という機能を使い、Claude Desktopと物理デバイスを接続できるIoT機能を試した記事です。
text
 
text
手持ちのCore2 For AWS向けにバイブ（vibe）コーディングで対応させた内容が紹介されています。
text

🔗 https://qiita.com/moritalous/items/cd53aec76db1dec20862

---

### 3. 🆕 Claude CodeのVSCode拡張が使いやすいよ
**約2週間前（2026-04-25）** ｜ `#ClaudeCode` `#VSCode`

text
Claude CodeをCLIではなくVSCodeの拡張機能で利用する方法について紹介しています。
text
 
text
左右にパネルが出る構成になっており、右側が通常のチャット欄、左が過去のセッション一覧のような形になっているとのことです。
text

🔗 https://qiita.com/moritalous/items/3c5269610f26e23c5b04

---

### 4. Vercel Labsのportlessがおもしろい！
**2026-02-23** ｜ `#Next.js` `#Vercel`

text
portlessはリバースプロキシで、ポート番号を気にせず `.localhost` のURLで開発サーバーにアクセスできるツールです。複数のアプリを同時に起動してもドメイン名で区別するのでポート番号が衝突しません。
text

🔗 https://qiita.com/moritalous/items/60768540f832e67b01cc

---

### 5. AgentCore GatewayのターゲットにAgentCore RuntimeにデプロイしたMCPサーバーを指定する
**2026-02-11** ｜ `#AWS` `#MCP` `#AgentCore`

text
AgentCore GatewayとAgentCore RuntimeにデプロイしたMCPサーバーを連携させる手順について、ハマりやすいポイントを記録したメモ記事です。
text

🔗 https://q
```

## すごポイント③ ファイルのアップロード・ダウンロード、そしてコード実行ができる！

ファイルアップロード、ダウンロードも、コード実行も！
これは、例のステートフルAPI？？ちがうか。

:::note
ファイル操作はBeta扱いのようで、`client.beta`で始まるAPIを使用します。
:::

```python
import os

from anthropic import AnthropicAWS

client = AnthropicAWS(workspace_id=os.environ["ANTHROPIC_AWS_WORKSPACE_ID"])

# ファイルアップロード
file_object = client.beta.files.upload(
    file=open("data.csv", "rb"),
)

response = client.beta.messages.create(
    model="claude-sonnet-4-6",
    betas=["files-api-2025-04-14"],
    max_tokens=4096,
    tools=[
        {"type": "code_execution_20260120", "name": "code_execution"},
    ],
    cache_control={"type": "ephemeral"},
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "CSVデータを分析して、matplotlibで可視化。output.pngで保存して。",
                },
                {"type": "container_upload", "file_id": file_object.id},
            ],
        }
    ],
)


# レスポンスからファイルIDを取得
def extract_file_ids(response):
    file_ids = []
    for item in response.content:
        if item.type == "bash_code_execution_tool_result":
            content_item = item.content
            if content_item.type == "bash_code_execution_result":
                # concrete-typed list: List[BashCodeExecutionOutputBlock]
                for file in content_item.content:
                    file_ids.append(file.file_id)
    return file_ids


# ファイルを保存
for file_id in extract_file_ids(response):
    file_metadata = client.beta.files.retrieve_metadata(file_id)
    file_content = client.beta.files.download(file_id)
    file_content.write_to_file(file_metadata.filename)
    print(f"Downloaded: {file_metadata.filename}")


for content in response.content:
    print(content.type)

    if content.type == "text":
        print(content.text)
```

```text:出力
Downloaded: output.png
text
まず、アップロードされたCSVファイルの内容を確認します。
server_tool_use
bash_code_execution_tool_result
text
データの内容を把握できました。次に、分析・可視化スクリプトを作成します。
server_tool_use
text_editor_code_execution_tool_result
server_tool_use
bash_code_execution_tool_result
text
`output.png` を出力しました！ダッシュボードの構成は以下の通りです。

---

## 📊 ダッシュボード構成（8チャート）

| # | チャート | 内容 |
|---|---------|------|
| **①** | **月次売上 積み上げ面グラフ** | Hardware / Service / Software 別の月次売上推移と合計トレンド |
| **②** | **売上ヒートマップ** | 地域 × カテゴリのクロス集計（色と数値で一目把握） |
| **③** | **セグメント別売上 ＋ 粗利率** | Consumer / Enterprise / SMB の売上棒グラフ＋粗利率折れ線の複合グラフ |
| **④** | **販売チャネル別 受注件数** | Online / Direct / Partner / Retail / SMB の水平バー |
| **⑤** | **地域別 月次売上推移** | 6都市（東京・大阪・名古屋・福岡・札幌）の折れ線グラフ |
| **⑥** | **返品率 ドーナツ円グラフ** | セグメント別の返品率分布 |
| **⑦** | **顧客評価スコア分布** | ヒストグラム＋平均値ラインで評価傾向を可視化 |
| **⑧** | **マーケ費用 vs 売上 散布図** | カテゴリ別の費用対効果を回帰トレンドライン付きで表示 |
```

ファイルもできました

![output.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/41574/5013eb9f-fcaf-4542-af43-e95f0b44d716.png)


## すごポイント④ 自動プロンプトキャッシュ！！

これが個人的に熱望してたやつです。多分本日時点でBedrockではできません。

トップレベルに書くだけ！だけ！

```python
import os

from anthropic import AnthropicAWS

client = AnthropicAWS(workspace_id=os.environ["ANTHROPIC_AWS_WORKSPACE_ID"])

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    cache_control={"type": "ephemeral"}, # これ！！！
    messages=[
        {"role": "user", "content": "HELLO!!!"}
    ],
)

print(response.content[0].text)
```

ちなみにですが、プロンプトキャッシュは何度かバージョンアップをしてまして、

- 初代：キャッシュしたいところにキャッシュポイントを書く。匠の技術でいい感じの場所に書く
- ２代目：メッセージの最後にキャッシュポイントを書く。常に最後だけでいいが、これはこれでめんどくさい
- ３代目：トップレベルに書くだけ！だけ！最高！

---

Bedrockにも来ないかなぁ
