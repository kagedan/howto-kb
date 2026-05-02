---
id: "2026-05-01-google-adk-javago-10入門-エンタープライズaiエージェント開発の全貌-01"
title: "Google ADK Java/Go 1.0入門 — エンタープライズAIエージェント開発の全貌"
url: "https://zenn.dev/kai_kou/articles/203-google-adk-java-go-10-enterprise-agent-guide"
source: "zenn"
category: "claude-code"
tags: ["API", "AI-agent", "LLM", "Gemini", "Python", "TypeScript"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年3月30日・31日、GoogleはAgent Development Kit (ADK) のJava版 1.0.0 とGo版 1.0 を相次いでリリースしました。既存のPython版・TypeScript版に続き、ADKはエンタープライズで広く使われるJavaとGoをサポートする **4言語対応の本格的なAIエージェント開発フレームワーク** となりました。

この記事では、両リリースの主要機能を公式ドキュメントとソースコードをもとに解説します。

### この記事で学べること

* ADK Java 1.0.0 のセットアップとクイックスタート
* Plugin System・Event Compaction・Human-in-the-Loop（HITL）の実装方法
* ADK Go 1.0 の OpenTelemetry 統合と YAML 設定
* A2A Protocol（Agent2Agent）を使ったマルチ言語エージェント間通信

### 対象読者

* Javaまたはサーバーサイド Go でAIエージェントを構築したい開発者
* エンタープライズ向けエージェントのセキュリティ・可観測性を強化したい方
* ADK Python/TypeScript版の利用経験があり、他言語への展開を検討している方

### 前提環境（Java）

* Java 17 以上
* Maven 3.9 以上
* Google Gemini API キー

### 前提環境（Go）

* Go 1.22 以上
* Google Gemini API キー

---

## TL;DR

* **ADK Java 1.0.0（3/30）**: Maven依存1行で導入可、Plugin/EventCompaction/HITL/A2Aをネイティブサポート
* **ADK Go 1.0（3/31）**: OpenTelemetry ネイティブ統合で本番デバッグが容易、YAMLでエージェント設定可能
* 両言語ともA2A Protocolで他言語エージェントと相互通信可能
* 人間承認フロー（HITL）がGoogle Safe AI Framework準拠で標準搭載

---

## ADK とは

ADK (Agent Development Kit) は、Googleが提供するオープンソースのAIエージェント開発フレームワークです。ビルド・デバッグ・デプロイを一貫して行えるよう設計されており、特に **エンタープライズ規模でのAIエージェント運用** を念頭に置いています。

### ADK の言語対応状況

| 言語 | バージョン | リリース日 | 主な用途 |
| --- | --- | --- | --- |
| Python | 1.x | 2025年〜 | データサイエンス・ML連携 |
| TypeScript | 1.x | 2026年初頭 | Webフロントエンド・Node.js |
| **Java** | **1.0.0** | **2026-03-30** | **エンタープライズバックエンド** |
| **Go** | **1.0** | **2026-03-31** | **マイクロサービス・クラウドネイティブ** |

全言語でA2A Protocolを介した相互通信がサポートされており、既存システムへの段階的な導入が可能です。

---

## ADK Java 1.0.0 入門

### セットアップ

`pom.xml` に以下の依存を追加します:

```
<dependency>
    <groupId>com.google.adk</groupId>
    <artifactId>google-adk</artifactId>
    <version>1.0.0</version>
</dependency>

<!-- 開発用Web UI（任意） -->
<dependency>
    <groupId>com.google.adk</groupId>
    <artifactId>google-adk-dev</artifactId>
    <version>1.0.0</version>
</dependency>
```

### クイックスタート

最小構成のエージェントを作成します:

```
package com.example.agent;

import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.FunctionTool;
import java.util.Map;

public class HelloTimeAgent {
    public static LlmAgent ROOT_AGENT = initAgent();

    private static LlmAgent initAgent() {
        return LlmAgent.builder()
            .name("hello-time-agent")
            .description("指定した都市の現在時刻を返すエージェント")
            .instruction("You are a helpful assistant that tells the current time.")
            .model("gemini-flash-latest")
            .tools(FunctionTool.create(HelloTimeAgent.class, "getCurrentTime"))
            .build();
    }

    public static Map<String, String> getCurrentTime(String city) {
        // 実際のアプリではタイムゾーンAPIを呼び出す
        return Map.of("city", city, "time", "10:30am");
    }
}
```

CLI実行:

```
mvn compile exec:java -Dexec.mainClass="com.example.agent.AgentCliRunner"
```

開発用Web UI起動:

```
mvn compile exec:java -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
    -Dexec.args="--adk.agents.source-dir=target --server.port=8000"
# → http://localhost:8000 でUIにアクセス可
```

### Plugin System

ADK Java 1.0 では `App` クラスを通じて **アプリケーション横断的な関心事（ロギング・コンテキスト制御・グローバル指示）** をPluginとして注入できます。

```
import com.google.adk.app.App;
import com.google.adk.plugins.*;
import java.util.List;

List<Plugin> plugins = List.of(
    new LoggingPlugin(),                                    // 構造化ログ
    new ContextFilterPlugin(),                             // トークン上限管理
    new GlobalInstructionPlugin("ALWAYS RESPOND IN JAPANESE") // 全エージェントへの共通指示
);

App myApp = App.builder()
    .name("customer-support-app")
    .rootAgent(supportAssistant)
    .plugins(plugins)
    .build();
```

`GlobalInstructionPlugin` はサブエージェントを含む全エージェントに一括で指示を適用できるため、言語切替・ポリシー適用などに有用です。

### Event Compaction — コンテキストウィンドウの自動管理

長時間のエージェントセッションではコンテキストウィンドウが溢れる問題があります。ADK Java 1.0 の **Event Compaction** は会話履歴を自動要約・圧縮してトークンコストを抑えます:

```
App myApp = App.builder()
    .name("long-running-agent")
    .rootAgent(assistant)
    .plugins(plugins)
    .eventsCompactionConfig(
        EventsCompactionConfig.builder()
            .compactionInterval(5)          // 5ターンごとに圧縮検討
            .overlapSize(2)                 // 圧縮後も直近2イベントを保持
            .tokenThreshold(4000)           // 4000トークン超で圧縮発動
            .eventRetentionSize(1000)       // 最大1000イベントを保持
            .summarizer(new LlmEventSummarizer(llm)) // LLMで要約
            .build())
    .build();
```

この機能により、カスタマーサポートや長時間の分析エージェントなどで**セッションを中断せずに長期運用**が可能になります。

### Human-in-the-Loop（HITL）

金融取引・データ変更などの高リスク操作では、エージェントを一時停止して人間の承認を求める必要があります。ADK Java 1.0 では `ToolConfirmation` で実装します:

```
import com.google.adk.tools.ToolContext;
import com.google.adk.tools.ToolConfirmation;
import com.google.adk.tools.annotations.Schema;

@Schema(name = "request_confirmation")
public String requestConfirmation(
    @Schema(name = "request_action", description = "承認を求めるアクションの説明")
    String actionRequest,
    @Schema(name = "toolContext")
    ToolContext toolContext) {

    boolean isConfirmed = toolContext.toolConfirmation()
        .map(ToolConfirmation::confirmed)
        .orElse(false);

    if (!isConfirmed) {
        // 人間への確認要求 → エージェントが一時停止
        toolContext.requestConfirmation(
            "以下のアクションを実行しますか？: " + actionRequest, null);
        return "確認待ちです。";
    }

    return "承認済み: " + actionRequest;
}
```

承認ツールをエージェントに組み込む:

```
LlmAgent assistant = LlmAgent.builder()
    .name("report-assistant")
    .instruction("""
        あなたは安全なレポートアシスタントです。
        アクションを実行する前に必ず request_confirmation ツールで確認を取得してください。
        """)
    .model("gemini-2.5-flash")
    .tools(
        FunctionTool.create(this, "requestConfirmation", true)
    )
    .build();
```

### A2A Protocol — マルチフレームワーク連携

ADK Java 1.0 は [Agent2Agent (A2A) Protocol](https://google.github.io/adk-docs/agents/multi-agents/) をネイティブサポートします。他フレームワーク（Python ADK、LangChain等）で構築されたエージェントと相互通信が可能です:

```
// リモートエージェントへの接続（AgentCard解決 → A2Aクライアント生成）
RemoteA2AAgent remoteAgent = RemoteA2AAgent.builder()
    .agentCardUrl("https://remote-agent.example.com/.well-known/agent.json")
    .build();

// ADKエージェントをA2Aエンドポイントとして公開
AgentExecutor executor = new AgentExecutor(myAgent);
// JSON-RPC RESTエンドポイントが自動生成される
```

---

## ADK Go 1.0 入門

ADK Go 1.0 は **クラウドネイティブ・マイクロサービス環境** を念頭に設計されています。Java版と同等の機能に加え、Goエコシステムならではの可観測性とパフォーマンスが特徴です。

### OpenTelemetry ネイティブ統合

ADK Go 1.0 の最大の特徴は **OpenTelemetry (OTel) のネイティブサポート** です。エージェントロジックのデバッグにかかるコストを大幅に削減します:

```
import (
    "github.com/google/adk-go/runner"
    "github.com/google/adk-go/telemetry"
)

// OTel初期化（Cloud Traceに送信する設定）
telemetryProviders, err := telemetry.New(ctx, telemetry.WithOtelToCloud(true))
if err != nil {
    log.Fatal(err)
}
defer telemetryProviders.Shutdown(ctx)

// グローバルOTelプロバイダーに登録
telemetryProviders.SetGlobalOtelProviders()
tp := telemetryProviders.TracerProvider()

// ランナーにテレメトリを設定
r, err := runner.New(runner.Config{
    Agent:     myAgent,
    Telemetry: telemetry.NewOTel(tp),
})
```

これにより、モデル呼び出し・ツール実行のすべてに **構造化トレース** が自動付与され、Google Cloud Trace などで可視化できます。

### Plugin System — Retry & Reflect

Go 1.0 では **Retry & Reflect プラグイン** が標準搭載されています。ツールがエラーを返すとモデルにフィードバックし、エージェントが自己修正を試みます:

```
import (
    "github.com/google/adk-go/runner"
    "github.com/google/adk-go/plugin"
    "github.com/google/adk-go/plugin/retryandreflect"
    "github.com/google/adk-go/plugin/loggingplugin"
)

r, err := runner.New(runner.Config{
    Agent:          myAgent,
    SessionService: mySessionService,
    PluginConfig: runner.PluginConfig{
        Plugins: []*plugin.Plugin{
            // エラー時に最大3回自己修正を試みる
            retryandreflect.MustNew(retryandreflect.WithMaxRetries(3)),
            // 構造化ロギング
            loggingplugin.MustNew(""),
        },
    },
})
```

### YAML 設定 — 再コンパイル不要のエージェント管理

Go 1.0 では **YAMLでエージェントを定義**できます。ペルソナやサブエージェント構成の変更にGoコードの再コンパイルが不要になります:

```
# agent_config.yaml
name: customer_service
description: 航空会社の顧客対応エージェント
instruction: >
  あなたは航空会社の顧客サービス担当です。
  フライトの予約・変更・キャンセルを丁寧にサポートしてください。
tools:
  - name: "google_search"
  - name: "builtin_code_executor"
sub_agents:
  - "policy_agent"      # ポリシー確認用サブエージェント
  - "booking_agent"     # 予約処理用サブエージェント
```

`adk` CLIでYAML設定を直接実行できます:

```
adk run --config=agent_config.yaml
```

### Human-in-the-Loop（Go版）

Google Safe AI Framework (SAIF) に準拠した人間承認フロー:

```
import "github.com/google/adk-go/tools/functiontool"

// 本番データベース削除など高リスク操作に承認フローを設定
myTool, err := functiontool.New(functiontool.Config{
    Name:                "delete_database",
    Description:         "本番データベースインスタンスを削除します。",
    RequireConfirmation: true, // HITLフローのトリガー
}, deleteDBFunc)
```

`RequireConfirmation: true` を設定すると、ツール実行前にエージェントが自動的に一時停止し、人間の承認を待ちます。承認後、エージェントは自動的に処理を再開します。

---

## Java vs Go vs Python vs TypeScript 比較

ADK の4言語対応により、ユースケースに応じた選択が可能です:

| 観点 | Java | Go | Python | TypeScript |
| --- | --- | --- | --- | --- |
| **向いている用途** | エンタープライズバックエンド | マイクロサービス・高並行処理 | ML/データサイエンス | Web・Node.js |
| **可観測性** | ログプラグイン | OTelネイティブ | ベーシック | ベーシック |
| **設定管理** | コード主体 | YAML対応 | コード主体 | コード主体 |
| **HITL** | ToolConfirmation | RequireConfirmation | 対応 | 対応 |
| **A2A** | ネイティブ | ネイティブ（改善版） | ネイティブ | ネイティブ |
| **コンテキスト管理** | Event Compaction | プラグイン | 基本 | 基本 |

### 選択指針

* **既存のJavaバックエンドにAI機能を追加** → ADK Java
* **Kubernetesネイティブなマイクロサービス** → ADK Go
* **ML実験・プロトタイプ** → ADK Python
* **Next.jsやNode.jsのフロントエンド連携** → ADK TypeScript

---

## 注意点

### Java版

### Go版

---

## まとめ

* **ADK Java 1.0.0 (3/30)** と **ADK Go 1.0 (3/31)** により、ADKは4言語対応のエンタープライズAIエージェントフレームワークとなった
* Java版は Plugin System・Event Compaction・HITLで **長時間・安全な運用** を実現
* Go版は OpenTelemetry ネイティブと Retry & Reflect Plugin で **本番可観測性** を強化
* 両言語ともA2A Protocolで他言語エージェントと相互運用可能
* エンタープライズJava環境またはGo（Kubernetes）環境へのAIエージェント統合が現実的になった

## 参考リンク
