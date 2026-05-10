---
id: "2026-05-09-cc-sdd-windsurf-skills-で-ai-開発フローを整える設計実装単体テストを迷子に-01"
title: "cc-sdd × Windsurf Skills で AI 開発フローを整える：設計・実装・単体テストを迷子にしないための運用設計"
url: "https://zenn.dev/conte0745/articles/198b5cf6512d64e2271a"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-05-09"
date_collected: "2026-05-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

AI コーディングを使うと、実装速度は大きく上がります。

一方で、実務で使い始めると、次のような問題が出ます。

* AI が最初の要件を途中で忘れる
* 実装が設計からずれる
* テスト観点が抜ける
* チームごと、開発者ごとに AI への指示がばらつく
* 「AI が作ったコード」をレビューする基準が曖昧になる

この問題を緩和するために、`cc-sdd` と Windsurf Skills を使って、AI 開発の流れを次のように整理します。

```
要件整理
  ↓
設計
  ↓
タスク分解
  ↓
実装
  ↓
単体テスト
  ↓
検証
```

この記事では、特に Windsurf Skills で cc-sdd を導入した場合に、「どのファイルを、どこまで書き換えるべきか」に重点を置きます。

※ [cc-sdd](https://github.com/gotalab/cc-sdd) とは、AGota / gotalab 氏による、Kiro 風の仕様駆動開発を AI コーディングエージェントに移植する OSS のこと。

※ Windsurf Skills とは、Windsurf の AI エージェントに特定の作業手順・ルール・制約・参照ファイルを教え、設計・実装・テストなどの工程を再利用可能な作業スキルとして実行させるための設定単位（Windsurf ではスラッシュコマンドではなく、`@` で呼び出します）。

---

## 対象読者

この記事は次のような人向けです。

* Windsurf で AI コーディングを使っている
* cc-sdd を導入したが、生成されたファイルの役割が分からない
* `AGENTS.md`、`.kiro/settings`、`.kiro/steering`、`.windsurf/skills` の違いが分からない
* チーム開発で AI コーディングのルールを標準化したい
* 既存アプリケーションに AI 開発フローを組み込みたい

---

## 目次

## cc-sdd とは

`cc-sdd` は、AI コーディングエージェント向けの仕様駆動開発、つまり Spec-Driven Development を支援するための仕組みです。

通常の AI コーディングでは、自然言語で指示してすぐにコードを書かせます。

一方で cc-sdd では、次のように段階を分けます。

```
requirements
  ↓
design
  ↓
tasks
  ↓
implementation
```

つまり、いきなり実装するのではなく、

1. 要件を整理する
2. 設計を作る
3. 実装タスクへ分解する
4. 実装する
5. 検証する

という流れを AI に守らせるための枠組みです。

---

## インストール

この記事は、cc-sdd v3 系の Skills mode を前提にしています。  
v1 / v2 系の command mode とは、呼び出し方や生成される成果物が一部異なります。

Windsurf Skills として使う場合は、次のように導入します。

```
npx cc-sdd@latest --windsurf-skills --lang ja
```

導入すると、主に次のような構成になります。

```
.
├── AGENTS.md
├── .kiro/
│   ├── settings/
│   ├── steering/
│   └── specs/
└── .windsurf/
    └── skills/
```

---

## まず結論：どこに何を書くか

最初に整理すると、次のように分けるのがよいです。

```
AGENTS.md
  → プロジェクトの入口説明書

.kiro/steering/
  → プロジェクト固有の恒久的な設計・実装判断ルール

.kiro/settings/
  → cc-sdd のテンプレート・生成ルール・検証ルール

.kiro/specs/<spec名>/
  → 個別機能・個別修正ごとの成果物

.windsurf/skills/
  → Windsurf が実行する cc-sdd の skill 本体（原則編集しない）
```

重要なのは、`.windsurf/skills/` は基本的に編集しない ことです。

開発チーム独自のルールは、skill 本体ではなく、次の場所に書きます。

```
AGENTS.md
.kiro/steering/
.kiro/settings/
.kiro/settings/templates/
.kiro/settings/rules/
.kiro/specs/
```

---

## `.windsurf/skills/` の役割

Windsurf Skills で導入すると、例えば次のような skill が生成されます。

```
kiro-debug
kiro-discovery
kiro-impl
kiro-review
kiro-spec-batch
kiro-spec-design
kiro-spec-init
kiro-spec-quick
kiro-spec-requirements
kiro-spec-status
kiro-spec-tasks
kiro-steering
kiro-steering-custom
kiro-validate-design
kiro-validate-gap
kiro-validate-impl
kiro-verify-completion
```

これらは、Windsurf から呼び出すための実行部品です。

役割を大きく分けると次の通りです。

| skill | 役割 |
| --- | --- |
| `kiro-discovery` | 何を作るべきか、spec 化すべきかを整理する |
| `kiro-spec-init` | 新しい spec を作成する |
| `kiro-spec-batch` | 大きな取り組みを複数 spec に分解する |
| `kiro-spec-quick` | 小さめの spec を素早く作る |
| `kiro-spec-requirements` | 要件定義を作る |
| `kiro-spec-design` | 設計を作る |
| `kiro-spec-tasks` | 実装タスクへ分解する |
| `kiro-impl` | tasks に基づいて実装する |
| `kiro-debug` | 失敗した実装・テストの原因を調査する |
| `kiro-review` | 仕様・設計・実装をレビューする |
| `kiro-validate-design` | 設計が要件を満たしているか確認する |
| `kiro-validate-impl` | 実装が仕様・設計・タスクを満たしているか確認する |
| `kiro-validate-gap` | 要件・設計・実装のズレを検出する |
| `kiro-verify-completion` | 完了判定を行う |
| `kiro-steering` | プロジェクトの恒久ルールを作る |
| `kiro-steering-custom` | 個別の追加ルールを作る |

`.windsurf/skills/` は、フレームワーク側の実行ロジックに近い場所です。

そのため、チーム独自の開発ルールをここに直接書くのは避けます。

理由は次の通りです。

* cc-sdd 更新時に上書きされる可能性がある
* 本来の拡張ポイントは `.kiro/settings` や `.kiro/steering` 側である
* レビュー対象として分かりにくい

---

## `AGENTS.md` の役割

`AGENTS.md` は、AI エージェント向けのプロジェクトの説明書です。

ここには、プロジェクトの概要や、最初に把握してほしい前提を書きます。

### 書く内容

例：

```
- このプロジェクトが何をするアプリか
- 採用技術
- ディレクトリ構成
- 開発時の基本方針
- 重要な禁止事項
```

### 書きすぎない

`AGENTS.md` にすべてのルールを書くと、肥大化します。  
`AGENTS.md` はあくまで入口です。詳細な設計ルールや実装ルールは `.kiro/steering/` に分けます。

プロジェクトの全体像が分かる程度に留めます。

---

## `.kiro/steering/` の役割

`.kiro/steering/` は、プロジェクト固有の恒久的な判断ルールを書く場所です。

`AGENTS.md` が「入口説明書」なら、`.kiro/steering/` は「設計・実装の判断基準」です。

### 向いている内容

```
- アーキテクチャ方針
- トランザクション方針
- ログ設計方針
- エラー処理方針
- API 設計方針
- DB 設計方針
- 単体テスト方針
```

### おすすめ構成

```
.kiro/steering/
├── product.md
├── architecture.md
├── design-rules.md
├── implementation-rules.md
├── testing-rules.md
├── database-rules.md
```

1ファイルに詰め込みすぎるより、関心ごとで分割した方が AI が参照しやすくなります。

---

## `.kiro/settings/` の役割

`.kiro/settings/` は、cc-sdd の動作ルールやテンプレートを置く場所です。

ここはプロジェクト固有にカスタマイズしてよいです。

特に重要なのは次です。

```
.kiro/settings/templates/
.kiro/settings/rules/
```

`templates/` には、requirements / design / tasks の出力形式を書きます。  
`rules/` には、AI がそれらを生成・検証するときの判断基準を書きます。

---

## `.kiro/settings/templates/requirements.md`

要件定義の出力形式を決めるテンプレートです。

ここには、要件定義時に必ず含めたい項目を書きます。

### 例

```
- 背景
- 目的
- 対象範囲
- 非対象範囲
- ユーザーストーリー
- 受け入れ条件
- 正常系
- 異常系
- 制約
- 未決事項
```

テンプレートなので、詳細を書きすぎる必要はありません。

「何を実装すべきか」が明確であれば十分です。

---

## `.kiro/settings/templates/design.md`

設計書の出力形式を決めるテンプレートです。

### 例

```
- 概要
- 変更対象
- 画面/API/バッチの変更点
- レイヤ別責務
- File Structure Plan
- DB変更有無
- トランザクション境界
- SQL方針
- バリデーション
- エラー処理
- ログ方針
- セキュリティ影響
- 性能影響
- テスト方針
```

設計テンプレートはやや厚めでよいです。

特に次のような項目は、最初からテンプレートに入れておくと効果があります。

```
- トランザクション境界
- DB変更有無
- 既存データ影響
- 外部API影響
- 非同期処理影響
- 変更ファイルと責務境界
- ログ出力方針
- テスト観点
```

cc-sdd v3 系では、設計段階で実装範囲の境界を明確にする考え方が重要です。  
そのため、どのファイルを変更するかだけでなく、「そのファイルが何を担当し、どこから先を担当しないか」も設計に含めると、後続の tasks や実装がぶれにくくなります。

---

## `.kiro/settings/templates/tasks.md`

実装タスク分解の出力形式を決めるテンプレートです。

ここでは、実装だけでなくテストもタスク化します。

### 例

```
- 実装タスク
- Boundary
- Depends
- DBマイグレーション
- Mapper修正（レイヤードアプリケーションなどの場合）
- Service修正（レイヤードアプリケーションなどの場合）
- Controller修正（レイヤードアプリケーションなどの場合）
- 画面修正
- 単体テスト追加
- 結合観点
- 動作確認
- ドキュメント更新
```

タスクテンプレートは、細かすぎると運用しづらくなります。

ただし、次は必ず含めた方がよいです。

```
- 実装タスク
- テストタスク
- 検証タスク
- ドキュメント更新タスク
```

cc-sdd v3 系では、tasks に `_Boundary:_` や `_Depends:_` のような境界・依存情報を持たせる流れがあります。  
これにより、AI がタスクごとの責務範囲を越えて実装してしまうリスクを下げられます。

---

## `.kiro/settings/rules/` の役割

`.kiro/settings/rules/` は、cc-sdd が requirements / design / tasks を作るときの判断基準を書く場所です。

`templates/` が「出力の型」なら、`rules/` は「生成・検証時の判断ルール」です。

向いている内容は次です。

```
- 要件定義で曖昧な表現を避けるルール
- 設計時に必ず確認する観点
- タスク分解時の粒度
- テスト観点の出し方
- 完了判定の基準
```

一方で、プロジェクト固有のアーキテクチャ方針やコーディング規約は `.kiro/steering/` に置く方が分かりやすいです。  
`.kiro/settings/rules/` には、cc-sdd の成果物をどう作るか、どう検証するかを書きます。

---

## `.kiro/specs/<spec名>/` の役割

`.kiro/specs/<spec名>/` は、個別機能や個別不具合修正ごとの成果物を置く場所です。

例：

```
.kiro/specs/add-schedule-comment/
├── brief.md
├── requirements.md
├── design.md
└── tasks.md
```

複数 spec に分けるような大きな取り組みでは、`roadmap.md` が作られる場合もあります。

ここには、その spec に閉じた情報だけを書きます。

### 書く内容

```
requirements.md
  → その機能・修正の要件

design.md
  → その機能・修正の設計、変更ファイル、責務境界

tasks.md
  → その機能・修正の実装タスク、境界、依存関係

brief.md
  → discovery で整理した背景、目的、進め方

roadmap.md
  → 複数 spec に分ける場合の全体計画
```

### 書かない内容

```
- プロジェクト全体の設計方針
- 全体のコーディング規約
- 全機能共通のテスト方針
```

それらは `.kiro/steering/` に書きます。  
1 spec が巨大化しすぎる場合は、分割を検討します。

---

## 設計・実装・単体テストとの対応

自分の開発フローを伝統的なWF開発に準して次の3つに分けるとします。

cc-sdd では次のように対応させると分かりやすいです。

| 自分の工程 | cc-sdd の対応 skill | 主な成果物 |
| --- | --- | --- |
| 基本設計 | `kiro-spec-requirements` / `kiro-spec-design` / `kiro-validate-design` | `requirements.md`, `design.md` |
| 実装 | `kiro-spec-tasks` / `kiro-impl` | `tasks.md`, 実装コード |
| 単体テスト | `kiro-impl` / `kiro-debug` / `kiro-validate-impl` / `kiro-verify-completion` | テストコード、検証結果 |

単体テスト専用の skill があるというより、`kiro-impl` が実装とテスト作成を含み、`kiro-validate-impl` や `kiro-verify-completion` が検証を担当する、という整理です。

---

## 推奨フロー

推奨フローは、Windsurf 上で `@` コマンドを使用して実行します。これらのコマンドは、`.windsurf/skills/` に定義されたスキルを参照しており、各工程を効率的に進めるためのテンプレートやルールが含まれています。

### 1. steering を作る

既存プロジェクトでは最初にこれを行います。

目的は、プロジェクト固有の構成・設計方針・実装ルールを AI に把握させることです。

### 2. 必要に応じて steering を追加する

```
@kiro-steering-custom <作りたいルール>
```

例：

```
@kiro-steering-custom Spring Boot のレイヤ構成ルール
@kiro-steering-custom MyBatis のSQL実装ルール
@kiro-steering-custom 単体テストの作成ルール
```

### 3. まず discovery から始める

```
@kiro-discovery <アイデアや課題>
```

`kiro-discovery` は、作業をそのまま実装するか、既存 spec を拡張するか、新しい spec を作るか、複数 spec に分けるかを整理する入口として使えます。  
迷う場合だけでなく、最初の振り分けとして使うと後続の流れを決めやすくなります。

### 4. 新しい spec が必要なら spec を作る

大きな取り組みを複数 spec に分ける場合は、`kiro-spec-batch` を使います。

### 5. 要件を作る

### 6. 設計を作る

### 7. 設計を検証する

### 8. 実装タスクへ分解する

### 9. 実装する

### 10. テスト失敗や不具合が出たら debug する

### 11. 実装の整合性を確認する

### 12. 完了判定する

---

## 不具合修正にも cc-sdd を使うべきか

使えます。

ただし、すべての不具合修正に使うと重くなります。

### cc-sdd を使うべき不具合

```
- 仕様が曖昧
- 原因が複数モジュールにまたがる
- DB変更を伴う
- API仕様が変わる
- 画面仕様が変わる
- トランザクション境界が変わる
- 認証、認可、CSRF、セッションに関わる
- 再発防止テストが必要
```

### cc-sdd を使わなくてよい不具合

```
- typo
- CSSの軽微な崩れ
- 単純な条件式ミス
- 1ファイルで閉じる小さな修正
```

判断基準は次です。

YES なら cc-sdd を使います。

NO なら通常の AI コーディングや通常の PR で十分です。

---

## cc-sdd と通常の AI コーディングの使い分け

cc-sdd と通常の AI コーディングは競合しません。

役割が違います。

| 観点 | cc-sdd | 通常の AI コーディング |
| --- | --- | --- |
| 強み | 仕様固定、再現性、チーム開発 | 速度、試行錯誤、軽微修正 |
| 向いている変更 | 新規機能、仕様変更、大きな不具合修正 | 小修正、UI調整、PoC |
| 弱み | 初期コストがある | 仕様ドリフトしやすい |
| 成果物 | requirements / design / tasks / code / test | 主に code / test |

おすすめは、次の使い分けです。

```
小さい修正:
  通常の AI コーディング

仕様に関わる変更:
  cc-sdd

DB / API / 認証 / トランザクションに関わる変更:
  cc-sdd 推奨
```

---

## 運用上のアンチパターン

### `.windsurf/skills/` を直接編集する

避けた方がよいです。

独自ルールは `.kiro/steering/` または `.kiro/settings/` に書きます。

### `AGENTS.md` に全部書く

これも避けます。

`AGENTS.md` は入口説明に留め、詳細ルールは steering に分けます。

### spec なしで大きな実装を始める

AI コーディングでは最も事故りやすいパターンです。

大きな変更では、先に requirements / design / tasks を作るべきです。

### テストを tasks に入れない

実装タスクだけを作ると、テストが後回しになります。

`tasks.md` には必ずテストタスクを含めます。

### 軽微修正まで全部 cc-sdd に乗せる

これも避けた方がよいです。

cc-sdd は強力ですが、軽微な修正には重いです。

```
軽微修正:
  通常の AI コーディング

仕様変更:
  cc-sdd
```

と分けるのが現実的です。

---

## まとめ

cc-sdd × Windsurf Skills を使うと、AI コーディングを単なる「その場のコード生成」ではなく、仕様駆動の開発フローに寄せられます。

整理すると次の通りです。

```
.windsurf/skills/
  → 実行部品
  → 原則編集しない

AGENTS.md
  → プロジェクトの入口説明

.kiro/steering/
  → 恒久的な設計・実装判断ルール

.kiro/settings/
  → cc-sdd のテンプレート・生成ルール・検証ルール

.kiro/specs/
  → 個別機能・個別修正の成果物
```

チーム開発で重要なのは、AI に毎回同じ説明をするのではなく、プロジェクトの知識と判断基準をファイルとして固定することです。

これにより、AI コーディングの速度を活かしつつ、設計・実装・単体テストの品質をチームで揃えやすくなります。
