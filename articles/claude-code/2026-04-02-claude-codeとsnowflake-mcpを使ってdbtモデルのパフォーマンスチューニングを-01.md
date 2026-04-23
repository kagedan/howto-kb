---
id: "2026-04-02-claude-codeとsnowflake-mcpを使ってdbtモデルのパフォーマンスチューニングを-01"
title: "Claude CodeとSnowflake MCPを使って、dbtモデルのパフォーマンスチューニングを自動化した話"
url: "https://zenn.dev/dely_jp/articles/9962b33ad86bc3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

# はじめに

こんにちは、クラシル社のレシチャレBUのKOHです。  
データエンジニアをしています。  
  
突然ですが、データエンジニアの業務は幅広いです。

* **パイプライン構築** — ソースからDWHへのデータ取り込み・変換
* **データモデリング** — スタースキーマ設計、ファクト/ディメンション構築
* **データ品質** — テスト実装、異常値検知
* **コスト管理** — Snowflakeクレジットの監視・最適化
* **BI連携** — Lightdash等へのデータ提供
* **パフォーマンスチューニング** — 遅いクエリの原因特定と改善

この中でもチューニングは、Snowflakeのアーキテクチャや原理原則を知っていないといけない専門性が求められることがあります。今回はMCPからクエリプロファイルを取得して、Agenticにチューニングを行う手法を共有します。

## この記事で話すこと

dbtモデル名を渡すとボトルネック箇所の特定と、クエリのチューニングまでを一貫で行うskill(query-profile)を作成しました。  
  
以下を使用していきます。

* Claude Code
* Snowflake MCP
* QUERY\_HISTORY
* GET\_QUERY\_OPERATOR\_STATS関数

以下、詳細を記していきます。  
  
Snowflake MCPとClaude Codeについては、  
  
<https://zenn.dev/dely_jp/articles/snowflake-managed-mcp-claude-code-agentic-dataops>  
こちらも合わせてご覧ください！！ 以下、詳細を記していきます。

## Snowflakeのクエリプロファイル取得

チューニングの第一歩は「何が遅いのか」の特定です。Snowflakeでは以下の2ステップで分析します。

1. `QUERY_HISTORY` からクエリの実行履歴を取得し、`QUERY_ID` を特定する
2. その `QUERY_ID` を `GET_QUERY_OPERATOR_STATS` に渡して、オペレーターレベルの実行プロファイルを取得する

それぞれ見ていきます。

### QUERY\_HISTORY — 実行履歴の取得

`SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY` から、対象モデルの実行時間・スキャン量・スピル量等のサマリーを取得します。

```
SELECT
    QUERY_ID,
    TOTAL_ELAPSED_TIME,
    BYTES_SCANNED,
    PARTITIONS_SCANNED,
    PARTITIONS_TOTAL,
    BYTES_SPILLED_TO_LOCAL_STORAGE,
    BYTES_SPILLED_TO_REMOTE_STORAGE,
    PERCENTAGE_SCANNED_FROM_CACHE
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE QUERY_TEXT ILIKE '%target_model_name%'
  AND QUERY_TYPE = 'SELECT'
  AND START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY START_TIME DESC
LIMIT 20;
```

ここで取得した `QUERY_ID` を次のステップで使います。

### GET\_QUERY\_OPERATOR\_STATS — オペレーターレベルのプロファイル

`QUERY_HISTORY` はクエリ全体のサマリーです。「どの部分が遅いか」を特定するには、オペレーターレベルの統計が必要です。

```
SELECT
    OPERATOR_ID,
    OPERATOR_TYPE,
    OPERATOR_STATISTICS,
    EXECUTION_TIME_BREAKDOWN,
    OPERATOR_ATTRIBUTES
FROM TABLE(GET_QUERY_OPERATOR_STATS('xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'))  -- query_idを指定
;
```

WebコンソールのクエリプロファイルをSQL経由で取得できる関数です。

`OPERATOR_STATISTICS` はVARIANT型（JSONオブジェクト）で、以下のような構造を持ちます。

```
// TableScan オペレーターの例
{
  "io": {
    "bytes_scanned": 8589934592,
    "percentage_scanned_from_cache": 0.05,
    "bytes_written": 0,
    "bytes_written_to_result": 0
  },
  "pruning": {
    "partitions_scanned": 450,
    "partitions_total": 500
  },
  "input_rows": 0,
  "output_rows": 5200000
}

// Join オペレーターの例
{
  "spilling": {
    "bytes_spilled_local_storage": 1073741824,
    "bytes_spilled_remote_storage": 0
  },
  "input_rows": 5200000,
  "output_rows": 12000000
}

// Aggregate オペレーターの例
{
  "input_rows": 12000000,
  "output_rows": 350000
}
```

`EXECUTION_TIME_BREAKDOWN` はクエリ全体に対する各オペレーターの時間配分を比率で返します。

```
{
  "overall_percentage": 0.45,
  "processing": 0.12,
  "local_disk_io": 0.28,
  "remote_disk_io": 0.03,
  "network_communication": 0.01,
  "synchronization": 0.01,
  "initialization": 0.00
}
```

これらの値から、「TableScanが全体の45%を占めていて、パーティションの90%をスキャンしている → プルーニングが効いていない」といった判断ができます。

### 分析フロー

```
QUERY_HISTORY → QUERY_ID 特定 → GET_QUERY_OPERATOR_STATS → ボトルネック特定 → 改善
```

この一連の流れを、前述の `/query-profile` スキルで自動化しています。以下でスキルの詳細を見ていきます。

## `/query-profile` の全体像

モデル名を渡すだけで分析が走ります。

```
/query-profile <model_name>          # デフォルト: 過去7日間
/query-profile <model_name> 30       # 過去30日間
```

### 分析ステップ

**ステップ1: SQLファイル読み取り** — モデルのSQL/YAMLを取得し静的解析に使用

**ステップ2: クエリ履歴取得** — `QUERY_HISTORY` からBIツール経由のSELECTクエリを収集。日別トレンドも集計

**ステップ2.5: オペレーター分析** — `GET_QUERY_OPERATOR_STATS` でボトルネックを特定

| 情報 | フィールド | HIGH判定 |
| --- | --- | --- |
| I/O | `bytes_scanned` | 10GB以上 |
| プルーニング | `partitions_scanned / partitions_total` | 80%以上（total≥100） |
| スピル | `bytes_spilled_remote_storage` | 0より大きい |
| 実行時間 | `overall_percentage` | 30%以上 |

**ステップ3: 27項目のアンチパターンチェック** — 3つの情報ソースを横断してチェック

**ステップ4: レポート出力** — 構造化されたレポートを生成

### 27項目のチェックリスト（抜粋）

事前に27個のチェックリストを作成しました。  
  
SQL静的解析・クエリ履歴・オペレータープロファイルの3ソースを横断して、作成したチェックリストを確認します。代表的なものを抜粋します。

| カテゴリ | チェック内容 | ソース | 重要度 |
| --- | --- | --- | --- |
| プルーニング | パーティションスキャン率 80%以上（total≥100） | Profile | HIGH |
| スキャン量 | TableScanで 10GB以上スキャン | Profile | HIGH |
| スピル | リモートスピル発生 | 履歴+Profile | HIGH |
| JOIN | CROSS JOINまたは条件なし結合 | SQL | HIGH |
| JOIN | Join実行時間30%以上またはスピル発生 | Profile | HIGH |
| Incremental | Incrementalだが日付フィルタなし | SQL | HIGH |
| 構造 | 3段以上のCTE多段集計 | SQL | HIGH |
| 構造 | 全期間毎回再計算 | SQL | HIGH |

### 改善パスの振り分け

チェック結果から、4つの改善パスに振り分けます。

| パス | 条件 |
| --- | --- |
| **A. クエリチューニング** | SQLの書き換えで解決 |
| **B. 既存dim/fct切り替え** | stg直参照→既存コンポーネントに置換 |
| **C. 新規dim/fct作成** | 対応コンポーネントが未存在 |
| **D. アーキテクチャ再設計** | SQL書き換えでは根本解決しない |

### 出力レポートの例

```
## Query Profile: adhoc__XX

### 基本情報
- マテリアライゼーション: view
- ウェアハウスサイズ: デフォルト(M)
- 分析期間: 過去7日

### クエリプロファイル（オペレーター統計）
| Operator ID | Type | 実行時間比率 | 出力行数 | スキャン量 | 備考 |
|-------------|------|------------|---------|-----------|------|
| 1 | **TableScan** | **45%** | 5.2M | 8.5 GB | ほぼフルスキャン |
| 3 | Join | 25% | 12M | - | ファンアウト発生 |
| 5 | Aggregate | 20% | 350K | - | スピル 1.2GB |

### ボトルネック分析
#### HIGH
- [プルーニング] PARTITIONS_SCANNED/TOTAL = 90% → 日付フィルタ追加を推奨
- [スピル] Aggregateでローカルスピル 1.2GB → WHサイズをLに増を検討

#### MEDIUM
- [構造] stg_を直接参照 → 既存dim/fctへの切り替え候補あり

### 改善提案サマリー
1. [HIGH] 日付フィルタ追加（lookback: 60日）
2. [HIGH] ウェアハウスサイズ調整（M → L）
3. [MEDIUM] stg_XX → fct__XX に切り替え
```

## 工夫したポイント

### CTE統合の罠

同一テーブルの複数TableScanを「CTEにまとめよう」は自然な発想ですが、Snowflakeでは**逆効果**になるケースがあります。

1. **フィルタ条件が異なる場合** — 和集合のスキャンでデータ量増加
2. **JoinFilter喪失** — Snowflakeの事前フィルタ最適化が無効化
3. **CTE実体化スピル** — 大量CTEが複数参照されるとメモリ溢れ

| 条件 | CTE統合 |
| --- | --- |
| フィルタ条件が同一 | 推奨 |
| フィルタ条件が異なる | **非推奨** |
| 10GB以上 × 3回以上スキャン | **非推奨** |
| 1GB未満 | 推奨 |

### パーティションプルーニングが効かないパターン

| フィルタ方式 | プルーニング |
| --- | --- |
| リテラル: `WHERE col >= '2025-01-01'` | 有効 |
| DATEADD: `WHERE col >= DATEADD('day', -365, CURRENT_DATE())` | 有効 |
| Scalar Subquery: `WHERE col >= (SELECT MIN(ts) FROM cte)` | **無効** |
| CTE由来: `WHERE col >= cte.min_date` | **無効** |

Snowflakeはコンパイル時に値を確定できない式ではプルーニングが効きません。

## 実装構成

`.claude/skills/` 以下のような構成でskillを作成しました。

```
.claude/skills/query-profile/
├── SKILL.md                     # 手順定義
└── references/
    ├── query_profile_guide.md   # OPERATOR_STATSの読み方
    ├── sql_query_template.md    # クエリテンプレート集
    └── report_template.md       # レポートテンプレート
```

SnowflakeへのクエリはMCPサーバー経由で実行します。

ポイントは**ドメイン知識の埋め込み**です。27項目のチェックリスト、判定閾値、CTE統合の注意事項など、すべて過去のチューニング経験から抽出したナレッジをMarkdownに記述しています。

## 参考: GET\_QUERY\_OPERATOR\_STATS の読み方

### ボトルネックオペレーター

`overall_percentage` が高いオペレーターから確認します。

| オペレーター | 対策 |
| --- | --- |
| TableScan | プルーニング改善、不要カラム除外 |
| Join | 結合条件最適化、事前フィルタ |
| Aggregate/Sort | GROUP BY見直し、事前集計 |
| WindowFunction | 関数統合、PARTITION BY見直し |

### スピル発生箇所

* **Join** → WHサイズ増 or 結合前データ削減
* **Aggregate** → GROUP BYのカーディナリティが高すぎる
* **Sort** → 大量データのORDER BY

### データ膨張

* Join: `output_rows >> input_rows` → ファンアウト（多対多結合）
* Filter: `output_rows << input_rows` → JOIN前にフィルタ移動を検討

## 最後に

冒頭で"データエンジニアの仕事"について触れましたが、今後ますますAIの進歩で、従来やるべきだった仕事が楽になっていくと思います。  
  
現在クラシルのデータチームは2人ですので、"本当にやるべきこと"に注力すべく、より一層活用を進めていきます。
