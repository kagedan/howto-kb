---
id: "2026-04-17-今日のclaude-code-v21111-リリース毎日changelog解説-01"
title: "今日のClaude Code v2.1.111 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/2c321dfbb6a3b87a4f4e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "qiita"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

Opus 4.7に `xhigh` という新しい推論レベルが増え、`/effort` がスライダーUIに進化。合わせて `/ultrareview` と `/less-permission-prompts` が追加されました。

## 今回の注目ポイント

1. **Opus 4.7 `xhigh` 登場と `/effort` スライダー化** - `high` と `max` の間に新しい段が追加。矢印キーで選ぶUIに。
2. **`/ultrareview` でクラウド並列レビュー** - ブランチやPRをマルチエージェントで総チェックする新コマンド。
3. **`/less-permission-prompts` と読み取り系Bashの許可プロンプト緩和** - 日々の「Yes連打」が目に見えて減ります。

---

## Opus 4.7 の `xhigh` と新しい `/effort` スライダー

対象: Opus 4.7を使っているユーザー、特に推論の深さと速度を細かく調整したい人。

推論の「効き具合」を選ぶ `/effort` に、`xhigh` が追加されました。位置は `high` と `max` の間。`max` まで上げると待ち時間が重いけど `high` では足りない、そういう場面向けの中間地点です。

使い方は3通り。`/effort` をスラッシュコマンドで叩く、起動時に `--effort` を渡す、モデルピッカーで選ぶ。Opus 4.7以外のモデルを選んだ場合は自動で `high` にフォールバックします。

```
# CLI引数で直接指定
claude --effort xhigh

# 起動後にスラッシュコマンドで切り替え
/effort xhigh
```

そして `/effort` を引数なしで叩くと、インタラクティブなスライダーが開きます。矢印キーで `low` → `medium` → `high` → `xhigh` → `max` を行き来して、Enterで確定。今までは値を覚えて打ち込む必要がありましたが、迷ったときに一覧から選べるのは素直に便利です。

ついでにMaxサブスクライバー向けには、Opus 4.7でAuto modeが使えるようになりました。`--enable-auto-mode` フラグも不要に。タスクの重さに応じてClaudeが自動でeffortレベルを調整してくれる挙動です。

---

## `/ultrareview` でクラウド並列マルチエージェントレビュー

対象: PRレビューに時間をかけたい人、手元のブランチを人に見せる前にセルフチェックしたい人。

新しいスラッシュコマンド `/ultrareview` が追加されました。クラウド上で並列マルチエージェントを走らせ、コードを多角的に批評する機能です。

呼び出しは2通り。

```
# 現在のブランチをレビュー
/ultrareview

# 特定のGitHub PRを取得してレビュー
/ultrareview 1234
```

引数なしで現在のブランチ、PR番号を渡すとそのPRをGitHubから取ってきてレビューしてくれます。通常の単一エージェントレビューと違い、複数視点で並行して分析・批判させるので、見落としを拾いやすい構造。手元の `/review` より重いぶん網羅的、という位置付けですね。

`/ultrareview` は「セルフレビューの最終関門」として使うのが良さそうです。コミット直前やPRドラフト直後に回すと、人に見られる前に一度強いチェックが入ります。

---

## `/less-permission-prompts` と読み取り系Bashの許可緩和

対象: 許可プロンプトに毎回Yesを押し続けている人。

日々のストレス要因だった「このBash叩いていい？」プロンプトに、二段構えの改善が入りました。

### 自動で許可プロンプトを減らす変更

まず仕様側の変更。以下はもうプロンプトを出しません。

* グロブパターン付きの読み取り専用Bash (`ls *.ts`, `cat src/*.md` など)
* `cd <project-dir> &&` で始まるコマンド

今までは `ls` 単体はOKでも `ls *.ts` で引っかかる、みたいな微妙な挙動がありました。ここが素直に通るようになります。

### `/less-permission-prompts` スキル

そのうえで新スキル `/less-permission-prompts` が追加。自分の過去トランスクリプトをスキャンし、よく使うBash/MCPツール呼び出しを抽出して、優先度順にallowlist案を出してくれます。

提案された設定は `.claude/settings.json` に追記する形。自分の作業パターンに合わせた許可ルールが機械的に作れるので、手動で `settings.json` を育ててきた人ほど刺さります。

## その他の変更

| カテゴリ | 変更点 | 概要 |
| --- | --- | --- |
| テーマ | `Auto (match terminal)` | `/theme` から端末のダーク/ライト設定に追従するオプションを選べるように |
| Windows | PowerShellツール | 段階ロールアウト中。`CLAUDE_CODE_USE_POWERSHELL_TOOL` でopt-in/opt-out可能 |
| CLI | タイポ検出 | `claude udpate` のような打ち間違いに「Did you mean `claude update`?」と提案 |
| プラン | ファイル命名 | ランダム語ではなくプロンプト由来の名前に (`fix-auth-race-snug-otter.md` など) |
| セットアップ | `/setup-vertex`, `/setup-bedrock` | `CLAUDE_CONFIG_DIR` 対応、既存ピンからの候補提示、1Mコンテキストモデル選択 |
| スキル | `/skills` メニュー | `t` キーで推定トークン数ソート |
| ショートカット | `Ctrl+U` / `Ctrl+L` | `Ctrl+U` で入力バッファ全消去 (復元は `Ctrl+Y`)、`Ctrl+L` で画面全再描画 |
| Transcript | フッター表記 | `[` でスクロールバックにダンプ、`v` でエディタ起動のショートカットを表示 |
| 長文貼り付け | 区切りマーカー | 切り詰めの「+N lines」表示が全幅の罫線に |
| Headless | `plugin_errors` | `--output-format stream-json` のinitイベントに、依存関係で外されたプラグインの情報を追加 |
| 観測性 | `OTEL_LOG_RAW_API_BODIES` | APIリクエスト/レスポンスの生ボディをOpenTelemetryログに出せる環境変数 |
| 安定性 | ノイズ抑制 | TUIに出ていた不要な解凍エラー・ネットワーク一時エラーを抑制 |
| リトライ | v2.1.110の挙動revert | non-streaming fallbackのリトライ上限設定を巻き戻し。過負荷時に完全失敗する事例が増えたため |

バグ修正(折りたたみ)

* iTerm2 + tmux で端末通知が送られた際に表示が崩れる問題を修正
* 非Gitディレクトリで `@` ファイル候補が毎ターン全スキャンされる問題、初期化直後のGitリポで設定ファイルしか出ない問題を修正
* 編集前のLSP診断が編集後に出て、Claudeが直したばかりのファイルを読み直す問題を修正
* `/resume` のタブ補完で任意の名前付きセッションが即再開してしまう問題を修正 (ピッカーを表示するように)
* `/context` のグリッドに行間の空白行が入る問題を修正
* `/clear` で `/rename` したセッション名が消え、statuslineの `session_name` が欠落する問題を修正
* プラグインの依存解決エラーを、競合・不正・複雑すぎる要件で区別するよう改善。`plugin update` 後の古いバージョン解決や、中断した `plugin install` からの復帰も修正
* 存在しない `commit` スキルが呼ばれ「Unknown skill: commit」が出ていた問題を修正
* Bedrock/Vertex/Foundryでの429レート制限エラーがAnthropic運用外のstatus.claude.comを参照していた問題を修正
* フィードバックアンケートが1つ閉じた直後に連続で出る問題を修正
* bash/PowerShell/MCP出力の生URLが端末折り返し時にクリックできない問題を修正
* Windows: `CLAUDE_ENV_FILE` とSessionStartフックの環境ファイルが無視されていた問題を修正
* Windows: ドライブレターパスの許可ルールが正しく根アンカーされ、大文字小文字違いのドライブレターを同一パスとして扱うように

## まとめ

目玉はOpus 4.7 `xhigh` の追加と `/effort` スライダー化。重めのタスクで `max` と `high` の間が欲しかった人に効きます。副次的に `/ultrareview` でレビュー負荷を外出しでき、`/less-permission-prompts` と読み取り系Bashの許可緩和で日々のYes連打も減ります。地味な品質改善が多めの堅いリリースですね。
