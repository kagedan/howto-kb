---
id: "2026-06-27-loop-engineering入門aiエージェント時代にプロンプトを書くからループを設計するへ-01"
title: "Loop Engineering入門：AIエージェント時代に「プロンプトを書く」から「ループを設計する」へ"
url: "https://zenn.dev/japan/articles/ebb10d5ef49c5d"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "AI-agent", "zenn"]
date_published: "2026-06-27"
date_collected: "2026-06-28"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/5da59d36386b-20260627.png)

AIコーディングエージェントを使っていると、次のような経験はないでしょうか。

* 最初の指示はうまくいったが、次に何を頼むべきか毎回考えている
* 実装は速いが、レビュー・修正・再実行の管理が人間側に残っている
* エージェントが途中で文脈を失い、同じ説明を何度も繰り返している
* 「テストして」「直して」「もう一度確認して」という指示を人間が手で回している

この状態は、AIを使っているようで、実際には人間がAIのジョブキュー兼プロジェクトマネージャーになっている状態です。

そこで注目されているのが **Loop Engineering** です。

一言でいうと、Loop Engineeringとは、

> AIエージェントに毎回プロンプトを書くのではなく、AIエージェントが目的達成まで自律的に考え、実行し、検証し、必要なら人間に戻す「ループ」そのものを設計する考え方

です。

この記事では、Loop Engineeringを単なる流行語としてではなく、実際の開発・運用に落とし込める設計パターンとして整理します。

---

## Loop Engineeringとは何か

従来のAI活用は、多くの場合このような流れでした。

```
人間が指示する
  ↓
AIが回答する
  ↓
人間が結果を見る
  ↓
人間が次の指示を考える
  ↓
AIが再実行する
```

これは **Prompt Engineering** の延長です。

一方、Loop Engineeringでは次のように考えます。

```
ゴールを定義する
  ↓
エージェントが状態を確認する
  ↓
必要な作業を決める
  ↓
実行する
  ↓
検証する
  ↓
成功条件を満たすまで繰り返す
  ↓
完了または人間へエスカレーション
```

つまり、設計対象が「1回のプロンプト」ではなく、**反復する制御システム** に変わります。

---

## Prompt Engineering / Context Engineering / Loop Engineering の違い

| 観点 | Prompt Engineering | Context Engineering | Loop Engineering |
| --- | --- | --- | --- |
| 主な設計対象 | 1回の指示文 | モデルに渡す情報 | 反復実行する仕組み |
| 人間の関与 | 毎ターン必要 | コンテキスト整備で必要 | 例外・承認時のみ |
| 状態管理 | ほぼなし | セッション内中心 | 外部状態を持つ |
| ゴール | 良い回答を得る | 良い判断材料を渡す | ゴール達成まで進める |
| 成果物 | プロンプト | ドキュメント・履歴・RAG | ワークフロー・エージェント群・評価基準 |

重要なのは、これらは対立概念ではないということです。

Loop Engineeringは、Prompt EngineeringやContext Engineeringの上に乗ります。

プロンプトが雑であれば、ループは「雑な作業を高速に繰り返す装置」になります。  
コンテキストが汚れていれば、ループは「誤った前提を持ち続ける装置」になります。

つまり、Loop Engineeringは魔法ではなく、**プロンプト・コンテキスト・評価・権限管理をまとめて設計する上位レイヤー** です。

---

## なぜ今Loop Engineeringなのか

AIエージェントの能力が上がるほど、人間のボトルネックは「コードを書くこと」から「仕事をどう任せるか」に移ります。

特に開発現場では、単発の生成よりも次のような作業のほうが多くなります。

* PRの差分を確認する
* テスト失敗を調査する
* 小さな修正を入れる
* 依存ライブラリの更新を確認する
* セキュリティ警告を整理する
* Issueを分類する
* ドキュメントと実装の差分を埋める

これらは1回のプロンプトで完結しにくいタスクです。

むしろ、状態を見て、判断し、実行し、検証し、必要なら人間に戻すというループに向いています。

---

## Loop Engineeringの基本構造

Loop Engineeringを実装する場合、最低限以下の要素を設計します。

ポイントは、AIに「頑張って」と頼むのではなく、以下を明確にすることです。

* 何を達成したら完了なのか
* 何を見て現在状態を判断するのか
* どのツールを使ってよいのか
* どの操作は禁止するのか
* 何回失敗したら止めるのか
* どの条件で人間に戻すのか

---

## 良いループに必要な6要素

### 1. Goal：目的

まず、ループの目的を明確にします。

悪い例:

良い例:

```
毎朝9時にリポジトリを確認し、以下を実行する。

- 失敗しているCIを検出する
- 原因が軽微な依存関係・型エラー・Lintエラーであれば修正PRを作る
- 仕様判断が必要な変更はIssueにコメントして人間に戻す
- mainブランチへの直接pushは禁止する
```

目的は、AIが解釈できるだけでなく、人間がレビューできる粒度にする必要があります。

---

### 2. State：状態

AIエージェントは、何も設計しなければセッションが切れた瞬間に文脈を失います。

そのため、ループには外部状態が必要です。

例:

```
.loop/state.md
.loop/history.json
.loop/decisions.md
GitHub Issues
Pull Requests
CI logs
Datadog / CloudWatch / Sentry
```

状態には以下を残します。

* 前回何をしたか
* 何が失敗したか
* どの判断を人間に委ねたか
* 次回再開時に何を見るべきか
* 既に試した修正は何か

状態管理がないループは、記憶を持たない作業者に毎回同じ仕事を頼むようなものです。

---

### 3. Action：実行

ループは、AIが使えるツールを持つことで初めて価値を出します。

例:

* Git操作
* テスト実行
* Lint実行
* Issue作成
* PR作成
* CIログ取得
* ドキュメント更新
* Slack通知
* チケット更新

ただし、ツールが増えるほどリスクも増えます。

そのため、権限は最小限にします。

```
permissions:
  github:
    contents: read
    pull_requests: write
    issues: write
  shell:
    allow:
      - npm test
      - npm run lint
      - composer test
      - php artisan test
    deny:
      - rm -rf
      - git push origin main
      - terraform apply
```

Loop Engineeringでは、AIの賢さだけでなく、**AIに何を許可し、何を禁止するか** が重要です。

---

### 4. Verify：検証

ループには必ず検証が必要です。

AIがコードを書けることと、そのコードが正しいことは別問題です。

最低限、以下のような検証を入れます。

* Unit Test
* Integration Test
* Type Check
* Lint
* Security Scan
* Build
* 差分レビュー
* 仕様との照合

さらに重要なのが、**実装者と検証者を分けること** です。

```
Implementer Agent:
  - コードを書く
  - 修正案を作る
  - PRを作成する

Verifier Agent:
  - テスト結果を見る
  - 差分をレビューする
  - 仕様違反を指摘する
  - マージ可否を判断する
```

同じエージェントが自分の成果物を評価すると、甘い判定になりがちです。

人間の開発でも、実装者とレビュアーを分けるのと同じです。

---

### 5. Stop Condition：停止条件

Loop Engineeringで最も危険なのは、止まらないループです。

停止条件は最初に設計します。

例:

```
以下のいずれかを満たしたら停止する。

- すべてのテストが成功した
- PRを作成した
- 同じテストが3回連続で失敗した
- 修正差分が500行を超えた
- セキュリティ関連ファイルに変更が必要になった
- DBマイグレーションが必要になった
- 本番影響の可能性があると判断した
```

「成功したら止める」だけでは不十分です。

「危なくなったら止める」  
「分からなくなったら人間に戻す」  
「コストが増えすぎたら止める」

この3つも必要です。

---

### 6. Human Gate：人間への戻し方

Loop Engineeringは、人間を不要にする設計ではありません。

むしろ、人間の判断をどこに置くかを明確にする設計です。

人間に戻すべきケース:

* 仕様判断が必要
* セキュリティ影響がある
* 課金・料金・契約に関わる
* 本番DBに影響する
* 顧客データに触れる
* 破壊的変更が必要
* テストでは判断できないUX変更がある

人間に戻すときは、単に「失敗しました」ではなく、判断しやすい形式にします。

```
## Human Review Required

### 目的
CI失敗の修正

### 現在の状況
`npm test` が `UserProfile.test.tsx` で失敗しています。

### 試したこと
1. 型定義の修正
2. mockデータの更新
3. snapshotの再生成

### 判断が必要な点
現在の仕様では、退会済みユーザーを一覧に表示するべきか不明です。

### 選択肢
A. 退会済みユーザーを非表示にする
B. 退会済みユーザーも表示し、ステータスを付ける
C. 既存仕様を確認するまで保留する

### 推奨
B。ただし仕様確認が必要です。
```

これにより、人間はゼロから状況を読む必要がなくなります。

---

## 実装例：GitHub Actionsで日次トリアージループを作る

ここでは、簡易的な「Daily Triage Loop」を考えます。

目的:

* 毎朝、CI失敗・古いPR・未分類Issueを確認する
* 自動修正できるものはPRを作る
* 判断が必要なものはIssueコメントにまとめる

### ディレクトリ構成

```
.github/
  workflows/
    daily-triage.yml

.loop/
  goal.md
  state.md
  policy.md
  prompt.md
```

### goal.md

```
# Daily Triage Loop Goal

このループは、リポジトリの保守作業を毎日実行する。

## 対象

- CIが失敗しているPR
- 7日以上更新されていないPR
- ラベルが付いていないIssue
- 軽微なLint / Type Error

## 自動対応してよいこと

- Lint修正
- 型エラー修正
- テストのmock修正
- ドキュメントのリンク切れ修正
- Issueへの分類コメント追加

## 自動対応してはいけないこと

- mainブランチへの直接push
- DBマイグレーション
- 認証・認可ロジックの変更
- 課金処理の変更
- 本番環境へのデプロイ
```

### policy.md

```
# Loop Policy

## Stop Conditions

以下の場合は作業を停止し、人間にレビューを依頼する。

- 同じ修正を3回試して失敗した
- 差分が500行を超えた
- security / auth / billing / infra 配下の変更が必要
- テストが存在しない領域のロジック変更が必要
- API仕様の判断が必要

## Output Format

作業後は以下を出力する。

- 実行したチェック
- 発見した問題
- 自動修正した内容
- 作成したPR
- 人間に判断してほしい事項
```

### daily-triage.yml

```
name: Daily Triage Loop

on:
  schedule:
    - cron: "0 0 * * *"
  workflow_dispatch:

permissions:
  contents: read
  issues: write
  pull-requests: write

jobs:
  triage:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 22

      - name: Install dependencies
        run: npm ci

      - name: Run checks
        run: |
          npm run lint || true
          npm test || true

      - name: Run AI triage loop
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          AI_API_KEY: ${{ secrets.AI_API_KEY }}
        run: |
          node scripts/triage-loop.js \
            --goal .loop/goal.md \
            --policy .loop/policy.md \
            --state .loop/state.md
```

実際には、`triage-loop.js` の中で以下を行います。

```
1. GitHub APIからIssue / PR / CI結果を取得
2. .loop/state.md を読み込む
3. AIに現在状態とポリシーを渡す
4. 次に行うべきアクションをJSONで受け取る
5. 許可されたアクションだけ実行する
6. 結果を検証する
7. state.md を更新する
8. 必要ならPR作成またはIssueコメントを行う
```

重要なのは、AIに自由にシェルを触らせるのではなく、**許可されたアクションの中から選ばせる** ことです。

---

## ループ設計テンプレート

実務でLoop Engineeringを始めるなら、以下のテンプレートを使うと整理しやすいです。

```
# Loop Design

## 1. Name

例: Daily PR Triage Loop

## 2. Goal

このループが達成する目的を書く。

## 3. Trigger

いつ実行するか。

- cron
- webhook
- 手動
- CI失敗時
- Issue作成時

## 4. Inputs

ループが読む情報。

- GitHub Issues
- Pull Requests
- CI logs
- Repository files
- Monitoring alerts
- Documents

## 5. Allowed Actions

実行してよい操作。

## 6. Denied Actions

実行してはいけない操作。

## 7. Verification

成功・失敗をどう判定するか。

## 8. Stop Conditions

どの条件で停止するか。

## 9. Human Escalation

どの条件で人間に戻すか。

## 10. State

何を記録し、次回に引き継ぐか。

## 11. Cost Budget

1回あたり、1日あたり、1か月あたりの上限。

## 12. Review Cycle

人間がどの頻度でループの判断をレビューするか。
```

---

## Loop Engineeringのアンチパターン

### 1. 成功条件が曖昧

これは危険です。

改善の定義がないため、ループが終わりません。

改善系のループでは、必ず測定可能な条件を置きます。

```
- テスト成功
- Lintエラー0件
- 既存API互換性維持
- Lighthouse Performance 90以上
- 未分類Issueを0件にする
```

---

### 2. AIに強すぎる権限を渡す

AIエージェントに広すぎる権限を渡すと、事故の影響範囲が広がります。

避けるべき例:

```
- 本番環境への直接デプロイ
- mainへの直接push
- DB削除権限
- secrets読み取り
- 課金設定変更
- IAM変更
```

AIエージェントは、優秀な新人エンジニアとして扱うくらいが安全です。

読み取りから始め、次にPR作成、最後に限定的な自動マージという順序で段階的に広げます。

---

### 3. 検証をAIの自己評価だけにする

これは弱いです。

最低限、機械的な検証を入れます。

```
- テスト
- 型チェック
- Lint
- Build
- セキュリティスキャン
- 差分制限
```

可能であれば、実装エージェントとは別の検証エージェントを使います。

---

### 4. コスト設計がない

ループは便利ですが、回しすぎるとトークンコストが膨らみます。

特に危険なのは以下です。

* 高頻度cron
* 大きなリポジトリ全体の読み込み
* 複数サブエージェント
* 長い履歴を毎回投入
* 失敗時の無制限リトライ

対策:

```
- 実行頻度を下げる
- 差分だけ読む
- コンテキストを要約する
- 最大試行回数を決める
- 1回あたりのトークン上限を決める
- 高価なモデルと安価なモデルを使い分ける
```

---

### 5. 理解負債を放置する

Loop Engineeringで開発速度が上がると、人間がコードを理解する速度を超えることがあります。

これを **理解負債** と呼べます。

AIが大量のPRを作り、テストも通っている。  
しかし、チームの誰も設計意図を説明できない。

これは非常に危険です。

対策:

* AI生成PRも必ず人間が読む
* 週次でAI変更のサマリを確認する
* 設計判断はADRに残す
* 大きな差分は自動マージしない
* 「なぜこの変更をしたか」をPR本文に書かせる

AIが実装を速くしても、責任は人間に残ります。

---

## どこから始めるべきか

いきなり完全自律のループを作る必要はありません。

おすすめは、次の3段階です。

### Level 1：Report Loop

AIは分析だけ行い、人間が判断します。

例:

```
毎朝、未対応Issue・失敗CI・古いPRを整理してSlackに報告する
```

リスクが低く、導入しやすいです。

---

### Level 2：Assisted Loop

AIが修正案やPRを作り、人間が承認します。

例:

```
Lintエラーや型エラーを修正するPRをAIが作成し、人間がレビューする
```

実務ではこのレベルが最もバランスが良いです。

---

### Level 3：Unattended Loop

AIが限定された範囲で自動修正・自動マージします。

例:

```
ドキュメントのリンク切れ修正や依存ライブラリのpatch更新を自動マージする
```

ただし、十分なテスト・権限制御・監査ログがある場合に限るべきです。

---

## インフラ・運用領域での活用例

Loop Engineeringはコーディングだけでなく、インフラ運用にも向いています。

### 監視アラート整理ループ

```
Trigger:
  CloudWatch / Datadog / Prometheus のアラート

Actions:
  - 過去の同種アラートを検索
  - 直近のデプロイ履歴を確認
  - 影響範囲を要約
  - Runbookを提示
  - Slackに一次分析を投稿

Denied:
  - 本番再起動
  - スケール変更
  - DB操作

Human Gate:
  - 顧客影響あり
  - データ不整合の可能性あり
  - 原因不明
```

### Terraform Planレビューループ

```
Trigger:
  Pull Request作成時

Actions:
  - terraform planを実行
  - 差分を要約
  - 破壊的変更を検出
  - コスト影響を推定
  - PRにコメント

Denied:
  - terraform apply
  - state操作
  - IAM権限拡大の自動承認
```

### セキュリティ修正ループ

```
Trigger:
  Dependabot Alert
  Trivy / Snyk / GitHub Advisory

Actions:
  - 脆弱性の影響範囲を確認
  - patch/minor更新で修正可能か確認
  - テストを実行
  - 修正PRを作成

Human Gate:
  - major updateが必要
  - 破壊的変更あり
  - 認証・認可周辺への影響あり
```

---

## Loop Engineering導入チェックリスト

導入前に以下を確認しましょう。

```
- [ ] ループの目的は明確か
- [ ] 成功条件は測定可能か
- [ ] 停止条件は定義されているか
- [ ] 人間に戻す条件は明確か
- [ ] AIが使えるツールは限定されているか
- [ ] 禁止操作は定義されているか
- [ ] 実行ログは残るか
- [ ] 状態は次回に引き継がれるか
- [ ] テスト・Lint・Buildなどの検証があるか
- [ ] コスト上限はあるか
- [ ] 生成された変更を人間がレビューする運用があるか
- [ ] セキュリティ・本番影響のある操作は自動化対象外か
```

このチェックリストに答えられない場合、まだ自律度を上げるべきではありません。

---

## まとめ

Loop Engineeringは、「AIにうまいプロンプトを書く技術」ではありません。

それは、AIエージェントを開発・運用プロセスの中で安全に働かせるための、**制御設計** です。

重要なポイントは以下です。

* プロンプトではなく、反復する仕組みを設計する
* ゴール・状態・実行・検証・停止条件を明確にする
* 実装者と検証者を分ける
* 権限は最小限にする
* コストと理解負債を管理する
* 人間の判断ポイントを設計に組み込む

AIエージェント時代のエンジニアリングでは、コードを書く力だけでなく、AIが安全に働ける環境を設計する力が重要になります。

これからの開発者の仕事は、AIに毎回指示を出すことではなく、AIが正しく進み、間違えたら止まり、必要なときに人間へ戻ってくるループを設計することかもしれません。

---

## 参考

* Akshay Pachaar, “Loop Engineering Clearly Explained”
* Addy Osmani, “Loop Engineering”
* Business Insider, “Forget prompt engineering: 'Loop engineering' is all the rage now”
* Zenn, “Loop Engineering入門：AIコーディングエージェントを動かすシステムを設計する”
