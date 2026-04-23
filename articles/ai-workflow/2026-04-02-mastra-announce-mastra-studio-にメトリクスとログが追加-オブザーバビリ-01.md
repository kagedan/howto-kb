---
id: "2026-04-02-mastra-announce-mastra-studio-にメトリクスとログが追加-オブザーバビリ-01"
title: "[Mastra Announce] Mastra Studio にメトリクスとログが追加 ― オブザーバビリティの三本柱がそろった"
url: "https://zenn.dev/shiromizuj/articles/2823ea84f1cd03"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

2026年4月1日、Mastra は **Mastra Studio へのメトリクスとログの追加**を発表しました。`@mastra/core` 1.20.0 以降で利用可能になるこの機能により、Mastra はオブザーバビリティの三本柱——**トレース**・**メトリクス**・**ログ**——をすべて網羅するフレームワークとなります。

---

## 背景

### プロダクション運用が始まって見えてきた「見えない問題」

Mastra が 1.0 を迎えた 2026年1月以降、より多くのチームが Mastra を使ったエージェントをプロダクション環境へ投入するようになりました。開発中は Mastra Studio のトレース機能によって、エージェントが何をどの順序で実行したかを1ステップずつ確認できていましたが、実運用が始まると**単発のトレースでは拾えない問題**が浮かび上がってくるようになりました。

* 「先週に比べてエラーが増えているんだけど、原因が特定できない」
* 「このモデルを使い続けると月額コストがどれくらいになるのかわからない」
* 「特定のツール呼び出しだけレイテンシーが異常に高い日がある」
* 「ユーザーから『変な返答が来た』と言われても、ログが残っていないので追跡できない」

こうした声が Mastra チームに届き続けていたのが、今回の機能追加の直接のきっかけだったとのことです。

### オブザーバビリティの三本柱

「オブザーバビリティ（可観測性）」という概念には、広く認知された三本柱があります:

| 柱 | 役割 | 問いに答えるもの |
| --- | --- | --- |
| **トレース** | 個別の実行の流れを時系列で記録する | 「この実行で**何が起きたのか**」 |
| **メトリクス** | 時系列データを集計した数値指標 | 「**全体として**コストや速度はどうなっているか」 |
| **ログ** | 任意のタイミングで記録される構造化されたテキスト | 「**特定の時点**でアプリケーションは何をしていたか」 |

Mastra はすでにトレース機能とログ機能を持っていましたが、メトリクスが不在だったため、開発者は外部の監視ツールへの橋渡しを自前で行うか、あるいは「とにかくトレースを掘る」という手間のかかる方法に頼らざるを得ませんでした。今回の発表でこのギャップが埋まります。

また、ログ機能についても observability ストアに保存し Studio 上で検索可能にする新しいロギングシステムが導入されています。

### なぜ列指向ストアが必要なのか

メトリクスダッシュボードの裏側では、大量のイベント（例えば「過去7日間のすべてのエージェント実行の平均レイテンシー」）を高速に集計するクエリが走ります。このような**集計・時系列クエリ**は、PostgreSQL や LibSQL のような行指向データベースが苦手とする処理です。

そこで Mastra は DuckDB という**列指向の分析データベース**（**OLAP**）を採用しています。DuckDB はファイルシステム上で動作する組み込み型のため、インフラの追加なしにローカル開発環境でも使えます。本番環境向けには、今後 ClickHouse サポートが追加される予定です。

この設計上の判断を支えているのが **`MastraCompositeStore`** という仕組みです。ストレージをドメイン単位で分割し、会話メモリは LibSQL、オブザーバビリティは DuckDB、ワークフロー状態は PostgreSQL、といった構成を1つの設定で表現できます。

---

## ニュースリリースの内容

### 発表の概要

* **日時**: 2026年4月1日
* **著者**: Eric Pinzur（Mastra ソフトウェアエンジニア・オブザーバビリティリード）
* **発表内容**: `@mastra/core` 1.20.0 から利用できる Studio 向けメトリクスダッシュボードと検索可能ログの追加

### 新機能の全体像

**メトリクスダッシュボード（Studio）**  
すべてのエージェント・ツール・ワークフローに対して、以下の指標をダッシュボード上で可視化できます:

* モデルコスト（推定値）
* レイテンシー（パーセンタイル表示）
* eval スコア
* エラー件数・エラー率

![](https://static.zenn.studio/user-upload/708fbbbae987-20260402.png)  
*Mastraの公式アナウンスページより、Studioのメトリクスダッシュボード画像*

**ログ（Studio）**  
`logger.info()` や `logger.warn()` の呼び出しが observability ストアに保存され、Studio から検索・フィルタリング可能になります。各ログエントリには以下のコンテキストが自動付与されます:

* トレース ID / スパン ID
* エンティティタイプ・エンティティ名（エージェント、ツール、ワークフローなど）
* 親エンティティ・ルートエンティティ
* ユーザー ID・リクエスト ID

これにより「このユーザーの操作に関連するログだけ見たい」「このトレースに紐づくログを全部出したい」といった絞り込みが Studio のUI から直感的に行えます。

![](https://static.zenn.studio/user-upload/ae7c80422645-20260402.png)  
*Mastraの公式アナウンスページより、Studioのログ確認画面の画像*

---

## 具体的な掘り下げ

### セットアップの全体構成

セットアップは3ステップで完結します。

#### ステップ1: DuckDB を observability ドメインに割り当てる

```
npm install @mastra/observability @mastra/duckdb
```

```
// src/mastra/index.ts
import { Mastra } from '@mastra/core/mastra';
import { MastraCompositeStore } from '@mastra/core/storage';
import { LibSQLStore } from '@mastra/libsql';
import { DuckDBStore } from '@mastra/duckdb';

export const mastra = new Mastra({
  storage: new MastraCompositeStore({
    id: 'composite-storage',
    default: new LibSQLStore({       // 既存のストレージ設定を維持
      id: 'mastra-storage',
      url: 'file:./mastra.db',
    }),
    domains: {
      observability: new DuckDBStore().observability,  // ← ここを追加するだけ
    },
  }),
});
```

`MastraCompositeStore` の `domains` に `observability` キーを追加するだけで、既存のメモリ・ワークフロー設定は一切変更不要です。

#### ステップ2: DefaultExporter を接続する

```
import { Observability, DefaultExporter } from '@mastra/observability';

export const mastra = new Mastra({
  observability: new Observability({
    configs: {
      default: {
        serviceName: 'my-app',
        logging: { enabled: true, level: 'info' },    // ログ転送を有効化
        exporters: [new DefaultExporter()],            // メトリクス収集に必須
      },
    },
  }),
});
```

`DefaultExporter` は Mastra が生成するすべてのスパンからメトリクスを抽出し、DuckDB に書き込む役割を担います。Datadog や Langfuse などの外部エクスポーターではこのメトリクス抽出は行われないため、Studio ダッシュボードを使うには `DefaultExporter` が必須です。

`logging.enabled: true` を設定すると、アプリケーション内の `logger.info()` などの呼び出しが Pino コンソール出力と observability ストアの**両方**に書き込まれるようになります。既存のロギング設定はそのままに、ストレージへの転送が追加される形です。

#### ステップ3: ツール・ワークフロー内にログを添える

```
// ツール内
const logger = context?.mastra.getLogger();
logger?.info(`Fetching weather for ${context.city}`, { city: context.city });

// ワークフロー内
const logger = mastra.getLogger();
logger.warn('Retry limit approaching', { retryCount: 3 });
```

ログには任意の構造化データを第2引数として渡せます。Studio ではこれらのフィールドもフィルタリングに使えます。

### 自動収集されるメトリクスの全貌

Mastra がスパン終了時に自動的に計算・保存するメトリクスは以下の3カテゴリです:

#### 実行時間（Duration）

| メトリクス名 | 計測対象 |
| --- | --- |
| `mastra_agent_duration_ms` | エージェント実行全体 |
| `mastra_tool_duration_ms` | ツール呼び出し（MCPツール含む） |
| `mastra_workflow_duration_ms` | ワークフロー実行 |
| `mastra_model_duration_ms` | LLMへのモデル生成呼び出し |
| `mastra_processor_duration_ms` | プロセッサ実行 |

各メトリクスには `status: ok | error` のラベルが付いているため、エラー発生時の実行時間を正常時と分けて分析できます。

#### トークン使用量（Token Usage）

モデル生成スパンのレスポンスから `usage` データを抽出して記録します:

| カテゴリ | メトリクス名の例 |
| --- | --- |
| 入力トークン合計 | `mastra_model_total_input_tokens` |
| テキスト入力 | `mastra_model_input_text_tokens` |
| キャッシュ読み込み（Anthropic等） | `mastra_model_input_cache_read_tokens` |
| 推論トークン（OpenAI o系） | `mastra_model_output_reasoning_tokens` |
| 出力トークン合計 | `mastra_model_total_output_tokens` |

プロバイダーが詳細カテゴリを報告しない場合、そのサブカテゴリのメトリクスは省略されます。

#### コスト推定（Cost Estimation）

Mastra 内部に組み込まれた**プライシングレジストリ**がプロバイダー名とモデル名からコストを推定します。主要プロバイダー（OpenAI・Anthropic 等）のモデルが網羅されており、一致するエントリが見つかった場合は各トークンメトリクスに以下のフィールドが追加されます:

| フィールド | 内容 |
| --- | --- |
| `estimatedCost` | このメトリクスの推定コスト |
| `costUnit` | 通貨単位（例: USD） |
| `provider` | プロバイダー名 |
| `model` | モデル識別子 |

### トレースとメトリクスの相互参照

メトリクスには生成元スパンの `CorrelationContext` スナップショットが付与されています。これにより「ダッシュボードでレイテンシーのスパイクを見つけた → そのスパイクを生んだトレースに直接ジャンプ → 問題のスパンを特定」という流れが Studio 内で完結します。

コリレーションコンテキストには以下が含まれます:

* トレース相関: `traceId`, `spanId`
* エンティティ階層: エンティティ・親エンティティ・ルートエンティティの種別/ID/名前
* アイデンティティ: `userId`, `organizationId`, `requestId`, `sessionId`
* デプロイ情報: `environment`, `serviceName`, `experimentId`

### ClickHouse への道

現在の DuckDB サポートはローカル開発・小〜中規模のプロダクションに適しています。しかし大規模なトラフィックでは「1エージェント呼び出しで数百スパン、1日で数千トレース」というスケールになり得ます。高トラフィックな本番環境向けに、次のステップとして **ClickHouse** サポートが追加される予定です。

ClickHouse は大量の書き込みと集計クエリに強い OLAP データベースで、Mastra のメトリクスが依存する集計処理には理想的な選択肢です。`MastraCompositeStore` の `observability` ドメインを ClickHouse に向けるだけで移行できるよう設計されているため、アプリケーションコードへの変更は最小限に抑えられる見込みです。

### 注意点

* メトリクスとログは**有効化した時点から**蓄積されます。過去のトレースデータへのバックフィルは行われません。
* DuckDB はインメモリ実行を含むモードでは再起動時にデータがリセットされます。ファイルパスを指定した永続化モードで使用してください。
* `DefaultExporter` 以外のエクスポーター（Datadog, Langfuse 等）はメトリクスを Mastra ストレージに書き込みません。Studio ダッシュボードには `DefaultExporter` が必須です。

---

## まとめ

| 機能 | 解決する課題 |
| --- | --- |
| **メトリクスダッシュボード** | 時系列での集計ビュー（コスト・エラー率・レイテンシー）を得る |
| **検索可能ログ** | トレースに紐付いた構造化ログを Studio から絞り込む |
| **DuckDB 対応** | インフラ追加なしでローカル開発からメトリクス収集を開始できる |
| **MastraCompositeStore** | 既存ストレージ設定を変更せず observability ドメインだけを追加できる |

1.20.0 以降で `@mastra/observability` と `@mastra/duckdb` を追加し、`DefaultExporter` と `DuckDBStore` を設定するだけでこれらすべてが有効になります。

---

## 参考リンク
