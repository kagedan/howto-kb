---
id: "2026-06-26-tidb-のベクトル検索と-claude-で作る最小-ragspring-boot-java-01"
title: "TiDB のベクトル検索と Claude で作る最小 RAG（Spring Boot / Java）"
url: "https://zenn.dev/propagandist/articles/0003-spring-boot-tidb-vector-rag"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "zenn"]
date_published: "2026-06-26"
date_collected: "2026-06-27"
summary_by: "auto-rss"
query: ""
---

## この記事について

「RAG はやりたい。でも、そのために専用のベクトル DB を新しく増やすのは気が重い」。そう感じたことはありませんか。本記事の答えは「**MySQL 互換の TiDB をそのまま検索基盤に使う**」です。いつもの **Spring Boot と JdbcTemplate のまま**、最小の RAG を作れるようになります。

* **対象読者**：Spring Boot / Java で RAG（検索拡張生成）を作りたい人／**専用ベクトル DB を増やさず**に始めたい人／TiDB のベクトル検索を実装で触ってみたい人
* **得られること**：埋め込み（Voyage）→ ベクトル検索（TiDB）→ 生成（Claude）の**動く最小 RAG**。`VECTOR` 列・`VEC_COSINE_DISTANCE` の呼び出しまで踏み込みます。コードは**実機で確認済み**なので、そのまま再現できます
* **前提・環境**：Java 21 / Spring Boot 3.5 / `anthropic-java` 2.34.0 / MySQL Connector/J / TiDB Cloud

> バージョン（SDK・Spring Boot）とモデル名は\*\*執筆時点（2026 年 6 月）\*\*のものです。最新は各公式情報で確認してください。SQL は [TiDB 公式ドキュメント](https://docs.pingcap.com/tidbcloud/vector-search-overview/)に準拠しています。

## 結論（先に全体像）

LLM（Claude のような大規模言語モデル）は、学習していないこと（社内ドキュメントや最新の仕様、あなた自身のデータ）を知りません。知らないことを聞くと、もっともらしい誤答（ハルシネーション）が混ざります。全文書をプロンプトへ詰めるのは、長さの上限で頭打ちになります。ファインチューニング（モデル自体の再学習）は、更新のたびに手間がかかります。

**RAG は、質問のたびに関係する文書だけを検索し、根拠として LLM へ渡す方法**です。これにより、モデルが知らない情報にも、根拠つきで答えられます。最小構成は次の 3 つの部品でできます。

1. **埋め込み（embedding）**：テキストをベクトルに変換する → **Voyage AI**
2. **ベクトル検索**：質問ベクトルに近い文書を探す → **TiDB のベクトル検索**
3. **生成**：見つけた文書を根拠に答える → **Claude**

文書は、検索しやすい小さな単位（チャンク）に区切ってから埋め込みます。検索もチャンク単位で行うので、関係する部分だけを根拠に渡せます。

ポイントは、**検索の置き場を新しいベクトル専用 DB ではなく TiDB にする**ことです。TiDB は MySQL 互換なので、アプリ側は**いつもの JDBC / JdbcTemplate のまま**ベクトルを読み書きできます。リレーショナルなデータとベクトルを同じ DB・同じトランザクションで扱えるのが、RAG の基盤としての TiDB の利点です。

この最小構成でも、RAG の効きどころは押さえられます。

* **取り込んだ文書が根拠**：一般知識ではなく、あなたの文書から答えます。
* **ハルシネーションを抑える**：根拠が無ければ「記載がありません」と返せます（手順6・動作確認で確かめます）。
* **再学習せずに更新**：知識の追加はチャンクを INSERT するだけで、最新へ追従できます。

しかも TiDB なら、これらを**専用ベクトル DB を足さずに**実現できます。さらに、この同居（リレーショナルなデータ × ベクトル）は、閲覧範囲・障害調査・業務条件での絞り込みといった実運用の応用（後述）にもそのまま活かせます。

「埋め込み」が初めてなら（クリックで開く）

埋め込み（embedding）は、テキストを数値の並び（ベクトル）に変換することです。その数値は、文の「意味」を表します。色は `(R, G, B)` の 3 つの数字で表せます。赤っぽい色どうしは、その値も近いです。これと同じことを、テキストの意味に対して行うのが埋め込みです。Voyage の埋め込みは 1024 個の数字を使います。

肝は、意味の近い文ほどベクトルも近くなるよう、モデルが学習されている点です。

```
「当社のコアタイムは11時から15時です」 → [ 0.01, -0.04, 0.02, ... ]（1024個）
「コアタイムは何時から？」          → [ 0.01, -0.03, 0.02, ... ]（似た並び）
```

この2つは意味が近いので、数値の並びも近くなります。あとは質問ベクトルに近い文書を距離で探すだけです。それが、ベクトル検索（近傍検索とも呼びます）です。距離は後述の `VEC_COSINE_DISTANCE` で測ります。

キーワード検索との違いもここにあります。キーワード検索は「コアタイム」という単語を含む文しか拾えません。埋め込み検索は意味で拾うので、「始業時間」のような言い換えにも反応します。

次元（1024）をそろえるのは、これが理由です。Voyage はいつも 1024 個の数字を返すので、保存先も `VECTOR(1024)` にします。長さの違うベクトルどうしは、距離を測れません。

### なぜ埋め込みは Voyage AI なのか

Claude（Anthropic）には**埋め込み API がありません**。埋め込みは専業の [Voyage AI](https://docs.voyageai.com/docs/embeddings) に任せ、生成を Claude が担当します。埋め込みモデルは差し替え可能なので、別のプロバイダや自前モデルでも構いません。**大事なのは「埋め込みの次元数」と「TiDB の `VECTOR(N)` の N を一致させる」こと**だけです。

## 準備：外部サービスのアカウント

3 つの外部サービスを使います。**Voyage と TiDB Cloud は無料枠**から始められます。**Claude には継続的な無料枠はなく従量課金**ですが、本記事の最小デモで使うトークンはごくわずか（1 問あたり 1 円未満）です（いずれも執筆時点）。

* **Claude（生成）**：[Anthropic Console](https://console.anthropic.com) で API キーを発行します。
* **Voyage AI（埋め込み）**：[Voyage AI のダッシュボード](https://dashboard.voyageai.com) でサインアップし、API キーを発行します。
* **TiDB Cloud（ベクトル検索）**：[TiDB Cloud](https://tidbcloud.com) でサインアップし、「Create Cluster」から **Starter**（無料・約 30 秒）を作成します。作成後、\*\*「Connect」\*\*からホスト・ユーザー・パスワードを控えます。

控えたキーと接続情報は、最後の「動かす」で `.env` にまとめて設定します。TiDB のテーブル作成（手順2）は、このクラスタの **SQL エディタ**で行います。

## 手順1：プロジェクトと依存

Java 21 / Spring Boot 3.5 のプロジェクトを用意します（Spring Initializr など）。その `build.gradle.kts` の `dependencies` を次のようにします。何のためかはコメントのとおりです。TiDB は MySQL 互換なので、接続は **MySQL Connector/J をそのまま**使います。

```
dependencies {
    // REST（/ingest・/ask）とリクエスト検証
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    // JdbcTemplate で TiDB を読み書き
    implementation("org.springframework.boot:spring-boot-starter-jdbc")
    // Claude を呼ぶ公式 Java SDK
    implementation("com.anthropic:anthropic-java:2.34.0")

    // TiDB は MySQL 互換 → Connector/J で接続
    runtimeOnly("com.mysql:mysql-connector-j")

    // ボイラープレート削減
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")
}
```

## 手順2：TiDB にベクトル列のテーブルを用意する

TiDB ではテーブルに **`VECTOR(N)` 列**を持たせ、近傍検索の距離関数として **`VEC_COSINE_DISTANCE`**（コサイン距離）を使います。コサイン距離はベクトルの向きの近さで、値が小さいほど似ています。チャンク本文と埋め込みを 1 行で持つテーブルを用意します。

```
CREATE TABLE rag_chunks (
    chunk_id   BIGINT       PRIMARY KEY AUTO_RANDOM,
    doc_id     VARCHAR(128) NOT NULL,
    chunk_text TEXT         NOT NULL,
    embedding  VECTOR(1024) NOT NULL,
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    -- コサイン距離での近傍検索を速くする HNSW ベクトルインデックス
    VECTOR INDEX idx_embedding ((VEC_COSINE_DISTANCE(embedding)))
);
```

* `VECTOR(1024)` の **1024 は Voyage の埋め込み次元**。両者を一致させます。
* `VECTOR INDEX ... ((VEC_COSINE_DISTANCE(embedding)))` は HNSW（Hierarchical Navigable Small World）のベクトルインデックスです。**データが少ないうちはインデックス無しでも全件スキャンで同じ結果**になるので、まず動かしたいだけなら後回しでも構いません（インデックスの詳細は [Vector Search Index](https://docs.pingcap.com/tidbcloud/vector-search-index/)）。

このスキーマは、準備で作ったクラスタの **SQL エディタ**で一度だけ実行します（`VECTOR` 型は TiDB 固有なので、ローカルの H2 などでは動きません）。

接続設定は `application.yaml` に書きます。TiDB Cloud Starter（旧 Serverless）は TLS 必須なので、接続 URL に `sslMode=VERIFY_IDENTITY` を付けます。

```
spring:
  config:
    import: optional:file:.env[.properties]   # 開発時は .env からキー・接続情報を読む（本番は OS 環境変数）
  datasource:
    url: ${TIDB_JDBC_URL}      # jdbc:mysql://gateway01.<region>.prod.aws.tidbcloud.com:4000/test?sslMode=VERIFY_IDENTITY
    username: ${TIDB_USER}
    password: ${TIDB_PASSWORD}
    driver-class-name: com.mysql.cj.jdbc.Driver

anthropic:
  model: claude-opus-4-8
  max-tokens: 1024
voyage:
  base-url: https://api.voyageai.com/v1
  model: voyage-4
  dimensions: 1024  # VECTOR(N) と一致させ、手順4の次元チェックに使う
rag:
  top-k: 4
```

`spring.config.import: optional:file:.env[.properties]` は、開発時にプロジェクト直下の `.env` からキー・接続情報を読み込む指定です。Spring Boot は標準では `.env` を読みません。`optional:` 付きなので、`.env` が無い本番では OS の環境変数がそのまま使われます。

## 手順3：設定を型で受ける

モデル名や次元数を散らさないよう、`record` の `@ConfigurationProperties` へ切り出します（3 つとも `@Validated`）。

```
@ConfigurationProperties(prefix = "anthropic")
@Validated
public record AnthropicProperties(@NotBlank String model, @Min(1) int maxTokens) {}

@ConfigurationProperties(prefix = "voyage")
@Validated
public record VoyageProperties(@NotBlank String baseUrl, @NotBlank String model, @Min(1) int dimensions) {}

@ConfigurationProperties(prefix = "rag")
@Validated
public record RagProperties(@Min(1) int topK) {}
```

外部クライアントは Bean 化します。API キーは環境変数（開発時は `.env`）から読み、コードに直書きしません。

```
@Configuration
@EnableConfigurationProperties({AnthropicProperties.class, VoyageProperties.class, RagProperties.class})
public class ClientConfig {

    @Bean
    public AnthropicClient anthropicClient(@Value("${ANTHROPIC_API_KEY}") String apiKey) {
        return AnthropicOkHttpClient.builder().apiKey(apiKey).build();
    }

    @Bean
    public RestClient voyageRestClient(VoyageProperties properties,
                                       @Value("${VOYAGE_API_KEY}") String apiKey) {
        return RestClient.builder()
                .baseUrl(properties.baseUrl())
                .defaultHeader("Authorization", "Bearer " + apiKey)
                .build();
    }
}
```

## 手順4：テキストを埋め込む（Voyage）

Voyage の `/v1/embeddings` に POST します。RAG では **保存する文書側は `input_type=document`、検索クエリ側は `input_type=query`** と使い分けると精度が上がります。返り値は入力順を保てるよう `index` で並べ直します。得られたベクトルの次元が `voyage.dimensions` と合うかも確認します。`VECTOR(N)` とのズレを早い段階で検出するためです。

まず、`input_type` の指定を取り違えないよう、小さな enum で表しておきます。

```
public enum InputType {
    QUERY("query"),
    DOCUMENT("document");

    private final String value;

    InputType(String value) {
        this.value = value;
    }

    public String value() {
        return value;
    }
}
```

埋め込みクライアント本体です。

```
@Component
@RequiredArgsConstructor
public class VoyageEmbeddingClient {

    private final RestClient voyageRestClient;
    private final VoyageProperties properties;

    public List<float[]> embed(List<String> inputs, InputType inputType) {
        var request = new EmbeddingRequest(inputs, properties.model(), inputType.value());

        var response = voyageRestClient.post()
                .uri("/embeddings")
                .body(request)
                .retrieve()
                .body(EmbeddingResponse.class);

        if (response == null || response.data() == null || response.data().isEmpty()) {
            throw new IllegalStateException("Voyage returned no embeddings");
        }
        return response.data().stream()
                .sorted(Comparator.comparingInt(EmbeddingResponse.Item::index))
                .map(item -> toVector(item.embedding()))
                .toList();
    }

    // List<Double> -> float[]。設定の次元数（= VECTOR(N)）と一致するかも確認する。
    private float[] toVector(List<Double> values) {
        if (values.size() != properties.dimensions()) {
            throw new IllegalStateException(
                    "埋め込み次元が不一致: " + values.size() + " != " + properties.dimensions()
                            + "（voyage.dimensions と VECTOR(N) を一致させてください）");
        }
        var array = new float[values.size()];
        for (int i = 0; i < values.size(); i++) {
            array[i] = values.get(i).floatValue();
        }
        return array;
    }

    record EmbeddingRequest(List<String> input, String model,
                            @JsonProperty("input_type") String inputType) {}

    record EmbeddingResponse(List<Item> data) {
        record Item(List<Double> embedding, int index) {}
    }
}
```

## 手順5：TiDB に保存し、ベクトル近傍検索で取り出す

ここが TiDB の肝です。やることは 2 つだけ。

* **保存**：`VECTOR` 列には `"[0.1,0.2,...]"` という**文字列リテラルを渡す**と TiDB 側でベクトルに暗黙変換されます。JDBC からはただの `setString`（＝ JdbcTemplate のパラメータ）で渡せます。
* **検索**：`ORDER BY VEC_COSINE_DISTANCE(embedding, ?) LIMIT ?` で、質問ベクトルに近い順で上位 k 件（設定では 4 件）を取り出します。

```
@Repository
@RequiredArgsConstructor
public class TidbVectorStore {

    private final JdbcTemplate jdbc;

    public void save(String docId, String chunkText, float[] embedding) {
        jdbc.update(
                "INSERT INTO rag_chunks (doc_id, chunk_text, embedding) VALUES (?, ?, ?)",
                docId, chunkText, toVectorLiteral(embedding));
    }

    public List<String> searchSimilar(float[] queryEmbedding, int topK) {
        return jdbc.query(
                """
                SELECT chunk_text
                FROM rag_chunks
                ORDER BY VEC_COSINE_DISTANCE(embedding, ?)
                LIMIT ?
                """,
                (rs, rowNum) -> rs.getString("chunk_text"),
                toVectorLiteral(queryEmbedding), topK);
    }

    // float[] -> TiDB が解釈できる "[1.0,2.0,3.0]"
    static String toVectorLiteral(float[] vector) {
        var sb = new StringBuilder(vector.length * 8 + 2);
        sb.append('[');
        for (int i = 0; i < vector.length; i++) {
            if (i > 0) sb.append(',');
            sb.append(vector[i]);
        }
        sb.append(']');
        return sb.toString();
    }
}
```

特別なドライバ拡張も、専用クライアントもありません。**MySQL を扱うのと同じ JdbcTemplate** で、ベクトルの保存と近傍検索が完結します。これが「ベクトル専用 DB を足さずに RAG を構築できる」ということです。

## 手順6：集めたコンテキストを添えて Claude に答えさせる

検索で集めたチャンクを「コンテキスト」として渡し、**その中だけを根拠に**答えるよう Claude へ指示します。コンテキスト外の質問には推測させない（ハルシネーション対策）のが RAG の作法です。

```
@Service
@RequiredArgsConstructor
@Slf4j
public class RagAssistant {

    private static final String SYSTEM = """
            あなたは社内ドキュメント QA アシスタントです。
            必ず「コンテキスト」内の情報だけを根拠に、日本語で簡潔に回答してください。
            コンテキストに答えが無い場合は、推測せず「ドキュメントには記載がありません」と答えてください。
            """;

    private final AnthropicClient client;
    private final AnthropicProperties properties;

    public String answer(String question, List<String> contexts) {
        var context = contexts.isEmpty() ? "(該当する情報なし)" : String.join("\n---\n", contexts);
        var userMessage = """
                コンテキスト:
                %s

                質問: %s""".formatted(context, question);

        var params = MessageCreateParams.builder()
                .model(properties.model())
                .maxTokens(properties.maxTokens())
                .system(SYSTEM)
                .addUserMessage(userMessage)
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

3 つの部品をつなぐオーケストレーションは、これだけです。

```
@Service
@RequiredArgsConstructor
public class RagService {

    private final VoyageEmbeddingClient embeddingClient;
    private final TidbVectorStore vectorStore;
    private final RagAssistant assistant;
    private final RagProperties properties;

    public int ingest(String docId, List<String> chunks) {
        var embeddings = embeddingClient.embed(chunks, InputType.DOCUMENT);
        for (int i = 0; i < chunks.size(); i++) {
            vectorStore.save(docId, chunks.get(i), embeddings.get(i));
        }
        return chunks.size();
    }

    public String ask(String question) {
        var queryEmbedding = embeddingClient.embed(List.of(question), InputType.QUERY).get(0);
        var contexts = vectorStore.searchSimilar(queryEmbedding, properties.topK());
        return assistant.answer(question, contexts);
    }
}
```

## 手順7：REST で公開する

最後に、`RagService` を呼ぶ薄いコントローラを用意します。リクエスト／レスポンスは `record` で受け、`spring-boot-starter-validation` の `@Valid` で最低限の入力チェックをかけます。

```
@RestController
@RequiredArgsConstructor
public class RagController {

    private final RagService ragService;

    @PostMapping("/ingest")
    public IngestResponse ingest(@RequestBody @Valid IngestRequest request) {
        var stored = ragService.ingest(request.docId(), request.chunks());
        return new IngestResponse(stored);
    }

    @PostMapping("/ask")
    public AskResponse ask(@RequestBody @Valid AskRequest request) {
        return new AskResponse(ragService.ask(request.question()));
    }

    public record IngestRequest(
            @NotBlank String docId,
            @NotEmpty List<@NotBlank String> chunks) {}

    public record IngestResponse(int stored) {}

    public record AskRequest(@NotBlank String question) {}

    public record AskResponse(String answer) {}
}
```

これで `POST /ingest`（`{docId, chunks}` → `{stored}`）と `POST /ask`（`{question}` → `{answer}`）が公開されます。

## 動かす

プロジェクト直下に `.env` を作ります（コミットしない）。準備で控えた `ANTHROPIC_API_KEY`・`VOYAGE_API_KEY` と TiDB の接続情報（`TIDB_JDBC_URL`・`TIDB_USER`・`TIDB_PASSWORD`）を書きます。あとは `./gradlew bootRun` で起動し、手順7 の `/ingest`・`/ask` に curl を投げるだけです。

```
# 1) ドキュメントを取り込む（チャンクごとに埋め込み → TiDB へ保存）
curl -s localhost:8080/ingest -H 'Content-Type: application/json' -d '{
  "docId": "handbook",
  "chunks": [
    "当社のコアタイムは 11 時から 15 時です。",
    "経費精算は毎月末締め、翌月 10 日払いです。",
    "有給休暇は入社初日から 10 日付与されます。"
  ]
}'

# 2) 質問する（質問を埋め込み → TiDB で近傍検索 → Claude が回答）
curl -s localhost:8080/ask -H 'Content-Type: application/json' -d '{
  "question": "コアタイムは何時から何時まで？"
}'
# => {"answer":"コアタイムは 11 時から 15 時までです。"}
```

## 動作確認

このコードは、TiDB Cloud Starter（無料枠）に Voyage と Claude をつなぎ、`/ingest` → `/ask` を実際に動かして確認しました。質問の埋め込み → ベクトル近傍検索 → 回答生成まで通り、別チャンクを問う質問では別の根拠が取り出せました。コンテキスト外の質問には「ドキュメントには記載がありません」と返り、推測しないことも確認できました。

TiDB Cloud の SQL エディタからも裏が取れます。`rag_chunks` には 1024 次元のベクトルが 3 行入っています。

![TiDB に保存された rag_chunks の行](https://static.zenn.studio/user-upload/deployed-images/de23e543f851f1c31b51c2bb.png?sha=cd97672d74512a9b62974bba80c48b7d2d681fbc)

あるチャンクの埋め込みを基準に距離を並べると、近傍検索が機能していることが見えます。下は「コアタイム」のチャンクを基準にした例で、自分自身が距離 0、内容が離れるほど距離が大きくなります。

![VEC_COSINE_DISTANCE による近傍検索の並び](https://static.zenn.studio/user-upload/deployed-images/a2305ea1a501ab21984c2aae.png?sha=9979eced56dfe329483b86eb887ff08048408bb2)

> **Voyage の無料枠に注意（執筆時点）**：支払い方法を登録するまではレート制限が厳しく、取り込みと質問を続けて投げると、レート制限を超えて **HTTP 429（Too Many Requests）** が返ることがあります。支払い方法を登録すると Tier 1（2000 RPM / 8M TPM）に上がり、無料トークン枠（`voyage-4` で 2 億トークン）はそのまま使えます。最新の制限・料金は [Voyage の料金](https://docs.voyageai.com/docs/pricing)・[レート制限](https://docs.voyageai.com/docs/rate-limits)ページで確認してください。

## 実運用での効きどころ（応用例）

ここまでは社内ドキュメント QA の最小形でした。TiDB が本領を発揮するのは、**構造化データでの絞り込みとベクトル検索を同じ SQL で組み合わせたい**場面です。リレーショナルなデータとベクトルが同じ DB に同居しています。だから `WHERE` で対象を絞ってから `ORDER BY VEC_COSINE_DISTANCE(...) LIMIT k` で近傍検索する、を 1 クエリで書けます。身近なところでは、次のような応用に展開できます（いずれもこの最小構成の延長線上にある発展例で、実装・検証はこれからの領域です）。

* **相手によって見せる文書を変える社内 QA**：正社員と契約社員、部署で参照すべき規程が違う場面です。`WHERE scope = '全社' OR department = ?` で対象者向けに絞ってから近傍検索すれば、出し分けを別の仕組みにせず同じ SQL で完結できます。
* **障害・インシデントの再発調査（SRE）**：「このアラート、前にも対応した気がする」を過去の障害対応から探す場面です。対応記録には `service`・発生日時・状態・対応内容がもともと 1 テーブルに並んでいます。`WHERE service = ? AND status = '復旧済み'` で復旧済みの記録に絞ってから、事象の説明に意味が近いものを引けば、似た過去対応とその直し方をまとめて参照できます。
* **自社サービスの意味検索・レコメンド**（EC・メディアなど）：「軽くて暖かい上着」のような曖昧な言葉での検索や、似た商品のレコメンドをしたい場面です。商品や記事の構造化列と埋め込みが同居するので、`WHERE in_stock AND price < ?` のような業務条件と意味の近さを 1 クエリで両立できます。

いずれも専用ベクトル DB を足さずに、いつもの JdbcTemplate のまま書けます。これが「リレーショナルなデータと同じ場所でベクトルを扱える」ことの実利です。

> **`WHERE` 併用時の注意（執筆時点）**：上の例のように `WHERE` で先に絞り込むクエリ（プレフィルタ）は、TiDB の仕様上ベクトルインデックスを使えず全件スキャンになります。結果は正しく返りますが、件数が増えると遅くなります。その場合は「先に近傍検索し、あとで絞り込む」ポストフィルタ（候補を多めに取ってから `WHERE` で絞る）が公式に案内されています。詳しくは公式ドキュメント [ベクトル検索の性能改善](https://docs.pingcap.com/tidb/stable/vector-search-improve-performance/) を参照してください。

## まとめと次の一歩

ここまでの要点を振り返り、実運用に向けた次の一歩を挙げます。

* RAG の最小構成は「**埋め込み（Voyage）→ ベクトル検索（TiDB）→ 生成（Claude）**」の 3 部品。
* **TiDB は MySQL 互換**なので、ベクトル検索も**いつもの JdbcTemplate**で書ける。専用ベクトル DB を増やさず、リレーショナルなデータと同じ場所で扱えるのが「AI 時代のデータ基盤」としての強み。
* 肝は **`VECTOR(N)` 列**と **`ORDER BY VEC_COSINE_DISTANCE(...) LIMIT k`**、そして **`VECTOR(N)` の N と埋め込み次元を一致させる**こと。

次の一歩：

* **HNSW インデックス**でデータ量が増えても近傍検索を速く保つ。
* **メタデータ絞り込みの拡張**：応用例で触れた `WHERE` 併用を、`doc_id` 以外の属性（部署・テナント・タグなど）へ広げる。
* **全文検索とのハイブリッド**：キーワード一致とベクトル類似を組み合わせて取りこぼしを減らす。
* **出典の提示**：`doc_id` も一緒に返し、回答の根拠をユーザーに示す。

> Spring Boot × Claude の実装は、別記事「[Spring Boot から公式 Java SDK で Claude API を呼ぶ最小実装](https://zenn.dev/propagandist/articles/0001-spring-boot-claude-api-java-sdk)」でも扱っています。
