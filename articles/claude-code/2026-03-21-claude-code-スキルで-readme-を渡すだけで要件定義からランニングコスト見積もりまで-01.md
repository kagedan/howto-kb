---
id: "2026-03-21-claude-code-スキルで-readme-を渡すだけで要件定義からランニングコスト見積もりまで-01"
title: "Claude Code スキルで README を渡すだけで要件定義からランニングコスト見積もりまでを自動化する"
url: "https://zenn.dev/kazusa_nakagawa/articles/article14_claude_code_skill_estimate"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

## はじめに

時間が限られた状況で、要件から実現可否・見積もりを出す必要がある場合に叩き台として使える **Skills** を作成してみました。

精度はブラッシュアップしながら上げていければと考えています。工数設定が大きい気がする。。。

すでに有用な情報はあるかと思いますが、私なりに Claude Skills 機能の理解を深めたく作成しました。

1. **README → 要件分析 → 顧客向けサマリー + 設計書**（`req-estimate`）
2. **設計書 → DB設計書**（`db-design`）
3. **設計書 + DB設計書 → 詳細設計書**（`detail-design`）
4. **設計書 → 月額ランニングコスト + 3年間TCO**（`running-cost`）
5. **サマリー → 経営者向け提案書**（`proposal`）
6. **設計書 → 規約・ポリシー調査レポート**（`req-investigate`）
7. **詳細設計書 → ジョブ処理API設計書**（`job-api-design`）※非同期ジョブ処理が含まれる場合のみ
8. **ジョブ設計書 → 運用監視設計書**（`ops-monitoring`）※`job-api-design` 実行時のみ

そして上記スキルを **一括で全実行** する親スキルを `req-full` にしています。

実際の出力サンプルは、自作の英語学習アプリ（EnglishLearnApp）の **Web版移植**を題材に実行した結果を使います。「どんな粒度で出力されるか」をイメージしながら読んでいただけると幸いです。

## リポジトリ

<https://github.com/KazusaNakagawa/claude_docs/>

---

## Claude Code スキルとは

Claude Code には **スキル（Skill）** という仕組みがあり、よく使う複雑なタスクを「名前付きのプロンプトセット」として定義・再利用できます。

```
~/.claude/skills/
├── req-estimate/       ← 要件分析・工数見積もり
│   └── SKILL.md
├── db-design/          ← DB設計・ER図
│   └── SKILL.md
├── detail-design/      ← 詳細設計・シーケンス図・API仕様
│   └── SKILL.md
├── running-cost/       ← ランニングコスト・TCO算出
│   └── SKILL.md
├── proposal/           ← 経営者向け提案書
│   └── SKILL.md
├── req-investigate/    ← 規約・ポリシー調査
│   └── SKILL.md
├── job-api-design/     ← ジョブ処理・バッチ系API詳細設計
│   └── SKILL.md
├── ops-monitoring/     ← CloudWatch + Slack 監視運用設計
│   └── SKILL.md
└── req-full/           ← 上記スキルを一括実行する親スキル
    └── SKILL.md
```

スキルを登録しておくと、Claude Code のチャットで `/スキル名 [ファイルパス]` のように呼び出せます。

---

## 今回使うスキル

### 1. `req-estimate` — 要件見積もり・実現可否判断スキル

顧客から受け取った `readme.md` をもとに、以下を **15分程度** で自動生成します。

※今回は、自作した英語アプリを基にしています。

| 出力ファイル | 対象読者 | 内容 |
| --- | --- | --- |
| `01.customer-summary.md` | 顧客・非技術者 | 対応可否・工数・リスクをわかりやすく |
| `02.design-doc.md` | 開発者 | アーキテクチャ図・工数明細・フェーズ計画 |

**対応技術スタック**: React / TypeScript（フロント）、Python（バックエンド）、AWS（インフラ）

---

### 2. `db-design` — DB設計スキル

`design-doc.md` または要件書を受け取り、`db-design.md` を生成します。

* ER図（Mermaid `erDiagram`）
* テーブル定義（カラム・型・制約・インデックス）
* AWS DBサービス選定（RDS / Aurora / DynamoDB の比較と選定根拠）
* マイグレーション方針（Alembic）

---

### 3. `detail-design` — 詳細設計スキル

`design-doc.md` と `db-design.md` を受け取り、**実装者がコードを書き始められる**レベルを意識して `detail-design.md` を生成します。

* シーケンス図（最大5枚: メインフロー・認証・エラー等）
* API仕様（エンドポイント・リクエスト・レスポンス・エラー定義）
* エラーハンドリング方針
* 環境変数一覧
* テスト仕様（単体・結合・E2E）

---

### 4. `running-cost` — ランニングコスト試算スキル

`design-doc.md`（アーキテクチャ設計）を読み込み、以下を算出した `running-cost.md` を生成します。

* **AWSインフラコスト**（東京リージョン / 1USD=150円換算）
* **運用・保守コスト**（工数単価10万円/人日）
* **障害対応コスト**（SLA別シナリオ）
* **3年間TCO**（開発費 + 運用コスト合計）

---

### 5. `proposal` — 経営者向け提案書スキル

`customer-summary.md` と設計書を受け取り、**意思決定者向けの提案書** `proposal.md` を生成します。

技術的な話を排除し、「何が解決されるか」「いくらかかるか」「いつ終わるか」「何が心配か」を1ページで伝えることにフォーカスします。Mermaid の Gantt チャートでスケジュールも可視化します。

---

### 6. `req-investigate` — 規約・ポリシー調査スキル

設計書・要件書を受け取り、**WebSearch を使って外部サービスの利用規約・API制約を実際に調べ**、`investigation-report.md` を生成します。

* 各外部サービスのToS・API制限・レート制限を調査
* 調査結果と出典URLをまとめる
* 顧客への確認事項を優先度付きで整理（🔴 高 / 🟡 中 / 🟢 低）

---

### 7. `job-api-design` — ジョブ処理API詳細設計スキル

`detail-design.md` または `design-doc.md` を受け取り、**SQS / Lambda / ECS Worker などの非同期ジョブ構成に特化した** `job-api-design.md` を生成します。

* ジョブスキーマ・キュー設計・ステータス管理
* ワーカー設計・リトライ/DLQ 設計
* スケジューリング・モニタリング

バッチ処理・非同期ジョブが含まれるシステムでは `detail-design` の後に実行します。

> **今回の case3（EnglishLearnApp Web版）では非同期ジョブ処理なし**。音声再生キューはブラウザ内の HTML5 Audio API で完結するため、このスキルはスキップされました。

---

### 8. `ops-monitoring` — 監視運用設計スキル

`job-api-design.md` または `detail-design.md` を受け取り、**AWS CloudWatch + Slack 通知を前提とした運用設計書** `ops-monitoring.md` を生成します。

* 日次ヘルスチェック・DLQ 監視・SLO 確認
* アラート対応フロー
* Slack 通知テンプレート（CloudWatch アラーム → SNS → Slack）

> **今回の case3 では `job-api-design` がスキップされたため、このスキルも実行されませんでした。** SQS / Worker 構成があるシステムで使います。

---

## 実際に動かしてみる

### 0. 事前準備

以下を実行してスキルファイルを生成します。

```
# 全スキルを一括パッケージ（SKILL.md があるディレクトリを自動検出）
cd skills/
bash install.sh
```

`README.md` 一枚でも要件が含まれていれば大丈夫です。  
情報が少ない場合は不明点・前提条件の確認項目が増え、出力の粒度が粗くなる傾向がありました。

```
# git clone で見積もりしたい対象を配置
./claude_docs/output/case3 (🍡 develop=) 
% git clone git@github.com:KazusaNakagawa/english_learn_app.git
```

![alt text](https://static.zenn.studio/user-upload/deployed-images/2beb21501ce4308deafa5d4c.png?sha=04cb5051a9591b4dedf6fcaf79230482dcb53da5)  
*git clone で見積もりしたい対象を配置*

![alt text](https://static.zenn.studio/user-upload/deployed-images/8ad76ebf5a513fb90aa046b9.png?sha=6c1897deaf58a05b53a2689820418e5c1f53f154)  
*Claude Code のチャットに生成したスキルをドラッグ&ドロップでインストール*

### 1. `req-full` で全スキルを一発実行

`req-full` は上記8スキルを **順番に自動実行する親スキル** です。

![alt text](https://static.zenn.studio/user-upload/deployed-images/3b5959820418349416630920.png?sha=9c70f7da05aace7664d03188dfa5529934eeb808)  
*チャットに上記のように投げる*

あとは Claude Code が `SKILL.md` を参照して自動的に処理します。これだけで最大9ファイルが一括生成されます。内部的には以下のステップが走ります。

| # | スキル | 出力ファイル | 備考 |
| --- | --- | --- | --- |
| 1 | req-estimate | 01.customer-summary.md, 02.design-doc.md | 常に生成 |
| 2 | db-design | 03.db-design.md | 常に生成 |
| 3 | detail-design | 04.detail-design.md | 常に生成 |
| 4 | job-api-design | 08.job-api-design.md | **条件付き**（SQS/Worker/バッチ処理が含まれる場合のみ） |
| 5 | ops-monitoring | 09.ops-monitoring.md | **条件付き**（Step 4 が実行された場合のみ） |
| 6 | running-cost | 05.running-cost.md | 常に生成 |
| 7 | proposal | 06.proposal.md | 常に生成 |
| 8 | req-investigate | 07.investigation-report.md | 常に生成 |

---

### 2. 個別スキルごとに実行したい場合

個別スキルごとに実行した場合（req-estimate / running-cost を例に）

### 1. req-estimate を実行する

```
手順A: 要件の読み取り・整理
  ├── 機能要件の抽出
  ├── 非機能要件の抽出
  └── 不明点・曖昧な箇所の洗い出し

手順B: 技術的実現可否の判断
  ├── 対応可能 / 条件付き対応可能 / 対応困難 を明示
  └── リスク箇所には理由を付記

手順C: 工数見積もり（3点見積もり法）
  ├── 機能・コンポーネント単位に分解
  ├── 楽観/通常/悲観 の3点見積もり
  ├── テスト工数（単体・結合・E2E・環境構築）を個別計上
  └── バッファ 20〜30% を加算

手順D: アーキテクチャ設計
  └── Mermaid 形式のアーキテクチャ図を必ず1枚含める
```

---

### 2. 出力サンプル: 01.customer-summary.md

実際に生成された顧客向けサマリーの例（EnglishLearnApp Web版移植）です。

```
# 要件確認・対応方針 — EnglishLearnApp Web版

## 対応可否
**対応可能**

iOS版で実績のある設計・インフラをそのままWeb版に転用できます。既存の VOICEVOX Lambda
エンドポイントを再利用し、React SPA を S3 + CloudFront でホスティングするアーキテクチャで、
追加バックエンドサーバーなしに全機能を実現できます。

## 概算工数・スケジュール感
| フェーズ | 内容 | 概算工数 |
|---------|------|---------|
| フェーズ0 | PoC・技術検証 | 5人日 |
| フェーズ1 | コア機能開発 | 38人日 |
| フェーズ2 | 発音チェック・QA・デプロイ | 17人日 |
| テスト | 単体・結合・E2E | 17人日 |
| バッファ（25%） | — | 19人日 |
| **合計** | — | **96人日（2人 × 約10週間）** |
・・・
```

---

### 3. 02.design-doc.md のアーキテクチャ図（自動生成）

`02.design-doc.md` には Mermaid 形式のアーキテクチャ図が自動で含まれます。

iOS版では ECS Fargate + Aurora + SQS だったアーキテクチャが、Web版では **サーバーレス SPA** になっています。既存の VOICEVOX Lambda を CORS 設定追加のみで再利用できるのがポイントです。

---

### 4. running-cost を実行する

`design-doc.md` が生成されたら、次に Claude Code に入力します。

```
design-doc.md からランニングコストを計算してください
```

これだけで `running-cost.md` が生成されます。

---

### 5. 出力サンプル: 05.running-cost.md

**月額コストサマリー**（EnglishLearnApp Web版、個人利用〜小規模5名想定）:

| サービス | 月額（税抜） |
| --- | --- |
| S3 | ¥5 |
| CloudFront | ¥190 |
| API Gateway | ¥1 |
| Lambda（Web版分増分） | ¥842 |
| **AWS合計** | **¥1,038/月** |

サーバーレス SPA + 既存 Lambda 共有という構成を選んだ結果、追加 AWS コストは **¥1,038/月** に抑えられています。OpenAI API 費用はユーザー自身のキーで支払うためインフラコストに含みません。

**3年間TCO**:

| 項目 | 金額 |
| --- | --- |
| 初期開発費 | ¥9,600,000（96人日 × 100,000円） |
| AWSインフラ（3年） | ¥37,368（¥1,038 × 36ヶ月） |
| 運用・保守（3年） | ¥1,800,000（¥50,000 × 36ヶ月） |
| 障害対応（3年） | ¥540,000（¥15,000 × 36ヶ月） |
| **3年間TCO合計** | **¥11,977,368** |

コスト最適化の提案も自動で出力されます。

| 施策 | 削減効果 | 実施タイミング |
| --- | --- | --- |
| IndexedDB 音声キャッシュ | Lambda 再実行を推定60〜80%削減 | フェーズ1 |
| CloudFront キャッシュポリシー最適化 | 転送コスト削減 | フェーズ1 |
| S3 音声キャッシュ（Lambda側） | 同一テキストの重複実行を排除 | フェーズ2 |
| Provisioned Concurrency | コールドスタート解消（50名以上で検討） | フェーズ2以降 |

---

## スキルの仕組み：SKILL.md の構造

スキルは `SKILL.md` という Markdown ファイルで定義します。  
メンテナンス時や出力が今ひとつの場合に随時修正していくイメージです。

```
---
name: running-cost
description: design-doc.md を受け取り、月額ランニングコスト・運用保守コスト・
  障害対応コスト・年間TCO を算出した running-cost.md を生成するスキル。
---

# running-cost

## Steps
### Step 1: アーキテクチャからコスト対象コンポーネントを抽出する
...（詳細な手順）

### Step 2: AWSインフラコストを算出する
- Fargate: vCPU時間 × $0.04048 + メモリGiB時間 × $0.004445
- Lambda: 100万リクエスト $0.20、GB秒 $0.0000166667
- Aurora Serverless v2: ACU時間 $0.12/ACU時間
...

## Output Template
### running-cost.md
...（出力テンプレート）

## Quality Checklist
- [ ] AWSインフラの全コンポーネントが網羅されているか
- [ ] 推定根拠が明記されているか
...
```

ポイントは以下の3つです。

1. **Steps**: Claude が実行する手順を具体的に記述する
2. **Output Template**: 出力形式を固定することで一貫した品質を保つ
3. **Quality Checklist**: 出力前の自己チェック項目

---

## まとめ

| スキル | 入力 | 出力ファイル | 対象読者 | 備考 |
| --- | --- | --- | --- | --- |
| `req-estimate` | readme.md | 01.customer-summary.md, 02.design-doc.md | 顧客・開発者 |  |
| `db-design` | 02.design-doc.md | 03.db-design.md | 開発者 |  |
| `detail-design` | 02.design-doc.md + 03.db-design.md | 04.detail-design.md | 開発者 |  |
| `running-cost` | 02.design-doc.md | 05.running-cost.md | 顧客・経営者 |  |
| `proposal` | 01.customer-summary.md | 06.proposal.md | 経営者・意思決定者 |  |
| `req-investigate` | 02.design-doc.md | 07.investigation-report.md | PM・開発者 |  |
| `job-api-design` | 04.detail-design.md | 08.job-api-design.md | 開発者 | ★条件付き |
| `ops-monitoring` | 08.job-api-design.md | 09.ops-monitoring.md | SRE・開発者 | ★条件付き |
| **`req-full`** | **readme.md** | **上記最大9ファイル一括** | **全員** |  |

Claude Code のスキル機能を使えば、**「README を渡す → ドキュメントができている」** という体験が実現できました。

見積もり精度の保証はできませんが、経験則で調整しながら初期検討・顧客向け提案・社内共有用のたたき台として使えると良さそうです。

---

## 参考
