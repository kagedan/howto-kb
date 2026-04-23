---
id: "2026-03-21-databricks-vector-indexの仕組みを技術的に理解する-deltaテーブルから類似-01"
title: "Databricks Vector Indexの仕組みを技術的に理解する — Deltaテーブルから類似検索まで"
url: "https://zenn.dev/tech_taka/articles/ead32412d7a5d2"
source: "zenn"
category: "ai-workflow"
tags: ["LLM", "zenn"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

[Mosaic AI Vector Searchとは](https://docs.databricks.com/aws/ja/vector-search/vector-search)  
[ベクトル検索エンドポイントとインデックスを作成する](https://docs.databricks.com/aws/ja/vector-search/create-vector-search)

## 第1章 Databricks Vector Indexとは何か

### 1-1. はじめに

LLMを使った検索やRAGを考えるとき、最初に出てくるのが「ベクトル検索」という考え方です。  
Databricksではこの機能を **Mosaic AI Vector Search** として提供しており、**Deltaテーブルを元に Vector Index を作成**し、類似した文書やデータを高速に検索する ことができます。Databricks公式でも、Vector Search は Delta table から index を構築し、埋め込みベクトルとメタデータを保持したうえで、REST API などから検索できる仕組みとして説明されています。

つまり、DatabricksのVector Indexは、単に「ベクトルを保存する箱」ではありません。  
**意味的に近いデータを高速に探すための検索用インデックス** であり、RAGやAIエージェントにおける「知識検索の実行面」を担うコンポーネントです。

## 1-2. そもそもベクトル検索とは何か

通常のデータベース検索では、`WHERE category = 'A'` や `LIKE '%battery%'` のように、値の一致や文字列条件で絞り込みます。  
一方、ベクトル検索では、文書やクエリを **embedding** に変換し、そのベクトル同士の近さを使って検索します。これにより、単語が完全一致していなくても、**意味的に近い内容** を見つけやすくなります。DatabricksのVector Searchも、この「埋め込みベクトルに基づく類似検索」を前提にした仕組みです。

ここで重要なのは、ベクトル検索は通常のインデックスとは目的が異なるという点です。  
B-treeインデックスのような一般的な索引は、等価条件や範囲条件の高速化には強い一方で、「意味的に近い文章を探す」用途には向いていません。Vector Indexはその代わりに、**高次元ベクトル空間の中で近いものを探すための索引** として使われます。Databricks公式でも、Vector Search は **「最も類似したベクトルを特定して関連文書を返す」** 仕組みとして整理されています。

### 1-3. DatabricksにおけるVector Indexの位置づけ

DatabricksでVector Indexを理解するうえで大事なのは、**データ本体と検索用インデックスを分けて考えること** です。  
Databricksでは、元データの保管先は基本的に **Deltaテーブル** です。その上で、検索を高速化するために **Vector Index** を作成し、さらにそのインデックスを外部から検索可能にするために **Vector Search Endpoint** を用意します。Databricks公式でも、Vector Search の主要コンポーネントとして endpoint と index を作成・管理する形が示されています。

この関係を整理すると、以下のように考えると分かりやすいです。

* **Delta Table**: 元データを保持する本体
* **Embedding**: 文書やレコードを数値ベクトルに変換したもの
* **Vector Index**: embedding と metadata を検索しやすい形に構成した索引
* **Vector Search Endpoint**: その索引をAPIやSDKから検索するための提供面

DatabricksのVector Indexは、あくまで **Lakehouse上のデータを意味検索できる形にするための検索層** です。  
このため、「Vector Index = データ保存基盤」ではなく、**「Delta Lake上のデータに対する検索アクセラレータ」** と捉える方が、アーキテクチャとして正確です。

#### テーブル→index構築→検索の全体イメージ

### 1-4. Vector Indexに入るもの

Databricks公式では、Vector Search index は **embedded data with metadata** を含むものとして説明されています。  
つまり、Vector Indexにはベクトルだけが入るわけではなく、検索結果として返したい文書本文やタイトル、カテゴリ、更新日時などの メタデータ列 も一緒に持たせる設計が重要になります。

#### ① ベクトルだけでは業務検索にならない

検索時に近いベクトルを見つけられても、結果として「何の文書なのか」「どのシステムのデータなのか」が分からなければ使いにくくなります。  
そのため、実際の検索基盤では **vector + metadata** の組み合わせが重要です。Databricksでも、filtering や reranking を使う前提で、文書に紐づく列を持つ設計が自然です。

#### ② 主キーが必要になる

Vector Indexは検索結果を返すだけでなく、元データとの対応関係を保つ必要があります。  
Databricksの index 作成時にも **primary key** を指定する設計になっており、どのレコードを返したのかを一意に識別するための列が重要です。

#### ③ 「検索用の列」を意識して設計する必要がある

全文をそのまま埋め込むのか、チャンク分割した本文を埋め込むのか、タイトルやカテゴリをメタデータで持つのかで、検索品質は大きく変わります。  
Databricks側はインデックス機能を提供しますが、**何をembeddingし、何をmetadataとして残すか** は利用者側の設計責任です。これはRAGの精度に直結する設計ポイントです。

### 1-5. Databricks Vector Indexは通常のDBインデックスと何が違うのか

Databricks Vector Indexを理解するうえで、通常のRDBインデックスとの違いを整理しておくと分かりやすいです。

#### 通常のインデックス

通常のインデックスは、`id = 100` や `date between ...` のような条件を高速に処理するためのものです。条件に一致するかどうかが明確であり、「近い」という概念は基本的に扱いません。

#### Vector Index

一方、Vector Indexは、クエリをベクトル化し、そのベクトルに **近い** レコードを探します。  
つまり、「一致」ではなく **類似度** に基づいて候補を返す点が本質です。Databricks公式でも、Vector Searchは「similar vectors」を見つけて関連文書を返す仕組みとして説明されています。

この違いを実務的に言い換えると、通常のインデックスは **構造化検索向け**、Vector Indexは **意味検索向け** です。  
そのため、両者は競合するものではなく、むしろ補完関係にあります。Databricksでも、Vector Searchは filtering をサポートしており、ベクトル類似検索に加えてメタデータ条件で絞り込む設計が取れます。

### 1-6. Databricksらしいポイント

DatabricksのVector Indexを他のベクトルDBと分けて考えるなら、特徴は **Lakehouseとの一体化** にあります。  
Databricksでは、Vector Search index は Deltaテーブルをソースにでき、更新時には自動同期させる構成も取れます。また、Unity Catalog配下のデータやガバナンスと組み合わせながら扱える点が大きな特徴です。Databricks公式でも、基盤となる Delta table の更新に応じて index を自動同期できることや、Vector Search が Databricksのガバナンスと統合されていることが示されています。

さらに、Databricksでは Vector Index を API や Python SDK だけでなく、**Databricks SQL** の **vector\_search() 関数** 経由でも利用できます。  
これは、検索基盤が単なるアプリ用APIに閉じず、Lakehouseの分析基盤からも呼び出せることを意味します。つまり、RAG用途だけでなく、分析基盤と検索基盤を近い位置に置けるのがDatabricksの強みです。

Databricks SQL

自然言語の文字列をそのまま投げて、近い文書を上位5件返す最小例です。  
この書き方は、**Databricks側で検索文をベクトル化して検索する** イメージで理解しやすいです。`num_results` のデフォルトは 10 ですが、ここでは 5 件に絞っています。

```
SELECT *
FROM vector_search(
  index => 'main.rag.product_manual_index',
  query_text => 'Databricks Vector Index の仕組み',
  num_results => 5
);
```

**何をしているか**

* index  
  検索対象の Vector Search index の完全修飾名
* query\_text  
  自然言語の検索文
* num\_results  
  返却する最大件数

vector\_search() 関数

こちらは、アプリや前段処理で既に埋め込みベクトルを作ってあり、それを直接検索に使う例です。  
Databricks公式では、`query_vector` は `ARRAY<FLOAT>` / `ARRAY<DOUBLE>` / `ARRAY<DECIMAL>` で渡せます。特に **self-managed vector のDelta Sync Index** では `query_vector` が必要です。

```
SELECT *
FROM vector_search(
  index => 'main.rag.product_manual_index',
  query_vector => array(
    0.0123, -0.0844, 0.1932, 0.0044, -0.2201
  ),
  num_results => 5
);
```

## 第2章 どうやってVector Indexを作るのか

### 2-1. はじめに

Databricks公式では、Mosaic AI Vector Searchを使うには、まず **vector search endpoint** を作成し、その上に **vector search index** を作成する流れになっています。index は Delta table から作成され、Unity Catalog 配下で管理されます。endpoint は index を提供する実行面であり、自動スケールにも対応しています。

つまり、作成手順の大枠は次の2段階です。

1. **Endpoint を作る**  
   Vector Indexを配置して検索要求を受ける実行基盤を用意する
2. **Index を作る**  
   Deltaテーブルや埋め込みベクトルを元に、検索用のインデックスを構築する

この2段階を理解すると、DatabricksのVector Searchの作り方がかなり整理しやすくなります。

### 2-2. まず何を準備するのか

Vector Indexを作る前に、最低限、次の要素を整理しておく必要があります。

* **検索対象データ**
* **主キー**
* **ベクトル化対象の列**
* **返却したいメタデータ列**
* **Vector Search Endpoint**
* **Index の作成方式**

Databricks公式でも、index は Delta table を元に作られ、embedded data with metadata を保持するものとして説明されています。また、インデックス作成時には primary key や embedding に関する設定が必要です。

ここで重要なのは、**Vector Indexの作成は単なるDDLではなく、検索設計そのもの** だという点です。どの列をembeddingするか、どの列をmetadataとして残すかで、後続の検索品質や使い勝手が大きく変わります。

たとえば、文書検索なら以下のような設計になります。

* `id`: 主キー
* `chunk_text`: embedding対象の本文
* `title`: 表示用メタデータ
* `category`: フィルタ用メタデータ
* `updated_at`: 新しさ判定や表示用メタデータ

このように、**検索のための列設計** を先に考えておくことが重要です。

### 2-3. Endpointを先に作る

Databricksでは、Vector Indexを使う前に **Vector Search Endpoint** を作成します。  
公式でも、Mosaic AI Vector Searchを使うには endpoint と index の両方が必要であり、endpoint が index を提供する役割を持つと説明されています。endpoint は index のサイズや同時リクエスト数に応じて自動でスケールします。

#### Endpointの役割

Endpointは、イメージとしては **「Vector Index専用の検索実行基盤」** です。  
アプリケーションやSDK、REST API、あるいはSQL関数から検索要求が来たときに、その要求を受けて実際にindexを検索します。

#### Endpoint作成時に意識すること

Databricks公式では、エンドポイントには **Standard** と **Storage-optimized** の考え方があり、性能・コスト・扱えるベクトル数の目安が異なります。コストガイドでは、Standard は 768次元換算で1ユニットあたり最大200万ベクトル、Storage-optimized は同条件で最大6400万ベクトルをカバーするとされています。

このため、PoC段階では次の観点を持っておくと設計しやすいです。

* **小〜中規模で低遅延を重視するか**
* **大規模データを効率よく持ちたいか**
* **同時アクセス数が多いか**
* **将来的に高QPSが必要か**

Databricksは高QPS向けの設定や負荷試験機能も提供しているため、本番運用を見据えるなら endpoint を先に性能観点で選ぶのが重要です。

Python SDKでのendpoint作成コード

`databricks-vectorsearch` をインストールし、`VectorSearchClient().create_endpoint(...)` を呼ぶ形です。

```
%pip install databricks-vectorsearch
dbutils.library.restartPython()
```

```
from databricks.vector_search.client import VectorSearchClient

# 自動でPATを使って認証
client = VectorSearchClient()

client.create_endpoint(
    name="my_vector_search_endpoint",
    endpoint_type="STANDARD"   # または "STORAGE_OPTIMIZED"
)
```

#### 何をしているか

* `name`  
  作成するVector Search Endpoint名
* `endpoint_type`  
  エンドポイント種別。`STANDARD` または `STORAGE_OPTIMIZED`。

高QPS向けの作成コード

リアルタイム検索や検索バー用途でQPSを高めたい場合、**Standard endpoint限定** で `min_qps` を指定できます。これはベータ機能で、追加容量を事前に確保するため、**実トラフィックに関係なくその分のコストが発生** します。

```
from databricks.vector_search.client import VectorSearchClient

client = VectorSearchClient()

client.create_endpoint(
    name="my_vector_search_endpoint_high_qps",
    endpoint_type="STANDARD",
    min_qps=500
)
```

Service Principalで認証する例

公式例では、Service Principal のクライアントID/シークレットを渡す形も示されています。

```
from databricks.vector_search.client import VectorSearchClient

client = VectorSearchClient(
    service_principal_client_id="<CLIENT_ID>",
    service_principal_client_secret="<CLIENT_SECRET>"
)

client.create_endpoint(
    name="my_vector_search_endpoint",
    endpoint_type="STANDARD"
)
```

#### 補足

* `min_qps` は **Standard endpointのみ**
* ベータ機能
* コスト増につながるため、本番要件があるときだけ使うのがよいです。  
  :::

### 2-4. Indexの作成方式は2つある

DatabricksのVector Indexには、実務上、まず **2つの作成方式** があると理解すると整理しやすいです。

* **Delta Sync Index**
* **Direct Access Index**

REST APIやCLIの説明でも、`DELTA_SYNC` は元のDelta tableと自動同期するindexとして定義されています。また、DatabricksのAgent連携ドキュメントでも、direct-access index と delta-sync index の両方が前提として登場します。

### 2-5. Delta Sync Indexとは何か

#### 概要

Delta Sync Indexは、**Deltaテーブルをソースとして、その内容を自動的・増分的にインデックスへ同期する方式** です。  
Databricks公式でも、基盤となるDelta table が更新されると index を自動同期できる構成として説明されています。

#### 向いているケース

この方式は、次のようなケースに向いています。

* 既にDatabricks上に文書やレコードを持っている
* Delta Lake を中心にRAG基盤を組みたい
* 元テーブル更新とインデックス更新の整合を保ちたい
* Lakehouseネイティブな構成にしたい

つまり、**Databricksで完結する標準的なRAG構成** にかなり相性がよい方式です。

#### 技術的なポイント

Delta Sync Indexでは、元のDelta tableが「検索対象の正」となります。  
そのため、検索基盤だけ別管理にするのではなく、**Delta tableの設計品質がそのまま検索品質と運用品質に効く** という特徴があります。

たとえば、次の観点が重要です。

* 主キーが一意であること
* embedding対象列が安定していること
* metadata列が適切に設計されていること
* 文書更新時のチャンク再生成方針が決まっていること

特にRAG用途では、本文を1レコード1文書で持つのか、チャンク単位で持つのかで検索性能と回答品質が変わるため、**Index作成前にデータモデリングを決める必要がある** のがポイントです。

### 2-6. Direct Access Indexとは何か

#### 概要

Direct Access Indexは、**アプリケーション側からベクトルやメタデータを直接書き込む方式** です。  
DatabricksのAgent向けドキュメントでも、Direct-access index は self-managed embeddings と組み合わせて使う前提が示されています。

#### 向いているケース

この方式は、次のようなケースに向いています。

* embeddingをDatabricks外で生成したい
* 外部の前処理パイプラインを持っている
* ベクトル更新をアプリ主導で制御したい
* Databricksを検索基盤として使いたいが、データ生成は別システムでやっている

つまり、**検索基盤としてDatabricksを使いつつ、データ投入制御はアプリ側で持ちたいケース** に向いています。

#### 技術的なポイント

Direct Access Indexでは、ベクトル生成・更新責任が利用者側に寄ります。  
そのため柔軟性は高い一方で、次の設計責任が増えます。

* embeddingモデルの選定
* 次元数の整合
* 再embedding時の置換方針
* metadata整備
* 更新順序や整合性管理

Databricks側がLakehouse同期を面倒見てくれるわけではないので、**自由度が高い代わりに運用設計が重くなる** と捉えると分かりやすいです。

### 2-7. managed embedding と self-managed embedding

Vector Index作成時に、もう1つ重要なのが **embeddingを誰が作るか** です。  
Databricks公式では、**managed Delta Sync index** で **custom embedding model** を使う話や、**self-managed embeddings** を前提とした **direct-access / delta-sync** の説明があり、embeddingの生成責任が選べることが分かります。

#### Databricks managed embeddings

Databricks側にembedding生成を寄せる形です。  
Databricks上で一貫して扱えるため、構成がシンプルになりやすく、PoCや標準構成に向いています。

#### Self-managed embeddings

利用者側でembeddingを生成して持ち込みます。  
既存のモデルや社内標準モデルを使いたい場合、あるいは埋め込み生成を別基盤で統一したい場合に向きます。

#### どちらを選ぶべきか

判断軸は次のように整理できます。

* **まず動かしたい** → managed embeddings
* **既存モデルを使いたい** → self-managed embeddings
* **検索と生成でモデル統一したい** → self-managed embeddings寄り
* **運用を簡素化したい** → managed embeddings

ここは単なる実装差ではなく、**モデル運用責任をどこに置くか** の設計判断です。

### 2-8. Index作成時に決める主要項目

実際にVector Indexを作るときは、概念的には次の項目を決めることになります。

**1. ソースデータ**  
どのDeltaテーブルを元にするか。  
Databricks公式では、Catalog Explorerから対象Delta tableを選択して index を作成するUI手順も案内されています。

**2. 主キー**  
レコードを一意に識別する列です。  
primary key はインデックス作成時の重要パラメータです。

**3. embedding対象列**  
どのテキストをベクトル化するかを決めます。  
本文全文なのか、チャンク化後の本文なのかで検索結果は大きく変わります。

**4. metadata列**  
検索結果として返す列や、filterに使う列です。  
カテゴリ、文書種別、作成日、製品名などを持たせると、後続の絞り込みがしやすくなります。filter や reranking が利用できることは query ドキュメントでも説明されています。

**5. embedding方式**  
Databricks managed にするか、自前生成にするかを決めます。

**6. endpoint種別**  
性能・コスト・規模に応じて選びます。

このように、Index作成は単なる「作成コマンド」ではなく、**検索対象データのモデリング + 実行基盤設計 + embedding運用設計** をまとめて決める行為です。

#### Index作成時に決める項目の関係

### 2-9. 作った後はどう使うのか

Indexを作成した後は、REST APIやSDKから検索できるほか、Databricks SQL の `vector_search()` 関数からも利用できます。 `vector_search()` は Databricks SQL で Mosaic AI Vector Search index をクエリするための関数として提供されています。

これは重要なポイントです。  
DatabricksのVector Indexは、単なるアプリ用の専用検索エンジンではなく、**Lakehouseの分析面やAgent連携面にも接続できる検索資産** として扱えます。

つまり、作って終わりではなく、

* アプリのRAG検索で使う
* AgentのRetrieverとして使う
* SQLから検索して評価・検証する

といった幅広い使い方につながります。Databricks managed MCP servers でも、Vector Search index をAIエージェント接続先として扱えることが公式に説明されています。  
[Use Databricks managed MCP servers](https://docs.databricks.com/aws/en/generative-ai/mcp/managed-mcp?utm_source=chatgpt.com)

### 2-10. 実務で押さえるべき設計上の注意点

#### ① まずデータ設計を決める

Index作成前に、文書をどう分割するか、何をmetadataに残すかを決める必要があります。  
ここが曖昧だと、indexは作れても検索品質が安定しません。

#### ② embedding生成責任を明確にする

Databricksに任せるのか、自前で持つのかで、運用負荷と柔軟性が大きく変わります。

#### ③ Endpointは性能要件から選ぶ

小規模PoCなら問題なくても、本番ではQPSやレイテンシ要件が効いてきます。Databricksも高QPSや負荷試験のガイドを出しているため、後からではなく先に見ておくのが安全です。

#### ④ Index作成を“検索基盤の実装”として捉える

DDLを1本打って終わりではなく、RAG品質を左右する設計工程 として扱うのが大事です。

QPSとは

QPSはVector Searchの設計でかなり重要なので、一般論だけでなく Databricks の endpoint 設計にもつながる形で整理します。意味、計算イメージ、レイテンシとの関係、Vector Searchでどこに効くかまで分かるようにまとめます。

QPS は **Queries Per Second** の略で、**1秒あたりにシステムが処理する問い合わせ数** を表す指標です。API、検索エンジン、データベース、ベクトル検索などで広く使われます。Databricks Vector Search でも、endpoint の処理能力を考えるうえで QPS が重要な設計指標になっています。  
[QPS management](https://developer.tomtom.com/platform/documentation/my-tomtom/qps-management?utm_source=chatgpt.com)

たとえば、1秒間に 50 件の検索リクエストを安定して処理できるなら、そのシステムは **50 QPS** です。10秒間で 500 リクエストを処理したなら、平均すると 50 QPS です。QPS は「瞬間的なピーク」と「一定時間の平均」で見え方が変わるため、本番設計では平均値だけでなくピーク時も見る必要があります。

技術的には、QPS は **スループット** の一種です。対になる概念が **レイテンシ** で、こちらは1件の処理に何秒・何ミリ秒かかるかを示します。一般に、同時に受けるリクエスト数が増えてスループットを上げていくと、平均レイテンシは悪化しやすくなります。

イメージとしては、  
**QPS = どれだけ多く捌けるか**  
**レイテンシ = 1件をどれだけ早く返せるか**  
です。  
この2つは似ていますが別物です。高QPSでも1件ごとの応答が遅いことはありえますし、低レイテンシでも大量アクセスに弱いことはあります。

Databricks Vector Search でQPSが重要になるのは、検索用途によって必要性能が大きく変わるからです。Databricksの現行ガイドでは、**Standard endpoint のデフォルトは index サイズに応じておおむね 20〜200 QPS**、一方で検索バーや推薦、エンティティ照合のようなリアルタイム用途では **100〜1000+ QPS** が必要になることがあると説明されています。

式としてはかなり単純で、概算なら  
`QPS ≒ 一定時間内の総リクエスト数 ÷ 秒数`  
です。

たとえば1分間に 3,600 回検索されるなら、平均 QPS は 60 です。実務ではこの平均値に加えて、ピーク時の揺れ、同時接続、検索条件の重さ、top\_k、フィルタ、reranking の有無まで見る必要があります。Databricks も性能は単一数値ではなく、**ワークロード特性・構成・クライアント実装に依存する範囲** と説明しています。

## 第3章 検索時に内部で何が起きているのか

Databricks Vector Search の検索処理は、細かく見ると多機能ですが、記事として押さえるべき本質は次の3つです。

1. **クエリを受け取る**
2. **Indexから近い候補を探す**
3. **必要に応じて絞り込み・並び替えをして返す**

Databricks公式でも、検索時は `query_text` または `query_vector` を入力に使え、既定の検索方式は **ANN（Approximate Nearest Neighbor）** です。さらに **filter** や **reranking**、`query_type="hybrid"` によるハイブリッド検索も使えます。

ANN（Approximate Nearest Neighbor）とは

ANN（Approximate Nearest Neighbor）とは、ベクトル検索において、最も近いデータを厳密に総当たりで探すのではなく、十分に近い候補を高速に見つけるための近似探索手法である。

`ベクトル検索では、全データと総当たりで距離計算すると遅くなるため、ANNを使って検索速度を大きく上げます。`  
`その代わり、理論上の最適解を100%保証するより、実用上ほぼ十分な近い候補を速く返すことを重視します。`

### 3-1. 全体像

**この図の意味**  
検索時は、まず質問文またはベクトルを受け取り、その後 **Vector Index から近い候補を探し**、必要があれば **metadata filter** や **reranking** を適用し、最後に **文書とメタデータ** を返します。Databricksのクエリ仕様でも、`query_text` / `query_vector`、既定の `ann`、`hybrid`、`filters`、`reranking` が案内されています。

**重要なのは次の3点**

* **入力は** `query_text` **か** `query_vector`
* **検索の中心は ANN による候補探索**
* **実務では metadata filter と reranking が効く**

### 3-2. 検索時の主要ポイント

| 項目 | 何が起きるか | 重要ポイント |
| --- | --- | --- |
| **入力** | `query_text` または `query_vector` を受け取る | text入力なら検索前にベクトル化が必要 |
| **候補探索** | Indexから近い候補を探す | 既定は **ANN** |
| **絞り込み** | metadata条件でfilterする | 業務検索ではかなり重要 |
| **並び替え** | rerankingで順位を調整する | 上位数件の精度を上げたいときに有効 |
| **返却** | 文書チャンクやmetadataを返す | LLMやアプリが使うのはベクトルではなく文書 |

Databricks公式では、既定の `query_type` は `ann` で、`hybrid` を指定するとキーワード検索と類似検索を組み合わせられます。また、クエリ時に filters と reranking を利用できます。

### 3-3. 読者が理解すべき3点だけ押さえる

#### ① 入力は text か vector

検索時の入力は、**自然言語の質問** か **埋め込みベクトル** のどちらかです。  
`query_text` を使うと扱いやすく、`query_vector` は自前でembeddingを作っている場合に向きます。Databricks SQL の `vector_search()` でも、`query_text` または `query_vector` を使う形です。

#### ② 本体は「近い候補を探す処理」

検索の中心は、Vector Index 内から **近い候補を高速に見つける** 処理です。  
Databricksでは既定が **ANN** なので、厳密総当たりではなく、実用上十分に近い候補を高速に取得する考え方です。

#### ③ 実務では filter が重要

ベクトル類似度だけでは、意味は近いが業務的には不要な結果が混ざることがあります。  
そのため、**category や date などの metadata で絞る** のが重要です。Databricksでも、filter は主要機能として提供されています。

## 第4章 運用で押さえるべき設計ポイント

### 4-1. 全体像

Vector Indexは作って終わりではありません。  
運用では、特に次の4点を抑えることが重要です。

運用では、単に「検索できるか」ではなく、  
**速く返せるか**、**コストに見合うか**、**欲しい文書が返るか**、**更新に追従できるか**  
を見ていく必要があります。

### 4-2. 重要ポイント一覧

| 観点 | 何を見るか | 重要ポイント |
| --- | --- | --- |
| **性能** | 応答時間、QPS、同時利用数 | `top_k` や filter 条件で負荷が変わる |
| **コスト** | Endpointサイズ、保持データ量 | データ量とアクセス量の両方で考える |
| **検索品質** | 欲しい文書が上位に来るか | chunk設計と metadata設計が重要 |
| **更新運用** | データ更新への追従 | Delta Sync か Direct Access かで運用負荷が変わる |

### 4-3. 設計でまず押さえるべきこと

#### ① 性能は `top_k` とアクセス量で大きく変わる

検索性能は、単にIndex件数だけでなく、**1秒あたりの検索件数** や **何件返すか** に左右されます。特に `top_k` を大きくしすぎると、返却量や後段処理が重くなりやすいため、必要最小限に絞るのが基本です。

#### ② コストは「保存量」だけでなく「使い方」で決まる

Vector Search のコストは、単に文書件数だけではなく、**どの程度の頻度で検索されるか、どの規模のEndpointを使うか** でも変わります。  
そのため、PoCではまず小さく始め、実アクセス量を見て調整するのが安全です。

#### ③ 品質はIndex作成時点でかなり決まる

検索品質を上げたい場合、まず見るべきはモデルよりも **データの持ち方** です。  
たとえば次の点が重要です。

* 文書をどの粒度で chunk 化するか
* title / category / date などの metadata を持たせるか
* filter を使える設計になっているか

つまり、検索品質は「検索時」だけでなく、**Index設計時のデータモデリング** に強く依存します。

#### ④ 更新運用は方式選択そのもの

運用で意外に重要なのが、**更新をどう回すか** です。  
Delta Sync を使えば Lakehouse と一体で運用しやすくなりますが、Direct Access は柔軟な代わりに自前管理が増えます。  
ここは単なる実装差ではなく、**誰が更新責任を持つか** の違いです。

### 4-4. 実務での見方

運用設計では、次のように考えると整理しやすいです。

PoCでは、この4点を最低限確認すると、「検索できた」だけで終わらず、実運用に耐えるかを判断しやすくなります。

### 4-5. この章で押さえる結論

Databricks Vector Search の運用で重要なのは、**性能・コスト・品質・更新運用** の4点です。

特に重要なのは次の3つです。

* `top_k` **やQPSを含めた性能設計**
* **chunk と metadata を含めた品質設計**
* **Delta Sync / Direct Access の運用責任の違い**

つまり、Vector Index の運用は単なる検索機能の管理ではなく、  
**検索基盤としての設計・評価・更新を継続すること** だと捉えるのが重要です。

## 第5章 RAG・AIエージェントでどう使うのか

Databricks Vector Index は、単体で使うというより、**RAGやAIエージェントの検索層** として使うと価値が出やすいです。Databricks公式でも、RAGは **LLMに対して外部データを検索・取得してから回答生成する方式** と説明されており、Vector Searchはその検索部分を担います。  
[RAG (Retrieval Augmented Generation) on Databricks](https://docs.databricks.com/aws/ja/generative-ai/retrieval-augmented-generation)

### 5-1. 全体像

#### この図の意味

RAGでは、最初にLLMへ直接質問するのではなく、まず **Retriever** が関連文書を探します。  
Databricksでは、この Retriever の実装として **Vector Search index** を使えます。検索で得た文書チャンクをLLMへ渡すことで、より正確で最新の回答を返しやすくなります。Databricksは、AIエージェントを Vector Search index や外部ベクトルストアの非構造化データへ接続する複数の方法を提供しています。

### 5-2. RAGとAIエージェントでの使い方

| 使い方 | Vector Index の役割 | ポイント |
| --- | --- | --- |
| **RAG** | 関連文書を検索してLLMへ渡す | 回答精度や最新性の向上に効く |
| **AIエージェント** | 知識検索ツールとして使う | エージェントが必要なときだけ検索できる |
| **Databricks SQL / 関数連携** | Retriever を SQL / UC関数として使う | Lakehouseの中で再利用しやすい |
| **MCP連携** | Agentから安全に検索ツールとして呼ぶ | Databricks管理の接続形態がある |

Databricksの現行ドキュメントでは、Vector Search index は RAG、セマンティック検索、推薦などの用途に使えると説明されています。また、AIエージェント向けには **managed MCP servers** や **Unity Catalog関数**、**AI Bridge packages** を使った接続方法が案内されています。

### 5-3. 読者が理解すべき3点だけ押さえる

#### ① RAGでは「検索してから答える」

RAGは、LLMに知識を全部持たせるのではなく、**質問のたびに必要な文書を検索してから回答する** 方式です。Databricksでも、RAGは proprietary、frequently changing、domain-specific な情報に有効だと説明されています。つまり、社内文書や更新の多い情報と相性がよいです。

#### ② Vector Indexは「知識検索の入口」

Vector Index 自体が回答するわけではありません。  
役割は、**質問に関連する文書チャンクを探して返すこと** です。LLMやAgentは、その結果を受けて最終回答を生成します。DatabricksのVector Searchは、類似ベクトルを見つけて関連文書を返す仕組みとして説明されています。

#### ③ AIエージェントでは「必要なときだけ検索するツール」になる

AIエージェントでは、Vector Searchは単なる固定検索ではなく、**ツール呼び出しの1つ** として使われます。Databricksは、Vector Search index を **managed MCP server** 経由でエージェントから利用できるようにしており、Unity Catalog権限も適用されます。つまり、エージェントが必要なタイミングで安全に知識検索できる構成が取りやすいです。

### 5-4. 実務での見方

この図のように、Databricks Vector Index は**RAG専用機能** というより、  
**検索資産を複数の入り口から使える形にしたもの** と捉えると分かりやすいです。Databricks公式でも、Vector Search index は REST API、SQL、Agent向けツール接続など複数の利用方法に広がっています。

### 5-5. この章で押さえる結論

Databricks Vector Index は、RAGやAIエージェントにおいて **知識検索の中核** を担います。  
RAGでは関連文書をLLMへ渡すための Retriever になり、AIエージェントでは必要なときだけ使う検索ツールになります。さらに Databricks では、SQL、Unity Catalog関数、MCP など複数の接続手段があるため、**Lakehouseの中で検索基盤を再利用しやすい** のが強みです。
