---
id: "2026-04-27-aiエージェントの作業ログをopentelemetryで追跡してみた-01"
title: "AIエージェントの作業ログをOpenTelemetryで追跡してみた"
url: "https://zenn.dev/dp_qb/articles/ai-agent-otel-tracing"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "OpenAI", "GPT"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

## はじめに

AIエージェントにコード修正や調査を任せる機会が増えてきました。便利な一方で、実運用に近づけるほど「何をしていたのか」が見えづらくなります。

たとえば、次のような疑問が出ます。

* どのファイルを読んでから判断したのか
* どのツール呼び出しに時間がかかったのか
* LLMへの問い合わせ回数はどれくらいか
* 失敗したコマンドの前後で何をしていたのか
* 最終回答に使われた根拠はどの作業から来たのか

通常のログでも追えますが、AIエージェントの作業は「計画」「推論」「ツール実行」「再計画」「検証」が入り混じります。時系列ログだけだと、処理のまとまりや親子関係が見えません。

そこで今回は、AIエージェントの作業ログを **OpenTelemetry の Trace として記録**してみました。

Node.jsで小さなエージェントランナーを作り、ファイル操作、シェル実行、LLM呼び出し、テスト実行を span として送信し、Jaegerで可視化します。この記事では、その構成、実装、見え方、やってみて分かった設計上の注意点をまとめます。

## なぜAIエージェントにOpenTelemetryを使うのか

OpenTelemetryは、アプリケーションの分散トレーシング、メトリクス、ログを扱うための標準的な仕組みです。Web APIであれば、HTTPリクエストを起点にDBクエリや外部API呼び出しを追跡する用途でよく使われます。

AIエージェントも構造としてはかなり近いです。

* ユーザー依頼が1つのリクエストになる
* 計画生成が内部処理になる
* ファイル読み取りやコマンド実行が外部呼び出しになる
* LLM API呼び出しが高コストな外部依存になる
* テスト実行や検証が後続処理になる

つまり、AIエージェントの作業を1つの trace とみなし、その中に複数の span を作ると自然に表現できます。

ログだけの場合、すべてのイベントが横一列に並びます。

一方でTraceにすると、「このツール実行はどの計画に属していたのか」「このテストはどの修正の検証なのか」が親子関係として残ります。あとから作業を調査するときに、この差はかなり大きいです。

## 今回作ったもの

今回は本格的なエージェントフレームワークではなく、検証用に小さなNode.js製ランナーを作りました。

ランナーが行う処理は次の通りです。

1. ユーザータスクを受け取る
2. 作業計画を生成する
3. 対象ファイルを読む
4. シェルコマンドを実行する
5. LLM呼び出しを模した処理を行う
6. パッチ適用を模した処理を行う
7. テストコマンドを実行する
8. 最終結果をまとめる

最初の検証では観測設計を確認したかったので、LLM呼び出し部分はダミー関数にしています。代わりに、入力トークン数、出力トークン数、モデル名、レイテンシを属性として span に記録しました。

構成は次のようにしました。

OpenTelemetry Collectorを挟んだのは、後からJaeger以外のバックエンドに切り替えやすくするためです。最初からアプリケーションがJaegerに直接依存すると、検証は簡単ですが実運用に寄せにくくなります。

## 検証環境

手元では次の環境で確認しました。

* macOS
* Node.js 20系
* TypeScript
* Docker Compose
* OpenTelemetry Collector
* Jaeger all-in-one

ディレクトリ構成はこのようにしました。

```
agent-otel-demo/
  docker-compose.yml
  otel-collector-config.yaml
  package.json
  src/
    telemetry.ts
    agent.ts
    tools.ts
    llm.ts
    index.ts
```

今回の主役は `telemetry.ts` と `agent.ts` です。

## CollectorとJaegerを起動する

まず、OpenTelemetry CollectorとJaegerをDocker Composeで立てます。

```
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otelcol/config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otelcol/config.yaml
    ports:
      - "4318:4318"
    depends_on:
      - jaeger

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "4317:4317"
```

Collectorの設定は次のようにしました。

```
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:

exporters:
  otlp/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true

  debug:
    verbosity: detailed

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/jaeger, debug]
```

JaegerはOTLPを受け取れるため、CollectorからはOTLP exporterで送ります。`debug` exporter も有効にしておくと、Jaeger UIを見る前にCollectorへspanが届いているか確認できて便利です。

起動します。

Jaeger UIは次のURLで開けます。

## Node.js側のOpenTelemetry設定

Node.js側では、`@opentelemetry/sdk-node` と OTLP HTTP exporter を使いました。

```
import { NodeSDK } from "@opentelemetry/sdk-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { resourceFromAttributes } from "@opentelemetry/resources";
import {
  ATTR_SERVICE_NAME,
  ATTR_SERVICE_VERSION,
} from "@opentelemetry/semantic-conventions";

export function startTelemetry() {
  const sdk = new NodeSDK({
    resource: resourceFromAttributes({
      [ATTR_SERVICE_NAME]: "agent-runner",
      [ATTR_SERVICE_VERSION]: "0.1.0",
      "deployment.environment": "local",
    }),
    traceExporter: new OTLPTraceExporter({
      url: "http://localhost:4318/v1/traces",
    }),
  });

  sdk.start();

  process.on("SIGTERM", async () => {
    await sdk.shutdown();
  });

  process.on("SIGINT", async () => {
    await sdk.shutdown();
    process.exit(0);
  });

  return sdk;
}
```

重要なのは、`service.name` を明示することです。これを入れないとJaeger側でサービスを探しづらくなります。

OpenTelemetry JSの現在のドキュメントでは、コードでResource属性を追加する場合に `resourceFromAttributes` を使う例が示されています。古いサンプルでは `new Resource(...)` を使っているものもありますが、新しく書くならこの形に寄せるのがよさそうです。

## どの単位をspanにするか

最初に悩んだのは、AIエージェントの何をspanにするかです。

細かくしすぎるとノイズが増えます。逆に粗すぎると、Traceにする意味が薄れます。

いくつか試した結果、今回は次の粒度にしました。

| span名 | 内容 |
| --- | --- |
| `agent.run` | ユーザー依頼全体 |
| `agent.plan` | 作業計画の生成 |
| `tool.read_file` | ファイル読み取り |
| `tool.search` | コード検索 |
| `gen_ai.client.operation` | LLM呼び出し |
| `tool.apply_patch` | コード変更 |
| `tool.exec` | コマンド実行 |
| `agent.finalize` | 最終回答の生成 |

ポイントは、「1つのspanがあとから見て意味のある作業単位であること」です。

たとえば、LLMのストリーミング出力をトークン単位でspanにするのは細かすぎます。そこはspan eventとして記録する方が扱いやすいです。

## エージェント実行全体をtraceにする

ユーザー依頼1件を `agent.run` というroot spanにします。

```
import { trace, SpanStatusCode } from "@opentelemetry/api";

const tracer = trace.getTracer("agent-runner");

export async function runAgent(input: string) {
  return tracer.startActiveSpan("agent.run", async (span) => {
    span.setAttributes({
      "agent.input.length": input.length,
      "agent.mode": "local-demo",
    });

    try {
      const plan = await createPlan(input);
      const files = await inspectFiles(plan);
      const draft = await callModel(input, files);
      await applyPatch(draft);
      const testResult = await runTests();
      const final = await finalize(testResult);

      span.setAttribute("agent.result", testResult.ok ? "success" : "failed");

      if (!testResult.ok) {
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: "test failed",
        });
      }

      return final;
    } catch (error) {
      span.recordException(error as Error);
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error instanceof Error ? error.message : "unknown error",
      });
      throw error;
    } finally {
      span.end();
    }
  });
}
```

`startActiveSpan` を使うと、その中で作ったspanが自動的に親子関係を持ちます。

この親子関係が崩れると、Jaeger上で作業がバラバラに見えてしまいます。AIエージェントの可観測性では、ここがかなり重要でした。

## 作業計画をspanにする

AIエージェントは、最初にざっくり計画を作ることが多いです。

この計画は後続のツール実行を解釈するための文脈になります。そこで `agent.plan` としてspanを作りました。

```
async function createPlan(input: string) {
  return tracer.startActiveSpan("agent.plan", async (span) => {
    const plan = [
      "関連ファイルを探索する",
      "実装箇所を特定する",
      "最小変更で修正する",
      "テストを実行する",
    ];

    span.setAttribute("agent.plan.step_count", plan.length);

    span.addEvent("plan.created", {
      "agent.plan.steps": JSON.stringify(plan),
    });

    span.end();
    return plan;
  });
}
```

ここで迷ったのが、計画の中身を attribute に入れるか event に入れるかです。

attributeは検索や集計に使いやすい一方で、長い文字列や配列には向きません。計画本文のように長くなる可能性があるものは、eventに入れる方が扱いやすいと感じました。

今回の方針は次の通りです。

* 検索・絞り込みに使う値は attribute
* 長文や詳細ログは event
* 機微情報を含む可能性がある本文は保存しないか、短く丸める

AIエージェントではプロンプトやファイル内容を扱うので、ここを雑にするとすぐにログが危険になります。

## ツール実行をspanにする

次に、ファイル読み取りやコマンド実行をspan化します。

```
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { SpanStatusCode } from "@opentelemetry/api";

const execFileAsync = promisify(execFile);

export async function runCommand(command: string, args: string[]) {
  return tracer.startActiveSpan("tool.exec", async (span) => {
    span.setAttributes({
      "tool.name": "exec",
      "process.command": command,
      "process.args": JSON.stringify(args),
    });

    const startedAt = performance.now();

    try {
      const result = await execFileAsync(command, args, {
        timeout: 30_000,
        maxBuffer: 1024 * 1024,
      });

      span.setAttributes({
        "process.exit_code": 0,
        "process.stdout.length": result.stdout.length,
        "process.stderr.length": result.stderr.length,
        "tool.duration_ms": Math.round(performance.now() - startedAt),
      });

      return result;
    } catch (error: any) {
      span.setAttributes({
        "process.exit_code": error.code ?? -1,
        "process.stdout.length": error.stdout?.length ?? 0,
        "process.stderr.length": error.stderr?.length ?? 0,
      });

      span.recordException(error);
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error.message,
      });

      throw error;
    } finally {
      span.end();
    }
  });
}
```

実際に `npm test` を失敗させてみると、Jaeger上では `tool.exec` が赤く表示されました。

通常のログだと、テスト失敗のstderrを探しに行く必要があります。Traceだと、失敗したspanを起点に前後の作業へたどれます。

ただし、stdoutやstderrの全文をspanに入れるのはやめました。理由は3つあります。

* 出力が大きいとバックエンドを圧迫する
* シークレットが混ざる可能性がある
* Jaeger UI上で読みにくい

代わりに、長さと終了コードだけをattributeに入れ、必要ならローカルログのファイルパスをeventに残す方針にしました。

## LLM呼び出しをspanにする

AIエージェントで最も見たいのは、やはりLLM呼び出しです。

OpenTelemetryにはGenerative AI向けのsemantic conventionsがあります。今回はそれに寄せて、次のような属性を記録しました。

* `gen_ai.operation.name`
* `gen_ai.provider.name`
* `gen_ai.request.model`
* `gen_ai.request.temperature`
* `gen_ai.usage.input_tokens`
* `gen_ai.usage.output_tokens`

```
export async function callModel(prompt: string, context: string[]) {
  return tracer.startActiveSpan("gen_ai.client.operation", async (span) => {
    span.setAttributes({
      "gen_ai.operation.name": "chat",
      "gen_ai.provider.name": "openai",
      "gen_ai.request.model": "gpt-4.1-mini",
      "gen_ai.request.temperature": 0.2,
      "agent.prompt.length": prompt.length,
      "agent.context.file_count": context.length,
    });

    const inputTokens = estimateTokens(prompt + context.join("\n"));

    try {
      await sleep(820);

      const output = {
        text: "テスト対象の関数に境界値チェックを追加します。",
        outputTokens: 74,
      };

      span.setAttributes({
        "gen_ai.usage.input_tokens": inputTokens,
        "gen_ai.usage.output_tokens": output.outputTokens,
      });

      span.addEvent("gen_ai.response.completed", {
        "gen_ai.response.finish_reasons": JSON.stringify(["stop"]),
      });

      return output.text;
    } finally {
      span.end();
    }
  });
}
```

ここでも、プロンプト全文は保存しませんでした。

検証のために一度だけプロンプト全文をeventへ入れてみましたが、すぐに「これは危ない」と感じました。ソースコード、環境変数名、ユーザーの依頼内容、社内用語などがそのまま観測基盤へ流れるからです。

AIエージェントの可観測性では、**見たい情報と保存してよい情報を分ける**必要があります。

個人的には、LLM呼び出しで最初に記録するなら次の程度で十分だと思います。

```
gen_ai.operation.name
gen_ai.provider.name
gen_ai.request.model
gen_ai.usage.input_tokens
gen_ai.usage.output_tokens
agent.llm.retry_count
```

プロンプト本文や生成本文は、デバッグ時だけ明示的にサンプリングするくらいが現実的です。

## attributeの命名

OpenTelemetryにはHTTPやDBなどのsemantic conventionsがあります。2026年4月時点ではGenerative AI向けの規約も用意されているため、LLM呼び出しは `gen_ai.*` に寄せるのがよさそうです。

一方で、エージェントの計画、ツール実行、パッチ適用などはアプリケーション固有の意味も多いため、今回は `agent.*` と `tool.*` を使いました。

```
service.name
service.version
deployment.environment

process.command
process.args
process.exit_code

agent.session_id
agent.task_id
agent.step_index
agent.result

tool.name
tool.input_hash
tool.output_size

gen_ai.operation.name
gen_ai.provider.name
gen_ai.request.model
gen_ai.usage.input_tokens
gen_ai.usage.output_tokens
```

個人的に重要だと感じたのは、`agent.session_id` と `agent.task_id` です。

Trace IDだけでも1回の実行は追えます。しかし実際のAIエージェントでは、1つの会話セッション内で複数の依頼が発生します。会話単位でまとめたい場合、session IDをattributeに入れておくと便利です。

```
span.setAttributes({
  "agent.session_id": sessionId,
  "agent.task_id": taskId,
});
```

Jaegerで検索するときも、`agent.session_id` があるとかなり追いやすくなりました。

## Traceの見え方

実際にランナーを実行すると、Jaegerでは次のようなTraceになりました。

```
agent.run                    2.41s
  agent.plan                 8ms
  tool.search                124ms
  tool.read_file             19ms
  tool.read_file             15ms
  gen_ai.client.operation    822ms
  tool.apply_patch           34ms
  tool.exec                  1.28s
  agent.finalize             21ms
```

この表示だけで、どこに時間がかかっているか分かります。

今回の実行では、`tool.exec`、つまりテスト実行が最も長く、次にLLM呼び出しが長いという結果でした。これは想定通りです。

面白かったのは、コード検索やファイル読み取りが思ったより目立つことです。1回1回は短いのですが、エージェントが迷って探索を繰り返すと、全体時間の中で無視できなくなります。

AIエージェントの高速化というとLLMのモデル選択に目が行きがちですが、実際には「無駄な探索を減らす」ことも効きます。Traceにすると、その無駄が見えます。

## 失敗ケースを追う

次に、わざとテストが失敗するケースを作りました。

`npm test` が終了コード1で落ちるようにして実行すると、Traceは次のようになりました。

```
agent.run                    error
  agent.plan                 ok
  tool.search                ok
  tool.read_file             ok
  gen_ai.client.operation    ok
  tool.apply_patch           ok
  tool.exec                  error
```

`tool.exec` spanには次の属性が入りました。

```
process.command = npm
process.args = ["test"]
process.exit_code = 1
process.stdout.length = 1840
process.stderr.length = 612
```

これだけでも、失敗の種類がかなり分かります。

さらに `recordException` を入れているので、Jaeger上でエラーメッセージも確認できます。

```
span.recordException(error);
span.setStatus({
  code: SpanStatusCode.ERROR,
  message: error.message,
});
```

ここで大事なのは、失敗した子spanだけでなく、root spanである `agent.run` も error にすることです。

子spanが失敗していても、root spanが success のままだと、一覧で見たときに成功扱いになります。エージェント全体として失敗なら、rootにも結果を反映させる方が調査しやすいです。

## retryをどう表現するか

LLM APIや外部ツールは失敗することがあります。そこで、リトライもTraceで表現してみました。

最初は、1つのLLM spanの中に `retry` eventを追加していました。

```
span.addEvent("llm.retry", {
  "agent.llm.retry.attempt": attempt,
  "error.type": "rate_limit",
});
```

これはシンプルですが、各試行のレイテンシが見えません。

そこで、最終的には次のようにしました。

```
gen_ai.client.operation
  gen_ai.client.attempt  error
  gen_ai.client.attempt  ok
```

親spanは論理的な呼び出し全体を表し、子spanの `gen_ai.client.attempt` が個別の試行を表します。

```
async function callModelWithRetry(prompt: string) {
  return tracer.startActiveSpan("gen_ai.client.operation", async (span) => {
    let attempt = 0;

    try {
      while (attempt < 3) {
        attempt += 1;

        try {
          const result = await tracer.startActiveSpan(
            "gen_ai.client.attempt",
            async (child) => {
              child.setAttribute("agent.llm.retry.attempt", attempt);

              try {
                const response = await callProvider(prompt);
                return response;
              } catch (error) {
                child.recordException(error as Error);
                child.setStatus({ code: SpanStatusCode.ERROR });
                throw error;
              } finally {
                child.end();
              }
            },
          );

          span.setAttribute("agent.llm.retry_count", attempt - 1);
          return result;
        } catch (error) {
          if (attempt >= 3) throw error;
        }
      }
    } catch (error) {
      span.recordException(error as Error);
      span.setStatus({ code: SpanStatusCode.ERROR });
      throw error;
    } finally {
      span.end();
    }
  });
}
```

この形にすると、「1回目はrate limitで失敗し、2回目は成功した」という流れがかなり見やすくなります。

## context propagationで詰まった点

実装していて一番詰まったのは、非同期処理で親子関係が切れる問題です。

Node.jsのOpenTelemetryはAsyncLocalStorageを使ってcontextを保持しますが、すべての非同期境界で直感通りに動くとは限りません。特に、自作のキューやイベントエミッタを挟むと、spanがroot扱いになることがありました。

たとえば、最初は次のような実装にしていました。

```
queue.push(async () => {
  await runCommand("npm", ["test"]);
});
```

この場合、キューに入れた時点のcontextと、実際に実行される時点のcontextがずれて、`tool.exec` が `agent.run` の子にならないことがありました。

対策として、enqueue時にcontextを保存し、実行時に復元しました。

```
import { context } from "@opentelemetry/api";

function enqueue(task: () => Promise<void>) {
  const activeContext = context.active();

  queue.push(() => {
    return context.with(activeContext, task);
  });
}
```

これで、キュー越しのツール実行も正しいtraceにぶら下がるようになりました。

AIエージェントは、並列ツール実行、ストリーミング、イベント駆動処理を入れたくなります。そうなるとcontext propagationはかなり重要です。

## 並列実行をどう見せるか

AIエージェントでは、複数のファイル読み取りや検索を並列で実行することがあります。

```
await Promise.all([
  readFile("src/index.ts"),
  readFile("src/agent.ts"),
  searchCode("runAgent"),
]);
```

この場合、Trace上では同じ親spanの下に複数の子spanが並びます。

```
agent.run
  agent.inspect
    tool.read_file
    tool.read_file
    tool.search
```

Jaegerでは横並びのバーとして見えるため、並列実行によってどれだけ時間が短縮されているかが分かります。

ただし、並列数を増やすとTraceも急に読みにくくなります。検証では、20個以上のファイル読み取りspanが並ぶと、UI上ではかなりノイズになりました。

そこで、ファイル読み取りはすべてspanにするのではなく、次のようなルールにするのがよさそうです。

* 明示的なツール呼び出しはspanにする
* 大量の細かいファイル読み取りは親spanに集約する
* 詳細はeventかローカルログに逃がす

可観測性は、細かければ細かいほど良いわけではありません。後から人間が読める粒度にする必要があります。

## eventとspanの使い分け

実装していくと、「これはspanかeventか」で何度も迷いました。

今回の検証では、次の基準に落ち着きました。

| 対象 | 表現 |
| --- | --- |
| 時間を測りたい作業 | span |
| 成功・失敗を見たい作業 | span |
| 親子関係を持たせたい作業 | span |
| 作業中に起きた細かい出来事 | event |
| ストリーミング中の断片 | event |
| 長文の詳細 | 原則保存しない |

たとえば、LLM呼び出し全体はspanです。リトライの各試行もspanにしました。一方で、`finish_reason` や「レスポンス生成完了」はeventにしました。

```
span.addEvent("gen_ai.response.completed", {
  "gen_ai.response.finish_reasons": JSON.stringify(["stop"]),
});
```

ファイル読み取りも、重要なものはspanにします。しかし、内部的に大量に読む設定ファイルまで全部spanにすると見づらくなります。

つまり、「調査したい単位」をspanにするのがよいです。

## ログとの組み合わせ

Traceだけでは、すべての情報を持たせるには向きません。

たとえばテスト失敗時のstdout全文、差分パッチ全文、モデルの生成テキスト全文などは、Traceに入れるには大きすぎます。

実運用を考えるなら、次のような組み合わせが良さそうです。

Traceは「どこで何が起きたか」を見るもの。

ログは「具体的に何が出力されたか」を見るもの。

Metricsは「全体として増えているか、悪化しているか」を見るもの。

AIエージェントでも、この役割分担は普通のアプリケーションと変わりません。

## 実行結果

実際にいくつかのタスクを流して、Jaegerで見ました。

### ケース1: 小さな修正

内容は、関数の境界値チェックを追加してテストするタスクです。

```
合計時間: 2.41s
span数: 9
LLM呼び出し: 1回
コマンド実行: 2回
テスト: success
```

Traceを見ると、処理時間の大半はテスト実行とLLM呼び出しでした。

```
gen_ai.client.operation    822ms
tool.exec                  1.28s
```

このケースでは、ファイル探索の時間は小さく、特に問題はありませんでした。

### ケース2: 対象ファイルを見つけられない

次に、わざと曖昧な依頼を投げました。

この場合、エージェントは関連ファイルを探すために検索を繰り返しました。

```
合計時間: 6.82s
span数: 31
tool.search: 8回
tool.read_file: 14回
LLM呼び出し: 2回
```

Traceを見ると、LLMよりも探索の多さが目立ちます。

これはログだけでは気づきにくい点でした。エージェントが「考えている」ように見えて、実際にはファイルを探し回っているだけということがあります。

この結果を見て、エージェントに次の改善を入れました。

* 最初にディレクトリ構造を読む
* ファイル名候補を絞ってから検索する
* 同じクエリを繰り返さない
* 読んだファイルの要約をキャッシュする

改善後、同じタスクのspan数は31から18まで減りました。

### ケース3: テスト失敗後に再修正

最後に、テストが一度失敗し、その結果を見て再修正するケースです。

```
agent.run
  agent.plan
  tool.search
  tool.read_file
  gen_ai.client.operation
  tool.apply_patch
  tool.exec error
  agent.replan
  gen_ai.client.operation
  tool.apply_patch
  tool.exec ok
  agent.finalize
```

このTraceはかなり分かりやすかったです。

失敗したテスト実行と、その後の再計画が同じTrace内に残ります。エージェントが単に失敗したのではなく、失敗を受けて修正できたことが見えます。

AIエージェントの品質を見るときは、最終成功だけでは不十分です。途中でどれだけ迷ったか、どれだけリカバリしたかも重要です。

Traceはその過程を見るのに向いています。

## トークン使用量をどう扱うか

LLMのトークン使用量は、コストと性能の両方に関係します。

今回はspan attributeとして記録しました。

```
gen_ai.usage.input_tokens
gen_ai.usage.output_tokens
```

Jaegerはメトリクス集計ツールではないので、トークン使用量の集計には向きません。それでも、個別Traceで「この実行はなぜ高かったのか」を見るには十分です。

本格的に運用するなら、同じ値をMetricsとしても出すべきです。

```
agent.llm.input_tokens
agent.llm.output_tokens
agent.llm.request_count
agent.llm.error_count
```

Traceは個別調査、Metricsは傾向把握です。

たとえば、次のような問いはMetricsで見たいです。

* 1日あたりのLLM呼び出し回数
* モデル別のトークン使用量
* タスク種別ごとの平均コスト
* リトライ率
* 失敗率

一方で、次の問いはTraceで見たいです。

* このタスクはなぜ遅かったのか
* この修正はどのファイルを根拠に行われたのか
* この失敗の直前に何をしていたのか
* なぜLLM呼び出しが2回発生したのか

## セキュリティとプライバシー

AIエージェントのObservabilityで最も注意すべきなのは、プロンプトとファイル内容です。

普通のWeb APIでも個人情報やトークンをログに出さないようにしますが、AIエージェントでは漏れやすい情報の範囲が広いです。

たとえば、次のものが簡単に混ざります。

* ユーザーの依頼文
* ソースコード
* 設定ファイル
* エラーログ
* 環境変数名
* APIレスポンス
* LLMへのプロンプト
* LLMの生成結果

そのため、今回の検証では次のルールにしました。

* プロンプト全文は保存しない
* ファイル本文は保存しない
* stdout/stderr全文は保存しない
* 入力はhash化する
* 長さ、件数、終了コードなどのメタデータを中心に保存する
* デバッグ用の全文保存は明示的なフラグがあるときだけにする

入力hashは次のようにしました。

```
import { createHash } from "node:crypto";

export function sha256Short(value: string) {
  return createHash("sha256")
    .update(value)
    .digest("hex")
    .slice(0, 12);
}
```

spanには次のように入れます。

```
span.setAttributes({
  "tool.input_hash": sha256Short(JSON.stringify(input)),
});
```

これなら、同じ入力が繰り返されているかは分かりますが、中身は保存されません。

## サンプリングの考え方

すべてのエージェント実行を詳細にTraceへ送ると、データ量が増えます。

特に、ファイル探索が多いタスクやリトライが多いタスクではspan数が増えます。LLMのプロンプトや出力をeventへ入れている場合は、さらに危険です。

サンプリング方針は、次のように分けるとよさそうです。

* 成功した通常タスクは一部だけ保存
* 失敗したタスクは保存
* レイテンシが閾値を超えたタスクは保存
* コストが高いタスクは保存
* ユーザーが明示的にデバッグ指定したタスクは保存

OpenTelemetry Collector側でtail samplingを使えば、「エラーになったtraceだけ残す」のような制御ができます。

AIエージェントでは、実行が終わるまで成功・失敗が分からないことが多いので、head samplingよりtail samplingの方が合っています。

## 実装して分かったこと

今回やってみて、特に大きかった学びは5つあります。

### 1. TraceはAIエージェントの作業表現と相性がいい

AIエージェントは、単なる関数呼び出しではなく、複数の作業を組み合わせて結果を出します。

Traceにすると、その作業の流れが自然に見えます。

これはログよりも直感的でした。

### 2. LLM呼び出しだけ見ても不十分

最初はLLM呼び出しのレイテンシとトークンだけ見ればよいと思っていました。

しかし実際には、ファイル探索、コマンド実行、テスト、リトライもかなり重要です。

特に、エージェントが迷っているときはLLMよりツール実行が増えます。ここが見えないと、改善点を誤ります。

### 3. spanを増やしすぎると読めない

何でもspanにすると、Traceが読みにくくなります。

AIエージェントは内部イベントが多いので、spanとeventの切り分けが重要です。

今回の感覚では、「人間があとから調査したい作業単位」だけspanにするのがよいです。

### 4. プロンプト全文保存は慎重に扱うべき

プロンプト全文を保存すると、デバッグは楽になります。

しかし、危険な情報もかなり入ります。特にコード修正エージェントでは、対象リポジトリのソースがそのままプロンプトに入ることがあります。

通常時はメタデータだけ保存し、全文は明示的なデバッグモードに限定した方がよいです。

### 5. context propagationは早めに設計する

最初は同期的な処理だけだったので簡単でした。

しかし、キュー、イベント、並列実行を入れると、spanの親子関係が崩れやすくなります。

後から直すと大変なので、エージェント基盤を作る段階でcontextをどう渡すか決めておくべきです。

## 実運用に入れるなら

今回の検証はローカルでしたが、実運用するなら次のような構成にしたいです。

特に必要なのは、Collector側の制御です。

* サンプリング
* 属性の削除
* 機微情報のマスク
* バックエンド振り分け
* 環境ごとの設定切り替え

アプリケーション側で全部やるより、Collector側に寄せた方が運用しやすいです。

たとえば、ローカルではdebug exporterへ出し、本番ではTrace backendへ送り、特定属性は削除する、といったことができます。

## どの属性を標準化したいか

AIエージェントを継続的に改善するなら、属性名をチーム内で揃えることが重要です。

最低限、次の属性は決めておくとよさそうです。

```
agent.session_id
agent.task_id
agent.step_id
agent.step_type
agent.result
agent.error_type

tool.name
tool.input_hash
tool.output_size
tool.duration_ms

gen_ai.operation.name
gen_ai.provider.name
gen_ai.request.model
gen_ai.usage.input_tokens
gen_ai.usage.output_tokens
agent.llm.retry_count
```

属性名が揺れると、検索や集計が面倒になります。

たとえば、ある場所では `model`、別の場所では `llm.model`、さらに別の場所では `gen_ai.request.model` のようになると、あとから分析しづらくなります。

OpenTelemetryのsemantic conventionsに合わせられるところは合わせ、足りない部分は自分たちのprefixを決めるのが現実的です。

## まとめ

AIエージェントの作業ログをOpenTelemetryで追跡してみたところ、Traceとの相性はかなり良いと感じました。

特に、次の点が見えるようになったのが大きいです。

* 1つの依頼の中で何が起きたか
* どのツール実行に時間がかかったか
* LLM呼び出しが何回発生したか
* テスト失敗後にどうリカバリしたか
* エージェントが迷って探索を繰り返していないか

一方で、何でもTraceに入れればよいわけではありません。spanの粒度、eventとの使い分け、プロンプトやファイル内容の扱い、サンプリング設計は慎重に考える必要があります。

今回の検証で一番の気づきは、AIエージェントの品質改善には「最終結果」だけでなく「途中の作業過程」が必要だということです。

成功したかどうかだけを見ても、エージェントが賢く動いたのか、たまたま成功したのかは分かりません。Traceを見ると、調査、判断、修正、検証の流れが残ります。

AIエージェントを実験段階から運用段階へ進めるなら、OpenTelemetryで作業過程を観測できるようにしておく価値は十分にあります。

## 参考
