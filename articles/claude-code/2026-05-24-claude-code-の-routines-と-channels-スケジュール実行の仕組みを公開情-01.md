---
id: "2026-05-24-claude-code-の-routines-と-channels-スケジュール実行の仕組みを公開情-01"
title: "Claude Code の Routines と Channels — スケジュール実行の仕組みを公開情報から整理"
url: "https://qiita.com/goki602/items/48cd1f30af1fb2f3c3c9"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-05-24"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

> 本記事は Claude Code(Anthropic)を活用して執筆しています。
> 検証可能な範囲で公開情報を整理したものですが、
> コード例等は実環境での動作確認をおすすめします。

Claude Code が 2026 年 4 月 14 日に **Routines**（クラウドスケジュールタスク）をリサーチプレビューとして公開した。「PC を閉じていても Anthropic のインフラ上でエージェントが動き続ける」という仕組みで、CI/CD 以外の定型保守作業を AI に委ねる選択肢が現実的になってきた。

同じ 2026 年春には **Channels**（Telegram・Discord・iMessage 連携）も登場。「スケジュール起動」と「外部イベント注入」の 2 軸が揃い、Claude Code の自動化レイヤーが一段と厚くなっている。本稿では[公式ドキュメント（Routines）](https://code.claude.com/docs/en/routines)と[Channels のドキュメント](https://code.claude.com/docs/en/channels)を元に両機能の概要を整理する。

## スケジュール実行の 3 層構造

[公式ドキュメント（scheduled-tasks）](https://code.claude.com/docs/en/scheduled-tasks)によると、Claude Code のスケジュール実行には 3 つの層がある。

**1. CLI `/loop`（セッションスコープ）**
現在開いているセッション中のみ動作する。一定間隔でプロンプトを再実行し、デプロイ完了待ちや CI ポーリングに使う。セッションを閉じると止まる。

**2. Desktop Scheduled Tasks（ローカル常駐）**
PC 起動中に動き続けるタスク。ファイル・MCP サーバー・スキル・コネクタへのフルアクセスを持つ（[Desktop Scheduled Tasks ドキュメント](https://code.claude.com/docs/en/desktop-scheduled-tasks)）。毎朝のログ集計や定時レポート生成に向いている。PC を落とすと止まる。

**3. Cloud Routines（Anthropic インフラ）**
ローカル環境から切り離されて動く層。Anthropic が管理するインフラ上で実行されるため、PC の電源状態に依存しない。リポジトリを読み込み、MCP コネクタを使い、`claude/` プレフィックス付きブランチに変更を push して人間レビューを待つのが基本フローだ。

この 3 層を「その場しのぎ ↔ インフラに委ねる」の軸で整理すると、Cloud Routines が最も「委ねる」側に位置する。

## Cloud Routines の仕組みと設定方法

### スケジューリングとトリガー

スケジュールは Hourly / Daily / Weekdays / Weekly のプリセット、またはカスタム cron 式で設定できる。加えて **GitHub イベントトリガー** にも対応しており、以下のイベントで自動起動が可能だ:

- `pull_request`・`push`・`issues`
- `check_run`・`workflow_run`・`discussion`
- `release`・`merge_queue`

「PR がオープンされたらレビューコメントを自動生成」「Issue 作成ごとにトリアージを走らせる」といったフローを、外部 CI なしに Claude Code のみで構成できるのが利点だ。

### 作成方法

- **Web UI**: `claude.ai/code/routines` から GUI で設定・管理できる
- **CLI**: `/schedule` コマンドを使う（要件未充足時は非表示になる）
- **API**: ベータヘッダー `experimental-cc-routine-2026-04-01` 付きの `/fire` エンドポイント経由で外部システムから起動できる

### 公式が挙げるユースケース

公式ドキュメントが例示するのは以下の 3 つ:

1. **毎晩の Issue トリアージ** — 新着 Issue に優先度ラベルを自動付与
2. **週次の古い PR 整理** — 長期放置 PR を検出してメンテナに通知
3. **ドキュメントの継続同期** — コードの変更に追随して docs を最新化

「定型的だが後回しにされがちな保守作業」という共通点がある。これらは変更の影響範囲が読みやすく、自動化の副作用が起きにくいタスクでもある。

### プランと実行制限

Routines は **Pro・Max・Team・Enterprise プランかつ Claude Code on the web が有効** な環境で使える。1 日の実行上限はプランによって異なる（公式: [routines](https://code.claude.com/docs/en/routines)）:

| プラン | 1 日の実行上限 |
|--------|----------------|
| Pro | 5 回 |
| Max | 15 回 |
| Team / Enterprise | 25 回 |

実行はサブスクリプション使用量を通常の対話セッションと同様に消費する。上限超過時は、Usage Credits（従量課金）が有効なら超過分で継続し、無効なら次の枠リセットまで新規起動が拒否される。`/schedule` コマンドが CLI で非表示になっている場合はプランや設定状況の確認が先決だ。

## Channels — メッセージアプリからセッションにイベントを注入する

Routines がスケジュール駆動なら、Channels はイベント駆動の補完機能に位置づけられる。

2026 年 3 月 20 日にリサーチプレビューとして公開（[公式ドキュメント](https://code.claude.com/docs/en/channels)）。現在の対応プラットフォームは:

- **Telegram**（初期リリース時から対応）
- **Discord**（同上）
- **iMessage**（macOS のみ、3 月 26 日追加）
- **カスタム Webhook**

仕組みは MCP サーバーを介したブリッジ。Telegram ボットにメッセージを送ると、ローカルで動作中の Claude Code セッションに転送され、ローカルファイル・MCP・git への完全アクセスで処理されたうえで同じチャットに返信が返ってくる。

セキュリティ面では allowlist 制が採用されており、あらかじめペアリングして承認した送信者 ID からのメッセージのみが通過する。未登録 ID からのメッセージはサイレントに破棄されるため、意図しない第三者からの操作リスクは設計上排除されている。

「外出中にスマートフォンの Telegram から作業を指示する」「チームの Discord サーバーからメンバーが直接 Claude にタスクを投げる」といった使い方が想定されている。MacStories のハンズオンレポート（[First Look: Claude Code's New Telegram and Discord Integrations](https://www.macstories.net/stories/first-look-hands-on-with-claude-codes-new-telegram-and-discord-integrations/)）でも実際のセットアップ手順と動作確認が紹介されており、参考になる。

## まとめ

Routines と Channels の登場で、Claude Code は「エディタ内の対話補助」から「バックグラウンドで継続稼働するエージェント基盤」へと進化しつつある段階に入った。どちらも現時点ではリサーチプレビューであり、API の破壊的変更や制限変更の可能性は残る。

まず試すなら、毎晩の Issue トリアージや週次 PR 整理のような低リスクの定型保守作業がよい出発点だ。[公式ドキュメントのクイックスタート](https://code.claude.com/docs/en/routines)を起点に、自分のワークフローで委ねられる部分を探してみると面白い。
