---
id: "2026-03-24-microsoft-learn参照させるagent-skillsあるじゃん-01"
title: "Microsoft Learn参照させるAgent Skillsあるじゃん！"
url: "https://zenn.dev/headwaters/articles/d4417cd67f7935"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

# はじめに

周りの方の業務におけるAI活用がすごい…！  
ヘッドウォータース初参画のプロジェクトで最初に感じた事です  
開発経験やAzureの知識が浅い事に不安を感じてましたが、そもそも業務、開発を進める上でのAI活用でも遅れてました😭

なので、今回は**Agent Skills**について調べてみたのでまとめようと思います！

# Agent Skillsとは

`Agent Skills`とは、コーディングエージェントに特定の能力や知識、手順を持たせるための仕組みです。  
エージェントが実行できるタスクをモジュールとして定義し、必要なときに読み込んで利用できるようにすることで、より安定した動作と高い再利用性を実現するために使われます。

# Agent Skillsの生まれた背景

以前までのコーディングエージェントは、基本的にプロンプトに書かれた内容だけを頼りに動作していました。しかし実際の開発では、毎回同じ指示を書く必要があったり、特定のツールの使い方を毎回説明しなければならなかったりと、プロンプトだけに依存する方法には限界があります。さらにエージェントがファイル編集、テスト実行、設計書生成、図作成など複数の操作を行うようになると、単純なプロンプトでは動作を安定させることが難しくなりました。

そこで登場したのが**Agent Skills**です。  
特定の作業手順や知識、ツールの使い方をまとめてパッケージ化し、必要なときにエージェントが読み込めるようにすることで、プロンプトに毎回書かなくても同じ振る舞いを再現できるようになります。

# Azureエージェントスキル

実際に**Agent Skills**を触ってみる。  
今回は、Microsoftが公式で公開しているAzure開発のため`Skills`を利用してみます。

<https://learn.microsoft.com/ja-jp/training/support/agent-skills>

## 活用事例(公式より)

* AIコーディングエージェントに、公式ドキュメントに記載されている専門家レベルのAzureガイダンスを提供する
* Azure開発タスクのエージェント応答の精度と完全性を向上させる
* 開発者がベスト プラクティス、フローのトラブルシューティング、アーキテクチャ パターン、セキュリティ ガイダンスをエディターで直接取得できるようにする
* MCPサーバーなどのライブデータツールを補完するために、最新の構造化された知識を提供します。

## 手順

`GitHub Copilot`、`Claude Code`、`Cursor`、`Gemini CLI`、`Codex CLI`などの互換性のある AIコーディングアシスタントと連携できる。

#### 1. リポジトリのクローン

```
git clone https://github.com/MicrosoftDocs/agent-skills.git
```

#### 2. クローンしたリポジトリ内のskillsフォルダを、ご自身のプロジェクトにコピーする

* Claude Code
  + `{project}/.claude/skills/`
* GitHub Copilot
  + `{project}/.github/skills/`
* Codex CLI

#### エージェントに質問してみる

```
Microsoft Agent FrameworkでAIエージェントを実装する際のログ収集・監視のアーキテクチャ設計を教えてください
```

上記の質問をエージェントに投げてみると↓

![](https://static.zenn.studio/user-upload/b3d12fe942a3-20260324.png)

エージェントが`Skills`を認識して推論を進めていることが分かります

## 実際にSkillsの中身を見てみる

先ほどエージェントが参照していた`Skills`である`skills/microsoft-foundry/SKILL.md`の中身を確認してみると、、、

中身としては、`Microsoft Foundry`に関する調査・実装・設計の参照ガイドで、あくまでどの内容をどのドキュメントで確認するかを整理したものになってなってますね！

```
---
name: microsoft-foundry
description: トラブルシューティング、ベストプラクティス、意思決定、アーキテクチャと設計パターン、制限とクォータ、セキュリティ、構成、統合と実装パターン、デプロイを含む Microsoft Foundry（旧 Azure AI Foundry）開発の専門知識。Azure OpenAI、ベクター検索/RAG、Sora 動画、リアルタイム音声、MCP/LangChain API を用いた Foundry エージェント構築や、その他の Microsoft Foundry 関連開発タスクで使用します。Microsoft Foundry Classic には使用しません（`microsoft-foundry-classic` を使用）。Microsoft Foundry Local には使用しません（`microsoft-foundry-local` を使用）。Microsoft Foundry Tools には使用しません（`microsoft-foundry-tools` を使用）。
compatibility: ネットワークアクセスが必要です。ドキュメント取得には `mcp_microsoftdocs:microsoft_docs_fetch` または `fetch_webpage` を使用します。
metadata:
  generated_at: "2026-03-19"
  generator: "docs2skills/1.0.0"
---
# Microsoft Foundry スキル

このスキルは Microsoft Foundry に関する専門ガイダンスを提供します。トラブルシューティング、ベストプラクティス、意思決定、アーキテクチャと設計パターン、制限とクォータ、セキュリティ、構成、統合と実装パターン、デプロイを対象とします。ローカルのクイックリファレンスと、リモートドキュメント取得機能を組み合わせています。

## このスキルの使い方

> **エージェント向け重要事項**: 関連セクションを見つけるには、以下の **カテゴリ一覧** を使用します。行範囲があるカテゴリ（例: `L35-L120`）は、指定行を `read_file` で読みます。ファイルリンクがあるカテゴリ（例: `[security.md](security.md)`）は、リンク先の参照ファイルを `read_file` で読みます。

> **エージェント向け重要事項**: `metadata.generated_at` が 3 か月以上前なら、ユーザーにリポジトリから最新版を取得するよう案内します。`mcp_microsoftdocs` ツールが利用できない場合は、次のインストール手順を案内します: [Installation Guide](https://github.com/MicrosoftDocs/mcp/blob/main/README.md)

このスキルはドキュメント内容の取得に **ネットワークアクセス** を必要とします。
- **推奨**: クエリ文字列 `from=learn-agent-skill` を付けて `mcp_microsoftdocs:microsoft_docs_fetch` を使います。Markdown を返します。
- **代替**: クエリ文字列 `from=learn-agent-skill&accept=text/markdown` を付けて `fetch_webpage` を使います。Markdown を返します。

## カテゴリ一覧

| カテゴリ | 行 | 説明 |
|----------|-------|-------------|
| トラブルシューティング | L37-L41 | Microsoft Foundry の機能、デプロイ、統合、ランタイム動作に関する既知の問題、エラーコード、制限事項、現在の回避策。 |
| ベストプラクティス | L42-L52 | Foundry 上の Azure OpenAI エージェント向けに、ツール、プロンプト、システムメッセージ、ビジョンモデル、ファインチューニング、評価、性能（レイテンシ/スループット）を構成するためのベストプラクティス。 |
| 意思決定 | L53-L80 | Foundry ベースの AI ソリューションを設計・改善するために、モデル、SDK、デプロイ種別、コスト、移行（Azure OpenAI、GitHub Models、classic/preview）を選ぶためのガイド。 |
| アーキテクチャと設計パターン | L81-L93 | Foundry エージェント向けのアーキテクチャパターン: 標準構成、RAG/インデックス化、HA/DR、リージョン復旧、プロビジョンドスループット、スピルオーバートラフィック、LLM ルーティング最適化。 |
| 制限とクォータ | L94-L109 | Foundry エージェント、モデル、ベクター検索、バッチジョブ、Sora 動画、RFT、Azure OpenAI アクセスに関する制限、クォータ、レート制限、リージョン、タイムアウト、キャッシュ、コスト制御。 |
| セキュリティ | L110-L142 | Foundry のセキュリティ、ID、コンプライアンス: 認証/RBAC、プライベートネットワーク、暗号化/CMK、安全ガードレール、ポリシー/ガバナンス、データプライバシー、安全なツール/エージェント構成。 |
| 構成 | L143-L202 | Foundry エージェント、モデル、ツール、ストレージ、安全性/ガードレール、トレース、評価器、Azure OpenAI/Fireworks 統合を、デプロイ、監視、高度機能向けに構成する方法。 |
| 統合と実装パターン | L203-L268 | Foundry エージェントとモデルを外部アプリ、ツール、サービスと統合する方法: SDK 利用、REST API、MCP/LangChain、検索/音声/ブラウジングツール、ファインチューニング、リアルタイム音声、安全性、評価。 |
| デプロイ | L269-L286 | Foundry エージェント/モデルのデプロイと管理: 基盤セットアップ、コンテナ/ホスト型デプロイ、Azure/M365 公開、IaC（Bicep/Terraform）、CI/CD 評価、リージョン可用性。 |

### トラブルシューティング
| トピック | URL |
|-------|-----|
| Microsoft Foundry の既知の問題と回避策を確認する | https://learn.microsoft.com/en-us/azure/foundry/reference/foundry-known-issues |

### ベストプラクティス
| トピック | URL |
|-------|-----|
| エージェント向けツール構成のベストプラクティスを適用する | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-best-practice |
| 組み込みの品質・安全性テストで Foundry エージェントを評価する | https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent |
| Prompt Optimizer で Foundry エージェントのプロンプトを最適化する | https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/prompt-optimizer |
| Foundry 上の Azure OpenAI 向けに効果的なシステムメッセージを設計する | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/advanced-prompt-engineering |
| ビジョン対応 GPT モデル向けプロンプトエンジニアリング手法を適用する | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/gpt-4-v-prompt-engineering |
| 画像を使って GPT-4 ビジョンモデルをファインチューニングする | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning-vision |
| Foundry で Azure OpenAI のレイテンシとスループットを最適化する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/latency |

### 意思決定
| トピック | URL |
|-------|-----|
| 新しい Foundry Agent Service へ移行する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/migrate |
| エージェント向けに適切な Web grounding ツールを選ぶ | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/web-overview |
| Foundry のベンチマークとリーダーボードでモデルを比較する | https://learn.microsoft.com/en-us/azure/foundry/concepts/model-benchmarks |
| Foundry モデルの非推奨化と廃止に備える | https://learn.microsoft.com/en-us/azure/foundry/concepts/model-lifecycle-retirement |
| Microsoft Foundry の展開方針と環境戦略を立てる | https://learn.microsoft.com/en-us/azure/foundry/concepts/planning |
| Ask AI でモデルのコストと性能を最適化する | https://learn.microsoft.com/en-us/azure/foundry/control-plane/how-to-optimize-cost-performance |
| Foundry のデプロイ種別とデータ所在地オプションを選ぶ | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types |
| Foundry におけるモデルのバージョン管理とアップグレード方針を管理する | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/model-versions |
| Foundry のパートナーモデルとコミュニティモデルを選ぶ | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-from-partners |
| Azure 提供の Foundry Models を機能とリージョンで選定する | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure |
| ユースケースに応じて GPT-5 と GPT-4.1 を選ぶ | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/model-choice-guide |
| GitHub Models のワークロードを Foundry Models にアップグレードする | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/quickstart-github-models |
| Foundry のモデルリーダーボードを使ってモデルを比較・選定する | https://learn.microsoft.com/en-us/azure/foundry/how-to/benchmark-model-in-catalog |
| 適切な Microsoft Foundry SDK とエンドポイントを選ぶ | https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview |
| Azure AI Inference SDK から OpenAI SDK に移行する | https://learn.microsoft.com/en-us/azure/foundry/how-to/model-inference-to-openai-migration |
| classic から現行 Foundry への移行計画を立てる | https://learn.microsoft.com/en-us/azure/foundry/how-to/navigate-from-classic |
| Azure OpenAI から Foundry へのアップグレードを判断し実行する | https://learn.microsoft.com/en-us/azure/foundry/how-to/upgrade-azure-openai |
| Ask AI を使って Foundry モデルをアップグレードまたは切り替える | https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/optimization-model-upgrade |
| Foundry におけるコンテンツのストリーミングとフィルタリングモードを選ぶ | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-streaming |
| Foundry における廃止済み Azure OpenAI モデルを確認する | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/legacy-models |
| Azure OpenAI モデルの非推奨化と廃止予定を追跡する | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements |
| Foundry におけるファインチューニングコストを見積もり管理する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning-cost-management |
| PTU コストを見積もり、Foundry の容量計画を立てる | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-onboarding |
| preview から GA Realtime API に移行する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/realtime-audio-preview-api-migration-guide |

### アーキテクチャと設計パターン
| トピック | URL |
|-------|-----|
| 分離されたリソースで標準的なエージェント構成を設計する | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/standard-agent-setup |
| Foundry で RAG とインデックス化パターンを適用する | https://learn.microsoft.com/en-us/azure/foundry/concepts/retrieval-augmented-generation |
| 標準モードの Foundry Agent Service 向けに災害復旧を計画する | https://learn.microsoft.com/en-us/azure/foundry/how-to/agent-service-disaster-recovery |
| リソース損失とデータ損失から Foundry Agent Service を復旧する | https://learn.microsoft.com/en-us/azure/foundry/how-to/agent-service-operator-disaster-recovery |
| リージョンプラットフォーム障害から Foundry Agent Service を復旧する | https://learn.microsoft.com/en-us/azure/foundry/how-to/agent-service-platform-disaster-recovery |
| Foundry のプロジェクトとエージェントに対する高可用性と回復性を計画する | https://learn.microsoft.com/en-us/azure/foundry/how-to/high-availability-resiliency |
| モデルルーターを使って Foundry の LLM ルーティングを最適化する | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-router |
| Foundry モデル向けにプロビジョンドスループットのアーキテクチャを計画する | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/provisioned-throughput |
| プロビジョンドデプロイ向けのスピルオーバートラフィック管理を設計する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/spillover-traffic-management |

### 制限とクォータ
| トピック | URL |
|-------|-----|
| Foundry Agent Service のクォータ、制限、対応リージョン | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/limits-quotas-regions |
| エージェントでベクターストアとファイル検索の制限を利用する | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/vector-stores |
| 実行時間制限付きで function calling ツールを実装する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/function-calling |
| 評価の対応リージョン、レート制限、VNet サポート | https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-regions-limits-virtual-network |
| モデル向けトークンレート制限とクォータを構成する | https://learn.microsoft.com/en-us/azure/foundry/control-plane/how-to-enforce-limits-models |
| Foundry Models のクォータと制限を参照する | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/quotas-limits |
| Foundry における Sora 動画生成の機能と制約を確認する | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/video-generation |
| Azure OpenAI のグローバルバッチ処理を効率よく使う | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/batch |
| プロンプトキャッシュを構成し、Azure OpenAI のキャッシュ制限を理解する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/prompt-caching |
| コスト制限付きで強化学習ファインチューニングを使う | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/reinforcement-fine-tuning |
| Foundry における Azure OpenAI のクォータ、レート制限、タイムアウト | https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits |
| Azure OpenAI の限定アクセス ポリシーを理解する | https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/limited-access |

### セキュリティ
| トピック | URL |
|-------|-----|
| Foundry でエージェントの ID と RBAC を構成する | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-identity |
| Agent2Agent ツールの認証方式を構成する | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-to-agent-authentication |
| エージェントにおける MCP サーバーの認証を構成する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/mcp-authentication |
| UI 自動化のために computer use ツールを安全に使う | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/computer-use |
| Foundry の AI gateway で MCP ツールをガバナンスする | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/governance |
| 認証オプション付きで Foundry エージェント向け OpenAPI ツールを安全に構成する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/openapi |
| Foundry Agent Service 向けにプライベートネットワークを構成する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/virtual-networks |
| Microsoft Foundry の認証と認可を構成する | https://learn.microsoft.com/en-us/azure/foundry/concepts/authentication-authorization-foundry |
| Microsoft Foundry の暗号化向けに顧客管理キーを構成する | https://learn.microsoft.com/en-us/azure/foundry/concepts/encryption-keys-portal |
| Microsoft Foundry における RBAC ロールを理解して適用する | https://learn.microsoft.com/en-us/azure/foundry/concepts/rbac-foundry |
| Entra 管理者として Foundry のエージェント基盤を統制する | https://learn.microsoft.com/en-us/azure/foundry/control-plane/govern-agent-infrastructure-entra-admin |
| Foundry のコンプライアンスとセキュリティ統合を管理する | https://learn.microsoft.com/en-us/azure/foundry/control-plane/how-to-manage-compliance-security |
| モデルデプロイ向けガードレールポリシーを作成する | https://learn.microsoft.com/en-us/azure/foundry/control-plane/quickstart-create-guardrail-policy |
| Foundry Models 向けにキー不要の Entra ID 認証を構成する | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/configure-entra-id |
| Microsoft Foundry リソースを Network Security Perimeter に追加する | https://learn.microsoft.com/en-us/azure/foundry/how-to/add-foundry-to-network-security-perimeter |
| Microsoft Foundry 向けに Private Endpoint ネットワーク分離を構成する | https://learn.microsoft.com/en-us/azure/foundry/how-to/configure-private-link |
| Microsoft Foundry を統制するカスタム Azure Policy を作成する | https://learn.microsoft.com/en-us/azure/foundry/how-to/custom-policy-definition |
| タグと RBAC を使って Microsoft Foundry の preview 機能を無効化する | https://learn.microsoft.com/en-us/azure/foundry/how-to/disable-preview-features |
| Microsoft Foundry プロジェクト向けにマネージド仮想ネットワークを構成する | https://learn.microsoft.com/en-us/azure/foundry/how-to/managed-virtual-network |
| Foundry モデルデプロイ向けの組み込み Azure Policy 定義を使う | https://learn.microsoft.com/en-us/azure/foundry/how-to/model-deployment-policy |
| Foundry MCP Server のセキュリティベストプラクティスを適用する | https://learn.microsoft.com/en-us/azure/foundry/mcp/security-best-practices |
| Foundry の既定ガードレール安全ポリシーを理解する | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/default-safety-policies |
| Azure OpenAI アプリ向けに安全性システムメッセージテンプレートを使う | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/safety-system-message-templates |
| Azure OpenAI 向けに安全性重視のシステムメッセージを作成する | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/system-message |
| ファインチューニング済みモデルに安全性評価を適用する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning-safety-evaluation |
| Foundry Agent Service のデータプライバシーとセキュリティ | https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/agents/data-privacy-security |
| Foundry における Anthropic Claude のデータプライバシーとセキュリティを理解する | https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/claude-models/data-privacy |
| Foundry OpenAI 向けに著作権リスク軽減策を実装する | https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/customer-copyright-commitment |
| Azure Direct Models のデータ、プライバシー、セキュリティを理解する | https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy |

### 構成
| トピック | URL |
|-------|-----|
| Foundry Agent Service の capability host を構成する | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/capability-hosts |
| Foundry で Grounding with Bing を管理し無効化する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/manage-grounding-with-bing |
| Foundry エージェントで長期メモリを作成・管理する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/memory-usage |
| Azure API Center でプライベートツールカタログを構成する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/private-tool-catalog |
| MCP ベースのカスタム code interpreter 環境を構成する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/custom-code-interpreter |
| Foundry エージェントで画像生成ツールを構成して使う | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/image-generation |
| 既存 Azure リソースを使うよう Foundry Agent Service を構成する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/use-your-own-resources |
| VS Code で宣言型エージェントワークフローを構成する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/vs-code-agents-workflow-low-code |
| ホスト型 Foundry エージェントワークフローを作成・デプロイする | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/vs-code-agents-workflow-pro-code |
| Foundry の組み込み評価器一覧を参照する | https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators |
| エージェント専用評価器で AI エージェントを評価する | https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators |
| Foundry でカスタム評価器を作成・構成する | https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/custom-evaluators |
| 汎用評価器（coherence、fluency）を構成する | https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/general-purpose-evaluators |
| groundedness と completeness のための RAG 評価器を構成する | https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators |
| Foundry でリスクと安全性の評価器を構成する | https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators |
| テキスト類似度評価器とメトリクスを使う | https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/textual-similarity-evaluators |
| Foundry で API Management と AI Gateway を有効化する | https://learn.microsoft.com/en-us/azure/foundry/configuration/enable-ai-api-management-gateway-portal |
| Foundry Control Plane にカスタムエージェントを登録する | https://learn.microsoft.com/en-us/azure/foundry/control-plane/register-custom-agent |
| Foundry で合成データ生成を構成する | https://learn.microsoft.com/en-us/azure/foundry/fine-tuning/data-generation |
| Foundry Models のエンドポイントと認証を正しく使う | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/endpoints |
| Responses API を使って Foundry Models でテキスト生成する | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/generate-responses |
| Foundry モデルデプロイ向けに Azure Monitor を構成する | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/monitor-models |
| Foundry で Anthropic Claude モデルをデプロイして呼び出す | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-claude |
| Foundry のガードレールと安全制御を構成する | https://learn.microsoft.com/en-us/azure/foundry/guardrails/how-to-create-guardrails |
| エージェント向け Task Adherence シグナルを構成する | https://learn.microsoft.com/en-us/azure/foundry/guardrails/task-adherence |
| Microsoft Foundry 向けに BYO ストレージを構成する | https://learn.microsoft.com/en-us/azure/foundry/how-to/bring-your-own-azure-storage-foundry |
| 顧客管理ストレージを Foundry Speech と Language に関連付ける | https://learn.microsoft.com/en-us/azure/foundry/how-to/bring-your-own-azure-storage-speech-language-services |
| Microsoft Foundry プロジェクトで接続を追加・構成する | https://learn.microsoft.com/en-us/azure/foundry/how-to/connections-add |
| Microsoft Foundry プロジェクトを作成・構成する | https://learn.microsoft.com/en-us/azure/foundry/how-to/create-projects |
| Foundry で Fireworks モデルを有効化して構成する | https://learn.microsoft.com/en-us/azure/foundry/how-to/fireworks/enable-fireworks-models |
| Foundry でカスタム Fireworks モデルをインポートしてデプロイする | https://learn.microsoft.com/en-us/azure/foundry/how-to/fireworks/import-custom-models |
| Foundry のエージェントトレースとテレメトリを理解する | https://learn.microsoft.com/en-us/azure/foundry/observability/concepts/trace-agent-concept |
| Agent Monitoring Dashboard で Foundry エージェントを監視する | https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard |
| Foundry で LangChain、LangGraph、SK のトレースを構成する | https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-framework |
| Foundry エージェント向け OpenTelemetry トレースをセットアップする | https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-setup |
| Foundry Models で Azure OpenAI v1 API を使う | https://learn.microsoft.com/en-us/azure/foundry/openai/api-version-lifecycle |
| Foundry ガードレール向けに Prompt Shields を構成する | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-prompt-shields |
| Foundry モデル向けに優先処理を有効化して構成する | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/priority-processing |
| Azure OpenAI の DALL-E プロンプト変換を理解して構成する | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/prompt-transformation |
| Foundry で Azure OpenAI のチャット補完モデルを呼び出す | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/chatgpt |
| Azure OpenAI の画像モデルで画像を生成・編集する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/dall-e |
| Responses API 経由で o3-deep-research を使った深い調査を実行する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/deep-research |
| Azure OpenAI で埋め込みを生成して使う | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/embeddings |
| Azure OpenAI 向け DPO ファインチューニングを構成する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning-direct-preference-optimization |
| Azure OpenAI で function calling を構成して使う | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/function-calling |
| Azure OpenAI のビジョン対応チャットモデルを呼び出す | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/gpt-with-vision |
| Azure OpenAI チャット補完の JSON mode を有効化して調整する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/json-mode |
| Chat API で Foundry モデルルーターを構成して呼び出す | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/model-router |
| predicted outputs を使って Azure OpenAI のレイテンシを削減する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/predicted-outputs |
| Foundry でプロビジョンドデプロイを作成して調整する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-get-started |
| 複雑なタスク向けに Azure OpenAI の推論モデルを呼び出す | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/reasoning |
| ツールとストリーミング付きで Azure OpenAI Responses API を使う | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses |
| Azure OpenAI で structured outputs による JSON schema を強制する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs |
| Azure OpenAI Responses API の web search tool を構成する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/web-search |
| Foundry で Azure OpenAI モデルデプロイを扱う | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/working-with-models |
| Azure Monitor データで Foundry OpenAI を監視する | https://learn.microsoft.com/en-us/azure/foundry/openai/monitor-openai-reference |

### 統合と実装パターン
| トピック | URL |
|-------|-----|
| SDK を使ってエージェント、会話、レスポンスを実装する | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components |
| エンタープライズ AI gateway を Foundry Agent Service に接続する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/ai-gateway |
| Foundry エージェントを Foundry IQ ナレッジベースに接続する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/foundry-iq-connect |
| Responses API プロトコル経由で Foundry Agent Applications を呼び出す | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-responses |
| Agent2Agent エンドポイントをツールとして追加・構成する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/agent-to-agent |
| Azure AI Search インデックスを Foundry エージェントに接続する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/ai-search |
| Azure Speech MCP ツールを Foundry エージェントに統合する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/azure-ai-speech |
| エージェントで Grounding with Bing Search ツールを使う | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/bing-tools |
| Browser Automation ツールで Web ブラウジングを自動化する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/browser-automation |
| Foundry エージェントで Code Interpreter ツールを使う | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/code-interpreter |
| Microsoft Fabric の data agent を Foundry に統合する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/fabric |
| エージェント向けに file search tool と vector store を構成する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/file-search |
| Foundry エージェントをツール経由で MCP サーバーに接続する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol |
| SharePoint コンテンツで Foundry エージェントをグラウンディングする | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/sharepoint |
| エージェントで web search tool を構成して使う | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/web-search |
| Foundry SDK で Azure OpenAI graders を使う | https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/azure-openai-graders |
| `azd` 拡張でファインチューニングジョブを実行する | https://learn.microsoft.com/en-us/azure/foundry/fine-tuning/fine-tune-cli |
| Foundry で Claude Code CLI と VS Code を構成する | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/configure-claude-code |
| Foundry Models で DeepSeek-R1 をデプロイして呼び出す | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/tutorials/get-started-deepseek-r1 |
| エージェントワークフローに Task Adherence チェックを適用する | https://learn.microsoft.com/en-us/azure/foundry/guardrails/how-to-task-adherence |
| Foundry にサードパーティの安全性ツールを統合する | https://learn.microsoft.com/en-us/azure/foundry/guardrails/third-party-integrations |
| Foundry SDK でクラウドバッチ評価を実行する | https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/cloud-evaluation |
| LangChain と LangGraph を Foundry に統合する | https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/langchain |
| Foundry Agent Service で LangGraph エージェントを構築する | https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/langchain-agents |
| Foundry の長期メモリを LangChain アプリに追加する | https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/langchain-memory |
| Foundry モデルデプロイを LangChain と組み合わせて使う | https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/langchain-models |
| Foundry と Azure Monitor で LangChain アプリをトレースする | https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/langchain-traces |
| クラウドで AI Red Teaming Agent スキャンを実行する | https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-ai-red-teaming-cloud |
| SDK でローカル AI Red Teaming スキャンを実行する | https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-scans-ai-red-teaming-agent |
| Foundry エンドポイントを外部アプリケーションと統合する | https://learn.microsoft.com/en-us/azure/foundry/how-to/integrate-with-other-apps |
| Microsoft Foundry 向け Azure Key Vault 接続をセットアップする | https://learn.microsoft.com/en-us/azure/foundry/how-to/set-up-key-vault-connection |
| サンプルプロンプトとともに Foundry MCP Server ツールを使う | https://learn.microsoft.com/en-us/azure/foundry/mcp/available-tools |
| Foundry 向けカスタム MCP サーバーを構築して登録する | https://learn.microsoft.com/en-us/azure/foundry/mcp/build-your-own-mcp-server |
| VS Code を Foundry MCP Server に接続する | https://learn.microsoft.com/en-us/azure/foundry/mcp/get-started |
| API 経由で Azure OpenAI の音声モデルを呼び出す | https://learn.microsoft.com/en-us/azure/foundry/openai/audio-completions-quickstart |
| Foundry OpenAI REST API の authoring 操作 | https://learn.microsoft.com/en-us/azure/foundry/openai/authoring-reference-preview |
| Foundry OpenAI で groundedness 検出を使う | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-groundedness |
| Codex CLI と VS Code を Azure OpenAI と統合する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex |
| SDK と REST で Foundry モデルをファインチューニングする | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning |
| Azure OpenAI で tool calling の挙動をファインチューニングする | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning-functions |
| 低レイテンシ音声向けに GPT Realtime API を統合する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/realtime-audio |
| SIP 経由で GPT Realtime API を使う | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/realtime-audio-sip |
| WebRTC 経由で GPT Realtime API を使う | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/realtime-audio-webrtc |
| WebSockets 経由で GPT Realtime API を使う | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/realtime-audio-websockets |
| Foundry で Azure OpenAI Webhook をセットアップして保護する | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/webhooks |
| Foundry における Azure OpenAI v1 REST API と統合する | https://learn.microsoft.com/en-us/azure/foundry/openai/latest |
| Foundry における Azure OpenAI v1 REST API と統合する | https://learn.microsoft.com/en-us/azure/foundry/openai/latest |
| Foundry における Azure OpenAI v1 REST API と統合する | https://learn.microsoft.com/en-us/azure/foundry/openai/latest |
| Foundry における Azure OpenAI v1 REST API と統合する | https://learn.microsoft.com/en-us/azure/foundry/openai/latest |
| Foundry における Azure OpenAI v1 REST API と統合する | https://learn.microsoft.com/en-us/azure/foundry/openai/latest |
| Foundry における Azure OpenAI v1 REST API と統合する | https://learn.microsoft.com/en-us/azure/foundry/openai/latest |
| Foundry における Azure OpenAI v1 REST API と統合する | https://learn.microsoft.com/en-us/azure/foundry/openai/latest |
| Foundry における Azure OpenAI v1 REST API と統合する | https://learn.microsoft.com/en-us/azure/foundry/openai/latest |
| Foundry における Azure OpenAI v1 REST API と統合する | https://learn.microsoft.com/en-us/azure/foundry/openai/latest |
| Foundry OpenAI のリアルタイム音声イベントを実装する | https://learn.microsoft.com/en-us/azure/foundry/openai/realtime-audio-reference |
| Foundry で Azure OpenAI 推論 REST API を呼び出す | https://learn.microsoft.com/en-us/azure/foundry/openai/reference |
| Foundry OpenAI preview 推論 REST API を使う | https://learn.microsoft.com/en-us/azure/foundry/openai/reference-preview |
| Foundry OpenAI v1 preview REST エンドポイントを呼び出す | https://learn.microsoft.com/en-us/azure/foundry/openai/reference-preview-latest |
| Azure OpenAI embeddings API でドキュメント検索を構築する | https://learn.microsoft.com/en-us/azure/foundry/openai/tutorials/embeddings |
| 音声テキスト変換に Azure OpenAI Whisper を使う | https://learn.microsoft.com/en-us/azure/foundry/openai/whisper-quickstart |
| プロジェクト向け Microsoft Foundry REST API を呼び出す | https://learn.microsoft.com/en-us/azure/foundry/reference/foundry-project |
| Microsoft Foundry Project REST API（preview）を使う | https://learn.microsoft.com/en-us/azure/foundry/reference/foundry-project-rest-preview |

### デプロイ
| トピック | URL |
|-------|-----|
| Foundry Agent Service 向け基盤をセットアップする | https://learn.microsoft.com/en-us/azure/foundry/agents/environment-setup |
| Foundry エージェントを Agent 365 のデジタルワーカーとしてデプロイする | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/agent-365 |
| カスタムホスト型エージェントを Foundry Agent Service にデプロイする | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent |
| ホスト型エージェントデプロイのライフサイクルを管理する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/manage-hosted-agent |
| Foundry エージェントを管理対象 Azure リソースとして公開する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-agent |
| Foundry エージェントを Microsoft 365 Copilot と Teams に公開する | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-copilot |
| コンテナ化したホスト型エージェントを Foundry にデプロイする | https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-hosted-agent |
| Azure CLI と Bicep テンプレートで Foundry Models をデプロイする | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/create-model-deployments |
| 推論向けに Foundry portal から Foundry Models をデプロイする | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/deploy-foundry-models |
| Bicep を使って Microsoft Foundry リソースをデプロイする | https://learn.microsoft.com/en-us/azure/foundry/how-to/create-resource-template |
| Terraform IaC テンプレートで Foundry をプロビジョニングする | https://learn.microsoft.com/en-us/azure/foundry/how-to/create-resource-terraform |
| Azure DevOps パイプラインで Foundry 評価を実行する | https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluation-azure-devops |
| GitHub Actions CI で Foundry 評価を実行する | https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluation-github-action |
| Foundry ホスティング上にファインチューニング済みモデルをデプロイする | https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning-deploy |
| Foundry の機能とモデルのリージョン別可用性を確認する | https://learn.microsoft.com/en-us/azure/foundry/reference/region-support |
```

## 【公式推奨】Learn MCP Serverの利用

先ほど`Skills`の中身を確認した通り、内容は`何をどのように検索するか`という指示になっています。  
なので、`Agent Skills`加えて、実際に情報を取得する際は、公式では`Learn MCP Server`の利用を推奨してます。

* `Learn MCP Server` には、`Microsoft Learn`コンテンツに対する検索、フェッチ、コード サンプルの取得などのツールが用意されています
* `Agent Skills`は知識を提供します。何を検索し、いつ、どのように 適用するかに関する構造化されたガイダンス

`Learn MCP Server`を利用する事により、最新のコンテンツ取得、より信頼性の高い情報を取得できるようです！

ちなみに、`Learn MCP Server`を利用できなくても、AIエージェントに組み込まれているWebフェッチ機能があるので、MCPサーバーが利用できなくても大丈夫です！

# まとめ

今回、Agent SkillsのようなAIの活用方法を一度立ち止まって学ぶことで、業務や開発のパフォーマンスを大きく向上できると感じました。

最近はAIを前提とした業務・開発のスタイルが当たり前になりつつあり、実装だけでなく調査・設計・ドキュメント作成なども含めてスピードがどんどん上がっています。

その中で、AIの活用方法を理解していないと、そのスピードについていくこと自体が難しくなると感じたため、今後は意識的にAIを活用した開発スタイルを身につけていきたいと思います！

引き続き、AI・アプリケーション開発・Azureの知識もそうですが、AIの活用方法でも  
周りの方に置いていかれないようキャッチアップ頑張っていきます💪
