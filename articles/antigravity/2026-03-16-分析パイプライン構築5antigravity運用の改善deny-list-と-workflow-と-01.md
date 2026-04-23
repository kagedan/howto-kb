---
id: "2026-03-16-分析パイプライン構築5antigravity運用の改善deny-list-と-workflow-と-01"
title: "分析パイプライン構築（5）〜Antigravity運用の改善：Deny List と Workflow と rules"
url: "https://zenn.dev/pdata_analytics/articles/46d0a9abfad90c"
source: "zenn"
category: "antigravity"
tags: ["Gemini", "antigravity", "zenn"]
date_published: "2026-03-16"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

# 分析パイプライン構築（5）

## Antigravity運用の改善：Deny List と Workflow と rules

この連載では、実務でデータ分析基盤を立ち上げる中で、  
「どのようにして分析パイプラインを構築してきたか」を、  
実際の試行錯誤を交えて書いています。

筆者は、プロダクトのログを扱いながら、  
分析・データ基盤の整備を行っている実務担当者です。

前回の記事では、Antigravityをデータ分析パイプライン開発に使う中で  
AIエージェントの挙動を安定させるため、次の3層構造のルールを整理しました。

GEMINI.md  
↓  
AI\_RULES.md  
↓  
AWS\_GLUE\_BEST\_PRACTICES.md

それぞれの役割は次の通りです。

* **GEMINI.md**：全体共通のルール、AIの行動制御
* **AI\_RULES.md**：分析思想や基本方針
* **AWS\_GLUE\_BEST\_PRACTICES.md**：Glue開発の実装ルール

今回は、この構成を実際に運用してみて見えてきた課題と、  
それに対して実施した改善を整理します。

Antigravityは現在も進化しているツールであり、  
今回の内容も **実運用の中で試行錯誤している途中の記録**です。

---

# この記事で分かること

Antigravityを使った開発を進める中で、主に次の2つの問題が発生しました。

* AIが勝手にコマンドを実行してしまう問題
* ルールやツールが増えすぎてコンテキストが膨らむ問題

この記事では、それらに対して導入した

* **Deny List Terminal Commands**
* **Workflow**
* **Antigravity公式構成へのルール再配置**

という改善について紹介します。

---

# 1. 課題：AIがジョブを実行してしまう

GEMINI.md では次のようなルールを書いていました。

* Glue Job を実行してはいけない
* Git Push をしてはいけない

しかし実際には、次のようなことが発生しました。

* １つの会話の中で **Glue Jobを3回勝手に実行**
* **Git Pushを1回勝手に実行**

その都度指摘すると

> ルール逸脱に関して、深く反省したような回答

は返ってくるのですが、  
しばらくすると同じことが起きます。

これはルールの書き方の問題というより、

**Antigravity側の制御機構を使っていなかった**

ことが原因であると考えました。  
知ってはいたのですが、まずは使ってみることを優先した結果ともいえます。

---

# 2. 対策：Deny List Terminal Commands

Antigravityには  
**Deny List Terminal Commands** という機能があります。

これは、特定のコマンドを実行する前に  
必ずユーザー確認を入れる機能です。

例えば次のコマンドを登録しました。

`aws glue start-job-run`  
`git push`

Deny Listに登録すると、

> Agent asks for permission before executing commands matched by a deny list entry.

つまり

**AIは必ずユーザー確認を求めるようになります。**

---

## 効果

設定して4日ほど経過しましたが、

Pushする前に確認が入るようになりました。

一方で、

原因は比較的単純でした。

Glue Jobの実行は

`aws glue start-job-run`

ではなく、

**ジョブ実行スクリプト経由**

で呼び出されていたためです。

`run_glue_job.sh`  
↓  
`aws glue start-job-run`

この場合、

**スクリプト自体は実行できてしまう**

状態でした。

現在は次の対応を行っています。

* 実行してはいけないスクリプトを  
  **AI\_RULES.md に明記**

しばらくこの運用で様子を見る予定です。

---

# 3. 課題：ルール読み込みが多すぎる

もう一つの問題は、

**新しい会話で全てのルールが読み込まれてしまう**

ことでした。

例えば次のようなファイルです。

* GEMINI.md
* AI\_RULES.md
* AWS\_GLUE\_BEST\_PRACTICES.md
* pipeline\_architecture.md

作業内容と関係ないルールまで  
すべて文脈に入ってしまいます。

その結果

が起きている可能性があります。

---

## rule bloat の問題

Antigravity でも

> AIエージェントに与えるプロンプト（指示・ルール）が増えすぎて、逆に精度が落ちる現象

が報告されています。

Context Saturation（コンテキストの飽和）や tool bloat と呼ばれることもあるようです。

**rule bloat** が起きると

につながる可能性があります。

---

# 4. 対策：Workflowへの切り出し

そこで、まずルールを軽くするために、いくつかの作業を

**Workflowとして切り出しました。**

Workflowには

をまとめることができます。

今回切り出したWorkflowは次の通りです。

---

## バックフィル

過去データの再作製処理を行うWorkflowです。

ジョブ毎に期間を指定して実行することができます。

また、すぐ終わるジョブはPCから、数時間かかるジョブはAWSから実行できるようにしています。

実行する前に、関連する過去のデータを削除する機能も入れています。

---

## 全カラム統計確認

データセットの全カラムについて

などを確認する処理です。

---

## ジョブスクリプトデプロイ

まで含めた一般的なデプロイ作業です。

しかし、１つだけ、なぜか何回もデプロイミスをする作業があるので、  
それを注意喚起しています。

---

## ジョブテスト

データパイプラインで最も怖い問題の一つは

**特定レコードが途中で消えること**

です。

そのため、特定のレコードが

S3 Raw  
↓  
Glue Transform  
↓  
Athena Table

まで **欠損なく処理されるか** を確認する  
ジョブテストを作製しました。

ジョブのロジックに変更が入った場合には、必ず実行します。

---

## Workflowの効果

Workflowとして切り出した作業は  
かなり安定して動作しています。

以前はよくあった

* 新しいスクリプトを作ってしまう
* テストを忘れる
* 作業手順を飛ばす
* ジョブの実行順を間違える

といった問題も  
ほぼ発生しなくなりました。

また、

**WorkflowはFastモードで実行**

しています。

定型処理なので  
高速モードでも十分安定しています。

---

# 5. ルールのスコープ整理

もう一つ行った改善は  
**ルールファイルの配置の見直し**です。

これまでルールファイルは  
GEMINI.md からリンクする形で読み込んでいました。

GEMINI.md  
↓  
AI\_RULES.md  
↓  
AWS\_GLUE\_BEST\_PRACTICES.md

しかしこの方法には問題があります。

GEMINI.md は **グローバルルール**として扱われるため、  
そこから読み込まれるルールも **すべてグローバルルール扱い**になってしまいます。

将来別のプロジェクトが増えた場合、

といった異なる領域で  
同じルールが適用されてしまう可能性があります。

---

# 6. Antigravity公式構成への再配置

そこで今回、ルールファイルの構造を  
**Antigravity公式の構成に合わせて再整理しました。**

Antigravityでは現在、次の構造が推奨されています。

この構成に合わせて、  
既存のMarkdownファイルを **一度分解して再配置**しました。

---

## 再配置後の構成

現在のプロジェクト構成は次のようになっています。

```
~/.gemini/GEMINI.md

data-pipeline
│
├─ AGENTS.md
│
└─ .agent
  │
  ├─ rules
  │  ├─ AI_EXECUTION_POLICY.md
  │  ├─ DATA_PIPELINE_ARCHITECTURE.md
  │  └─ AWS_GLUE_BEST_PRACTICES.md
  │
  └─ workflows
　   └─ PIPELINE_OPERATIONS.md
```

---

## 既存ファイルの再配置

今回の整理では、  
既存のファイルをそのまま移動したわけではありません。

それぞれのMarkdownを

* AIの実行ポリシー
* パイプライン設計
* Glue実装ルール
* 運用手順

という観点で **分解して再配置**しました。

---

## AI\_RULES.md → AI\_EXECUTION\_POLICY.md

AIの行動制御に関する部分は

`.agent/rules/AI_EXECUTION_POLICY.md`

に移動しました。

ここでは

* Glue Job実行ポリシー
* Git操作制御
* 危険コマンドの扱い

などを定義しています。

Deny List にも記載はしているのですが、こちらにも残しています。  
スクリプトの実行禁止もここで指定しています。

---

## pipeline\_architecture.md → DATA\_PIPELINE\_ARCHITECTURE.md

パイプライン設計に関する内容は

`.agent/rules/DATA_PIPELINE_ARCHITECTURE.md`

に整理しました。

ここでは

* S3レイヤー構造
* Glue処理フロー
* Athenaテーブル設計

など

**データパイプラインの設計思想**

を説明しています。

新しい会話で分析を始める時にも、毎回毎回説明しなくてもすみます。  
説明不足だとパイプラインの調査を始めてしまいます。

DATA\_PIPELINE\_ARCHITECTURE.md  
は調査時間とクオータが無駄に消費されるのも防ぎます。

---

## AWS\_GLUE\_BEST\_PRACTICES.md

Glue開発ルールは

`.agent/rules/AWS_GLUE_BEST_PRACTICES.md`

としてそのまま維持しました。

分析で得たノウハウはこちらに追記する運用にしています。

---

## OPERATIONS\_MANUAL.md → Workflow

運用手順は

`.agent/workflows/PIPELINE_OPERATIONS.md`

として整理しました。

ここには

などの **作業手順** がまとめられています。

---

## なぜこの構造にしたのか

Antigravityでは  
AIが次の順序で情報を参照します。

GEMINI.md  
↓  
AGENTS.md  
↓  
rules  
↓  
workflows

つまり

* **AGENTS.md → プロジェクトの地図**
* **rules → 技術ルール**
* **workflows → 作業手順**

という構造にすることで、

AIは

1. プロジェクトを理解する
2. 制約を確認する
3. 作業を実行する

という順序で動くようになります。

---

# 7. AIエージェント運用で重要だったこと

今回の運用で感じたのは、

AIエージェントでは

**ルールの内容以上に  
ルールの構造が重要**

ということでした。

例えば

* ルールのスコープ
* Workflow化
* 役割ごとのファイル分割

といった設計によって、  
AIの挙動はかなり安定します。

Antigravityのようなツールでは、

**「何を書くか」だけでなく  
「どこに置くか」も設計の一部**

だと感じています。

---

## まだ測定できていないこと

Workflow導入やルールの再配置によって

がどれだけ減ったかは  
まだ定量的には測定できていません。  
（そもそも定量的に測定できるものなのかも分かりません。）

例えば

* rule bloat が減ったか
* 推論トークンが減ったか

などは  
今後の観測ポイントになりそうですが、しばらくはこの設定で運用します。

---

# 次回予告

AIの進化の速度が早く、正しく理解してから開発を開始するでは  
時間がもったいないです。

多少の回り道はあるのですが、実際やってみて、問題を理解して、改善するという  
方法で、なんとかついていけてると感じています。

データ分析パイプラインも回り始め、Workflowsも整理できたので、

**仮説検証を高速で回す**

ことに取り組みます。
