---
id: "2026-05-24-claude-code-routinesanthropic-インフラで動くスケジュール自動化を整理-01"
title: "Claude Code Routines：Anthropic インフラで動くスケジュール自動化を整理"
url: "https://qiita.com/goki602/items/31f054eff0f6be583fe2"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "qiita"]
date_published: "2026-05-24"
date_collected: "2026-05-25"
summary_by: "auto-rss"
query: ""
---

> 本記事は Claude Code(Anthropic)を活用して執筆しています。
> 検証可能な範囲で公開情報を整理したものですが、
> コード例等は実環境での動作確認をおすすめします。

PC の電源を落とした後も、Claude Code が自律的に動き続けるようになった。

Anthropic が 2026 年 4 月 14 日に研究プレビューとして公開した **Routines** は、Claude Code のタスクを Anthropic のクラウドインフラ上でスケジュール実行できる機能だ（[公式ドキュメント](https://code.claude.com/docs/en/routines)）。「毎晩 2 時にバグ報告を確認して PR を自動作成する」ような定型タスクを、ローカルマシン不要で継続実行できる。

この記事では、公式ドキュメントと各メディアの報道をもとに、Routines の概要・3 種のトリガー・料金・注意点を整理する。

## Routines でできること：3 つのトリガー

公式ドキュメント（[Automate work with routines](https://code.claude.com/docs/en/routines)）によれば、Routines は以下の 3 種類のトリガーに対応している。

**1. スケジュール実行**

毎時・毎日・毎週など cron 的な定期起動。公式の例として「毎晩 2 時に GitHub Issues を自動スキャンし、バグを再現する手順を添えたドラフト PR を作成する」フローが示されている。

**2. API エンドポイント**

ルーティンごとに専用の HTTP エンドポイントが発行される。Bearer トークンを添えて外部サービスや CI パイプラインから POST することでトリガーできる。エラー発生時に Claude へ調査を委ねるなど、既存ワークフローへの組み込みが想定されている。

**3. GitHub イベント**

Pull Request 作成やリリースなどリポジトリイベントに反応して自動実行できる。コードレビューコメントの自動投稿や変更サマリーの生成が主なユースケースとして挙げられている。

最大の特徴は **Anthropic 管理インフラ上での実行**だ。自前の cron サーバーや常時起動マシンが不要で、ローカル PC がオフの間も動作し続ける（[DevOps.com 解説記事](https://devops.com/claude-code-routines-anthropics-answer-to-unattended-dev-automation/)）。

## 作成の流れ

公式ドキュメント（[Run prompts on a schedule](https://code.claude.com/docs/en/scheduled-tasks)）によれば、Routines の作成は以下の手順で行う。

1. `claude.ai/code` の Web 画面でアカウントとリポジトリを紐付ける
2. Claude Code CLI から `/schedule` コマンドを実行してルーティンを定義する
3. トリガー種別・頻度・実行プロンプトを設定して保存する
4. 以降は Anthropic インフラが定刻・イベント発生時に Claude を自動呼び出す

なお `/schedule` コマンドは研究プレビュー段階であり、コマンド仕様は変更される可能性があると公式が明記している。動作確認は最新のドキュメントを参照してほしい。

## Channels との組み合わせ

Routines と相性のよい関連機能として **Channels** がある。Channels は Telegram・Discord・iMessage・カスタム Webhook からアクティブな Claude Code セッションにイベントをプッシュできる機能で、2026 年 3 月に研究プレビューとして公開された（[公式: channels](https://code.claude.com/docs/en/channels)）。

Routines が「スケジュールや外部イベントで Claude を起動する仕組み」なら、Channels は「メッセージアプリから Claude に指示を送る仕組み」と整理できる。たとえば CI のアラートを Telegram Bot 経由で受け取り、その場で Claude に調査を依頼するフローなど、2 つの機能を組み合わせることで自動化の幅が広がる。ただし Channels はローカルマシンが起動中であることが前提で、Routines とはインフラ層が異なる点に注意したい。

## 注意点と制約

現時点（2026 年 5 月）での主な制約は次の通りだ。

- **対応プラン**: Pro・Max・Team・Enterprise のみ。Free プランは対象外
- **料金**: Pro・Max は **3 回まで無料**、以降は追加使用量として課金（[公式概要](https://code.claude.com/docs/en/overview)）
- **研究プレビュー**: API 仕様・コマンド構文は変更される可能性あり（公式明記）
- **本番活用には段階的な検証を**: 9to5Mac の報道（[記事](https://9to5mac.com/2026/04/14/anthropic-adds-repeatable-routines-feature-to-claude-code-heres-how-it-works/)）でも「rough edges（粗い部分）が残る段階」と指摘されている

InfoQ の記事（[Anthropic Introduces Routines for Claude Code Automation](https://www.infoq.com/news/2026/05/anthropic-routines-claude/)）では、Routines を「Claude Code エージェントを補助ツールから並行プロセスへと昇格させる転換点」と評している。公式の見解ではないが、エージェント活用の方向性を示す視点として参考になる。

## まとめ

Routines は、スケジュール・API・GitHub イベントの 3 つのトリガーで Claude Code のタスクを Anthropic インフラに委ねられる機能だ。「ローカルマシンを常時起動しなくてよい」「自前サーバーが不要」という点が最大のメリットで、定期 Issue トリアージ・ドキュメントドリフト監視・PR 自動生成といった夜間バッチ系タスクから試してみるとフィット感をつかみやすい。Pro・Max プランなら 3 回まで無料で動作確認できるので、まずは低リスクな補助タスクから始めるのが現実的なスタートだろう。実際に使い込んだ事例がもう少し出てきたら、改めて深掘りしてみたい。
