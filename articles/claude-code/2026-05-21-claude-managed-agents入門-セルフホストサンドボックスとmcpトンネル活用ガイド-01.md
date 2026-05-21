---
id: "2026-05-21-claude-managed-agents入門-セルフホストサンドボックスとmcpトンネル活用ガイド-01"
title: "Claude Managed Agents入門 — セルフホストサンドボックスとMCPトンネル活用ガイド"
url: "https://qiita.com/kai_kou/items/16b4aa9fe3f235d66205"
source: "qiita"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "Python", "qiita"]
date_published: "2026-05-21"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

![Claude Managed Agents enterprise security architecture](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-agents-sandbox-mcp-tunnel-guide/01-hero.png)

## はじめに

2026年5月19日、AnthropicはClaude Managed Agentsに2つの新機能を追加しました。

- **Self-hosted sandboxes（セルフホスト型サンドボックス）**（Beta）
- **MCP tunnels（MCPトンネル）**（Research Preview）

どちらも「AIエージェントにセンシティブなデータや内部システムを扱わせたいが、クラウドにデータを出したくない」という企業ニーズに応える機能です。本記事では公開情報をもとに、これら2機能の設計思想・使い方・ユースケースを解説します。

### この記事で学べること

- Self-hosted Sandboxesの仕組みとアーキテクチャ
- MCP Tunnelsによるプライベートサービス接続の方法
- 対応プロバイダーと選定基準
- 金融・医療・製造業などの規制業界でのユースケース
- Claude Managed Agents APIの基本的な使い方

### 対象読者

- エンタープライズ環境でClaude Managed Agentsの導入を検討しているエンジニア
- AIエージェントのセキュリティ要件を担当するアーキテクト
- MCPサーバーをプライベートネットワーク内に構築したい開発者

### 前提知識

- Claude Managed Agentsの基礎知識
- MCPプロトコルの概要
- Python 3.9以上

## TL;DR

- **Self-hosted sandboxes**: エージェントのオーケストレーションはAnthropicクラウド、ツール実行は企業インフラ内で完結。センシティブなファイルやネットワークトラフィックが外部に出ない
- **MCP tunnels**: 内部MCPサーバーへのアウトバウンドのみの暗号化接続。インバウンドファイアウォールルールが不要でゼロトラスト設計
- 対応プロバイダー: Cloudflare / Daytona / Modal / Vercel
- APIヘッダー: `anthropic-beta: managed-agents-2026-04-01`
- セッション料金: $0.08/session-hour（実行中のみ課金）

![Self-hosted Sandboxアーキテクチャ — オーケストレーションとツール実行の分離](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-agents-sandbox-mcp-tunnel-guide/02-sandbox-architecture.png)

## Self-hosted sandboxesとは

### 従来の課題

Claude Managed Agentsはエージェントのオーケストレーション（コンテキスト管理、エラーリカバリー、ループ制御）とツール実行（ファイル操作、コマンド実行、APIコール）をAnthropicのマネージドインフラで一括処理していました。これはセットアップの手軽さという利点がある反面、センシティブなファイルや内部ネットワークへのアクセスが必要な業務では採用しにくい課題がありました。

### アーキテクチャの分離

Self-hosted sandboxesはこの問題を「オーケストレーションとツール実行を分離する」設計で解決します。

| レイヤー | 実行場所 | 内容 |
|--------|--------|------|
| オーケストレーション | Anthropicクラウド | コンテキスト管理・エラーリカバリー・ループ制御 |
| ツール実行 | 企業インフラ（自社クラウドまたはオンプレ） | ファイル操作・コマンド実行・内部APIコール |

これにより、センシティブなファイルやパッケージが企業ネットワーク外に出ることなく、エージェントが社内リソースを操作できます。

### 技術的な特徴

- **ステートフルな長期実行サンドボックス**: セッションをまたいでファイルシステムの状態を保持
- **カスタムランタイムイメージ**: 企業独自のツールや依存関係を含むコンテナイメージを指定可能
- **フレキシブルなリソースサイジング**: CPU・メモリの割り当てを要件に応じて設定
- **既存セキュリティツールとの統合**: 企業の監査ログ・ネットワークポリシー・SIEMツールと連携

### 対応プロバイダー

| プロバイダー | 特徴 | 適したユースケース |
|-----------|------|----------------|
| **Cloudflare** | MicroVM、カスタムプロキシ、ゼロトラストシークレット管理 | グローバル分散、セキュリティ重視 |
| **Daytona** | ステートフルな長期実行「フルコンポーザブルコンピュータ」 | 長時間実行タスク、開発環境 |
| **Modal** | サブ秒起動、GPUリソース対応 | 機械学習パイプライン、バースト処理 |
| **Vercel** | VPCピアリング、ミリ秒起動 | Webアプリ統合、低レイテンシ |

### 現時点での制限事項

公式ドキュメントによると、以下はまだ対応していません。


> - **Claude Platform on AWS** ではself-hosted sandboxesは未対応
> - **Memoryフィーチャー**はself-hosted sandboxesと組み合わせた場合に未サポート


## MCP tunnelsとは

### 背景: 内部MCPサーバーへのアクセス問題

MCPサーバーを企業のプライベートネットワーク内に構築した場合、外部のClaudeエージェントからアクセスするには従来、以下のような問題がありました。

- パブリックエンドポイントを用意する必要がある → セキュリティリスク
- VPN経由でアクセスする → 設定の複雑さ
- インバウンドのファイアウォールルールを開ける → セキュリティ審査が必要

MCP tunnelsはこれらの問題を「アウトバウンドのみの単一暗号化接続」で解決します。

![MCP Tunnelフロー図 — アウトバウンドのみの暗号化接続](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-agents-sandbox-mcp-tunnel-guide/03-mcp-tunnel-flow.png)

### 仕組み

```
企業内部ネットワーク
┌─────────────────────────────────────────────┐
│  Internal DB  →  MCP Server  →  Tunnel GW  │
└─────────────────────────────────────────────┘
                                    │
                          (アウトバウンド暗号化接続)
                                    │
                            Anthropic Cloud
                                    │
                           Claude Managed Agent
```

- **ゲートウェイ**: 企業ネットワーク内に軽量ゲートウェイをデプロイ
- **アウトバウンド接続のみ**: インバウンドのファイアウォールルール変更は不要
- **エンドツーエンド暗号化**: ゼロトラストアーキテクチャで通信を保護
- **単一接続**: 1つのトンネルにつき1つのアウトバウンド接続

### 接続可能な内部サービス例

- 内部データベース（PostgreSQL、MySQL、社内Elasticsearch等）
- プライベートAPI（社内マイクロサービス、ERP、MES等）
- 社内ナレッジベース（Confluence、社内Wiki等）
- チケットシステム（社内Jira、ServiceNow等）
- カスタムMCPサーバー（社内業務ロジックをラップしたもの等）

### 利用可能なAPI

公式ドキュメントによると、MCP tunnelsはManaged AgentsとMessages API両方で利用可能です。

## APIの使い方

Claude Managed AgentsのAPIはすべて `anthropic-beta: managed-agents-2026-04-01` ヘッダーを付与して呼び出します。

### セルフホストサンドボックスを使ったセッション作成（Pythonサンプル）

公式ドキュメント（[Quickstart](https://platform.claude.com/docs/en/managed-agents/quickstart)・[Self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes)）に基づいた実装例です。Claude Managed Agentsは **Agent → Environment → Session** の3オブジェクトで構成されます。

```python
import anthropic

client = anthropic.Anthropic()

# Step 1: Agentを作成（モデル・ツールを定義）
agent = client.beta.agents.create(
    name="enterprise-agent",
    model="claude-opus-4-7",
    tools=[{"type": "agent_toolset_20260401"}],
)

# Step 2: セルフホスト用Environmentを作成
environment = client.beta.environments.create(
    name="self-hosted-env",
    config={
        "type": "self_hosted",
        "provider": "cloudflare",  # cloudflare / daytona / modal / vercel
    },
)

# Step 3: SessionをAgent + Environmentで開始
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
)

print(f"Session ID: {session.id}")
print(f"Status: {session.status}")
```

### MCP tunnels経由でのMessages API呼び出し

MCP tunnelsはManaged AgentsとMessages API両方で利用できます。Messages API経由の場合は `mcp_servers` にトンネルのURLを渡します。

```python
import anthropic

client = anthropic.Anthropic()

# MCP tunnelを介してプライベートサービスへアクセス
response = client.beta.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    mcp_servers=[
        {
            "type": "url",
            "url": "https://your-subdomain.tunnel-domain/mcp",  # トンネルのエンドポイント
            "name": "internal-db-mcp",
        }
    ],
    messages=[
        {"role": "user", "content": "社内データベースの最新レポートを取得してください"}
    ],
    extra_headers={"anthropic-beta": "managed-agents-2026-04-01"}
)
```


> 上記はAPIの基本的な構造を示した例です。実際のトンネルURLの払い出し手順、エラーハンドリング、ストリーミングの実装などの詳細は[公式ドキュメント](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview)を参照してください。


### セッション課金の仕組み

Claude Managed Agentsの料金は以下の2要素で構成されます。

| 課金要素 | 単価 | 備考 |
|--------|------|------|
| トークン使用量 | 通常のClaude APIと同一 | input/output/cache write/read |
| セッション実行時間 | **$0.08/session-hour** | `status = "running"` の間のみ、ミリ秒単位で計測 |

Self-hosted SandboxesやMCP Tunnels自体には追加料金はかかりません。エンタープライズ向けのカスタム料金についてはセールスチームへの問い合わせが推奨されています。

## エンタープライズユースケース

### 金融サービス（FISC安全管理基準・SOX対応）

```
[シナリオ]
社内の取引データ分析エージェントが、本番DBにアクセスして
レポートを自動生成する

[課題]
→ 取引データをAnthropicクラウドに送れない（内部規定）
→ 本番DBをインターネットに公開できない（セキュリティポリシー）

[解決策]
→ Self-hosted Sandbox（Modal or Cloudflare）で実行環境を社内に限定
→ MCP Tunnelで社内DBへのアクセスをセキュアに確立
```

### ヘルスケア（HIPAA準拠）

患者データを含む医療記録へのエージェントアクセスは、PHI（Protected Health Information）のクラウド転送を禁止するHIPAAの要件と競合することがあります。Self-hosted Sandboxesを使えば、エージェントの実行環境を自社のHIPAA準拠インフラ内に閉じ込めることができます。

### 製造業（工場システム連携）

MCP TunnelsによりERP・MES・PLCなどの工場内システムを、インバウンドポートを開けることなくエージェントに接続できます。既存のOTセキュリティポリシーを変更せずにAIエージェントを導入できる点が評価されています。

## 既存のManaged Agents機能との関係

2026年5月時点のClaude Managed Agentsの主な機能を整理します。

| 機能 | ステータス | 概要 |
|------|---------|------|
| Self-hosted sandboxes | **Beta** | セルフホスト型実行環境 |
| MCP tunnels | **Research Preview** | プライベートMCP接続 |
| [Dreaming](https://claude.com/blog/new-in-claude-managed-agents) | Research Preview | 過去セッション学習・メモリ改善 |
| [Outcomes](https://claude.com/blog/new-in-claude-managed-agents) | Public Beta | タスク成功基準の定義・自動再実行 |
| [Multiagent Orchestration](https://claude.com/blog/new-in-claude-managed-agents) | Public Beta | リードエージェントによるサブエージェント委譲 |

## まとめ

- **Self-hosted sandboxes**: オーケストレーション（Anthropicクラウド）とツール実行（企業インフラ）を分離することで、センシティブなデータを外部に出さずにエージェントを運用可能
- **MCP tunnels**: アウトバウンドのみの単一暗号化接続で、社内MCPサーバーへのアクセスをゼロトラスト設計で実現
- どちらも規制業界（金融・医療・製造業）でのAIエージェント導入ハードルを大幅に下げる機能
- APIは `anthropic-beta: managed-agents-2026-04-01` ヘッダーで利用可能
- セッション料金は $0.08/session-hour（実行中のみ）

Claude Managed AgentsはDreaming・Outcomes・Multiagent Orchestrationに続き、エンタープライズセキュリティ面でも着実に機能を拡充しています。社内データの外部転送に制約がある組織でも、これらの機能によりAIエージェントの本格導入が現実的になりつつあります。

## 参考リンク

- [Anthropic: New in Claude Managed Agents: self-hosted sandboxes and MCP tunnels（公式ブログ）](https://claude.com/blog/claude-managed-agents-updates)
- [Claude Managed Agents overview（公式ドキュメント）](https://platform.claude.com/docs/en/managed-agents/overview)
- [Self-hosted sandboxes（公式ドキュメント）](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes)
- [MCP tunnels overview（公式ドキュメント）](https://platform.claude.com/docs/en/agents-and-tools/mcp-tunnels/overview)
- [Anthropic enhances Claude Managed Agents with two new privacy and security features（9to5Mac）](https://9to5mac.com/2026/05/19/anthropic-enhances-claude-managed-agents-with-two-new-privacy-and-security-features/)
- [Managed Agents Quickstart（公式ドキュメント）](https://platform.claude.com/docs/en/managed-agents/quickstart)
