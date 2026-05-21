---
id: "2026-05-21-claude-for-legal入門-法務aiの12プラグインとmanaged-agents-api-01"
title: "Claude for Legal入門 — 法務AIの12プラグインとManaged Agents APIの実装ガイド"
url: "https://qiita.com/kai_kou/items/056b61e90311c15f4768"
source: "qiita"
category: "claude-code"
tags: ["CLAUDE-md", "MCP", "API", "AI-agent", "cowork", "Python"]
date_published: "2026-05-21"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

![Claude for Legal の全体像 — 法務ワークフローとMCPコネクタの連携](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-for-legal-mcp-plugins-api-guide/01-hero.png)

## はじめに

Anthropicは2026年5月12日、法律業界向けの包括的なAIソリューション「**Claude for Legal**」を正式ローンチしました。法務部門・法律事務所向けに設計された12の実務プラグインと20以上のMCPコネクタを提供し、契約レビュー・訴訟対応・コンプライアンス管理などの法務ワークフローをClaudeのAIで自動化できます。

### この記事で解説すること

- Claude for Legalの全体アーキテクチャと12のプラグイン
- 20以上のMCPコネクタ（Docusign、iManage、Relativityなど）の活用法
- **Managed Agents API**を使ったPythonによるプログラム実装
- 開発者向けオープンソースリポジトリの活用

### 対象読者

- 法務ワークフロー自動化を検討しているエンジニア
- Claude APIを業務システムに組み込みたい開発者
- Legal Tech系SaaSの開発チーム

### 前提条件

- Python 3.10+
- Anthropic APIキー（Managed Agents API利用可能なアカウント）
- `pip install anthropic`

## TL;DR

- Claude for Legalは12プラグイン＋20+コネクタで法務ワークフローをカバー
- MCPコネクタ経由でDocusign・iManage・Relativityなどの既存システムと連携
- `managed-agents-2026-04-01` ベータヘッダーでManaged Agents APIから呼び出し可能
- OSSリポジトリ `anthropics/claude-for-legal` に実装テンプレートが揃っている

## Claude for Legalの全体像

![Claude for Legal の3層アーキテクチャ — Plugins / Claude / MCPコネクタ](https://raw.githubusercontent.com/kai-kou/zenn-blog-automation/main/images/claude-for-legal-mcp-plugins-api-guide/02-architecture.png)

Claude for Legalは3つのコンポーネントで構成されています。

| コンポーネント | 説明 |
|--------------|------|
| **Practice-Area Plugins** | 実務領域別の12プラグイン。プレイブック・リスク校正を学習 |
| **MCPコネクタ** | 法務SaaSと双方向連携する20以上のコネクタ |
| **実行環境** | Claude Cowork / Microsoft 365 / Managed Agents API |

[公式ブログ](https://claude.com/blog/claude-for-the-legal-industry)では以下のように説明されています。

> "The plugin and skill ecosystem are open protocols, and early contributors including Box, Legal Quants, Lawve AI, and Thomson Reuters have already shipped skills, plugins, and style conventions of their own."
> — [Claude for the Legal Industry](https://claude.com/blog/claude-for-the-legal-industry)（2026-05-12）

## 12の実務領域別プラグイン

各プラグインはセットアップ時のインタビューで組織固有のプレイブック・エスカレーションルール・リスク校正・文体を学習します。

| プラグイン名 | 主な用途 |
|------------|---------|
| **Commercial Legal** | ベンダー契約・NDA・プレイブックレビュー |
| **Corporate Legal** | M&Aデュー・ディリジェンス、開示スケジュール、クロージングチェックリスト |
| **Employment Legal** | 採用・解雇・労働者区分・州別方針 |
| **Privacy Legal** | DPAレビュー・PIA/DPIAトリアージ・DSAR対応 |
| **Product Legal** | ローンチレビュー・マーケティング実証チェック |
| **Regulatory Legal** | 規制動向モニタリング・方針比較・ギャップ追跡 |
| **AI Governance Legal** | ユースケーストリアージ・影響評価・ベンダーAI条項 |
| **IP Legal** | 商標クリアランス・C&D書簡・OSS準拠 |
| **Litigation Legal** | 案件インテーク・リーガルホールド・召喚状トリアージ・ブリーフ起案 |
| **Law Student** | ソクラテス式ドリル・判例ブリーフ・司法試験準備 |
| **Legal Clinic** | クライアントインテーク・期限追跡・スーパーバイザーレビューキュー |
| **Legal Builder Hub** | コミュニティスキルのインストール・管理 |


> Corporate LegalプラグインとLitigation Legalプラグインは、Managed Agents APIからCookbookバージョンとしてプログラム的にデプロイ可能です。


## 20以上のMCPコネクタ

### 契約・文書管理

| コネクタ | 主な機能 |
|---------|---------|
| **Docusign** | 契約データへのアクセス・更新日/義務の抽出・ワークフロー操作 |
| **Ironclad** | パーミッション範囲スコープで契約リポジトリにクエリ |
| **Definely** | ライブ契約構造・定義解決・相互参照バリデーション |
| **iManage** | パーミッション制御されたガバナンスコンテンツとマター履歴へのアクセス |
| **NetDocuments** | ガバナンスを尊重したリポジトリからの文書検索・取得 |

### 電子証拠開示・訴訟

| コネクタ | 主な機能 |
|---------|---------|
| **Relativity** | マター管理・スキーマ設定・RelativityOne分析 |
| **Everlaw** | メタデータとキーワードによる文書検索・レビューリンク |
| **Consilio** | Aurora Legal AI統合によるライブマターアクセス |

### リーガルリサーチ

| コネクタ | 主な機能 |
|---------|---------|
| **Thomson Reuters / CoCounsel** | 受託者責任レベルの起案・調査 |
| **Midpage** | ハイパーリンク付きソース検証の判例データベース |
| **Trellis** | 米国州裁判所データセット（判事・弁護士分析） |
| **Legal Data Hunter** | 160以上の司法管轄から3100万件超のドキュメント |
| **Free Law Project** | CourtListener: 米国判例・PACERドケット・口頭弁論 |

### ディールルーム・トランザクション

| コネクタ | 主な機能 |
|---------|---------|
| **Box** | パーミッション強制付きファイル検索・メタデータ抽出 |
| **Datasite** | バーチャルデータルーム統合・フォルダ管理・文書追跡 |


> すべてのコネクタはユーザーがすでに認可済みのデータのみClaudeがアクセスできる設計です。基盤システムのパーミッション制御はそのまま維持されます。


## Managed Agents APIでの実装

### セットアップ

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Step 1: 法務エージェントの作成

```python
from anthropic import Anthropic

client = Anthropic()

agent = client.beta.agents.create(
    name="Legal Contract Review Agent",
    model="claude-opus-4-7",
    system="""あなたは契約書レビューを専門とする法務AIエージェントです。
    リスクのある条項を特定し、組織のプレイブックに基づいてフラグを立ててください。
    分析は構造化され、引用可能な出典を含めてください。""",
    tools=[
        {"type": "agent_toolset_20260401"},
    ],
)

print(f"Agent ID: {agent.id}, version: {agent.version}")
```


> すべてのManaged Agents APIリクエストには `managed-agents-2026-04-01` ベータヘッダーが必要です。SDKを使用する場合は自動的に付与されます。


### Step 2: 実行環境の設定

```python
environment = client.beta.environments.create(
    name="legal-review-env",
    config={
        "type": "cloud",
        "networking": {"type": "unrestricted"},
    },
)

print(f"Environment ID: {environment.id}")
```

### Step 3: セッションの開始と契約書レビュー

```python
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="NDA Contract Review Session",
)

print(f"Session ID: {session.id}")

# ストリーミングでレビュー実行
with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.message",
                "content": [
                    {
                        "type": "text",
                        "text": """以下のNDA条項をレビューし、リスクのある点をリストアップしてください。
                        特に以下の観点で確認：
                        1. 秘密情報の定義範囲
                        2. 有効期間と残存条項
                        3. 競業避止義務の合理性
                        
                        [契約書テキストをここに挿入]""",
                    },
                ],
            },
        ],
    )

    for event in stream:
        match event.type:
            case "agent.message":
                for block in event.content:
                    print(block.text, end="")
            case "agent.tool_use":
                print(f"\n[ツール実行: {event.name}]")
            case "session.status_idle":
                print("\n\nレビュー完了")
                break
```

### Step 4: スケジュール自動化（規制モニタリング）

`claude-for-legal` リポジトリには、定期実行パターンのCookbookが含まれています。

```python
# 定期的な規制フィードモニタリングエージェント
regulatory_agent = client.beta.agents.create(
    name="Regulatory Feed Monitor",
    model="claude-sonnet-4-6",  # 定常監視にはコスト効率重視
    system="""規制当局のフィードを監視し、組織に影響するアップデートを
    優先度付きで要約してください。月次コンプライアンスレポートを生成します。""",
    tools=[
        {"type": "agent_toolset_20260401"},
    ],
)
```

### モデル選択の指針

| モデル | 推奨ユースケース |
|--------|---------------|
| `claude-opus-4-7` | 複雑な法的分析・長文書推論・M&Aデュー・ディリジェンス |
| `claude-sonnet-4-6` | 契約レビュー・起案自動化・定常的ワークフロー |
| `claude-haiku-4-5` | 高速分類・軽量Q&A・ドキュメントルーティング |

## オープンソースリポジトリの活用

[`anthropics/claude-for-legal`](https://github.com/anthropics/claude-for-legal)には以下のリソースが含まれています。

```
claude-for-legal/
├── plugins/              # 12実務プラグインの定義
├── managed-agent-cookbooks/  # スケジュール自動化テンプレート
│   ├── renewal-watcher/       # 契約更新日監視
│   ├── docket-watcher/        # 訴訟ドケット監視
│   └── regulatory-feed-monitor/  # 規制フィード監視
├── mcp-connectors/       # 各コネクタのセットアップガイド
├── CLAUDE.md             # 実務領域別テンプレート
└── agent.yaml            # エージェント設定ファイル
```

### CLAUDE.mdテンプレートの活用

```yaml
# managed-agent-cookbooks/renewal-watcher/agent.yaml
name: "Contract Renewal Watcher"
model: claude-sonnet-4-6
system: |
  契約の更新日を監視し、期限の60日・30日・7日前にアラートを生成します。
  アクションが必要な場合は責任者へのエスカレーション手順を提示してください。
tools:
  - type: agent_toolset_20260401
mcp_servers:
  - type: ironclad        # 契約リポジトリ
  - type: docusign        # 署名ワークフロー
```

## 注意点

### パーミッション管理

- Claudeがアクセスできるのはユーザーが認可済みのデータのみ
- MCPコネクタは既存システムのアクセス制御をバイパスしない
- エンタープライズデプロイでは AWS IAM認証も利用可能（[Claude Platform on AWS](https://qiita.com/kai_kou/items/placeholder)参照）

### ハルシネーションリスク

法律分野では誤情報のリスクが特に高いです。Anthropicは以下の対策を推奨しています。

- 判例・法令の引用には必ずMCPコネクタ経由の一次ソースを参照
- Midpage コネクタを使用すればハイパーリンク付き出典を自動取得
- 最終判断は必ず資格を持つ法律専門家が行う

### ベータ機能について

Managed Agents APIは現在ベータ提供中です。`managed-agents-2026-04-01` ベータヘッダーが必要で、動作仕様は改善のため変更される可能性があります。

## まとめ

Claude for Legalは法務ワークフローのAI自動化において以下の特徴があります。

- **12のプラグイン**: 実務領域ごとに最適化されたワークフローを提供
- **20以上のMCPコネクタ**: 既存の法務SaaSとシームレスに統合
- **Managed Agents API**: Pythonから4ステップで法務エージェントをデプロイ
- **オープンエコシステム**: OSSリポジトリでカスタム実装が可能

法務部門の定型業務（契約レビュー・規制監視・ドケット管理）の自動化に有効なソリューションです。アクセスは[Claude Cowork](https://claude.com)のPro/Max/Team/Enterpriseプランから利用可能で、非営利法律支援団体向けの割引プログラムも用意されています。

## 参考リンク

- [Claude for the Legal Industry — 公式ブログ](https://claude.com/blog/claude-for-the-legal-industry)（2026-05-12）
- [anthropics/claude-for-legal — GitHub](https://github.com/anthropics/claude-for-legal) — 実装テンプレートとCookbook
- [Managed Agents API Quickstart](https://platform.claude.com/docs/en/managed-agents/quickstart) — APIドキュメント
- [Anthropic Goes All-In on Legal — LawSites](https://www.lawnext.com/2026/05/anthropic-goes-all-in-on-legal-releasing-more-than-20-connectors-and-12-practice-area-plugins-for-claude.html)（2026-05-12）
- [Claude for Legal: 12 Plugins and 80 AI Agents — Legaltech Hub](https://www.legaltechnologyhub.com/contents/anthropic-unveils-claude-for-legal-with-12-new-plugins-20-mcp-connectors-and-more/)
