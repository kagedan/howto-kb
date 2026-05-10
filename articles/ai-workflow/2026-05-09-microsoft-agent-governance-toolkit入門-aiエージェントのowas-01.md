---
id: "2026-05-09-microsoft-agent-governance-toolkit入門-aiエージェントのowas-01"
title: "Microsoft Agent Governance Toolkit入門 — AIエージェントのOWASP対策をPythonで実装する"
url: "https://zenn.dev/kai_kou/articles/210-microsoft-agent-governance-toolkit-guide"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "Python", "TypeScript", "zenn"]
date_published: "2026-05-09"
date_collected: "2026-05-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

AIエージェントが本番システムで自律的に動作するようになった今、「エージェントが何をしているか」を制御・監査する仕組みが不可欠になっています。

2026年4月2日、Microsoftは[**Agent Governance Toolkit**](https://github.com/microsoft/agent-governance-toolkit)をMITライセンスでオープンソース公開しました。このツールキットは、自律型AIエージェントに対して以下を提供します。

* **ポリシー強制**: 各エージェントアクションをサブミリ秒で事前検査
* **ゼロトラスト ID**: エージェント間の信頼を暗号的に検証
* **実行サンドボックス**: ツール呼び出しを隔離された環境で実行
* **OWASP Agentic AI Top 10**: 10項目すべてに対応

### この記事で学べること

* OWASP Agentic AI Top 10 の各リスクと対策
* Agent Governance Toolkit のコンポーネント構成
* Python でのクイックスタートと PolicyEngine の使い方
* LangChain・CrewAI・Google ADK との統合方法
* ポリシー記述（YAML / OPA Rego / Cedar）の実例

### 対象読者

* AIエージェントを本番運用しているエンジニア
* エージェントのセキュリティ・ガバナンスに課題を感じている方
* OWASP や AI セキュリティに関心がある方

### 前提条件

* Python 3.10 以上
* pip によるパッケージ管理
* AIエージェントフレームワーク（LangChain、CrewAI 等）の基本知識

## TL;DR

* Microsoft が 2026-04-02 に **MIT** でリリースした AI エージェント向けランタイムセキュリティ OSS
* OWASP Agentic AI Top 10 を **10/10 カバー**、p99 ガバナンスレイテンシ **0.1ms 以下**
* `pip install "agent-governance-toolkit[full]"` で全機能インストール可能
* LangChain・CrewAI・Google ADK など **12以上** のフレームワークと統合可能
* ポリシー記述言語は **YAML / OPA Rego / Cedar** から選択可能

---

## OWASP Agentic AI Top 10 とは

OWASP（Open Worldwide Application Security Project）は、AIエージェント特有のセキュリティリスクを体系化した「OWASP Agentic AI Top 10」を公開しています。

Agent Governance Toolkit が対応する 10 項目は以下のとおりです。

| # | リスク名 | 説明 |
| --- | --- | --- |
| 1 | **Goal Hijacking** | プロンプトインジェクション等でエージェントの目的を乗っ取る |
| 2 | **Tool Misuse** | エージェントが意図しないツールを不正に呼び出す |
| 3 | **Identity Abuse** | 別エージェントや外部システムへの権限昇格 |
| 4 | **Supply Chain Risk** | プラグイン・スキルのサプライチェーン汚染 |
| 5 | **Unsafe Code Execution** | サンドボックスなしのコード実行による脱出 |
| 6 | **Memory Poisoning** | 長期記憶への悪意あるデータ注入 |
| 7 | **Insecure Communications** | エージェント間通信の盗聴・改ざん |
| 8 | **Cascading Failures** | マルチエージェントでの連鎖障害 |
| 9 | **Human-Agent Trust Exploitation** | 人間の過度な信頼を利用した不正動作 |
| 10 | **Rogue Agent** | 制御不能になった自律エージェントの暴走 |

従来のアプリケーションセキュリティ対策（WAF、SAST等）はこれらのリスクをカバーできません。AIエージェント特有のガバナンスレイヤーが必要です。

---

Agent Governance Toolkit はモノリポ構造で、以下のパッケージを個別にも組み合わせても利用できます。

```
agent-governance[full]
├── agent-os-kernel          # ステートレスポリシーエンジン（コア）
├── agentmesh-platform       # ゼロトラスト信頼メッシュ
├── agentmesh-runtime        # ランタイムスーパーバイザー
├── agent-sre                # SRE ツールキット（サーキットブレーカー等）
├── agent-governance-toolkit # コンプライアンス・アテステーション
├── agentmesh-marketplace    # プラグインマーケットプレイス（署名・検証）
└── agentmesh-lightning      # RL トレーニングガバナンス
```

### agent-os（ポリシーエンジン）

すべてのエージェントアクションが実行される前に、**同一プロセス内**で以下のフローを通過します。

```
エージェント → アクション要求 → agent-os（ポリシー評価）→ 許可 / 拒否 → ツール実行
```

ポリシー評価は p99 で **0.1ms 以下** と報告されており、エージェントの動作速度に実質的な影響を与えません。

### agentmesh-marketplace（プラグインサプライチェーン）

プラグイン・スキルのライフサイクルを管理します。

* **Ed25519 署名**: プラグインの改ざん検知
* **信頼ティアゲーティング**: 信頼レベルに応じたケイパビリティ制限
* **サプライチェーンセキュリティ**: OWASP リスク #4（Supply Chain Risk）に対応

---

## インストールとクイックスタート

### インストール

```
# フルスタックインストール
pip install "agent-governance-toolkit[full]"

# 個別インストール（段階的導入向け）
pip install agent-os-kernel          # ポリシーエンジンのみ
pip install agentmesh-platform       # 信頼メッシュのみ
pip install agent-sre                # SRE ツールキットのみ
```

TypeScript / .NET でも利用可能です。

```
# TypeScript
npm install @agentmesh/sdk

# .NET
dotnet add package Microsoft.AgentGovernance
```

### Python クイックスタート（10 分）

公式クイックスタートでは `PolicyEvaluator` クラスを使った以下の構成が示されています。

```
from agent_os.policies import PolicyEvaluator

# ポリシーエバリュエーター初期化（YAML / Rego / Cedar 対応）
evaluator = PolicyEvaluator.from_yaml("policies/agent-rules.yaml")

# エージェントアクションを評価（サブミリ秒）
decision = evaluator.evaluate(
    principal="did:mesh:agent-1",
    context={"tool_name": "analyze"}
)

if decision.allowed:
    # ツール実行
    result = run_tool("analyze", ...)
else:
    # ポリシー違反ログ & 拒否
    log_violation(decision.reason)
```

`principal` は DID（Decentralized Identifier）形式でエージェントを識別します。これにより、どのエージェントがどのツールを呼び出したかを完全に追跡できます。

---

## ポリシー記述の実例

Agent Governance Toolkit では 3 種類のポリシー言語をサポートしています。チームの習熟度やユースケースに応じて選択してください。

### YAML ルール（最もシンプル）

```
# policies/agent-rules.yaml
rules:
  - name: "block-external-http"
    description: "外部 HTTP リクエストを拒否する"
    condition:
      tool: "http_request"
      url_pattern: "^https?://(?!internal\\.)"
    action: deny
    severity: high

  - name: "limit-file-write"
    description: "ファイル書き込みを /tmp 配下に限定する"
    condition:
      tool: "file_write"
      path_prefix: "!"
      allowed_paths: ["/tmp/"]
    action: deny
    severity: critical
```

### OPA Rego（柔軟なルール記述）

```
# policies/mesh.rego
package agentmesh

default allow = false

# 内部エンドポイントへの HTTP リクエストのみ許可
allow {
    input.tool_name == "http_request"
    startswith(input.context.url, "https://internal.")
}

# /tmp 配下のファイル書き込みのみ許可
allow {
    input.tool_name == "file_write"
    startswith(input.context.path, "/tmp/")
}
```

### Cedar（AWS が開発した認可言語）

```
// Cedar ポリシー
permit(
    principal == Agent::"did:mesh:agent-analyst",
    action == Action::"ReadDatabase",
    resource in Database::"internal"
);

forbid(
    principal,
    action == Action::"DeleteRecord",
    resource
) unless {
    principal.trust_level >= 3
};
```

---

## フレームワーク統合

Agent Governance Toolkit は 12 以上のフレームワーク統合を提供しており、既存のエージェントコードにガバナンスを後付けで追加できます。

### LangChain 統合

```
from langchain.agents import AgentExecutor
from agentmesh.integrations.langchain import GovernanceCallbackHandler

# ガバナンスハンドラーを追加（既存コードの変更は最小限）
governance_handler = GovernanceCallbackHandler(
    policy_file="policies/agent-rules.yaml"
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=[governance_handler],  # この1行を追加
    verbose=True
)
```

LangChain のコールバックシステムにフックするため、既存エージェントの書き換えは不要です。

### CrewAI 統合

```
from crewai import Agent, Task, Crew
from agentmesh.integrations.crewai import governed_agent

@governed_agent(policy="policies/agent-rules.yaml")
class ResearchAgent(Agent):
    role = "Research Analyst"
    goal = "Gather and analyze market data"
    # デコレータがガバナンスを自動注入
```

### Google ADK 統合

Google ADK 向けには `ADKPolicyEvaluator` と `GovernanceCallbacks` が提供されています。

```
from google.adk import Agent
from adk_agentmesh import ADKPolicyEvaluator, GovernanceCallbacks

# ポリシーエバリュエーターを初期化
policy_evaluator = ADKPolicyEvaluator.from_yaml("policies/agent-rules.yaml")

app = Agent(
    name="my-agent",
    callbacks=GovernanceCallbacks(evaluator=policy_evaluator)
)
```

---

## OWASP Top 10 への対応マッピング

各コンポーネントと OWASP リスクの対応関係を整理します。

| OWASP リスク | 対応コンポーネント | 実装手段 |
| --- | --- | --- |
| Goal Hijacking | agent-os | ツール呼び出しのインターセプト、プロンプト署名検証 |
| Tool Misuse | agent-os | ツール許可リスト・アクションポリシー評価 |
| Identity Abuse | agentmesh-platform | DID ベースのゼロトラスト認証 |
| Supply Chain Risk | agentmesh-marketplace | Ed25519 署名、信頼ティアゲーティング |
| Unsafe Code Execution | agentmesh-runtime | 実行サンドボックス（コンテナ / gVisor） |
| Memory Poisoning | agent-os | メモリ書き込みのポリシー評価 |
| Insecure Communications | agentmesh-platform | mTLS によるエージェント間通信暗号化 |
| Cascading Failures | agent-sre | サーキットブレーカー、ブルヘッドパターン |
| Human-Agent Trust | agent-governance-toolkit | コンプライアンス監査証跡、信頼スコアリング |
| Rogue Agent | agentmesh-runtime | ランタイム異常検知、自動シャットダウン |

### コンプライアンスフレームワーク対応

`agent-governance-toolkit` パッケージは、以下の規制フレームワークへの準拠証跡を自動収集します。

* **EU AI Act**: 高リスク AI システムの透明性要件
* **HIPAA**: 医療データへのエージェントアクセス監査
* **SOC 2**: セキュリティ・可用性・機密性の継続的証明

```
# コンプライアンスレポート生成
python -m agent_governance.compliance report \
  --framework eu-ai-act \
  --output compliance-report.json
```

---

## 注意点

### 現在のステータス

Agent Governance Toolkit は **公開プレビュー** 段階です（2026-04-11 時点）。本番環境での採用にあたっては以下を確認してください。

* 各パッケージのバージョン安定性（PyPI の CHANGELOG 参照）
* フレームワーク統合のカバレッジ（12以上あるが、マイナーフレームワークは別途確認）
* ポリシー評価の副作用（`deny` 時のエラーハンドリングを適切に実装）

### パフォーマンス考慮

p99 ガバナンスレイテンシは <0.1ms と報告されていますが、これは埋め込みエンジン（cedarpy / opa CLI）使用時の値です。OPA Rego を **リモートサーバー**モードで実行する場合はネットワークレイテンシが加算されます。

評価モードは 3 種類から選択できます。

| モード | レイテンシ | 可用性 |
| --- | --- | --- |
| Embedded（デフォルト） | <0.1ms | 外部依存なし |
| Remote Server | ネットワーク次第 | 集中管理可能 |
| Built-in Fallback | <0.05ms | 外部依存ゼロ |

---

## まとめ

Microsoft Agent Governance Toolkit は、急速に普及する自律型 AI エージェントに対して「ガバナンスの欠如」という課題に正面から向き合った OSS です。主な特徴を振り返ります。

* **OWASP Agentic AI Top 10 を 10/10 カバー** — エージェント特有のリスクを体系的に防御
* **フレームワーク非依存** — 20以上のアダプタで既存システムへの導入コストを最小化
* **サブミリ秒ポリシー評価** — 実用的な速度でエージェントを制御
* **多言語ポリシー対応** — YAML / OPA Rego / Cedar から選択可能
* **MIT ライセンス** — 商用利用も含めて自由に利用可能

AIエージェントが「何でもできる存在」として動作するのではなく、「ポリシーに従って動作する信頼できるシステム」として設計するための基盤として、本ツールキットは検討に値します。

## 参考リンク
