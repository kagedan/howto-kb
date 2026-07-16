---
id: "2026-07-16-minicoohei-httpstcompf2xnzxca-01"
title: "@minicoohei: https://t.co/Mpf2xNZxCA"
url: "https://x.com/minicoohei/status/2077803056876724689"
source: "x"
category: "claude-code"
tags: ["MCP", "API", "LLM", "GPT", "x"]
date_published: "2026-07-16"
date_collected: "2026-07-17"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

https://t.co/Mpf2xNZxCA


--- Article ---
## 「MCPをつなぐ」から「MCPを運用する」へ——Enterprise MCPに必要な4つの機能

先日のエンタープライズAI関連のセッションを見ていた時に、MCPをめぐる議論の中心が変わってきたと感じました。

少し前までの関心は、「MCP Serverをどう作るか」「ClaudeやChatGPTから社内ツールへどう接続するか」でした。

ところがエンプラ利用、企業利用で本当に難しいのは、接続そのものではありません。多数のMCP Server、AIエージェント、ユーザー、業務システムを、**誰が、どの権限で、どれだけ、いくらで利用し、何が起きたかを追跡できる状態で運用すること**です。

Workatoのスライドにあった、次の言葉がこの変化を端的に表しています。

![](https://pbs.twimg.com/media/HNXQYFubUAIEQM4.jpg)

*図1：MCPは接続の標準であり、それ単体で企業向けの運用基盤になるわけではない（撮影：筆者）*

MCPは、AIクライアントとデータ・ツールを接続するための標準プロトコルです。しかし、HTTPだけでは企業向けWebサービスが成立しないのと同じように、MCPの仕様だけでは企業の業務システムを安全に動かせません。

そこで必要になるのが、本稿でいう **Enterprise MCP** です。これは単一の製品名ではなく、MCPを企業で継続運用するためのコントロールプレーン全体を指します。各社の発表を横断して見ると、主要な論点は次の4つに整理できます。

1. MCP Serverのライフサイクルを扱う Managed MCP
1. ユーザーの権限を接続先まで伝える Identity / Permission Management
1. モデルからツール実行までを追跡する Observability / Audit
1. トークンやモデル利用料を管理する AI FinOps
加えて、ツールの粒度設計と、LLMの判断から業務実行を分離する設計が、本番利用の成否を左右します。

## 1. Managed MCPは「ホスティング」ではなく「運用のコントロールプレーン」

Databricksの発表では、MCP Serverを大きくManagedとCustomの2系統に分けていました。

![](https://pbs.twimg.com/media/HNXQ5j_bUAUTcHn.jpg)

Managed MCPという言葉からは、サーバーを代わりに起動してくれるサービスを想像しがちです。しかし、企業利用で必要なのはそれだけではありません。

MCP Serverの登録と発見、デプロイ、バージョン管理、ロールバック、死活監視、スケーリング、シークレット管理、接続ポリシー、監査ログまでを一貫して扱える必要があります。

Custom MCPについても、自由に実装できるだけでは不十分で、組織の認証・監査・監視の仕組みに載せられることが重要です。

つまりManaged MCPの本質は、MCP Serverを「動かすこと」ではなく、**「組織の管理対象として扱えることに**あります。

## 2.権限管理の核心は「誰として実行したか」を接続先まで伝えること

Enterprise MCPで最も難しい論点の一つが、アイデンティティの伝搬です。

![](https://pbs.twimg.com/media/HNXRU1nbUAUaNeN.jpg)

たとえば、ある社員がAIエージェントに「Salesforceの商談を更新して」と依頼したとします。この処理がMCP Serverを経由する場合でも、Salesforce上では本人に許可された範囲だけを操作しなければなりません。

共有サービスアカウントですべてを実行すると、最小権限を維持できず、「誰が、なぜ、その変更を行ったか」という監査も曖昧になります。

一方で接続先はOAuth、SAML、JWT、API Keyなど認証方式が異なり、トークンの更新・失効・ローテーションも個別に管理する必要があります。

Enterprise MCPに必要なのは、単なるログイン機能ではありません。

**エンドユーザーのアイデンティティをエージェントからMCP Server、さらに接続先システムまで安全に伝搬し、既存のRBACやデータ権限を引き継ぐ仕組み**です。高リスクな操作では、ポリシー判定や人間による承認もこの経路に組み込む必要があります。

## 3. 監視はMCP Server単体ではなく、モデル・エージェント・ツールを一つの実行系列として見る
