---
id: "2026-07-18-spring-boot-で-claude-api-のエラーレート制限に強くする-01"
title: "Spring Boot で Claude API のエラー・レート制限に強くする"
url: "https://zenn.dev/propagandist/articles/0019-spring-boot-claude-error-handling"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "zenn"]
date_published: "2026-07-18"
date_collected: "2026-07-19"
summary_by: "auto-rss"
query: ""
---

## この記事について

* **対象読者**：[1本目](https://zenn.dev/propagandist/articles/0001-spring-boot-claude-api-java-sdk)で Claude を呼べるようになり、実運用に向けて**失敗時の挙動**を整えたい人
* **得られること**：レート制限（429）・サーバエラー（5xx）・ネットワーク断を**指数バックオフで再試行**し、それ以外は即失敗させる最小実装
* **前提・環境**：Java 21 / Spring Boot 3.5 / `com.anthropic:anthropic-java` 2.34.0

> この記事は「[Spring Boot から公式 Java SDK で Claude API を呼ぶ最小実装](https://zenn.dev/propagandist/articles/0001-spring-boot-claude-api-java-sdk)」の続編です。クライアントの Bean 化・設定の外出し（`AnthropicClientConfig` / `AnthropicProperties`）は前回までを引き継ぎます。

> バージョン（SDK・Spring Boot）とモデル名は\*\*執筆時点（2026年6月）\*\*のものです。最新は公式情報で確認してください。

## 結論（先に全体像）

エラーは「再試行で直るもの」と「直らないもの」に分けて扱います。

* **再試行する**：429（レート制限）・5xx（500・529 overloaded など）・ネットワーク断
* **即失敗**：400・401・404 など（再試行しても直らない）

判定ロジックを SDK や HTTP に依存しない**純粋関数**として切り出すと、そのままテストできます。

```
public static boolean isRetryable(int statusCode) {
    return statusCode == 429 || statusCode >= 500;
}
```

> 公式 SDK も執筆時点では既定で数回リトライしますが、「業務に合わせて回数やバックオフを制御したい」「ログを残したい」場合は、自前で実装すると挙動が読めます。

## 手順1：再試行可否とバックオフを純粋関数にする

再試行の「判断」と「待ち時間」を独立させます。HTTP やネットワークに触れないので、ユニットテストが書きやすくなります。

```
public final class RetryPolicy {

    private RetryPolicy() {}

    // 429 と 5xx は一時的なので再試行。4xx は直らないので false。
    public static boolean isRetryable(int statusCode) {
        return statusCode == 429 || statusCode >= 500;
    }

    // 指数バックオフ：1回目=base、2回目=base*2、3回目=base*4 ...
    public static long backoffMillis(int attempt, long baseMillis) {
        if (attempt < 1) {
            throw new IllegalArgumentException("attempt は1以上で指定してください");
        }
        return baseMillis * (1L << (attempt - 1));
    }
}
```

```
class RetryPolicyTest {
    @Test
    void retriesOnRateLimitAndServerErrors() {
        assertTrue(RetryPolicy.isRetryable(429));
        assertTrue(RetryPolicy.isRetryable(529));
    }
    @Test
    void doesNotRetryOnClientErrors() {
        assertFalse(RetryPolicy.isRetryable(400));
    }
    @Test
    void backoffGrowsExponentially() {
        assertEquals(500L, RetryPolicy.backoffMillis(1, 500L));
        assertEquals(2000L, RetryPolicy.backoffMillis(3, 500L));
    }
}
```

## 手順2：例外を型で受けて、ステータスで判断する

公式 SDK の例外は型で分かれています。HTTP 応答のあるエラーは `AnthropicServiceException`（`statusCode()` を持つ）、ネットワーク断は `AnthropicIoException` です（いずれも `com.anthropic.errors`）。ステータスを `RetryPolicy` に渡して、再試行するか決めます。

```
@Service
@RequiredArgsConstructor
@Slf4j
public class ResilientAiAssistant {

    private static final int MAX_ATTEMPTS = 3;
    private static final long BASE_BACKOFF_MILLIS = 500L;

    private final AnthropicClient client;
    private final AnthropicProperties properties;

    public String ask(String prompt) {
        var params = MessageCreateParams.builder()
                .model(properties.model())
                .maxTokens(properties.maxTokens())
                .system("あなたは簡潔に答えるアシスタントです。")
                .addUserMessage(prompt)
                .build();

        for (int attempt = 1; ; attempt++) {
            try {
                var response = client.messages().create(params);
                return response.content().stream()
                        .flatMap(block -> block.text().stream())
                        .map(text -> text.text())
                        .collect(Collectors.joining());
            } catch (AnthropicServiceException e) {
                // HTTP ステータス（429 / 5xx など）で再試行可否を判断
                if (RetryPolicy.isRetryable(e.statusCode()) && attempt < MAX_ATTEMPTS) {
                    backoff(attempt, e);
                    continue;
                }
                throw new IllegalStateException("Claude call failed (status=" + e.statusCode() + ")", e);
            } catch (AnthropicIoException e) {
                // ネットワーク断なども一時的なので再試行
                if (attempt < MAX_ATTEMPTS) {
                    backoff(attempt, e);
                    continue;
                }
                throw new IllegalStateException("Claude call failed (I/O)", e);
            }
        }
    }

    private void backoff(int attempt, Exception cause) {
        long millis = RetryPolicy.backoffMillis(attempt, BASE_BACKOFF_MILLIS);
        log.warn("retry attempt {} after {}ms due to: {}", attempt, millis, cause.toString());
        try {
            Thread.sleep(millis);
        } catch (InterruptedException ie) {
            Thread.currentThread().interrupt(); // 割り込みフラグを復元
            throw new IllegalStateException("interrupted during backoff", ie);
        }
    }
}
```

`MAX_ATTEMPTS` で試行上限を切り、無限ループを防ぎます。429 の場合は本来 `retry-after` ヘッダに従うのが望ましいですが、まずは指数バックオフから始めれば十分でしょう。

## つまずきポイントと解決

再試行を自前で実装するとき、つまずきやすいのは次の4点です。

* **何でも再試行してしまう**：400・401 を再試行しても直りません。`isRetryable` で 429・5xx に限定します。
* **無限ループ**：上限（`MAX_ATTEMPTS`）を必ず設けます。超えたら包んで投げます。
* **`InterruptedException` を握りつぶす**：`Thread.sleep` の割り込みは `Thread.currentThread().interrupt()` でフラグを復元してから例外にします。
* **判定ロジックがテストしづらい**：再試行の判断を `RetryPolicy`（純粋関数）に切り出すと、ネットワークなしで実値検証できます。

## まとめ

* エラーは「再試行で直る（429・5xx・I/O）」と「直らない（4xx）」に分ける
* 判断は `AnthropicServiceException.statusCode()` を `RetryPolicy` に渡して決める
* 上限と指数バックオフで安全に制御する。判定ロジックは純粋関数にしてテストで固める

ここでは「失敗に強くする」最小形に絞りましたが、**仕様定義から実装・テスト・デプロイまで**を Claude Code と一気通貫で進める流れは、拙著にまとめています。Spring Security / JPA / Flyway や本番デプロイ（Railway）まで、AI と対話しながら 1つの Web アプリを完成させる構成です。

📘 『**Claude Codeと生み出す Spring Boot実践開発 ～AI日記アプリを仕様定義からデプロイまで～**』

※ Amazon のリンクはアフィリエイトリンクを含みます。
