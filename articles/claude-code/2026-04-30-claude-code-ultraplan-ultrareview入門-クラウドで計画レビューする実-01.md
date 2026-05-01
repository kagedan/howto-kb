---
id: "2026-04-30-claude-code-ultraplan-ultrareview入門-クラウドで計画レビューする実-01"
title: "Claude Code Ultraplan & Ultrareview入門 — クラウドで計画・レビューする実践ガイド"
url: "https://qiita.com/kai_kou/items/fe63afd97fe6e2aaf0a4"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-30"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

## はじめに

Claude Code でコードを書いていると、次の2つの場面でターミナルの限界を感じることがあります。

- **大きな機能の実装計画を立てる場面**: テキストだけのプランを見ながら「ここを修正してほしい」と何度もやり取りするのは不便
- **マージ前に深いコードレビューをしたい場面**: ローカルの `/review` は速いが、複雑な変更では見落としが心配

これを解決するのが、Claude Code の新機能 **Ultraplan**（計画をクラウドへ）と **Ultrareview**（レビューをクラウドへ）です。

### この記事で学べること

- Ultraplan でプランニングをクラウドにオフロードし、ブラウザで精密にフィードバックする方法
- Ultrareview でマルチエージェントが並列実行する深いコードレビューをマージ前に走らせる方法
- 2つの機能の使い分けとワークフローへの組み込み方

### 対象読者

- Claude Code を日常的に使うエンジニア
- 大規模なリファクタリングや機能追加で計画フェーズを丁寧にやりたい方
- マージ前のバグ検出精度を上げたい方

### 前提環境

- Claude Code v2.1.91 以降（Ultraplan）、v2.1.86 以降（Ultrareview）
- Claude.ai アカウント（Pro または Max プラン）
- GitHub リポジトリ

---

## TL;DR

- **Ultraplan**: `/ultraplan {タスク}` でプランニングをクラウドに移譲。ブラウザでインラインコメントを付けて精緻化し、クラウドまたはローカルで実装
- **Ultrareview**: `/ultrareview` でマルチエージェントがクラウド上でバグを並列検証。Pro/Max は 3 回無料（2026年5月5日まで）
- 両機能とも **Bedrock / Vertex AI / Foundry では利用不可**（Claude.ai アカウント必須）

---

## Ultraplanとは

Ultraplan は、Claude Code の CLI から計画タスクを **Claude Code on the web** のクラウドセッションに移譲する機能です。

```
/ultraplan migrate the auth service from sessions to JWTs
```

従来のローカルプランニングとの違いは以下の通りです。

| 項目 | ローカルプラン | Ultraplan |
|------|--------------|-----------|
| 実行場所 | ローカルターミナル | Anthropic クラウド |
| レビュー方法 | テキストベース | ブラウザでインラインコメント |
| ターミナルの占有 | プラン中は占有 | 解放される |
| フィードバック粒度 | 会話全体への返答 | 段落単位でコメント |

ターミナルが解放されるため、Ultraplan がクラウドで動いている間、ローカルで別の作業を並行できます。

### Ultraplan の仕組み

Ultraplan を起動すると、Claude Code は GitHub リポジトリを一時クラウドコンテナにクローンし、**Plan Mode** でコードベースを解析します。完成したプランはインタラクティブな Web UI に表示され、レビュー待ちになります。


> Ultraplan は **Research Preview** です。Claude Code v2.1.91 以降が必要で、GitHub リポジトリと Claude.ai アカウント（Pro または Max）が前提です。Amazon Bedrock・Google Cloud Vertex AI・Microsoft Foundry では使用できません。


---

## Ultraplan の使い方

### ステップ1: 起動する（3つの方法）

**方法A: `/ultraplan` コマンド**

最も明示的な方法です。

```
/ultraplan migrate the auth service from sessions to JWTs
```

**方法B: 通常プロンプトに "ultraplan" を含める**

会話の流れで自然に起動できます。

```
I need an ultraplan for refactoring the payment module to support multi-currency.
```

**方法C: ローカルプランから昇格させる**

Claude がローカルでプランを作り終えたとき、承認ダイアログで **「No, refine with Ultraplan on Claude Code on the web」** を選ぶと、そのプランがクラウドに転送されます。この経路はダイアログ選択自体が確認なので、追加の確認ダイアログは表示されません。


> Ultraplan 起動中は [Remote Control](/en/remote-control) が自動的に切断されます。両機能は claude.ai/code インターフェースを共有するため、同時実行できません。


### ステップ2: ターミナルのステータスを確認する

起動後、CLI のプロンプト入力欄にステータスインジケーターが表示されます。

| ステータス | 意味 |
|-----------|------|
| `◇ ultraplan` | Claude がコードベースを調査・プランを下書き中 |
| `◇ ultraplan needs your input` | Claude が確認事項を質問中（ブラウザで回答） |
| `◆ ultraplan ready` | プランが完成。ブラウザで確認可能 |

`/tasks` を実行してUltraplanエントリを選ぶと、セッションリンク・エージェントアクティビティ・**Stop ultraplan** アクションを含む詳細ビューを開けます。

### ステップ3: ブラウザでレビューして実行する

`◆ ultraplan ready` になったらセッションリンクを開きます。

**レビュー操作**

- **インラインコメント**: 任意のテキストをハイライトしてコメントを追加 → Claude が当該箇所を修正
- **絵文字リアクション**: 承認・懸念を絵文字でシグナル
- **アウトラインサイドバー**: 長いプランのセクション間をジャンプ

何度でも改訂できます。プランに満足したら、実行場所を選びます。

**実行オプション A: クラウドで実装**

**「Approve Claude's plan and start coding」** を選ぶと、同じクラウドセッションで実装が進みます。完了後は Web インターフェースからDiffをレビューし、PR を作成します。

**実行オプション B: ターミナルに転送**

**「Approve plan and teleport back to terminal」** を選ぶと、プランがローカルに転送されます。ターミナルに以下のダイアログが表示されます。

| オプション | 動作 |
|-----------|------|
| **Implement here** | 現在の会話にプランを注入して継続 |
| **Start new session** | 新しいセッションを開始（上部に `claude --resume` コマンドを表示） |
| **Cancel** | プランをファイルに保存のみ（ファイルパスを表示） |

---

## Ultrareviewとは

Ultrareview は、マージ前の深いコードレビューをクラウド上のマルチエージェントフリートで実行する機能です。

```
/ultrareview
```

通常の `/review` との最大の違いは、**すべての指摘が独立したエージェントによって再現・検証される**点です。誤検知が大幅に減り、実際のバグに絞った結果が返ってきます。

### `/review` と `/ultrareview` の比較

| 項目 | `/review` | `/ultrareview` |
|------|-----------|----------------|
| 実行場所 | ローカルセッション | クラウドサンドボックス |
| 深度 | シングルパスレビュー | マルチエージェント + 独立検証 |
| 所要時間 | 数秒〜数分 | 5〜10 分 |
| コスト | 通常使用に含む | 無料枠後は $5〜$20 / 回（extra usage）|
| 適した用途 | 開発中の高速フィードバック | マージ前の確信を得たい場面 |


> Ultrareview は **Research Preview** です。Claude Code v2.1.86 以降が必要です。Claude.ai アカウントで認証（`/login`）が必要で、Bedrock・Vertex AI・Foundry では使用できません。また、Zero Data Retention を有効にしている組織では使用できません。


---

## Ultrareview の使い方

### 基本: ブランチのレビュー

引数なしで実行すると、現在ブランチとデフォルトブランチのdiffをレビューします（コミット済み・未コミット・ステージング済みの変更を含む）。

```
/ultrareview
```

起動前に、以下を示す確認ダイアログが表示されます。

- レビュースコープ（ファイル数・行数）
- 残りの無料実行回数
- 推定コスト

確認後はバックグラウンドで実行されるため、セッションで他の作業を継続できます。

### PR モード: Pull Request をレビュー

PR 番号を渡すと、GitHub から直接 PR をクローンしてレビューします。

```
/ultrareview 1234
```


> PR モードには `github.com` リモートが設定されたリポジトリが必要です。リポジトリが大きすぎてバンドルできない場合、Claude Code はPRモードの使用を促します。


### 結果の確認

レビューには通常 5〜10 分かかります。完了すると、セッションに通知として結果が表示されます。各指摘には以下が含まれます。

- ファイルの場所（行番号）
- 問題の説明

指摘を見てすぐ `Claude、これを修正して` と頼めます。

進行中のレビューは `/tasks` で確認・停止できます。停止した場合、途中の結果は返ってきません。

### 料金体系

Pro・Max ユーザーは 2026年5月5日までに使える **3回分の無料実行枠** があります。

| プラン | 無料実行 | 有料時の単価 |
|-------|---------|------------|
| Pro | 3回（2026年5月5日まで） | $5〜$20 / 回（extra usage）|
| Max | 3回（2026年5月5日まで） | $5〜$20 / 回（extra usage）|
| Team / Enterprise | なし | $5〜$20 / 回（extra usage）|

有料の場合は **extra usage** として課金されるため、事前に extra usage を有効にしておく必要があります。`/extra-usage` で現在の設定を確認・変更できます。

---

## Ultraplan と Ultrareview の使い分け

2つの機能は、開発サイクルの**異なるフェーズ**をカバーします。

```
[実装前]              [実装中]         [マージ前]
  ↓                    ↓                 ↓
Ultraplan           /review          Ultrareview
（クラウドでプラン）   （ローカル高速）   （クラウド深堀り）
```

### 推奨ワークフロー

**大きな機能追加・リファクタリング時:**

1. `ultraplan で認証サービスをJWT方式に移行する計画を立てて` と依頼
2. ブラウザでプランをレビュー・コメントでフィードバック
3. `Approve plan and teleport back to terminal` → `Implement here` でローカル実装
4. 実装中は `/review` で高速フィードバックを繰り返す
5. PR を作成したら `/ultrareview {PR番号}` でマージ前の最終確認

**小さなバグ修正・軽微な変更時:**

- Ultraplan / Ultrareview は不要
- ローカルの Claude Code で実装・`/review` で確認して PR

---

## まとめ

Claude Code の Ultraplan と Ultrareview は、クラウドインフラを活用して**計画とレビューの品質を大幅に向上**させる機能です。

- **Ultraplan**: ブラウザの豊富なレビューUIでプランを精緻化し、クラウドまたはローカルで実装を選べる
- **Ultrareview**: マルチエージェントが独立検証した高信頼度のバグ指摘をマージ前に受け取れる
- 両機能とも Claude.ai アカウント（Pro/Max）が必要で、Bedrock/Vertex AI/Foundry では使用不可

どちらも Research Preview 段階ですが、大規模な変更を扱う場面では今すぐ試す価値があります。Pro/Max ユーザーは Ultrareview の無料枠（3回）を 2026年5月5日までに使い切りましょう。

## 参考リンク

- [Plan in the cloud with ultraplan — Claude Code Docs](https://code.claude.com/docs/en/ultraplan)
- [Find bugs with ultrareview — Claude Code Docs](https://code.claude.com/docs/en/ultrareview)
- [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)
- [Claude Code: Plan mode](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode)
