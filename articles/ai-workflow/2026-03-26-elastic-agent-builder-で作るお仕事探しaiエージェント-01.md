---
id: "2026-03-26-elastic-agent-builder-で作るお仕事探しaiエージェント-01"
title: "Elastic Agent Builder で作る、お仕事探しAIエージェント"
url: "https://zenn.dev/ozeshun/articles/fdef731277684e"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

こんにちは。株式会社タイミーで Data Scientist をしている小関 ([@ozeshun](https://x.com/ozeshun_))です。  
先日、[Elastic{ON} Tokyo 2026](https://www.elastic.co/events/elasticon/tokyo) に参加しました。そこで [Elastic Agent Builder](https://www.elastic.co/docs/explore-analyze/ai-features/elastic-agent-builder) が気になり、実際に触ってみました。

## 1. はじめに

Elastic Stack 9.3 で GA となった Elastic Agent Builder を使い、求人を自然言語で探せる「お仕事探しAIエージェント」を構築してみました。  
Kibana の UI 操作だけで、以下のようなやりとりができるエージェントが作れます。

#### 対話イメージ

```
> ユーザー: 新宿で明日働ける4000円以上の飲食系の仕事ある？

> エージェント:
新宿駅周辺（1km以内）で明日働ける飲食系のお仕事を探しました！

① 居酒屋のランチ営業スタッフ募集！
📍 新宿駅から約0.8km
💰 報酬 4,200円
📅 2026/03/25 10:00〜13:00
⏱️ 3時間
🏷️ 飲食
📝 ランチタイムの接客・配膳業務。未経験歓迎、まかない付き。

(他にも何件かお仕事を列挙)

他にもxx件あります。条件を絞りますか？
```

#### システム構成

```
[ユーザー]
  ↓ 自然言語で質問
[お仕事探しアシスタント]
  ↓ 意図解析 & Tool 選択
  ├─ 求人フリーワード検索（Index Search Tool）
  ├─ 条件指定求人検索（ES|QL）
  └─ エリア指定求人検索（ES|QL）
  ↓ クエリ実行
[Elasticsearch: job_index]
  ↓ 結果返却
[エージェントが自然言語で回答を生成]
  ↓
[ユーザー]
```

## 2. Elastic Agent Builder とは

Elastic Agent Builder は、Elasticsearch のデータに対して自然言語で問い合わせできる AI エージェントを構築・管理する機能です。Elastic Stack 9.3 で GA になりました。  
主要コンポーネントは下記3つです。

| コンポーネント | 役割 |
| --- | --- |
| Agent Chat | エージェントと自然言語でやりとりするチャットインターフェース。Kibana UI のほか、API 経由での利用も可能 |
| Agent | LLM + Custom Instructions + Tool で構成される。ユーザーの質問を解釈し、Tool を使ってデータを取得し、回答を生成する |
| Tool | エージェントがデータにアクセスするための道具。[Index Search Tool](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/index-search-tools)（LLM がクエリを自動生成）, [ES|QL Tool](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/esql-tools)（定義済みクエリを実行）, [MCP Tool](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/mcp-tools), [Workflow Tool](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/workflow-tools)（執筆時点では Preview 機能） の4種類ある |

## 3. 構築手順

### 前提

* Elasticsearch（9.3+）と Kibana が稼働済み
* LLM コネクタが設定済み
  + 今回は、Claude Sonnet 4.5 を使用しました
* 求人情報は、`job_index` に投入済みであり、データ構造は下記のようになっています

  | フィールド | 型 | 内容 |
  | --- | --- | --- |
  | `job_id` | long | 求人ID |
  | `title` | text | 求人タイトル |
  | `description` | text | 求人本文（kuromoji アナライザー対応） |
  | `salary` | integer | 1勤務あたりの報酬総額 |
  | `working_hours` | float | 勤務時間（hours） |
  | `start_at` / `end_at` | date | 勤務開始・終了時間（UTC） |
  | `category` | keyword | 職種カテゴリ |
  | `area` | keyword | 勤務エリア |
  | `location` | geo\_point | 勤務地の緯度経度 |
  | `is_available` | boolean | 現在応募可能か |

Kibana → Agents → Tools → New tool から、Tool を3つ作成しました。  
今回は、Index Search, ES|QL ベースの Tool を用意しました。

最も手軽な Tool です。検索クエリをエージェントが自動生成してくれるので、定義する側はインデックスを指定するだけです。

| 項目 | 値 |
| --- | --- |
| Type | Index search |
| Tool ID | `search_job_freetext` |
| Target pattern | `job_index` |
| Maximum rows | `任意の値` |

Index Search Tool は、エージェントがインデックスのマッピングを自動で探索し、クエリを動的に生成します。曖昧な質問に強い一方で、意図しないクエリが生成される可能性もあります。そのため、Description に「必ず適用したい条件」を明示しておくと安心です。

Description 例:

```
現在応募可能な求人 (`is_available=True`) のみを返してください。
結果にはtitle, description, salary, working_hours, start_at, end_at, category, area を含めてください。
```

キーワード・最低報酬額・日付範囲を組み合わせて絞り込む ES|QL Tool です。  
日本語テキストを検索する場合は、アナライザーが適用されたフィールドに対して MATCH を使うのが良さそうです。

| 項目 | 値 |
| --- | --- |
| Type | ES|QL |
| Tool ID | `search_job_by_conditions` |

パラメータ（すべて Required）:

| Name | Type | Description |
| --- | --- | --- |
| `search_terms` | text | 検索キーワード（仕事内容やタイトル） |
| `min_salary` | integer | 最低報酬額（円）。指定なしなら 0 |
| `start_date` | date | 検索範囲の開始日時（UTC）。指定なしなら 2000-01-01T00:00:00.000Z |
| `end_date` | date | 検索範囲の終了日時（UTC）。指定なしなら 2099-12-31T23:59:59.000Z |

ES|QL クエリ例:

```
FROM job_index
| WHERE is_available == true
  AND MATCH(description, ?search_terms)
  AND salary >= ?min_salary
  AND start_at >= ?start_date
  AND start_at <= ?end_date
| KEEP job_id, title, description, salary, working_hours, start_at, end_at, category, area
| SORT start_at ASC
| LIMIT 10
```

Description 例:

```
キーワード・報酬額・日付で求人を絞り込みます。
すべての条件を同時に指定できます。
- キーワードのみ → min_salary=0, start_date=2000-01-01T00:00:00.000Z, end_date=2099-12-31T23:59:59.000Z
- 日付のみ → search_terms に「仕事」など汎用的なワードを入れてください
- 両方指定 → そのまま全パラメータを設定
```

ES|QL の ST\_DISTANCE 関数と geo\_point 型フィールドを使った距離検索を行う ES|QL Tool です。  
この Tool の面白いところは、ユーザーが「新宿で」と言ったとき、エージェントが事前知識から座標を推定し、パラメータとして渡す点です。主要な駅・地名であれば十分な精度で動作しました。

| 項目 | 値 |
| --- | --- |
| Type | ES|QL |
| Tool ID | `search_job_by_location` |

パラメータ（すべて Required）:

| Name | Type | Description |
| --- | --- | --- |
| `longitude` | double | 経度 |
| `latitude` | double | 緯度 |
| `radius_meters` | integer | 検索半径（メートル） |

ES|QL クエリ例:

```
FROM job_index
| WHERE is_available == true
  AND ST_DISTANCE(location, TO_GEOPOINT(CONCAT("POINT(", TO_STR(?longitude), " ", TO_STR(?latitude), ")"))) <= ?radius_meters
| EVAL distance_km = ST_DISTANCE(location, TO_GEOPOINT(CONCAT("POINT(", TO_STR(?longitude), " ", TO_STR(?latitude), ")"))) / 1000
| KEEP job_id, title, description, salary, working_hours, start_at, end_at, category, area, distance_km
| SORT distance_km ASC
| LIMIT 10
```

Description 例:

```
指定した地点の近くにある求人を距離順で検索します。
ユーザーが「新宿で」「渋谷駅の近くで」「池袋駅周辺で」など場所を指定した場合に使ってください。
【座標の求め方】
ユーザーが指定した地名・駅名から、あなたの知識を使って経度と緯度を推定してください。
【radius_meters の目安】
場所によって適切な検索半径は異なるので以下の情報を参考にしてください。
■ 都市部（東京23区、大阪市、名古屋市、横浜市、福岡市など）
- 「駅近で」「駅の近くで」→ 1000m
- 「○○で」（エリア名）→ 2000m
- 「○○周辺で」「○○あたりで」→ 3000m

■ 地方都市（県庁所在地クラス: 仙台、広島、札幌、盛岡、金沢など）
- 「駅近で」「駅の近くで」→ 1000m
- 「○○で」（エリア名）→ 3000m
- 「○○周辺で」「○○あたりで」→ 5000m

■ 郊外・地方（上記以外の市町村、郊外エリア）
- 「駅近で」「駅の近くで」→ 3000m
- 「○○で」（エリア名）→ 5000m
- 「○○周辺で」「○○あたりで」→ 8000m

判断に迷う場合は、まず狭い半径で検索し、結果が0件なら自動的に半径を広げて再検索してください。
```

### 3-2. カスタムエージェントの作成

Kibana → Agents → New agent でエージェントを作成し、上記3つの Tool を割り当てます。  
エージェントの振る舞いは Custom Instructions で定義します。今回設定した内容のポイントは以下です。

##### データの理解を教える

Custom Instructions にフィールドの意味や計算方法を明示することで、エージェントが正しくデータを解釈できるようになります。

```
- salary は1勤務あたりの報酬総額です。
- start_at / end_at はUTCです。日本時間（JST = UTC+9）に変換して表示してください。
```

##### Tool 選択の基準を指示する

複数の Tool を割り当てた場合、エージェントがどの Tool を使うべきかの判断基準を明示しておくことが重要です。

```
1. 場所が指定されている（駅名・地名）→ エリア指定求人検索
2. 日付や報酬など具体条件がある → 条件指定求人検索
3. それ以外（曖昧・フリーワード）→ 求人フリーワード検索
```

##### 回答フォーマットを指定する

出力の見た目も Custom Instructions で制御できるので、フォーマットを明示しておくと、回答品質が安定します。

```
検索結果は以下のように表示してください:

① [title]
📍 [エリア]（距離情報があれば「○○駅から約○.○km」）
💰 報酬 [salary]円
📅 [日時をJSTで表示]
⏱️ [勤務時間]
🏷️ [職種カテゴリ]
📝 [仕事の特徴を1行で要約]
```

## 4. 今後の展望

今回構築したエージェントは「聞かれたら検索する」という受動的な仕組みですが、「ユーザーの好みを学習したパーソナライズされたエージェント」への発展も考えられます。  
現状のエージェントは会話が終わるとユーザーの好みを忘れてしまいますが、Elasticsearch をメモリストアとして活用すれば、セッションをまたいだ「長期記憶」を持つエージェントが構築可能です。

Elastic 公式ブログの [AI agent memory: Creating smart agents with Elasticsearch managed memory](https://www.elastic.co/search-labs/blog/ai-agent-memory-management-elasticsearch) で、エージェントのメモリ管理アーキテクチャが紹介されていました。  
これを本ユースケースに当てはめると、以下のような段階的な拡張が考えられます。

### Step 1: 過去の検索傾向の参照

ユーザーの検索履歴を Elasticsearch のインデックスに記録しておき、ES|QL Tool で読み取ってエージェントのコンテキストに注入する。  
検索履歴の読み取りは、今回作成したものと同じ ES|QL Tool をもう1つ追加するだけで対応できます。

```
[ユーザー] 「なんかいい仕事ない？」
     ↓
[エージェント]
  1. メモリ検索 Tool で過去の好みを取得
     → 「渋谷周辺の飲食系をよく検索している」
     → 「報酬4000円以上を条件にすることが多い」
  2. 好みに基づいて求人検索 Tool を呼び出し
  3. パーソナライズされた結果を返す
```

### Step 2: 好みの自動学習

エージェントが会話の中で把握した好み（エリア、職種、報酬帯）を、自動でメモリ用インデックスに書き込むようにします。実現方法としては、MCP Tool で外部サーバー経由にするか、Elastic Workflows を使う方法が考えられます。  
semantic\_text 型を使えば、「この人は以前どんな仕事に興味を持っていたか」をベクトルベースで意味的に検索することもできそうです。

## We’re hiring!

**現在、タイミーではデータサイエンスやエンジニアリングの分野で、共に成長し、革新を推し進めてくれる新たなチームメンバーを積極的に探しています！**  
<https://product-recruit.timee.co.jp/data>

また、気軽な雰囲気での[カジュアル面談](https://product-recruit.timee.co.jp/casual)も随時行っておりますので、ぜひお気軽にエントリーしてください。↓  
<https://hrmos.co/pages/timee/jobs/16822514041183191753>  
<https://hrmos.co/pages/timee/jobs/16822514041183191878>  
<https://hrmos.co/pages/timee/jobs/16822514041183191879>
