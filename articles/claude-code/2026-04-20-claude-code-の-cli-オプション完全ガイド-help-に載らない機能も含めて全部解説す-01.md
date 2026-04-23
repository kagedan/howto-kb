---
id: "2026-04-20-claude-code-の-cli-オプション完全ガイド-help-に載らない機能も含めて全部解説す-01"
title: "# Claude Code の CLI オプション完全ガイド：`--help` に載らない機能も含めて全部解説する"
url: "https://zenn.dev/takuh/articles/1d3877bc588df5"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

## はじめに

ターミナルから `claude --help` を叩くと、ずらりと並ぶオプションの多さに少し圧倒された経験はないでしょうか。`--bare`、`--effort`、`--permission-mode`、`--fork-session`、`--from-pr`、`--worktree`、`--teleport` など、名前だけ見てもすぐには用途が想像しづらいフラグが多数あります。しかも厄介なことに、Claude Code のヘルプ出力に**載っていないオプションも存在する**ため、`--help` だけを頼りにしていると使える機能を見落としがちです。

この記事では、Claude Code 2.1 系の CLI について、サブコマンドとオプションを一通り整理した上で、実際の開発現場でどう使い分けるかを解説します。単なるリファレンスの日本語訳ではなく、「このフラグはどういう場面で効くのか」「組み合わせるとどんなワークフローが作れるのか」という実践的な視点を盛り込みました。

想定する読者は以下のような方です。

* Claude Code をインストールしたばかりで、`claude` コマンドを素で叩く以上の使い方を知りたい方
* すでに日常的に使っているが、スクリプトや CI から呼び出す使い方に広げたい方
* チームでの運用や権限設計を意識しながら Claude Code を導入しようとしている方

記事の情報は Anthropic 公式ドキュメント(`code.claude.com/docs`)を一次情報として確認しています。ただし Claude Code は短いサイクルで機能追加・変更が行われているため、最終的には必ず自環境の `claude --help` と公式ドキュメントで最新の挙動を確認してください。

## 前提：Claude Code の基本構造

本題に入る前に、コマンドの構造をざっくり押さえておきます。公式の表記は以下の形です。

```
claude [options] [command] [prompt]
```

ここで登場する3つの要素を区別しておくと、後の話が理解しやすくなります。

1. **options（オプション / フラグ）**: `--model sonnet` や `--permission-mode plan` のように、挙動を切り替えるハイフン付き引数
2. **command（サブコマンド）**: `claude auth login` や `claude mcp` のように、特定の機能を呼び出す名前付きコマンド
3. **prompt（プロンプト）**: `claude "このプロジェクトの構造を説明して"` のように、そのまま Claude に渡されるテキスト

サブコマンドを指定しない場合は、インタラクティブセッションが起動します。プロンプトだけを渡した場合も、そのプロンプトを初期メッセージとしてインタラクティブセッションが始まる挙動です(`-p` を付けた場合のみ非対話で応答して終了します)。

## インストールと動作確認

Claude Code が手元にまだ入っていない場合は、公式のインストーラーで導入できます。macOS / Linux / WSL なら以下の1行です。

```
curl -fsSL https://claude.ai/install.sh | bash
```

Windows では PowerShell の `irm https://claude.ai/install.ps1 | iex` か、WinGet の `winget install Anthropic.ClaudeCode` が利用できます。Homebrew を使う場合は `brew install --cask claude-code` で、安定版とは別に `claude-code@latest` という最新チャネル版も用意されています。

インストール直後は `~/.local/bin` が `PATH` に通っていないこともあるので、以下を `.zshrc` や `.bashrc` に追記しておくと確実です。

```
export PATH="$HOME/.local/bin:$PATH"
```

動作確認は `claude --help` で行いますが、**公式ドキュメントには「`--help` にすべてのフラグが載っているわけではない」と明記されています**。したがって、本記事のような記事や公式リファレンスと併用するのが現実的です。

## サブコマンド一覧：まずは全体像から

Claude Code のサブコマンドは、大きく「セッション管理系」「認証系」「設定・診断系」「拡張機能管理系」に分類できます。ここでは代表的なものを用途別に紹介します。

### セッション起動と制御

| コマンド | 役割 |
| --- | --- |
| `claude` | インタラクティブセッションを起動する |
| `claude "プロンプト"` | 初期プロンプト付きでインタラクティブセッションを起動 |
| `claude -p "プロンプト"` | 非対話モード。応答を出力して終了する |
| `claude -c` | カレントディレクトリの直近会話を継続 |
| `claude -r` | セッションを選んで再開（インタラクティブピッカー） |
| `claude -r "セッション名"` | 指定したセッション ID または名前で再開 |

`-c` と `-r` はよく混同されますが、`-c` が「直近1つ」を開くのに対して、`-r` は「任意のセッションを選ぶ」のが違いです。プロジェクトを行き来して作業していると、つい `-c` で違うリポジトリの会話を引き継いでしまうことがあるので、複数案件を並行している場合は `-r` で明示的に選ぶ方が安全です。

### 認証・アカウント管理

```
# ログイン（通常のサブスク認証）
claude auth login

# Console（API キー運用）でログインしたい場合
claude auth login --console

# SSO を強制したい場合
claude auth login --sso

# メールアドレスを事前入力
claude auth login --email takuya@example.com

# 認証状態の確認
claude auth status
claude auth status --text  # 人間が読みやすい形式

# ログアウト
claude auth logout
```

`claude auth status` は JSON を返し、ログイン済みなら終了コード 0、未ログインなら 1 を返します。これは CI スクリプトで「認証済みかどうか」を判定したいときに便利です。

### セットアップと診断

```
# 長命の認証トークンを発行（CI やスクリプト用）
claude setup-token

# インストールのヘルスチェック
claude doctor

# 最新版への更新
claude update
```

`claude setup-token` は、GitHub Actions や GitLab CI の中で Claude Code を動かすときに重要です。通常のログイン状態は端末ごとに保持されるため、CI 環境ではこのトークンを環境変数に入れて使う運用になります。

### 拡張機能の管理

| コマンド | 役割 |
| --- | --- |
| `claude agents` | 設定済みのサブエージェントを一覧表示 |
| `claude mcp` | MCP (Model Context Protocol) サーバーの設定・管理 |
| `claude plugin` | プラグインのインストール・管理（`plugins` もエイリアス） |
| `claude auto-mode defaults` | Auto モードの分類器ルールを JSON で出力 |

MCP サーバーを扱う人にとっては `claude mcp` が日常的な窓口になります。筆者も Dify のナレッジベース API をラップする MCP サーバーや MoneyForward の MCP を接続する場面で使っていますが、このサブコマンドの下に `add`、`list`、`remove` といった操作がぶら下がっています。詳細は `claude mcp --help` で参照できます。

## オプションを役割別に解きほぐす

ここからが本題です。ヘルプ出力を頭から順に追うのではなく、**やりたいこと別**にフラグをまとめて整理します。

### カテゴリ1：セッションの性格を決める

#### モデル選択：`--model`

使いたいモデルを指定します。エイリアス（`sonnet`、`opus`、`haiku` など）と、`claude-sonnet-4-6` のような正式名称のどちらも受け付けます。

```
# Opus で起動
claude --model opus

# Sonnet の 1M コンテキスト版で起動
claude --model sonnet[1m]

# 正式名称で固定したい場合
claude --model claude-opus-4-6
```

特殊なエイリアスとして `opusplan` があります。これは**プランモード中は Opus で思考し、実行フェーズに入ると Sonnet に切り替える**という挙動をする賢いモードで、設計の深さとコード生成の軽快さを両立できます。普段 Opus と Sonnet を手で切り替えていた人にはおすすめです。

#### 思考量の調整：`--effort`

2026年時点の Claude Code には `effort`（思考量）という概念があります。`low`、`medium`、`high`、`xhigh`、`max` の5段階（ただし `xhigh` と `max` はモデル依存）から選べ、デフォルトは `medium` です。

```
# 難題に腰を据えて取り組ませたいとき
claude --effort high

# ちょっとしたリファクタや整形ならこれで十分
claude --effort low
```

公式ドキュメントでは\*\*「medium が多くのコーディング作業に対する推奨値」であり、「high や max は本当に深い推論が必要なタスクに予約すべき」\*\*と明言されています。これは実感としても合っていて、単純なファイル整形を `max` で走らせると「考えすぎて回り道する」ことがあります。難度とコストを見ながら段階的に上げるのが実務的です。

なお、セッション中に変えたいときはスラッシュコマンドの `/effort low` や `/effort max` で切り替えられます。また、プロンプト内に "ultrathink" という単語を含めると、そのターンだけ high effort で走るという面白いショートカットも用意されています。

#### システムプロンプトのカスタマイズ

システムプロンプトをいじるフラグは4種類あります。

| フラグ | 挙動 |
| --- | --- |
| `--system-prompt` | デフォルトのシステムプロンプトを**完全に置き換える** |
| `--system-prompt-file` | ファイル内容で**完全に置き換える** |
| `--append-system-prompt` | デフォルトに**末尾追加**する |
| `--append-system-prompt-file` | ファイル内容を**末尾追加**する |

運用上は、よほど特殊な用途でない限り `--append-system-prompt` か `--append-system-prompt-file` を使うのが推奨です。Claude Code の組み込みの振る舞い（ツール使用のルール、ファイル編集の流儀など）を壊さずに、プロジェクト固有の制約だけ足すことができます。

```
# TypeScript を必ず使わせる
claude --append-system-prompt "Always use TypeScript. Never suggest JavaScript alternatives."

# プロジェクトのコーディング規約をファイルで渡す
claude --append-system-prompt-file ./docs/coding-style.txt
```

#### カスタムエージェントの定義：`--agents`

`--agents` フラグは JSON でカスタムエージェントを動的に定義できます。サブエージェントの `.md` ファイルを作るほどではないけれど、特定の役割を持たせたインスタンスを起動したい時に便利です。

```
claude --agents '{
  "reviewer": {
    "description": "Reviews code changes",
    "prompt": "You are a strict code reviewer. Focus on security and performance."
  }
}'
```

### カテゴリ2：権限と安全性のコントロール

ここは最初のうちはなんとなくで済ませがちですが、**きちんと理解するとセッションの快適さが大きく変わる**領域です。

#### 権限モード：`--permission-mode`

Claude Code には以下の権限モードがあります。

| モード | 許諾なしに実行できること | 向いている用途 |
| --- | --- | --- |
| `default` | ファイル読み込み | 初めての作業、慎重に確認したいとき |
| `acceptEdits` | ファイル読み書き | コードをレビューしながら進めるとき |
| `plan` | ファイル読み込みのみ（編集はせず計画を立てる） | リファクタ設計、コードベース探索 |
| `auto` | すべての操作（分類器が背後で安全チェック） | 長時間タスク、プロンプト疲れの軽減 |
| `dontAsk` | 事前許可されたツールのみ | CI、ロックダウン環境 |
| `bypassPermissions` | すべての操作（チェックなし） | サンドボックス内のみ |

```
# 計画だけ立てさせたい
claude --permission-mode plan

# 編集は自動承認、コマンド実行は確認
claude --permission-mode acceptEdits
```

特に知っておいて損がないのが `plan` モードです。大規模なリファクタ、あるいは見慣れないコードベースを触る前に `claude --permission-mode plan` で起動して計画だけ立てさせると、実装を始める前に「このリファクタはどのファイルに影響して、どの順序で進めるべきか」がはっきりします。プランが固まったら「このプランで実行して」と指示するだけで済みます。

#### Auto モード：`claude auto-mode` と `--permission-mode auto`

Auto モードは比較的新しい機能で、**バックグラウンドで分類器モデルが各アクションの安全性を判定しながら、プロンプトを出さずに実行を進める**ものです。以下のコマンドでルールを確認できます。

```
# デフォルトの分類器ルールを JSON で確認
claude auto-mode defaults

# ファイルに保存して全体像を把握
claude auto-mode defaults > auto-mode-rules.json
```

Auto モードは Team、Enterprise、API プランで利用可能で、Claude Sonnet 4.6 または Opus 4.6 が必要です。Bedrock、Vertex AI、Foundry 経由では使えない点に注意してください。

#### 危険フラグ：`--dangerously-skip-permissions` と `--allow-dangerously-skip-permissions`

名前の通り、権限チェックをスキップするフラグです。ただし、この2つは役割が異なります。

* `--dangerously-skip-permissions`: いきなり bypassPermissions モードで起動する。`--permission-mode bypassPermissions` と等価
* `--allow-dangerously-skip-permissions`: bypassPermissions を Shift+Tab のサイクルに**追加するだけ**で、自動で有効化はしない

後者は「普段は plan モードで作業したいけれど、必要な時だけ Shift+Tab で bypassPermissions に切り替えたい」というユースケースで使います。以下のような組み合わせが可能です。

```
claude --permission-mode plan --allow-dangerously-skip-permissions
```

ただし `bypassPermissions` はインターネットに繋がらない完全隔離環境（Dev Container、VM など）でのみ使うことが強く推奨されています。プロンプトインジェクションへの防御がゼロになるためです。

特定のツールだけを許可する、あるいは逆に特定のツールを禁止する指定です。パターンマッチングにも対応しています。

```
# git 系のコマンドと Read だけ許可
claude --allowedTools "Bash(git *)" "Read"

# Edit ツールを封じる（読み取り専用セッション的な使い方）
claude --disallowedTools "Edit" "Write"
```

さらに厳しく「使えるツール自体を制限したい」場合は `--tools` を使います。

```
# Bash、Edit、Read のみ有効にする
claude --tools "Bash,Edit,Read"

# すべてのツールを無効化（チャット専用モード）
claude --tools ""
```

`--allowedTools` が「許可スキップ」なのに対して、`--tools` は「使える道具箱の中身を絞る」というニュアンスの違いがあります。

### カテゴリ3：会話の永続化と継続

#### セッション名とリジューム：`--name`、`-c`、`-r`、`--fork-session`

長く使うセッションには名前を付けておくと、後で探しやすくなります。

```
# セッションに名前を付けて起動
claude --name "auth-refactor"

# 後日、名前で再開
claude --resume "auth-refactor"

# セッション一覧から対話的に選んで再開
claude --resume
```

`--fork-session` を `--resume` や `--continue` と組み合わせると、**元のセッションを保ちつつ新しい ID でフォーク**できます。本線の作業を維持しながら「ちょっと別の方向性を試してみたい」ときに便利です。

```
claude --resume "auth-refactor" --fork-session
```

#### GitHub PR との連携：`--from-pr`

特定の PR に紐づけられたセッションを再開できます。`gh pr create` 経由で作った PR には自動でセッションが紐付くので、その場合は PR 番号や URL を渡すだけで会話を引き継げます。

```
# PR 番号で指定
claude --from-pr 123

# URL で指定
claude --from-pr https://github.com/my-org/my-repo/pull/123

# 検索ピッカーを開く
claude --from-pr
```

#### セッション ID の明示指定：`--session-id`

UUID 形式のセッション ID を自分で指定できます。外部システムと連携して ID を管理したい場合に使います。

```
claude --session-id "550e8400-e29b-41d4-a716-446655440000"
```

### カテゴリ4：作業ディレクトリと git 連携

#### ディレクトリ追加：`--add-dir`

デフォルトではカレントディレクトリの配下しか触れませんが、`--add-dir` で追加の作業領域を渡せます。モノレポで複数パッケージを横断して作業したいときに役立ちます。

```
claude --add-dir ../apps ../lib
```

**注意**：`--add-dir` は**ファイルアクセス権を付与するだけ**で、追加ディレクトリ内の `.claude/` 配下の設定（CLAUDE.md や hooks など）は基本的に自動読み込みされません。この点は公式ドキュメントにも明記されています。

#### git worktree：`--worktree` / `-w`

Claude Code は git worktree との連携機能を内蔵しており、`-w` フラグで**独立した作業ブランチ用のディレクトリ**を作ってそこで起動できます。

```
# 自動生成された名前で worktree を作る
claude -w

# 名前を指定
claude -w feature-oauth

# tmux と組み合わせる（iTerm2 があればネイティブペインを使用）
claude -w feature-oauth --tmux
```

worktree は `<repo>/.claude/worktrees/<name>` に作られるため、複数のタスクを並行して走らせたいときに便利です。メインブランチの作業を続けながら、別ブランチで実験的な変更を試す、といった使い方ができます。

### カテゴリ5：非対話モード（`-p` / `--print`）と周辺フラグ

CI やスクリプトから Claude Code を呼び出したい場合、`-p`（`--print`）が中心的な役割を担います。このフラグを付けると、応答を出力して即座に終了するワンショットモードになります。

```
# シンプルな例
claude -p "このリポジトリの言語構成を要約して"

# パイプで渡す
cat error.log | claude -p "このログのエラー原因を特定して"
```

`-p` と組み合わせて使うフラグがいくつかあります。

| フラグ | 役割 |
| --- | --- |
| `--output-format` | 出力フォーマット。`text`（デフォルト）、`json`、`stream-json` |
| `--input-format` | 入力フォーマット。`text` または `stream-json` |
| `--max-turns` | エージェントの最大ターン数を制限 |
| `--max-budget-usd` | 消費する API コストの上限（USD） |
| `--fallback-model` | デフォルトモデルが過負荷の時に切り替える代替モデル |
| `--json-schema` | JSON Schema に従った構造化出力を要求 |
| `--no-session-persistence` | セッションを保存しない（再開不可） |
| `--include-partial-messages` | ストリーミング中の途中メッセージも出力 |

例えば、バッチ処理で予算を決めて走らせたい時は以下のように書けます。

```
claude -p "全モジュールのテストカバレッジを見て、改善ポイントをまとめて" \
  --max-turns 10 \
  --max-budget-usd 2.00 \
  --output-format json
```

`--json-schema` は特に強力で、出力を特定の JSON 形式に強制できます。Claude Code の応答を後続のスクリプトで確実にパースしたい場合に使います。

```
claude -p "このファイルの関数一覧を抽出して" \
  --json-schema '{
    "type": "object",
    "properties": {
      "functions": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "lineNumber": {"type": "integer"}
          },
          "required": ["name", "lineNumber"]
        }
      }
    },
    "required": ["functions"]
  }'
```

### カテゴリ6：高速起動と最小モード：`--bare`

これはスクリプト実行において地味に効くフラグです。`--bare` を付けると、以下の自動発見処理がすべてスキップされます。

* hooks の読み込み
* LSP の起動
* プラグインの同期
* 自動メモリ
* CLAUDE.md の自動発見
* バックグラウンドのプリフェッチ
* キーチェーン読み取り

環境変数 `CLAUDE_CODE_SIMPLE=1` が自動でセットされ、認証は `ANTHROPIC_API_KEY` または `--settings` 経由の API キーに限定されます。つまり、**余計なことをせず最短で LLM 呼び出しだけを行う**モードです。

```
claude --bare -p "この関数の単体テストを書いて" --add-dir ./src
```

CI で Claude Code を呼ぶときや、複数の軽いジョブを大量に並列実行したいときに向いています。ただしプラグインや CLAUDE.md も読まれなくなるため、必要なコンテキストは `--system-prompt-file` や `--add-dir` で明示的に渡す必要があります。

### カテゴリ7：IDE・Web・Remote Control との連携

#### `--ide`：IDE への自動接続

起動時に、有効な IDE が1つだけ見つかった場合に自動接続します。VS Code や JetBrains と併用している場合に便利です。

#### `--chrome` / `--no-chrome`：Claude in Chrome との連携

Chrome ブラウザ統合を有効にすると、Web アプリのテスト、コンソールログ経由のデバッグ、フォーム入力の自動化、ページからのデータ抽出といったことがターミナルから指示できます。

```
# Chrome 連携を有効化
claude --chrome

# 逆に無効化（デフォルトで ON になっている環境用）
claude --no-chrome
```

#### `--remote`：Web セッションの新規作成

`claude.ai` 上に新しい Web セッションを作成できます。

```
claude --remote "ログインバグを修正して"
```

#### `--remote-control` / `--rc`：ローカルセッションを遠隔操作

ローカルで走らせている Claude Code のセッションを、`claude.ai` やモバイルアプリから遠隔操作できるようにします。

```
claude --remote-control "My Project"
```

出先からスマホで手元の PC のセッションに指示を出す、というような使い方ができます。

#### `--teleport`：Web セッションをローカルに引き継ぐ

`claude.ai` で始めたセッションを、ローカルターミナルに引き継いで継続できます。

### カテゴリ8：プラグインと MCP

#### `--plugin-dir`：セッション単位でプラグインを読む

指定したディレクトリのプラグインを、そのセッションに限って読み込めます。複数指定する場合はフラグを複数回書きます。

```
claude --plugin-dir ./local-plugins --plugin-dir ~/my-plugins
```

開発中のプラグインを試すときに、グローバル設定を汚さずに検証できるのが利点です。

#### `--mcp-config` と `--strict-mcp-config`

MCP サーバーを一時的に読ませたい場合は `--mcp-config` で JSON ファイルを渡せます。

```
claude --mcp-config ./my-mcp-servers.json
```

さらに `--strict-mcp-config` を付けると、**指定ファイルの MCP 以外は一切使わない**状態になります。テストや本番環境の切り分けに有効です。

```
claude --strict-mcp-config --mcp-config ./prod-mcp.json
```

### カテゴリ9：デバッグとログ

不具合調査には `--debug` と `--debug-file` が役立ちます。

```
# API と MCP 関連のログのみ有効化
claude --debug "api,mcp"

# すべて有効化 + ファイルに書き出す
claude --debug-file /tmp/claude-debug.log
```

`--verbose` は少し毛色が違って、「設定ファイルの verbose モードを上書き」する挙動です。ターンごとの詳細出力を一時的に見たい時に付けます。

## 実践的な組み合わせパターン

ここまでで個別のフラグを見てきましたが、現実の作業ではこれらを組み合わせて使います。いくつかパターンを挙げます。

### パターン1：リファクタ設計フェーズ

```
claude --model opusplan \
  --permission-mode plan \
  --effort high \
  --name "auth-oauth-migration"
```

Opus で深く考えさせ、plan モードで読み取り専用にし、セッション名を付けて後から戻れるようにする、という構成です。計画が固まったら `--resume` で戻り、権限モードを `acceptEdits` に切り替えて実装に入ります。

### パターン2：CI での非対話的なレビュー

```
claude -p "このコミット差分のセキュリティリスクを JSON で列挙して" \
  --bare \
  --permission-mode dontAsk \
  --allowedTools "Bash(git diff *)" "Read" \
  --max-turns 5 \
  --max-budget-usd 0.50 \
  --output-format json \
  --no-session-persistence
```

`--bare` で最短起動、`dontAsk` で事前許可ツール以外は拒否、予算とターン数に上限を設けつつ JSON で出力、セッションは保存しない。GitHub Actions などに組み込む際のテンプレとして使えます。

### パターン3：並列タスクの並行実行

```
# ターミナル1: 機能A
claude -w feature-a --tmux --name "feature-a"

# ターミナル2: 機能B
claude -w feature-b --tmux --name "feature-b"
```

git worktree で物理的に作業ディレクトリを分離しつつ、tmux で並べて眺める構成です。メインブランチを汚さずに、複数の実験を同時に走らせられます。

### パターン4：チームで安全に運用

```
claude --settings /etc/claude-code/team-settings.json \
  --setting-sources user,project \
  --permission-mode acceptEdits \
  --disallowedTools "Bash(rm *)" "Bash(sudo *)"
```

組織の設定ファイルを明示的に読み込ませ、危険なコマンドは一律拒否する運用です。`--setting-sources` で優先度の高い管理設定だけを信頼させる構成にも応用できます。

## `--help` に載らないフラグたち

冒頭で触れた通り、`claude --help` の出力は網羅的ではありません。公式の CLI リファレンスには記載があるものの、ヘルプには出てこないフラグとしては以下のようなものがあります。

* `--init`：初期化フックを実行してからインタラクティブモードに入る
* `--init-only`：初期化フックだけ実行して終了
* `--maintenance`：メンテナンスフックを実行してからインタラクティブモードに入る
* `--teleport`：Web セッションをローカルに引き継ぐ
* `--remote`：Web セッションを新規作成する
* `--append-system-prompt-file`：システムプロンプトの末尾追加をファイルから
* `--system-prompt-file`：システムプロンプトをファイルで置換
* `--channels`：MCP チャネル通知を受信する（リサーチプレビュー）
* `--teammate-mode`：エージェントチームのメイト表示モード

これらは**ドキュメントで明示的に「help には全て載っていない」と注意書きがある**ため、気になるフラグがあれば公式リファレンスを併読するのが確実です。

## トラブルシューティング

| 症状 | 対処 |
| --- | --- |
| `command not found: claude` | `~/.local/bin` が PATH に入っていない。`.zshrc` などに `export PATH="$HOME/.local/bin:$PATH"` を追記 |
| Auto モードが選べない | Team / Enterprise / API プランかつ Sonnet 4.6 または Opus 4.6 である必要がある。Bedrock / Vertex / Foundry では不可 |
| `--effort max` が効かない | Opus 4.6 のみ対応。Sonnet や Haiku では利用不可 |
| セッションが見つからない | `claude -r` でピッカーを開く。スコープはカレントディレクトリ配下が基本 |
| CI で `claude auth login` ができない | `claude setup-token` で長命トークンを発行し、環境変数として渡す |
| プラグインが読み込まれない | `--setting-sources` と `--plugin-dir` で明示的に読ませる。`--bare` 使用時は特に注意 |

## まとめ

Claude Code の CLI は、表面的にはシンプルに見えて、掘り下げると**セッション管理、権限制御、非対話実行、IDE 連携、Web 連携**と、広い守備範囲を持つツールです。オプションの数が多いのは「何にでも使える汎用性の裏返し」であり、一度に全部覚える必要はありません。

まず押さえるべきは、以下の4つです。

1. **`--model` と `--effort`** でタスクの難度にモデルを合わせる
2. **`--permission-mode`** で作業の性格（計画・レビュー・自動化）を切り替える
3. **`-p` と関連フラグ**で非対話モードを使いこなす
4. **`--resume` と `--name`、`--worktree`** で長期のセッション管理を整える

ここまで使えるようになると、「Claude Code をエディタの代わりに使う」段階から、「Claude Code を自分のワークフローに組み込んで自動化する」段階に進めます。後は用途に応じて、`--bare` でスクリプト用途を磨いたり、`--chrome` や `--remote-control` で働き方を拡張したりと、自然と広がっていくはずです。

## 参考リソース

最新の機能追加や仕様変更は頻繁に行われているため、業務で使う前には必ず公式ドキュメントと自環境の `claude --help` を照合するようにしてください。
