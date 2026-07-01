---
id: "2026-06-30-mistral-connectors入門-mcpでgithubgmailをaiエージェントに接続する-01"
title: "Mistral Connectors入門 — MCPでGitHub・GmailをAIエージェントに接続する"
url: "https://zenn.dev/kai_kou/articles/240-mistral-connectors-mcp-studio-agent-guide"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "OpenAI", "Python", "zenn"]
date_published: "2026-06-30"
date_collected: "2026-07-02"
summary_by: "auto-rss"
query: ""
---

<!-- IMAGE\_SLOT: hero  
description: "Mistral Connectors overview showing connections between AI agents and enterprise tools like GitHub, Gmail, Web Search with MCP protocol in the middle"  
aspect: "16:9"  
-->

## はじめに

2026年4月15日、Mistral AIは「Connectors」機能をパブリックプレビューとして公開しました。Connectorsは、MCPプロトコル（Model Context Protocol）を使ってAIエージェントと企業データ・外部サービスを接続する仕組みです。

GitHub、Gmail、ウェブ検索などの組み込みコネクターが用意されており、独自のMCPサーバーをカスタムコネクターとして登録することもできます。本記事では、Mistral ConnectorsのAPI・SDKを使った実装方法を解説します。

### この記事で学べること

* Mistral ConnectorsとMCPの関係
* 組み込みコネクターの種類と使い方
* Python SDKを使ったエージェントの作成と会話
* カスタムMCPコネクターの登録・利用

### 対象読者

* Mistral APIを使ってエージェントを構築したいエンジニア
* MCPを活用したエンタープライズAI統合に興味がある方

### 前提条件

* Python 3.9以上
* Mistral APIキー（[Mistral Console](https://console.mistral.ai/)から取得）
* `mistralai` Python SDKのインストール

## TL;DR

* Mistral ConnectorsはMCPプロトコルでAIエージェントと外部ツールを接続する
* GitHub・Gmail・Web Search・Code Executionなど複数の組み込みコネクターがある
* カスタムMCPコネクターをAPIで登録・管理できる
* `client.beta.conversations.start()` でコネクター付きエージェントと会話できる
* Mistral Studio（console.mistral.ai）でGUI管理も可能

<!-- IMAGE\_SLOT: architecture  
description: "Architecture diagram showing Mistral Connectors system: Agent at center, connected via MCP protocol to GitHub, Gmail, Web Search, Code Execution, Image Generation, Document Library nodes. Clean flat design on white background."  
aspect: "16:9"  
-->

## Mistral Connectorsとは

Mistral Connectorsは、AIエージェントと外部サービス・データソースを繋ぐ統合レイヤーです。MCPプロトコルを採用することで、バラバラな統合ロジックを1つの標準に集約します。

### MCPとConnectorsの関係

MCPはAIシステムと外部ツール・データを繋ぐオープン標準規格です。ConnectorsはこのMCPをベースに構築されており、各コネクターが「パッケージ化された統合エンティティ」として機能します。

登録したコネクターは以下から利用できます。

| 利用方法 | 詳細 |
| --- | --- |
| Conversation API | 会話スレッド内でコネクターをツールとして呼び出し |
| Completions API | チャット補完と組み合わせて利用 |
| Agent SDK | エージェント定義にコネクターを組み込み |
| Le Chat / Mistral AI Studio | GUIベースで直接利用 |

### 利用可能な組み込みコネクター

Mistral Connectorsには以下の組み込みコネクターが用意されています（ウェブ検索はベーシックとプレミアムの2バリアント）。

| コネクター | 用途 |
| --- | --- |
| `web_search` | ウェブ検索で最新情報を取得（ベーシック） |
| `web_search_premium` | ニュース記事等の強化版ウェブ検索 |
| Code Execution | Pythonコードを安全なサンドボックス環境で実行 |
| Image Generation | FLUX1.1 [pro] Ultraによる画像生成 |
| Document Library | クラウドドキュメントを対象としたRAG（ベータ） |
| GitHub | リポジトリコンテンツへのアクセス・分析 |
| Gmail | メールの読み取り・検索 |

## 組み込みコネクターの使い方

### Web Searchエージェントの作成

```
import os
from mistralai import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# ウェブ検索コネクター付きエージェントを作成
websearch_agent = client.beta.agents.create(
    model="mistral-medium-latest",
    description="Webから最新情報を検索するエージェント",
    name="Web Search Agent",
    instructions="web_searchを使って最新情報を検索し、引用元URLを明示してください",
    tools=[{"type": "web_search"}],
    completion_args={
        "temperature": 0.3,
        "top_p": 0.95,
    }
)

# エージェントと会話を開始
response = client.beta.conversations.start(
    agent_id=websearch_agent.id,
    inputs="2026年4月の主要AIモデルリリースをまとめてください",
)

print(response.outputs[-1].content[0].text)
```

`web_search_premium` を使うと、ニュースメディアのコンテンツにも優先的にアクセスできます。

```
tools=[{"type": "web_search_premium"}]
```

### Code Executionエージェントの作成

Pythonコードをサンドボックス環境で実行するエージェントを作成できます。数値計算、データ分析、グラフ描画などに活用できます。

```
code_agent = client.beta.agents.create(
    model="mistral-medium-latest",
    description="Pythonコードを安全に実行するエージェント",
    name="Code Execution Agent",
    instructions="ユーザーの要求に応じてPythonコードを書いて実行してください",
    tools=[{"type": "code_interpreter"}],
)

response = client.beta.conversations.start(
    agent_id=code_agent.id,
    inputs="フィボナッチ数列の最初の20項を計算して、matplotlibでグラフを描画してください",
)
```

### GitHubコネクターでリポジトリを分析

```
github_agent = client.beta.agents.create(
    model="mistral-large-latest",
    description="GitHubリポジトリを分析するエージェント",
    name="GitHub Audit Agent",
    instructions="指定されたGitHubリポジトリのコードを分析し、セキュリティ上の問題点を報告してください",
    tools=[
        {"type": "web_search"},
        {"type": "connector", "connector_id": "github"}  # IDはMistral Consoleで確認
    ],
)

response = client.beta.conversations.start(
    agent_id=github_agent.id,
    inputs="openai/openai-python リポジトリの依存関係の脆弱性を調査してください",
)
```

## カスタムMCPコネクターの登録

独自のMCPサーバーをコネクターとして登録し、チームや組織全体で共有できます。

<!-- IMAGE\_SLOT: custom-connector  
description: "Step-by-step flow diagram showing custom MCP connector registration process: Developer creates MCP server → Register in Mistral Studio → Available to all agents → Used in conversations. Clean horizontal flowchart, blue accent colors."  
aspect: "16:9"  
-->

### カスタムコネクターの作成

```
# 外部MCPサーバーをコネクターとして登録
my_connector = client.beta.connectors.create(
    name="my-internal-crm",
    description="社内CRMシステムへのアクセスコネクター",
    server="https://crm.example.com/mcp",
    visibility="shared_workspace"  # チーム内で共有
)

print(f"コネクターID: {my_connector.id}")
```

### コネクターの管理

```
# コネクター一覧を取得
connectors = client.beta.connectors.list()
for c in connectors:
    print(f"{c.name}: {c.id}")

# コネクターを削除
client.beta.connectors.delete(connector_id=my_connector.id)
```

登録したカスタムコネクターは、組み込みコネクターと同様に `tools` パラメーターで指定できます。

```
tools=[{"type": "connector", "connector_id": my_connector.id}]
```

### Salesforce CRMとの連携例

```
crm_agent = client.beta.agents.create(
    model="mistral-medium-latest",
    description="CRM分析エージェント",
    name="CRM Agent",
    tools=[{"type": "connector", "connector_id": "salesforce-crm"}]  # IDはMistral Consoleで確認
)

response = client.beta.conversations.start(
    agent_id=crm_agent.id,
    inputs="先四半期に更新された企業アカウントはどれですか？",
)
```

## エンタープライズ活用ユースケース

### 1. GitHubリポジトリのセキュリティ監査

GitHub + Web Searchコネクターを組み合わせ、リポジトリのコードとリアルタイムの脆弱性情報を照合するエージェントを構築できます。

```
入力: "django/django の SECRET_KEY 管理に関するセキュリティリスクを分析"
→ GitHubで最新コードを取得
→ Web Searchで関連CVEを検索
→ 統合分析レポートを生成
```

### 2. メールベースの契約分析

GmailコネクターとDocument Libraryを組み合わせ、受信メールの内容と社内ドキュメントを照合する分析エージェントを構築できます。

### 3. リアルタイムデータ分析パイプライン

Web Search + Code Executionを組み合わせ、最新のマーケットデータを取得してPythonで分析・可視化するパイプラインを構築できます。

## ガバナンスと制御

Mistral Connectorsはエンタープライズ要件を考慮した制御機能を提供しています。

### Human-in-the-loop承認フロー

セキュリティが重要なツール実行前に、人間による承認フローを実装できます。

```
# ツール実行の承認フローを組み込む
response = client.beta.conversations.continue_(
    conversation_id=conv.id,
    inputs=[{
        "role": "tool_result",
        "tool_use_id": pending_tool.id,
        "content": "承認済み: 実行を許可します"
    }]
)
```

### コネクターの可視性制御

| 設定値 | 公開範囲 |
| --- | --- |
| `private` | 作成者のみ |
| `shared_workspace` | ワークスペース内の全メンバー |

## 注意点

* Connectors機能は2026年4月時点でパブリックプレビュー段階のため、APIの仕様が変更される可能性があります
* カスタムMCPコネクターはMCPプロトコルに準拠したサーバーが必要です
* GitHubおよびGmailコネクターはOAuth認証が必要です
* 料金はコネクターの種類と使用量によって異なります。詳細は[Mistral料金ページ](https://mistral.ai/pricing/)を参照してください

## まとめ

Mistral Connectorsにより、MCPプロトコルを通じてAIエージェントを企業データや外部サービスに統合できるようになりました。

* **組み込みコネクター**（Web Search・Code Execution・Image Generation・Document Library・GitHub・Gmail）がすぐに利用可能
* **カスタムMCPコネクター** を登録・共有してチーム全体で再利用できる
* **API/SDK対応** により全モデル・エージェント呼び出しからコネクターを使える
* **Human-in-the-loop** や可視性制御でエンタープライズ要件に対応

Mistral StudioのGUI（[console.mistral.ai](https://console.mistral.ai/build/connectors)）からもコネクターを設定できるため、コードを書かずに検証することもできます。

## 参考リンク
