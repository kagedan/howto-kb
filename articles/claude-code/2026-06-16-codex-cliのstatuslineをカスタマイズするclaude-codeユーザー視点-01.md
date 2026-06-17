---
id: "2026-06-16-codex-cliのstatuslineをカスタマイズするclaude-codeユーザー視点-01"
title: "Codex CLIのstatuslineをカスタマイズする（Claude Codeユーザー視点）"
url: "https://qiita.com/ohakutsu/items/3bf4694a83b6e60ecfa6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "OpenAI", "GPT", "qiita"]
date_published: "2026-06-16"
date_collected: "2026-06-17"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Codeはよく触っているのですが、Codex CLIは触ったことがほとんどなかったので、ChatGPT Plusに課金してCodex CLIも触り始めてみました。
現状、ほとんどデフォルトの状態でCodex CLIを使っているのですが、Claude Codeで整えてきた環境に寄せていこうと考えており、いろいろ調べてみました。

この記事では、Claude Codeでできる機能のうちのstatuslineをCodex CLIではどのように設定するのかを紹介します。

## Claude Codeのstatuslineのおさらい

Claude Codeでは、コンテキストウィンドウの使用量、gitステータスや5時間セッション制限などをステータスバーに表示できます。

例）モデル、コンテキスト使用率、5時間セッション制限の使用率、週次制限の使用率などを表示できる

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/352836/b889a5fe-ed41-4fa1-bc37-0f69c669f1e0.png)

https://code.claude.com/docs/en/statusline

Claude Codeのstatuslineの設定は、ステータスラインに表示したい内容を標準出力に出力するスクリプトを書く or Claudeに書いてもらう（`/statusline`コマンド）ことでできます。
（詳しい設定方法は[ドキュメント](https://code.claude.com/docs/en/statusline#set-up-a-status-line)を参照）

そのため自由度が高く、自分がほしい情報を追加したり、見た目を整えたり、複数行での表示などできます。
また、statuslineをいい感じに表示するツールもいくつか公開されており、好みに合わせたものが使えるようになっています。

例）

- https://github.com/sirmalloc/ccstatusline
- https://github.com/ccusage/ccusage （記事執筆時点では、statuslineはベータ版）

## Codex CLIのstatusline

Codex CLIでも同様にコンテキストウィンドウの使用率、gitステータスや5時間セッション制限などをステータスバーに表示できます。

例）モデル、コンテキスト使用率、5時間セッション制限の使用率、週次制限の使用率などを表示できる

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/352836/a32e4b8c-c987-48e3-804b-5303cac1b918.png)

### 設定方法

Codex CLIのstatuslineは`/statusline`コマンドから設定ができます。

https://developers.openai.com/codex/cli/slash-commands#configure-footer-items-with-statusline

また、`~/.codex/config.toml`の`tui.status_line`に記述することでも設定できます。

```toml:~/.codex/config.toml
[tui]
status_line = [
  "model-with-reasoning",
  "context-used",
  "five-hour-limit",
  "weekly-limit",
  "git-branch",
]
status_line_use_colors = true
```

https://developers.openai.com/codex/config-reference

### Claude Codeとの違い

Codex CLIのstatuslineは、Claude Codeほどの自由度の高さはありません。

Claude Codeでは、statuslineの表示に任意のスクリプトを書けるのに対し、Codex CLIでは決められた選択肢の中から選ぶスタイルとなっています。

そのため、見た目のこだわりや、サポートされていない情報をみたい場合は、別の方法を取る必要があります。

### statuslineに表示できるもの

記事執筆時点（`v0.140.0`）で、選択できるのは以下です。
かなり多くのものがサポートされているので、大体のユースケースはカバーできているのではないかなと思います。

| 項目 | 説明 | Claudeによる日本語訳 |
| --- | --- | --- |
| `model-with-reasoning` | Current model name with reasoning level | 現在のモデル名と推論（reasoning）レベル |
| `current-dir` | Current working directory | 現在の作業ディレクトリ |
| `model` | Current model name | 現在のモデル名 |
| `reasoning` | Current reasoning level | 現在の推論（reasoning）レベル |
| `project-name` | Project name (omitted when unavailable) | プロジェクト名（取得できない場合は非表示） |
| `git-branch` | Current Git branch (omitted when unavailable) | 現在のGitブランチ（取得できない場合は非表示） |
| `pull-request-number` | Open pull request number for the current branch (omitted when unavailable) | 現在のブランチに対するオープン中のプルリクエスト番号（取得できない場合は非表示） |
| `branch-changes` | Committed branch changes against the default branch (omitted when unavailable) | デフォルトブランチに対するブランチのコミット済み変更（取得できない場合は非表示） |
| `run-state` | Compact session run-state text (Ready, Working, Thinking) | セッションの実行状態を表す短いテキスト（Ready, Working, Thinking） |
| `permissions` | Active permission profile or sandbox mode | 有効なパーミッションプロファイルまたはサンドボックスモード |
| `approval-mode` | Active command approval mode | 有効なコマンド承認モード |
| `context-remaining` | Percentage of context window remaining (omitted when unknown) | コンテキストウィンドウの残り割合（不明な場合は非表示） |
| `context-used` | Percentage of context window used (omitted when unknown) | コンテキストウィンドウの使用割合（不明な場合は非表示） |
| `five-hour-limit` | Remaining usage on the 5-hour usage limit (omitted when unavailable) | 5時間ごとの利用上限の残り（取得できない場合は非表示） |
| `weekly-limit` | Remaining usage on the weekly usage limit (omitted when unavailable) | 週ごとの利用上限の残り（取得できない場合は非表示） |
| `codex-version` | Codex application version | Codexアプリケーションのバージョン |
| `context-window-size` | Total context window size in tokens (omitted when unknown) | コンテキストウィンドウの合計サイズ（トークン単位、不明な場合は非表示） |
| `used-tokens` | Total tokens used in session (omitted when zero) | セッションで使用した合計トークン数（0の場合は非表示） |
| `total-input-tokens` | Total input tokens used in session | セッションで使用した合計入力トークン数 |
| `total-output-tokens` | Total output tokens used in session | セッションで使用した合計出力トークン数 |
| `thread-id` | Current thread identifier (omitted until thread starts) | 現在のスレッド識別子（スレッド開始までは非表示） |
| `fast-mode` | Whether Fast mode is currently active | Fastモードが現在有効かどうか |
| `raw-output` | Whether raw scrollback mode is active | rawスクロールバックモードが有効かどうか |
| `thread-title` | Current thread title, or thread identifier when unnamed | 現在のスレッドタイトル（未命名の場合はスレッド識別子） |
| `task-progress` | Latest task progress from update_plan (omitted until available) | update_planによる最新のタスク進捗（取得できるまでは非表示） |

## 最後に

Claude Codeユーザーの視点で、Codex CLIのstatuslineを紹介してみました。
もし、Codex CLIを試そうと思っている方の助けになれば幸いです。

私はCodex CLIをまだ触りはじめたばかりなので、Claude Codeと同等くらいまで使えるように整えていければと思います。
