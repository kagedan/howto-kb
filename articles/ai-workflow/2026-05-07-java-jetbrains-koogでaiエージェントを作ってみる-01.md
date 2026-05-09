---
id: "2026-05-07-java-jetbrains-koogでaiエージェントを作ってみる-01"
title: "Java + JetBrains KoogでAIエージェントを作ってみる"
url: "https://zenn.dev/sen_shimizu/articles/6a7c9d62d0de5b"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "OpenAI", "GPT"]
date_published: "2026-05-07"
date_collected: "2026-05-09"
summary_by: "auto-rss"
query: ""
---

<https://github.com/sen-shimizu/koog-java-sample>

# はじめに

この記事では、JavaからJetBrains Koogを使って、簡単なAIエージェントを作る流れを整理します。

Koogは、LLM（大規模言語モデル）を使ったAIエージェントを構築するためのJVM向けフレームワークです。KotlinだけでなくJavaからも利用できるようになっており、JavaエンジニアでもAIエージェント開発を試しやすい点が特徴です。

今回は、まず最小構成のサンプルでKoogの基本を確認し、そのあとに「天気取得」「翻訳」「計算」の3つのツールを持つマルチツール型AIエージェントを作る構成で進めます。

# 作るもの

最終的には、コンソール上で次のように会話できるAIエージェントを作る想定です。

```
マルチツールAIエージェントへようこそ！（終了するには 'exit' と入力）
あなた: 東京の天気は？
エージェント: 東京の現在の気温は18.3℃、天気は曇りです。

あなた: それを英語にして
エージェント: The current temperature in Tokyo is 18.3°C and the weather is cloudy.

あなた: 25*12は？
エージェント: 25*12 = 300.0
```

ここで大事なのは、AIエージェントが単に文章を返すだけではなく、必要に応じてJava側で定義したツールを呼び出す点です。

たとえば、

* 天気を聞かれたら天気APIを呼び出す
* 翻訳を頼まれたら翻訳APIを呼び出す
* 計算を頼まれたら計算ツールを呼び出す

というように、ユーザーの入力内容に応じて処理を切り替えます。

# ファイル構成

今回はMavenプロジェクトとして、次のような構成にします。

```
koog-java-sample/
├── pom.xml
├── README.md
├── mvn.cmd
├── .gitignore
└── src/
    └── main/
        └── java/
            └── com/
                └── example/
                    └── koog/
                        ├── KoogJavaExample.java
                        └── MultiToolAgent.java
```

`KoogJavaExample.java` は基本動作確認用、`MultiToolAgent.java` は複数ツールを扱う本命のサンプルとして使います。

# Maven依存関係

`pom.xml` には、Koog本体のほか、JSON処理用のJackson、HTTP通信を行うApache HttpClient、計算式を処理するためのライブラリを追加します。

```
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>koog-java-sample</artifactId>
    <version>1.0.0</version>

    <properties>
        <maven.compiler.source>25</maven.compiler.source>
        <maven.compiler.target>25</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <!-- Koog Java API -->
        <dependency>
            <groupId>ai.koog</groupId>
            <artifactId>koog-agents-jvm</artifactId>
            <version>0.7.3</version>
        </dependency>

        <!-- JSON処理用 -->
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>2.17.0</version>
        </dependency>

        <!-- HTTPクライアント -->
        <dependency>
            <groupId>org.apache.httpcomponents.client5</groupId>
            <artifactId>httpclient5</artifactId>
            <version>5.3</version>
        </dependency>

        <!-- 計算式処理用 -->
        <dependency>
            <groupId>org.mariuszgromada.math</groupId>
            <artifactId>MathParser.org-mXparser</artifactId>
            <version>6.1.0</version>
        </dependency>
    </dependencies>
</project>
```

KoogのAPIやMaven座標は変更される可能性があります。実際に動かす場合は、公式ドキュメントやMaven Centralで最新版を確認してください。

# 最小構成のKoogサンプル

まずは、Koogの基本的な流れを確認します。

```
package com.example.koog;

import ai.koog.agents.core.agent.AIAgent;
import ai.koog.agents.core.agent.AIAgentBuilder;
import ai.koog.prompt.executor.llms.all.SimplePromptExecutorsKt;

public class KoogJavaExample {
    public static void main(String[] args) {
        // APIキーを環境変数から取得（例: OPENAI_API_KEY）
        String apiKey = System.getenv("OPENAI_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            System.out.println("OPENAI_API_KEY環境変数を設定してください。");
            return;
        }

        AIAgent<String, String> agent = new AIAgentBuilder()
                .promptExecutor(SimplePromptExecutorsKt.simpleOpenAIExecutor(apiKey))
                .systemPrompt("You are a helpful assistant. Answer user questions concisely.")
                .build();

        String response = agent.run("Hello Koog from Java!");
        System.out.println("Agent response: " + response);
    }
}
```

このコードでは、`AIAgentBuilder` を使ってAIエージェントを作成し、`SimplePromptExecutorsKt.simpleOpenAIExecutor` でOpenAIのプロンプト実行者を設定しています。

ポイントは次の3つです。

* `AIAgentBuilder` でエージェントを構築する
* `SimplePromptExecutorsKt.simpleOpenAIExecutor` でプロンプト実行者を設定する
* `AIAgent<String, String>` の `run()` メソッドで入力を処理する

最小サンプルなので、まだ外部APIには接続していません。まずは「Koogのエージェントに入力を渡し、応答する」という全体像を掴むためのコードです。

# マルチツールAIエージェントを作る

次に、天気・翻訳・計算の3つのツールを持つエージェントを作ります。

`MultiToolAgent.java` の全体像は次のようになります。

```
package com.example.koog;

import ai.koog.agents.core.agent.AIAgent;
import ai.koog.agents.core.agent.AIAgentBuilder;
import ai.koog.agents.core.tools.ToolRegistry;
import ai.koog.prompt.executor.llms.all.SimplePromptExecutorsKt;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import kotlin.Unit;
import kotlin.coroutines.Continuation;
import kotlin.coroutines.CoroutineContext;
import kotlin.coroutines.EmptyCoroutineContext;
import org.apache.hc.client5.http.classic.methods.HttpGet;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.core5.http.io.entity.EntityUtils;

import java.lang.reflect.Method;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Scanner;

public class MultiToolAgent {

    private static final String OPENAI_API_KEY = System.getenv("OPENAI_API_KEY");
    private static final String WEATHER_API_KEY = System.getenv("OPENWEATHERMAP_API_KEY");
    private static final String WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather";

    public static void main(String[] args) throws Exception {
        if (OPENAI_API_KEY == null || OPENAI_API_KEY.isBlank()) {
            System.err.println("OPENAI_API_KEY が設定されていません。環境変数を設定してください。");
            return;
        }

        if (WEATHER_API_KEY == null || WEATHER_API_KEY.isBlank()) {
            System.err.println("OPENWEATHERMAP_API_KEY が設定されていません。環境変数を設定してください。");
            return;
        }

        ToolRegistry toolRegistry = ToolRegistry.builder()
                .tool(getStaticMethod("getWeather", String.class), null, "getWeather", "指定された都市の天気を取得します")
                .tool(getStaticMethod("translate", String.class), null, "translate", "テキストを指定言語に翻訳します。入力例: Hello, ja")
                .tool(getStaticMethod("calculate", String.class), null, "calculate", "数式を計算します。入力例: 25*12")
                .build();

        AIAgent<String, String> agent = new AIAgentBuilder()
                .promptExecutor(SimplePromptExecutorsKt.simpleOpenAIExecutor(OPENAI_API_KEY))
                .toolRegistry(toolRegistry)
                .systemPrompt("あなたは必要に応じて天気・翻訳・計算のツールを呼び出して応答するマルチツールAIエージェントです。")
                .build();

        try {
            try (Scanner scanner = new Scanner(System.in)) {
                System.out.println("マルチツールAIエージェントへようこそ！（終了するには 'exit' と入力）");

                while (true) {
                    System.out.print("あなた: ");
                    String userInput = scanner.nextLine();

                    if ("exit".equalsIgnoreCase(userInput.trim())) {
                        break;
                    }

                    String response = agent.run(userInput);
                    System.out.println("エージェント: " + response);
                }
            }
        } finally {
            Continuation<Unit> closeContinuation = new Continuation<Unit>() {
                @Override
                public CoroutineContext getContext() {
                    return EmptyCoroutineContext.INSTANCE;
                }

                @Override
                public void resumeWith(Object result) {
                    // close の完了を待たず、例外も無視します
                }
            };
            agent.close(closeContinuation);
        }
    }

    private static Method getStaticMethod(String name, Class<?>... parameterTypes) throws NoSuchMethodException {
        return MultiToolAgent.class.getMethod(name, parameterTypes);
    }

    public static String getWeather(String city) {
        try (CloseableHttpClient client = HttpClients.createDefault()) {
            String url = WEATHER_BASE_URL
                    + "?q=" + URLEncoder.encode(city, StandardCharsets.UTF_8)
                    + "&appid=" + WEATHER_API_KEY
                    + "&units=metric&lang=ja";

            HttpGet request = new HttpGet(url);
            String json = client.execute(request, response -> EntityUtils.toString(response.getEntity()));

            ObjectMapper mapper = new ObjectMapper();
            JsonNode root = mapper.readTree(json);

            if (root.has("main") && root.has("weather")) {
                double temp = root.get("main").get("temp").asDouble();
                String desc = root.get("weather").get(0).get("description").asText();
                return String.format("%sの現在の気温は%.1f℃、天気は%sです。", city, temp, desc);
            } else {
                return "天気情報を取得できませんでした。";
            }
        } catch (Exception e) {
            return "エラー: " + e.getMessage();
        }
    }

    public static String translate(String input) {
        String[] parts = input.split(",", 2);
        if (parts.length < 2) {
            return "入力形式: <テキスト>,<言語コード>";
        }

        try (CloseableHttpClient client = HttpClients.createDefault()) {
            String encodedText = URLEncoder.encode(parts[0].trim(), StandardCharsets.UTF_8);
            String url = "https://api.mymemory.translated.net/get?q="
                    + encodedText
                    + "&langpair=auto|"
                    + parts[1].trim();

            HttpGet request = new HttpGet(url);
            String json = client.execute(request, response -> EntityUtils.toString(response.getEntity()));

            ObjectMapper mapper = new ObjectMapper();
            JsonNode root = mapper.readTree(json);

            JsonNode translatedText = root.path("responseData").path("translatedText");
            if (translatedText.isTextual()) {
                return translatedText.asText();
            }
            return "翻訳失敗";
        } catch (Exception e) {
            return "翻訳エラー: " + e.getMessage();
        }
    }

    public static String calculate(String expression) {
        try {
            double result = new org.mariuszgromada.math.mxparser.Expression(expression).calculate();

            if (Double.isNaN(result)) {
                return "計算できませんでした。";
            }

            return expression + " = " + result;
        } catch (Exception e) {
            return "計算エラー: " + e.getMessage();
        }
    }
}
```

# 各ツールの役割

## 天気ツール

```
.tool(getStaticMethod("getWeather", String.class), null, "getWeather", "指定された都市の天気を取得します")
```

このツールは、都市名を受け取り、OpenWeatherMap APIから現在の天気を取得します。

`getWeather()` メソッドでは、HTTPリクエストを送り、返ってきたJSONから気温と天気説明を取り出しています。

```
double temp = root.get("main").get("temp").asDouble();
String desc = root.get("weather").get(0).get("description").asText();
```

JSONの処理にはJacksonを使っています。

## 翻訳ツール

```
.tool(getStaticMethod("translate", String.class), null, "translate", "テキストを指定言語に翻訳します。入力例: Hello, ja")
```

翻訳ツールでは、入力文字列をカンマで分割しています。

たとえば、

という入力であれば、`Hello` を `ja`、つまり日本語に翻訳する想定です。

実際の翻訳処理では、MyMemory Translated APIを呼び出しています。

```
String url = "https://api.mymemory.translated.net/get?q="
        + encodedText
        + "&langpair=auto|"
        + targetLang;
```

## 計算ツール

```
.tool(getStaticMethod("calculate", String.class), null, "calculate", "数式を計算します。入力例: 25*12")
```

計算ツールでは、文字列として受け取った数式を計算します。

```
double result = new org.mariuszgromada.math.mxparser.Expression(expression).calculate();
```

これにより、たとえば次のような入力を処理できます。

結果は、次のようになります。

# AIAgentBuilderでツールを登録する

作成したツールは、`ToolRegistry.builder()` でレジストリを作成し、`AIAgentBuilder` に登録します。

```
ToolRegistry toolRegistry = ToolRegistry.builder()
        .tool(getStaticMethod("getWeather", String.class), null, "getWeather", "指定された都市の天気を取得します")
        .tool(getStaticMethod("translate", String.class), null, "translate", "テキストを指定言語に翻訳します。入力例: Hello, ja")
        .tool(getStaticMethod("calculate", String.class), null, "calculate", "数式を計算します。入力例: 25*12")
        .build();

AIAgent<String, String> agent = new AIAgentBuilder()
        .promptExecutor(SimplePromptExecutorsKt.simpleOpenAIExecutor(OPENAI_API_KEY))
        .toolRegistry(toolRegistry)
        .systemPrompt("あなたは必要に応じて天気・翻訳・計算のツールを呼び出して応答するマルチツールAIエージェントです。")
        .build();
```

ここでは、3つのツールを登録しています。

* `getWeather`
* `translate`
* `calculate`

この部分が、今回のサンプルの中心です。

# 会話ループを作る

最後に、コンソールから入力を受け取り、エージェントに渡すループを作ります。

```
while (true) {
    System.out.print("あなた: ");
    String userInput = scanner.nextLine();

    if ("exit".equalsIgnoreCase(userInput.trim())) {
        break;
    }

    String response = agent.run(userInput);
    System.out.println("エージェント: " + response);
}
```

`agent.run(userInput)` によって、ユーザーの入力をエージェントに渡しています。

エージェント側では、入力内容に応じて必要なツールを判断し、結果を返す想定です。

# 実行方法

プロジェクト直下で、まずコンパイルします。

または、MavenがPATHにない場合は：

基本サンプルを実行する場合は、次のようにします。

```
mvn exec:java -Dexec.mainClass="com.example.koog.KoogJavaExample"
```

マルチツール版を実行する場合は、次のようにします。

```
mvn exec:java -Dexec.mainClass="com.example.koog.MultiToolAgent"
```

OpenAI APIとOpenWeatherMap APIを使う場合は、環境変数を設定してください。

```
export OPENAI_API_KEY="your-openai-api-key"
export OPENWEATHERMAP_API_KEY="your-openweathermap-api-key"
```

Windows PowerShellなら、次のように設定できます。

```
$env:OPENAI_API_KEY="your-openai-api-key"
$env:OPENWEATHERMAP_API_KEY="your-openweathermap-api-key"
```

# 注意点

## APIキーをコードに直書きしない

サンプルでは説明を簡単にするために、APIキーを環境変数から読み込んでいます。

```
private static final String OPENAI_API_KEY = System.getenv("OPENAI_API_KEY");
private static final String WEATHER_API_KEY = System.getenv("OPENWEATHERMAP_API_KEY");
```

GitHubなどに公開する場合、APIキーをコードに直接書くのは危険です。環境変数や設定ファイルから読み込むようにしましょう。

## 外部APIのエラー処理を入れる

天気APIや翻訳APIは、ネットワークエラー、API制限、入力ミスなどで失敗する可能性があります。

そのため、`try-catch` で例外を捕捉し、ユーザーに分かりやすいメッセージを返すようにしています。

```
} catch (Exception e) {
    return "エラー: " + e.getMessage();
}
```

本番用途であれば、ログ出力やリトライ処理も検討した方がよいです。

## 計算式の扱いには注意する

計算ツールでは、ユーザーが入力した文字列を数式として評価しています。

```
new org.mariuszgromada.math.mxparser.Expression(expression).calculate();
```

今回のような学習用サンプルであれば問題ありませんが、実際のサービスで使う場合は、入力値の検証や利用可能な式の制限を検討する必要があります。

# まとめ

この記事では、Java + JetBrains Koogを使って、簡単なAIエージェントを作る構成を整理しました。

最初に `KoogJavaExample.java` で基本的なエージェントの作り方を確認し、その後 `MultiToolAgent.java` で天気・翻訳・計算の3つのツールを持つエージェントに拡張しました。

今回のポイントは、LLMに文章を返させるだけではなく、必要に応じてJava側の処理や外部APIを呼び出せるようにすることです。

JavaからAIエージェントを扱えるようになると、既存のJavaアプリケーションにAI機能を組み込む選択肢が広がります。

まだKoogのAPIや周辺情報は変わる可能性があるため、実際に試す場合は公式ドキュメントを確認しながら進めるのがよさそうです。

# おまけ: 次に試したいこと

「今回のサンプルを発展させるならどうすればいいか」をChatGPTに尋ねたところ、次のような機能を提案されました。

* データベース検索ツールを追加する
* ファイル読み込みツールを追加する
* Web検索ツールを追加する
* Spring Bootアプリに組み込む
* 会話履歴をDBに保存する

特にJavaエンジニアであれば、Spring Bootと組み合わせて「業務データを参照できるAIエージェント」を作る方向に進めると、より実用的なサンプルになりそうです。
