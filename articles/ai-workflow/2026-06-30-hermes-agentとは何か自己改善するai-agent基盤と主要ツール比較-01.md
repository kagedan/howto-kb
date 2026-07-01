---
id: "2026-06-30-hermes-agentとは何か自己改善するai-agent基盤と主要ツール比較-01"
title: "Hermes Agentとは何か：自己改善するAI Agent基盤と主要ツール比較"
url: "https://zenn.dev/idealab/articles/4192136368168a"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "LLM", "OpenAI", "Gemini"]
date_published: "2026-06-30"
date_collected: "2026-07-02"
summary_by: "auto-rss"
query: ""
---

この記事では、Hermes Agent が何を解決するものなのか、類似ツールと比べてどこが違うのか、どんな人に向いているのかを整理します。

<https://hermes-agent.nousresearch.com/>

![](https://static.zenn.studio/user-upload/deployed-images/1093c7d26e4793244bb9ce12.png?sha=b5424b95373e669ee4a6d4bdff2d7f297e4101c2)  
*出典: [Hermes Agent](https://hermes-agent.nousresearch.com/)*

## AI Agent基盤とHermes Agent

### AI Agent基盤は何を解決するものなのか

LLM 単体は、質問に答えることは得意だが、業務で継続的にタスクを任せようとすると以下の弱点が顕在化します。

**1. 過去の会話を覚えていない**

**2. 外部ツール使用に関わる安全性の管理**

**3. 長時間タスクの進捗管理**

**4. 権限管理**

AI Agent 基盤は、このあたりを補うための層です。

2025年以降に Agent 基盤が増えているのは、モデルの性能だけでは実務に足りないことが見えてきたからだと思われます。

![](https://res.cloudinary.com/zenn/image/fetch/s--0OPekXm8--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://sight-r.sts-inc.co.jp/wp/wp-content/uploads/2026/05/%25E7%2594%25BB%25E5%2583%258F2.png?_a=BACMTiAE)  
*出典: [Google Cloudで実現する、企業向けAIエージェント基盤の考え方](https://sight-r.sts-inc.co.jp/google_cloud_article/ai_agent_infra_strategy/)*

### Hermes Agentとは何か

Hermes Agent は、Nous Research が開発するオープンソースの AI Agent 基盤で、公式 GitHub では「self-improving AI agent」として紹介されています。

特徴は、自己改善を前提にしている点にあります。

Hermes Agent は、会話や作業を通じてスキルを作り、過去の文脈を保存し、必要に応じて呼び出します。  
CLI や TUI だけでなく、Telegram、Discord、Slack などのメッセージング環境からも使えます。  
つまり、単発のチャットアプリというより、「**自分専用の常駐 AI Agent を動かすための基盤**」に近いという認識で良いかと思います。

![](https://static.zenn.studio/user-upload/deployed-images/dec3bf94292db9e04545f5de.png?sha=9ddd3a6981c64cd8381dac70156b3a4cdcc5893c)  
*出典: [Hermes Agent入門 — 永続メモリと自動スキル生成で成長するOSSエージェント](https://qiita.com/kai_kou/items/c4ba4c6dfd0342634a78)*

### Hermes Agentのアーキテクチャ

Hermes Agent の構成は、大きく分けると次のようになります。

| 層 | 役割 |
| --- | --- |
| 入力チャネル | CLI、TUI、Slack、Discord、Telegram などから指示を受ける |
| Agent Runtime | 会話、ツール実行、スキル、メモリを束ねる中核 |
| LLM Provider | OpenAI、OpenRouter、Nous Portal など複数モデルを扱う |
| Tool System | ブラウザ、端末、ファイル、API、MCP などを実行する |
| Memory / State | SQLite や検索機構で会話履歴や状態を保存する |
| Skill System | よく使う手順や作業パターンを再利用可能にする |
| Scheduler | 定期実行や継続タスクを扱う |
| Sub Agents | 作業を分担して並列に進める |

![](https://res.cloudinary.com/zenn/image/fetch/s--I3VBgpGW--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://miro.medium.com/v2/resize:fit:2000/1%2ANonfjmkkAbVPSsUH_bj0Dg.png?_a=BACMTiAE)  
*出典: [What Is Hermes Agent, and Why It's Better Than OpenClaw for Personal AI Workflows](https://medium.com/data-science-collective/what-is-hermes-agent-and-why-its-better-than-openclaw-for-personal-ai-workflows-d59d83436ad2)*

### Hermes Agentが強いユースケース

Hermes Agent が強いのは、使うほど文脈が増え、作業パターンが育っていく用途です。

たとえば、**個人用の常駐アシスタント**。毎日の調査、メモ整理、リマインド、定期レポートを任せたい場合に向いています。

**開発支援**にも向いていると思われます。CLI やツール実行、サブエージェント、スキル化を組み合わせることで、単発のコード生成ではなく、作業の継続や再利用に寄せられます。

**Slack や Discord 経由の業務自動化**にも使いやすい。人間が普段いるチャネルから指示し、裏側で Agent が調査や整理を進める形を作れます。

一方で、社内全体に配る統制済み Agent 基盤としては、別途設計が必要になります。権限管理、監査ログ、データ保持、SLA、管理者機能は、Copilot Studio や Bedrock Agents、Agentforce のような企業向け製品のほうが最初から揃っています。

## Hermes Agentと類似ツール

### 類似ツール一覧

| カテゴリ | 代表ツール | 向いている用途 |
| --- | --- | --- |
| 自己改善・長寿命・個人用 Agent 系 | Hermes Agent、OpenClaw、Letta | 個人化、長期メモリ、常駐 Agent、個人秘書 |
| OSS SDK / オーケストレーション系 | LangGraph、CrewAI、OpenAI Agents SDK、Semantic Kernel | 自社アプリへの組み込み |
| ローコード / ビジュアル系 | Dify、Flowise、Relevance AI | PoC、業務部門の内製 |
| 企業マネージド系 | Copilot Studio、Bedrock Agents、Gemini Enterprise、Agentforce | 統制、監査、既存 SaaS 連携 |
| 開発特化 Agent 系 | OpenHands | ソフトウェア開発自動化 |

Hermes Agent は、この中では「自己改善・長寿命 Agent 系」に入ります。

### 主要ツール比較

| ツール | 強み | 弱み | 向いている人 |
| --- | --- | --- | --- |
| Hermes Agent | 自己改善、永続メモリ、常駐運用、複数チャネル | 企業統制は自前設計が必要 | 個人開発者、研究者、R&D |
| OpenClaw | メッセージング中心の個人用AIアシスタント、スキル拡張、ローカル実行 | スキル供給網や権限管理にリスクがある | 個人用AI秘書、日常業務の自動化 |
| LangGraph | 状態管理、長時間 Agent、堅牢なワークフロー | 設計力が必要 | Agent アプリ開発者 |
| CrewAI | マルチ Agent 設計が直感的 | 複雑な本番運用は設計次第 | Python 開発者 |
| OpenAI Agents SDK | 軽量で組み込みやすい、Tracing が扱いやすい | 完成品ではなく SDK | OpenAI 周辺で開発する人 |
| Semantic Kernel | Microsoft 系との親和性、企業開発向け | 設計は開発者依存 | .NET / Azure 系の開発者 |
| Dify | UI で作りやすい、RAG やワークフローに強い | 深い制御は SDK 系に劣る | PoC、業務部門、内製チーム |
| Flowise | ビジュアルに Agent / workflow を組める | 大規模統制は別途必要 | 小規模チーム、プロトタイピング |
| Copilot Studio | Microsoft 365 連携と管理機能 | Microsoft 依存が強い | M365 利用企業 |
| Bedrock Agents | AWS 統合、IAM、Guardrails | コストと構成が複雑 | AWS 中心の企業 |
| Agentforce | Salesforce データと業務に直結 | Salesforce 前提 | CRM 中心の企業 |
| OpenHands | 開発作業に特化 | 汎用業務 Agent ではない | 開発組織 |

### Hermes Agentと他ツールの主な違い

Hermes Agent の一つ目の違いは、SDK というより常駐 Agent に近いことです。

LangGraph や OpenAI Agents SDK は、開発者が自社アプリの中に Agent 機能を組み込むための基盤です。  
それに対して Hermes Agent は、CLI、チャット、メモリ、ツール、スキル、定期実行を含む実行環境として使えます。

二つ目の違いは、自己改善ループが中心にあることです。

多くの Agent 基盤は、決められたワークフローを実行します。  
Hermes Agent は、経験からスキルを作り、過去の文脈を再利用し、使うほど個人化していく方向に寄っています。

三つ目の違いは、長期記憶と個人化に強いことです。

Letta も memory-first な Agent 基盤として近い位置にあります。  
ただ、Hermes Agent はメッセージング連携、ツール実行、スケジューリングまで含めた常駐運用の色が強いです。

!

**OpenClawとの違い**

Hermes Agent と OpenClaw は、どちらも「自分専用の常駐 AI Agent」を作るための OSS という点で近い位置にあります。

ただし、重心は少し異なります。

OpenClaw は、Telegram、Discord、Signal、WhatsApp などのメッセージング環境を主な UI とする、**個人用 AI アシスタント**に近い存在です。ユーザーが普段使うチャット環境から指示し、スキルを追加しながら日常業務を自動化していく使い方に向いています。

一方で Hermes Agent は、自己改善、永続メモリ、スキル生成、過去文脈の再利用を中心にした「**育つ Agent runtime**」としての性格が強いです。単にメッセージからタスクを実行するだけでなく、作業経験を蓄積し、次回以降のタスクに再利用する方向に寄っています。

つまり、OpenClaw が「チャットから使える個人秘書」寄りだとすれば、Hermes Agent は「記憶とスキルを育てる長寿命 Agent 基盤」寄りです。

四つ目の違いは、企業統制より自由度に寄っていることです。

Copilot Studio、Bedrock Agents、Agentforce は、企業の管理、監査、権限、既存システム連携に強いです。  
Hermes Agent は OSS として自由度が高い一方、組織導入では権限設計やログ管理を自分たちで考える必要があります。

なお、この注意点は Hermes Agent だけでなく、OpenClaw のようなスキル拡張型 Agent にも共通します。

Agent に外部ツール、ファイル、ブラウザ、メール、決済、社内システムへのアクセス権限を渡すと、便利になる一方で攻撃面も広がります。特に、第三者が配布するスキルやプラグインをそのまま実行する場合、それは通常の拡張機能以上に注意が必要です。

常駐 Agent を使う場合は、少なくとも以下を設計しておくべきです。

* 許可するツールの範囲
* 実行前確認が必要な操作
* ログの保存
* スキルやプラグインのレビュー
* 外部ネットワークアクセスの制限
* 秘密情報や認証情報へのアクセス制御

自己改善する Agent やスキルを追加できる Agent は、「できること」が増えるほど「事故ったときの影響範囲」も広がります。

### 用途別のおすすめ

| 用途 | 第一候補 | 理由 |
| --- | --- | --- |
| 個人用 AI 秘書 | Hermes Agent | 常駐、記憶、チャネル連携が強い |
| Agent 研究 / R&D | Hermes Agent、LangGraph、Letta | 状態、記憶、自己改善を試しやすい |
| 自社アプリ組み込み | LangGraph、OpenAI Agents SDK、Semantic Kernel | SDK として扱いやすい |
| 業務部門の PoC | Dify、Flowise、Relevance AI | UI で早く作れる |
| Microsoft 365 企業 | Copilot Studio | M365 / Power Platform とつながる |
| AWS 企業 | Bedrock Agents | IAM、VPC、Guardrails と統合しやすい |
| Salesforce 企業 | Agentforce | CRM データと自然に統合できる |
| 開発作業の自動化 | OpenHands、Hermes Agent | coding agent 運用に寄せやすい |

Hermes Agent を選ぶべきなのは、「自分専用の長寿命 Agent を育てたい人」だと思います。

単発のチャットではなく、日々の作業を覚え、スキルを作り、複数のチャネルから呼び出せる Agent がほしい場合です。  
その場合、Hermes Agent は有力な選択肢になります。

## 結論：Hermes Agentは誰に向いているか

Hermes Agent は、企業向け統制基盤というより、個人・研究者・開発者が**自分専用の長寿命 Agent を育てて運用する OSS 基盤**です。  
自己改善、永続メモリ、スキル生成、マルチチャネル連携を一体で試せる一方、記憶・権限・ログ・レビュー設計なしに常駐させるとリスクも増えます。  
Agent 基盤選びでは「何ができるか」だけでなく、**どこまで任せるか、どう止めるか、どう育てるか**を考える必要があります。

## おまけ: Hermes Agents導入

### インストール

<https://hermes-agent.nousresearch.com/>

```
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### CLIから起動する

![](https://static.zenn.studio/user-upload/deployed-images/9462c5fd8ca64144ef09cd7a.png?sha=2c1f946072735f0f21f6260d04a9908f9e09610f)

### Slackに接続する

1. Slack manifest を生成

   ```
   hermes slack manifest --write
   ```
2. Slack App を作成

   Slack API の App 管理画面で、

   1. `Create New App`
   2. `From an app manifest`
   3. 対象 `workspace` を選択
   4. `~/.hermes/slack-manifest.json` の中身を貼り付け
   5. `Create`
3. App-Level Token を取得  
   Slack App の Socket Mode を有効化し、`connections:write` scope 付きの App-Level Token を作ります。  
   この token が `SLACK_APP_TOKEN` で、`xapp-...` から始まります。
4. Workspace にインストールして Bot Token を取得  
   Slack App の Install App から workspace にインストールします。インストール後に表示される **Bot User OAuth Token** が `SLACK_BOT_TOKEN` で、`xoxb-...` から始まります。
5. Hermes の .env に設定

   最低限これを入れます。

   ```
   SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   SLACK_APP_TOKEN=xapp-your-app-token-here
   SLACK_ALLOWED_USERS=U01ABC2DEF3
   ```

   `SLACK_ALLOWED_USERS` は Slack の Member ID です。これを設定しないと安全のため全メッセージが拒否される仕様です
6. Gateway を起動

   ```
   # 手動起動なら
   hermes gateway
   # サービス化するなら
   hermes gateway install
   # sudo hermes gateway install --system
   ```
7. Slack チャンネルに Bot を招待

   を実行します。Bot は自動でチャンネル参加しないので、使いたいチャンネルごとに招待が必要です。

![](https://static.zenn.studio/user-upload/deployed-images/55a97d2f77d6ff43c3cbcf2e.png?sha=5c5534f4b8cea598313b8e1d90d60fef56a5e253)
