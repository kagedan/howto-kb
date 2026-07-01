---
id: "2026-07-01-ストリーミング応答を-opentelemetry-で計測するttft-と中断を可視化する-01"
title: "ストリーミング応答を OpenTelemetry で計測する：TTFT と中断を可視化する"
url: "https://zenn.dev/propagandist/articles/0008-spring-boot-otel-streaming-ttft"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "LLM", "zenn"]
date_published: "2026-07-01"
date_collected: "2026-07-02"
summary_by: "auto-rss"
query: ""
---

## この記事について

* **対象読者**：Claude のストリーミング応答をブラウザへ流していて、その**体感速度（最初の1文字までの速さ）や、途中で切られた割合**を数字で見たい人
* **得られること**：ストリーミング呼び出しを 1 本の span で計測し、**TTFT（Time To First Token＝最初のトークンまでの時間）**・出力スループット・チャンク数・\*\*中断（クライアント切断）\*\*を、属性とメトリクスに残す方法
* **前提・環境**：Java 21 / Spring Boot 3.5 / `com.anthropic:anthropic-java` 2.34.0 / Micrometer Observation

> この記事は、[Claude のストリーミング応答を SSE でブラウザへ流す記事](https://zenn.dev/propagandist/articles/0002-spring-boot-claude-streaming)と、[Claude 呼び出しを OpenTelemetry で計測する記事](https://zenn.dev/propagandist/articles/0004-spring-boot-otel-claude-observability)の交差点です。ストリーミングの実装と、可観測性の土台は、それぞれを引き継ぎます。

> SDK・モデル名・属性規約は\*\*執筆時点（2026年6月）\*\*のものです。最新は公式情報で確認してください。

## なぜストリーミングは「別の計測」が要るのか

同期呼び出しなら、計測したいのは基本ひとつ——**全体のレイテンシ**です。ところがストリーミングでは、ユーザーの体感は「最後まで返ってくる時間」では決まりません。**最初の1文字が出るまで**に、待たされ感のほとんどが決まります。

つまりストリーミングでは、見るべき数字が変わります。

* **TTFT（最初のトークンまでの時間）**：体感速度そのもの。これが長いと「固まった」と感じられる
* **出力スループット**：1秒あたり何トークン出たか。途中の詰まりを表す
* **中断**：ユーザーがタブを閉じるなどで、**最後まで届く前に切れた**割合。LLM では中断＝途中までの課金でもある

同期版の span をそのまま流用しても、これらは出てきません。ストリーミングには、**ストリーミング用の計装**が要ります。

> **用語**：**TTFT（Time To First Token）** は、リクエストを送ってから最初のトークン（差分）が届くまでの時間。OpenTelemetry の GenAI 規約にも、生成サーバ側の指標として `gen_ai.server.time_to_first_token` が定義されています。本記事はそれを**クライアント側で**測ります。

## 結論（先に全体像）

ストリーミングの計装は、**差分を受け取るループに、3つの「印」を打つ**だけです。

1. **開始時刻を記録**し、ストリーム全体を 1 本の span（`Observation`）で包む
2. **最初の差分が来た瞬間**に TTFT を確定し、span にイベントを残す
3. **最後の `message_delta`** から出力トークン・停止理由を取り、span 属性とメトリクスに記録する

中断は特別扱いしません。クライアント切断は例外として伝わるので、**そのまま span のエラー**になり、「最後まで届かなかった呼び出し」として残ります。

## 手順1：ストリーム全体を span で包み、開始時刻を持つ

[ストリーミングの記事](https://zenn.dev/propagandist/articles/0002-spring-boot-claude-streaming)で作った `askStream` を計装版にします。まず、呼び出し全体を `Observation` で包み、`System.nanoTime()` で開始時刻を控えます。span 名とメトリクス名の分け方は[規約に沿った計装の記事](https://zenn.dev/propagandist/articles/0001-spring-boot-claude-api-java-sdk)と同じです。

```
public String askObservedStream(String prompt, Consumer<String> onDelta) {
    var params = MessageCreateParams.builder()
            .model(properties.model())
            .maxTokens(properties.maxTokens())
            .system("あなたは簡潔に答えるアシスタントです。")
            .addUserMessage(prompt)
            .build();

    Observation observation = Observation.createNotStarted(
                    "gen_ai.client.operation.duration", observationRegistry) // timer メトリクス名
            .contextualName("chat " + properties.model())                    // span 名
            .lowCardinalityKeyValue("gen_ai.operation.name", "chat")
            .lowCardinalityKeyValue("gen_ai.provider.name", "anthropic")
            .lowCardinalityKeyValue("gen_ai.request.model", properties.model());

    return observation.observe(() -> consumeStream(params, onDelta, observation));
}
```

`observe(...)` が span の開始・終了・例外をまとめて扱うのは、同期版と同じです。中身（`consumeStream`）が、ストリーミング固有の計測になります。

## 手順2：最初の差分で TTFT を確定する

差分を受け取るループの中で、**最初の1回だけ** TTFT を記録します。あわせてチャンク数を数え、最後の `message_delta` から出力トークンと停止理由を取り出します。

```
private String consumeStream(MessageCreateParams params, Consumer<String> onDelta, Observation observation) {
    long startNanos = System.nanoTime();
    var firstTokenNanos = new AtomicLong(0);   // 0 = まだ最初の差分が来ていない
    var chunkCount = new AtomicInteger(0);
    var outputTokens = new AtomicLong(0);
    var finishReason = new AtomicReference<>("end_turn");
    var body = new StringBuilder();

    try (StreamResponse<RawMessageStreamEvent> stream = client.messages().createStreaming(params)) {
        stream.stream().forEach(event -> {
            // 最後の message_delta：出力トークンと停止理由が乗る
            event.messageDelta().ifPresent(md -> {
                outputTokens.set(md.usage().outputTokens());
                md.delta().stopReason().ifPresent(r -> finishReason.set(r.toString()));
            });
            // 本文の差分（text_delta）だけを拾う
            event.contentBlockDelta()
                    .flatMap(delta -> delta.delta().text())
                    .map(TextDelta::text)
                    .ifPresent(chunk -> {
                        if (firstTokenNanos.compareAndSet(0, System.nanoTime())) {
                            // 最初の差分が来た瞬間。span にイベントを残す
                            observation.event(Observation.Event.of("gen_ai.first_token"));
                        }
                        chunkCount.incrementAndGet();
                        body.append(chunk);
                        onDelta.accept(chunk); // ブラウザへ流す（SSE は前回の記事）
                    });
        });
    } catch (AnthropicException e) {
        log.error("claude streaming call failed", e);
        throw new IllegalStateException("Failed to stream from Claude", e);
    }

    recordStreamingMetrics(startNanos, firstTokenNanos.get(), outputTokens.get(),
            chunkCount.get(), finishReason.get(), observation);
    return body.toString();
}
```

`compareAndSet(0, ...)` は「まだ記録していなければ、今の時刻を入れる」を1回で済ませる書き方です。最初の差分だけが TTFT を確定し、2回目以降は素通りします。`gen_ai.first_token` のイベントを span に打っておくと、**Jaeger のタイムライン上で「いつ最初の1文字が出たか」が点として見えます**。

![Jaeger：chat span のタイムラインに gen_ai.first_token イベントが点として乗り、TTFT 属性が記録される](https://static.zenn.studio/user-upload/deployed-images/82453096aadab9d4903b209f.png?sha=badd808c5b81b17b626632ff74a3fca315953879)

実際に Jaeger で `chat claude-opus-4-8` span を開くと、TTFT・出力トークン・チャンク数が属性として並びます。このトレースでは `gen_ai.client.time_to_first_token_ms` が 1098 でした。Logs には `gen_ai.first_token` の点が残ります。

## 手順3：TTFT・トークン・スループットを残す

計測した値を、span 属性とメトリクスに記録します。TTFT は体感の指標なので、\*\*分布（Histogram）\*\*で持つのが要点です。平均だけ見ると、一部の「待たされた」リクエストが平らされてしまいます。

```
private void recordStreamingMetrics(long startNanos, long firstTokenNanos, long outputTokens,
                                    int chunkCount, String finishReason, Observation observation) {
    long ttftMs = (firstTokenNanos - startNanos) / 1_000_000;

    // span 属性：1リクエストの内訳（高基数はここだけに）
    observation.highCardinalityKeyValue("gen_ai.client.time_to_first_token_ms", String.valueOf(ttftMs));
    observation.highCardinalityKeyValue("gen_ai.usage.output_tokens", String.valueOf(outputTokens));
    observation.highCardinalityKeyValue("gen_ai.client.stream.chunk_count", String.valueOf(chunkCount));
    observation.lowCardinalityKeyValue("gen_ai.response.finish_reasons", finishReason);

    // メトリクス：TTFT は分布で持つ（p95 が体感の指標）。
    // publishPercentileHistogram() を付けるのが要点。これが無いと Micrometer は
    // 合計・件数と +Inf バケットしか出さず、Prometheus の histogram_quantile で p95 を計算できない。
    // 期待レンジを TTFT の現実値（50ms〜15s）に絞ると、バケットがそこに集まり p95 が意味のある値になる。
    Timer.builder("gen_ai.client.time_to_first_token")
            .tag("gen_ai.request.model", properties.model())
            .publishPercentileHistogram()
            .minimumExpectedValue(Duration.ofMillis(50))
            .maximumExpectedValue(Duration.ofSeconds(15))
            .register(meterRegistry)
            .record(Duration.ofMillis(ttftMs));

    // 出力トークンも分布で（前回の規約準拠の記事と同じ Histogram）
    DistributionSummary.builder("gen_ai.client.token.usage")
            .tag("gen_ai.token.type", "output")
            .tag("gen_ai.request.model", properties.model())
            .publishPercentileHistogram()
            .register(meterRegistry)
            .record(outputTokens);
}
```

> **p95 を出すには `publishPercentileHistogram()` が要る**：これを付け忘れると、メトリクスは合計・件数（と `+Inf` バケット）だけになり、Grafana で `histogram_quantile(0.95, ...)` を計算しても `NaN` になります。「TTFT は分布で」と言いながら p95 が出ない、という取りこぼしが起きやすいところです。

ヒストグラムさえ出ていれば、Grafana 側は次の PromQL で p95 を引けます。

```
histogram_quantile(0.95, sum by (le) (rate(gen_ai_client_time_to_first_token_milliseconds_bucket[$__rate_interval])))
```

![Grafana：TTFT の p95 / p50 を分布から算出したパネル](https://static.zenn.studio/user-upload/deployed-images/240d5acb6cfb6c5ce223ddb8.png?sha=db0c05263c2cdc3f2efbbd99809106df03a5a3e9)

p50 と p95 を並べると、「ふだんの体感」と「遅かったときの体感」の差が見えます。平均 1 本では、この差が消えてしまいます。

全体のレイテンシは、手順1の `Observation`（`gen_ai.client.operation.duration`）が timer として自動で出します。TTFT を引けば「最初の1文字から生成しきるまでの時間」も分かります。スループット（トークン/秒）は、出力トークンと全体時間から後段（Grafana）で割り算しても、ここで計算して属性に足してもよいです。

## 手順4：中断（クライアント切断）を見えるようにする

ストリーミングならではの状態が **中断** です。[前回の SSE 実装](https://zenn.dev/propagandist/articles/0002-spring-boot-claude-streaming)では、ブラウザが切断すると `emitter.send(...)` が `IOException` を投げ、それを例外として送り返してストリームを打ち切りました。

この例外は `AnthropicException` でなく、`consumeStream` の `catch` を素通りし、`observe(...)` の外まで伝わります。結果として——**特別なコードを足さなくても、中断は span のエラーとして記録されます**。

つまり、Jaeger では「正常に最後まで返した span」と「途中で切れた span」が、**成否で区別**できます。中断の割合が知りたいときは、`gen_ai.client.operation.duration` メトリクスの `error.type` タグ（Micrometer が失敗時に付与）で絞り込めます。

![Jaeger：途中で切断された span が error=true・status ERROR で残り、client disconnected の例外が記録される](https://static.zenn.studio/user-upload/deployed-images/5afea15cbb01add0490927be.png?sha=c45526d7cd09d65ef88a39f471db9402c981a56c)

切断したトレースを開くと、span は `otel.status_code=ERROR`（`client disconnected`）で閉じます。Logs には `gen_ai.first_token` と `exception` の両方が残ります。最初の1文字は届いたのに最後まで届かなかった、という途中経過がそのまま読めます。

> 中断は「ユーザーがもう要らないと判断した」サインでもあり、「**そこまでのトークンは課金された**」事実でもあります。中断率が高い画面は、TTFT が遅すぎないか・出力が長すぎないかを見直す手がかりになります。

## つまずきポイントと解決

ストリーミング計測は、非同期と「最後のイベント」まわりでつまずきます。

* **TTFT が全体レイテンシと同じ値になる**：最初の差分ではなく、ストリーム終了時に測ってしまうケースです。**最初の `text_delta` が来た瞬間**に1回だけ記録します（`compareAndSet(0, ...)`）。
* **出力トークンが 0 のまま**：トークンと停止理由は**最後の `message_delta`** に乗ります。`content_block_delta` だけを見ていると取りこぼします。`event.messageDelta()` も拾います。
* **中断が「成功」に見える**：切断時の例外を握りつぶすと、span は成功で閉じます。`emitter.send` の `IOException` を**例外として伝える**ことで、span がエラーになり、中断として残ります。
* **TTFT を平均で見てしまう**：体感は外れ値で決まります。\*\*Histogram（p95）\*\*で持ち、「遅かった上位5%」を見ます。
* **p95 が `NaN`**：`Timer` や `DistributionSummary` で **`publishPercentileHistogram()`** を付け忘れた状態です。出るのは合計・件数と `+Inf` バケットだけで、Grafana の `histogram_quantile` が計算できません。分布を見るなら、計装側でヒストグラムを有効にします。
* **別スレッドで span の文脈が切れる**：SSE 送信を別スレッドへ渡す構成では、`Observation` の文脈がスレッドをまたぎます。計測は**ストリームを消費するスレッドの中**（`consumeStream`）で完結させ、span をまたいで持ち回らない形にすると単純です。

## まとめ

ストリーミングは、同期呼び出しとは見るべき数字が違います。それを span とメトリクスに落とすのが要点です。

* ストリーム全体を 1 本の span（`Observation`）で包み、**開始時刻**を控える
* **最初の差分**で TTFT を確定し、`gen_ai.first_token` イベントを span に打つ。TTFT は **Histogram（p95）** で持つ
* 出力トークン・停止理由は**最後の `message_delta`** から取る。チャンク数も残す
* **中断は例外のまま** span のエラーになる。`error.type` で中断率を絞り込める

TTFT が数字で見えると、「速くなった/遅くなった」を体感ではなく計測で語れます。ストリーミングを売りにする画面ほど、最初に通しておきたい指標です。

ここでは「ストリーミングを可観測にする」ことに絞りましたが、**仕様定義から実装・テスト・デプロイまで**を Claude Code と一気通貫で進める流れは、拙著にまとめています。Spring Security / JPA / Flyway や本番デプロイ（Railway）まで、AI と対話しながら1つのWebアプリを完成させる構成です。

📘 『**Claude Codeと生み出す Spring Boot実践開発 ～AI日記アプリを仕様定義からデプロイまで～**』

※ Amazon のリンクはアフィリエイトリンクを含みます。
