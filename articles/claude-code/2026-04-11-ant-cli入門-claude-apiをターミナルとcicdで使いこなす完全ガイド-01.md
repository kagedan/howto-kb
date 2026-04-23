---
id: "2026-04-11-ant-cli入門-claude-apiをターミナルとcicdで使いこなす完全ガイド-01"
title: "ant CLI入門 — Claude APIをターミナルとCI/CDで使いこなす完全ガイド"
url: "https://qiita.com/kai_kou/items/ae85e3ea3e3e4be84e20"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## はじめに

AnthropicはClaude API専用の公式コマンドラインツール **ant CLI** をリリースしました。`curl` でAPIを叩くより大幅に少ないコードで、Claude APIのすべてのリソースをターミナルから操作できます。

### この記事で学べること

* ant CLIのインストールとセットアップ
* Messages APIへのメッセージ送信とレスポンス整形
* エージェント・セッションのCLI操作（beta:リソース）
* `--transform` を使った出力フィルタリング
* YAML定義ファイルによるAPIリソースのGit管理
* Claude Codeとant CLIの連携

### 対象読者

* Claude APIをターミナルやスクリプトから利用したいエンジニア
* Claude Managed Agentsをコマンドラインで管理したい方
* curlを使ったAPI呼び出しをより効率化したい方

### 前提条件

---

## TL;DR

* ant CLIはAnthropicが公式提供するClaude API専用CLIツール（v1.1.0、2026年4月9日リリース）
* `brew install anthropics/tap/ant` または `go install` でインストール可能
* `curl` + JSON手書きの代わりに、typed flags や YAML heredoc でリクエストを組み立てられる
* `--transform`（GJSON）でレスポンスを整形してシェル変数に代入できる
* `beta:agents`、`beta:sessions` サブコマンドでManaged Agentsをターミナルから管理可能
* YAML定義ファイルをGitに管理してCI/CDパイプラインでAPIリソースを同期できる

---

## ant CLIとは

ant CLIは[Anthropic公式のCLIツール](https://platform.claude.com/docs/en/api/sdks/cli)で、Claude APIのすべてのリソースを `resource action` パターンのコマンドから操作できます。

```
ant <resource>[:<subresource>] <action> [flags]
```

最新バージョンは **v1.1.0**（2026年4月9日リリース）。Go製（MIT License）で、[anthropics/anthropic-cli](https://github.com/anthropics/anthropic-cli) にてオープンソースで公開されています。

### curlと比較した主な利点

| 機能 | curl | ant CLI |
| --- | --- | --- |
| リクエストボディの記述 | JSON手書き | typed flags / YAML / heredoc |
| ファイルのインライン | base64変換が必要 | `@path` 参照で自動変換 |
| レスポンスの整形 | jq が別途必要 | `--transform`（GJSON）内蔵 |
| ページネーション | 手動ループ | list系で自動ページネーション |
| betaヘッダー | 手動で `anthropic-beta` を付与 | `beta:` リソースで自動付与 |
| Claude Codeとの連携 | ネイティブ対応なし | Claude Codeがant出力を直接解析 |

---

## インストール・セットアップ

### Homebrew（macOS）

```
brew install anthropics/tap/ant

# バイナリのquarantineを解除（macOS必須）
xattr -d com.apple.quarantine "$(brew --prefix)/bin/ant"
```

### curl（Linux / WSL）

```
VERSION=1.0.0
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m | sed -e 's/x86_64/amd64/' -e 's/aarch64/arm64/')
curl -fsSL "https://github.com/anthropics/anthropic-cli/releases/download/v${VERSION}/ant_${VERSION}_${OS}_${ARCH}.tar.gz" \
  | sudo tar -xz -C /usr/local/bin ant
```

### Go（ソースビルド）

Go 1.22以上が必要です。

```
go install github.com/anthropics/anthropic-cli/cmd/ant@latest

# Go binをPATHに追加
export PATH="$PATH:$(go env GOPATH)/bin"
```

### バージョン確認

### API キー設定

```
# zsh
echo 'export ANTHROPIC_API_KEY=sk-ant-api03-...' >> ~/.zshrc
source ~/.zshrc

# bash
echo 'export ANTHROPIC_API_KEY=sk-ant-api03-...' >> ~/.bashrc
source ~/.bashrc
```

---

## 基本的な使い方

### メッセージ送信（Messages API）

Claude APIへの最初のリクエストです。

```
ant messages create \
  --model claude-opus-4-6 \
  --max-tokens 1024 \
  --message '{role: user, content: "Hello, Claude"}'
```

レスポンス例（ターミナルではpretty-print JSONで表示）:

```
{
  "model": "claude-opus-4-6",
  "id": "msg_01YMmR5XodC5nTqMxLZMKaq6",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Hello! How are you doing today? Is there something I can help you with?"
    }
  ],
  "stop_reason": "end_turn",
  "usage": { "input_tokens": 27, "output_tokens": 20 }
}
```

パイプに繋いだ場合はコンパクトJSON（1行）が出力されるため、`jq` などのツールとシームレスに連携できます。

### 利用可能なモデル一覧

### 出力フォーマット

`--format` フラグで出力形式を制御できます。

| フォーマット | 説明 |
| --- | --- |
| `auto` | ターミナル時はpretty JSON、パイプ時はコンパクトJSON（デフォルト） |
| `json` | 常にpretty JSON |
| `jsonl` | 1オブジェクト1行（list系で便利） |
| `yaml` | YAML形式 |
| `pretty` | インデントありpretty JSON（ターミナル判定に依存しない明示的指定） |
| `raw` | APIレスポンスをそのまま出力 |
| `explore` | TUI折り畳み表示（大きなレスポンスに便利） |

YAMLフォーマットの例:

```
ant models retrieve --model-id claude-opus-4-6 --format yaml
```

```
type: model
id: claude-opus-4-6
display_name: Claude Opus 4.6
created_at: "2026-02-04T00:00:00Z"
```

TUI探索モード（`--format explore`）では矢印キーでノードを展開/折りたたみ、`/` で検索、`q` で終了できます。

---

## --transformでレスポンスを加工する

`--transform` フラグに [GJSON パス](https://github.com/tidwall/gjson/blob/master/SYNTAX.md) を指定すると、レスポンスから必要なフィールドだけを抽出できます。

### 本文テキストのみ抽出

```
ant messages create \
  --model claude-sonnet-4-6 \
  --max-tokens 512 \
  --message '{role: user, content: "Pythonでフィボナッチ数列を生成するコードを書いて"}' \
  --transform 'content.0.text' \
  --format yaml
```

`--format yaml` と組み合わせると、スカラー値がクォートなしで出力されるためシェル変数への代入に適しています。

### IDの抽出（スクリプト活用パターン）

```
AGENT_ID=$(ant beta:agents create \
  --name "My Agent" \
  --model '{id: claude-sonnet-4-6}' \
  --transform id --format yaml)

echo "Created Agent: $AGENT_ID"
```

### listコマンドとの組み合わせ

list系コマンドで `--transform` を使うと、各アイテムに対してクエリが適用されます。

```
ant beta:agents list \
  --transform "{id,name,model}" \
  --format jsonl
```

出力例:

```
{"id": "agent_011CYm1B...", "name": "Docs CLI Test Agent", "model": "claude-sonnet-4-6"}
{"id": "agent_011CYkVw...", "name": "Coffee Making Assistant", "model": "claude-sonnet-4-6"}
```

---

## エージェント・セッション操作（beta:リソース）

Managed Agentsのリソースは `beta:` プレフィックスのサブコマンドで操作します。`beta:` リソースは適切な `anthropic-beta` ヘッダーを自動で付与します。

### エージェントの作成

```
ant beta:agents create \
  --name "Research Agent" \
  --model '{id: claude-opus-4-6}' \
  --tool '{type: agent_toolset_20260401}' \
  --tool '{type: custom, name: search_docs, input_schema: {type: object, properties: {query: {type: string}}}}'
```

heredocを使ったYAMLスタイルも利用できます（変数展開を防ぐため区切り文字をクォート）:

```
ant beta:agents create <<'YAML'
name: Research Agent
model: claude-opus-4-6
system: |
  You are a research assistant. Cite sources for every claim.
tools:
  - type: agent_toolset_20260401
YAML
```

### エージェントの一覧・取得

```
# 一覧
ant beta:agents list

# 特定エージェントの取得
ant beta:agents retrieve --agent-id agent_01...
```

### セッションの作成と会話

セッションはエージェントが実際にタスクを実行する実行単位です。

```
# セッション作成
ant beta:sessions create \
  --agent '{type: agent, id: agent_011CYm1BLqPXpQRk5khsSXrs, version: 1}' \
  --environment env_01595EKxaaTTGwwY3kyXdtbs \
  --title "Research Task"
```

```
# ユーザーメッセージ送信
ant beta:sessions:events send \
  --session-id session_01JZCh78XvmxJjiXVy3oSi7K \
  --event '{type: user.message, content: [{type: text, text: "Pythonのasync/awaitを3行で説明して"}]}'
```

```
# 会話内容の確認
ant beta:sessions:events list \
  --session-id session_01JZCh78XvmxJjiXVy3oSi7K \
  --transform 'content.0.text' --format yaml
```

### セッションのリアルタイム監視

実行中のセッションのイベントをリアルタイムで受信できます。

```
ant beta:sessions stream --session-id session_01JZCh78XvmxJjiXVy3oSi7K
```

---

## API リソースのGit管理

ant CLIの特徴的な機能の一つが、**APIリソースをYAMLファイルとしてGitリポジトリで管理できる**点です。

### YAML定義ファイルの作成

エージェントの定義を `summarizer.agent.yaml` として保存します:

```
# summarizer.agent.yaml
name: Summarizer
model: claude-sonnet-4-6
system: |
  You are a helpful assistant that writes concise summaries.
tools:
  - type: agent_toolset_20260401
```

### 作成と更新

```
# 初回作成
ant beta:agents create < summarizer.agent.yaml

# 更新（agent IDとversionが必要）
ant beta:agents update \
  --agent-id agent_011CYm1BLqPXpQRk5khsSXrs \
  --version 1 \
  < summarizer.agent.yaml
```

### CI/CDでの自動同期

GitHub Actionsでのパイプライン例:

```
# .github/workflows/sync-agents.yml
name: Sync Agents
on:
  push:
    paths:
      - 'agents/*.yaml'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install ant CLI
        run: |
          VERSION=1.0.0
          curl -fsSL "https://github.com/anthropics/anthropic-cli/releases/download/v${VERSION}/ant_${VERSION}_linux_amd64.tar.gz" \
            | sudo tar -xz -C /usr/local/bin ant
      
      - name: Update Agent
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          ant beta:agents update \
            --agent-id ${{ vars.AGENT_ID }} \
            --version ${{ vars.AGENT_VERSION }} \
            < agents/summarizer.agent.yaml
```

これにより、エージェント定義の変更をGitのPRレビューフローで管理できます。

---

## スクリプティングパターン集

### list出力をパイプで次のコマンドへ渡す

```
# 最初のエージェントIDを取得して、バージョン一覧を確認
FIRST_AGENT=$(ant beta:agents list \
  --transform id --format yaml | head -1)

ant beta:agents:versions list \
  --agent-id "$FIRST_AGENT" \
  --transform "{version,created_at}" --format jsonl
```

### エラーの詳細確認

`--transform-error` と `--format-error` でエラーレスポンスを整形できます。

```
ant beta:agents retrieve --agent-id bogus \
  --transform-error error.message --format-error yaml 2>&1
```

出力例:

```
GET "https://api.anthropic.com/v1/agents/bogus?beta=true": 404 Not Found
Agent not found.
```

### PDFをMessages APIに送信

```
ant messages create \
  --model claude-opus-4-6 \
  --max-tokens 1024 \
  --message '{role: user, content: [
    {type: document, source: {type: base64, media_type: application/pdf, data: "@./report.pdf"}},
    {type: text, text: "このドキュメントの要点を3点にまとめてください"}
  ]}' \
  --transform 'content.0.text' --format yaml
```

`@./report.pdf` のように `@` を前置するだけで、バイナリファイルが自動でbase64エンコードされます。

### デバッグ（HTTPリクエスト/レスポンスの確認）

```
ant --debug beta:agents list
```

APIキーはリダクションされた状態で、送受信したHTTPの詳細がstderrに出力されます。

---

## Claude Codeとの連携

Claude Codeはant CLIをネイティブに認識します。ant CLIがインストールされ `ANTHROPIC_API_KEY` が設定されている環境では、Claude Codeに以下のような指示が可能です。

* "最近のエージェントセッションをリストして、エラーになったものをまとめて"
* "`./reports` 内のPDFをすべてFiles APIにアップロードして、IDをリストアップして"
* "`session_01...` のイベントを取得して、どこでエージェントが詰まったか分析して"

Claude Codeはant CLIの出力を直接パースして推論するため、カスタムの統合コードは不要です。

---

## シェル補完の設定

```
# zsh
ant @completion zsh > "${fpath[1]}/_ant"
autoload -U compinit && compinit

# bash
ant @completion bash > /etc/bash_completion.d/ant

# fish
ant @completion fish > ~/.config/fish/completions/ant.fish

# PowerShell
ant @completion powershell | Out-String | Invoke-Expression
# 永続化する場合:
# ant @completion powershell >> $PROFILE
```

---

## まとめ

ant CLIを活用することで、Claude APIの操作が大幅に効率化されます。

* **typed flags / YAML / heredoc**: curlのJSON手書きからの解放
* **`--transform`（GJSON）**: jqなしでレスポンスの整形・スカラー抽出が可能
* **`beta:` リソース**: Managed AgentsをCLIから管理（betaヘッダーを自動付与）
* **YAML定義ファイル**: エージェント・環境をGitで管理してCI/CDと統合
* **Claude Code連携**: ant出力をClaude Codeが直接解析

Claude APIを本格的に活用するプロジェクトでは、ant CLIの導入でターミナルワークフローとCI/CDの両方を効率化できます。

## 参考リンク
