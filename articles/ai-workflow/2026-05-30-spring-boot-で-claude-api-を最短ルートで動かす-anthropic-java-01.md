---
id: "2026-05-30-spring-boot-で-claude-api-を最短ルートで動かす-anthropic-java-01"
title: "Spring Boot で Claude API を最短ルートで動かす — anthropic-java 2.35.0 実戦ガイド"
url: "https://zenn.dev/ooze/articles/3056d4bf25df3e"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "LLM", "OpenAI", "Python", "zenn"]
date_published: "2026-05-30"
date_collected: "2026-05-31"
summary_by: "auto-rss"
query: ""
---

> Java/Spring 開発者向けに「コピペで動く Claude API スニペット 10 本」を 1 つの Gradle プロジェクトにまとめた。  
> 全文（PDF + Java コード）は Gumroad で配布している。本記事はそのダイジェスト版。

## なぜ書いたか

LLM 連携のサンプルは、ほぼ 100% が Python と OpenAI SDK で書かれている。  
だが実際の業務システムの大半は Java、特に Spring Boot で動いている。  
「Spring から Claude を叩く最短手順」をまとめた日本語資料が見当たらなかったので、自分で書いた。

公式 `anthropic-java` 2.35.0 が 2026 年 5 月にリリースされ、API も安定したので、  
今のタイミングで作ったテンプレ集は **半年以上は無修正で使える** はず。

## 動作環境

* Java 21（Temurin）
* Gradle 8.10.x
* `com.anthropic:anthropic-java:2.35.0`
* Claude Haiku 4.5 / Sonnet 4.6 / Opus 4.6

## 最小構成：1 行で API キーを読む

```
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.*;

public class Ping {
  public static void main(String[] args) {
    AnthropicClient client = AnthropicOkHttpClient.fromEnv();  // ANTHROPIC_API_KEY を読む
    Message msg = client.messages().create(MessageCreateParams.builder()
        .model(Model.CLAUDE_HAIKU_4_5)
        .maxTokens(64L)
        .addUserMessage("Spring Boot で Claude を使う最小コードを 1 行で。")
        .build());
    System.out.println(msg.content().get(0).text().orElseThrow().text());
  }
}
```

`build.gradle` は依存 1 行追加するだけ：

```
dependencies {
  implementation 'com.anthropic:anthropic-java:2.35.0'
}
```

## ストリーミング（SSE 風）

```
try (var stream = client.messages().createStreaming(params)) {
  stream.stream().forEach(event -> event.contentBlockDelta()
      .flatMap(d -> d.delta().text())
      .ifPresent(t -> System.out.print(t.text())));
}
```

Spring WebFlux で `Flux<String>` に流し込めば、フロントには SSE / WebSocket でそのまま返せる。

`com.anthropic.models.messages.Tool` を組み立てて `MessageCreateParams.builder().tools(...)` に渡す。  
2.35.0 系では `List<ToolUnion>` 受け取りに変わったので、ラップが必要：

```
.tools(myTools.stream().map(ToolUnion::ofTool).toList())
```

ここでハマる人が多い（自分も 1 時間溶かした）。

## Prompt Caching でコストを 80% 落とす

長いシステムプロンプトや大量の文脈は `CacheControlEphemeral` を付けてキャッシュ可能：

```
TextBlockParam.builder()
    .text(longSystemPrompt)
    .cacheControl(CacheControlEphemeral.builder().build())
    .build()
```

5 分間有効。同じプロンプトが連続するチャットボット用途では実測 80% コストダウン。

## 続きは

ここで触れた 10 本のスニペットを 1 つの Gradle プロジェクトにまとめた最小版と、Spring Boot 統合（ストリーミング Controller、RAG、エラー再試行、コスト計算、Cloudflare Tunnel デプロイ）まで全部入れたフル版の 2 種類を Gumroad で配布しています。

### 🛒 ¥980 / Spring × Claude 10連発スニペット集 v0.1.0

API 叩く最小コードだけ欲しい人向け。Gradle プロジェクト + PDF 8 ページ。

👉 <https://keisuke62.gumroad.com/l/spring-claude-quickstart>

### 📘 ¥2,480 / Spring Boot × Claude API 実装テンプレ集 v1.0.0

業務に組み込みたい人向け。**12 章 / 94 ページ PDF + 11 個の動く Gradle プロジェクト**。  
ストリーミング・Tool Use・Prompt Caching・pgvector RAG・Cloudflare Tunnel デプロイまで全部入り。

👉 <https://keisuke62.gumroad.com/l/xphul>

---

質問・要望は GitHub Issues へ。  
リポジトリ: <https://github.com/kekke98810/ooze>
