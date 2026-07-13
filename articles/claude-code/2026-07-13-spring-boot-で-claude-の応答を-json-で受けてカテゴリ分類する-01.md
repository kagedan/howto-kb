---
id: "2026-07-13-spring-boot-で-claude-の応答を-json-で受けてカテゴリ分類する-01"
title: "Spring Boot で Claude の応答を JSON で受けてカテゴリ分類する"
url: "https://zenn.dev/propagandist/articles/0018-spring-boot-claude-structured-output"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-07-13"
date_collected: "2026-07-14"
summary_by: "auto-rss"
query: ""
---

## この記事について

* **対象読者**：[1本目](https://zenn.dev/propagandist/articles/0001-spring-boot-claude-api-java-sdk)で Claude を呼べるようになった人、あるいは自由文ではなく**決まった選択肢**で結果を受け取りたい人
* **得られること**：Claude に JSON で答えさせ、Java の `enum` に**安全に**マッピングする実装（未知値・崩れた出力のフォールバック込み）
* **前提・環境**：Java 21 / Spring Boot 3.5 / `com.anthropic:anthropic-java` 2.34.0。JSON パースは Spring Web 同梱の Jackson を使います

> この記事は「[Spring Boot から公式 Java SDK で Claude API を呼ぶ最小実装](https://zenn.dev/propagandist/articles/0001-spring-boot-claude-api-java-sdk)」の続編です。

> バージョン・モデル名は\*\*執筆時点（2026年6月）\*\*のものです。最新は公式情報で確認してください。

## 結論（先に全体像）

「日記の文章をカテゴリ（`WORK`・`PRIVATE`・`LEARNING`・`OTHER`）に分類する」例で実装します。やることは3つ。

1. JSON だけを返すよう `system` で指示する
2. 応答を Jackson でパースして `category` を取り出す
3. `enum` に変換し、**未知値・崩れた出力は `OTHER` にフォールバックさせる**

生成 AI の出力は一定しません。前後に説明文が付いたり、未知のカテゴリを返したりするので、**フォールバックを最初から入れておく**のが要点です。

## 手順1：カテゴリを enum で定義する

選択肢を `enum` にし、安全側のデフォルトも持たせます。

```
public enum PostCategory {
    WORK, PRIVATE, LEARNING, OTHER;

    // 未知値・パース失敗時に倒す安全側のデフォルト
    public static final PostCategory FALLBACK = OTHER;
}
```

## 手順2：JSON を指示し、パースして enum に変換する

`system` で「JSON だけを出力」と明示します。パース部分は**ネットワーク非依存の純粋メソッド**に切り出しておくと、そのままユニットテストできます（後述）。

```
@Service
@RequiredArgsConstructor
@Slf4j
public class CategoryClassifier {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private static final String SYSTEM = """
            あなたは日記の文章をカテゴリに分類する分類器です。
            次のいずれかをちょうど1つ選び、JSON だけを出力してください。
            カテゴリ: WORK / PRIVATE / LEARNING / OTHER
            出力形式: {"category": "WORK"}
            前後に説明文やコードフェンスを付けないこと。
            """;

    private final AnthropicClient client;
    private final AnthropicProperties properties;

    public PostCategory classify(String diaryText) {
        var params = MessageCreateParams.builder()
                .model(properties.model())
                .maxTokens(properties.maxTokens())
                .system(SYSTEM)
                .addUserMessage(diaryText)
                .build();
        try {
            var response = client.messages().create(params);
            var raw = response.content().stream()
                    .flatMap(block -> block.text().stream())
                    .map(text -> text.text())
                    .collect(Collectors.joining());
            return parse(raw);
        } catch (AnthropicException e) {
            log.error("claude classify call failed", e);
            return PostCategory.FALLBACK;
        }
    }

    // 応答文字列から category を取り出して enum に変換。未知値・失敗は OTHER に倒す。
    static PostCategory parse(String raw) {
        if (raw == null || raw.isBlank()) {
            return PostCategory.FALLBACK;
        }
        try {
            JsonNode node = MAPPER.readTree(extractJson(raw));
            String value = node.path("category").asText("");
            return PostCategory.valueOf(value.trim().toUpperCase(Locale.ROOT));
        } catch (Exception e) {
            return PostCategory.FALLBACK; // パース不能・未知カテゴリ
        }
    }

    // 前後に文章が混じっても、最初の { から最後の } までを JSON として取り出す
    private static String extractJson(String raw) {
        int start = raw.indexOf('{');
        int end = raw.lastIndexOf('}');
        return (start >= 0 && end > start) ? raw.substring(start, end + 1) : raw;
    }
}
```

`PostCategory.valueOf(...)` は未知の文字列で例外を投げます。これを `catch` して `OTHER` にフォールバックさせるのが、分類を**壊さない**ための要点です。

## 手順3：パースをテストで固める

`parse` は API を呼ばないので、実値で検証できます。「正常系」「前後に文章が混じる・大小文字」「未知値・崩れ・空」を押さえておけば、主要な崩れを吸収できます。

```
class CategoryClassifierTest {

    @Test
    void parsesValidJson() {
        assertEquals(PostCategory.WORK, CategoryClassifier.parse("{\"category\":\"WORK\"}"));
    }

    @Test
    void toleratesSurroundingTextAndCase() {
        assertEquals(PostCategory.PRIVATE,
                CategoryClassifier.parse("はい → {\"category\": \"private\"} 以上"));
    }

    @Test
    void fallsBackOnUnknownOrBroken() {
        assertEquals(PostCategory.OTHER, CategoryClassifier.parse("{\"category\":\"SHOPPING\"}"));
        assertEquals(PostCategory.OTHER, CategoryClassifier.parse("not json"));
        assertEquals(PostCategory.OTHER, CategoryClassifier.parse(null));
    }
}
```

## つまずきポイントと解決

実運用で遭遇しやすい崩れ方と、その吸収方法をまとめます。いずれも本記事の `parse`・`extractJson` で対処済みなので、対応の勘所として押さえておいてください。

* **コードフェンスや前置きが混ざる**：```` ```json ```` で囲われていることがあります。最初の `{` から最後の `}` までを取り出せば吸収できます。
* **未知のカテゴリが返される**：`valueOf` が例外になります。`catch` して `OTHER` にフォールバックさせ、分類処理を止めないこと。
* **空応答**：`null`・空文字はいずれも `OTHER` として扱い、入口でガードします。
* **より厳密にやりたい**：本記事はプロンプトで JSON 形式を指示し、パースとフォールバックで守る方式です。これで十分実用的ですが、SDK 側で出力スキーマそのものを強制したい場合は、構造化出力（Structured Outputs：strict なツール定義や出力フォーマット指定）という別アプローチもあります（対応モデルは執筆時点で要確認）。

## まとめ

* 「JSON だけ」を `system` で指示 → Jackson でパース → `enum` に変換
* 未知値・崩れ・空は **既定値の `OTHER` に寄せる**フォールバックを最初から入れる
* パースは純粋メソッドに切り出してユニットテストで固める

この「AI でカテゴリを自動分類する」発想は、書籍のサンプルアプリ（AI 日記アプリ）でも日記の自動分類として使っています。**仕様定義から実装・テスト・デプロイまで**を Claude Code と一気通貫で進める流れは、拙著にまとめています。Spring Security / JPA / Flyway や本番デプロイ（Railway）まで、AI と対話しながら 1つの Web アプリを完成させる構成です。

📘 『**Claude Codeと生み出す Spring Boot実践開発 ～AI日記アプリを仕様定義からデプロイまで～**』

※ Amazon のリンクはアフィリエイトリンクを含みます。
