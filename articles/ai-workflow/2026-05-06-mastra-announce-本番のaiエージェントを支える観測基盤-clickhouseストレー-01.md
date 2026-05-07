---
id: "2026-05-06-mastra-announce-本番のaiエージェントを支える観測基盤-clickhouseストレー-01"
title: "[Mastra Announce] 本番のAIエージェントを支える観測基盤 ― ClickHouseストレージサポートが正式リリース"
url: "https://zenn.dev/shiromizuj/articles/2202620087cd64"
source: "zenn"
category: "ai-workflow"
tags: ["LLM", "zenn"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## AIエージェントが本番に出た後、最初の壁

2026年5月5日、Mastraは **ClickHouseストレージアダプター（`@mastra/clickhouse`）** の正式リリースを発表しました。

AIエージェントを開発環境でうまく動かすことと、本番で安定して運用し続けることは、まったく別の話です。特に「観測性（Observability）」の領域でこのギャップが顕著に現れます。

エージェントがどんなLLM呼び出しをしたか、ツールは何を受け取って何を返したか、どこで失敗したか、どのモデルがトークンを食い尽くしているか――本番エージェントを持つチームが知りたい情報はどこにあるのでしょうか？Mastraはこれらのデータを「トレース」「ログ」「メトリクス」として収集しますが、収集したデータをどこに貯めるかが、スケールするかどうかの分かれ目になっていました。

今回のリリースは、その問いへの明確な答えです。

---

## 背景：なぜ「ストレージ」が問題になるのか

### ローカル開発では十分だったDuckDB

Mastraのオブザーバビリティは、デフォルトでは **DuckDB** という組み込みデータベースを使います。DuckDBはOLAP（オンライン分析処理）に特化した高性能な組み込みデータベースで、ローカル開発や小規模なプロトタイプには十分すぎるほどの性能があります。

ただし「組み込み」という性質が、本番環境では制約になります。DuckDBはファイルシステム上の単一ファイルにデータを書き込みます。多くの現代的なクラウドホスティング環境では、コンテナやサーバーレス関数の**ファイルシステムがエフェメラル（一時的）**、つまりコンテナが再起動するたびにデータが消えます。Railway・Fly.io・Render・Vercelなどのプラットフォームはすべてこの「エフェメラルなファイルシステム」を持っています。

試しにDuckDBをこれらのプラットフォームにデプロイすると、毎回の再デプロイのたびにトレースとメトリクスの履歴がリセットされます。これでは継続的な品質改善のためのデータが積み上がっていかず、本番モニタリングツールとしては使えません。

### OLTP型データベース（PostgresやLibSQL）では何が起きるか

「ならPostgresに入れればいいのでは？」と思うかもしれません。しかし、Mastraが収集するトレースとメトリクスのデータ量と書き込みパターンは、PostgresのようなOLTP（オンライントランザクション処理）型データベースには向いていません。

トレースデータは**ストリーム的な大量書き込み**が発生します。エージェントが動くたびに、LLM呼び出し・ツール実行・ステップ完了・エラーなど無数のスパンが生成されます。そして分析時には「過去1週間のモデルごとのトークン消費を集計したい」「最後の100回の実行でエバリュエーションスコアがどう推移したか見たい」といった**集計クエリ**が走ります。

行単位の書き込みと読み込みを得意とするOLTPデータベースに対し、こうした集計処理は非常に重くなります。Mastraのロードマップウェビナーでも「Postgresでメトリクスをスケールさせようとしたチームが軒並み詰まった」という話が出ていました。

---

## ClickHouseとは何か ― 分析に特化した「列指向データベース」

ClickHouseはOSSのカラム型（列指向）データベースで、2009年にYandexで開発が始まり、2021年にオープンソース企業として独立しました。BINDINGとなるのは以下の特性です。

### 列指向ストレージとは

一般的なRDB（PostgresやMySQL）は**行指向**で、1レコードのすべての列がディスク上に連続して並びます。一方、ClickHouseは**列指向**で、同じ列のデータが連続して並びます。

```
行指向（通常のRDB）:
  [span_id, trace_id, timestamp, duration, model, tokens, status]
  [span_id, trace_id, timestamp, duration, model, tokens, status]
  ...

列指向（ClickHouse）:
  [span_id1, span_id2, span_id3, ...]
  [trace_id1, trace_id2, trace_id3, ...]
  [timestamp1, timestamp2, timestamp3, ...]
  [duration1, duration2, duration3, ...]
```

これの何がうれしいかというと、「過去7日間のすべてのスパンのモデル名ごとのトークン合計を出せ」というクエリで、`model`列と`tokens`列だけ読み込めばよく、他の列を完全に無視できます。同じデータ量でも読み込むバイト数が劇的に減るため、集計クエリが高速になります。

また、同じ値が並ぶ列は圧縮が非常に効きます。例えば `status: "success"` が1万行並んでいれば、ほぼ1レコード分のストレージで済みます。これがトレースデータの圧縮率がPostgresより高い理由です。

### ReplacingMergeTree：書き込み最優先の設計

MastraのClickHouseアダプター（vNextスキーマ）は `ReplacingMergeTree` というテーブルエンジンを使います。これはClickHouseが提供するエンジンの一つで、**挿入専用（insert-only）** の動作に最適化されています。

通常のデータベースでは「レコードを更新（UPDATE）」しますが、ReplacingMergeTreeでは更新も「新しい行を挿入する」という形で行い、後から同一キーの行をマージして最新状態を確定させます。これにより書き込み時のロック競合が最小化され、高スループットの並行書き込みが実現します。

Mastraの `DefaultExporter` は、ClickHouseをバックエンドとして使う場合に自動的に「挿入専用ストラテジー」を選択し、スパンを個別に更新するのではなくまとめてバッチ挿入します。これが「高スループット書き込み」の正体です。

---

## 何が変わるか ― Mastraでの具体的な変化

### メトリクスダッシュボードが機能する

Mastra Studioにはメトリクスダッシュボードがあり、モデルごとのコスト推移・トークン消費・エバリュエーションスコアの変化などを視覚化できます。このダッシュボードは本番データが継続的に積み上がってこそ意味があります。

DuckDBではデプロイのたびにリセットされ、PostgresではOLAP的な集計クエリが重くなる。ClickHouseはその両方の問題を解決し、メトリクスダッシュボードを「真に使えるもの」にします。

### コンポジットストレージという設計思想

今回のアダプターは `MastraCompositeStore` と組み合わせて使います。これはMastraのストレージを「ドメインごとに別々のバックエンドに分ける」仕組みです。

```
import { MastraCompositeStore } from "@mastra/core/storage";
import { PostgresStore } from "@mastra/pg";
import { ObservabilityStorageClickhouseVNext } from "@mastra/clickhouse";

storage: new MastraCompositeStore({
  id: "composite-storage",
  default: new PostgresStore({
    id: "pg",
    connectionString: process.env.DATABASE_URL!,
  }),
  domains: {
    observability: new ObservabilityStorageClickhouseVNext({
      url: process.env.CLICKHOUSE_URL!,
      username: process.env.CLICKHOUSE_USERNAME!,
      password: process.env.CLICKHOUSE_PASSWORD!,
    }),
  },
})
```

この設計では：

* **アプリケーションデータ（メモリ・ワークフロー・メッセージ履歴など）→ PostgresやLibSQL**
* **オブザーバビリティデータ（トレース・ログ・メトリクス・スコア）→ ClickHouse**

という役割分担になります。それぞれのデータ特性に合ったデータベースを使う、というシンプルで理にかなった分割です。

### すべてをClickHouseに集約する選択肢もある

アプリケーションデータもClickHouseで管理したい場合は、`ClickhouseStoreVNext` を使えばコンポジットを自分で組まなくてもすべてのドメインがClickHouseでカバーされます。

```
import { ClickhouseStoreVNext } from "@mastra/clickhouse";

export const mastra = new Mastra({
  storage: new ClickhouseStoreVNext({
    id: "clickhouse-storage",
    url: process.env.CLICKHOUSE_URL!,
    username: process.env.CLICKHOUSE_USERNAME!,
    password: process.env.CLICKHOUSE_PASSWORD!,
  }),
});
```

---

## vNextスキーマとレガシースキーマの違い

`@mastra/clickhouse` パッケージには2種類のアダプターがあります。

| クラス | スキーマ | 推奨用途 |
| --- | --- | --- |
| `ObservabilityStorageClickhouseVNext` | vNext（新スキーマ） | 新規プロジェクト |
| `ObservabilityStorageClickhouse` | レガシースキーマ | 既存プロジェクトの後方互換 |

vNextスキーマは `ReplacingMergeTree` ベースの挿入専用設計で書き込みスループットが高く、新規プロジェクトに推奨されます。レガシースキーマは既存プロジェクトが壊れないために残されており、設定インターフェイスはvNextと同じです。

---

## ホスティングオプション

ClickHouseは以下の方法で利用できます。

### ClickHouse Cloud（マネージドサービス）

[ClickHouse Cloud](https://clickhouse.com/cloud) は無料トライアルが付いたマネージドサービスです。URLとユーザー名・パスワードをそのまま `@mastra/clickhouse` の設定に使えます。最も手軽な選択肢です。

### セルフホスト（Dockerで1分起動）

```
docker run -d --name mastra-clickhouse \
  -p 8123:8123 -p 9000:9000 \
  -e CLICKHOUSE_USER=default \
  -e CLICKHOUSE_PASSWORD=password \
  clickhouse/clickhouse-server
```

ローカル開発はこれで十分です。本番ではKubernetesやVPS上での運用も可能です。

### Railway・Fly.io・Renderなどのプラットフォーム

RailwayはDockerイメージからClickHouseサービスを追加でき、アプリコンテナからRailwayのプライベートネットワーク経由で接続できます。他のプラットフォームでも同様のアプローチが使えます。

---

## セットアップ手順まとめ

### 1. パッケージのインストール

```
npm install @mastra/clickhouse
# @mastra/core@1.29.0 以降が必要
```

### 2. 環境変数の設定

```
CLICKHOUSE_URL=https://your-instance.clickhouse.cloud:8443
CLICKHOUSE_USERNAME=default
CLICKHOUSE_PASSWORD=your-password
```

### 3. Mastraインスタンスの設定

```
import { Mastra } from "@mastra/core";
import { MastraCompositeStore } from "@mastra/core/storage";
import { ObservabilityStorageClickhouseVNext } from "@mastra/clickhouse";
import { Observability, DefaultExporter } from "@mastra/observability";

export const mastra = new Mastra({
  storage: new MastraCompositeStore({
    id: "composite-storage",
    default: {
      // 既存のデフォルトストレージ（PostgresやLibSQLなど）
    },
    domains: {
      observability: new ObservabilityStorageClickhouseVNext({
        url: process.env.CLICKHOUSE_URL!,
        username: process.env.CLICKHOUSE_USERNAME!,
        password: process.env.CLICKHOUSE_PASSWORD!,
      }),
    },
  }),
  observability: new Observability({
    configs: {
      default: {
        serviceName: "mastra",
        exporters: [new DefaultExporter()],
      },
    },
  }),
});
```

`DefaultExporter` はClickHouseバックエンドを検出すると自動的に挿入専用ストラテジーを使います。追加の設定は不要です。

### 4. 自前のClickHouseクライアントを使う場合

タイムアウトや圧縮などカスタム設定が必要な場合は、`@clickhouse/client` で事前設定したクライアントを渡せます。

```
import { createClient } from "@clickhouse/client";
import { ClickhouseStore } from "@mastra/clickhouse";

const client = createClient({
  url: process.env.CLICKHOUSE_URL!,
  request_timeout: 60_000,
  compression: { request: true, response: true },
});

const storage = new ClickhouseStore({ id: "clickhouse-storage", client });
```

---

## どんな場面でClickHouseに切り替えるべきか

| 状況 | 推奨ストレージ |
| --- | --- |
| ローカル開発・プロトタイプ | DuckDB（デフォルト） |
| 本番デプロイ（Railway・Vercel等） | ClickHouse |
| 継続的なメトリクス・スコア追跡が必要 | ClickHouse |
| チームでStudio共有・Studio Authを使う | ClickHouse |
| エフェメラルなファイルシステムの環境 | ClickHouse（必須） |

---

## ClickHouse 入門ガイド ― 歴史・競合・価格・選択の基準

ここまではMastraにおけるClickHouseの使い方を中心に解説してきましたが、「そもそもClickHouseとはどんなプロダクトなのか」をもう少し掘り下げます。

### 誕生の経緯 ― Yandexの「分析の壁」から生まれたデータベース

ClickHouseが産まれたのは **2009年** 、ロシアの検索エンジン企業 **Yandex** の社内プロジェクトとしてです。Yandexが運営するウェブ解析サービス **Yandex.Metrica** は、世界第2位の規模を持つウェブアナリティクスプラットフォームでした。1日あたり120億件のイベント（ページビューやクリック）を処理し、ユーザーが「任意のセグメントでリアルタイムにカスタムレポートを作れる」という要件がありました。

当時Yandexが使っていた既存のOLAPデータベースでは、このような「事前集計なしに、ユーザーの好みに応じてその場で集計するクエリ」に対応できませんでした。そこで社内で開発が始まったのがClickHouseです。

**2016年** にClickHouseはオープンソースとして公開（Apacheライセンス）。Yandex以外の企業にも急速に広がり、2014年時点ですでに1日200億イベントを処理するまで成長していた実績が注目を集めました。

**2021年** に Alexey Milovidov（ClickHouseの生みの親・首席エンジニア）をはじめとするコアチームがYandexからスピンアウトし、独立企業 **ClickHouse, Inc.** を設立。2021年に2億5000万ドルのシリーズBを調達し、現在はサンフランシスコ（ベイエリア）とオランダのアムステルダムに拠点を置くグローバル企業になっています。

---

### 競合製品との位置付け

ClickHouseが競合するのは、Snowflake・Amazon Redshift・Google BigQuery・Databricksといった、いわゆる **クラウドデータウェアハウス（DWH）** カテゴリの製品です。ただし、立ち位置には明確な差異があります。

| 製品 | 強みの領域 | リアルタイム性 | コスト傾向 | OSS有無 |
| --- | --- | --- | --- | --- |
| **ClickHouse** | リアルタイム分析・高並行クエリ | 非常に高い（ミリ秒〜秒） | 低め | ✅ Apache 2.0 |
| **Snowflake** | バッチ型DWH・BI連携 | 中（秒〜分） | 高め | ❌ クローズド |
| **Amazon Redshift** | AWS統合・バッチ分析 | 低〜中（秒〜分） | 中〜高 | ❌ クローズド |
| **Google BigQuery** | 大規模バッチ・ML連携 | 低（分単位が主） | 従量制で高くなりやすい | ❌ クローズド |
| **Databricks** | データレイク+ML・Sparkベース | 中（数十秒〜） | 高め | Delta Lake部分のみOSS |

**ClickHouseが際立つのは「リアルタイム性」と「コスト効率」の組み合わせ**です。公式の比較ページによると、Snowflakeと比べてクエリが3〜5倍高速かつコストが4倍低い、Redshiftと比べてクエリが2.5倍高速かつコストが最大75%削減できると主張しています（いずれもClickHouse社の自社データであるため参考値として捉えてください）。

ただし、ClickHouseが向いていない場面もあります。トランザクション処理（OLTP）や、複雑な結合・更新が多いワークロードには適しておらず、そうしたケースではPostgresのようなOLTPデータベースの方が適切です。

---

### ライセンスと利用形態

#### オープンソース版（セルフホスト）

ClickHouseのコアエンジンは **Apache License 2.0** でGitHubに公開されています（[github.com/ClickHouse/ClickHouse](https://github.com/ClickHouse/ClickHouse)）。Dockerイメージも公式に提供されており、ライセンス料は **完全無料** です。自分のサーバーやKubernetes上で動かす場合のコストは、インフラ費用のみです。

セルフホストの場合に必要な作業としては、クラスタ管理・スケールアップ・バックアップ・アップグレード対応などを自分で行う必要があります。小〜中規模ならDockerで十分ですが、大規模になるにつれて運用コストが上がります。

#### ClickHouse Cloud（マネージドSaaS）

公式マネージドサービスの **ClickHouse Cloud** は以下の3プランです。

| プラン | ストレージ | メモリ | コンピュート単価/時 | 用途 |
| --- | --- | --- | --- | --- |
| **Basic** | 最大1TB | 8〜12GiB | $0.2181/unit | 小規模・検証 |
| **Scale** | 無制限 | 可変 | $0.2985/unit | 本番・中〜大規模 |
| **Enterprise** | 無制限 | 可変（カスタム） | $0.3903/unit | 大企業・コンプライアンス要件あり |

ストレージは共通で **$25.30/TB/月**（データ圧縮後）。コンピュートは使った分だけ課金され、アイドル時は自動でスケールダウン（ゼロまで落とすことも可）されます。30日間の無料トライアルと $300 のクレジットが付きます。

BasicプランとScaleプランの実質的な違いは、可用性ゾーン数（1 vs 2+）・バックアップ設定の自由度・サポート応答速度（1営業日 vs 24×7で1時間）・自動垂直スケーリングの有無などです。

Enterpriseプランには HIPAA・PCI コンプライアンス対応・SAML SSO・暗号化キーの自己管理（CMEK）などが追加されます。

#### BYOC（Bring Your Own Cloud）

Enterpriseの延長として、自社のVPC内にClickHouse Cloudをデプロイするモデルも提供されています。「データが外に出てはいけない」というコンプライアンス要件がある企業向けです。料金は要相談。

---

### 競合との性能・拡張性・可用性・価格の比較

#### パフォーマンス

ClickHouseの最大の特徴は、**高い同時並行性とミリ秒〜数秒のクエリレイテンシ**です。ClickHouseは1ノードあたり1,000 QPS以上を自然にこなせます。一方でRedshiftは全キューを合わせて同時実行数50が上限とされており、ユーザー向けアプリケーションに埋め込むような「リアルタイム・高並行」の用途には難があります。Snowflakeも並行性を高めるにはマルチクラスタ設定が必要で、追加コストが発生します。

AIエージェントのオブザーバビリティという文脈では、「トレースを書き込みながら同時にダッシュボードの集計クエリを走らせる」という混在ワークロードが発生します。ClickHouseはこれが得意な設計になっています。

#### 拡張性

* **ClickHouse（セルフホスト）**: シェアードナッシング（Shared-Nothing）アーキテクチャで水平スケールが得意。ノードを追加するだけで線形にスケールします。
* **ClickHouse Cloud**: ストレージとコンピュートが分離されており、それぞれ独立してスケールできます。AutoScaling機能により、急増するクエリに自動で対応します。
* **Snowflake**: 同じくストレージ・コンピュート分離設計ですが、スケールアップにウォームアップ時間がかかり、ClickHouseほどリアルタイムのバーストに強くありません。
* **Redshift**: 水平スケールはできますが、ノード追加には時間とコストがかかります。

#### 可用性

ClickHouse CloudのScaleプランは複数のアベイラビリティゾーンに対応し、フルマネージドで高可用性を確保します。セルフホストの場合は自分でレプリケーション（ReplicatedMergeTree）と分散クエリ（Distributed テーブルエンジン）を設計する必要があります。

#### 価格

大雑把な感覚値として：

* **ClickHouse（セルフホスト）**: インフラ代のみ。VPS1台（$20〜$50/月程度）から始められる。大規模になるほど管理コストが課題になる。
* **ClickHouse Cloud Basic**: 小規模ならストレージ数十GB + わずかなコンピュートで月数ドル〜数十ドル程度に収まることが多い。
* **Snowflake**: コンピュートはクレジット単位で$2〜$4/クレジット（リージョンにより変動）。インタラクティブなクエリが多いと急速にコストが膨らみやすい。
* **Redshift**: ノード固定課金（例：ra3.xlplusで$0.65/時/ノード）で、使わない時間も課金される。
* **BigQuery**: クエリごとにスキャンしたデータ量で課金（$5/TB）。大規模な分析クエリでは高コストになる場合がある。

---

### まとめ ― ClickHouseを選ぶべきか

ClickHouseが「圧倒的に向いている」のは、**高スループットの書き込みと、低レイテンシの集計クエリを同時に求める**ユースケースです。AIエージェントのオブザーバビリティはまさにこれに当たります。

一方で、ClickHouseは「何でもできる万能DB」ではありません。トランザクション処理・行レベルの更新・複雑なリレーションを持つアプリケーションデータには向いていません。だからこそMastraも、アプリケーションデータにはPostgresを使い、オブザーバビリティデータにはClickHouseを使う「コンポジットストレージ」という設計を採用しているのです。

---

## 関連リンク
