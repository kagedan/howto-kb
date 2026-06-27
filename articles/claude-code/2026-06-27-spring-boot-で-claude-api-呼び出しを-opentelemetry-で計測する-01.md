---
id: "2026-06-27-spring-boot-で-claude-api-呼び出しを-opentelemetry-で計測する-01"
title: "Spring Boot で Claude API 呼び出しを OpenTelemetry で計測する"
url: "https://zenn.dev/propagandist/articles/0004-spring-boot-otel-claude-observability"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "LLM", "zenn"]
date_published: "2026-06-27"
date_collected: "2026-06-28"
summary_by: "auto-rss"
query: ""
---

## この記事について

* **対象読者**：Spring Boot から Claude API を呼んでいて、その**レイテンシ・トークン・コスト・失敗**を可視化したい人／LLM 呼び出しに OpenTelemetry を入れる最小の型を知りたい人
* **得られること**：Spring Boot 3 標準の Micrometer Observation を **OpenTelemetry（OTLP）で送り出し**、Claude 呼び出しを 1 本の span として計測する方法。さらにトークン数と推定コストをメトリクス化し、ローカルの **OTel Collector → Jaeger・Prometheus・Grafana** で確認するところまで
* **前提・環境**：Java 21 / Spring Boot 3.5 / `com.anthropic:anthropic-java` 2.34.0。トレース・メトリクスの確認に Docker（任意）

> この記事は「[Spring Bootから公式Java SDKでClaude APIを呼ぶ最小実装](https://zenn.dev/propagandist/articles/0001-spring-boot-claude-api-java-sdk)」から続く Spring Boot × Claude API シリーズの続編です。クライアントの Bean 化・設定の外出し（`AnthropicClientConfig` / `AnthropicProperties`）は前回までを引き継ぎます。

> バージョン（SDK・Spring Boot・各ツール）とモデル名・料金は\*\*執筆時点（2026年6月）\*\*のものです。最新は公式情報で確認してください。

## なぜ LLM 呼び出しに可観測性が要るか

Claude を本番に組み込んでまず落ち着かなかったのは、「いま何が起きているか」が手元から見えないことでした。

通常の HTTP クライアント呼び出しと違い、LLM 呼び出しは「**遅い・高い・たまに失敗する**」が常態です。とくに次の3点が見えにくくなります。

* どれくらい時間がかかったか（レイテンシ）
* 入力・出力で何トークン使ったか（=コスト）
* どんな理由で止まったか（`end_turn`・`max_tokens`・`refusal` など）

どれも、ログを `grep` して拾うだけでは把握しづらい情報です。**1リクエスト単位のトレース** と **集計用のメトリクス** に乗せれば、まとめて見通せます。OpenTelemetry はその標準で、送信先（バックエンド）は自由に選べます。

> **用語**：**トレース**は1リクエスト全体の処理の連なり、その「処理ひとつ分」が **span**（この記事では Claude 呼び出し1回＝1 span）。**メトリクス**は件数・合計・レイテンシなどを集計した時系列の数値です。トレースは「1回の詳細」、メトリクスは「全体の傾向」を見るのに向きます。

## 結論（先に全体像）

やることは大きく3つです。

1. 依存を足して、Spring Boot の計測データ（トレース・メトリクス）を **OTLP で送る**設定をする
2. Claude 呼び出しを **`Observation`（= span）で包み**、モデル名・トークン・停止理由を属性として乗せる
3. トークン数・推定コストを **メトリクス（Counter）** として記録する

データの流れはこうなります。送信先は自由なので、ここではローカル完結の最小構成にします。

ポイントは、**Claude を呼ぶ SDK 内部の HTTP クライアント（OkHttp）は自動計装されない**ことです。だからこそ、呼び出しを自分で span として包みます。ここがこの記事の中心です。

> **用語**：**計装（instrumentation）** は、コードの中に「ここを計測する」処理を仕込むこと。Spring Boot のように**フレームワークが自動でやってくれる**のが**自動計装**で、対象外のものは自分で span として包む（手動で計装する）必要があります。

なお、この記事のコードは**実際にビルド・起動する検証プロジェクト**で動作確認しています。

## 手順1：依存を足す

可観測性の土台（`actuator`）と、Micrometer の Observation を **OpenTelemetry のトレース・メトリクスとして OTLP で送る**ための依存を追加します。

```
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-actuator") // Observation/メトリクスの土台
    implementation("com.anthropic:anthropic-java:2.34.0")

    // OpenTelemetry：背骨は OTel。Micrometer から OTLP で送る
    implementation("io.micrometer:micrometer-tracing-bridge-otel") // span を OTel として生成
    implementation("io.opentelemetry:opentelemetry-exporter-otlp") // trace を OTLP で送信
    implementation("io.micrometer:micrometer-registry-otlp")       // metrics を OTLP で送信
}
```

バージョン指定が無いのは、これらの**バージョンを** Spring Boot の依存管理（BOM）が解決するからです。Spring Boot のバージョンに整合したものが選ばれます。

> 「Micrometer なのに OpenTelemetry？」と思うかもしれません。Spring Boot 3 は計測の抽象として Micrometer Observation を標準採用しており、`micrometer-tracing-bridge-otel` を入れると **span は OpenTelemetry の実装で生成され、OTLP で送り出されます**。ワイヤ上は紛れもなく OpenTelemetry です。Spring に馴染みつつ OTel に乗れる、というのが採用理由です。より純粋な OpenTelemetry SDK に寄せたいなら `opentelemetry-spring-boot-starter` を使う選択肢もありますが、本記事は Spring 標準の Observation を起点にします。

## 手順2：OTLP の送信先を設定する

`application.yaml` で、送信先（OTel Collector の OTLP/HTTP 受信口）とサンプリング、サービス名を指定します。

```
spring:
  application:
    name: spring-boot-otel-claude-observability  # OTel の service.name になる

management:
  otlp:
    tracing:
      endpoint: http://localhost:4318/v1/traces
    metrics:
      export:
        url: http://localhost:4318/v1/metrics
        step: 5s
  tracing:
    sampling:
      probability: 1.0   # 検証用に全トレースを送る。本番はコストに応じて下げる
```

`spring.application.name` がそのまま OpenTelemetry の `service.name` リソース属性になり、Jaeger や Grafana で「どのサービスのトレース・メトリクスか」を表します。

これで、`/ask` のような受信リクエストには **Spring MVC の server span** が自動で付きます。あとは、その配下に Claude 呼び出しの span を子として加えるだけです。

## 手順3：Claude 呼び出しを span で包む

ここが本題です。実は最初、Jaeger を開いても Claude 呼び出しがトレースに出てこず、しばらく悩みました。原因は、SDK が独自の OkHttp を使っていて自動計装の対象外だったこと。「出てこないなら自分で span にすればいい」と決めたのが、この実装の出発点です。

`ObservedAiAssistant` で、`Observation` を使って Claude 呼び出し全体を 1 本の span として計測します。属性名は [GenAI セマンティック規約](https://opentelemetry.io/docs/specs/semconv/gen-ai/)に寄せています。

```
@Service
@RequiredArgsConstructor
@Slf4j
public class ObservedAiAssistant {

    private final AnthropicClient client;
    private final AnthropicProperties properties;
    private final ObservationRegistry observationRegistry;
    private final MeterRegistry meterRegistry;

    public String ask(String prompt) {
        var params = MessageCreateParams.builder()
                .model(properties.model())
                .maxTokens(properties.maxTokens())
                .system("あなたは簡潔に答えるアシスタントです。")
                .addUserMessage(prompt)
                .build();

        // この呼び出し全体を1つの span として計測する
        Observation observation = Observation.createNotStarted("claude.message", observationRegistry)
                .lowCardinalityKeyValue("gen_ai.system", "anthropic")
                .lowCardinalityKeyValue("gen_ai.request.model", properties.model());

        return observation.observe(() -> {
            try {
                Message response = client.messages().create(params);

                long inputTokens = response.usage().inputTokens();
                long outputTokens = response.usage().outputTokens();
                String finishReason = response.stopReason().map(Object::toString).orElse("end_turn");

                // span に内訳を残す（trace で1リクエストのトークン・停止理由が見える）
                observation.highCardinalityKeyValue("gen_ai.usage.input_tokens", String.valueOf(inputTokens));
                observation.highCardinalityKeyValue("gen_ai.usage.output_tokens", String.valueOf(outputTokens));
                observation.lowCardinalityKeyValue("gen_ai.response.finish_reason", finishReason);

                recordMetrics(inputTokens, outputTokens);

                return response.content().stream()
                        .flatMap(block -> block.text().stream())
                        .map(text -> text.text())
                        .collect(Collectors.joining());
            } catch (AnthropicException e) {
                // observe() が span にエラーを記録してから投げ直す
                log.error("claude api call failed", e);
                throw new IllegalStateException("Failed to call Claude", e);
            }
        });
    }
    // recordMetrics は手順4
}
```

ポイントは3つです。

* **`observe(...)` が開始・終了・例外をまとめて扱う**：`observe` は span を開始し、ラムダを実行し、最後に必ず閉じます。途中で例外が出れば **span にエラーを記録してから投げ直す**ので、失敗もトレースに残ります。
* **`lowCardinalityKeyValue` と `highCardinalityKeyValue` を使い分ける**：低基数（モデル名・`gen_ai.system`・停止理由）は span 属性に加え**メトリクスのタグ**にもなります。一方、トークン数は値の種類が多い（高基数）ので `highCardinalityKeyValue` にして **span 属性だけ**に乗せます。これを取り違えると、メトリクスのタグが爆発（カーディナリティ爆発）して Prometheus を圧迫します。
* **SDK のレスポンスから usage を取り出す**：`response.usage()` に入出力トークン、`response.stopReason()` に停止理由が入っています。

モデル名や `max-tokens` は[前回まで](https://zenn.dev/propagandist/articles/0001-spring-boot-claude-api-java-sdk)と同じく `AnthropicProperties` で設定に切り出しています。

## 手順4：トークン・コストをメトリクスに

span は「1リクエストの詳細」を見るのに向きますが、「今日の合計トークン」「コストの推移」は**メトリクス**の仕事です。`MeterRegistry` で Counter を増やします。

```
private void recordMetrics(long inputTokens, long outputTokens) {
    meterRegistry.counter("gen_ai.client.token.usage",
                    "gen_ai.token.type", "input",
                    "gen_ai.request.model", properties.model())
            .increment(inputTokens);
    meterRegistry.counter("gen_ai.client.token.usage",
                    "gen_ai.token.type", "output",
                    "gen_ai.request.model", properties.model())
            .increment(outputTokens);

    double costUsd = inputTokens / 1_000_000.0 * properties.inputUsdPerMtok()
            + outputTokens / 1_000_000.0 * properties.outputUsdPerMtok();
    meterRegistry.counter("gen_ai.client.cost.usd",
                    "gen_ai.request.model", properties.model())
            .increment(costUsd);
}
```

コストの**単価は設定に外出し**します。料金はモデルと時期で変わるので、コードへ直書きせず `application.yaml` に置いて公式値で更新する方針です。

```
anthropic:
  model: claude-opus-4-8
  max-tokens: 1024
  # コスト計測用の単価（USD / 100万トークン）。下記は Claude Opus 4.8（2026年6月時点）の例。
  input-usd-per-mtok: 5.0
  output-usd-per-mtok: 25.0
```

> 単価は**必ず公式（platform.claude.com）で確認**してください。ここでの目的は「正確な請求額」ではなく、**コストの桁と推移を運用ダッシュボードで把握する**ことです。

ちなみに、手順3で生成した `claude.message` という Observation は、**span と同時に timer メトリクスも生成**します（Spring Boot が Observation を両方のハンドラに渡すため）。つまりレイテンシは、追加実装なしで `claude.message` 由来のメトリクス（Prometheus では `claude_message_milliseconds` 系）として記録されます。

## 手順5：トレースとメトリクスを見る

ローカルに可観測性バックエンドを `docker compose` で立てます。OTel Collector が OTLP を受け、トレースは Jaeger へ、メトリクスは Prometheus 形式で公開して Grafana で見ます。

```
docker compose up -d                      # Collector / Jaeger / Prometheus / Grafana
cp .env.example .env                       # .env に実 ANTHROPIC_API_KEY（コミットしない）
./gradlew bootRun
curl "http://localhost:8080/ask?prompt=Spring%20Boot%20を一言で"  # 1回だけ実呼び出し
```

Jaeger を開くと、受信リクエストの span の下に `claude.message` が子 span として連なり、その属性に入出力トークンと停止理由が乗っているのを確認できます。Prometheus 側では命名規則により、ドットが `_` へ置き換わり、Counter には `_total` が付きます。たとえば `gen_ai.client.token.usage` は `gen_ai_client_token_usage_total` として見えます。

![Jaeger のトレース画面](https://static.zenn.studio/user-upload/deployed-images/8abf4fddb7f169cf171a1669.png?sha=280cfa37469280fead99d76608275bdcdce59d2a)

*Jaeger：`GET /ask` の配下に `claude.message` が子 span として連なる。`gen_ai.*` 属性（モデル・停止理由など）で1呼び出しの内訳を追える。*

![Grafana のダッシュボード](https://static.zenn.studio/user-upload/deployed-images/af7621079a9afda7edb77b8b.png?sha=0767ef5b6cbc0e9488ffe7954e3be66a6299ec58)

*Grafana：`gen_ai_client_token_usage_total` と推定コストの推移を可視化したダッシュボード。*

## つまずきポイントと解決

計装そのものより、可観測性バックエンドとのつなぎ込みや設計判断でつまずきがちです。代表的な4点と対処を挙げます。

* **SDK の HTTP 呼び出しがトレースに出てこない**：anthropic-java は内部で独自の OkHttp クライアントを使うため、Spring の自動計装（`RestClient` 等）の対象外です。本記事のように**呼び出しを `Observation` で包む**のが確実です。
* **メトリクスのタグが増えすぎる（一度やりました）**：トークン数やプロンプト文字列を**メトリクスのタグ**にすると、値の種類だけ時系列が生成されて破綻します。高基数の値は `highCardinalityKeyValue`（span 属性のみ）に。タグにするのはモデル名・停止理由など**種類が限られるもの**だけにします。
* **Collector を立てる前にアプリだけ起動したときの警告**：送信先が無いと OTLP エクスポータは接続エラーを出します。動作自体は止まりませんが、先に `docker compose up -d` してから `bootRun` すると警告が出ません。テスト時は送信を無効化しておけば、Collector 不在でもテストが通ります。
* **全トレースを送るとコストがかさむ**：`management.tracing.sampling.probability` は検証用として `1.0` にしています。本番では落とすか、テールサンプリング（Collector 側）を検討します。

## まとめ

ここまでの要点を、Claude 呼び出しを可観測にする最小構成として4点に整理します。

* Spring Boot 3 の **Observation を `micrometer-tracing-bridge-otel` で OpenTelemetry 化**し、OTLP で送るのが最小の型
* Claude 呼び出しは**自動計装されない**ので、`Observation.observe(...)` で 1 本の span に包む。モデル名・トークン・停止理由を属性に乗せ、失敗も自動で span に残す
* 「合計・推移」はメトリクス（Counter）に。**トークンは高基数 → span 属性、低基数 → タグ**の使い分けが要
* 送信先は自由。ローカルなら **Collector → Jaeger・Prometheus・Grafana** で完結する

計装を入れて Jaeger でトレースが流れた瞬間、Claude 呼び出しが「ブラックボックス」から「ただの、計測できる処理」に変わります。コスト・レイテンシ・失敗を、勘ではなく数字で語れます。LLM をプロダクトへ載せるなら、最初に通しておきたい土台だと考えています。

> **次回**：本記事は属性名を GenAI 規約に「寄せた」最小形でした。続編では、属性とメトリクスを規約へ**厳密に**沿わせ（`gen_ai.provider.name`・`finish_reasons` 配列・トークンの Histogram 化など）、ベンダーをまたいで通用する計装に仕上げます。

ここでは「Claude 呼び出しを可観測にする」最小形に絞りましたが、**仕様定義から実装・テスト・デプロイまで**を Claude Code と一気通貫で進める流れは、拙著にまとめています。Spring Security / JPA / Flyway や本番デプロイ（Railway）まで、AI と対話しながら1つのWebアプリを完成させる構成です。

📘 『**Claude Codeと生み出す Spring Boot実践開発 ～AI日記アプリを仕様定義からデプロイまで～**』

※ Amazon のリンクはアフィリエイトリンクを含みます。
