---
id: "2026-07-19-aiエージェントの行動を可視化する-エージェントトレーシングとactivity-stream監査-01"
title: "AIエージェントの行動を可視化する — エージェントトレーシングとActivity Stream監査"
url: "https://zenn.dev/76hata/articles/agentic-observability-tracing-activity-stream"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "LLM", "Python", "zenn"]
date_published: "2026-07-19"
date_collected: "2026-07-20"
summary_by: "auto-rss"
query: ""
---

## この記事で分かること

* なぜ従来のアプリケーションログではAIエージェントの障害が追跡できないのか
* OpenTelemetry GenAIセマンティック規約を使ったエージェントトレーシングの設計パターン
* Activity Stream監査パターンとトレーシングの棲み分け・組み合わせ方
* プロダクションで回すための設計判断を、スパン構造・品質評価・委任追跡・サンプリング・保持期間まで含めてどう下すか
* Pythonコード、SQLスキーマ、クエリ例を交えた具体的な実装方法

## 前提知識

* **OpenTelemetry（OTel）**: 分散トレーシングの業界標準です。アプリケーション内の処理単位を「スパン（Span）」として記録し、親子関係で因果経路を表現します。
* **エージェントループ**: LLMが「観察→判断→ツール実行→観察」を反復する制御構造です。毎回同じ経路を通る保証がなく、分岐数もループ回数も入力依存になります。
* **Activity Stream**: 「誰が・いつ・何を・なぜ・どの委任で」を時系列イベントとして残す監査パターンです。DDD由来のイベント記録と、セキュリティ監査の証跡要求の中間に位置する実装スタイルだと考えると理解しやすいです。
* **Eval-on-Span**: 推論やツール実行の品質評価を、別のデータストアではなくスパン属性または関連イベントとして直接ぶら下げる設計です。性能劣化と品質劣化を同じ観測面で扱える利点があります。

---

## ある夜間の障害から

午前2時、プロダクションのエージェントが顧客データを誤って削除しました。アラートは飛んできました。オンコールに入ったあなたは、最初の15分で次の3つに答えなければいけません。

1. エージェントは**何を**実行したのか
2. なぜその実行を**妥当だと判断**したのか
3. その実行は**どの権限文脈で**起き、どのデータに影響したのか

ここで `grep request_id` しかできないなら、監視基盤は存在していても可観測性は成立していません。HTTP 200、Lambda成功、SQL実行完了、すべて緑でも、エージェントは平然と誤るからです。しかも厄介なのは、誤りの型が単一ではないことです。

* ルーティング誤り: 本来 `search_customer` を呼ぶべき場面で `delete_customer` を選ぶ
* 引数誤り: ツール選択は正しいが `customer_id` の抽出がずれる
* 委任誤り: 権限の弱いユーザーの依頼を、強いサービスアカウントで実行する
* 反復誤り: 同じツールを8回呼んでループする
* 回答誤り: ツール結果は正しいのに最終要約が誤る

この5種類は、同じ「エージェントの不具合」に見えても、必要な観測面が異なります。ルーティング誤りには意思決定トレースが必要です。委任誤りには監査ログが必要です。回答誤りには品質評価が必要です。だから本稿の結論は最初から明確です。**トレースだけでは足りず、監査ログだけでも足りず、評価ログだけでも足りません。三者を分離しつつ相互参照できる構造が必要です。**

## なぜ従来のログでは追跡できないのか

従来の分散トレーシングは「決定的なサービス間パス」を仮定しています。`POST /api/orders` が `orders-api -> payment -> inventory -> mailer` と流れるなら、障害解析は主に次の3変数に還元できます。

* どこで遅くなったか
* どこで例外が出たか
* どの下流サービスが失敗したか

しかしLLMエージェントは、その前提そのものを壊します。

| 従来のシステム | AIエージェント |
| --- | --- |
| 実行経路がほぼ決定的 | 実行経路が入力と推論に応じて毎回変わる |
| 失敗は例外やHTTPステータスに出やすい | ステータス200でも内容が誤る |
| 呼び出し先の集合が比較的固定 | ツール、サブエージェント、MCP先が動的に変わる |
| トレース長は概ね有界 | ループで非有界に伸びうる |
| デバッグ対象は計算処理 | デバッグ対象に「判断」と「委任」が入る |

この差は、単に「ログ量が増えた」という話ではありません。**観測したい対象が、処理そのものから判断過程へ拡張した**ということです。

もっと厳密に言うと、エージェント運用では少なくとも次の6面を観測しなければいけません。

1. **Control Plane**: どのワークフロー、どのエージェント、どのバージョンが動いたか
2. **Reasoning Plane**: どの観測に基づき、何を次の行動として選んだか
3. **Actuation Plane**: どのツールを、どの引数で、何回実行したか
4. **Memory Plane**: 何を検索し、どの文書片が判断材料になったか
5. **Policy Plane**: どの認可・ガードレール判定が通り、どれがブロックしたか
6. **Outcome Plane**: 最終結果の品質、ビジネス影響、ユーザー影響

通常のアプリケーションログが強いのは 1 と 3 です。弱いのは 2、5、6 です。AIエージェント運用で事故が難しくなる本質はここにあります。

## この記事の主張を先に置く

本稿の主張は次の1文に尽きます。

> エージェントの可観測性は、OpenTelemetryのスパンを中心に据えつつも、そこへ意思決定理由と品質評価を埋め込み、さらに委任・権限・証跡の長期保存を担うActivity Streamを独立レイヤーとして持たなければ実運用に耐えません。

この主張がなぜ強いかというと、エージェント障害は「遅い」「落ちた」ではなく、「誤って進んだ」が中心だからです。誤って進んだときに必要なのは、単一の巨大ログではありません。因果経路、評価、監査が分離された上で結び付いていることです。

## 設計の全体像

以下が、本稿で推奨する最小十分なアーキテクチャです。

この構造の要点は、責務を次のように割ることです。

* **L1 トレース**は「何が、どの順で起きたか」を表現する
* **L2 評価**は「その選択は良かったのか」を表現する
* **L3 監査**は「誰の委任で、どの権限で起きたか」を表現する

同じデータ基盤に全部押し込まない理由は、クエリ粒度と保持期間が違うからです。開発者は `trace_id` で障害解析したい。監査担当は `actor`、`delegation_chain`、`tool_id`、`time range` で引きたい。SREは `ToolSelectionScore` の移動平均でアラートしたい。これらを一つの巨大JSONに詰めると、必ず検索性か保持コストのどちらかが破綻します。

## 可観測性の失敗は「記録不足」ではなく「データモデル不備」で起きる

多くの現場では、エージェント事故のあとで「もっとログを増やそう」という反応が起きます。半分は正しいですが、半分は誤りです。必要なのはログ総量ではなく、**あとから再構成できる因果モデル**です。

その因果モデルに必要な最小単位は、私は次の4つだと考えています。

1. **Intent**: エージェントがその時点で達成しようとした局所目的
2. **Evidence**: その判断の根拠になった観測や文書断片
3. **Action**: 実行に移した具体的操作
4. **Authority**: その操作を許した主体と権限文脈

従来ログはたいてい 3 しか持っていません。良くて 3 と一部の 4 です。しかし、事故解析で最も欲しいのは 1 と 2 です。たとえば `delete_customer` が実行された事実だけでは不十分で、「同姓同名の顧客が二人いる文脈で、エージェントが `exact_match=false` の検索結果を根拠に削除候補を誤認した」という粒度まで見えないと、再発防止策を設計できません。

## 層1: OpenTelemetry GenAI規約によるトレーシング

OpenTelemetryのGenAIセマンティック規約は、LLM呼び出し、ツール呼び出し、モデル入出力、トークン利用量、ストリーミング遅延などを標準化された属性で表現します。2026年7月時点では、OpenTelemetry本体ドキュメント上ではGenAI規約が専用リポジトリへ移管済みとして案内されており、属性レジストリ側でも `gen_ai.*` は移管元ページとして参照できます。重要なのは、**この領域はまだ変化している**という前提で設計することです。

### まず押さえるべき3つの事実

1. `gen_ai.system` ではなく `gen_ai.provider.name` を使う
2. `gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens` のように入出力トークンを分ける
3. 推論内容やプロンプト全文は高機密・高カーディナリティなので、常時属性化しない

最後の点が特に重要です。OpenTelemetryのGenAI関連資料でも、内容キャプチャはデフォルトで抑制される前提が強く打ち出されています。なぜか。理由は3つです。

* 機微情報を含みやすい
* 属性サイズが大きく、ストレージとインデックスコストを急増させる
* カーディナリティが高く、検索・集計を壊しやすい

これは「取るな」という意味ではありません。**全件属性化するな**という意味です。詳細は後述しますが、本文・ツール引数・ツール結果は、常設の属性よりもイベント、ログ、もしくは別の暗号化ストアに逃がすほうが安全です。

### スパン階層の推奨形

エージェント実行のスパンは、少なくとも次の3段で切るのが実務上扱いやすいです。

1. **Root span**: `invoke_agent` または `invoke_workflow`
2. **Reasoning spans**: 計画、再計画、最終合成などの `gen_ai.chat`
3. **Execution spans**: ツール呼び出し、検索、外部API、サブエージェント委譲

これをさらに厳密化すると、次のようになります。

```
invoke_workflow
├── invoke_agent(planner)
│   ├── gen_ai.chat(plan)
│   ├── invoke_agent(researcher)
│   │   ├── gen_ai.chat(route)
│   │   ├── retrieve(memory)
│   │   ├── execute_tool(search_docs)
│   │   └── gen_ai.chat(summarize)
│   └── gen_ai.chat(decide_next_step)
└── gen_ai.chat(final_answer)
```

この分割の利点は、単に見やすいことではありません。

* `planner` の判断が悪いのか
* `researcher` の検索が悪いのか
* 最終合成だけが悪いのか

をトレース木の構造だけで切り分けやすくなります。逆に、すべてを `agent_loop` 1スパンに押し込むと、遅延分解も責任分解もできません。

### 実装例

```
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer("agent.observability")

@dataclass
class AgentContext:
    request_id: str
    actor_id: str
    delegation_id: str
    workflow_name: str
    agent_name: str
    agent_version: str

def run_agent(ctx: AgentContext, task: str) -> str:
    with tracer.start_as_current_span("invoke_agent") as root:
        root.set_attribute("gen_ai.agent.name", ctx.agent_name)
        root.set_attribute("gen_ai.agent.version", ctx.agent_version)
        root.set_attribute("gen_ai.workflow.name", ctx.workflow_name)
        root.set_attribute("app.request.id", ctx.request_id)
        root.set_attribute("app.actor.id", ctx.actor_id)
        root.set_attribute("app.delegation.id", ctx.delegation_id)
        root.set_attribute("agent.loop.max_iterations", 8)

        plan = plan_next_action(task)

        with tracer.start_as_current_span("gen_ai.chat") as plan_span:
            plan_span.set_attribute("gen_ai.provider.name", "anthropic")
            plan_span.set_attribute("gen_ai.request.model", "claude-sonnet-4-20250514")
            plan_span.set_attribute("gen_ai.request.temperature", 0.0)
            plan_span.set_attribute("gen_ai.usage.input_tokens", 1821)
            plan_span.set_attribute("gen_ai.usage.output_tokens", 244)
            plan_span.set_attribute("agent.decision.intent", "decide_next_action")
            plan_span.set_attribute("agent.decision.reasoning", plan.reasoning_summary)
            plan_span.set_attribute("agent.decision.evidence.count", len(plan.evidence_ids))
            plan_span.set_attribute("agent.decision.branch_factor", len(plan.candidate_actions))

        result = None
        try:
            with tracer.start_as_current_span("execute_tool") as tool_span:
                tool_span.set_attribute("gen_ai.tool.name", plan.tool_name)
                tool_span.set_attribute("gen_ai.tool.type", "function")
                tool_span.set_attribute("gen_ai.tool.call.id", plan.tool_call_id)
                tool_span.set_attribute("agent.decision.reasoning", plan.reasoning_summary)
                tool_span.set_attribute("agent.decision.risk", plan.risk_level)
                tool_span.set_attribute("agent.decision.evidence.ids", json.dumps(plan.evidence_ids))
                tool_span.add_event(
                    "tool.arguments.masked",
                    {"payload": json.dumps(mask_secrets(plan.arguments))}
                )
                start = time.perf_counter()
                result = execute_tool(plan.tool_name, plan.arguments)
                tool_span.set_attribute("tool.duration_ms", round((time.perf_counter() - start) * 1000, 2))
                tool_span.set_attribute("tool.result.size_bytes", len(json.dumps(result)))

            with tracer.start_as_current_span("gen_ai.chat") as final_span:
                final_span.set_attribute("gen_ai.provider.name", "anthropic")
                final_span.set_attribute("gen_ai.request.model", "claude-sonnet-4-20250514")
                final_span.set_attribute("agent.decision.intent", "compose_final_response")
                final_span.set_attribute("agent.decision.evidence.count", len(plan.evidence_ids))
                final_span.set_attribute("gen_ai.response.finish_reasons", ["stop"])
                return synthesize_answer(task, result)
        except Exception as exc:
            root.record_exception(exc)
            root.set_status(Status(StatusCode.ERROR, str(exc)))
            raise
```

ここで標準規約にないのに追加している属性があります。

* `agent.decision.intent`
* `agent.decision.reasoning`
* `agent.decision.evidence.ids`
* `agent.decision.branch_factor`
* `agent.decision.risk`

これらは独自拡張です。独自拡張を嫌う人もいますが、私はここで遠慮すべきではないと考えています。理由は単純で、**標準規約は「相互運用性」を与えるが、あなたの事故解析責務までは肩代わりしない**からです。標準だけで足りない観測軸は、自分で補うしかありません。

### 「なぜ」をどう記録するか

問題は `agent.decision.reasoning` に何を書き、何を書かないかです。Chain-of-Thoughtそのものを全面記録すべきかという論点もあります。私の結論は次です。

* 生の長文推論全文は常設属性にしない
* 代わりに**要約済みの意思決定理由**を保存する
* 根拠文書や検索結果との結び付けはIDで行う
* 高リスク操作だけ、暗号化された詳細監査レコードへ深掘り保存する

たとえば、良い `reasoning` はこうです。

```
ユーザーは注文状況ではなく顧客プロファイル更新を依頼している。候補ツールは update_customer と create_ticket の2つ。既存顧客ID CUST-1024 が文脈内にあり、更新対象フィールドが住所のみであるため update_customer を選択。
```

悪いのはこうです。

差は明白です。前者は後からレビュー可能です。候補集合、判断条件、選択理由がある。後者は記録した意味がありません。

### エージェント特有のメトリクス

LLM呼び出しのトークン数と遅延だけでは、エージェントの異常は見えません。少なくとも以下は追加で出すべきです。

| 指標 | 意味 | 異常時に疑うこと |
| --- | --- | --- |
| `agent.loop.iterations` | 1リクエスト内の思考反復回数 | ループ、過剰探索、ゴール不明確 |
| `agent.branch_factor` | 各ステップでの候補行動数 | ツール定義が広すぎる、プロンプトが曖昧 |
| `tool.calls_per_trace` | トレース内ツール回数 | 冗長実行、再試行暴走 |
| `retrieval.docs_per_step` | 1判断で見た文書数 | 検索過多、コンテキスト汚染 |
| `approval.wait_ms` | 人間承認待ち時間 | オペレーション設計不備 |
| `destructive_tool_rate` | 高リスクツール比率 | 権限境界の欠陥 |

これらは標準規約の外側でも、メトリクスとしては非常に有効です。なぜなら、エージェント障害の初期兆候は例外率ではなく、**探索幅・反復回数・危険行動率の変化**として先に出るからです。

## 層2: 品質スコアをスパンに載せる

ここが、多くの記事で一番薄く扱われる部分です。しかし実運用では、私はこの層が最も重要だと思っています。理由は、エージェントの本当に危険な異常は**サイレントドリフト**だからです。

サイレントドリフトとは何か。単純に言えば、

* 例外は出ない
* レイテンシも大きくは悪化しない
* 成功率も落ちない
* なのに選択品質や回答品質が徐々に悪化する

という現象です。

モデル切り替え、プロンプト修正、ツール説明の変更、RAG索引の更新、外部API仕様変更。どれでも起こります。しかも、ユーザー苦情が来るまで気づかれにくい。だから**品質をメトリクス化し、性能と同じ面に置く**必要があります。

### Eval-on-Spanが効く理由

別DBに評価結果を溜める方式もあります。しかし、それだけだと実運用で次の問題が起きます。

* トレースと評価の相関分析が遅い
* アラート基盤が二重化する
* 「高レイテンシかつ低品質」みたいな複合条件が書きづらい

対して、評価結果をスパンに直接載せると次が可能になります。

* 低品質スパンだけをUI上で即座に絞り込める
* `p95 latency` と `mean ToolSelectionScore` を同じダッシュボードに置ける
* 尾部サンプリングで「低品質トレースを優先保存」できる

### 何をスコア化するか

評価対象は「最終回答だけ」では足りません。エージェントでは判断が多段化するため、**中間意思決定**も評価対象に入れるべきです。

| スコア | 対象 | 典型的な算出法 |
| --- | --- | --- |
| `ToolSelectionScore` | ツール選択 | 期待ツールとの一致、審査器LLM、ルールベース |
| `ArgumentValidityScore` | 引数の妥当性 | JSON Schema適合、業務ルール適合 |
| `GroundednessScore` | 最終回答の根拠性 | 引用文書との整合、根拠欠落率 |
| `DelegationCorrectnessScore` | 委任先の妥当性 | 正しいサブエージェントへ渡したか |
| `LoopRiskScore` | ループリスク | 反復回数、重複行動率、状態停滞 |
| `PolicyComplianceScore` | ポリシー順守 | 危険ツール前の承認、PIIマスキング有無 |

### 実装例

```
def attach_tool_evaluations(span, expected_tool: str, actual_tool: str, args: dict) -> None:
    tool_score = 1.0 if expected_tool == actual_tool else 0.0
    arg_score = 1.0 if validate_arguments(args) else 0.0

    span.set_attribute("gen_ai.evaluation.name", "ToolSelectionScore")
    span.set_attribute("gen_ai.evaluation.score.value", tool_score)
    span.set_attribute("gen_ai.evaluation.score.label", "pass" if tool_score == 1.0 else "fail")
    span.add_event(
        "evaluation.argument_validity",
        {
            "gen_ai.evaluation.name": "ArgumentValidityScore",
            "gen_ai.evaluation.score.value": arg_score,
            "gen_ai.evaluation.score.label": "pass" if arg_score == 1.0 else "fail",
        },
    )
```

ここで1点だけ注意があります。`gen_ai.evaluation.*` は「1スパンに1種類の評価しか持てない」と解釈すると窮屈です。現実には複数評価が欲しいので、私は次の使い分けを推奨します。

* 主評価を属性に置く
* 副評価をイベントに置く
* さらに長期分析用に、Collectorまたは後段ETLでメトリクス化する

### 評価とサンプリングを接続する

OpenTelemetryのTail Samplingは、トレース完了後に各スパンを見て採否を決められるため、エージェントとの相性が良いです。標準的なエラー率ベースではなく、次のような条件にすると価値が出ます。

* `ToolSelectionScore < 0.6`
* `LoopRiskScore > 0.8`
* `agent.loop.iterations >= 6`
* `agent.decision.risk = destructive`
* `gen_ai.response.finish_reasons` に `length` が多発

つまり、**低品質トレースを保存対象に昇格させる**わけです。これはサンプリングを単なるコスト削減ではなく、障害解析戦略に変える発想です。

### サイレントドリフトの検知設計

有効なのは単発失敗率ではなく、窓関数での変化率です。

```
SELECT
  date_trunc('hour', observed_at) AS bucket,
  AVG(tool_selection_score) AS avg_tool_score,
  AVG(groundedness_score) AS avg_groundedness,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_latency
FROM agent_eval_metrics
WHERE workflow_name = 'customer_support'
  AND observed_at >= now() - interval '7 days'
GROUP BY 1
ORDER BY 1;
```

このクエリで見たいのは、性能と品質の乖離です。例えば、

* p95レイテンシは横ばい
* 例外率も横ばい
* しかし `avg_tool_score` だけ3日かけて 0.91 -> 0.73 に低下

なら、監視基盤は「正常」に見えてもエージェントは壊れ始めています。これを検知できるかどうかが、Agentic Observability の成熟度を分けます。

## 層3: Activity Stream監査パターン

ここからは監査の話です。トレースはデバッグに向いていますが、監査にそのまま使うには弱点があります。

* 保持期間が短い
* クエリ軸が `trace_id` 寄りで、人・権限・委任に弱い
* 機微データを含む本文を長期保存しにくい
* 監査で欲しい「承認された／拒否された」事実が、スパンだけでは欠けやすい

だからActivity Streamを分けます。

### 何を残すべきか

最低限、以下は必要です。

```
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

@dataclass
class ActivityEvent:
    event_id: str = field(default_factory=lambda: uuid4().hex)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = ""
    actor_id: str = ""
    actor_type: str = ""           # user / service / agent
    delegation_chain: list[str] = field(default_factory=list)
    approval_id: str | None = None
    workflow_name: str = ""
    agent_name: str = ""
    tool_name: str | None = None
    tool_risk: str | None = None
    resource_ids: list[str] = field(default_factory=list)
    parameter_fingerprint: str | None = None
    result_status: str = ""
    policy_decision: str | None = None
    trace_id: str = ""
    span_id: str | None = None
```

ここで重要なのは `delegation_chain` です。単一の `delegation` 文字列だけでは足りないことが多いからです。たとえば、

```
user:alice@example.com
-> service:customer-portal
-> workflow:billing_assistant
-> agent:refund_specialist
-> tool:refund.execute
```

のように、誰の依頼がどの代理主体を経由して危険操作に至ったかが見えないと、委任の正当性を監査できません。

### SQLスキーマ例

監査基盤をログ保存で済ませず、構造化テーブルにする理由は、後から複数条件で絞る必要があるからです。

```
CREATE TABLE activity_events (
  event_id                text PRIMARY KEY,
  occurred_at             timestamptz NOT NULL,
  event_type              text NOT NULL,
  actor_id                text NOT NULL,
  actor_type              text NOT NULL,
  delegation_chain        jsonb NOT NULL,
  approval_id             text,
  workflow_name           text NOT NULL,
  agent_name              text NOT NULL,
  tool_name               text,
  tool_risk               text,
  resource_ids            jsonb NOT NULL DEFAULT '[]'::jsonb,
  parameter_fingerprint   text,
  result_status           text NOT NULL,
  policy_decision         text,
  trace_id                text NOT NULL,
  span_id                 text,
  metadata                jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX idx_activity_events_occurred_at
  ON activity_events (occurred_at DESC);

CREATE INDEX idx_activity_events_actor
  ON activity_events (actor_id, occurred_at DESC);

CREATE INDEX idx_activity_events_trace
  ON activity_events (trace_id);

CREATE INDEX idx_activity_events_tool
  ON activity_events (tool_name, occurred_at DESC);

CREATE INDEX idx_activity_events_delegation_chain
  ON activity_events USING gin (delegation_chain jsonb_path_ops);
```

このテーブルを見れば、「誰が」「どの承認で」「危険なツールを」「いつ」「何件」実行したかが監査で引けます。トレースと違い、親子木ではなく**監査の問いに最適化したフラット時系列**にするのがコツです。

### トレースとActivity Streamをどうつなぐか

答えは明確で、`trace_id` を共有します。さらに高リスク操作は `span_id` まで残すと便利です。

### 監査で本当に重要なイベント種別

私は最低でも次の7種を推奨します。

1. `delegation.accepted`
2. `policy.checked`
3. `tool.execution.approved`
4. `tool.execution.blocked`
5. `tool.execution.completed`
6. `artifact.persisted`
7. `response.emitted`

なぜ `tool.execution.completed` だけでは足りないのか。理由は、「実行された」事実と「実行してよいと判断された」事実は別だからです。セキュリティ事故の事後調査では、この差が非常に重要になります。

### Finatext MCPass型の設計が示唆すること

公開されているMCPゲートウェイ事例では、CloudWatch Logsだけで監査要件を満たさず、CloudWatch Logs -> Lambda -> Aurora PostgreSQL のETLで監査証跡を構造化保存しています。これは単に好みの問題ではありません。監査では以下が要求されるからです。

* 長期保持
* SQLでの柔軟検索
* テナント分離
* 機密レコードの暗号化管理

エージェント監査も同じです。開発者向けログの最適解と、監査向けログの最適解は一致しません。**開発者に見せやすいログ基盤を、そのまま監査基盤に流用しない**ことが重要です。

## 3層をつなぐ中核概念は「因果参照可能性」

ここまでの内容を、より抽象化してまとめます。優れたAgentic Observabilityの条件は、すべてを取ることではありません。**後から問いを因果的に辿れること**です。

具体的には、任意の危険操作について次の連鎖が辿れればよい。

```
監査イベント
-> 対応する trace_id
-> 問題の span_id
-> その span の意思決定理由
-> 参照した evidence ids
-> その判断の品質スコア
-> 承認と権限文脈
```

この鎖のどこかが切れると、障害解析は急に属人的になります。

* `trace_id` が無いと、監査からトレースへ飛べない
* `evidence ids` が無いと、判断根拠を検証できない
* `quality score` が無いと、誤りを統計的に検知できない
* `delegation chain` が無いと、責任境界が曖昧になる

要するに、設計の勝負どころは「何を記録するか」より「どう結ぶか」です。

## プロダクションで回すための設計判断 1: スパン構造を「ワークフロー」と「行為」に分ける

OpenTelemetryのリリースノートでも、`invoke_agent` の扱いは変化しています。これは、エージェントの観測対象が単一推論からワークフロー全体へ広がっているためです。実装上の判断としては、**ワークフローの根スパンと、個別行為の実行スパンを混ぜない**ことを強く推奨します。

### 悪い設計

* すべて `agent_loop` 1スパン
* その中にログ文字列を大量に追加

### 良い設計

* `invoke_workflow`: ワークフロー単位
* `invoke_agent`: エージェント単位
* `gen_ai.chat`: 推論単位
* `execute_tool`: 行為単位
* `retrieve`: 証拠取得単位
* `approval.wait`: 人間承認待ち単位

この分解により、例えば次の分析が可能になります。

* ワークフロー全体は成功したが、どのエージェントが遅かったか
* ツール実行は成功したが、どの推論スパンで誤選択が起きたか
* 承認待ちがボトルネックなのか、モデルが遅いのか

## 設計判断 2: プロンプト全文は属性に詰め込まない

ここは強く言います。全文キャプチャを安易に常時ONにしないでください。OpenTelemetryのGenAI資料でも、内容キャプチャはセンシティブデータを含むことが明示されています。たしかにデバッグは楽になります。しかし、次の副作用が大きすぎます。

* PIIや業務機密が可観測基盤へ二次流出する
* 属性のサイズが指数的に増える
* ベクトル検索や要約結果まで取り始めると保持コストが跳ねる
* トレースUIの可読性が落ちる

私が推奨するのは次の4段階です。

1. **通常運用**: 本文は取らず、メタデータと要約理由だけ
2. **高リスク操作前**: マスク済み要約のみ
3. **インシデント解析**: 期間限定で対象ワークフローだけ内容キャプチャを有効化
4. **機密案件**: 本文は暗号化ストアへ分離し、トレースには参照IDのみ

設定例は以下です。

```
export OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false
```

加えて、Collector側で次の処理を入れると安全性が上がります。

* `authorization`, `cookie`, `api_key` などのヘッダ削除
* `email`, `phone`, `customer_name` の正規表現マスキング
* `gen_ai.tool.call.arguments` のキー単位サニタイズ
* 危険ワークフローだけ別Exporterへ分流

## 設計判断 3: サンプリングは頭部ベースだけで終わらせない

OpenTelemetryのSamplingドキュメントが示す通り、Tail Samplingはトレース全体を見てから採否を決められます。エージェントではこれが本質的に重要です。なぜなら、危険かどうかは根スパン開始時点では分からないからです。

例えば、次の2トレースは開始時点では同じに見えます。

* 問い合わせに対して1回の検索で正しく応答したトレース
* 7回ループしたあと危険ツールへ到達し、最終的に低品質回答を返したトレース

Head Samplingだけでは区別できません。だから実運用ではハイブリッドが妥当です。

* **Head-based 10〜30%**: 全体傾向把握とコスト制御
* **Tail-based keep**: エラー、低品質、高リスク、長大トレースを優先保持

Collectorポリシーの考え方はこうです。

```
processors:
  tail_sampling:
    decision_wait: 10s
    num_traces: 50000
    expected_new_traces_per_sec: 100
    policies:
      - name: errors
        type: status_code
        status_code:
          status_codes: [ERROR]
      - name: destructive-risk
        type: numeric_attribute
        numeric_attribute:
          key: agent.risk.score
          min_value: 0.8
          max_value: 1.0
      - name: long-loops
        type: numeric_attribute
        numeric_attribute:
          key: agent.loop.iterations
          min_value: 6
          max_value: 999
```

ここでのポイントは、サンプリング基準に**品質と危険度**を入れることです。通常のAPM発想だと、遅延と例外しか入りません。しかしエージェントで保持すべきは、誤りの兆候がある正常終了トレースです。

## 設計判断 4: 委任を1属性で済ませず、チェーンとして扱う

エージェント事故では、主体が増えます。

* ユーザー
* フロントエンド
* APIサーバー
* ワークフロー
* エージェント
* ツール
* 外部サービス

ここで `delegated_by=user:alice` のような1属性だけ残すと、中継した主体が消えます。後から監査で問われるのは、「誰が押したか」よりも「どの代理連鎖で権限が使われたか」です。

だから私は、委任を**チェーン**として記録することを勧めます。

```
[
  {"type": "user", "id": "alice@example.com"},
  {"type": "service", "id": "customer-portal"},
  {"type": "workflow", "id": "billing_assistant"},
  {"type": "agent", "id": "refund_specialist"},
  {"type": "tool", "id": "refund.execute"}
]
```

この配列があるだけで、次の設計が可能になります。

* ワークフロー単位の責務分離
* 危険ツール前の追加承認
* テナント境界を超える委任の検知
* 「人が承認したから安全」ではなく「誰が何を承認したか」の追跡

## 設計判断 5: ループを障害とみなさず、「状態停滞」として測る

エージェントではループ自体は必ずしも悪ではありません。探索、再試行、再計画は必要です。問題は、**状態が進んでいないのに反復している**ことです。

そのため、単に `iterations > 5` でアラートするのは雑です。おすすめは次の複合指標です。

* 直近3ステップで同じツールを同じ引数で実行している
* 取得した証拠集合が変わっていない
* `agent.decision.intent` が変化していない
* 最終回答の草案の埋め込み類似度が 0.98 以上で停滞している

この4つのうち3つ以上を満たしたら「状態停滞」と判定する、といった設計のほうが現実的です。

```
def detect_stagnation(steps: list[dict]) -> bool:
    if len(steps) < 3:
        return False
    last = steps[-3:]
    same_tool = len({s["tool_name"] for s in last}) == 1
    same_args = len({s["arg_hash"] for s in last}) == 1
    same_intent = len({s["intent"] for s in last}) == 1
    same_evidence = len({tuple(sorted(s["evidence_ids"])) for s in last}) == 1
    return sum([same_tool, same_args, same_intent, same_evidence]) >= 3
```

この判定を `LoopRiskScore` としてスパンに載せると、「単なる長い思考」と「壊れた反復」を分けられます。

## 設計判断 6: Retrievalも独立スパンにし、証拠IDを必ず残す

RAGやメモリ検索を伴うエージェントで最も困るのは、回答が間違ったときに「何を見てそう言ったのか」が追えないことです。だから retrieval は単なる内部処理ではなく、観測上は一級市民にすべきです。

最低限残したいのは次の4つです。

* `gen_ai.retrieval.query.text`
* 上位 `document ids`
* 各文書の `score`
* その文書群を参照した後段スパンの `evidence ids`

```
with tracer.start_as_current_span("retrieve") as retrieval_span:
    retrieval_span.set_attribute("gen_ai.retrieval.query.text", query)
    retrieval_span.add_event(
        "retrieval.top_docs",
        {
            "docs": json.dumps(
                [{"id": doc.id, "score": doc.score} for doc in top_docs[:5]]
            )
        },
    )
```

私は、後段の `agent.decision.evidence.ids` には文書IDだけでなく、できればスナップショット版数も含めることを勧めます。そうしないと、インデックス再構築後に同じ `doc-123` が別内容を指してしまい、事故再現が崩れます。

## 設計判断 7: ガードレール判定そのものをイベント化する

よくある誤りは、「危険ツールを最終的に実行したか」しか記録しないことです。しかし本当に重要なのは、**その前段でどのポリシーが評価されたか**です。

例えば、削除系ツールの前に

* actor が社内ユーザーか
* 承認者が存在するか
* 対象リソースが同一テナントか
* 24時間以内に同一顧客への削除操作が無かったか

を見ているなら、その評価事実をイベントとして残すべきです。

```
tool_span.add_event(
    "policy.checked",
    {
        "policy.name": "destructive_tool_requires_approval",
        "policy.result": "allow",
        "approval.id": approval_id,
        "approval.type": "human",
    },
)
```

これがあると、監査で「削除は行われたが承認規程は守られていたか」に答えられます。逆に無いと、実行結果だけ見えて意思決定統制は見えません。

## 実装パターン: トレース、監査、評価を同時に出すラッパー

実装で重要なのは、各開発者が毎回手書きしないことです。観測設計は共通ライブラリ化しないと抜け漏れます。

```
class ObservedToolExecutor:
    def __init__(self, tracer, activity_store, evaluator, policy_engine):
        self.tracer = tracer
        self.activity_store = activity_store
        self.evaluator = evaluator
        self.policy_engine = policy_engine

    def execute(self, ctx, tool_name: str, arguments: dict, reasoning: str, evidence_ids: list[str]):
        with self.tracer.start_as_current_span("execute_tool") as span:
            span.set_attribute("gen_ai.tool.name", tool_name)
            span.set_attribute("agent.decision.reasoning", reasoning)
            span.set_attribute("agent.decision.evidence.count", len(evidence_ids))
            span.set_attribute("agent.decision.evidence.ids", json.dumps(evidence_ids))

            policy = self.policy_engine.check(ctx, tool_name, arguments)
            span.add_event("policy.checked", policy.to_event())
            self.activity_store.append(policy.to_activity_event(ctx, span))

            if not policy.allowed:
                span.set_status(Status(StatusCode.ERROR, "policy_blocked"))
                self.activity_store.append(blocked_event(ctx, tool_name, span))
                raise PermissionError("tool blocked by policy")

            self.activity_store.append(approved_event(ctx, tool_name, arguments, span))

            result = run_tool(tool_name, arguments)
            evals = self.evaluator.score_tool(tool_name, arguments, result)

            span.set_attribute("gen_ai.evaluation.name", "ToolSelectionScore")
            span.set_attribute("gen_ai.evaluation.score.value", evals.tool_selection_score)
            span.add_event("evaluation.argument_validity", {"score": evals.argument_validity_score})

            self.activity_store.append(completed_event(ctx, tool_name, result, span))
            return result
```

このラッパーの利点は、開発者が `execute_tool(...)` を呼ぶだけで次が揃うことです。

* span属性
* policy event
* Activity Stream
* evaluation attributes

観測品質は文化ではなく、**SDK化**で担保するのが正解です。

## クエリ例: 事故調査で本当に欲しい問い合わせ

### 1. 低品質かつ危険操作を含むトレースを抽出する

```
SELECT
  trace_id,
  MIN(occurred_at) AS started_at,
  MAX(tool_name) FILTER (WHERE tool_risk = 'destructive') AS destructive_tool,
  AVG((metadata->>'tool_selection_score')::float) AS avg_tool_score
FROM activity_events
WHERE occurred_at >= now() - interval '24 hours'
  AND workflow_name = 'customer_support'
GROUP BY trace_id
HAVING AVG((metadata->>'tool_selection_score')::float) < 0.7
ORDER BY started_at DESC;
```

### 2. 同一承認者が短時間に多すぎる危険操作を通していないか確認する

```
SELECT
  approval_id,
  COUNT(*) AS destructive_runs
FROM activity_events
WHERE event_type = 'tool.execution.approved'
  AND tool_risk = 'destructive'
  AND occurred_at >= now() - interval '1 hour'
GROUP BY approval_id
HAVING COUNT(*) >= 10
ORDER BY destructive_runs DESC;
```

### 3. ループ停滞したトレースを開発者レビュー用に抜く

```
SELECT
  trace_id,
  COUNT(*) FILTER (WHERE event_type = 'tool.execution.completed') AS tool_runs,
  MAX((metadata->>'loop_risk_score')::float) AS max_loop_risk
FROM activity_events
WHERE occurred_at >= now() - interval '7 days'
GROUP BY trace_id
HAVING MAX((metadata->>'loop_risk_score')::float) > 0.8
ORDER BY max_loop_risk DESC;
```

ここでのポイントは、トレースストアだけでも監査DBだけでも、この問いのすべてには答えづらいということです。両者が必要で、評価も要る。これが3層分離の実務的根拠です。

## よくある落とし穴

### 「トレースを取れば全部見える」と思い込む

見えるのは経路です。見えないのは、統制、承認、責任境界、長期履歴です。トレースは強力ですが万能ではありません。

### 監査ログを可読性重視のJSON文字列で保存する

監査では、見た目のきれいさより再検索性です。`actor_id`、`tool_name`、`approval_id`、`trace_id` を独立列にしないと後で詰みます。

### 推論本文を取りすぎる

機密漏洩、保持コスト、UIノイズの三重苦です。必要なときだけ深掘りする設計にしてください。

### 低品質を例外に変換しようとする

品質劣化は多くの場合、例外ではありません。例外中心のアラート思想を捨てない限り、サイレントドリフトは見えません。

### ループ回数だけで異常判定する

探索と停滞を区別できません。状態停滞を見るべきです。

### `trace_id` を監査レイヤーへ渡していない

この1点だけで、後からの因果追跡がほぼ不可能になります。

## 小規模チーム向けの現実解

「そこまで作る余裕がない」というチームもあるはずです。その場合でも、最低限ここまではやってください。

1. `invoke_agent` / `gen_ai.chat` / `execute_tool` の3階層スパン
2. `agent.decision.reasoning` を要約形で保存
3. 高リスクツールだけ `ActivityEvent` を別テーブルへ保存
4. `trace_id` と `approval_id` を監査イベントに含める
5. `ToolSelectionScore` だけでもスパンへ載せる

この5つがあれば、少なくとも「何が起きたか」「なぜそうしたか」「誰の委任か」の三問には答えやすくなります。

## まとめ

AIエージェントの可観測性は、従来APMの延長では足りません。追いたい対象が、処理から判断へ、実行から委任へ、例外から品質劣化へ拡張しているからです。

そのための実装原則は明確です。

1. **トレーシング層（OTel GenAI）** で、ワークフロー、推論、ツール、検索の因果経路を取る
2. **品質評価層（Eval-on-Span）** で、ツール選択や回答根拠性をスパンへ載せる
3. **Activity Stream層** で、委任、承認、危険操作、権限文脈を長期保存する

私なら、最初の1週間でやることは次の順です。

1. `execute_tool` スパンに `agent.decision.reasoning` と `agent.decision.risk` を追加する
2. 危険ツール前後だけ `activity_events` テーブルへ保存する
3. `ToolSelectionScore` の7日移動平均ダッシュボードを作る

これだけでも、次の障害で調査時間は大きく変わります。エージェント観測の本質は「たくさん残すこと」ではありません。**誤った判断に到達した因果連鎖を、再現可能な形で残すこと**です。

---

### こちらもよく読まれています
