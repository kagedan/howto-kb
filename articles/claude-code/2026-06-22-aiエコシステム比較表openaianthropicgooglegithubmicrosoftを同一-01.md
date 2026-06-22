---
id: "2026-06-22-aiエコシステム比較表openaianthropicgooglegithubmicrosoftを同一-01"
title: "AIエコシステム比較表：OpenAI、Anthropic、Google、GitHub、Microsoftを同一レイヤーで整理"
url: "https://qiita.com/ochtum/items/c7e0814d4e9646a22cb0"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-06-22"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

:::note info
※お役に立てたらストック、いいねをよろしくお願いします！！
:::

**＜📝本記事のターゲット層＞**

- 主要AIサービスの違いを表で把握したい人
- 生成AIサービス選定の比較表を作りたい担当者
- 開発者向け・企業向けAI基盤を横断比較したい人

---

[目次ページ](https://qiita.com/ochtum/items/4ba6359edfd451ff9a08)

# 🔷<font color="1A5E2A">AIエコシステム比較表：OpenAI、Anthropic、Google、GitHub、Microsoftを同一レイヤーで整理</font>

AIサービスを比較するとき、ChatGPT、Claude、Gemini、GitHub Copilot、Microsoft Copilotをそのまま横に並べると、少し分かりにくくなります。

理由は、それぞれが同じ役割のサービスではないためです。

ChatGPTやClaudeは汎用チャットAIとして使われることが多く、GitHub Copilotは開発者の作業場所に入るコーディング支援です。Microsoft 365 Copilotは業務アプリとの統合が中心で、GoogleのGeminiは個人向けアプリ、Workspace、Google Cloudの各レイヤーに広がっています。

つまり、AIサービス比較では「名前」ではなく、**同じレイヤーに並べて見ること**が重要です。

この記事では、OpenAI、Anthropic、Google、GitHub、Microsoftを、Foundation Models、Consumer AI、Coding AI、Agent、Platform、Enterpriseの6レイヤーで整理します。

「OpenAI Anthropic Google GitHub Microsoft 比較」や「AIサービス 比較表」を作りたい人向けに、まず横断比較の入口として使える形にまとめます。

## 🔹<font color="2E7D32">1. AIエコシステムは同じレイヤーで比較する</font>

AIエコシステム比較で最初に大切なのは、役割が違うものを無理に一対一で比べないことです。

たとえば、ChatGPTとGitHub CopilotはどちらもAIサービスですが、主な利用場所が違います。

- ChatGPT：文章作成、調査、要約、ファイル分析などに使う汎用AIアプリ
- GitHub Copilot：IDE、リポジトリ、Pull Request、Issueなどで使う開発者向けAI
- Microsoft 365 Copilot：Word、Excel、Teams、Outlookなどで使う業務向けAI
- OpenAI Platform：AI機能をアプリに組み込むための開発者向け基盤
- Gemini Enterprise Agent Platform：企業向けAIエージェントを構築、運用するための基盤

このように、同じ「AI」という言葉でも、アプリ、開発基盤、エージェント、企業管理では見ているものが違います。

この記事では、次の6レイヤーで整理します。

| レイヤー          | 何を見るか                                         |
| ----------------- | -------------------------------------------------- |
| Foundation Models | GPT、Claude、Gemini、MAI、Phiなどの基盤モデル      |
| Consumer AI       | 一般利用者向けのチャット、検索、日常作業支援       |
| Coding AI         | IDE、CLI、リポジトリ、レビュー、開発タスク支援     |
| Agent             | ツール利用、タスク分解、自律実行、承認フロー       |
| Platform          | API、SDK、モデル管理、評価、デプロイ、開発者基盤   |
| Enterprise        | ID管理、権限、監査、社内データ連携、業務アプリ統合 |

この6レイヤーで見ると、各社の強みがかなり整理しやすくなります。

OpenAIはChatGPTとPlatformが強く、AnthropicはClaudeとMCP連携が特徴的です。GoogleはGeminiとGoogle Cloud / Workspace、GitHubは開発ワークフロー、MicrosoftはMicrosoft 365 / Foundry / Copilot Studioとの統合に強みがあります。

## 🔹<font color="2E7D32">2. レイヤー別の主要サービス比較表</font>

比較表に入る前に、まず「同じレイヤーで見る」イメージを図で押さえておきましょう。

以下の図は、主要5社をレイヤー別に並べて比較するためのマトリクスです。

![主要AIエコシステムをレイヤー別に比較するマトリクス図](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/755626/1294d885-04cd-4fea-a019-0a2abdb77024.png)

_AIエコシステムは同じレイヤーに並べると違いが見えやすい_

図の通り、AIエコシステムは「モデル」「チャット」「コーディング」「エージェント」「基盤」「企業」のように分けると比較しやすくなります。

ここからは、OpenAI、Anthropic、Google、GitHub、Microsoftを同じ表に並べます。

| レイヤー          | OpenAI                                                        | Anthropic                            | Google                                                                     | GitHub                                                        | Microsoft                                                        |
| ----------------- | ------------------------------------------------------------- | ------------------------------------ | -------------------------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------- |
| Foundation Models | GPT系モデル                                                   | Claude系モデル                       | Gemini                                                                     | 外部モデル利用、GitHub Models                                 | MAI、Phi、Foundry Models                                         |
| Consumer AI       | ChatGPT                                                       | Claude                               | Gemini app、Gemini Live                                                    | Copilot Chat                                                  | Microsoft Copilot                                                |
| Coding AI         | Codex、Codex CLI、Codex SDK                                   | Claude Code                          | Gemini Code Assist                                                         | GitHub Copilot、agent mode                                    | GitHub Copilot連携、Copilot for Azure、Azure DevOps連携          |
| Agent             | Responses API、Agents SDK、Agent Builder、Codex系ワークフロー | Claude Code、Tool use、MCP connector | Agent Development Kit、Agent Engine、A2A、Gemini Enterprise Agent Platform | Copilot cloud agent、custom agents、third-party coding agents | Foundry Agent Service、Microsoft Agent Framework、Copilot Studio |
| Platform          | OpenAI Platform                                               | Claude API                           | Vertex AI、Gemini Enterprise Agent Platform                                | GitHub Models、GitHub Spark、GitHub Actions                   | Microsoft Foundry                                                |
| Enterprise        | ChatGPT Business / Enterprise系機能                           | Claude Team / Enterprise系機能       | Google Workspace with Gemini、Google Cloud                                 | GitHub Enterprise、Copilot Business / Enterprise              | Microsoft 365 Copilot、Entra ID、Power Platform、Copilot Studio  |

※2026年6月20日時点の公開情報をもとに整理しています。各社の名称、提供地域、プラン、プレビュー表記、管理者設定は変わる可能性があります。導入前には必ず公式ページを確認してください。

### ▸<font color="388E3C">表の読み方</font>

この表は「どれが一番良いか」を決めるためのランキングではありません。

むしろ、次のような問いに答えるための地図です。

- 汎用チャットAIとして使いたいなら、どの選択肢があるか
- 開発者向けのコーディング支援なら、どこを見るべきか
- APIやSDKで自社サービスに組み込むなら、どのPlatformが候補になるか
- AIエージェントを作るなら、どのSDKや実行基盤があるか
- 企業導入なら、ID管理、監査、社内データ連携をどこまで確認すべきか

たとえば、個人で文章作成や調査に使うならConsumer AIの行を見れば十分なこともあります。

一方で、開発チームで使うならCoding AIとPlatform、企業導入ならEnterpriseとAgentの行まで確認した方が安全です。

:::note info
💡<font color="1976D2">Tips：比較表は「選定の入口」として使う</font>

比較表は便利ですが、表だけで最終決定するのは危険です。

同じレイヤーに見えても、料金、提供地域、管理機能、データ保持、監査ログ、プレビュー扱いの有無が違います。まず候補を絞り、そのあと公式ドキュメントと契約条件を確認する流れにしましょう。
:::

## 🔹<font color="2E7D32">3. レイヤーごとに見える各社の強み</font>

比較表を見ると、各社がどのレイヤーを得意としているかが見えてきます。

ここでは、会社ごとの特徴をもう少し実務目線で整理します。

### ▸<font color="388E3C">OpenAI：汎用AIアプリと開発者Platformに強い</font>

OpenAIは、ChatGPTとOpenAI Platformを中心に広がるエコシステムです。

Consumer AIではChatGPTが入口になり、開発者向けにはOpenAI Platform、Responses API、Agents SDK、Codex系ワークフローがあります。

特に、チャット体験とAPI/SDKの両方を持っているため、個人利用からプロダクト組み込みまで広く検討しやすいのが特徴です。

### ▸<font color="388E3C">Anthropic：ClaudeとMCP周辺の連携に特徴がある</font>

Anthropicは、Claude、Claude Code、Claude API、MCPを中心に整理できます。

Claudeは文章作成、分析、要約、コーディングに使いやすく、Claude Codeは開発者の作業支援に向いています。

MCPは、AIアプリケーションが外部ツールやデータソースに接続するためのプロトコルとして重要です。エージェント時代では、モデル単体の性能だけでなく、どのツールや文脈につながるかが大きな差になります。

### ▸<font color="388E3C">Google：Gemini、Cloud、Workspace、Agent Platformをつなぐ</font>

Googleは、Geminiを個人向けアプリ、Workspace、Google Cloud、Gemini Enterprise Agent Platformに広げています。

Google Workspaceを使っている組織では、Gmail、Docs、Sheets、Meetなどの業務アプリとの連携が重要になります。開発者や企業向けには、Vertex AIやGemini Enterprise Agent Platform、Agent Development Kit、Agent Engineが比較対象になります。

2026年6月時点では、Gemini Enterprise Agent Platformのドキュメントが活発に更新されており、Agent Platformの進化形として、企業向けAIエージェントを構築、デプロイ、ガバナンス、最適化する統合基盤として案内されています。

### ▸<font color="388E3C">GitHub：開発ワークフローそのものに強い</font>

GitHubは、自社LLM企業として見るよりも、開発ワークフローにAIを組み込む基盤として見るのが自然です。

GitHub Copilotは、IDE、リポジトリ、Pull Request、Issue、GitHub Actionsと結びついています。Copilot cloud agentでは、Azure Boardsの作業項目からCopilot cloud agentへ送ってPull Requestを生成する連携も公式ドキュメントで案内されています。

また、Azure DevOpsに関しては、2026年6月時点で「GitHub Copilot for Azure DevOps」という単独の横並び名称で断定するより、Azure Boards連携、GitHub Advanced Security for Azure DevOpsのCopilot Autofix限定プレビュー、GitHub Copilot for Azureなど、用途ごとに確認する方が正確です。

### ▸<font color="388E3C">Microsoft：Microsoft 365、Azure、Foundry、Copilot Studioの企業統合に強い</font>

Microsoftは、Microsoft Copilot、Microsoft 365 Copilot、Microsoft Foundry、Foundry Agent Service、Microsoft Agent Framework、Copilot Studioを組み合わせた企業向けエコシステムが強みです。

Microsoft 365を使っている企業では、Word、Excel、PowerPoint、Teams、Outlook、SharePointなどとの統合が重要になります。

Microsoft Foundryでは、OpenAI、Metaなどを含む多数のモデルに加えて、MAI、PhiなどのMicrosoftモデル群もFoundry Modelsの文脈で扱われています。モデル選択、アプリ開発、エージェント運用をAzure上でまとめて見たい場合に比較対象になります。

以下の図は、各社の強みの中心がどの領域にあるかを整理したものです。

![主要AI企業の強みを領域別に整理した図](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/755626/ac3ef6f1-f857-40e2-a4fe-c017f790981e.png)

_各社の強みはエコシステム内の得意レイヤーに表れる_

図のポイントは、優劣ではなく適性で見ることです。

OpenAIは汎用AIと開発者Platform、Anthropicは連携思想、GoogleはクラウドとWorkspace、GitHubは開発ワークフロー、Microsoftは企業統合に強みがあります。

## 🔹<font color="2E7D32">4. 比較時に注意したい名称・提供範囲の変化</font>

AIエコシステム比較で難しいのは、サービス名や提供形態が変わりやすいことです。

同じ名前でも、個人向け、チーム向け、企業向け、API向けで機能が違う場合があります。また、同じ機能でも、GA、プレビュー、限定プレビュー、地域限定、管理者設定が必要など、導入条件が変わることがあります。

特に注意したいのは次の点です。

| 確認ポイント   | 見る内容                                                          |
| -------------- | ----------------------------------------------------------------- |
| 正式名称       | 旧名称、リブランド、統合後の名称が混在していないか                |
| 提供地域       | 日本や自社の利用地域で使えるか                                    |
| プラン         | 個人、Team、Business、Enterprise、API課金で使える範囲が違わないか |
| プレビュー表記 | GAか、public previewか、limited public previewか                  |
| 管理者設定     | 組織管理者が有効化する必要があるか                                |
| データ利用     | 入力データ、ログ、学習利用、保持期間を確認したか                  |
| 監査・権限     | ID管理、監査ログ、権限、社内データ連携を扱えるか                  |

### ▸<font color="388E3C">GitHubとAzure DevOpsまわりは特に注意</font>

Azure DevOpsとの関係では、たとえば次のような機能があります。

- Azure BoardsからCopilot cloud agentへ作業を送る連携
- GitHub Advanced Security for Azure DevOpsにおけるCopilot Autofixの限定プレビュー
- Visual Studio CodeなどでAzure開発を支援するGitHub Copilot for Azure
- Azure DevOps WikiをMicrosoft 365 Copilotで検索可能にするコネクタ

このように、Azure DevOpsそのものに単一の「Copilot製品」があるというより、GitHub、Azure、Microsoft 365 Copilot、Azure DevOpsの各連携が用途別に用意されていると見る方が自然です。

### ▸<font color="388E3C">GoogleのVertex AIとGemini Enterprise Agent Platformも確認する</font>

Google Cloudでは、Vertex AI、Gemini API、Agent Development Kit、Agent Engine、Gemini Enterprise Agent Platformなどの関係を確認する必要があります。

Gemini Enterprise Agent Platformの公式ドキュメントでは、企業向けAIエージェントやモデルベースのソリューションを構築、デプロイ、ガバナンス、最適化する統合プラットフォームとして案内されています。また、Agent Platformの進化形として、200以上の基盤モデルへのアクセスからエージェントのデプロイ、管理までを支援する説明があります。

Google Cloudは名称や構成が更新されやすいため、導入時は最新のリリースノートと公式ドキュメントを確認しましょう。

### ▸<font color="388E3C">Microsoftのモデル表記はFoundry Modelsで確認する</font>

Microsoftのモデルは、MAIやPhiだけでなく、Foundry Modelsのカタログ全体で見る必要があります。

Microsoft Learnでは、Foundry ModelsにはOpenAI、Metaなどを含む多数のモデルがあり、MicrosoftモデルとしてMAI、Phi、Healthcare AI modelsなどのモデルグループが示されています。

そのため、比較表では「Microsoft = MAI / Phiだけ」と固定せず、Microsoft Foundry上のモデルカタログ、Azure Direct Models、パートナー・コミュニティモデルを含めて確認するのがおすすめです。

## ✅<font color="2E7D32">5. まとめ：横並び比較は選定の入口にする</font>

AIエコシステムを比較するときは、ChatGPT、Claude、Gemini、GitHub Copilot、Microsoft Copilotのような名前だけで判断しないことが大切です。

同じAIサービスでも、役割が違います。

- Foundation Modelsでは、GPT、Claude、Gemini、MAI、Phiなどのモデルを見る
- Consumer AIでは、ChatGPT、Claude、Gemini、Microsoft Copilotなどの利用体験を見る
- Coding AIでは、Codex、Claude Code、Gemini Code Assist、GitHub Copilotなどを見る
- Agentでは、Agents SDK、MCP、ADK、Copilot cloud agent、Foundry Agent Serviceなどを見る
- Platformでは、OpenAI Platform、Claude API、Vertex AI、GitHub Models、Microsoft Foundryなどを見る
- Enterpriseでは、権限管理、監査、社内データ連携、業務アプリ統合を見る

比較表は、最終決定の答えではなく、選定の入口です。

まず同じレイヤーに並べて候補を整理し、そのあと用途別、開発者視点、エンタープライズ要件、料金・プランの詳細を確認していきましょう。

特に企業導入では、モデル性能だけでなく、データ保護、監査ログ、ID管理、提供地域、契約条件、管理者設定まで確認する必要があります。

この記事の比較表を起点に、自分の目的に必要なレイヤーを絞り込んでみてください。

## 🔹<font color="2E7D32">参考URL</font>

本記事では、2026年6月20日時点で確認できる公式情報を参考にしています。各サービスの名称、料金、提供状況、プレビュー表記は変わる可能性があるため、導入前には最新の公式ページを確認してください。

- [OpenAI Developers](https://developers.openai.com/)
- [OpenAI Agents SDK](https://developers.openai.com/api/docs/guides/agents)
- [Anthropic Claude Docs](https://docs.anthropic.com/)
- [Claude Code MCP](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/overview)
- [Gemini Enterprise Agent Platform release notes](https://docs.cloud.google.com/gemini-enterprise-agent-platform/release-notes)
- [GitHub Copilot](https://docs.github.com/copilot)
- [GitHub Copilot cloud agent with Azure Boards](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/integrate-cloud-agent-with-azure-boards)
- [GitHub Copilot for Azure](https://learn.microsoft.com/en-us/azure/developer/github-copilot-azure/get-started)
- [Azure DevOps Sprint 275 update](https://learn.microsoft.com/en-us/azure/devops/release-notes/2026/sprint-275-update)
- [Microsoft Foundry Models overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/foundry-models-overview)
- [Microsoft models in Foundry](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-from-partners)
- [Microsoft Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/overview)
- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/)
- [Microsoft Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio)

---

:::note info
※お役に立てたらストック、いいねをよろしくお願いします！！
:::
