---
id: "2026-07-10-spring-boot-で-claude-に会話履歴を渡して多ターンで話す-01"
title: "Spring Boot で Claude に会話履歴を渡して多ターンで話す"
url: "https://zenn.dev/propagandist/articles/0017-spring-boot-claude-multi-turn"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

## この記事について

* **対象読者**：[1本目](https://zenn.dev/propagandist/articles/0001-spring-boot-claude-api-java-sdk)で単発の呼び出しまで作った人／チャットのように「文脈を覚えた」やり取りをしたい人
* **得られること**：`system` で役割を固定し、過去のやり取り（会話履歴）を積んで**多ターン**で Claude に話す最小実装
* **前提・環境**：Java 21 / Spring Boot 3.5 / `com.anthropic:anthropic-java` 2.34.0。1本目の `AnthropicClient` と `AnthropicProperties` を使います

> この記事は「[Spring Boot から公式 Java SDK で Claude API を呼ぶ最小実装](https://zenn.dev/propagandist/articles/0001-spring-boot-claude-api-java-sdk)」の続編です。応答を逐次表示する[ストリーミング編](https://zenn.dev/propagandist/articles/0002-spring-boot-claude-streaming)も別記事にあります。

> バージョン・モデル名は\*\*執筆時点（2026年6月）\*\*のものです。最新は公式情報で確認してください。

## 結論（先に全体像）

ポイントは2つです。

* **役割・前提は `system` に置く**（`messages` に混ぜない）
* **Claude API はステートレス**。サーバー側に会話状態は残らないので、これまでの履歴を `user` / `assistant` 交互に**毎回**送る

```
var params = MessageCreateParams.builder()
        .model(properties.model())
        .maxTokens(properties.maxTokens())
        .system("あなたは Spring Boot に詳しいメンターです。")
        .addUserMessage("DIって何？")
        .addAssistantMessage("依存を外から渡す仕組みです。")
        .addUserMessage("それを Spring でやるには？") // ← 今回の発話
        .build();
```

## 手順1：会話履歴を表す型を用意する

履歴を文字列で持ち回ると順序や役割が崩れがちです。`user` / `assistant` のターン列を**不変**で持つ小さな型を用意します。`with〜` は新しい `Conversation` を返すので、状態の取り回しが安全になります。あわせて「`user` から始まり、`user` / `assistant` が交互に並ぶ」ことを生成時に検証し、崩れた履歴は拒否します。

```
public record Conversation(List<Turn> turns) {

    public enum Role { USER, ASSISTANT }

    public record Turn(Role role, String text) {}

    public Conversation {
        turns = List.copyOf(turns); // 不変化
        for (int i = 0; i < turns.size(); i++) {
            var expected = (i % 2 == 0) ? Role.USER : Role.ASSISTANT; // user から交互
            if (turns.get(i).role() != expected) {
                throw new IllegalArgumentException("履歴は user から始め、user / assistant を交互に積みます");
            }
        }
    }

    public static Conversation empty() {
        return new Conversation(List.of());
    }

    public Conversation withUser(String text) {
        return append(new Turn(Role.USER, text));
    }

    public Conversation withAssistant(String text) {
        return append(new Turn(Role.ASSISTANT, text));
    }

    private Conversation append(Turn turn) {
        var next = new ArrayList<>(turns);
        next.add(turn);
        return new Conversation(next);
    }
}
```

## 手順2：system ＋ 履歴 ＋ 今回の発話で呼ぶ

履歴を順に積んでから、最後に今回のユーザー発話を足して呼び出します。テキストブロックを連結して応答を取り出す流れは1本目と同じです。空のレスポンスの扱いは1本目を参照してください。

```
@Service
@RequiredArgsConstructor
@Slf4j
public class ConversationAiAssistant {

    private final AnthropicClient client;
    private final AnthropicProperties properties;

    public String ask(String system, Conversation history, String userMessage) {
        var builder = MessageCreateParams.builder()
                .model(properties.model())
                .maxTokens(properties.maxTokens())
                .system(system); // 役割づけは messages ではなく system に

        for (var turn : history.turns()) {
            switch (turn.role()) {
                case USER -> builder.addUserMessage(turn.text());
                case ASSISTANT -> builder.addAssistantMessage(turn.text());
            }
        }
        builder.addUserMessage(userMessage); // 今回の発話を最後に

        try {
            var response = client.messages().create(builder.build());
            return response.content().stream()
                    .flatMap(block -> block.text().stream())
                    .map(text -> text.text())
                    .collect(Collectors.joining());
        } catch (AnthropicException e) {
            log.error("claude conversation call failed", e);
            throw new IllegalStateException("Failed to call Claude", e);
        }
    }
}
```

呼び出し側は、今回の発話と返された応答の**両方**を履歴に足してから、次のターンへ渡します。どちらか片方だけだと、次の呼び出しで文脈が抜けます。

```
var system = "あなたは Spring Boot に詳しいメンターです。";
var history = Conversation.empty()
        .withUser("DIって何？")
        .withAssistant("依存を外から渡す仕組みです。");

var question = "それを Spring でやるには？";
var answer = assistant.ask(system, history, question);

history = history.withUser(question).withAssistant(answer); // 次のターンへ
```

## つまずきポイントと解決

多ターンでつまずきやすいのは、履歴の持ち方とトークンの消費まわりです。代表的な4点と対処を挙げます。

* **前のやり取りを覚えていない**：API はステートレスです。サーバー側に会話状態は残らないので、履歴は毎回まるごと送ります。
* **履歴の並びが崩れる**：`messages` の先頭は `user` である必要があります。その先を `user` / `assistant` の交互に保つのは、履歴を扱いやすくするために `Conversation` が自前で課した不変条件です。応答を履歴へ戻し忘れると、直前のやり取りが抜けたまま送られ、文脈がつながりません。`Conversation` は生成時にこの並びを検証し、崩れた履歴を拒否します。
* **トークンが増え続ける**：履歴は長くなるほど入力トークンを消費します。上限を見ながら、古いターンを要約・間引くなどの対処を検討します。
* **役割を `messages` に書いてしまう**：キャラクターや前提は `system` に置くのが基本です。`messages` はあくまで「やり取り」に使います。

## まとめ

* 役割は `system`、過去のやり取りは `user` / `assistant` 交互に `messages` へ
* API はステートレス。履歴は毎回送る前提で、不変の `Conversation` に持たせると、並びの崩れも生成時に拒否できる
* 応答は履歴へ足して次のターンに渡す

ここでは「文脈を保った会話」の最小形に絞りましたが、**仕様定義から実装・テスト・デプロイまで**を Claude Code と一気通貫で進める流れは、拙著にまとめています。Spring Security / JPA / Flyway や本番デプロイ（Railway）まで、AI と対話しながら 1つの Web アプリを完成させる構成です。

📘 『**Claude Codeと生み出す Spring Boot実践開発 ～AI日記アプリを仕様定義からデプロイまで～**』

※ Amazon のリンクはアフィリエイトリンクを含みます。
