---
id: "2026-05-30-anthropic-java-の-tool-use-を-spring-boot-で実装する-tool-01"
title: "anthropic-java の Tool Use を Spring Boot で実装する — ToolUnion 化と JSON Sche"
url: "https://zenn.dev/ooze/articles/df44aecd9b0a57"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "zenn"]
date_published: "2026-05-30"
date_collected: "2026-05-31"
summary_by: "auto-rss"
query: ""
---

> anthropic-java 2.35.0 で Tool Use（関数呼び出し）を実装する際の最短コードと、  
> 0.x 系から 2.x 系に上がる時にハマるポイントを Spring Boot 文脈で解説する。

## TL;DR

```
// 1. Tool 定義
Tool weather = Tool.builder()
    .name("get_weather")
    .description("指定都市の現在天気を返す")
    .inputSchema(Tool.InputSchema.builder()
        .properties(JsonValue.from(Map.of(
            "city", Map.of("type", "string", "description", "都市名"))))
        .putAdditionalProperty("required", JsonValue.from(new String[]{"city"}))
        .build())
    .build();

// 2. ⚠️ 2.x 系では List<ToolUnion> でないとコンパイル通らない
var params = MessageCreateParams.builder()
    .model(Model.CLAUDE_HAIKU_4_5)
    .maxTokens(1024L)
    .tools(List.of(weather).stream().map(ToolUnion::ofTool).toList())  // ←ここ
    .addUserMessage("東京の天気は？")
    .build();
```

`ToolUnion::ofTool` のラップを忘れると `incompatible types: List<Tool> cannot be converted to List<ToolUnion>` で死ぬ。

2.x で `tools()` の受け取り型が `List<Tool>` → `List<ToolUnion>` に変わったのは、  
**Server Tools（`web_search`, `computer_use`, `text_editor` など）と User Tool を同じ配列に混ぜられるように** するため。

```
// User Tool + Anthropic 提供の Web 検索ツールを同居可能
.tools(List.of(
    ToolUnion.ofTool(weather),
    ToolUnion.ofWebSearchTool20250305(WebSearchTool20250305.builder().build())
))
```

これは旧 SDK ではできなかった重要な進化。

## ツール呼び出しの結果を返すループ

Claude が「ツール使いたい」と返してきたら、こっちで実行して結果を `tool_result` で返す：

```
Message response = client.messages().create(params);

if (response.stopReason().equals(StopReason.TOOL_USE)) {
  // response.content() の中から ToolUseBlock を探す
  ToolUseBlock toolUse = response.content().stream()
      .map(ContentBlock::toolUse)
      .flatMap(Optional::stream)
      .findFirst().orElseThrow();

  // 実行
  String result = executeWeather(toolUse.input());

  // 次のターン: 結果を tool_result で返す
  var nextParams = MessageCreateParams.builder()
      .model(Model.CLAUDE_HAIKU_4_5)
      .maxTokens(1024L)
      .messages(List.of(
          MessageParam.builder().role(MessageParam.Role.USER)
              .content("東京の天気は？").build(),
          MessageParam.builder().role(MessageParam.Role.ASSISTANT)
              .content(response.content()).build(),
          MessageParam.builder().role(MessageParam.Role.USER)
              .contentOfBlockParams(List.of(
                  ContentBlockParam.ofToolResult(ToolResultBlockParam.builder()
                      .toolUseId(toolUse.id())
                      .content(result)
                      .build())))
              .build()))
      .tools(List.of(ToolUnion.ofTool(weather)))
      .build();

  Message finalAnswer = client.messages().create(nextParams);
  System.out.println(finalAnswer.content().get(0).text().orElseThrow().text());
}
```

## Spring Boot に組み込む時の型分離

Service 層は `List<Tool>` で受け、API 呼ぶ直前で `ToolUnion` 化が綺麗：

```
@Service
public class ClaudeToolService {
  private final AnthropicClient client = AnthropicOkHttpClient.fromEnv();
  private final List<Tool> myTools;  // Bean として注入

  public String ask(String userInput) {
    var params = MessageCreateParams.builder()
        .model(Model.CLAUDE_HAIKU_4_5)
        .maxTokens(1024L)
        .tools(myTools.stream().map(ToolUnion::ofTool).toList())  // ← ここで union 化
        .addUserMessage(userInput)
        .build();
    // ...ループ実装
  }
}
```

ドメイン層は SDK 型に汚染されない（`Tool` の方がドメインに近い）。

## ハマったポイント 3 つ

1. **`inputSchema` の `required` を `putAdditionalProperty` で渡す** — 直接 `.required(...)` メソッドは無い
2. **`input()` は `JsonValue`** — `Map` にしたければ `.asObject()` 経由
3. **`StopReason` は文字列ではなく enum** — `.toString()` ではなく `==` か `.equals()` 比較

## 続き

この記事の完全版コードは GitHub にあります。  
さらに「ストリーミング」「Prompt Caching」「pgvector RAG」まで含む 12 章フル版を Gumroad で配布中：

リポジトリ: <https://github.com/kekke98810/ooze>
