---
id: "2026-04-16-claude-code-の-routines-で-dotfiles-の設定を自動改善する-01"
title: "Claude Code の Routines で dotfiles の設定を自動改善する"
url: "https://zenn.dev/genda_jp/articles/f425cc7354f608"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* Claude Code の Routines (旧 scheduled tasks) を使い、dotfiles の Claude 設定を週次で自動改善する仕組みを構築した
* 最新情報の収集から PR 作成まで、Claude Code がクラウド上で自動実行する
* `/schedule` で構築した直後に Routines がリリースされ、既存のトリガーは自動で移行された
* 個人アカウントでは PR 作成まで問題なく成功。Team プランではパーミッションに課題あり

## 背景: Claude Code の設定を手動で改善していた

dotfiles リポジトリで Claude Code の設定を管理しています。`.config/claude/` 配下には以下のようなファイルが並んでいます。

```
.config/claude/
  settings.json       # パーミッション、環境変数、フック等
  rules/              # Markdown、日本語表記、Bash のルール
  skills/             # レビュー、ドキュメント検索等のスキル定義
  agents/             # コード品質、セキュリティ等のレビューエージェント
```

Claude Code は頻繁にアップデートされます。新しいフックイベント、環境変数、設定オプションが追加されるたびに、CHANGELOG を確認して settings.json を更新し、必要に応じてルールやスキルを追加する作業が頻度高く発生していました。

作業自体は難しくないのですが、「最新情報の収集 → 現状との差分確認 → 変更 → 動作確認」のサイクルを定期的に回すのは地味に手間がかかります。Claude Code の設定改善を Claude Code に任せられないか、と考えました。

## /schedule で自動化を試みる

### scheduled tasks とは

Claude Code には `/schedule` というスキルがあります。これはクラウド上で Claude Code のセッションを定期実行する仕組みで、ローカルマシンが起動している必要はありません。`/loop` がセッション内での繰り返し実行であるのに対し、`/schedule` は完全にリモートで動作します。

仕組みはシンプルで、以下の 3 つを指定してトリガーを作成します。

1. **プロンプト**: エージェントに実行させたい指示
2. **リポジトリ**: 対象の GitHub リポジトリ
3. **スケジュール**: cron 式による実行頻度

### セットアップ

まず `/web-setup` で GitHub アカウントを連携します。これにより、エージェントがリポジトリのクローン、ブランチ作成、PR 発行を行えるようになります。

次に `/schedule` を実行してトリガーを作成します。

対話形式でプロンプト、リポジトリ、実行頻度を設定していきます。CLI から直接指定することも可能です。

```
/schedule weekly claude config improvement on Monday 9am
```

### プロンプト設計のポイント

Routines のエージェントはゼロコンテキストで起動します。ローカルの環境変数やファイルにはアクセスできないため、プロンプトだけで何をすべきかを完全に伝える必要があります。

設計で意識した点は以下の通りです。

1. **情報収集の手段を明示する**: 「Claude Code の CHANGELOG や公式ドキュメントを WebSearch/WebFetch で確認」のように、どこから情報を取るかを指定した
2. **対象ファイルを列挙する**: `settings.json`、`rules/`、`skills/`、`agents/` など、確認すべきファイルを漏れなく指定した
3. **判断基準を与える**: 「確信が持てない変更はしない」「改善点がなければ何もしない」のように、保守的な方針を明示した
4. **出力形式を指定する**: ブランチ命名規則 (`improve/claude-config-YYYY-MM-DD`) や PR の body に含める内容を指定した

実際には深く考えなくとも、 `/schedule` スキルとの対話的なやり取りでこれらのポイントを引き出してくれます。

実際に作成したプロンプト

```
あなたは dotfiles リポジトリの Claude Code 設定を定期的に改善するエージェントです。

## タスク

以下の手順で情報収集し、改善点があれば feature ブランチを作成して PR を開いてください。

### 1. 情報収集

以下のソースから Claude Code の最新情報を収集してください:
- Claude Code 公式ドキュメント・リリースノート (WebSearch / WebFetch を使用)
- 新しい環境変数・設定オプション・hooks イベントの追加
- 廃止予定・変更された設定
- コミュニティで話題の設定やベストプラクティス

### 2. 現状確認

リポジトリの以下ファイルを読み込み、現状を把握してください:
- `.config/claude/settings.json`
- `.config/claude/rules/` 配下の全ファイル
- `.config/claude/skills/` 配下の全ファイル
- `.config/claude/agents/` 配下の全ファイル
- `agents/AGENTS.md`

### 3. 改善提案の判断基準

以下の基準で改善点を特定してください:
- settings.json に未設定の有用な新オプション・環境変数がある
- permissions の allow/deny リストに追加・削除すべきエントリがある
- hooks に追加できる便利な自動化がある
- スキル・ルール・AGENTS.md に陳腐化した情報や追加すべき内容がある

### 4. PR 作成

改善点がある場合:
1. `improve/claude-config-YYYY-MM-DD` ブランチを作成
2. 変更を加えてコミット
3. 日本語で PR を作成 (タイトル・本文とも日本語)
4. PR 本文に「情報収集結果」と「変更理由」を明記

改善点がない場合は何もしないで終了してください。

## 注意事項
- 変更は保守的に。確信が持てない変更はしない
- コメントや説明文は日本語で記述
- 既存の設定スタイル・フォーマットを維持する
- JSON の追加・変更時はキーのアルファベット順を保つ
```

### cron 式とタイムゾーン

cron 式は UTC で指定します。毎週月曜 9:00 JST に実行したい場合、UTC では月曜 0:00 になるため `0 0 * * 1` と設定しました。

## 実際に生成された PR

トリガーを作成してから 2 週間で 2 つの PR が自動生成されました。1 つ目は `settings.json` の env キーのアルファベット順ソート、2 つ目が以下の PR です。

### 不足 git コマンドの allow 追加と StopFailure hook 追加

* git コマンドの allow 追加
* StopFailure hook の追加
  + 既存の `Stop` hook で実装されている正常終了音の再生処理を見て `StopFailure` のエラー終了時の音の再生処理を追加

![StopFailure 追加の差分](https://static.zenn.studio/user-upload/6b501e42225a-20260416.png)

### エージェントの判断力

この PR で特に印象的だったのは、「変更しなかった項目」のセクションです。

> * `UserPromptSubmit` hook: セッション命名の基準が不明確なため見送り
> * `PermissionDenied` hook: 具体的なユースケースが明確でないため見送り
> * `disableSkillShellExecution`: 現設定の動作への影響範囲が不明なため見送り

候補として検討した上で、確信が持てないものは変更しない判断をしています。プロンプトで「保守的な方針」を指示した通りの振る舞いで、安心して任せられます。

## Routines のリリースと移行

### /schedule から Routines へ

2026年4月14日 に Anthropic から [Routines](https://claude.com/blog/introducing-routines-in-claude-code) がリサーチプレビューとして公開されました。

Routines は `/schedule` で作成していた scheduled tasks を拡張・統合した機能で、既存のトリガーは自動的に Routines として移行されました。管理画面も `claude.ai/code/routines` に統一されています。

![Routines 管理画面](https://static.zenn.studio/user-upload/74f24d29e41b-20260416.png)

### schedule との違い

主な拡張点は以下の通りです。

| 観点 | /schedule (旧) | Routines |
| --- | --- | --- |
| トリガー種別 | cron スケジュールのみ | スケジュール + API + GitHub Webhook の 3 種類 |
| 管理画面 | CLI のみ | Web UI (`claude.ai/code/routines`) + CLI |
| セッション継続性 | 単発実行 | Webhook は PR 単位でセッションを継続 |
| 外部連携 | 限定的 | API エンドポイント + 認証トークンで連携可能 |
| コネクタ | なし | Slack、Linear、Google Drive 等の MCP 対応 |

GitHub Webhook トリガーでは、PR が作成されたときにカスタムチェックリストでレビューしたり、特定ディレクトリへの変更を検知してフラグを立てたりといったユースケースが考えられます。

### CLI と Web UI の使い分け

Routines の作成は CLI (`/schedule`) と Web UI (`claude.ai/code/routines`) の両方から行えます。ただし、CLI から作成できるのは Scheduled トリガーのみで、API トリガーや GitHub Webhook トリガーの追加は Web UI で行う必要があります。

また、`allowed_tools` の変更は CLI からは設定できますが、Web UI にはその項目が存在しません。後述する Team プランのパーミッション問題に関わるため、CLI での操作に慣れておく必要があります。

## Team プランでの注意点

個人の Pro アカウントでは問題なく動作し、PR 作成まで完了していました。しかし Team プランで同様の Routine を設定したところ、実行時に `.claude/settings.json` の Edit に対してパーミッション許可を求められました。

問題は、この許可ダイアログに **セッションをまたぐ "Always allow" の選択肢がない** ことです。"一度だけ許可" と "Always allow for session" しか表示されないため、Routine が実行されるたびに人間が手動で許可を与える必要があります。

!["Always allow" の選択肢が無いパーミッションダイアログ](https://static.zenn.studio/user-upload/af82a058ff9a-20260416.png)

Routines は無人で定期実行されることを前提とした機能のため、毎回の手動許可が必要では実用になりません。

### Issue の報告

この問題は [anthropics/claude-code#33027](https://github.com/anthropics/claude-code/issues/33027) として報告されています。同様の報告が複数あり、Routines を実運用で使おうとしたユーザーが共通して直面している課題のようです。  
Issue に記載された allowed\_tools 変更のワークアラウンドを試してみましたが、解決には至りませんでした。

Routines はリサーチプレビュー段階であるため、今後の改善に期待しています。

## まとめ

* Claude Code の Routines を使うことで、dotfiles の Claude 設定を週次で自動改善する仕組みを構築できた
* エージェントは最新情報を収集し、不足している設定の追加や整合性の修正を PR として提案してくれる。「変更しなかった理由」まで記載してくれるため、判断の透明性が高い
* `/schedule` で構築した直後に Routines がリリースされたが、既存のトリガーは自動的に移行されたため作り直しは不要だった
* Routines はスケジュール以外にも API トリガーや GitHub Webhook に対応しており、自動化の幅が広がっている
* Team プランではパーミッションの "Always allow" 欠如が課題として残っている。リサーチプレビューの今後のアップデートに期待したい

巷にあふれる最新情報のキャッチアップに割く時間を削減できました。定期的なメンテナンスタスクを抱えている方は、Routines の導入を検討してみてください。
