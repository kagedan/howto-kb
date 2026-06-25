---
id: "2026-06-24-spring-bootから公式java-sdkでclaude-apiを呼ぶ最小実装-01"
title: "Spring Bootから公式Java SDKでClaude APIを呼ぶ最小実装"
url: "https://zenn.dev/propagandist/articles/0001-spring-boot-claude-api-java-sdk"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "zenn"]
date_published: "2026-06-24"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

## この記事について

* **対象読者**：Spring Boot / Java の基礎があり、アプリにAI（Claude）を組み込んでみたい人
* **得られること**：Anthropic 公式 Java SDK を使い、Spring Boot から Claude API を呼ぶ最小構成（依存・設定・サービス）が作れる
* **前提・環境**：Java 21 / Spring Boot 3.5 / `com.anthropic:anthropic-java` 2.34.0 / Lombok / Anthropic の API キー

> サンプルは「プロンプトを渡すとテキストが得られる」最小の形に絞っています。チャットや要約など、用途に合わせて広げてください。

> バージョン（SDK・Spring Boot）とモデル名は\*\*執筆時点（2026年6月）\*\*のものです。対応モデルやSDKは更新されるため、最新は公式情報で確認してください。

## 結論（先に全体像）

公式 Java SDK を1つ足し、`AnthropicClient` を Bean として登録すれば、あとは `client.messages().create(...)` を呼ぶだけです。

```
var params = MessageCreateParams.builder()
        .model("claude-opus-4-8")
        .maxTokens(1024)
        .system("あなたは簡潔に答えるアシスタントです。")
        .addUserMessage("Spring Bootとは何ですか？1文で。")
        .build();

var response = client.messages().create(params);
```

ここから、設定の外出し・キーの扱い・レスポンスの取り出しまでを順に作っていきます。

## 手順1：依存を追加する

プロジェクトに依存を加えます。公式 Java SDK 本体に加えて、設定値の検証用に `spring-boot-starter-validation` を入れます。さらにボイラープレート削減用として Lombok（`@RequiredArgsConstructor` / `@Slf4j`）も使います。

build.gradle.kts

```
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("com.anthropic:anthropic-java:2.34.0")

    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")
}
```

Maven の場合：

pom.xml

```
<dependencies>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
  </dependency>
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
  </dependency>
  <dependency>
    <groupId>com.anthropic</groupId>
    <artifactId>anthropic-java</artifactId>
    <version>2.34.0</version>
  </dependency>
  <dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <optional>true</optional>
  </dependency>
</dependencies>
```

## 手順2：APIキーの扱いとクライアントのBean化

SDK には `AnthropicOkHttpClient.fromEnv()` という便利メソッドがあります。ただしこれは **`System.getenv()` を直接読む**ため、Spring の `Environment` を参照しません。`spring.config.import` で読み込んだ `.env` も対象外です。

そこで、`@Value` で Spring 経由にキーを解決すると、**本番の OS 環境変数**と**開発時の `.env`** の両方から同じコードで読めます。

```
@Configuration
public class AnthropicClientConfig {

    @Bean
    public AnthropicClient anthropicClient(@Value("${ANTHROPIC_API_KEY}") String apiKey) {
        return AnthropicOkHttpClient.builder()
                .apiKey(apiKey)
                .build();
    }
}
```

開発時に `.env` から読むなら、`application.yaml` にこう書いておきます（本番では OS 環境変数が直接使われるので `optional`）。

application.yaml

```
spring:
  config:
    import: optional:file:.env[.properties]
```

> `.env` や API キーは**コミットしない**こと。`.gitignore` に `.env` を入れておきます。

## 手順3：モデルとmax\_tokensを設定に外出しする

モデル名や `max_tokens` はコードに直書きせず、設定に逃がしておくと切り替えが楽です。`record` + `@ConfigurationProperties` が簡潔です。

```
@ConfigurationProperties(prefix = "anthropic")
@Validated
public record AnthropicProperties(
        @NotBlank String model,
        @Min(1) int maxTokens) {}
```

この record を Bean にするには登録が必要です。手順2の `AnthropicClientConfig` に `@EnableConfigurationProperties` を足して有効化します。起動クラスに `@ConfigurationPropertiesScan` を付ける方法でも構いません。

```
@Configuration
@EnableConfigurationProperties(AnthropicProperties.class)  // ← この1行を追加
public class AnthropicClientConfig {
    // 手順2の anthropicClient(...) はそのまま
}
```

application.yaml

```
anthropic:
  model: claude-opus-4-8
  max-tokens: 1024
```

> `max-tokens`（ケバブケース）が `maxTokens` に対応します（Spring のリラックスバインディング）。用途に応じてモデルは差し替え可能で、高頻度・低レイテンシ重視なら `claude-haiku-4-5` のような軽量モデルが向きます。

## 手順4：呼び出して、レスポンスからテキストを取り出す

レスポンスの `content()` は複数ブロックの配列です。テキストブロックだけを取り出して連結します。

```
@Service
@RequiredArgsConstructor
@Slf4j
public class AiAssistant {

    private final AnthropicClient client;
    private final AnthropicProperties properties;

    public String ask(String prompt) {
        var params = MessageCreateParams.builder()
                .model(properties.model())
                .maxTokens(properties.maxTokens())
                .system("あなたは簡潔に答えるアシスタントです。")
                .addUserMessage(prompt)
                .build();
        try {
            var response = client.messages().create(params);

            var body = response.content().stream()
                    .flatMap(block -> block.text().stream())
                    .map(text -> text.text())
                    .collect(Collectors.joining());

            if (body.isBlank()) {
                throw new IllegalStateException("Claude returned an empty body");
            }
            return body;
        } catch (AnthropicException e) {
            log.error("claude api call failed", e);
            throw new IllegalStateException("Failed to call Claude", e);
        }
    }
}
```

`response.usage()`（入出力トークン数）や `response.stopReason()` も取れるので、ログに残しておくと運用時に役立ちます。

## つまずきポイントと解決

実装で詰まりやすいのは、APIキーの解決と、レスポンスの取り出しまわりです。代表的な3点と回避策を挙げます。

* **`fromEnv()` でキーが読めない**：`fromEnv()` は `System.getenv()` を直接読みます。`.env` を `spring.config.import` で読み込んでも認識しません。`@Value("${ANTHROPIC_API_KEY}")` で Spring 経由にすれば解決できます（手順2）。
* **空のレスポンスが返される**：`content()` にテキストブロックが無い、`stopReason` が想定外、というケースがあります。空チェックを入れ、`stopReason` をログに出して原因を切り分けます。
* **例外の型**：API 呼び出しの失敗は `com.anthropic.errors.AnthropicException` で受けられます。アプリ側の例外に包んで扱うとレイヤーが整理できます。

## まとめ

* 公式 Java SDK（`com.anthropic:anthropic-java`）を足して `AnthropicClient` を Bean 化すれば、Spring Boot から Claude API を呼べる
* キーは `@Value` で Spring 経由に解決すると、本番の OS 環境変数と開発時の `.env` の両方で動く
* モデル・`max_tokens` は設定に外出し、レスポンスはテキストブロックを連結して取り出す

ここでは「呼ぶ」最小形に絞りましたが、**仕様定義から実装・テスト・デプロイまで**を Claude Code と一気通貫でやる流れは、拙著にまとめています。Spring Security / JPA / Flyway や本番デプロイ（Railway）まで、AI と対話しながら1つのWebアプリを完成させる構成です。

📘 『**Claude Codeと生み出す Spring Boot実践開発 ～AI日記アプリを仕様定義からデプロイまで～**』
