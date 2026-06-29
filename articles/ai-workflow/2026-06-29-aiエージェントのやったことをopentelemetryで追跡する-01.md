---
id: "2026-06-29-aiエージェントのやったことをopentelemetryで追跡する-01"
title: "AIエージェントの「やったこと」をOpenTelemetryで追跡する"
url: "https://zenn.dev/daideguchi/articles/agentops-otel-flight-recorder"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "Python", "zenn"]
date_published: "2026-06-29"
date_collected: "2026-06-30"
summary_by: "auto-rss"
query: ""
---

AIエージェントを業務に入れると、便利になる一方で、運用側はすぐに別の問題にぶつかります。

「エージェントは何をしたのか」  
「どの証拠を見て判断したのか」  
「本番変更や高コスト処理は人間が止められるのか」  
「あとから事故調査できる形で残っているのか」

チャット履歴だけでは、これは追いにくいです。そこで、AIエージェントの作業を OpenTelemetry の span と metric にして、通常のオブザーバビリティ基盤で追える形にしてみました。

この記事では、AIエージェント運用のイベントログを OpenTelemetry に変換する小さなデモを作ります。題材は、AIエージェントの作業を記録する `AgentOps Flight Recorder` です。

デモコードはGitHubに置きました。

<https://github.com/daideguchi/agentops-otel-flight-recorder-demo>

## この記事で解く課題

対象は、AIエージェントを業務に入れ始めた platform / SRE / security / support operations のチームです。

解きたい課題は、AIの回答をきれいに見せることではありません。

* AIエージェントがどのツールを呼んだのか分からない
* 本番操作、顧客対応、セキュリティ調査のどこで人間承認が必要だったのか分からない
* 失敗、警告、ポリシーブロックがチャット履歴の中に埋もれる
* 後から事故調査や監査をしようとしても、時系列と証拠がつながらない
* 高リスク操作と高コストなAI呼び出しを同じ画面で追えない

そこで、AIエージェントを「チャット相手」ではなく、運用上の actor として扱います。人間、AIエージェント、API、ロボット、システムの動きを同じ OpenTelemetry の trace / metric に載せ、あとから検索・集計・監査できる形にします。

## 作ったもの

作ったのは、AIエージェントのイベント列を読み込み、以下を出す Python スクリプトです。

* セッションごとの trace
* 作業イベントごとの span
* 人間承認が必要な回数
* block / failed / warning の件数
* リスクスコアの分布
* 推定コスト
* Splunk Observability Cloud へ送るための Collector テンプレート

全体像はこの形です。

今回のデータは、次のようなイベント列です。

```
{
  "event_id": "evt-0007",
  "event_type": "tool_call",
  "actor_type": "ai_agent",
  "phase": "execution",
  "status": "blocked",
  "risk_level": "critical",
  "human_approval_required": true,
  "decision": "blocked_by_policy",
  "summary": "Attempted production deployment was blocked by policy before execution."
}
```

ポイントは、AIエージェントの発話ではなく、運用イベントとして残すことです。

## なぜOpenTelemetryで扱うのか

AIエージェントのログは、最初はアプリ独自のJSONでも十分に見えます。

ただ、実運用ではすぐに次のような検索が必要になります。

* この本番操作を止めた span はどれか
* どのAI呼び出しが高コストだったか
* 人間承認を要求した処理はどこか
* 失敗したテストの前後に何が起きたか
* 複数のエージェント、API、ロボット、人間を同じ時系列で見たい

これは、OpenTelemetry の trace / metric と相性が良いです。

Webリクエストの trace と同じように、AIエージェントの1セッションを trace にし、その中の「計画」「API呼び出し」「テスト実行」「リスク検出」「承認」「引き継ぎ」を span にします。

## イベントをspanにする

今回のデモでは、1つの agent session を親 span にし、その下にイベント span をぶら下げました。

```
session_span = tracer.start_span(
    f"agentops.session/{session_id}",
    start_time=session_start_ns,
    attributes={
        "agentops.session_id": session_id,
        "agentops.case_ids": case_ids,
        "agentops.events_in_session": len(session_events),
    },
)

with trace.use_span(session_span, end_on_exit=False):
    for event in session_events:
        with tracer.start_as_current_span(
            f"{event['phase']}.{event['event_type']}",
            start_time=start_ns,
            end_on_exit=False,
            attributes=as_attributes(event),
        ) as span:
            span.add_event("agentops.summary", {"summary": event["summary"]})
            span.end(end_time=end_ns)

session_span.end(end_time=session_end_ns)
```

span attribute には、検索したい軸を入れます。

```
{
    "agentops.event_id": event["event_id"],
    "agentops.case_id": event["case_id"],
    "agentops.phase": event["phase"],
    "agentops.event_type": event["event_type"],
    "agentops.actor_type": event["actor_type"],
    "agentops.status": event["status"],
    "agentops.risk_level": event["risk_level"],
    "agentops.human_approval_required": event["human_approval_required"],
    "agentops.decision": event.get("decision", "none"),
}
```

ここで大事なのは、本文の自然言語を全部検索対象にするより、まず「運用で切りたい軸」を attribute にすることです。

## 失敗・警告・ブロックをイベントとして足す

AIエージェントの運用では、成功だけを追っても意味がありません。

今回のデモでは、`failed` / `blocked` / `warning` の span に追加イベントを入れています。

```
if event["status"] in {"failed", "blocked", "warning"}:
    span.add_event(
        "agentops.needs_human_review",
        {
            "status": event["status"],
            "risk_level": event["risk_level"],
            "risk_reason": event.get("risk_reason", ""),
        },
    )
```

これで、あとから「人間が見るべきだった箇所」だけを拾いやすくなります。

## metricsにするもの

trace は事故調査に向いています。一方で、日々の運用では metric も必要です。

今回のデモでは、次の metric を出しました。

```
event_counter = meter.create_counter("agentops.events")
approval_counter = meter.create_counter("agentops.approvals.required")
blocked_counter = meter.create_counter("agentops.blocked")
cost_counter = meter.create_counter("agentops.cost.usd.estimate")
duration_histogram = meter.create_histogram("agentops.duration.ms")
risk_histogram = meter.create_histogram("agentops.risk.score")
```

AIエージェント運用でまず見たいのは、モデルの精度だけではありません。

* 人間承認を何回要求したか
* policy block は増えているか
* warning が特定フェーズに偏っていないか
* 高リスク操作と高コスト操作が同時に増えていないか

このあたりを metric にすると、運用改善の会話に乗せやすくなります。

## 動かし方

リポジトリ内のデモは、クラウド認証なしで動くようにしています。

```
git clone https://github.com/daideguchi/agentops-otel-flight-recorder-demo.git
cd agentops-otel-flight-recorder-demo
python3.11 -m venv .venv311
. .venv311/bin/activate
pip install -r demo/requirements.txt
python demo/agentops_otel_demo.py --output-dir evidence/latest-run
```

実行すると、console exporter が span / metric を出し、同時に集計ファイルも作ります。

```
{
  "events_total": 26,
  "cases_total": 3,
  "human_approval_required": 5,
  "blocked_events": 1,
  "failed_events": 1,
  "warning_events": 4,
  "high_or_critical_risk_events": 3
}
```

この結果だけでも、次のようなことが分かります。

* 3つの運用ケースをまたいで26イベントある
* 5回、人間承認が必要になった
* 1回、本番操作がポリシーで止まった
* 失敗と警告が残っている
* 高リスクまたはcriticalなイベントが3件ある

つまり、AIエージェントの「なんとなく動いた」ではなく、「何が起き、どこが危なかったか」を機械的に追えます。

## Splunk Observability Cloudに送るなら

今回はローカルで再現できることを優先しました。

Splunk Observability Cloud に送る場合は、OpenTelemetry Collector を間に置き、OTLP を Splunk 側の endpoint に流す形にできます。

デモにはテンプレートだけ入れています。

```
receivers:
  otlp:
    protocols:
      http:
      grpc:

processors:
  batch:

exporters:
  otlphttp/splunk:
    endpoint: https://ingest.<realm>.signalfx.com/v2/trace/otlp
    headers:
      X-SF-Token: ${SPLUNK_ACCESS_TOKEN}

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlphttp/splunk]
```

本物の token は環境変数で渡し、記事やGitには入れません。

## やってみて分かった設計ルール

AIエージェントの可観測性では、通常のHTTP spanとは違う設計が必要でした。

### 1. actorを必ず分ける

AIエージェント、人間、API、ロボット、システムを同じ `actor` として扱うと、あとから責任境界が分からなくなります。

今回のデモでは `actor_type` を `human` / `ai_agent` / `robot` / `api` / `system` に分けました。

### 2. approvalはログではなく運用イベント

人間承認は、ただのメモではありません。

本番操作を止めたのか、追加証拠を要求したのか、拒否したのか。これはインシデント調査でも監査でも重要です。

そのため `human_approval_required` と `decision` を attribute にしました。

### 3. riskは自然文だけにしない

`risk_reason` には説明文を入れますが、それだけだと集計できません。

そこで `risk_level` と `risk_score` を別に持たせました。

### 4. AIのコストも運用信号

AIエージェントでは、失敗していなくてもコストが問題になることがあります。

今回は `agentops.cost.usd.estimate` を metric にして、あとからフェーズ別・actor別に見られるようにしました。

## まとめ

AIエージェントの運用で怖いのは、エージェントが間違えることだけではありません。

もっと怖いのは、あとから「何が起きたか分からない」ことです。

OpenTelemetry に寄せておくと、AIエージェントの作業も、通常のシステム運用と同じ土俵で見られます。

* セッションを trace にする
* 作業単位を span にする
* 承認・ブロック・リスク・コストを attribute / metric にする
* Splunk Observability Cloud などのバックエンドに送れる形にする

これだけで、AIエージェントは「チャットで動く便利ツール」から、「運用できる作業者」に近づきます。

次は、同じ telemetry を実際の Observability backend に送り、ダッシュボードとアラートまで作ってみます。
