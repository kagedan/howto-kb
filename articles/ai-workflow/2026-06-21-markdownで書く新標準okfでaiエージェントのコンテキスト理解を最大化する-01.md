---
id: "2026-06-21-markdownで書く新標準okfでaiエージェントのコンテキスト理解を最大化する-01"
title: "Markdownで書く新標準「OKF」でAIエージェントのコンテキスト理解を最大化する"
url: "https://zenn.dev/caron14/articles/open-knowledge-format-intro"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "zenn"]
date_published: "2026-06-21"
date_collected: "2026-06-22"
summary_by: "auto-rss"
query: ""
---

こんにちは！最近、LLMを用いたAIエージェントの開発や、社内データのコンテキスト集約に取り組んでいる方は多いのではないでしょうか。

AIエージェントやRAGの精度を高めるためには、モデルへ「正しいコンテキスト（社内独自の用語定義、メトリクスの計算ロジック、テーブル構造など）」を渡すことが不可欠です。しかし、これらの情報はメタデータカタログ、社内Wiki、コードのコメント、あるいはベテランエンジニアの頭の中など、さまざまな場所に断片化（サイロ化）して存在しているのが現状です。

2026年6月、Google Cloudチームはこの課題を解決するための新しいオープンな仕様である「[Open Knowledge Format (OKF)](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing?hl=en)」を発表しました。

今回は、この注目の新標準「OKF」について、私の試行錯誤やハマりポイントを交えつつ、何が優れているのか、どのような構造なのかを分かりやすく紹介します。

---

## 1. メタデータ管理で直面した「泥臭い」課題

実務でAIエージェントに社内データベースを操作させようとした際、以下のような課題にぶつかりました。

* **パーサー自作の闇**: AIにコンテキストを渡すため、独自のMarkdown Wikiを作ってGit管理してみたものの、エージェント側のプロンプト構築やMarkdownのパース処理が毎回泥臭いアドホックなコードになり、メンテナンスがカオス化しました。
* **テーブル増殖に伴う破綻**: スキーマや関連テーブルが増えるたびに手動でWikiを更新するのが破綻し、古いメタデータのままAIにクエリを生成させ、エラーを連発させてしまうというハマりポイントを経験しました。

そんな中、著名なAI研究者であるAndrej Karpathy氏が「LLM Wiki」という構想で語ったように、「AIが読み書きしやすい標準化されたナレッジフォーマット」があれば解決するのではないか、と考えていました。

そこへ登場したのが、Googleが提唱する\*\*Open Knowledge Format（OKF）\*\*です。

---

## 2. Open Knowledge Format（OKF）とは？

Open Knowledge Format（OKF）は、現代のAIシステムが必要とするメタデータ、コンテキスト、そして厳選された知識を表現するための、**ベンダーニュートラルで、AIエージェントと人間の双方にとって扱いやすいオープンな標準仕様**です。

一言で言えば、近年トレンドとなっている「LLM-Wiki」パターン（AIに共有のMarkdownライブラリを読み書きさせ、知識を蓄積していく手法）を共通化し、ポータブルかつ相互運用可能にしたフォーマットです。

### OKFが掲げる3つの設計原則

1. **最小限の主張（Minimally opinionated）**: OKFがドキュメントに求める必須フィールドは `type`（種類）の1つだけです。それ以外の項目や構成は、作成者が自由に定義できます。
2. **生産者と消費者の独立性（Producer/consumer independence）**: 人間が手動で書いたWikiをAIエージェントに読ませることも、逆にシステムが自動生成したデータを可視化ツールで人間が閲覧することも可能です。
3. **プラットフォームではなくフォーマット（Format, not platform）**: 特定のクラウド、データベース、モデルプロバイダー、AIフレームワークに依存しません。専用のSDKや独自のアカウントがなくても、誰でも読み書き・提供が可能です。

---

## 3. OKFのデータ構造はどうなっている？

OKF v0.1の仕様は非常にシンプルです。基本は\*\*「YAMLフロントマター（メタデータ部）が付いたMarkdownファイルのディレクトリ構造」\*\*です。

例えば、ある販売データ（sales）に関するナレッジは、以下のようなファイル配置になります。

```
sales/
├── index.md
├── datasets/
│   ├── index.md
│   └── orders_db.md
├── tables/
│   ├── index.md
│   ├── orders.md
│   └── customers.md
└── metrics/
    ├── index.md
    └── weekly_active_users.md
```

そして、個々の概念（コンセプト）を表すファイル（例：`orders.md`）の中身は、次のように定義されます。

sales/tables/orders.md

```
---
type: BigQuery Table
title: Orders
description: One row per completed customer order.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders
tags: [sales, revenue]
timestamp: 2026-05-28T14:30:00Z
---

# Schema
| Column | Type | Description |
|---------------|-----------|------------------------------------------|
| `order_id` | STRING | Globally unique order identifier. |
| `customer_id` | STRING | FK to [customers](/tables/customers.md). |

# Joins
Joined with [customers](/tables/customers.md) on `customer_id`.
```

### ファイル形式と詳細仕様

OKFは特別な独自形式ではなく、既存の標準的なファイル形式と規約の組み合わせで構成されています。

* **ファイル拡張子と構成**:
  + 各知識（概念）は標準の **Markdown (`.md`)** ファイルとして記述されます。
  + 各ファイルの先頭にはメタデータとなる **YAMLフロントマター** を配置します。
* **概念 ID (Concept ID) の決定**:
  + ナレッジバンドル（ディレクトリ）内でのファイル相対パスが、そのまま「概念 ID」として機能します。
* **予約ファイル (Reserved Files)**:
  + `index.md`: ディレクトリやバンドルの目次・マップ（Table of Contents）として機能します。
  + `log.md`: ナレッジベースの更新履歴（変更履歴）を記録するために使用します。
* **フロントマターのフィールドルール**:
  + **必須フィールド**: `type`（種類、例：`BigQuery Table` や `Metric`）のみです。
  + **推奨フィールド**: `title` (タイトル), `description` (説明), `resource` (データソースのURI), `tags` (タグ配列), `timestamp` (更新日時) など。
* **マークダウンリンクによる関連付け**:
  + ファイル同士を通常のマークダウン相対リンク（例: `[customers](/tables/customers.md)`）で繋ぐことで、ディレクトリの階層構造を超えて、AIが探索可能な\*\*「ナレッジグラフ（知識の関係性グラフ）」\*\*を構築できます。

### 注目すべき特徴

* **ただのMarkdown**: あらゆるエディタで読め、GitHub上で美しくレンダリングされ、あらゆる検索ツールでインデックス可能です。
* **ただのファイル**: tarballとして配布でき、任意のGitリポジトリでホスト可能、任意のファイルシステムにマウントできます。
* **限定されたYAMLフロントマター**: 検索やクエリに必要な最小限の共通フィールドのみを標準化しています。
* **移植性の高さ**: 独自のSDKやAPI、中央集権的なレジストリが不要なため、Gitによるバージョン管理やポータビリティに優れています。

---

## 4. すでに公開されているエコシステム

Googleは仕様の公開（v0.1）と同時に、GitHub上の `GoogleCloudPlatform/knowledge-catalog` リポジトリにて、具体的なイメージを掴むためのリファレンス実装（ツールやサンプル群）を公開しています。

### 🤖 Enrichment Agent (濃縮エージェント)

BigQueryのデータセットをスキャンしてテーブルやビューごとのOKFドキュメントを自動作成し、さらにLLMが公式ドキュメントを巡回してスキーマや結合（Join）経路、引用元などを補完・リッチ化するエージェントです。

### 📊 Static HTML Visualizer (静的HTMLビジュアライザ)

OKFのディレクトリ群を、1つの自己完結型HTMLファイルだけで動的なインタラクティブ・グラフビューに変換できるツールです。バックエンドの設置やインストールは不要で、ブラウザ外にデータが流出することもありません。

サンプル bundle と Dataplex との統合

* **3つのサンプル bundle**: 「GA4 e-commerce」「Stack Overflow」「Bitcoin」の公開データセットを元に、自動生成された本物のOKFドキュメント群がサンプルとしてコミットされており、手元で構造を確認できます。
* **Dataplex との連携**: Google Cloud の既存製品である「Knowledge Catalog（旧Dataplex）」もすでにOKFの取り込み（Ingest）に対応しており、取り込んだナレッジをAIエージェントに提供できるようアップデートされています。

---

## 5. まとめと個人的な所感

「Open Knowledge Format（OKF）」は、まだ始まったばかりのスタートライン（v0.1）です。

しかし、結果的に複雑な圧縮技術や新しいランタイム、強制されるSDKなどを一切排除し、**「MarkdownとYAML」という誰もがすでに使っている技術の上に作られている点**が非常に強力であると感じます。

振り返ると、私たちが欲しかったのは、豪華なメタデータSaaSではなく、Gitでコミット・差分レビューができ、そのままLLMのコンテキストとして投入できる「シンプルなファイル」でした。

AIエージェントに社内データをうまく咀嚼させたい、あるいはメタデータ管理に頭を悩ませている方は、ぜひ以下の公式リポジトリから仕様をチェックし、まずは小さなリポジトリから試してみてはいかがでしょうか？
