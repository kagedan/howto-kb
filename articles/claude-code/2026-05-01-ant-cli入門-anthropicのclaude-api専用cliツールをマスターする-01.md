---
id: "2026-05-01-ant-cli入門-anthropicのclaude-api専用cliツールをマスターする-01"
title: "ant CLI入門 — AnthropicのClaude API専用CLIツールをマスターする"
url: "https://qiita.com/kai_kou/items/196bacb2393ee71918de"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "Python", "qiita"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

## はじめに

Anthropic が公式リリースした **ant CLI** は、Claude API のすべてのリソースをコマンドラインから操作できる開発者向けツールです。手書きの JSON なしに API リクエストを組み立て、`--transform` フラグでレスポンスを整形し、`@path` 構文でローカルファイルをリクエストにインライン展開できます。

Claude Code とのネイティブ統合も備えており、エージェントワークフロー・API プロトタイプ・CI/CD パイプラインへの組み込みまで幅広く活用できます。

### この記事で学べること

- ant CLI のインストールと認証設定
- メッセージ送信・ファイル入力・ストリーミングの基本操作
- `@path` ファイル参照構文と `--transform` フラグ（GJSON）の活用法
- YAML ベースのリソースバージョニング
- Claude Code との連携パターン

### 対象読者

- Claude API を使った開発を行っているエンジニア
- curl や HTTP クライアントでの API 呼び出しを CLI に置き換えたい方
- Claude Code でエージェントワークフローを自動化したい方

### 前提条件

- Anthropic API キーを取得済み（[Claude Console](https://console.anthropic.com/)）
- macOS / Linux（Windows は WSL で対応）
- Go 1.22 以上（Go インストール方法を選ぶ場合）

---

## TL;DR

- `brew install anthropics/tap/ant` または `go install` で即インストール可能
- `ant messages create --model claude-opus-4-7 --message '...'` で API コールが完結
- `@path` で PDF・画像・テキストを自動エンコードしてリクエストに埋め込める
- `--transform` と GJSON 構文でレスポンスから必要なフィールドだけ抽出できる
- エージェント・セッション・バッチを含む全 API リソースに対応

---

## インストール

### Homebrew（macOS 推奨）

```bash
brew install anthropics/tap/ant
```

### Go（クロスプラットフォーム）

Go 1.22 以上が必要です。

```bash
go install github.com/anthropics/anthropic-cli/cmd/ant@latest
```

### バイナリダウンロード（Linux / curl）

[GitHub Releases](https://github.com/anthropics/anthropic-cli/releases) から最新バイナリ（v1.3.2 以降）をダウンロードして PATH に配置します。

```bash
# インストール確認
ant --version
```

---

## 認証設定

ant CLI は環境変数 `ANTHROPIC_API_KEY` を読み込みます。

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

`.zshrc` や `.bashrc` に追記しておくと毎回設定不要です。

```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-..."' >> ~/.zshrc
source ~/.zshrc
```

**オプション: API エンドポイントの上書き**

カスタムプロキシや社内エンドポイントを使う場合は、環境変数またはフラグで指定します。

```bash
export ANTHROPIC_BASE_URL="https://your-proxy.example.com"
# または
ant messages create --base-url https://your-proxy.example.com ...
```

---

## コマンド構造

ant CLI のコマンドは、API のリソース階層をそのまま反映しています。

```
ant <resource>[:<subresource>] <action> [flags]
```

| リソース | アクション例 | 対応 API |
|---------|-----------|---------|
| `messages` | `create` | Messages API |
| `beta:agents` | `create`, `retrieve`, `list`, `update` | Agents API (Beta) |
| `beta:sessions` | `create`, `stream` | Sessions API (Beta) |
| `models` | `list`, `retrieve` | Models API |
| `batches` | `create`, `retrieve` | Batch API |

グローバルフラグ:

| フラグ | 説明 |
|-------|------|
| `--format` | 出力形式: `auto`, `json`, `jsonl`, `yaml`, `pretty`, `raw`, `explore` |
| `--transform` | GJSON 構文でレスポンスを絞り込む |
| `--debug` | HTTP リクエスト/レスポンスを表示 |
| `--base-url` | API エンドポイントを上書き |

---

## 基本操作

### メッセージ送信

```bash
ant messages create \
  --model claude-opus-4-7 \
  --max-tokens 1024 \
  --message '{role: user, content: "Claude APIのベストプラクティスを3つ教えてください"}'
```

モデルは `claude-opus-4-7`・`claude-sonnet-4-6`・`claude-haiku-4-5` などの正式モデル ID を指定します。

### システムプロンプト付きメッセージ

```bash
ant messages create \
  --model claude-sonnet-4-6 \
  --max-tokens 2048 \
  --system "あなたはPythonの専門家です。コードには必ずコメントを付けてください。" \
  --message '{role: user, content: "二分探索のPython実装を書いてください"}'
```

### YAML 形式で出力

```bash
ant messages create \
  --model claude-sonnet-4-6 \
  --max-tokens 512 \
  --message '{role: user, content: "Pythonでfizzbuzzを書いて"}' \
  --format yaml
```

---

## @path ファイル参照構文

`@path` 構文を使うと、ローカルファイルをリクエストフィールドに直接インライン展開できます。バイナリファイル（PDF・画像）は自動で Base64 エンコードされます。

### テキストファイルの読み込み（システムプロンプト）

```bash
ant messages create \
  --model claude-opus-4-7 \
  --max-tokens 2048 \
  --system @./prompts/code-reviewer.txt \
  --message '{role: user, content: "このコードをレビューして"}'
```

`prompts/code-reviewer.txt` の内容がそのままシステムプロンプトに挿入されます。

### PDF ドキュメントの送信

```bash
ant messages create \
  --model claude-opus-4-7 \
  --max-tokens 4096 \
  --message '{
    role: user,
    content: [
      {
        type: document,
        source: {
          type: base64,
          media_type: "application/pdf",
          data: "@./report.pdf"
        }
      },
      {
        type: text,
        text: "このレポートの主要な指摘事項を日本語で要約してください"
      }
    ]
  }'
```

### エンコードの明示指定

| 構文 | 動作 |
|------|------|
| `@./file.pdf` | 自動判定（バイナリ→Base64、テキスト→UTF-8） |
| `@file://./notes.txt` | テキストとして読み込む |
| `@data://./image.png` | Base64 強制エンコード |

---

## --transform フラグ（GJSON 構文）

`--transform` フラグは [GJSON](https://github.com/tidwall/gjson) 構文でレスポンス JSON を絞り込みます。jq なしでシェルスクリプトに組み込めます。

### テキスト本文だけ取り出す

```bash
ant messages create \
  --model claude-sonnet-4-6 \
  --max-tokens 512 \
  --message '{role: user, content: "今日の天気は？"}' \
  --transform 'content.0.text' \
  --format yaml
```

`--format yaml` と組み合わせると、スカラー値をクォートなしのプレーンテキストで出力します。


> `--format raw` を指定すると `--transform` が無効化されます。テキスト抽出には必ず `--format yaml` を使用してください。


### 複数フィールドを抽出

```bash
ant messages create \
  --model claude-sonnet-4-6 \
  --max-tokens 512 \
  --message '{role: user, content: "こんにちは"}' \
  --transform '{id,model,stop_reason}' \
  --format json
```

出力例:

```json
{"id":"msg_01XY...","model":"claude-sonnet-4-6","stop_reason":"end_turn"}
```

### シェル変数への代入

```bash
MESSAGE_ID=$(ant messages create \
  --model claude-sonnet-4-6 \
  --max-tokens 512 \
  --message '{role: user, content: "Hello"}' \
  --transform id \
  --format yaml)

echo "Message ID: $MESSAGE_ID"
```

### エージェント一覧をフィルタリング

```bash
ant beta:agents list \
  --transform "{id,name,model}" \
  --format jsonl
```

JSONL 形式で出力されるため、`while read` ループで処理しやすくなります。

---

## YAML ベースのリソースバージョニング

エージェント・環境・スキルの定義を YAML ファイルで管理することで、変更をバージョン管理できます。`--version` フラグによる楽観的ロック（Optimistic Locking）で、意図しない上書きを防止します。

### エージェント定義を YAML で管理

```yaml
# agents/code-review-agent.yaml
name: "Code Review Agent"
model: "claude-sonnet-4-6"
system: |
  あなたはシニアエンジニアです。
  コードの品質・セキュリティ・パフォーマンスを審査し、
  改善提案を日本語で提供してください。
max_tokens: 4096
```

### エージェントの作成・更新

```bash
# 作成
ant beta:agents create < agents/code-review-agent.yaml

# 取得（バージョン確認）
ant beta:agents retrieve --agent-id agent_01... --format yaml

# バージョン指定で更新（楽観的ロック）
ant beta:agents update \
  --agent-id agent_01... \
  --version 1 \
  < agents/code-review-agent.yaml
```

`--version` を指定すると、サーバー側のバージョンと一致しない場合にエラーを返すため、並行更新による上書き事故を防げます。

---

## Claude Code との統合

ant CLI は Claude Code とネイティブに連携します。Claude Code は内部で `ant` コマンドを呼び出し、構造化された出力を解析して API リソースを直接操作します。カスタム連携の実装は不要です。

### Claude Code からエージェントを操作するパターン

`$DIFF` をシェル変数として `--message` に直接展開すると、差分内の `"` や `$` がパースエラーを起こします。`@path` 構文で一時ファイル経由で渡すのが推奨パターンです。

```bash
# .claude/hooks/pre-commit.sh
#!/bin/bash
DIFF_FILE=$(mktemp)
git diff --cached | head -c 8000 > "$DIFF_FILE"

# @path 構文で差分ファイルを安全に渡す
REVIEW=$(ant messages create \
  --model claude-sonnet-4-6 \
  --max-tokens 2048 \
  --system @./.claude/prompts/code-review.txt \
  --message "{role: user, content: \"@$DIFF_FILE\"}" \
  --transform 'content.0.text' \
  --format yaml)

rm -f "$DIFF_FILE"
echo "$REVIEW"
```

### CI/CD パイプラインへの組み込み

```yaml
# .github/workflows/ai-review.yml
name: AI Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install ant CLI
        run: go install github.com/anthropics/anthropic-cli/cmd/ant@latest
      - name: Run AI Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          git diff origin/main...HEAD | head -c 8000 > /tmp/diff.txt
          ant messages create \
            --model claude-sonnet-4-6 \
            --max-tokens 4096 \
            --system "あなたはコードレビュアーです。問題点を指摘してください。" \
            --message '{role: user, content: "@/tmp/diff.txt"}' \
            --transform 'content.0.text' \
            --format yaml
```

---

## デバッグ

`--debug` フラグで HTTP リクエスト/レスポンスの詳細を確認できます。

```bash
ant messages create \
  --model claude-sonnet-4-6 \
  --max-tokens 128 \
  --message '{role: user, content: "test"}' \
  --debug
```

出力例（抜粋）:

```
> POST https://api.anthropic.com/v1/messages
> Content-Type: application/json
> x-api-key: sk-ant-api03-...
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 128,
  "messages": [{"role": "user", "content": "test"}]
}
< HTTP/2 200
< content-type: application/json
...
```

---

## 注意点

### API キーの管理

`ANTHROPIC_API_KEY` はシェルの履歴や `.env` ファイルに平文で残らないよう注意してください。CI 環境では Repository Secrets を使用し、ローカルでは `direnv` や `1Password CLI` などのシークレット管理ツールと組み合わせることを推奨します。

### レートリミット

ant CLI は標準の Claude API レートリミットに従います。大量リクエストを送る場合は Batch API（`ant batches create`）の使用を検討してください。

### Beta リソース

`beta:agents`・`beta:sessions` など `beta:` プレフィックスのリソースは、API の変更が発生する可能性があります。本番環境への適用前に公式ドキュメントで最新の仕様を確認してください。

---

## まとめ

ant CLI の主要ポイントを整理します：

- **統一コマンド構文**: `ant <resource> <action>` で Messages・Agents・Batches などすべての API リソースを操作できる
- **`@path` ファイル参照**: PDF・画像・テキストを自動エンコードしてリクエストにインライン展開できる
- **`--transform` + GJSON**: jq 不要でレスポンスフィールドを抽出・整形し、シェル変数への代入もできる
- **YAML バージョニング**: エージェント定義を YAML ファイルで管理し、楽観的ロックで安全に更新できる
- **Claude Code 統合**: Claude Code が `ant` をネイティブ呼び出しするため、カスタム連携の実装が不要

公式ドキュメント（[platform.claude.com/docs/en/api/sdks/cli](https://platform.claude.com/docs/en/api/sdks/cli)）に最新の全コマンドリファレンスが掲載されています。

## 参考リンク

- [anthropics/anthropic-cli — GitHub](https://github.com/anthropics/anthropic-cli) — ソースコードと最新リリース
- [Claude API CLI ドキュメント](https://platform.claude.com/docs/en/api/sdks/cli) — 公式コマンドリファレンス
- [Claude Console](https://console.anthropic.com/) — API キーの取得
- [GJSON ドキュメント](https://github.com/tidwall/gjson) — --transform フラグで使用するクエリ構文
