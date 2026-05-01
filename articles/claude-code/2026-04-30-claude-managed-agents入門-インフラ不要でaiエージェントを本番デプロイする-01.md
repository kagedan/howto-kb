---
id: "2026-04-30-claude-managed-agents入門-インフラ不要でaiエージェントを本番デプロイする-01"
title: "Claude Managed Agents入門 — インフラ不要でAIエージェントを本番デプロイする"
url: "https://zenn.dev/kai_kou/articles/202-claude-managed-agents-deploy-guide"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-04-30"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

## はじめに

2026年4月9日、Anthropicは **Claude Managed Agents** をパブリックベータとして公開しました。

AIエージェントを本番環境で運用する際、開発者はサンドボックス構築・状態管理・ツール実行・認証情報の安全な取り回しなど、モデル本来の機能とは無関係なインフラ課題に多大な時間を費やしてきました。Claude Managed Agentsはこれらを丸ごとAnthropicのクラウド基盤が引き受けるサービスです。

### この記事で解説すること

* Claude Managed Agentsの概要とアーキテクチャ
* Python SDK を使ったクイックスタート
* 組み込みツールの種類と使い分け
* マルチエージェント構成の概要
* 料金体系と従来手法との比較

### 対象読者

* AIエージェントの開発・本番運用を検討しているエンジニア
* Claude APIを使ったエージェント構築に興味がある方
* 自前インフラでのエージェント運用に課題を感じている方

### 前提条件

* Anthropic APIキーの取得済み
* Python 3.10以上

---

## TL;DR

* Claude Managed Agentsは**エージェント実行インフラをAnthropic側で管理**するサービス
* サンドボックス実行・状態管理・MCP連携・トレーシングが最初から使える
* PythonのClaude Agent SDKで数行のコードからエージェントを起動できる
* 料金はトークン料金（通常レート）＋**$0.08/セッション実行時間**
* マルチエージェント・永続メモリはリサーチプレビュー段階

---

## Claude Managed Agentsとは

Claude Managed Agentsは、Anthropicが提供する**クラウドホスト型のエージェント実行プラットフォーム**です。

従来のエージェント開発では、開発者自身が以下を実装・管理する必要がありました:

* サンドボックス環境の構築・維持
* エージェントの状態（コンテキスト）の永続化
* ツール実行の権限管理・セキュリティ境界
* エラーリカバリーと再起動ロジック
* 実行ログ・トレーシング基盤

Claude Managed Agentsはこれらをすべて提供し、開発者は**エージェントの「何をするか」に集中できる**設計になっています。Anthropic社内テストでは、プロトタイプから本番投入までのリードタイムを**最大10倍短縮**できると報告されています。

### 早期採用企業の活用事例

パブリックベータに参加した企業の活用例を以下に示します:

| 企業 | 活用領域 |
| --- | --- |
| Notion | コードオートメーション |
| Rakuten | 生産性ツール連携 |
| Asana | HRプロセス自動化 |
| Vibecode | 開発ワークフロー |
| Sentry | ファイナンス処理 |

---

## アーキテクチャ概要

Anthropicのエンジニアリングブログ「Scaling Managed Agents: Decoupling the brain from the hands」では、アーキテクチャが以下の3層に整理されています:

### Brain（脳）

LLMと制御ロジックを担当します。エージェントの**判断・推論・ツール選択**がここで行われます。Claudeモデル（Opus 4.6 / Sonnet 4.6）が思考を実行し、次に呼び出すツールを決定します。

### Hands（手）

サンドボックス実行環境です。Brainが指示したツール（ファイル操作・コード実行・Webアクセスなど）が**セキュアな環境で実際に実行**されます。ツールへのインターフェースは統一されており、名前と入力を渡すと文字列が返る設計になっています。

### Session（セッション）

**追記専用のイベントログ**です。エージェントが行ったすべての思考・ツール呼び出し・観察結果が記録され、エージェントの外部メモリとして機能します。セッションをまたいでコンテキストを参照したい場合は、過去のセッションIDを指定できます。

---

## クイックスタート

### インストール

```
pip install claude-agent-sdk
```

### エージェントの作成

エージェントは**再利用可能なバージョン管理された設定**です。モデル・システムプロンプト・利用可能なツール・MCPサーバーを定義します。

```
import anthropic

client = anthropic.Anthropic()

# エージェントを作成
agent = client.beta.managed_agents.agents.create(
    name="my-research-agent",
    model="claude-sonnet-4-6",
    system_prompt="""あなたは調査エージェントです。
与えられたトピックについてWebを検索し、
日本語で要約レポートを作成してください。""",
    tools=[{"type": "agent_toolset_20260401"}],  # フルツールセット（型名は公式ドキュメントで確認）
    betas=["managed-agents-2026-04-01"],
)

print(f"Agent ID: {agent.id}")
```

### セッションの開始と実行

```
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def run_agent():
    options = ClaudeAgentOptions(
        agent_id="your-agent-id",            # 上記で作成したエージェントID
        permission_mode="auto",              # ツール実行を自動承認
    )

    # エージェントを実行し、ストリームで結果を受け取る
    async for message in query(
        prompt="量子コンピューターの2026年最新動向を調査してまとめてください",
        options=options,
    ):
        if message.type == "text":
            print(message.text, end="", flush=True)
        elif message.type == "tool_use":
            print(f"\n[ツール実行: {message.name}]")

asyncio.run(run_agent())
```

### REST APIを直接使う場合

Python SDKを使わず、REST APIを直接呼び出す場合のサンプルです:

```
# セッションの作成
curl https://api.anthropic.com/v1/sessions \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "content-type: application/json" \
  -d '{
    "agent_id": "your-agent-id",
    "initial_prompt": "量子コンピューターの2026年最新動向を調査してまとめてください"
  }'
```

---

## 組み込みツール一覧

Claude Managed Agentsで利用できる組み込みツールを以下に示します:

| ツール | 用途 | 有効化方法 |
| --- | --- | --- |
| `bash` | シェルコマンドの実行 | フルツールセット指定 または個別指定 |
| `file_operations` | ファイルの読み書き・編集 | 同上 |
| `web_search` | Web検索（$10/1,000回） | 同上 |
| `code_execution` | Pythonコードの実行 | 同上 |
| MCP server | 外部サービス連携 | `mcp_connector` で個別設定 |
| Claude Agent Skills | 再利用可能なスキル定義 | `skills` パラメータで指定 |

フルツールセットを指定するとすべての組み込みツールが一括で有効になります。正確なツールタイプ名は[公式ドキュメント（Tools）](https://platform.claude.com/docs/en/managed-agents/tools)で確認してください。特定のツールだけを使いたい場合は個別に指定できます:

```
# 特定のツールだけ有効化する場合
agent = client.beta.managed_agents.agents.create(
    name="code-only-agent",
    model="claude-sonnet-4-6",
    system_prompt="コード実行とファイル操作のみを行うエージェントです。",
    tools=[
        {"type": "code_execution"},
        {"type": "file_operations"},
    ],
    betas=["managed-agents-2026-04-01"],
)
```

---

## マルチエージェント構成（リサーチプレビュー）

マルチエージェント機能は現在**リサーチプレビュー**段階です。

公式ドキュメントのMultiagent sessionsページによると、**オーケストレーター・ワーカーパターン**が基本設計となっています:

* **オーケストレーター**: タスクを受け取り、分析・戦略立案・サブエージェントへの委譲を担当（Claude Opus 4.6を推奨）
* **ワーカーエージェント**: 特定のサブタスクを並列処理（Claude Sonnet 4.6を推奨）

Anthropicの社内リサーチシステムでの評価では、マルチエージェント構成（Opus 4.6 + Sonnet 4.6）は単一エージェント（Opus 4.6のみ）と比較して**90.2%高いスコア**を記録し、複雑なクエリの処理時間を**最大90%短縮**できたとされています。

### リサーチプレビュー中の機能

以下の機能はリサーチプレビューとして限定公開されています:

| 機能 | 説明 |
| --- | --- |
| Multiagent sessions | 複数エージェントの協調実行 |
| Memory tooling | セッションをまたいだ永続メモリ |
| Outcomes | エージェントが自己評価し反復改善する仕組み |

リサーチプレビューへのアクセスは、Anthropicの公式ドキュメントから申請できます。

---

## 料金体系

Claude Managed Agentsの料金は**2つの課金軸**で構成されています:

### 1. トークン料金（標準レート）

| モデル | 入力 | 出力 |
| --- | --- | --- |
| Claude Opus 4.6 | $5.00/MTok | $25.00/MTok |
| Claude Sonnet 4.6 | $3.00/MTok | $15.00/MTok |

（MTok = 100万トークン）

### 2. セッション実行時間

**$0.08/エージェント実行時間（時間課金）**

* 実行時間はミリ秒単位で計測
* セッションの status が `running` の間のみ課金対象
* **ユーザーの返信待ち・アイドル状態・終了後は非課金**

### 3. オプション: Web検索

$10.00 / 1,000回の検索呼び出し

### コスト見積もり例

軽量なリサーチタスク（Sonnet 4.6、入力10万トークン・出力2万トークン・実行時間5分）の場合:

* トークン料金: $0.30（入力）+ $0.30（出力）= $0.60
* 実行時間料金: $0.08 × (5/60) ≈ $0.007
* **合計: 約$0.61**

---

## 従来のエージェント実装との比較

| 比較項目 | 従来（自前実装） | Claude Managed Agents |
| --- | --- | --- |
| セットアップ | サンドボックス構築が必要 | 不要（Anthropic管理） |
| 状態管理 | 独自実装が必要 | Session（イベントログ）が自動提供 |
| ツール実行 | 権限・セキュリティを自前で設計 | 組み込みツールが即利用可能 |
| MCP連携 | 個別に実装・管理 | `mcp_connector` で設定のみ |
| トレーシング | 独自のログ基盤が必要 | Claude Consoleでエンドツーエンド可視化 |
| スケーリング | インフラ設計・構築が必要 | Anthropicが自動スケール |
| デプロイ期間 | 数ヶ月単位 | 数日単位（社内比10倍高速） |

---

## まとめ

Claude Managed Agentsの主なポイントをまとめます:

* **インフラ管理不要**: サンドボックス・状態管理・スケーリングをAnthropicが担当
* **すぐに使える組み込みツール**: bash・ファイル操作・Web検索・コード実行が初期から利用可能
* **セッション = 追記専用イベントログ**: エージェントの外部メモリとして機能し、長時間タスクに対応
* **MCP・Agent Skills対応**: 既存のMCPサーバーやスキル定義をそのまま流用できる
* **料金はトークン＋$0.08/実行時間**: アイドル時間は課金されない合理的な設計
* **マルチエージェントはリサーチプレビュー**: 本番投入前に設計・テストを検討する段階

エージェント開発の「インフラ課題」から解放され、ビジネスロジックの設計と品質向上に集中できる点が最大のメリットです。パブリックベータ中は機能追加・変更が続く可能性があるため、リリースノートの継続的なチェックを推奨します。

## 参考リンク
