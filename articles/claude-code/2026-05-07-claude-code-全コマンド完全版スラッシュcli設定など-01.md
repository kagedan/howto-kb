---
id: "2026-05-07-claude-code-全コマンド完全版スラッシュcli設定など-01"
title: "Claude Code 全コマンド完全版｜スラッシュ・CLI・設定など"
url: "https://zenn.dev/ai_heatland/articles/3b7186c20c69f0"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-05-07"
date_collected: "2026-05-08"
summary_by: "auto-rss"
---

ターミナルで`claude --help`を叩いても、表示されるフラグは全体の半分以下しかない。公式ドキュメントには記載されているのにヘルプには出てこないオプションが大量にあり、しかもv2.1.x系のリリースが続くたびに/vim・/enable-auto-mode・/pr-commentsが廃止され、/ultrareview・/security-review・/scheduleが新たに追加された。`/cost`と`/stats`は`/usage`に統合され、フラグ体系も再編が続いている。

本記事では**2026年5月7日時点のClaude Code v2.1.x系の全スラッシュコマンド・CLIフラグ・主要設定**を、公式リファレンスをベースに「概要・使い方・実用例」の3点セットで体系的にまとめた。アップデートを追えていなかった人がこの1本で最新の機能セットへキャッチアップできることを目指している。

!

**この記事のポイント**

* 2026年5月時点で**約60種類のスラッシュコマンドと80を超えるCLIフラグ**が存在。本記事はその全体像を1本で網羅する
* v2.1.x系で\*\*/ultrareview・/security-review・/schedule・/loop・/focus・/effort・/recap\*\*が新設、/vim・/pr-comments・/enable-auto-modeが削除された
* **カテゴリ別の体系図・コマンド対比表・実用シナリオ**付き。コピペで使えるコード例を多数収録

## 早見表：全コマンド一覧

「あのコマンド何だっけ？」を最短で引けるよう、本記事で扱う全コマンドをカテゴリ別に1表にまとめた。詳細は各セクションへ。

### スラッシュコマンド早見表

### ターミナルコマンド早見表

### CLIフラグ早見表

---

## Claude Code コマンド体系の全体像

Claude Codeのコマンドは大きく分けて、CLIから叩く**ターミナルコマンド**と、セッション内で叩く**スラッシュコマンド**の2階層がある。さらにスラッシュコマンドは「ビルトイン（CLIにロジックが直接実装されているもの）」と「バンドルスキル（プロンプトとしてClaudeに渡され、Claude自身がツールを駆使して実行するもの）」に分かれる。

**まずは「ターミナルから叩く7コマンド」と「セッション内の頻出20コマンド」を押さえれば日常運用の8割はカバーできる**。本記事ではここを軸に、その先のレア機能までを順に解説する。

---

## ターミナルコマンド：claude実行系

セッションを起動・継続・終了する基本コマンド群だ。`claude`単体でインタラクティブモードに入るのは多くの人が知っているが、実際にはサブコマンドが10種類以上ある。

<a id="cmd-claude"></a>

### claude — インタラクティブセッションを開始

**概要**：何も付けずに実行すると現在のディレクトリでセッションが立ち上がる。後ろにクエリを書くと、そのクエリを最初のメッセージとしてセッション開始。

**使い方**：

```
# 通常起動
claude

# 初期プロンプト付きで起動
claude "explain this project structure"
```

**実用例**：プロジェクトのルートで`claude`を叩くと、そのディレクトリの`CLAUDE.md`と`.claude/`配下が自動ロードされる。サブディレクトリで叩くと、上位ディレクトリのCLAUDE.mdも階層的に読まれる。

<a id="cmd-claude-p"></a>

### claude -p / --print — 非対話のSDKモード

**概要**：応答を1回だけ取得して終了する。CIスクリプト・他コマンドとのパイプ・自動化に必須。

**使い方**：

```
# 単発クエリ
claude -p "summarize this README in 3 bullets"

# パイプで標準入力を渡す
cat error.log | claude -p "explain the root cause"

# JSON出力でプログラム処理
claude -p --output-format json "analyze code style"
```

**実用例**：GitHub Actionsから`claude -p`で呼び出してPRに自動でレビューコメントを書かせる、`pre-commit`フックでコード差分をClaudeに要約させる、といった自動化に向く。`--max-turns 3`や`--max-budget-usd 5.00`で上限を設けるとコストが暴走しない。

<a id="cmd-claude-c"></a>

### claude -c / --continue / -r / --resume — 会話の継続と再開

**概要**：`-c`は同一ディレクトリの直近セッションを継続。`-r`はセッションIDまたは名前で特定のセッションを呼び戻す。

**使い方**：

```
# 直近セッションの続き
claude -c

# 直近セッションにスクリプトから問い合わせ
claude -c -p "Run type checks and report errors"

# 名前付きセッションを呼び戻す
claude -r "auth-refactor" "Finish this PR"

# UUIDで指定
claude --resume 550e8400-e29b-41d4-a716-446655440000

# 再開時に新セッションIDで分岐
claude --resume abc123 --fork-session
```

**実用例**：機能ブランチごとに`claude -n "feature-payments"`と名前を付けて起動し、後日`claude -r feature-payments`で続きを書ける。長時間のリファクタを中断して翌日再開するときに重宝する。`--from-pr 123`を使えばPR番号からセッションを引き戻すこともできる。

<a id="cmd-claude-install"></a>

### claude install / update — バージョン管理

**概要**：`claude update`は最新版に上げる。`claude install <version>`で特定バージョンを固定インストール。

**使い方**：

```
# 最新へ更新
claude update

# 安定版を入れ直す
claude install stable

# 特定バージョンを固定
claude install 2.1.118
```

**実用例**：CIや本番運用でバージョンの揺らぎを抑えたいときは`2.1.118`のようにピン留めする。逆に検証環境では`claude install latest`で最先端の機能を試す、という使い分けが効く。

<a id="cmd-claude-auth"></a>

### claude auth login / logout / status — 認証管理

**概要**：Anthropicアカウントへのサインイン・サインアウト・状態確認。`auth status`は終了コードでJSON判定もできる。

**使い方**：

```
# 通常ログイン
claude auth login

# SSO強制
claude auth login --sso

# Anthropic Console（API課金）でログイン
claude auth login --console

# ログアウト
claude auth logout

# JSONで認証状態取得（exit 0=ログイン中、1=未ログイン）
claude auth status
```

**実用例**：CI環境では`claude setup-token`で長寿命OAuthトークンを生成し、環境変数として保存して`claude auth status`で生死を監視するパターンが鉄板。

<a id="cmd-claude-mcp"></a>

### claude mcp / plugin / agents — 拡張機能管理

**概要**：3つのコマンドはそれぞれMCPサーバー・プラグイン・サブエージェントを管理する独立サブコマンド群。

**使い方**：

```
# MCPサーバー追加
claude mcp add github
claude mcp add slack --scope user

# プラグインインストール
claude plugin install code-review@claude-plugins-official

# プラグイン整理（孤立した依存を削除）
claude plugin prune

# 設定済みサブエージェント一覧
claude agents
```

**実用例**：MCPサーバーは`claude mcp add`した後に`/mcp`コマンドでセッション内のステータスを確認する流れ。プラグインの自作・配布フローはMCPサーバー構築と相補的に組み合わせると効果が高い。

<a id="cmd-claude-purge"></a>

### claude project purge / remote-control / ultrareview — 運用系

**概要**：プロジェクトのローカル状態をまとめて削除、Webアプリ/モバイルアプリからのリモート制御、CLIから非対話でultrareviewを叩く。

**使い方**：

```
# 削除前にドライラン
claude project purge ~/work/repo --dry-run

# 全プロジェクト一括（要確認）
claude project purge --all -y

# Remote Controlサーバーモード起動
claude remote-control --name "My Project"

# ultrareviewをCIから非対話実行
claude ultrareview 1234 --json --timeout 45
```

**実用例**：`project purge`はストレージ整理に使う。トランスクリプト・タスクリスト・debugログ・編集履歴・プロンプト履歴・`~/.claude.json`内の該当エントリをまとめて消す。CIで`claude ultrareview`を起動するとクラウド側で並列レビューが走り、JSONで結果を受け取れる。

---

## CLIフラグ徹底解説：起動時に効くオプション

`claude --help`に出ないフラグも多数ある。ここでは2026年5月時点で利用可能なフラグを「実行モード制御・出力制御・権限・モデル・セッション管理」の5カテゴリで整理する。

<a id="flag-execmode"></a>

### 実行モード系フラグ

| フラグ | 役割 |
| --- | --- |
| `-p` / `--print` | 非対話モード。1回応答して終了 |
| `--bare` | hooks/skills/plugins/MCP/auto-memory/CLAUDE.mdの自動検出をスキップして高速起動 |
| `--remote` | claude.aiでWebセッションを新規作成 |
| `--remote-control` / `--rc` | claude.aiから制御可能なインタラクティブセッション |
| `--teleport` | Webセッションをローカル端末に引き戻す |
| `--worktree` / `-w` | `.claude/worktrees/<name>`にgit worktreeで隔離起動 |
| `--tmux` | worktree起動時にtmuxセッション作成（要 `--worktree`） |
| `--ide` | 利用可能なIDEに自動接続 |
| `--chrome` / `--no-chrome` | Chrome連携の有効/無効 |

**`--bare`の実用例**：

```
# 起動時間最重視の自動化
claude --bare -p "summarize CHANGELOG.md"

# Hooksなしで素のClaudeを叩きたいとき
claude --bare -p --output-format json "what files changed?"
```

`--bare`は`CLAUDE_CODE_SIMPLE`環境変数と等価で、起動時のディスクI/Oが最小化されるためバッチ処理に向く。

**`--worktree`の実用例**：

```
# 並行作業用にworktreeを切ってtmuxまで起動
claude -w feature-auth --tmux

# worktreeから戻ってPR連動でセッション再開
claude --from-pr 456
```

並行で複数機能を進めるときに、ファイルの状態が混ざらないので推奨される。

<a id="flag-output"></a>

### 出力制御系フラグ

| フラグ | 役割 |
| --- | --- |
| `--output-format` | `text` / `json` / `stream-json` |
| `--input-format` | `text` / `stream-json` |
| `--include-partial-messages` | 部分ストリームを出力（`--print`必須） |
| `--include-hook-events` | フックイベントを出力に含める |
| `--replay-user-messages` | stdin入力を再emitする |
| `--json-schema` | JSON Schemaでバリデーション付きの構造化出力 |
| `--verbose` | turn-by-turnの完全ログ |
| `--debug` | カテゴリ指定可能（例: `"api,mcp"`） |
| `--debug-file <path>` | デバッグログをファイルへ |

**実用例**：

```
# JSON Schemaで構造化レスポンスを取得
claude -p \
  --json-schema '{"type":"object","properties":{"summary":{"type":"string"},"risks":{"type":"array"}}}' \
  "review the diff and output {summary, risks}"

# ストリーム出力でhookイベントも一緒に観測
claude -p --output-format stream-json --include-hook-events "build the project"

# 特定カテゴリだけdebug
claude --debug "api,hooks" --debug-file /tmp/cc.log
```

`--json-schema`はAgent SDKの構造化出力を活用するための核となるフラグだ。エージェントの結果を後続のスクリプトで安全に消費できる。

<a id="flag-permission"></a>

### 権限・モデル系フラグ

| フラグ | 役割 |
| --- | --- |
| `--permission-mode` | `default` / `acceptEdits` / `plan` / `auto` / `dontAsk` / `bypassPermissions` |
| `--dangerously-skip-permissions` | 全権限プロンプトをスキップ（=`bypassPermissions`） |
| `--allow-dangerously-skip-permissions` | Shift+Tabのモードサイクルにbypassを追加 |
| `--allowedTools` / `--disallowedTools` | 個別ツールの許可/禁止 |
| `--tools` | 利用可能なツールセットを限定 |
| `--model` | `sonnet` / `opus` / フルモデル名 |
| `--effort` | `low` / `medium` / `high` / `xhigh` / `max` |
| `--fallback-model` | デフォルトモデル過負荷時のフォールバック先 |
| `--agent` / `--agents` | 個別/動的サブエージェント指定 |

**実用例**：

```
# プランモードで開始 → 必要時bypass可能
claude --permission-mode plan --allow-dangerously-skip-permissions

# Bashとファイル読み書きだけ許可
claude --tools "Bash,Edit,Read"

# 重い思考が必要なタスクはxhighで
claude --effort xhigh -p "design a sharding strategy"

# Opus 4.7をフルネームで指定
claude --model claude-opus-4-7

# 過負荷対策のフォールバック
claude -p --model opus --fallback-model sonnet "deep analysis"
```

**`--effort`は2026年5月時点でProMaxサブスクライバーのデフォルトが`medium`から`high`に昇格した**。`xhigh`はOpus 4.7専用、`max`はセッション中のみ有効で永続化されない。

<a id="flag-session"></a>

### セッション管理・プロンプト系フラグ

| フラグ | 役割 |
| --- | --- |
| `--resume` / `-r` | セッションをID/名前で再開 |
| `--continue` / `-c` | 直近セッションを継続 |
| `--from-pr` | PR番号/URLからリンク済みセッションを再開 |
| `--fork-session` | resume時に新IDで分岐 |
| `--session-id <UUID>` | UUIDを指定してセッション作成 |
| `--name` / `-n` | セッションに表示名を付与 |
| `--no-session-persistence` | セッションをディスクに保存しない（print mode） |
| `--system-prompt` / `--system-prompt-file` | システムプロンプトを完全置換 |
| `--append-system-prompt` / `--append-system-prompt-file` | システムプロンプトに追記 |
| `--exclude-dynamic-system-prompt-sections` | マシン依存セクションを最初のユーザーメッセージへ移動（キャッシュ最適化） |
| `--max-turns` | エージェントターン数上限 |
| `--max-budget-usd` | 金額上限 |
| `--init` / `--init-only` | Setup hooksを実行 |
| `--add-dir` | 追加の作業ディレクトリを許可 |
| `--mcp-config` / `--strict-mcp-config` | MCP設定ファイル指定/限定 |
| `--plugin-dir` / `--plugin-url` | このセッション限定でプラグインをロード |
| `--settings` / `--setting-sources` | 設定の差し替え/読み込み元限定 |
| `--betas` | API betaヘッダ指定（APIキー利用者のみ） |

**`--exclude-dynamic-system-prompt-sections`の実用例**：

```
# 複数マシン・複数ユーザーで同じタスクを叩く際、プロンプトキャッシュ命中率を上げる
claude -p \
  --exclude-dynamic-system-prompt-sections \
  --append-system-prompt-file ./team-rules.txt \
  "review the latest commits"
```

これは大規模な共有CIで効く。マシン依存情報（cwd・環境・gitステータス）を最初のユーザーメッセージへ動かすことで、システムプロンプトのキャッシュが他ユーザーと共有可能になる。

**`--plugin-dir`の実用例**：

```
# ローカルで開発中のプラグインを試す
claude --plugin-dir ./my-plugin

# ZIPアーカイブから一時利用
claude --plugin-url https://example.com/plugin.zip
```

設定に永続化せずに「このセッションだけ」プラグインを使えるので、検証・トラブルシューティングに重宝する。

---

## セッション内コマンド：基本操作・コンテキスト系

セッションを開始したあとに使う`/コマンド`を、用途別に解説していく。

<a id="slash-help"></a>

### /help / /doctor — ヘルプと診断

**概要**：`/help`は使えるコマンドを一覧表示。`/doctor`はインストール状態と設定を診断する。

**使い方**：

```
/help

/doctor
（結果の右上に問題があれば「f」キーでClaudeに自動修正させられる）
```

**実用例**：プラグインの読み込みエラーやMCP接続の不調を切り分けるとき、まず`/doctor`を叩く。各項目にステータスアイコンが付き、`f`を押すと修正案を実行してくれる。

<a id="slash-clear"></a>

### /clear / /compact / /context / /memory — コンテキスト操作

**概要**：それぞれ「会話を新規」「要約して節約」「現在のコンテキスト使用量を可視化」「CLAUDE.md/auto-memoryを編集」する。

**使い方**：

```
# 完全クリア（過去セッションは/resumeで残る）
/clear

# 焦点付きで圧縮
/compact focus on the API contract decisions

# コンテキストの色付きグリッド表示
/context

# CLAUDE.mdとauto-memoryエントリを編集
/memory
```

**実用例**：長時間セッションでトークンが膨らんだら`/context`でどこが重いかを見て、メモリブロートが原因なら`/memory`で整理、それでも足りなければ`/compact`で要約、というのが定石。`/compact`は引数で「何にフォーカスして要約するか」を指示できる点が強力だ。

<a id="slash-config"></a>

### /config / /status / /usage — 設定とステータス

**概要**：`/config`は設定UI、`/status`はバージョン・モデル・接続状況、`/usage`はコストとプラン使用量。

**使い方**：

```
/config

/status

/usage
（/cost と /stats はエイリアス。/statsを叩くとStatsタブが先に開く）
```

**実用例**：Pro/Max契約のRate Limitを確認したいときは`/usage`。`/status`は応答中でも開けるので「Claudeが今何をやっているか」を素早く確認できる。

<a id="slash-model"></a>

### /model / /effort / /fast — 推論調整

**概要**：モデル選択、思考の強度、Fast Mode（Opus 4.6で出力高速化）。

**使い方**：

```
# 確認ダイアログ付きでモデル切替
/model

# Sonnet 4.6に固定
/model claude-sonnet-4-6

# インタラクティブスライダーでeffort調整
/effort

# 直接high指定
/effort high

# Fast Mode切替（Opus 4.6専用）
/fast on
```

**実用例**：軽い修正は`/effort low`に下げてレスポンスを速くし、設計レビューは`/effort xhigh`に上げる、といった切り分けが効く。`/fast`はOpus 4.6で出力が物理的に速くなるが、小さなモデルへのダウングレードではない点に注意。

<a id="slash-resume"></a>

### /resume / /branch / /rewind / /rename — セッション履歴操作

**概要**：履歴の引き戻し・分岐・リネーム。

**使い方**：

```
# 別セッションへ切替
/resume auth-refactor

# 現在地点で会話を分岐（元はそのまま）
/branch try-different-approach

# チェックポイントへ巻き戻す
/rewind

# 名前を付ける（プロンプトバーに表示される）
/rename payments-feature
```

**実用例**：「この方針でうまくいくか試したいが、戻れるようにしたい」場面では`/branch`が最適。`/rewind`はファイル変更も戻すモードを選べるので、誤ったエージェント動作のロールバックに便利。

<a id="slash-diff"></a>

### /diff / /copy / /export — 結果の取り出し

**概要**：差分ビューア、応答コピー、会話のテキストエクスポート。

**使い方**：

```
/diff

# 直前応答をクリップボードへ
/copy

# 2つ前の応答をコピー
/copy 2

# テキスト保存
/export session-notes.md
```

**実用例**：`/copy`はコードブロックがあれば対話ピッカーが出て、特定のブロックだけコピーできる。SSH越しなら`w`を押せばファイルへ書き出せる。`/export`はトリアージのドキュメント化に使える。

---

## セッション内コマンド：コードレビュー・品質系

ここからは「Claude Codeを使う最大のメリット」と言ってもいい品質系コマンドの解説に入る。

<a id="slash-review"></a>

### /review — ローカルPRレビュー

**概要**：現在のセッション内でPRを軽量にレビューするビルトインコマンド。

**使い方**：

```
# 現在のブランチに対応するPRをレビュー
/review

# PR番号またはURLを指定
/review 123
/review https://github.com/owner/repo/pull/123
```

**実用例**：ドラフトPRを上げる前のセルフレビューに使う。`gh`CLIが入っていれば自動でPR検出する。深い検証が必要なら次の`/ultrareview`へ。

<a id="slash-ultrareview"></a>

### /ultrareview — クラウド並列レビュー

**概要**：Anthropicのクラウドサンドボックスで複数のレビューエージェントを並列起動し、独立に検証してから報告する深いレビュー。

**使い方**：

```
# 現在ブランチをレビュー
/ultrareview

# PR指定
/ultrareview 1234

# 非対話CLIから（CIで使う）
$ claude ultrareview 1234 --json --timeout 45
```

**実用例**：mergeの最終ゲートに置く。Pro・Maxは2026年5月5日まで月3回無料で、以降はExtra Usageが必要。1レビューあたりの目安は5〜20ドル程度。`--json`で機械可読な出力にできるのでGitHub Checksに統合しやすい。

<a id="slash-security-review"></a>

### /security-review — セキュリティ脆弱性スキャン

**概要**：現在ブランチの差分を読み、SQLインジェクション・認証バイパス・データ漏えい等のリスクを洗い出す。

**使い方**：

**実用例**：機密処理を含む変更をマージする前のセルフチェックに使う。OWASP Top 10系の典型脆弱性に強く、出力結果を踏まえて修正→再度`/security-review`が定番フロー。

<a id="slash-simplify"></a>

### /simplify — 並列レビュー＆修正（バンドルスキル）

**概要**：直近変更ファイルに対して3エージェントを並列で走らせ、再利用性・品質・効率の観点でレビューし修正まで適用するスキル。

**使い方**：

```
# 全観点で
/simplify

# 観点を絞る
/simplify focus on memory efficiency
/simplify focus on test coverage gaps
/simplify focus on duplicated logic
```

**実用例**：新規実装を一通り書いた直後に走らせる。コミット前にセルフレビュー→修正までやってくれるので、PRの初版品質が一段上がる。

<a id="slash-debug"></a>

### /debug — デバッグ支援（バンドルスキル）

**概要**：セッションのデバッグログを有効化し、ログを読みながら問題を切り分ける。

**使い方**：

```
/debug

# 状況を伝える
/debug MCP connection drops every 30s
```

**実用例**：MCPサーバーが落ちる、フックが期待通り動かない、API呼び出しが失敗する、といった原因不明の挙動を調べるときに最初に叩くコマンド。

<a id="slash-batch"></a>

### /batch — 大規模並列変更（バンドルスキル）

**概要**：コードベース全体に対する大規模変更を5〜30の独立ユニットに分解し、各ユニットを別worktreeでバックグラウンドエージェントが実行→各々がPRを作る。

**使い方**：

```
/batch migrate src/ from Solid to React

/batch upgrade all axios calls to fetch with proper error handling
```

**実用例**：依存リプレース・大規模リファクタ・命名規則統一など、横断的だが独立性のある変更。実行前に分解計画が提示されレビューできるので、暴走リスクが少ない。

---

## セッション内コマンド：設定・環境・拡張系

<a id="slash-permissions"></a>

### /permissions / /hooks / /skills / /plugin — 拡張・権限管理

**概要**：それぞれ権限ルール、ツールイベントフック、スキル、プラグインを管理。

**使い方**：

```
# 権限ルールUI
/permissions

# Hooks設定の確認
/hooks

# スキル一覧と表示制御
/skills
（tでトークン数ソート、Spaceで非表示切替、Enterで保存）

# プラグイン管理
/plugin
```

**実用例**：チームで共有したい権限ルールやHooksは`.claude/settings.json`に書いてコミット。個人用の上書きは`.claude/settings.local.json`に分ける。`/skills`はトークン消費の可視化に役立ち、不要なスキルを`name-only`に降格させてコンテキスト消費を抑えられる。

<a id="slash-agents"></a>

### /agents / /add-dir / /init — エージェント・ディレクトリ・初期化

**概要**：サブエージェント設定、追加作業ディレクトリ、CLAUDE.md初期化。

**使い方**：

```
/agents

/add-dir ../shared-libs

/init
```

**実用例**：モノレポで作業中、別パッケージのファイルも触りたいときは`/add-dir`。`/init`は新規プロジェクトでCLAUDE.mdの初期テンプレートを作る。`CLAUDE_CODE_NEW_INIT=1`を設定すると、スキル・フック・パーソナルメモリも対話的にセットアップされる。

<a id="slash-mcp"></a>

### /mcp / /chrome / /ide — 外部連携

**概要**：MCPサーバー、Chrome連携、IDE連携の管理。

**使い方**：

**実用例**：`/mcp`でOAuth認証の更新、サーバー個別の有効/無効を切り替えられる。Cursor・VS Code・JetBrains系を使っているなら`/ide`で接続状態を確認しておくとIDE連携の不調を切り分けやすい。

<a id="slash-theme"></a>

### /theme / /color / /statusline / /tui / /focus — 画面まわり

**概要**：テーマ、プロンプトバー色、ステータスライン、TUIレンダラ、フォーカスビュー。

**使い方**：

```
# テーマ変更（autoはターミナル背景に追従）
/theme

# プロンプトバーの色を一時変更
/color cyan

# ステータスラインを自然言語で構成
/statusline show git branch and current model

# 全画面ちらつき防止レンダラへ切替
/tui fullscreen

# 直近プロンプト・ツール要約・最終応答だけ表示
/focus
```

**実用例**：プロジェクトごとにプロンプト色を変えると、複数ターミナルを並べたときの誤操作が減る。`/tui fullscreen`は描画パフォーマンスに敏感な人に効く（環境変数`CLAUDE_CODE_NO_FLICKER=1`と等価）。

<a id="slash-keybindings"></a>

### /keybindings / /terminal-setup — 入力環境

**概要**：キーバインド設定、ターミナル特有のショートカット設定。

**使い方**：

```
/keybindings

/terminal-setup
```

**実用例**：`Shift+Enter`で改行が入らない端末（VS Code・Cursor・Windsurf・Alacritty・Zed）では`/terminal-setup`を叩いて自動構成する。Vimライクな操作にしたい場合は`/config`からEditor modeを切り替える（v2.1.92で`/vim`は廃止された）。

---

## セッション内コマンド：自動化・リモート系

<a id="slash-loop"></a>

### /loop — 繰り返し実行（バンドルスキル）

**概要**：プロンプトを一定間隔または自動ペースで繰り返し実行するスキル。

**使い方**：

```
# 5分ごとにデプロイ確認
/loop 5m check if the deploy finished and pingoff if so

# Claudeに自分でペース判断させる
/loop watch the build, ping me when green

# 引数なしならautonomousチェック（.claude/loop.mdがあればそれを使う）
/loop
```

**実用例**：CIの完了待ち、ロングタスクの監視、DBマイグレーション完了の確認など。セッションが開いている間だけ動く点に注意。長期運用なら`/schedule`を使う。

<a id="slash-schedule"></a>

### /schedule — 定期実行ルーチン

**概要**：cronベースで動くリモートエージェントを登録する。Claudeが対話的にセットアップを案内してくれる。

**使い方**：

```
# 対話的に作成
/schedule

# 説明から作成
/schedule run /security-review every Monday at 9am

# 一覧
/schedule list
```

**実用例**：毎週月曜の依存関係更新、夜間のテスト実行、毎朝のCIヘルスチェックなど。`/web-setup`でGitHub接続が済んでいないと初回はリクエストされる。

<a id="slash-autofix-pr"></a>

### /autofix-pr — PRを継続監視して自動修正

**概要**：現在ブランチのPRを監視して、CI失敗やレビューコメントが入ったら自動でpushして修正するWebセッションをspawnする。

**使い方**：

```
# デフォルト: CI失敗とレビューコメントを全部対応
/autofix-pr

# 指定範囲だけ対応
/autofix-pr only fix lint and type errors
```

**実用例**：レビュー指摘の対応中に他のコメントが追加で来るような繁忙期に効く。`gh`CLIの認証とWebセッションのアクセスが必要。

<a id="slash-remote-control"></a>

### /remote-control / /teleport / /desktop / /mobile — マルチデバイス連携

**概要**：claude.aiやモバイルアプリからセッションを操作する仕組み。

**使い方**：

```
# このセッションをclaude.aiから操作可能に
/remote-control

# Webセッションをローカル端末に引き戻す
/teleport
（/tpエイリアス）

# デスクトップアプリへ移行（macOS/Windows）
/desktop

# モバイルアプリのQR表示
/mobile
```

**実用例**：オフィスのPCでセッションを始め、移動中はモバイルから状況確認、自宅で続きを書く、といったフローが組める。`--remote-control`フラグを起動時に付ければ最初からRemote Control有効で立ち上がる。

<a id="slash-rewind"></a>

### /rewind / /tasks / /heapdump — 履歴・バックグラウンド・診断

**概要**：チェックポイント巻き戻し、バックグラウンドタスク管理、ヒープスナップショット。

**使い方**：

```
/rewind

# バックグラウンド実行中のbashプロセス管理
/tasks

# メモリ使用量診断
/heapdump
```

**実用例**：`/tasks`は`/bashes`のエイリアスでもあり、長時間動かしているバックグラウンドプロセスの状態を一覧できる。`/heapdump`は高CPU/高メモリ問題の解析用に`~/Desktop`にスナップショットを書く。

---

## バンドルスキル：プロンプトベースで動く拡張

`/simplify`・`/batch`・`/debug`・`/loop`・`/claude-api`・`/fewer-permission-prompts`の6つはビルトインコマンドではなく**バンドルスキル**だ。プロンプトとしてClaudeに渡され、Claude自身がツールを駆使して実行する。

<a id="slash-claude-api"></a>

### /claude-api — Claude API学習＆移行支援

**概要**：プロジェクトの言語（Python/TypeScript/Java/Go/Ruby/C#/PHP/cURL）に合わせたClaude APIリファレンスをロード。Managed Agentsのオンボーディングや、モデル移行も支援。

**使い方**：

```
# リファレンスをロード
/claude-api

# モデルマイグレーション（ファイルとターゲットモデルを対話で選択）
/claude-api migrate

# Managed Agentsを最初から作る
/claude-api managed-agents-onboard
```

**実用例**：Claude 4.6 → 4.7のマイグレーション時に`migrate`を叩くとモデルID・thinking設定・パラメータの差分を自動で更新してくれる。`anthropic`や`@anthropic-ai/sdk`をimportするコードでは自動起動もする。

<a id="slash-fewer-permission-prompts"></a>

### /fewer-permission-prompts — 権限プロンプト削減

**概要**：トランスクリプトを走査して、頻出するread-onlyのBash/MCPコマンドを抽出し、プロジェクトの`.claude/settings.json`にallowリストとして自動追加する。

**使い方**：

```
/fewer-permission-prompts
```

**実用例**：「`git status`を実行しますか？」「`ls`を実行しますか？」と毎回聞かれる状況を一気に解消する。チームに共有したい場合はそのままコミットする。

---

## カスタムスキル：自前のスラッシュコマンドを作る

`.claude/skills/<name>/SKILL.md`にYAMLフロントマター付きのMarkdownを置けば、それが`/<name>`コマンドとして使える。**v2.1.x系で従来の`.claude/commands/`はSkillsに統合された**。既存ファイルはそのまま動くが、新規はSkillsで書くのが推奨だ。

### 最小スキル例

```
---
description: Summarize uncommitted changes and flag risks. Use when the user asks what changed.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the diff in 2-3 bullets, then list risks (missing error handling, hardcoded values, tests to update). If the diff is empty, say "no uncommitted changes".
```

`!`バッククォート付きでシェルコマンドを書くと、Claudeに渡る前にコマンドが実行され、結果が埋め込まれる（dynamic context injection）。

### 主要フロントマターフィールド

| フィールド | 役割 |
| --- | --- |
| `name` | コマンド名（省略時はディレクトリ名） |
| `description` | 自動起動の判断材料。1,536字でtruncateされる |
| `when_to_use` | descriptionに追加される起動条件 |
| `argument-hint` | オートコンプリートのヒント |
| `arguments` | 名前付き位置引数（`$name`置換に対応） |
| `disable-model-invocation` | trueでClaude自動起動を禁止（手動のみ） |
| `user-invocable` | falseで`/`メニューから隠す（Claudeのみ起動可能） |
| `allowed-tools` | スキル有効時に確認なしで使えるツール |
| `model` | スキル実行中のモデルオーバーライド |
| `effort` | スキル実行中のeffortオーバーライド |
| `context: fork` | サブエージェントとして隔離実行 |
| `agent` | forkで使うエージェントタイプ |
| `paths` | 起動対象のglobパターン |
| `shell` | `bash`(default)or`powershell` |

### 引数置換

```
---
name: migrate-component
description: Migrate a component from one framework to another
---

Migrate the $0 component from $1 to $2. Preserve behavior and tests.
```

```
/migrate-component SearchBar React Vue
```

`$0`が`SearchBar`、`$1`が`React`、`$2`が`Vue`に置換される。`$ARGUMENTS`は引数全体、`$ARGUMENTS[N]`もしくは`$N`で個別アクセス、フロントマターで`arguments: [issue, branch]`と宣言すれば`$issue`・`$branch`で参照できる。

---

## 設定ファイルの優先順位とHooks

### settings.json階層

```
（高優先度）
managed-settings.json     # 組織管理
.claude/settings.json     # プロジェクト共有（commit）
.claude/settings.local.json  # プロジェクトローカル（.gitignore）
~/.claude/settings.json   # ユーザーグローバル
CLI args / 環境変数        # 一時上書き
（低優先度）
```

### 主要設定キー

| キー | 役割 |
| --- | --- |
| `model` | デフォルトモデル |
| `effortLevel` | デフォルトeffort |
| `permissions.defaultMode` | `auto` / `acceptEdits` / `ask` / `bypass` |
| `permissions.additionalDirectories` | `--add-dir`の永続化 |
| `permissions.allow` / `deny` / `ask` | ツール毎ルール |
| `hooks` | フックスクリプト |
| `mcpServers` | MCP設定 |
| `disableSkillShellExecution` | スキル内シェル実行の禁止 |
| `skillOverrides` | スキル可視性の上書き |
| `viewMode` | デフォルトビューモード |
| `autoScrollEnabled` | フルスクリーン自動スクロール |
| `showThinkingSummaries` | 思考要約表示（デフォルト無効化） |
| `refreshInterval` | ステータスライン再実行間隔 |
| `prUrlTemplate` | コードレビュー用カスタムURL |
| `sandbox.network.deniedDomains` | サンドボックスのネットワーク拒否ドメイン |
| `teammateMode` | エージェントチーム表示 |

### Hooks

ツール実行前後・セッション開始・セッション終了など、ライフサイクル各点で任意スクリプトを走らせる仕組み。タイミングは複数あり、代表的なのは以下。

| イベント | タイミング |
| --- | --- |
| `SessionStart` | セッション起動直後 |
| `Setup` | `--init` / `--maintenance`時に実行 |
| `PreToolUse` | ツール実行前 |
| `PostToolUse` | ツール実行後 |
| `UserPromptSubmit` | ユーザー入力直後 |
| `Stop` | 応答完了時 |
| `PermissionDenied` | 権限拒否時 |
| `Notification` | 通知発火時 |

`settings.json`に書く例：

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "npm run lint -- --fix" }
        ]
      }
    ]
  }
}
```

ファイルが書き換わるたびに自動でlint修正が走る、というよくある構成だ。

---

## 環境変数：知っておくと得する20個

CLIフラグの裏側で効く環境変数も多い。実用度の高いものを抜粋する。

| 環境変数 | 役割 |
| --- | --- |
| `ANTHROPIC_API_KEY` | APIキー認証 |
| `ANTHROPIC_MODEL` | デフォルトモデル |
| `ANTHROPIC_BEDROCK_SERVICE_TIER` | `default` / `flex` / `priority` |
| `CLAUDE_CODE_USE_BEDROCK` / `CLAUDE_CODE_USE_VERTEX` | クラウドプロバイダ切替 |
| `CLAUDE_CODE_SIMPLE` | `--bare`相当 |
| `CLAUDE_CODE_NO_FLICKER` | フルスクリーンレンダリング |
| `CLAUDE_CODE_FORCE_SYNC_OUTPUT` | 同期出力強制 |
| `CLAUDE_CODE_FORK_SUBAGENT` | フォーク可能サブエージェント |
| `CLAUDE_CODE_EFFORT_LEVEL` | デフォルトeffort |
| `CLAUDE_CODE_NEW_INIT` | `/init`の対話モード |
| `CLAUDE_CODE_USE_POWERSHELL_TOOL` | Windows PowerShellツール有効化 |
| `CLAUDE_CODE_DEBUG_LOGS_DIR` | デバッグログ出力先 |
| `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | `--add-dir`先のCLAUDE.mdも読み込む |
| `CLAUDE_CODE_SKIP_PROMPT_HISTORY` | プロンプト履歴を保存しない |
| `CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX` | リモート制御セッション名のprefix |
| `MCP_CONNECTION_NONBLOCKING` | MCP非ブロッキング起動 |
| `SLASH_COMMAND_TOOL_CHAR_BUDGET` | スキル説明の文字バジェット拡張 |

`SLASH_COMMAND_TOOL_CHAR_BUDGET`は**スキルが多い環境でClaudeが「スキルを認識できない」状態になったとき**の処方箋。デフォルトはコンテキストの1%（フォールバック8,000字）で、超えたぶんは説明が刈り取られて自動起動キーワードが消える。

---

## v2.1.x系で起きた破壊的変更まとめ

ここ数ヶ月の主な廃止と置き換えを表で整理する。

| バージョン | 廃止 | 置き換え |
| --- | --- | --- |
| v2.1.91 | `/pr-comments` | Claudeに直接「PRコメント見て」と指示する |
| v2.1.92 | `/vim` | `/config` → Editor mode |
| v2.1.111 | `--enable-auto-mode` | `--permission-mode auto`がShift+Tabサイクルに常駐 |
| v2.1.x | `/cost` 単独・`/stats`単独画面 | `/usage`に統合（両者はエイリアス） |
| v2.1.x | `/tag` | 廃止（プラグイン側`claude plugin tag`に移行） |
| v2.1.x | 思考要約のデフォルト表示 | `showThinkingSummaries: false`がデフォルト |

<a id="new-features"></a>  
新規追加で押さえておくべきもの：

| 追加 | 概要 |
| --- | --- |
| `/ultrareview` | クラウド並列レビュー（Pro/Maxは月3回無料・5/5まで） |
| `/security-review` | 脆弱性スキャン |
| `/schedule` (`/routines`) | cronベースのリモートエージェント |
| `/loop` | 繰り返し実行スキル |
| `/focus` | 簡易表示モード |
| `/effort` | 思考強度UI |
| `/recap` | セッション要約 |
| `/powerup` | インタラクティブ機能学習 |
| `/tui fullscreen` | ちらつき防止フルスクリーン |
| `/team-onboarding` | チーム向けオンボーディングガイド生成 |
| `/insights` | セッション分析レポート |
| `--bare` / `--from-pr` / `--plugin-dir` / `--plugin-url` | 高速起動・PR連動・プラグイン一時利用 |
| `xhigh` effort level | Opus 4.7専用の追加レベル |
| Cowork Dispatch / monitors / bin/ | プラグインマニフェスト拡張 |

---

## 実用シナリオ別おすすめコマンドセット

### 個人開発でPRを高品質に保ちたい

```
1. 実装後 → /simplify
2. PRを開く前 → /security-review
3. PR作成後 → /review
4. mergeの最終ゲート → /ultrareview
```

### CI/自動化に組み込みたい

```
# CIのレビューステップ
claude -p \
  --bare \
  --output-format json \
  --max-budget-usd 3 \
  --max-turns 5 \
  --tools "Bash,Read,Grep,Glob" \
  "review the last commit and output {summary, risks[]}"

# 別ステップでultrareview
claude ultrareview $PR_NUMBER --json --timeout 30 > review.json
```

### 大規模リファクタを安全に進めたい

```
1. /plan rewrite the auth module to use OAuth 2.1
2. /branch try-oauth21
3. /batch migrate auth/* from custom session to OAuth 2.1
4. /diff で変更レビュー → 必要に応じ /rewind
5. /review → /security-review → /ultrareview
```

### モバイルでもセッションを進めたい

```
# 朝、PCで起動
claude --remote-control "feature-payments"

# 移動中、claude.aiから状態確認・指示追加
# 帰宅後、PCで /teleport で続きをローカルへ
```

### 起動の遅さを解消したい

```
# 自動化なら--bare
alias ccq='claude --bare -p'

# フルスクリーンモード（ちらつき抑制）
echo 'export CLAUDE_CODE_NO_FLICKER=1' >> ~/.zshrc
```

---

## まとめ：コマンド体系を「層」で理解する

Claude Codeのコマンド群は**ターミナル層・セッション層・スキル層・設定層**の4階層で動いている。本記事のリファレンスを片手に、まずは以下の順で習熟していくと迷わない。

1. **ターミナル層**：`claude` / `-p` / `-c` / `-r` / `--worktree`
2. **セッション層・基本**：`/clear` / `/compact` / `/context` / `/usage` / `/model` / `/effort`
3. **セッション層・品質**：`/review` / `/security-review` / `/ultrareview` / `/simplify`
4. **スキル層**：`.claude/skills/` でカスタムコマンドを追加
5. **設定層**：`settings.json`の`permissions` / `hooks` / `mcpServers`を整える

CLIフラグについては`--bare`・`--from-pr`・`--plugin-dir`・`--exclude-dynamic-system-prompt-sections`の4つが、自動化ワークフローを作るうえでの強力なレバーになる。Hooksと組み合わせると\*\*「Claudeの行動をデフォルトで安全に・チーム共有で・速く動かす」\*\*体制が整う。

公式ドキュメントは数日単位で更新が入っているので、本記事と合わせて[Claude Code公式コマンドリファレンス](https://code.claude.com/docs/en/commands)もブックマークしておくと取りこぼしがない。アップデートで挙動が変わったコマンドや新コマンドが出たときは、本記事の該当セクションを更新していく。

---

## 参照ソース

---
