---
id: "2026-05-20-splunk-ai-agent-monitoring-と-otel-genai-spanの計装202-01"
title: "Splunk AI Agent Monitoring と OTel GenAI Spanの計装(2026/4時点)"
url: "https://zenn.dev/gen_sobunya/articles/splunk-ai-agent-otel-attributes"
source: "zenn"
category: "construction"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "OpenAI", "Python"]
date_published: "2026-05-20"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

SplunkでObservability Solutions Architectをしている髙柴です。今月の[Splunk公式ブログ](https://www.splunk.com/ja_jp/blog/observability/using-observability-to-identify-failures-in-ai-powered-systems.html)では、Splunk Observability CloudのAI Agent MonitoringとAI Infrastructure Monitoringを使い、AIエージェントのアプリケーション処理からGPUまでを追跡するデモを紹介しました。

<https://www.splunk.com/ja_jp/blog/observability/using-observability-to-identify-failures-in-ai-powered-systems.html>

このZenn記事では、検証用アプリケーション作成時に得られたOpenTelemetry GenAI関連のSpan属性と、AI Agent Monitoringの機能に関する知見を書き残します。

本記事は入門解説よりも、開発者サポートを目的としています。LLMを利用したアプリにOTel自動計装を入れてみたものの、期待したTrace/Spanが出力されず、追加の計装や設定を検討している方がターゲットです。

コードやライブラリ・UIの表記は2026/4/28時点でのものとなります。検証はSplunk Observability Cloud(jp0 Realm)で行いました。

Splunk Observability for AIとOpenTelemetry GenAI Semantic Conventionsはまだ動きが大きい領域なので、仕様の断定ではなく、今回の検証環境で確認できた対応表として読んでください。

## はじめに

Splunk Observability Cloudの画面で「AI Agent Monitoringっぽい表示」を出すには、単にトレースを送ればよいわけではありません。

OpenTelemetryのGenAI Semantic Conventionsに沿ったspan属性、Splunk GenAI utilityのemitter設定、Collectorのlogs pipeline、Log Observer Connectの設定がそろって初めて、AI Trace、AI Details、レスポンス評価といったAI Agent Monitoringの機能を一通り活用できる状態となります。

特にハマりやすいのは、`gen_ai.input.messages` や `gen_ai.output.messages` がspan属性として見えているかどうかだけを見てしまう点です。AI Detailsや評価イベントまで含めると、通常のアプリケーションログとは別にOTLP logsとHEC経由のイベント取り込みが必要になります。

この記事では、私が作成したサンプルアプリをもとに、次の2つを整理します。

* AI Traceやレスポンス評価を表示するために必要だったGenAI span属性とCollector設定
* `splunk-otel-util-genai` のPython APIが、どの `gen_ai.*` span属性になり、Splunk Observability CloudのAI Agent Monitoring上の表示とどう関連するか

なお、実プロダクトでは、まずzero-code instrumentationを試し、足りない属性や表現したい業務上の区切りだけを手動計装で補うのが現実的です。本記事のように、最初から全てを手動spanで作ると、フレームワークやSDKがすでに出してくれる情報と重複しやすくなります。

## 今回のサンプル構成

サンプルアプリは、社内サポート問い合わせを想定した簡単なAIエージェントです。

* `orchestrator-api`: ユーザーの質問を受け取り、プレイブック検索ツールを実行する
* `worker-agent`: orchestratorから渡されたプロンプトでLLMを呼び出す
* `vLLM` または `Ollama`: OpenAI互換APIとしてLLMを提供する
* `Splunk OpenTelemetry Collector`: traces / metrics / logsをSplunk Observability CloudとSplunk Cloud Platformに送る

トレース上は、次のような構造を作ります。

```
workflow support_incident_triage
├── POST /chat
├── execute_tool catalog_lookup
├── POST /delegate
└── invoke_agent resolution_worker
    └── chat Qwen/Qwen2.5-7B-Instruct
```

HTTPのserver / client spanは `opentelemetry-instrument` に任せています。一方、`workflow`、`invoke_agent`、`execute_tool`、`chat` のGenAI spanは `splunk-otel-util-genai` で手動計装しました。

## AI Agent Monitoring上の表示要件

AI Agent MonitoringはAPMの上にGenAI固有の解釈を載せる機能です。ただし、AI Traceを見るだけなのか、AI Detailsの入出力まで見るのか、レスポンス評価まで使うのかで必要な設定は変わります。

今回の検証で必要になったものを、表示したい内容ごとに分解すると次のようになります。

| 表示したい内容 | アプリケーション / Collector 側の責務 | 今回の設定 |
| --- | --- | --- |
| AI Trace と AI span として認識させる | `gen_ai.operation.name` を持つ span を送る | `invoke_workflow` / `invoke_agent` / `execute_tool` / `chat` |
| Agents page の基本メトリクスを表示する | traces / metrics を収集し、histogram を Splunk Observability Cloud に送る | `signalfx.send_otlp_histograms: true` |
| AI Details に入出力やメタデータを出す | message content を capture し、GenAI content logs も送る | `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true` と `SPAN_AND_EVENT` |
| レスポンス評価を表示する | evaluation package、評価用 LLM、HEC、Log Observer Connect を設定する | DeepEval + `splunk_hec/logs` exporter |
| 評価イベントと trace を関連付ける | Splunk Cloud / Enterprise の events index を Log Observer Connect で Observability Cloud に紐付ける | Settings > AI Agent Monitoring で index を指定 |

Splunkのドキュメントでも、Agents pageにhistogram metricsが必要であること、評価を有効にする場合はHEC、Log Observer Connect、Collectorのlogs pipeline設定が必要であると説明されています。

<https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/set-up-ai-agent-monitoring>

また、Splunkの概念整理では、AI Agent Monitoringが認識するspan kindは [OpenTelemetry GenAI Attributes](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/#genai-attributes) に定義されている `gen_ai.operation.name=<value>` で識別されます。今回のサンプルアプリケーションでは、`chat`、`execute_tool`、`invoke_agent`、`invoke_workflow` を付与しています。Splunkで対応済みの `gen_ai.operation.name` 値はドキュメントから確認できます。

<https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/key-concepts-in-ai-agent-monitoring>

## レスポンス評価の前提

レスポンス評価は、Splunk Observability Cloud側がプロンプト本文を直接読んで判定しているわけではありません。Splunkの説明では、instrumentation frameworkがDeepEvalを使って評価し、Collectorが評価結果をSplunk Observability Cloudに送信します。

つまり、レスポンス評価の観点では、**Observability Cloudは評価結果をquality scoreとして表示しますが、ユーザーによるinput/outputそのものを評価画面で直接扱うわけではない**という理解になります。なお、input/outputは後述する仕組みでログとしてSplunk Platform側に送信・保存されます。

<https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/monitor-and-troubleshoot-ai-agents-and-applications/monitor-ai-agents-with-splunk-apm>

レスポンス評価を利用するための最低要件は以下の通りです。

* 評価対象になる `AgentInvocation` または `LLMInvocation` spanがある
* 評価の根拠になるinput / output contentがcaptureされている
* `splunk-otel-genai-evals-deepeval` と `splunk-otel-genai-emitters-splunk` がインストールされている
* 評価用LLMにアクセスできる
* 評価結果をSplunk Platform(Cloud/Enterprise)のindexに送るHEC exporterがCollectorにある
* Splunk Observability CloudのAI Agent Monitoring設定でLog Observer Connectのconnection / indexが指定されている

今回の `app/pyproject.toml` では、関連packageを次のように固定しました。

```
"splunk-otel-genai-emitters-splunk==0.1.8",
"splunk-otel-genai-evals-deepeval==0.1.7",
"splunk-otel-util-genai-evals==0.1.7",
"splunk-otel-util-genai==0.1.11",
```

元々、SDKの自動計装だけでサンプルアプリケーションを作るつもりでしたが、OpenAI SDKの自動計装では、ローカル環境とAWS環境で `chat` spanの表示に差分がありました。そのため、今回のデモではLLM呼び出しだけは明示的に `LLMInvocation` を作る方針としています。

## Splunk GenAI emitterの動作とOpenTelemetry Collectorのログパイプライン設定

今回、サンプルアプリケーション作成で最もハマった点はCollectorのlogs pipelineです。

サンプルアプリケーションはJSON構造化ログを `/var/log/ai-agent-demo/*.jsonl` に出しています。そのため最初は、Collectorの `filelog` receiverでログを拾えば、Related logsとAI Detailsが揃うだろうと考えていました。

しかし、実際には次のような差がありました。

| ログ種別 | 出力元 | Collector receiver | Splunk 上の主な用途 |
| --- | --- | --- | --- |
| アプリケーション JSON ログ | `logging` で出したアプリケーションログ | `filelog/agent_api` | Related logs、trace\_id / span\_id 相関 |
| GenAI content logs / evaluation events | Splunk GenAI emitter / OTel logging | `otlp` logs | AI Details の message content、評価結果 |

`chat.request.received`、`tool.catalog_lookup.completed`、`llm.response.completed` のような業務ログは `filelog` で拾えます。これはこれで有用です。trace\_id / span\_idを含めておけば、通常のRelated logsとして十分に使えます。

一方、`gen_ai.input.messages`、`gen_ai.output.messages`、`gen_ai.system_instructions` など、AI Detailsと評価の根拠になるcontentは、Splunk GenAI utility側がOTLP logsとして出していました。そのため、logs pipelineに `otlp` receiverを入れ、アプリケーション側でもlogs exporterのendpointを明示する必要がありました。

今回のCollector設定では、logs pipelineを次のように設定しています。

```
service:
  pipelines:
    logs:
      receivers: [otlp, filelog/agent_api]
      processors: [memory_limiter, batch, resource/local]
      exporters: [debug, splunk_hec/logs]
```

![ログのパイプライン](https://static.zenn.studio/user-upload/deployed-images/33b3895f94474d82899473cc.png?sha=e7b35c5c5add8af05dfd290ed62c34a6d2dd1199)

### アプリケーション側の環境変数

アプリケーションサイドで評価を実施するので、アプリケーションの稼働している環境変数にもいくつか追加の設定が必要です。

今回はドキュメント記載の手順と、Python Agentの設定一覧をもとに設定して特にトラブルがなかったので、全項目の説明は割愛します。今回の検証で明示的に設定した環境変数は下記の通りです。

```
OTEL_INSTRUMENTATION_GENAI_EMITTERS: span_metric_event,splunk
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT: "true"
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT_MODE: SPAN_AND_EVENT
OTEL_INSTRUMENTATION_GENAI_EVALS_SEPARATE_PROCESS: "true"
OTEL_EXPORTER_OTLP_LOGS_ENDPOINT: http://otel-collector:4318/v1/logs
OTEL_EXPORTER_OTLP_LOGS_PROTOCOL: http/protobuf
```

評価用LLMやDeepEval関連の設定は、利用するモデルやネットワーク構成によって変わります。詳しくは公式ドキュメントを確認してください。

<https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/set-up-ai-agent-monitoring#optional-enable-instrumentation-side-evaluations-for-ai-agent-responses-0>

<https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/set-up-ai-agent-monitoring/configure-the-python-agent>

## Splunk GenAI utility で作る span

ここからがコード計装の本丸です。

`splunk-otel-util-genai` のcode-based instrumentationは、`Workflow`、`AgentInvocation`、`LLMInvocation`、`ToolCall` などのデータ型を作り、`handler.start_*` / `handler.stop_*` でspanを開始・終了します。

公式ドキュメントでも、これらの型を使うことでGenAI telemetryがSemantic Conventionsに従い、Splunk Observability Cloudで処理できる形になると説明されています。

<https://help.splunk.com/en/splunk-observability-cloud/observability-for-ai/splunk-ai-agent-monitoring/set-up-ai-agent-monitoring/code-based-instrumentation>

今回の実装では次のAPIを使いました。

| Python API | 出力される span | 主な `gen_ai.operation.name` |
| --- | --- | --- |
| `handler.start_workflow(workflow)` | `workflow support_incident_triage` | `invoke_workflow` |
| `handler.start_agent(worker)` | `invoke_agent resolution_worker` | `invoke_agent` |
| `handler.start_llm(llm_call)` | `chat Qwen/Qwen2.5-7B-Instruct` | `chat` |
| `handler.start_tool_call(tool_call)` | `execute_tool catalog_lookup` | `execute_tool` |

ここで重要なのは、`set_attribute("gen_ai.xxx", ...)` を大量に手書きしているわけではない点です。Splunk GenAI utilityの型に値を入れると、emitterが `gen_ai.*` 属性に変換してくれます。

### Workflow span

orchestratorでは、ユーザーからの `/chat` リクエスト全体を1つのworkflowとして扱っています。

```
workflow = Workflow(
    name="support_incident_triage",
    workflow_type="support-orchestrator",
    input_messages=[InputMessage(role="user", parts=[Text(content=question)])],
    conversation_id=conversation_id,
)
workflow.provider = self.settings.llm_provider_name
handler.start_workflow(workflow)
```

workflow spanは、AI Traceのrootに相当するGenAI spanとして見せるために使いました。OpenTelemetryのGenAI agent span仕様でも、`invoke_workflow` は複数のagent invocationなどをまとめるhigh-level orchestrationとして説明されています。

<https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/>

今回確認した対応は次の通りです。

| Python field | span 属性 | Splunk Observability Cloud での見え方 |
| --- | --- | --- |
| `name` | `gen_ai.workflow.name` | Trace waterfall の workflow 名、Agent flow graph の起点 |
| `workflow_type` | `gen_ai.workflow.type` | Span properties の属性 |
| `provider` | `gen_ai.provider.name` | AI Details / Span properties の provider |
| `conversation_id` | `gen_ai.conversation.id` | 関連する AI interaction の相関キー |
| `input_messages` | `gen_ai.input.messages` | AI Details の input messages |
| `output_messages` / `final_output` | `gen_ai.output.messages` など | AI Details の output messages / final output |
| utility 側の固定値 | `gen_ai.operation.name=invoke_workflow` | AI span kind として workflow 扱い |

`gen_ai.workflow.*` はOTelのGenAI Semantic Conventions側でもdevelopment扱いの領域です。SplunkのUIは `invoke_workflow` をサポートしていますが、他バックエンドへの移植性を強く意識する場合は、利用中のOTel semconvバージョンを確認した方が安全です。

ツール呼び出しは、プレイブック検索を `execute_tool catalog_lookup` として表現しました。

```
tool_call = ToolCall(
    name="catalog_lookup",
    id=str(uuid.uuid4()),
    arguments=request.question,
    tool_type="function",
    tool_description="社内プレイブックカタログをキーワード一致で検索して関連 snippet を返す",
    conversation_id=conversation_id,
)
handler.start_tool_call(tool_call)
retrieval = self.retriever.lookup(request.question, request.fault_mode)
tool_call.tool_result = "\n".join(retrieval.snippets)
handler.stop_tool_call(tool_call)
```

対応表です。

| Python field | span 属性 | Splunk Observability Cloud での見え方 |
| --- | --- | --- |
| utility 側の固定値 | `gen_ai.operation.name=execute_tool` | Trace waterfall / Agent flow graph で tool call として認識 |
| `name` | `gen_ai.tool.name` | span 名、AI Details の tool 名 |
| `id` | `gen_ai.tool.call.id` | Span properties の tool call id |
| `tool_type` | `gen_ai.tool.type` | Span properties の tool type |
| `tool_description` | `gen_ai.tool.description` | Span properties の description |
| `arguments` | `gen_ai.tool.call.arguments` | content capture 有効時に tool input として確認可能 |
| `tool_result` | `gen_ai.tool.call.result` | content capture 有効時に tool output として確認可能 |
| `conversation_id` | `gen_ai.conversation.id` | workflow / agent / chat span との相関 |

OpenTelemetryのGenAI span仕様では、`execute_tool` はLLMが生成した引数でプログラムや外部サービスを呼び出すspanとして扱われます。

<https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/>

今回のサンプルではツール選択自体をLLMにさせていません。厳密には「LLMがtool call argumentsを生成した」わけではなく、ユーザー入力をorchestratorがそのまま検索に渡しています。とはいえ、AI Trace上で「回答前に外部知識参照をした」ことを示す目的では、`execute_tool` として表現するのが最もUI上も読みやすい形でした。

### AgentInvocation span

worker-agentの処理区間は `AgentInvocation` として表現しています。

```
worker = AgentInvocation(
    name="resolution_worker",
    agent_id=self.settings.worker_agent_id,
    description=self.settings.worker_agent_description,
    model=self.settings.model_name,
    system_instructions=request.system_prompt,
    input_messages=[InputMessage(role="user", parts=[Text(content=request.question)])],
    conversation_id=request.conversation_id,
)
worker.provider = self.settings.llm_provider_name
handler.start_agent(worker)
```

対応表です。

| Python field | span 属性 | Splunk Observability Cloud での見え方 |
| --- | --- | --- |
| utility 側の固定値 | `gen_ai.operation.name=invoke_agent` | Agents page / Agent flow graph で agent invocation として認識 |
| `name` | `gen_ai.agent.name` | Agents page の agent 名、Related traces の filter |
| `agent_id` | `gen_ai.agent.id` | Span properties の agent id |
| `description` | `gen_ai.agent.description` | Span properties / AI Details の agent metadata |
| `model` | `gen_ai.request.model` | AI Details の model、LLM 関連メタデータ |
| `provider` | `gen_ai.provider.name` | provider 表示 |
| `conversation_id` | `gen_ai.conversation.id` | interaction 相関 |
| `system_instructions` | `gen_ai.system_instructions` | content capture 有効時に AI Details / content logs |
| `input_messages` | `gen_ai.input.messages` | AI Details の input messages |
| `output_messages` / `output_result` | `gen_ai.output.messages` など | AI Details の output messages、評価対象 |

Agents pageに出したい場合、少なくとも今回の検証では `gen_ai.agent.name` を明示するのが重要でした。SplunkのLangChain / LangGraphのzero-code instrumentationでも、`agent_name` metadataを設定することでchainを `AgentInvocation` として扱う説明があります。フレームワーク側の自動計装でも、追加すべきコードがある点には注意して下さい。

### LLMInvocation span

実際のLLM呼び出しは `LLMInvocation` として表現しています。

```
llm_call = LLMInvocation(
    request_model=self.settings.model_name,
    server_address=parsed_base_url.hostname,
    server_port=parsed_base_url.port,
    input_messages=llm_messages,
    request_temperature=request.temperature,
    request_max_tokens=request.max_tokens,
    conversation_id=request.conversation_id,
)
llm_call.provider = self.settings.llm_provider_name
handler.start_llm(llm_call)
```

レスポンスを受け取った後に、出力やtoken使用量を追記してからspanを閉じます。

```
llm_call.output_messages = [_to_output_message(answer, choice.finish_reason)]
llm_call.response_id = response.id
llm_call.response_model_name = getattr(response, "model", None)
llm_call.response_finish_reasons = [choice.finish_reason or "stop"]

if response.usage:
    llm_call.input_tokens = response.usage.prompt_tokens
    llm_call.output_tokens = response.usage.completion_tokens

handler.stop_llm(llm_call)
```

UtilityとOTel span属性、Splunk側での見え方の対応表を下記にまとめました。

| Python field | span 属性 | Splunk Observability Cloud での見え方 |
| --- | --- | --- |
| `operation` または utility 既定値 | `gen_ai.operation.name=chat` | AI Trace 上の LLM call、LLM service 関連表示 |
| `request_model` | `gen_ai.request.model` | AI Details の request model |
| `provider` | `gen_ai.provider.name` | provider 表示 |
| `server_address` | `server.address` | inferred service / Span properties |
| `server_port` | `server.port` | inferred service / Span properties |
| `request_temperature` | `gen_ai.request.temperature` | Span properties、LLM request parameter |
| `request_max_tokens` | `gen_ai.request.max_tokens` | Span properties、LLM request parameter |
| `conversation_id` | `gen_ai.conversation.id` | interaction 相関 |
| `input_messages` | `gen_ai.input.messages` | AI Details の input messages、評価根拠 |
| `output_messages` | `gen_ai.output.messages` | AI Details の output messages、評価根拠 |
| `response_id` | `gen_ai.response.id` | Span properties |
| `response_model_name` | `gen_ai.response.model` | AI Details / Span properties の response model |
| `response_finish_reasons` | `gen_ai.response.finish_reasons` | Span properties |
| `input_tokens` | `gen_ai.usage.input_tokens` | token usage の集計 |
| `output_tokens` | `gen_ai.usage.output_tokens` | token usage の集計 |

`server.address` / `server.port` はGenAI固有ではありませんが、vLLMやOllamaのようなOpenAI互換endpointをinferred serviceとして見せたい場合に効きます。実際のサービスマップ表現は通信span、host情報、Collector側のenrichmentにも依存するので、これだけで必ず期待通りのノードが出るとは限りません。この点も、今回の検証での観測結果として扱ってください。

## content capture は本番では慎重に扱う

OpenTelemetryのGenAI Semantic Conventionsでは、`gen_ai.input.messages` と `gen_ai.output.messages` はOpt-In属性です。また、仕様ページでも、これらの属性はユーザー情報やPIIを含み得るため注意が必要とされています。

<https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/>

今回のデモでは、AI Detailsと評価を見せることを優先して次の設定にしました。

```
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT: "true"
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT_MODE: SPAN_AND_EVENT
```

ただし、本番でこのまま運用してよいとは限りません。問い合わせ本文、社内ナレッジ、検索結果、system promptがobservability backendやSplunk Cloud Platformのevents indexに送られます。

実運用では、少なくとも次を検討すべきです。

* PII / credential / customer confidential dataを送らない設計にする
* content captureを環境ごとに切り替える
* redaction済みのプロンプトや評価用サマリを送る
* HEC indexの保持期間、アクセス権、監査要件を決める
* 評価用LLMに送ってよいデータの範囲を明確にする

AI Agent Monitoringを有効化することで、プロンプトや回答も観測可能になります。これはデバッグ観点では強力ですが、データガバナンスの観点では新しいデータ流通経路を作ることでもあります。慎重に設定してください。

## AI Trace 上の表示対応まとめ

今回の検証で、Splunk Observability Cloud上の表示と属性の対応はおおむね次のように見えました。

| Splunk 画面 / 表示 | 主に効いた属性・データ | 補足 |
| --- | --- | --- |
| Trace Analyzer の AI traces filter | `gen_ai.operation.name` | GenAI span を含む trace として扱われる |
| Trace waterfall の span ラベル | span name、`gen_ai.operation.name`、agent/tool/model 名 | `invoke_agent resolution_worker`、`chat <model>` など |
| Agent flow graph | `invoke_workflow`、`invoke_agent`、`execute_tool`、`chat` の親子関係 | HTTP span と GenAI span の親子関係も重要 |
| Agents page の agent 名 | `gen_ai.agent.name` | `AgentInvocation.name` から設定 |
| Agent detail の token usage | `gen_ai.usage.input_tokens`、`gen_ai.usage.output_tokens` | LLM response の usage を span に追記 |
| AI Details の metadata | `gen_ai.provider.name`、`gen_ai.request.model`、`gen_ai.response.model` など | span properties と重複して確認できる |
| AI Details の input / output | `gen_ai.input.messages`、`gen_ai.output.messages`、OTLP logs | content capture と logs pipeline が必要 |
| Quality score / Quality issue | DeepEval evaluation events | HEC + Log Observer Connect が必要 |
| Related logs | trace\_id / span\_id 付きの application logs、evaluation logs | `filelog` と `otlp` logs の両方を見る |
| LLM service dependency | `server.address`、`server.port`、HTTP client span | inferred service 表示は通信形態にも依存 |

※正式な仕様表ではなく、2026/4/28時点の検証結果です。

## トラブルシュート観点

最後に、今回の検証で得た切り分け観点をまとめます。

### AI Trace として出ない

まず `gen_ai.operation.name` がspanに付いているか確認します。SplunkがAI span kindとして見る起点はここです。

最低限、LLM呼び出しなら `chat`、agent呼び出しなら `invoke_agent`、ツール呼び出しなら `execute_tool` を出します。

### Agents page に agent が出ない

`invoke_agent` spanと `gen_ai.agent.name` を確認します。LangChain / LangGraphのzero-code instrumentationではmetadataの `agent_name` が重要になります。手動計装では `AgentInvocation(name=...)` を必ず設定します。

### token usage が出ない

LLM responseのusageを `llm_call.input_tokens` と `llm_call.output_tokens` に追記してから `stop_llm()` しているか確認します。

OpenAI互換endpointでも、モデルサーバーやSDKの設定によってusageが返らない場合もあります。その場合は、span側にtoken属性を付けようとしても値がありません。

### AI Details の message が空

次を順番に確認します。

* `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true`
* `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT_MODE=SPAN_AND_EVENT`
* `input_messages` / `output_messages` に `InputMessage` / `OutputMessage` を入れている
* アプリが `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` にlogsを送れる
* Collectorのlogs pipelineに `otlp` receiverが入っている
* logs pipelineのexporterが `splunk_hec` に向いている
* Log Observer ConnectのindexがAI Agent Monitoring設定に紐付いている

`filelog` でアプリケーションログが見えていても、GenAI content logsが届いているとは限りません。

### Quality score が出ない

評価用LLMとHEC側を確認します。

* `splunk-otel-genai-evals-deepeval` が入っている
* `splunk-otel-genai-emitters-splunk` が入っている
* `DEEPEVAL_LLM_BASE_URL` / `DEEPEVAL_LLM_MODEL` / `DEEPEVAL_LLM_API_KEY` が正しい
* `OTEL_INSTRUMENTATION_GENAI_EVALUATION_SAMPLE_RATE` が0になっていない
* `splunk_hec` exporterのtoken / endpoint / indexが正しい
* Splunk Cloud Platform側のHEC tokenが有効
* Observability CloudのAI Agent Monitoring設定でconnection / indexが指定済み

Splunkのドキュメント上、Quality scoreはBias、Hallucination、Relevance、Sentiment、Toxicityを対象に表示されます。評価結果はイベントとして取り込まれるため、APM traceの設定だけを見ていても原因にたどり着けません。

## まとめ

Splunk Observability CloudのAI Agent Monitoringは、OpenTelemetry GenAI spanを送るだけでもAI Traceの入口を作れます。しかし、AI Detailsの入出力、Quality score、Related logsまで揃えるには、span属性、GenAI content logs、評価イベント、HEC、Log Observer Connectの設定をまとめて考える必要があります。

今回の検証で特に重要だったのは次の3点です。

* AI spanとして認識させる中心は `gen_ai.operation.name`
* AI Detailsと評価のためには `input_messages` / `output_messages` とcontent captureが必要
* 通常ログの `filelog` と、GenAI content / evaluation用の `otlp` logsは別経路として考える

AIエージェントの観測では、「spanが出た」だけではまだ半分です。どのagentが、どのtoolを使い、どのmodelに、どの入力を渡し、何を返し、その結果が評価上どうだったのか。そこまでを一連のtraceとして読める状態にして初めて、プロンプト、ツール、モデル、基盤のどこを直すべきか判断しやすくなります。

この記事で解説した全コードは下記リポジトリで公開しています。

<https://github.com/gentksb/splunk-ai-agent-observability-sample>
