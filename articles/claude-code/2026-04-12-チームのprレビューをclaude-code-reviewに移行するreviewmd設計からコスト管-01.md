---
id: "2026-04-12-チームのprレビューをclaude-code-reviewに移行するreviewmd設計からコスト管-01"
title: "チームのPRレビューをClaude Code Reviewに移行する、REVIEW.md設計からコスト管理まで"
url: "https://qiita.com/moha0918_/items/1176df010b1a7aeadff1"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

PRのレビュー待ちが数日かかる、レビュアーによって指摘の粒度がバラバラ、セキュリティ系の見落としが後から発覚する。チームが大きくなるほど、こうした問題は避けにくくなります。

Claude Code Reviewは、PRが開くたびに複数の専門エージェントがコードを並列で分析し、インラインコメントとして結果を返す管理サービスです。GitHub Actionsで自前構築するのとは異なり、Anthropicのインフラ上で動くフルマネージド形式で、設定はadmin画面から数クリックで完結します。

Team・Enterpriseプランのみが対象です。1レビューあたり平均$15〜25のコストがかかります（PRサイズと複雑さで変動）。

## 仕組みを理解する

レビューが走ると、複数のエージェントがdiffと周辺コードを並行して分析します。それぞれが異なる種類の問題（ロジックエラー、セキュリティ脆弱性、エッジケース等）を担当し、最後に検証ステップで誤検知をフィルタリングします。レビューは平均20分で完了します。

結果は3つの重要度でタグ付けされます:

| 重要度 | 意味 |
| --- | --- |
| `Important` | マージ前に修正すべきバグ |
| `Nit` | 軽微な問題（ブロッキングではない） |
| `Pre-existing` | このPRとは無関係の既存バグ |

`Pre-existing` の存在が地味に便利です。「このPRで入ったバグなのか、元々あったのか」の切り分けを自動でやってくれます。PRをブロックする仕組みではないので、既存のレビューフローを壊さずに導入できます。

## セットアップ手順

admin権限を持つメンバーが一度だけ設定します。GitHub organizationへの管理者権限も必要です。

1. `claude.ai/admin-settings/claude-code` でCode Reviewセクションを開く
2. `Setup` をクリックし、GitHub Appインストールフローへ進む
3. 必要な権限を許可する（`Contents`、`Issues`、`Pull requests` への read/write）
4. レビュー対象のリポジトリを選択する

リポジトリを追加したあと、`Review Behavior` を各リポジトリ単位で設定します:

| モード | 動作 | 向いているケース |
| --- | --- | --- |
| `Once after PR creation` | PR作成時に1回 | 安定したリポジトリ |
| `After every push` | プッシュのたびに実行 | 継続的フィードバックが欲しい場合 |
| `Manual` | `@claude review` で手動起動 | コスト重視のリポジトリ |

`After every push` は最もコストがかかります。ブランチに20回プッシュするPRなら、単純計算で20倍のコストになります。まずは `Once after PR creation` か `Manual` から試すのが安全です。

## REVIEW.mdでチームの基準を統一する

`REVIEW.md` はCode Review専用の指示ファイルです。デフォルトでは正確性（バグ）だけを見ますが、このファイルでチェック範囲を広げられます。

```
# Code Review Guidelines

## Always check
- 新しいAPIエンドポイントには結合テストを追加すること
- DBマイグレーションは後方互換性を保つこと
- エラーメッセージにスタックトレースやDB内部情報を含めないこと

## Style
- ネストした条件より early return を使うこと
- ログにはf-string補間でなく構造化ログを使うこと

## Skip
- src/gen/ 以下の自動生成ファイル
- *.lock ファイルのフォーマット変更のみのPR
```

リポジトリルートに置くだけで自動で読み込まれます。追加設定は不要です。

`CLAUDE.md` との使い分けも重要です。インタラクティブなClaude Codeセッションにも適用したいルールは `CLAUDE.md` に書き、レビュー専用の指摘ルールは `REVIEW.md` に分離します。こうすることで、対話セッション中に余計な制約が入らなくなります。

## 手動トリガーの使い方

`@claude review` と `@claude review once` は動作が異なります:

```
# PRを以後のプッシュでも自動レビュー対象にする
@claude review

# 現在の状態だけを1回レビューする
@claude review once
```

`Manual` モードで運用しながら、コードが固まったタイミングで `@claude review` を打つのが現実的なパターンです。`@claude review once` はドラフトPRの途中チェックや、長期間プッシュが続くPRで一時的にレビューしたいときに使います。

ひとつ注意点として、GitHubのChecksタブにある `Re-run` ボタンではCode Reviewは再実行されません。失敗したレビューを再実行するには `@claude review once` コメントを使います。初見だと戸惑いやすい部分です。

## コスト管理

運用を始めると、コストが集中するリポジトリが出てきます。

* 月次上限: `claude.ai/admin-settings/usage` からClaude Code Reviewサービス単位でキャップを設定できます
* 使用状況の確認: `claude.ai/analytics/code-review` でリポジトリ別のレビュー数とコストが見られます

Bedrock・Vertex AI経由でClaude Codeを利用している組織でも、Code ReviewはAnthropicへの直接課金になります。請求管理担当者への説明時に伝えておくと混乱を防げます。

## まとめ

まず1〜2リポジトリを `Manual` モードで試し、`REVIEW.md` を整備してから本格稼働させるのが安全な導入ステップです。最初の一歩として、`REVIEW.md` テンプレートをリポジトリルートに置くことから始めてみてください。
