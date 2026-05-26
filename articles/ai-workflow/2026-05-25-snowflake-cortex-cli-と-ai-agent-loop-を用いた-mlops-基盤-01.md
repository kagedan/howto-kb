---
id: "2026-05-25-snowflake-cortex-cli-と-ai-agent-loop-を用いた-mlops-基盤-01"
title: "Snowflake Cortex CLI と AI Agent Loop を用いた MLOps 基盤構築"
url: "https://zenn.dev/sirok/articles/13bcaed37f893c"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-05-25"
date_collected: "2026-05-26"
summary_by: "auto-rss"
query: ""
---

# Snowflake Cortex CLI と AI Agent Loop を用いた MLOps 基盤構築

## はじめに

近年、会社の成長に伴い、

など、データや機械学習を活用した施策への需要が高まっています。

しかし一方で、社内にはまだ ML や MLOps の知見・運用基盤が十分に整備されておらず、  
モデル構築や運用を継続的に行うハードルが高いという課題がありました。

そこで今回は、会社の KPI や業務要件に応じて、

までを自動的に実行できる MLOps 基盤を構築しました。

また、この基盤は従来の Pipeline 中心の MLOps とは異なり、  
多くの処理を AI Agent ベースで動作させる構成にしています。

これにより、

* Workflow の柔軟性向上
* 動的な意思決定
* 要件変更への追従性向上

を実現しています。

さらに、MLOps に詳しくないメンバーでも比較的簡単にモデル構築・運用を行えるようにし、  
より実運用しやすい ML 基盤を目指しました。

---

## 目次

1. 実際の実行フロー
2. Snowflake における ML 操作の基礎
3. 機能別に設計した 4 つの Snowflake AI Agent
4. Skills と Cortex Code を利用した AI 自動化
5. 状態ファイル `mlops-state.json` による Workflow 管理
6. まとめ

---

## 1. 実際の実行フロー

皆さんに理解しやすいように、まず全体の構造を大まかに紹介した上で、そこから段階的に詳細へ掘り下げていく形で進めたいと思います。

大まかな流れとしては、

1. 学習用データを Snowflake 上に作成
2. やいたいことをGitHub Issueとして の起票
3. plan,develop,verify,releaseの四つのai agentが構成されたAI Agent Loop を起動
4. SlackやGitHub Kankan 上で各 phase の進捗を管理

最終的な実行フローの図が以下のようになります。  
![](https://static.zenn.studio/user-upload/bddfb16915a1-20260522.png)

この仕組みにより、  
Snowflake 上の ML Workflow を AI Agent が自動で進めながら、  
GitHub Issue と Slack によって人間が常に実行状況を追跡できる MLOps Loop を構築できました。

各 Agent は GitHub Issue の内容を読み取りながら、

* どの table を利用するか
* 何を予測するのか
* どのようなモデルを利用するか
* 現在どの phase にいるか

を判断し、`mlops-state.json` を更新しながら次の phase へ進みます。

また、各 phase の実行結果は GitHub Issue や Slack に通知されるため、  
人間側もリアルタイムで進捗を確認できます。

---

### 1.1 学習用データの準備

まず、機械学習に利用する training table を Snowflake 上に作成します。

例えば、以下のようなテーブルを事前に用意します。

このテーブルには、モデル学習に必要な特徴量と目的変数を含めておきます。

---

### 1.2 やいたいことをGitHub Issueとして の起票

次に、GitHub 上で MLOps 実行用の Issue を作成します。

この Issue には、例えば以下のような情報を記載します。

```
training_table
training_purpose
```

AI Agent はこの Issue を読み取り、  
`mlops-state.json` に必要な情報を反映したうえで処理を開始します。

---

### 1.3 plan,develop,verify,releaseの四つのai agentが構成されたAI Agent Loop を起動

Issue を作成した後、AI Agent Loop を起動します。  
![](https://static.zenn.studio/user-upload/0c758822de2b-20260521.png)

例えば `snowflake-plan` Agent が実行されると、  
Agent は Issue の内容を読み取り、Snowflake 上で必要な準備を開始します。

```
snowflake-plan
    ↓
GitHub Issue を読む
    ↓
mlops-state.json を確認
    ↓
Compute Pool / Service / Notebook を準備
    ↓
実行結果を GitHub Issue に投稿
```

また、実行結果は元の Issue とは別に、  
進捗確認用の Issue として継続的に記録されます。

![](https://static.zenn.studio/user-upload/e16af314486e-20260522.png)

これにより、Agent が現在どの phase を実行しているか、  
どのような判断を行ったかを GitHub 上で確認できます。

---

### 1.4 SlackやKankan 通知による進捗確認

各 Agent の処理が完了すると、Slack に通知が送信されます。

通知では、以下を確認できます。

* 完了した phase
* 実行結果
* 次に実行される phase
* 次の Agent が行う予定の処理

これにより、AI Agent Loop の進行状況をリアルタイムで追跡できます。また、GitHub Kankan 上でも Issue の進捗を確認できます。

例：

slackの通知:  
![](https://static.zenn.studio/user-upload/b31399d90375-20260522.png)  
kankanの画面:  
![](https://static.zenn.studio/user-upload/a33355944f98-20260522.png)  
plan の AI Agent が起動すると、まず現在 `plan` phase に存在し、かつ `Open` 状態になっている GitHub Issue を確認します。

その後、対象の Issue に対して自動で処理を開始し、  
実行が成功すると、その Issue を GitHub Kankan 上の `plan-review` カラムへ移動します。

ここでは人間による review を行い、問題なければ Issue を手動で `develop` カラムへ移動します。

すると今度は `snowflake-develop` Agent がその状態を検知し、自動で develop phase の処理を開始します。

---

## 2. Snowflake における ML 操作の基礎

今回の AI Agent による MLOps Workflow を理解するためには、  
まず Snowflake 上でどのように End-to-End の機械学習 Workflow を実行できるかを理解する必要があります。

Snowflake での ML 操作は、ざっくり整理すると以下の流れになります。

1. 学習環境の準備
2. Snowflake Table の読み込み
3. データ前処理
4. モデル学習
5. モデル評価
6. Model Registry 登録

詳細は下の図の通りです。

![](https://static.zenn.studio/user-upload/4799dc3470f4-20260521.png)

Snowflake では、Snowpark / Snowpark ML / Notebook / Model Registry などを利用することで、 データ取得からモデル管理までを Snowflake 内で一貫して実行できます。

公式ドキュメントでも、End-to-End ML Workflow が紹介されています。

参考:  
<https://www.snowflake.com/en/developers/guides/end-to-end-ml-workflow/#1>

---

## 3. 機能別に設計した 4 つの Snowflake AI Agent

Snowflake 上での ML Workflow を整理すると、 これらの処理を以下の4つの Agent に分割できます。

* `snowflake-plan`
* `snowflake-develop`
* `snowflake-verify`
* `snowflake-release`

それぞれの Agent は、Snowflake ML Workflow の各ステップを担当します。

### 6ステップ × 4エージェントの対応表

| ステップ | plan | develop | verify | release |
| --- | --- | --- | --- | --- |
| 1. 学習環境の準備 | ● |  |  |  |
| 2. Snowflake Table の読み込み |  | ● | ● |  |
| 3. データ前処理 |  | ● |  |  |
| 4. モデル学習 |  | ● | ● |  |
| 5. モデル評価 |  | ● | ● |  |
| 6. Model Registry 登録 |  |  |  | ● |

---

### 3.1 snowflake-plan

**担当: ① 学習環境の準備 + 実行 plan の作成**

`snowflake-plan` は、Snowflake 上の ML 実行環境を準備・確認する Agent です。

主な役割は以下の2つです。

* Snowflake の学習環境準備
* 目的と使用するべきなテーブルをもとにした ML 実行 plan の作成

---

#### 学習環境の準備

まず、モデル学習に必要な Snowflake 環境を確認・作成します。

主な処理は以下です。

* Compute Pool の確認 / 作成
* Service の確認 / 作成
* Notebook の確認 / 作成
  + `MLOPS_RECOMMEND_STOP_MODEL_PREP`

---

#### 目的と使用するべきなテーブルをもとにした ML 実行 plan の作成

また、`snowflake-plan` は GitHub Issue の内容(利用するべきなテーブルかつ目的)を読み取り、大まかな実行 plan も作成します。

サンプル図はこんな感じになります。

![](https://static.zenn.studio/user-upload/28864c6405a1-20260522.png)

---

### 3.2 snowflake-develop

**担当: ② Table 読み込み / ③ 前処理 / ④ モデル学習 STG / ⑤ モデル評価 STG**  
**DB: `STG環境`**

`snowflake-develop` は、STG 環境でモデル学習・比較・評価を行う Agent です。

#### ② Snowflake Table の読み込み

STG 環境の training table を Notebook 実行時に読み込みます。

```
FACT_ML_XXXXX_TEST_TRAIN_DATA
```

#### ③ データ前処理

Notebook 内で特徴量エンジニアリングを実行します。

また、特徴量重要度 TOP15 を確認し、データリークの可能性もチェックします。

例えば、特定の特徴量だけが極端に高い重要度を持つ場合、  
予測対象に近すぎる情報や未来情報が含まれている可能性があります。

その場合は、`phase` を `model-prep` に戻して処理を終了します。

#### ④ モデル学習 STG

STG データを使って、PLANで提示してたの3モデルを訓練します。

例：

```
from xgboost import XGBClassifier

model = XGBClassifier(
    n_estimators=xxx,
    max_depth=xx,
    learning_rate=xxx,
    random_state=42,
    eval_metric='logloss'
)
```

#### ⑤ モデル評価 STG

Accuracy / F1 / AUC を比較し、最良モデルを選定します。

選定結果は `mlops-state.json`というファイル に記録します。

```
{
  "selected": {
    "model_type": "lightgbm",
    "features": ["..."],
    "best_params": {},
    "stg_accuracy": xxxx
  }
}
```

---

### 3.3 snowflake-verify

**担当: ② Table 読み込み / ④ モデル学習 PRD / ⑤ モデル評価 PRD**  
**DB: `PRD環境`**

`snowflake-verify` は、STG で選定されたモデルを PRD データで再検証する Agent です。

#### ② Snowflake Table の読み込み PRD

PRD 環境の training table を読み込みます。

```
DATA_PLATFORM_PRD.MART_MACHINE_LEARNING.{training_table}
```

#### ④ モデル学習 PRD

`mlops-state.json` に保存された以下の情報を読み取ります。

* `selected.model_type`
* `selected.features`
* `selected.best_params`

STG で選定済みのモデル・特徴量・パラメータをそのまま PRD データに適用します。

#### ⑤ モデル評価 PRD

PRD データでの AUC / F1 を確認し、結果を `mlops-state.json` に記録します。

```
{
  "metrics": {
    "prd_accuracy": xxxx,
    "prd_f1": xxxx
  }
}
```

---

### 3.4 snowflake-release

**担当: ⑥ Model Registry 登録**  
**DB: `DATA_PLATFORM_PRD`**

`snowflake-release` は、PRD で検証済みのモデルを Model Registry に登録する Agent です。

主な処理は以下です。

* PRD Model Registry にモデルを登録
* モデル名とバージョンを管理
* PostgreSQL 側の推論設定を更新(こちらが自社のレコメンドサービスのDBです)

例:

```
model_name: XXX_LIGHTGBM_MODEL
model_version: V1
```

また、PostgreSQL の `ml_model_configs` も更新します。

```
model_key='XXXX'
model_version='V1'
```

---

## 4. Skills と Cortex Code を利用した AI 自動化

4つの Snowflake AI Agent は、それぞれ直接すべての処理を書くのではなく、  
それぞれの Skill を呼び出して Snowflake 操作を実行します。

今回の構成では、Snowflake に対する操作は基本的に `cortex -p` を使って実行しています。

cortex の利用方法はsnowflakeの公式ドキュメントを参考にします。

参考:  
<https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-cli>

snowflake-planのskillsを例にすると：

```
### phase: model-prep（snowflake-plan のみ）

**目的**: Snowflake 上に ML 実行環境を整備し、候補モデルを Notebook に記述する

TARGET を状態ファイルの `target` フィールドから取得する（例: `XXXX_test`）。
`target` フィールドがない場合は `snowflake.training_table` から抽出する（例: `FACT_ML_XXXX_TEST_TRAIN_DATA` → `XXXX_test`）。
TARGET に `test` が含まれる場合、モデル名にも必ず `TEST` を含めること（例: `XXXX_TEST_{MODEL_TYPE}_MODEL`）。

**ステップ1: Compute Pool の確認/作成**

- 状態ファイルの `snowflake.notebook_name` が既に設定済みの場合 → model-prep は完了済みとみなし sf-develop に進む
- 未設定の場合のみ以下を実行:

```bash
cortex -p "DATA_PLATFORM_STGに MLOPS_COMPUTE_POOL というCompute Poolが存在するか確認して。なければ MIN_NODES=X MAX_NODES=X INSTANCE_FAMILY=XXX で作成して"
```

**ステップ2: Service の確認/選択/作成**

```bash
cortex -p "利用可能なSnowflake Serviceを全て表示して。あれば最も新しいServiceの名前を教えて。なければ MLOPS_COMPUTE_POOL を使って GPU compute type、その他デフォルト設定で新しいServiceを作成して"
```

- 既存Serviceがあれば → そのうち最新のものを使用（新規作成しない）
- 既存Serviceが1つもなければ → 新規作成し名前を `MLOPS_SERVICE` とする
- 使用するService名を変数として保持し、以降のステップで参照する

**ステップ3: Notebook の確認/作成**

- `MLOPS_{TARGET}_MODEL_PREP` という名前の Notebook が既に存在するか確認:

```bash
cortex -p "MLOPS_{TARGET}_MODEL_PREP という名前のSnowflake Notebookが既に存在するか確認して"
```

- **既存あり** → そのまま使用（再作成しない）
- **既存なし** → 新規作成:

```bash
cortex -p "{DB_NAME}.{SCHEMA_NAME}.{training_table} のデータを使って、{target}を予測するためのSnowflake Notebookを MLOPS_{TARGET}_MODEL_PREP という名前で作成して。Serviceは{service_name}を使用。Notebook内に候補モデルを最低3つ選定し、各モデルの特徴量リストと選定理由もコメントで記載して"
```

**完了後**

- 状態ファイルを更新:

```json
{
  "phase": "sf-develop",
  "snowflake": {
    "notebook_name": "MLOPS_{TARGET}_MODEL_PREP",
    "service_name": "{service_name}"
  }
}
```
```

---

## 5. 状態ファイル `mlops-state.json` による Workflow 管理

今回の構成で最も重要なのが、`mlops-state.json` です。

4つの Agent はそれぞれ独立していますが、  
この state ファイルを共有することで、1つの MLOps Loop として動作します。

```
Agent は状態を持たない
        ↓
mlops-state.json が状態を持つ
        ↓
phase に応じて次の Agent が起動する
```

つまり、`mlops-state.json` は Workflow 全体の Single Source of Truth です。

---

### 5.1 全体の制御構造

```
┌────────────────────────────────────────────┐
│              agentloop                     │
│        10秒ごとに状態を確認                 │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────┐
│            mlops-trigger.sh                │
│      mlops-state.json の phase を読む       │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────┐
│        phase に応じて Agent を起動          │
└──────────────────┬─────────────────────────┘
                   │
     ┌─────────────┼─────────────┬─────────────┐
     ▼             ▼             ▼             ▼
┌────────┐   ┌──────────┐   ┌────────┐   ┌─────────┐
│ plan   │   │ develop  │   │ verify │   │ release │
└────────┘   └──────────┘   └────────┘   └─────────┘
```

`loop_active=false` の場合は、すべての Agent を skip します。

`loop_active=true` の場合のみ、`phase` を見て対象 Agent を起動します。

---

### 5.2 `mlops-state.json` の例

`mlops-state.json` には、現在の phase だけではなく、  
モデル選定結果、評価指標、Snowflake のリソース情報なども保存します。

```
{
  "phase": "sf-develop",
  "iteration": 2,
  "loop_active": true,
  "target": "xxx",

  "snowflake": {
    "training_table": "FACT_XXXX_TEST_TRAIN_DATA",
    "notebook_name": "MLOPS_XXXX_MODEL_PREP",
    "service_name": "MLOPS_SERVICE",
    "model_name": "XXXX_LIGHTGBM_MODEL",
    "model_version": "V1"
  },

  "selected": {
    "model_type": "lightgbm",
    "features": [
      "xxxx",
      "xxxx",
      "xxxx",
      "xxxx"
    ],
    "best_params": {
      "num_leaves": xx,
      "learning_rate": xxx,
      "n_estimators": xxx
    },
    "stg_accuracy": xxxx
  },

  "metrics": {
    "lightgbm": {
      "auc": xxx,
      "f1": xxx,
      "accuracy": xxx
    },
    "xgboost": {
      "auc": xxxx,
      "f1": xxxx,
      "accuracy": xxxx
    },
    ....
    "prd_accuracy": xxxx,
    "prd_f1": xxxx
  }
}
```

---

### 5.3 state によって Agent をつなぐ

各 Agent は前の Agent の処理結果を直接受け取るのではなく、  
`mlops-state.json` を通して情報を受け渡します。

```
snowflake-develop
    ↓
selected.model_type / features / best_params を書く
    ↓
snowflake-verify
    ↓
selected 情報を読んで PRD 検証を実行
    ↓
snowflake-release
    ↓
model_name / model_version を書く
```

この構成により、Agent 間の依存を疎結合にできます。

---

## 6. まとめ

今回の構成では、Snowflake 上の ML Workflow を4つの AI Agent に分割し、  
`mlops-state.json` を中心に接続しました。

ポイントは以下です。

* Snowflake ML の処理を plan / develop / verify / release に分割
* Cortex Code によって Snowflake 操作を自然言語で実行
* Skill によって処理ロジックを再利用可能にする
* `mlops-state.json` によって Agent 間の状態を管理
* GitHub Issue と Slack によって実行状況を監視

今回の基盤は、単なる Notebook 自動化ではなく、

> Snowflake 上の ML Workflow を状態駆動で制御する AI Agent MLOps 基盤

として設計しています。
