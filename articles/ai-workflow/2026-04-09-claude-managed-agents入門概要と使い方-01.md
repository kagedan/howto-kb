---
id: "2026-04-09-claude-managed-agents入門概要と使い方-01"
title: "Claude Managed Agents入門【概要と使い方】"
url: "https://zenn.dev/galirage/articles/claude-managed-agents-quickstart"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

はじめまして、ますみです！

[株式会社Galirage（ガリレージ）](https://galirage.com/)というAIスタートアップで、代表をしております^^

その他にも、「[AIとコミュニケーションする技術（インプレス出版）](https://amzn.to/3ME8mLF)」という書籍を執筆させていただいたり、[生成AIアカデミー](https://www.youtube.com/@masumi_engineer)というチャンネルを運営したり、上智大学で非常勤講師をしたりしています！

[![自己紹介.png](https://res.cloudinary.com/zenn/image/fetch/s--9tzCxv3U--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://storage.googleapis.com/zenn-contents/images/intro/introduction_banner.png?_a=BACAGSGT)](https://bit.ly/banner_intro_masumi_creator_zenn)

## AIエージェントをクラウドで動かす時代へ

2026年4月、Anthropicが新機能 **「Claude Managed Agents」** を発表しました。

これは、クラウド上でAIエージェントを構築・運用するためのAPIスイートです。  
サンドボックス環境でコード実行やWeb検索、MCP（Model Context Protocol）連携が可能になります。

本記事では、Claude Managed Agentsの概要を解説した上で、実際にハンズオンで触ってみます。

具体的には、**「Notionのドキュメントを検索して、Slackに回答を投稿するAIエージェント」** を構築します。

## Claude Managed Agentsとは

**Claude Managed Agents** は、Anthropicが提供するクラウドホスト型のエージェント基盤です。

公式の説明を引用します。

> Introducing Claude Managed Agents: a suite of composable APIs for building and deploying cloud-hosted agents at scale. It pairs an agent harness tuned for performance with production infrastructure, so you can go from prototype to launch in days.

つまり、エージェントの「頭脳（推論）」と「実行環境（サンドボックス）」がセットで提供されるサービスです。

### 従来のClaude APIとの違い

| 比較項目 | Claude API（Messages API） | Claude Managed Agents |
| --- | --- | --- |
| 実行形態 | 1回のリクエスト・レスポンス | 長時間実行のセッション |
| ツール実行 | 自前で実装が必要 | サンドボックスで自動実行 |
| インフラ | 自前で構築 | Anthropicが管理 |
| MCP連携 | 自前で構築 | 組み込みでサポート |
| 用途 | カスタムな制御が必要な場合 | 長時間タスクや非同期処理 |

一言でまとめると、Claude APIが「素のモデル呼び出し」なのに対し、Managed Agentsは **「エージェントの実行基盤まるごと」** を提供するサービスです。

### 5つの構成要素

Claude Managed Agentsは、以下の5つの要素で構成されています。

| 構成要素 | 説明 |
| --- | --- |
| **Agent** | モデル・システムプロンプト・ツール・MCPサーバーの定義 |
| **Environment** | エージェントが動作するクラウドコンテナの設定 |
| **Session** | エージェントの実行インスタンス（イベントログを保持） |
| **Vault** | OAuthトークンなどの認証情報を安全に保管する仕組み |
| **MCP** | 外部ツール（Notion、Slackなど）との接続プロトコル |

### アーキテクチャの特徴

Managed Agentsのアーキテクチャには、興味深い設計思想があります。

Anthropicの公式エンジニアリングブログによると、システムは3つの仮想化レイヤーに分離されています。

1. **Session（セッション）**: すべてのエージェント活動を記録する追記専用ログ
2. **Harness（ハーネス）**: Claudeを呼び出し、ツール実行をルーティングするステートレスなループ
3. **Sandbox（サンドボックス）**: コードやファイル操作の実行環境

この分離により、各コンポーネントが独立して障害回復できます。  
たとえば、ハーネスがクラッシュしても、新しいハーネスがセッションIDからイベントログを取得して再開できます。

## 実際に触ってみた：Notion→Slackサポートエージェントの構築

ここからは、実際にManaged Agentsを使ってエージェントを構築していきます。

### 今回作るもの

今回構築するのは、以下のようなエージェントです。

1. ユーザーが質問を送信する
2. エージェントがNotionのドキュメントを検索する（[RAG：Retrieval-Augmented Generation](https://zenn.dev/umi_mori/books/llm-rag-langchain-python/viewer/what-is-rag)）
3. 検索結果をもとに回答を生成する
4. 指定したSlackチャンネルに回答を投稿する

では、さっそく構築していきましょう。

### Step1：Claude Consoleにログイン・Quickstartにアクセス

まず、Claude Console（`platform.claude.com`）にログインします。

左サイドバーの **「Managed Agents」** 配下にある **「Quickstart」** をクリックします。

![Claude ConsoleのQuickstart画面。左サイドバーのManaged Agents配下にあるQuickstartを選択し、右側にBrowse templatesとしてSupport agentなどのテンプレート一覧が表示されている](https://static.zenn.studio/user-upload/deployed-images/dcfab552d993b70c484a5996.png?sha=e5d4fae72e310792b4ee74ac9e1c613199aa6c2a)

画面右側に「Browse templates」としてテンプレート一覧が表示されます。  
今回は **「Support agent」** を選択します。

これは、顧客の質問に回答し、必要に応じてエスカレーションを行うエージェントのテンプレートです。

他にも、Deep researcher・Structured extractor・Data analystなど、さまざまなテンプレートが用意されています。

### Step2：Support agentテンプレートを選択

テンプレートを選択すると、YAML形式のエージェント設定が表示されます。

![Support agentテンプレートのYAML設定画面。model: claude-sonnet-4-6、MCPサーバーとしてNotionとSlackが設定されている。右上に「Use this template」ボタンがある](https://static.zenn.studio/user-upload/deployed-images/95f48df1bd4fbd36be84fce7.png?sha=800fb1e8e20de0c3c13388427564a0cb03115037)

設定内容の主なポイントは以下の通りです。

* モデル：`claude-sonnet-4-6`
* MCPサーバー：Notion（`mcp.notion.com`）とSlack（`mcp.slack.com`）
* システムプロンプト：「Notionのドキュメントを検索して回答する」「80%以上の確信がない場合はエスカレーションする」などのルール

右上の **「Use this template」** をクリックして進みます。

### Step3：エージェントを作成する

テンプレートを使用すると、エージェントが自動的に作成されます。

![エージェント作成完了画面。「Agent created」のチェックマークが表示され、POST /v1/agentsのcURLコマンドも確認できる。左下に「Next: Configure environment →」ボタンがある](https://static.zenn.studio/user-upload/deployed-images/74b55499d0f4aaf12787fe6d.png?sha=c9546c5ee46a834b62cf43577a65e9645f6a35cd)

「Agent created」のチェックマークが表示されれば成功です。  
画面には `POST /v1/agents` のcURLコマンドも表示されており、コードでの実装方法も確認できます。

左下の **「Next: Configure environment →」** をクリックして、環境設定に進みます。

### Step4：環境（Environment）を設定する

環境設定では、Claudeから対話形式で質問が表示されます。

![環境設定のネットワーク制限に関する質問画面。「Limited（Notion + Slack MCP only）」「Unrestricted」「Something else」の3つの選択肢が表示されている](https://static.zenn.studio/user-upload/deployed-images/283980a7a71c9ae1a3f02223.png?sha=ea8847c35153e1dfd9b43f73373e1c328122d759)

「このエージェントのネットワークアクセスを、NotionとSlackのMCPサーバーに限定しますか？」と聞かれます。

セキュリティの観点から **「Limited（Notion + Slack MCP only）」** を選択しました。  
これにより、エージェントが接続できるネットワークを最小限に絞ることができます。

![環境作成完了画面。「Environment is ready — limited to Notion and Slack MCP traffic only.」というメッセージと、POST /v1/environmentsのcURLコマンドが表示されている](https://static.zenn.studio/user-upload/deployed-images/e4073f69cbd153c0205cd292.png?sha=bff05e90391bfb5fa7956611b303dffb3a00178e)

環境が作成されると、「Environment is ready」というメッセージが表示されます。  
**「Next: Start session →」** をクリックして次に進みます。

### Step5：Slackチャンネルを指定する

セッション開始前に、Claudeから2つの質問が表示されます。

**1つ目**：顧客への回答を投稿するSlackチャンネル

![Slackチャンネル指定画面（1/2）。「Which Slack channel should the agent post customer replies to?」という質問に対し、フリー入力欄に「#galirage_qaサポートセンター」と入力している](https://static.zenn.studio/user-upload/deployed-images/3a8882d8dd9865aee79f60ff.png?sha=86422f0e82b535e9660668b0b93d3013f7f1357a)

選択肢が提示されますが、フリー入力欄に任意のチャンネル名を指定できます。  
今回は **「#galirage\_qaサポートセンター」** と入力しました。

**2つ目**：内部エスカレーション用のSlackチャンネル

![Slackチャンネル指定画面（2/2）。内部エスカレーション用チャンネルとして「galirage_qaサポートセンター_管理者のチャンネル」と入力している](https://static.zenn.studio/user-upload/deployed-images/568af4849092568c77f4f14b.png?sha=464afa623b20b16a74448c6aeef692ea57b09f7d)

エージェントが80%の確信を持てない場合に、この内部チャンネルへエスカレーションされます。  
**「galirage\_qaサポートセンター\_管理者のチャンネル」** を指定しました。

### Step6：Notion・SlackのMCP認証を行う

チャンネル設定が完了すると、Vault（認証情報保管庫）が自動作成されます。  
続いて、NotionとSlackそれぞれのOAuth認証を行います。

**Notionの認証**

![Notion MCP認証画面。「Authorization required to use this MCP」と表示され、セキュリティの注意書きへのチェックボックスと「Connect」ボタンが表示されている](https://static.zenn.studio/user-upload/deployed-images/148cb368670748efb376dbf6.png?sha=25d7fc6c510f1e6f062bb46e8471b62f9db0f68f)

「Authorization required to use this MCP」という画面が表示されます。  
セキュリティに関する注意書きを確認し、チェックを入れてから **「Connect」** で接続を開始しましょう。

![NotionのOAuth認証画面。Notion MCPへの接続を許可する画面で、Galirage Inc.ワークスペースへのアクセス権限の詳細と「続行」ボタンが表示されている](https://static.zenn.studio/user-upload/deployed-images/06cfdf7031271a017e44966f.png?sha=fa3055f3fc4bb09a61d963442b7af0f6decab193)

別ウィンドウでNotionのOAuth認証画面が開きます。  
接続先のワークスペースと付与される権限を確認した上で、**「続行」** をクリックすれば認証完了です。

**Slackの認証**

![Slack MCP認証画面。Notion認証完了後に続けてSlackの認証を求められている。「Connect」ボタンが表示されている](https://static.zenn.studio/user-upload/deployed-images/8c476a4cc76954046c4505c9.png?sha=490b708379f349d3a2d493a11579e2d44142e159)

Notionの認証が完了したら、続けてSlackの認証に進みます。  
同様にセキュリティの注意書きを確認し、**「Connect」** で接続を開始しましょう。

![SlackのOAuth認証画面。「Claude」アプリにGalirage Inc.ワークスペースへのアクセスを許可する画面。コンテンツへのアクセスやアクションの実行などの権限一覧と「許可する」ボタンが表示されている](https://static.zenn.studio/user-upload/deployed-images/e64b6ca5b7fd1ed46ca9c769.png?sha=511d4600e64004331bccf0d192ca695d61c7834c)

SlackのOAuth認証画面では、「Claude」アプリに付与される権限の一覧が表示されます。  
コンテンツへのアクセスやアクションの実行権限を確認の上、**「許可する」** をクリックして認証を完了させましょう。

### Step7：テスト実行

NotionとSlackの両方の認証が完了すると、テスト準備が整います。

![テスト準備完了画面。「Both credentials are in place. The agent is ready to test」というメッセージと「Test run」ボタンが表示されている](https://static.zenn.studio/user-upload/deployed-images/0f4fd9e6d4ac83a77ec6bb96.png?sha=c197680776de8e519513286aed48b2ad97e595b7)

「Both credentials are in place. The agent is ready to test」というメッセージが表示されます。  
**「Test run」** ボタンをクリックしてテストを開始します。

![セッション作成後のPreview画面。右側のDebugタブに「No events yet」と表示されており、入力欄に「Galirageのビジョンは？」と入力している状態](https://static.zenn.studio/user-upload/deployed-images/91552f0bfaaba204f17f92fa.png?sha=35cec03ef9205014ab8c56c928c5a6e4ecb59fed)

セッションが作成され、Previewパネルが表示されます。  
入力欄に **「Galirageのビジョンは？」** と入力し、「Send」をクリックします。

## 動作確認

### エージェントの処理の流れ（RAG）

質問を送信すると、右側のDebugパネルにリアルタイムでイベントログが流れ始めます。

![Debugパネルのイベントログ。質問送信後のRAG処理がリアルタイムで表示されている。Notion-searchやNotion-fetchのツール呼び出し、認証エラーの発生と自律的なリトライの様子が確認できる](https://static.zenn.studio/user-upload/deployed-images/5c5f3832be9b36026544d6d5.png?sha=870c4352b4f6f7eb3d7948b2e2e739a812366abd)  
*Debugパネルには、Notion-search → Notion-fetch（認証エラー）→ Notion-search（再検索）→ Notion-fetch（成功）→ Slack投稿という一連のRAG処理がリアルタイムで表示される*

処理の流れは以下の通りです。

1. **User** → 「Galirageのビジョンは？」
2. **Thinking** → エージェントが考え始める
3. **Tool（Notion-search）** → クエリ「Galirageのビジョン」で検索
4. **Tool（Notion-fetch）** → 認証エラーが発生（後述）
5. **Tool（Notion-search）** → クエリを変えて再検索「Galirage vision ミッション 理念」
6. **Tool（Notion-fetch）** → ページ内容を取得（成功）
7. **Tool（Slack Search Channels）** → 投稿先チャンネルを検索
8. **Tool（Slack Send Message）** → 回答を投稿

注目すべきは、途中でNotion-fetchの認証エラーが発生しても、エージェントが **自律的に検索クエリを変えてリトライしている** 点です。  
このような耐障害性は、実運用において非常に心強い特徴だと感じました。

### Slackチャンネルへの回答投稿

指定したSlackチャンネルに、エージェントからの回答が投稿されました。

![Slack「#galirage_qaサポートセンター」チャンネルに投稿された回答。森重 真純（Masumi Morishige）のアカウント名義でGalirageのビジョンが回答されている。Notionの出典ページへのリンクも付記されている](https://static.zenn.studio/user-upload/deployed-images/b30cf182b5f6befe9312b1ba.png?sha=430b6e21b08c513530f4251be10f1242ed88f217)  
*投稿者名がBotではなく、OAuth認証に使用した自分のアカウント名義（森重 真純 / Masumi Morishige）になっている点に注目。メッセージ末尾に「使用して送信されました @Claude」と表示される*

投稿内容を確認すると、Notionのドキュメントから正確にビジョンを引用し、出典ページへのリンクも付記されています。

!

**重要な仕様：Slack投稿はユーザーアカウント名義になる**

ここで気づいた重要な点があります。  
Slackへの投稿は、OAuth認証に使用したユーザーアカウント（筆者の場合は「森重 真純 / Masumi Morishige」）の名義で行われます。

Botアカウントではなく **自分のアカウントとして投稿される** という独特な仕様です。  
メッセージ末尾に「使用して送信されました @Claude」と表示されますが、投稿者名は自分のアカウント名になります。

運用時には、専用のサービスアカウントで認証することを検討した方が良いかもしれません。

### セッションのトレース確認

Previewパネル右上の **「View session」** をクリックすると、セッションの詳細トレース画面に遷移します。

![Quickstart画面のPreviewパネル（Debugタブ）。イベントログが表示されており、右上の「View session」ボタンからセッション詳細画面へ遷移できる](https://static.zenn.studio/user-upload/deployed-images/723b83607edb6f78ef5dd369.png?sha=5e97f2a837a80bc59840bb1df6e3a0805b52ea1c)  
*Previewパネル右上の「View session」ボタンをクリックすると、より詳細なセッショントレース画面に遷移できる*

以下が、セッションの詳細トレース画面です。

![Sessions詳細画面。左側にTranscript（処理ステップの時系列表示）、右側に選択したステップの詳細（Agentの回答内容）が表示されている。各ステップの実行時間・トークン数も確認できる](https://static.zenn.studio/user-upload/deployed-images/872399ce72cff4194be42f55.png?sha=d9fd2df03582f77ea9ce81da1da8197b9f4e5acb)  
*Sessions画面のTranscriptでは、Notion-search（13.1s）→ Notion-fetch（エラー）→ Notion-search（再試行 14.8s）→ Slack投稿という各ステップの実行時間とトークン消費量が一覧で確認できる*

Sessions画面では、以下の情報を確認できます。

* セッションID・使用エージェント・環境・処理時間・トークン数
* 各ステップの実行時間とトークン消費量
* ツール呼び出しの詳細（入力パラメータ・出力結果）

左側のTranscript（トランスクリプト）に処理ステップが時系列で表示されます。  
各ステップをクリックすると、右側パネルに詳細が表示されます。

全体の処理時間は約1分50秒でした。  
Notion検索→Slack投稿までの一連の流れがトレースできるのは、デバッグや運用監視に非常に役立ちます。

### Ask Claudeでデバッグ分析

Sessions画面の右上にある **「Ask Claude」** ボタンをクリックすると、セッションに関する質問ができるサイドパネルが表示されます。

![Sessions画面で「Ask Claude」ボタンをクリックした状態。右側にサイドパネルが開き、「Identify errors」「Analyze performance」「Trace conversation flow」「Suggest improvements」の4つのクイック質問オプションが表示されている](https://static.zenn.studio/user-upload/deployed-images/33b6e42eb9162dfbbfbffc6c.png?sha=6cadb4ed3d2a2ccb9666063e821f9327e291d17f)

以下のクイック質問オプションが用意されています。

| オプション | 内容 |
| --- | --- |
| **Identify errors** | セッション中のエラー・例外を特定 |
| **Analyze performance** | ツール実行時間・ボトルネックを分析 |
| **Trace conversation flow** | 会話ロジックと意思決定ポイントを追跡 |
| **Suggest improvements** | プロンプト・ツール使用の改善提案 |

今回は **「Identify errors」** を選択して、先ほどのNotion-fetchエラーを分析してみました。

![Ask Claudeによるエラー分析結果。「Notion MCP Auth Failure（Critical）」として、OAuthトークンの期限切れが原因であること、Vaultの自動リフレッシュが約25秒後に作動した可能性が高いことが報告されている](https://static.zenn.studio/user-upload/deployed-images/20110fe74dc48d97bf5c2029.png?sha=201931d5ae6a5108423fe2fdab373a9d7dab5881)  
*Ask Claudeは、エラーの内容・影響範囲・根本原因の推定・修正案までを構造化して報告してくれる。従来のログ解析を大幅に効率化できる*

Ask Claudeの分析結果として、以下が報告されました。

* **エラー内容**：Notion MCP Auth Failure（Critical）
* **原因**：OAuthトークンの期限切れ（断続的）
* **影響**：初回のNotion-fetchが失敗し、約15秒のロスが発生
* **根本原因の推定**：セッション開始時にアクセストークンがちょうど期限切れの境界にあり、Vaultの自動リフレッシュが約25秒後に作動した可能性

このように、エラーの原因分析から改善提案まで、Claude自身がセッションのトレースを読み解いてくれます。  
従来であればログを目視で追う必要があった作業が、大幅に効率化されると感じました。

## 発展：Slackからトリガーして自動応答させるには？

ここまでの構成では、Claude Console上から手動で質問を送信していました。  
では、**Slack上で質問を投稿したら、エージェントが自動で回答する** ことはできるのでしょうか。

Ask Claudeに聞いてみました。

![Ask Claudeへの質問結果。Slackからの自動トリガーはManaged Agents単体では実現できないが、バックエンドサーバーとSlack Event APIを組み合わせれば可能という回答。必要なコンポーネントの表と最小実装イメージ（Python）も表示されている](https://static.zenn.studio/user-upload/deployed-images/1c39aad716e67ac80ab9f2ca.png?sha=91260592197246ed5a52ebaddf0c17ca1fa6cada)  
*現時点のManaged Agentsはプル型アーキテクチャのため、Slackからの自動トリガーには別途バックエンドサーバーが必要。ただし、必要なコンポーネントと最小実装コードも提示してくれる*

結論として、**現時点のManaged Agents単体では直接は実現できません。**

理由は、Managed Agentsが **プル型** のアーキテクチャだからです。  
ユーザーがセッションにメッセージを送る形式であり、Slackメッセージを自動トリガーにする機能は標準では提供されていません。

ただし、バックエンドサーバーを組み合わせれば実現可能です。

### 必要な構成

| コンポーネント | 役割 |
| --- | --- |
| **Slack App（Event Subscriptions）** | チャンネルへの新規メッセージを検知 |
| **バックエンドサーバー** | Slackイベントを受信 → セッションに `user.message` を送信 |
| **Managed Agentsセッション** | 既存の設定そのまま（Notion検索 + Slack投稿） |

### 処理フロー

```
Slack（質問投稿）
  ↓ Slack Event API / Webhook
バックエンドサーバー（メッセージを抽出）
  ↓ Managed Agents セッションに user.message として送信
エージェント（Notion検索 → 回答生成 → Slack MCP で投稿）
  ↓
Slack（回答が投稿される）
```

### 最小実装イメージ（Python）

まず、必要なパッケージをインストールします。

```
pip install flask anthropic
```

```
import anthropic
from flask import Flask, request

app = Flask(__name__)
client = anthropic.Anthropic()

# 実運用では、セッションIDを動的に管理する必要があります。
# 例：チャンネルごとにセッションを作成し、DBやキャッシュで管理する
SESSION_ID = "YOUR_SESSION_ID"

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json

    # Slack Event APIのURL検証
    if data.get("type") == "url_verification":
        return {"challenge": data["challenge"]}

    # メッセージイベントの処理
    event = data.get("event", {})
    if event.get("type") == "message" and not event.get("bot_id"):
        question = event["text"]

        # Managed Agentsセッションにメッセージを送信
        client.beta.sessions.send_event(
            session_id=SESSION_ID,
            event={
                "type": "user.message",
                "content": question
            }
        )

    return {"ok": True}
```

## まとめ

本記事では、Claude Managed Agentsの概要と、実際にNotionナレッジベース×Slack回答エージェントを構築する手順を紹介しました。

### 良かった点

* ウィザード形式の対話型セットアップで、コードを書かずにエージェントを構築できる
* セッションのトレース機能が充実しており、デバッグが容易
* Ask Claude機能でエラーの原因分析・改善提案をすぐに得られる
* エージェントが自律的にエラーをリカバリーする耐障害性がある

### 注意点

* Slack投稿がOAuth認証したユーザーアカウント名義になる（Bot名義ではない）
* Slackからの自動トリガーには、別途バックエンドサーバーの実装が必要
* OAuthトークンの期限切れが発生しうる（Vaultの自動リフレッシュに依存）
* 2026年4月時点でベータ版のため、仕様変更の可能性がある

### 今後の展望

Managed Agentsは、AIエージェントの構築・運用の敷居を大きく下げるサービスだと感じました。  
特に、MCPを通じた外部ツール連携が標準でサポートされているため、Notion・Slack以外にも、GitHub・Jira・Google Driveなど、さまざまなSaaSとの連携が期待できます。

今後、Slackトリガーのようなプッシュ型の機能が標準サポートされれば、さらに活用の幅が広がるでしょう。

## 最後に

最後まで読んでくださり、ありがとうございました！  
この記事を通して、少しでもあなたの学びに役立てば幸いです！

宣伝：もしもよかったらご覧ください^^

**『[AIとコミュニケーションする技術（インプレス出版）](https://amzn.to/3ME8mLF)』という書籍を出版しました🎉**

これからの未来において「変わらない知識」を見極めて、生成AIの業界において、読まれ続ける「バイブル」となる本をまとめ上げました。

かなり自信のある一冊なため、もしもよろしければ、ご一読いただけますと幸いです^^

## 参考文献

<https://platform.claude.com/docs/en/managed-agents/overview>

<https://www.anthropic.com/engineering/managed-agents>
