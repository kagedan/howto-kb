---
id: "2026-04-10-microsoft-agent-governance-toolkit入門-aiエージェントのセキュリ-01"
title: "Microsoft Agent Governance Toolkit入門 — AIエージェントのセキュリティをOSSで実装する"
url: "https://zenn.dev/kai_kou/articles/188-microsoft-agent-governance-toolkit-guide"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

## はじめに

AIエージェントの本番運用が広がる中、セキュリティリスクへの対策が急務になっています。企業の88%がAIエージェントのセキュリティインシデントをすでに経験しているという調査もあり、ガバナンスの仕組みを整備しないまま本番運用を続けることは難しくなっています。

2026年4月2日、Microsoftがオープンソースの「**Agent Governance Toolkit**」をリリースしました。[OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)の全10リスクに対応し、LangChain・CrewAI・Google ADKなど主要フレームワークとコードを書き直さずに統合できる設計が特徴です。

本記事では、このツールキットの概要・7つのコンポーネント・実装方法をまとめます。

### この記事で学べること

* OWASP Top 10 for Agentic Applicationsの各リスクとAgent Governance Toolkitの対応方法
* 7つのパッケージの役割と使い分け
* Python/TypeScriptでのポリシー定義と既存フレームワークへの組み込み方

### 対象読者

* LangChain・CrewAI・AutoGen等でAIエージェントを開発しているエンジニア
* AIエージェントの本番運用・セキュリティに関心があるエンジニア

### 前提条件

* Python 3.10 以上（Pythonパッケージを使用する場合）
* Node.js 18 以上（TypeScriptパッケージを使用する場合）

## TL;DR

* **Microsoft Agent Governance Toolkit**: OWASP Top 10 for Agentic Applications全10リスク対応のOSSガバナンス基盤（MIT License）
* **7パッケージ構成**: Agent OS（ポリシーエンジン）・Mesh（ID管理）・Runtime（実行制御）・SRE・Compliance・Marketplace・Lightning
* **サブミリ秒強制**: p99レイテンシ < 0.1ms（LLM API呼び出しの1万分の1）
* **統合方式**: LangChainのコールバック・CrewAIのデコレータ等、既存コードの書き換え不要
* **ポリシー言語**: YAML・OPA Rego・Cedarの3形式に対応

### 背景: AIエージェントが直面するセキュリティ課題

単一のLLM APIコールとは異なり、AIエージェントは「計画→ツール呼び出し→結果評価→再試行」というループを自律的に繰り返します。この自律性が新たな攻撃面を生み出します。

| 課題 | 具体例 |
| --- | --- |
| ゴールハイジャック | プロンプト注入でエージェントの目標を書き換え |
| ツール誤用 | 曖昧な指示でファイル削除コマンドを実行 |
| ID/権限の悪用 | エージェントがユーザー権限を引き継ぎ、意図しないリソースにアクセス |
| マルチエージェントの連鎖障害 | 1エージェントのエラーが全体に伝播 |

これらに対応するため、[OWASP](https://owasp.org/)は2026年に**OWASP Top 10 for Agentic Applications**を策定しました。

### OWASP Top 10 for Agentic Applications

| リスクID | 名称 | 概要 |
| --- | --- | --- |
| ASI01 | Agent Goal Hijack | 悪意あるテキスト注入でエージェントの目標を改変 |
| ASI02 | Tool Misuse and Exploitation | 曖昧な指示により正規ツールを危険な方法で使用 |
| ASI03 | Identity and Privilege Abuse | エージェントがユーザー/システムIDを意図せず引き継ぐ |
| ASI04 | Agentic Supply Chain Vulnerabilities | ツール・プラグイン・MCPサーバーの改ざん |
| ASI05 | Unexpected Code Execution | コード/コマンドをサンドボックスなしで実行 |
| ASI06 | Memory and Context Poisoning | RAGデータベースへの汚染で将来の判断を誘導 |
| ASI07 | Insecure Inter-Agent Communication | マルチエージェント間の認証・暗号化の欠如 |
| ASI08 | Cascading Failures | 小さなエラーが複数エージェントに連鎖 |
| ASI09 | Human-Agent Trust Exploitation | ユーザーのエージェント過信を悪用した情報抽出 |
| ASI10 | Rogue Agents | 正常に見える不正・誤整合エージェントの活動 |

### 設計哲学

MicrosoftはOSや分散システムのパターンをAIエージェントに応用しています。

* **カーネル型権限分離**（OS由来）: エージェントアクションを実行前にインターセプト
* **Mutual TLSとID管理**（サービスメッシュ由来）: Ed25519ベースの暗号化ID
* **SLOベース信頼性**（SRE由来）: エラーバジェットとサーキットブレーカー

```
ガバナンスゲート → トラストゲート → 信頼性ゲート → 実行 → 出力チェック → 監査ログ
```

ガバナンスはオプション追加ではなく、**実行パスに組み込まれる**設計です。

> We designed governance as infrastructure, not as an afterthought. Every agent action passes through the policy engine before execution—there are no bypass paths.  
> — [Microsoft Open Source Blog, April 2, 2026](https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/)

## 7パッケージの構成と役割

### 1. Agent OS（ポリシーエンジン）

エージェントのすべてのアクションを実行前にインターセプトするステートレスなポリシーエンジン。p99レイテンシ0.1ms未満の高速評価が特徴。

* YAML / OPA Rego / Cedarの3形式のポリシーをサポート
* allow/denyルール、トークン上限、ツール呼び出し回数制限

### 2. Agent Mesh（ID管理）

DIDs（Decentralized Identifiers）とEd25519署名を用いた暗号化IDシステム。

* 0〜1000スケールのトラストスコアを各エージェントに付与
* SPIFFE/SVIDによる証明書管理

### 3. Agent Runtime（実行制御）

4段階の権限リング、サガオーケストレーション、緊急停止機能を提供。

* 実行権限をリングごとに分離（OSのプロセスリングと同概念）
* 長時間タスクをサガパターンでロールバック可能に

### 4. Agent SRE（信頼性）

AIエージェント向けのSLO管理、エラーバジェット、サーキットブレーカー。

* エラー率が高いエージェントを自動的に一時停止
* SLOダッシュボードへのメトリクスエクスポート

### 5. Agent Compliance（コンプライアンス）

EU AI Act・HIPAA・SOC2へのマッピングとコンプライアンス証跡を自動生成。

* コンプライアンスグレードの自動算出
* 監査に必要な証拠ファイルをエクスポート

### 6. Agent Marketplace（プラグイン管理）

Ed25519署名によるプラグインのライフサイクル管理。

* マニフェスト検証と信頼ティア別の機能ゲーティング
* ASI04（サプライチェーン）リスクへの直接対応

### 7. Agent Lightning（RL学習制御）

強化学習ワークフローにポリシーを適用し、学習段階からの逸脱を防止。

## インストールと基本的な使い方

### インストール

```
# Python（全パッケージ）
pip install agent-governance-toolkit[full]

# TypeScript/Node.js
npm install @agentmesh/sdk

# .NET
dotnet add package Microsoft.AgentGovernance
```

### ポリシーの定義（YAML）

最もシンプルなYAML形式から始めることが推奨されています。

```
version: "1.0"
default_action: deny

rules:
  - name: "Allow Safe Web Search"
    condition: tool_name == "web_search"
    action: allow
    priority: 100

  - name: "Block Destructive File Operations"
    condition: tool_name in ["file_write", "file_delete"]
    action: deny
    priority: 50

governance:
  enabled: true
  max_tokens_per_task: 8000
  max_tool_calls_per_task: 20
  max_files_changed: 15
  policy_mode: "strict"    # strict | permissive | audit

  blocked_patterns:
    - "rm -rf /"
    - "DROP TABLE"
    - "DELETE FROM"
    - "TRUNCATE"
```

`policy_mode: "audit"` から始めて実際の呼び出しパターンを把握し、`permissive` → `strict` と段階的に移行するアプローチが推奨されています。

### PolicyEngineの基本使用（Python）

```
from agent_os import PolicyEngine, CapabilityModel

# ポリシーエンジンを初期化
engine = PolicyEngine(capabilities=CapabilityModel(
    allowed_tools=["web_search", "file_read"],
    denied_tools=["file_write", "shell_exec"],
))

# エージェントアクションを実行前に評価
decision = engine.evaluate(
    agent_id="researcher-1",
    action="tool_call",
    tool="web_search"
)

if decision.allowed:
    # ツール呼び出しを実行
    result = tool.call()
else:
    # ポリシー違反として記録・ブロック
    logger.warning(f"Blocked: {decision.reason}")
```

### OPA Regoポリシー（複雑なロジック向け）

```
package agent_governance

# ロール別のアクセス制御
allow {
    input.tool_name == "web_search"
    input.agent_role == "researcher"
}

deny {
    input.action == "delete"
    input.resource_type == "production_data"
}
```

### Cedarポリシー（AWS環境向け）

```
permit (
    principal == Agent::"analyst-1",
    action == Tool::call,
    resource == Tool::"data_query"
)
when {
    resource.sensitivity_level < 3
};
```

## 既存フレームワークへの統合

コードを書き直さずにガバナンスを追加できることが設計上の重要な原則です。

### LangChainへの統合

LangChainのコールバックシステムを通じてガバナンスを注入します。

```
from langchain.agents import AgentExecutor
from agent_governance import LangChainGovernanceHandler

# ガバナンスコールバックを追加するだけで統合完了
governance_callback = LangChainGovernanceHandler()

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=[governance_callback]  # 既存コードへの変更はここだけ
)
```

### CrewAIへの統合

CrewAIのタスクデコレータを用いて統合します。

```
from crewai import Task
from agent_governance import governed_task

# デコレータを追加するだけでガバナンスが有効になる
@governed_task()
def research_task():
    """ガバナンスが自動適用されるタスク"""
    pass
```

### 対応フレームワーク一覧

| フレームワーク | 統合方式 |
| --- | --- |
| LangChain | コールバックハンドラ |
| CrewAI | タスクデコレータ |
| Google ADK | プラグインシステム |
| Microsoft Agent Framework | ミドルウェアパイプライン |
| AutoGen | メッセージフック |
| LangGraph | ステップインターセプタ |
| PydanticAI | ランタイムフック |
| OpenAI Agents SDK | 統合対応済み |

## 本番導入の実績

[11エージェントを11日間稼働させた事例](https://medium.com/@isiddique/running-11-ai-agents-in-production-how-the-agent-governance-toolkit-secures-our-workflows-10a6399638fc)では、以下の結果が報告されています。

| 指標 | 値 |
| --- | --- |
| ブロックされたアクション数 | 473件 |
| ブロック内容 | 破壊的コマンド・SQLインジェクション・トークンオーバーフロー |
| 強制レイテンシ（最大値） | 8ms以下 |
| 合計オーバーヘッド | 0.43秒 |

ガバナンスによるオーバーヘッドが非常に小さいことが確認できます。

## まとめ

Microsoft Agent Governance Toolkitのポイントを整理します。

* **OWASP Top 10 for Agentic Applications全10リスク**に対応する唯一のOSSツールキット
* **ゼロコード書き換え**: コールバック・デコレータ等の既存拡張ポイントで統合
* **サブミリ秒強制**: p99 < 0.1msにより本番パフォーマンスへの影響は軽微
* **段階的導入**: `audit` → `permissive` → `strict` モードで漸進的に適用可能
* **多言語対応**: Python・TypeScript・Rust・Go・.NETをサポート

AIエージェントのセキュリティ整備はツールキット単体で完結するものではありませんが、まず`audit`モードで現状のエージェント動作を可視化するところから始めると、実際のリスクを把握しやすくなります。

## 参考リンク
