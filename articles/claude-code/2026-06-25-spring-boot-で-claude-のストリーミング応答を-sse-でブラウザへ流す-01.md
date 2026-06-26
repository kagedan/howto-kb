---
id: "2026-06-25-spring-boot-で-claude-のストリーミング応答を-sse-でブラウザへ流す-01"
title: "Spring Boot で Claude のストリーミング応答を SSE でブラウザへ流す"
url: "https://zenn.dev/propagandist/articles/0002-spring-boot-claude-streaming"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "zenn"]
date_published: "2026-06-25"
date_collected: "2026-06-26"
summary_by: "auto-rss"
query: ""
---

## この記事について

* **対象読者**：[前回](https://zenn.dev/propagandist/articles/0001-spring-boot-claude-api-java-sdk)で Claude API の同期呼び出しまで作った人／応答を**ブラウザに逐次表示**したい人
* **得られること**：公式 Java SDK の `createStreaming` で差分を受け取り、それを **SSE（Server-Sent Events）でブラウザまで流す**最小実装。非同期・完了・エラー・クライアント切断の扱いまで
* **前提・環境**：Java 21 / Spring Boot 3.5 / `com.anthropic:anthropic-java` 2.34.0。前回作った `AnthropicClient` と `AnthropicProperties`、Spring MVC（`spring-boot-starter-web`）を使います

> この記事は「[Spring Bootから公式Java SDKでClaude APIを呼ぶ最小実装](https://zenn.dev/propagandist/articles/0001-spring-boot-claude-api-java-sdk)」の続編です。依存・設定・Bean 化は前回を参照してください。

> バージョン（SDK・Spring Boot）とモデル名は\*\*執筆時点（2026年6月）\*\*のものです。最新は公式情報で確認してください。

## 結論（先に全体像）

SDK でストリーミングに切り替えるための変更は、ほぼ**1か所だけ**です。

* `client.messages().create(...)` → `client.messages().createStreaming(...)`
* 得られる**イベント列**から、テキストの差分（`text_delta`）だけを取り出す

本題はその先の、**「差分をブラウザまでどう届けるか」**です。ここでは SSE（`SseEmitter`）へ橋渡しします。ただし、SDK のストリーム消費は**ブロッキング**です。リクエストスレッドでそのまま実行すると、応答が終わるまでスレッドを占有してしまいます。そこで別スレッドで送信し、最後は必ず `complete()` を呼んで閉じます。この点が本記事の中心です。

```
[Claude API] --(差分)--> StreamingAiAssistant.askStream(onDelta)
                                   │ onDelta（別スレッドで実行）
                                   ▼
                          SseEmitter.send(差分)  --(SSE)-->  ブラウザの EventSource
```

ストリーミングと SSE は、どちらも追加の依存なしで利用できます（SDK と Spring MVC に含まれています）。

## 手順1：差分を渡せる `askStream` を用意する

まずは SDK 側の実装です。`createStreaming` は `StreamResponse<RawMessageStreamEvent>` を返します。これは `AutoCloseable` なので、**必ず try-with-resources で閉じます**（接続を開いたままにしないため）。

ストリームには `message_start` や `content_block_start`、最後の `message_delta`（usage を含む）など複数種類のイベントが流れます。必要なのは本文の差分だけなので、`content_block_delta` のうち `text_delta` を二段の `flatMap` で絞り込みます。受け取った差分はその都度呼び出し側へ渡しつつ、全文も組み立てて返しておくと、さまざまな場面で再利用できます。

```
@Service
@RequiredArgsConstructor
@Slf4j
public class StreamingAiAssistant {

    private final AnthropicClient client;
    private final AnthropicProperties properties;

    public String askStream(String prompt, Consumer<String> onDelta) {
        var params = MessageCreateParams.builder()
                .model(properties.model())
                .maxTokens(properties.maxTokens())
                .system("あなたは簡潔に答えるアシスタントです。")
                .addUserMessage(prompt)
                .build();

        var body = new StringBuilder();
        try (StreamResponse<RawMessageStreamEvent> stream = client.messages().createStreaming(params)) {
            stream.stream()
                    .flatMap(event -> event.contentBlockDelta().stream()) // content_block_delta だけ
                    .flatMap(delta -> delta.delta().text().stream())       // その中の text_delta だけ
                    .map(TextDelta::text)
                    .forEach(chunk -> {
                        body.append(chunk);
                        onDelta.accept(chunk); // 受け取った瞬間に呼び出し側へ
                    });
        } catch (AnthropicException e) {
            log.error("claude streaming call failed", e);
            throw new IllegalStateException("Failed to stream from Claude", e);
        }
        return body.toString();
    }
}
```

`onDelta` に「コンソールへ出力する処理」を渡せば、その場で逐次表示できます。次は、この `onDelta` の中身をブラウザへ流す SSE に差し替えます。全文が必要な処理（ログ・保存など）は、戻り値で受け取れます。

## 手順2：SSE エンドポイントを用意する

`SseEmitter` を返すコントローラを用意し、`onDelta` で `emitter.send(...)` を呼びます。ポイントは3つです。

```
@RestController
@RequiredArgsConstructor
@Slf4j
public class StreamingChatController {

    private final StreamingAiAssistant assistant;
    private final TaskExecutor taskExecutor; // Spring Boot 既定の applicationTaskExecutor

    @GetMapping(path = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter stream(@RequestParam String prompt) {
        var emitter = new SseEmitter(60_000L); // タイムアウト（ms）。超えると接続を閉じる

        taskExecutor.execute(() -> {            // ① リクエストスレッドを占有しない
            try {
                assistant.askStream(prompt, chunk -> send(emitter, chunk));
                emitter.complete();             // ③ 正常終了：ストリームを閉じる
            } catch (Exception e) {
                log.warn("SSE streaming aborted", e);
                emitter.completeWithError(e);   // ③ 異常終了：エラーで閉じる
            }
        });
        return emitter;
    }

    // ② 差分1つを SSE イベントとして送る。クライアント切断時は IOException。
    private void send(SseEmitter emitter, String chunk) {
        try {
            emitter.send(SseEmitter.event().data(chunk));
        } catch (IOException e) {
            // 送信に失敗した場合はクライアント切断とみなす。例外で askStream のループを止め、以降のトークン生成を打ち切る。
            throw new IllegalStateException("client disconnected", e);
        }
    }
}
```

* **① 別スレッドで送信する**：`createStreaming` の消費はブロッキングです。`@GetMapping` のメソッド内で直接実行すると、応答が完了するまでリクエストスレッドを占有し続けます。同時接続が増えると、スレッドの枯渇につながります。そこで `SseEmitter` を**即座に返し**、実際の送信は `TaskExecutor`（Spring Boot 既定の `applicationTaskExecutor`）の別スレッドへ委ねます。
* **② `send` でクライアント切断を検知する**：`emitter.send(...)` は、相手が切断していると `IOException` を投げます。これを投げ返すと `askStream` の `forEach` が中断し、try-with-resources が `StreamResponse` を閉じます。結果として**以降のトークン生成を打ち切れる**ため、無駄なコストの発生も防げます。
* **③ 必ず閉じる**：正常終了時は `complete()`、失敗時は `completeWithError(e)` を呼びます。どちらも呼ばないと、接続が開いたままになります。念のため、`new SseEmitter(60_000L)` のようにタイムアウトも設定しておきます。

## 手順3：ブラウザ側（EventSource）

フロント側は、標準の `EventSource` で受け取ります。差分が届くたびに画面へ追記します。

```
<input id="prompt" size="50" value="Spring Boot を一言で。">
<button id="send">送信</button>
<pre id="out"></pre>
<script>
  const out = document.getElementById('out');
  document.getElementById('send').onclick = () => {
    out.textContent = '';
    const prompt = document.getElementById('prompt').value;
    const es = new EventSource('/chat/stream?prompt=' + encodeURIComponent(prompt));
    es.onmessage = (e) => { out.textContent += e.data; }; // 差分が届くたびに追記
    es.onerror = () => es.close(); // 完了（complete）でも接続は閉じる→再接続させないため close
  };
</script>
```

`EventSource` は GET しか送信しないため、エンドポイントも GET にしています。なお SSE では、**サーバが `complete()` で閉じても、ブラウザ側では `onerror` が発火**します（正常な切断と異常な切断を区別できないためです）。そのままにすると自動的に再接続し、生成がもう一度実行されてしまいます。これを避けるため、`onerror` で `close()` を呼んで停止します。

## つまずきポイントと解決

実装でつまずきやすいのは、スレッドの扱いとストリームの閉じ方まわりです。代表的な5点と対処を挙げます。

* **リクエストスレッドを占有してしまう**：ブロッキングな `createStreaming` を `@GetMapping` 内で直接消費すると、応答が完了するまでスレッドを占有します。`SseEmitter` を返し、送信は別スレッド（`TaskExecutor`）で行います。
* **`emitter` を閉じ忘れて接続が残る**：`complete()` / `completeWithError()` を必ず通る形にします。`try`〜`catch` の両側で閉じ、`new SseEmitter(timeout)` でタイムアウトも設定しておきます。
* **クライアント切断に気づかない**：`emitter.send` の `IOException` が切断のサインです。例外で `askStream` を止めれば `StreamResponse` も閉じ、以降のトークン生成（＝課金）も打ち切れます。
* **エラーが早いと SSE 形式にならない**：差分を1つも送らない段階で失敗するケースです。このとき返るレスポンスは、`text/event-stream` ではなく通常の 500（JSON）になります。接続は閉じるためハングしません。フロント側は `EventSource` の `onerror` で検知します。
* **トークン数や停止理由を取得したい**：出力トークン数や停止理由は、最後の `message_delta` イベントに乗ります（`usage()` と `delta().stopReason()`）。`event.messageDelta()` から取り出して集計すると、運用ログに残せます。

## まとめ

* SDK 側は `create` を `createStreaming` に替え、イベントから `text_delta` を取り出すだけ。差分は `onDelta` で逐次処理しつつ、全文は戻り値で受け取る
* ブラウザまで流す本題は SSE。`SseEmitter` を**即座に返し**、ブロッキングな送信は**別スレッド**で行う
* 終わりは必ず `complete()` / `completeWithError()` で閉じる。`send` の `IOException` で切断を検知し、ストリームごと打ち切る

ここでは「ブラウザまで逐次表示する」最小形に絞りましたが、**仕様定義から実装・テスト・デプロイまで**を Claude Code と一気通貫で進める流れは、拙著にまとめています。Spring Security / JPA / Flyway や本番デプロイ（Railway）まで、AI と対話しながら1つのWebアプリを完成させる構成です。

📘 『**Claude Codeと生み出す Spring Boot実践開発 ～AI日記アプリを仕様定義からデプロイまで～**』
