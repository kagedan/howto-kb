---
id: "2026-05-30-spring-boot-で-claude-api-を最短ルートで動かす-anthropic-java-02"
title: "Spring Boot で Claude API を最短ルートで動かす — anthropic-java 2.35.0 実戦ガイド"
url: "https://qiita.com/ooze/items/794618c88587c93b9305"
source: "qiita"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "LLM", "OpenAI", "GPT", "Python"]
date_published: "2026-05-30"
date_collected: "2026-05-31"
summary_by: "auto-rss"
query: ""
---

# Spring Boot で Claude API を最短ルートで動かす — anthropic-java 2.35.0 実戦ガイド

## はじめに（あるいは、Java おじさんの嘆き）

世の LLM チュートリアル、なぜか 100% Python と OpenAI で書かれている。

「`pip install openai` で 3 行ですよ〜」じゃないんだよ。
こっちは月曜の朝 9 時から WebSphere の起動待ってる側の人間なんだよ。
`pom.xml` が 4000 行ある側の人間なんだよ。

そういう我々のための記事です。Spring Boot から Claude を叩きます。Python は使いません。
`requirements.txt` も書きません。代わりに `build.gradle` を 1 行書きます。勝ちです。

## 動作環境

- Java 21（Temurin 推奨。Oracle JDK 使ってる人は法務に怒られてないか確認してください）
- Gradle 8.10.x
- `com.anthropic:anthropic-java:2.35.0`（2026/05 公式リリース、これでようやく API 安定）
- Claude Haiku 4.5 / Sonnet 4.6 / Opus 4.6
- Anthropic API キー（無いなら今すぐ取ってきてください、5 分で済みます）

## 最小構成（マジで 10 行）

`build.gradle`:

```groovy
dependencies {
  implementation 'com.anthropic:anthropic-java:2.35.0'
}
```

`Ping.java`:

```java
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.*;

public class Ping {
  public static void main(String[] args) {
    AnthropicClient client = AnthropicOkHttpClient.fromEnv();
    Message msg = client.messages().create(MessageCreateParams.builder()
        .model(Model.CLAUDE_HAIKU_4_5)
        .maxTokens(64L)
        .addUserMessage("Hello, Claude!")
        .build());
    System.out.println(msg.content().get(0).text().orElseThrow().text());
  }
}
```

```bash
export ANTHROPIC_API_KEY=sk-ant-...
./gradlew run
```

動きます。動かなかったら `JAVA_HOME` が Java 8 を指してます。10 年前のあなたが悪い。

## Spring Boot から呼ぶ

```java
@Service
public class ClaudeService {
  private final AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  public String ask(String prompt) {
    return client.messages().create(MessageCreateParams.builder()
        .model(Model.CLAUDE_HAIKU_4_5)
        .maxTokens(1024L)
        .addUserMessage(prompt)
        .build())
        .content().get(0).text().orElseThrow().text();
  }
}
```

`@Service` 付けて Bean 化。`fromEnv()` が `ANTHROPIC_API_KEY` を読みに行ってくれる。
ここで「いやキーは AWS Secrets Manager から…」とか言い出す人は、まず動かしてから言ってください。動かす前に設計を語る人がプロジェクトを壊します。

## ストリーミング（SSE）— ChatGPT みたいなアレ

```java
@RestController
public class StreamController {
  private final AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  @GetMapping(value = "/chat/stream", produces = "text/event-stream")
  public Flux<String> stream(@RequestParam String q) {
    return Flux.create(sink -> {
      try (var stream = client.messages().createStreaming(...)) {
        stream.stream().forEach(event ->
            event.contentBlockDelta()
                .flatMap(d -> d.delta().text())
                .ifPresent(t -> sink.next(t.text())));
        sink.complete();
      }
    });
  }
}
```

`Flux` 出してきた瞬間に「うっ Reactive…」って顔する人多いんですが、
こいつに関しては「文字をちょびちょび吐く蛇口」だと思っとけば 8 割いけます。
残り 2 割で本番が落ちます。`backpressure` で検索しといてください。

## Tool Use（関数呼び出し）— 最大の地雷ポイント

⚠️ 2.x 系では `List<ToolUnion>` でラップ必須：

```java
.tools(myTools.stream().map(ToolUnion::ofTool).toList())
```

これ忘れると `incompatible types: List<Tool> cannot be converted to List<ToolUnion>` で javac が真顔で殴ってきます。

0.x からの移行者全員 1 回これで詰まる。私も詰まった。Stack Overflow にもまだ載ってない（2026/05 時点）。
**この記事を踏んだあなたはラッキー**。ブクマしといてください。後で同僚を救えます。

## Prompt Caching — 課金を 80% カットする魔法

長いシステムプロンプトに `CacheControlEphemeral` を貼る：

```java
TextBlockParam.builder()
    .text(longSystemPrompt)
    .cacheControl(CacheControlEphemeral.builder().build())
    .build()
```

実測で **入力トークン課金が 80〜90% カット** されます。
うちのチームはこれ入れた翌月の請求書見て「桁間違ってない？」って 3 回確認しました。

5 分で実装できて月数万円浮きます。やらない理由がない。
（ただし「同じプロンプトが繰り返される」前提です。毎回違うプロンプトを投げてる場合はキャッシュヒット 0% です。当たり前です。）

## エラーハンドリング — 一見トラップ

`RateLimitException` は `AnthropicException` を継承しています。
継承してるなら一括 catch できるよね？

**できません。**

```java
try {
  client.messages().create(params);
} catch (RateLimitException e) {        // ← 必ず別で書く
  sleep(60_000);
  retry();
} catch (AnthropicException e) {
  log.error("Claude error", e);
}
```

`catch (RateLimitException | AnthropicException e)` と書くと javac に
`Alternatives in a multi-catch statement cannot be related by subclassing` と怒られます。

「いや知っとるわ Java の仕様や」とイキりたいところですが、書いた直後に毎回これで javac に詰められます。人間は学ばない。

## まとめ

- `AnthropicOkHttpClient.fromEnv()` で 1 行起動
- ストリーミングは `StreamResponse<RawMessageStreamEvent>`
- Tool Use は `ToolUnion::ofTool` ラップ必須（**ここでだいたい詰む**）
- Prompt Caching は `CacheControlEphemeral`（**ここで請求書が桁違いに減る**）

公式 SDK は驚くほど薄いです。薄すぎて「これ自前ラッパー書いた方が早くない？」と思った瞬間、3 ヶ月後の自分が `null` で落ちて泣きます。素直に使いましょう。

---

サンプルコードは GitHub に置いてあります：https://github.com/kekke98810/ooze
