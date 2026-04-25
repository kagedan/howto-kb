---
id: "2026-04-24-goose入門-block発ossエージェントをmcpで拡張する-01"
title: "Goose入門 — Block発OSSエージェントをMCPで拡張する"
url: "https://zenn.dev/kai_kou/articles/198-goose-aaif-mcp-agent-developer-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-04-24"
date_collected: "2026-04-25"
summary_by: "auto-rss"
query: ""
---

## はじめに

[Goose](https://github.com/aaif-goose/goose) は、Block（旧Square）が開発したオープンソースのAIエージェントです。単なるコード補完ツールに留まらず、コードの実行・ファイル操作・依存関係のインストール・テスト実行まで自律的に行う「真のエージェント」として設計されています。

2025年後半の公開以来、Blockエンジニアの週8〜10時間節約、開発時間50〜75%削減という実績を上げ、[Agentic AI Foundation (AAIF)](https://aaif.io/) に寄贈されてLinux Foundation傘下のオープン標準プロジェクトとなりました。

この記事では、Gooseの概要・セットアップ・MCP拡張活用・カスタム拡張作成までを解説します。

### この記事で学べること

* Gooseとは何か、どんな問題を解決するか
* AAIF寄贈によるオープン標準としての位置づけ
* インストールと各LLMプロバイダーの設定方法
* MCPを使った拡張機能の追加
* カスタムMCP拡張の作成（Python）
* リードワーカーモデルとスケジュールタスクの活用

### 対象読者

* AIエージェントを開発ワークフローに組み込みたいエンジニア
* Claude Code / Cursorなどの商用エージェントの代替を探している方
* ローカルLLMでコスト削減を検討している方

### 前提条件

* Python 3.13以上 / Node.js
* LLMプロバイダーのAPIキー（Anthropic / OpenAI / Gemini、またはOllamaでゼロコスト）

---

## TL;DR

* GooseはBlock発のOSSエージェント（Apache 2.0）で、Rustで実装・AAIF/Linux Foundation傘下
* 15以上のLLMプロバイダーに対応（Claude、GPT、Gemini、Ollama等）を1ツールで切り替え可能
* Model Context Protocol（MCP）でSnowflake、Databricks、Slack、GitHub等と接続
* `goose configure` → APIキー設定のみで即座に利用開始
* 役割別モデル割り当て（計画用・実行用・レビュー用）と定期実行タスクをサポート

---

## GooseとAAIF — オープン標準エージェントの誕生

### BlockからAAIFへの寄贈

GooseはBlock社の内部ツールとして開発され、2025年にオープンソース化されました。その後、AnthropicのMCP・OpenAIのAGENTS.mdとともに[Agentic AI Foundation (AAIF)](https://aaif.io/)に寄贈され、Linux Foundation傘下のプロジェクトとなっています。

> Block is contributing its open source agent goose to the AAIF, along with Anthropic's Model Context Protocol (MCP) and OpenAI's AGENTS.md.  
> — [Block公式ブログ](https://block.xyz/inside/block-anthropic-and-openai-launch-the-agentic-ai-foundation)

AAIFはOpenAI・Anthropic・Blockが共同設立した財団で、AIエージェントのオープン標準を策定します。Gooseはその中心的なエージェント実装として位置付けられています。

### Apache 2.0ライセンスと商用利用

GooseはApache 2.0ライセンスで公開されており、商用プロダクトへの組み込みも無料で可能です。GitHub上では39,000以上のスターを獲得しています（2026年4月時点）。

---

## 主要機能

### 15以上のLLMプロバイダーに対応

GooseはAPIキーを差し替えるだけで複数のLLMを使い分けられます。

| カテゴリ | 対応プロバイダー |
| --- | --- |
| クラウドAPI | Anthropic (Claude), OpenAI, Google (Gemini), Azure OpenAI, Amazon Bedrock |
| 統合プロキシ | OpenRouter, Groq |
| ローカル実行 | Ollama (Qwen, Llama, Phi等) |
| その他 | Cohere, Mistral, Perplexity |

商用APIとローカルLLMを組み合わせることで、コスト効率と機能性を両立できます。

### MCP拡張エコシステム

GooseはModel Context Protocol（MCP）を採用しており、外部ツールとの連携を標準化されたインターフェースで実現します。公式・コミュニティ製の拡張機能を追加するだけで、Gooseの能力を大幅に拡張できます。

主な拡張機能の例：

* **GitHub**: Issue作成・PR操作・リポジトリ検索
* **Snowflake / Databricks**: データ分析・クエリ実行
* **Slack**: メッセージ送受信・チャンネル管理
* **Google Drive / Docs**: ドキュメント読み書き

### リードワーカーモデル

商用エージェントにはない特徴として、役割ごとに異なるLLMを割り当てる「リードワーカーモデル」があります。

| 役割 | 推奨モデル例 | 用途 |
| --- | --- | --- |
| Lead（計画） | Claude Opus 4.6 | 複雑な設計・アーキテクチャ決定 |
| Worker（実行） | Claude Sonnet 4.6 / Gemini Flash | 繰り返し処理・コード生成 |
| Reviewer（検証） | GPT-5.4 mini / ローカルLLM | コードレビュー・構文チェック |

これにより、高精度なモデルを「必要な場面だけ」使い、コストを最適化できます。

---

## インストールと初期セットアップ

### CLIインストール

```
# macOS CLI (Homebrew)
brew install block-goose-cli

# macOS デスクトップアプリ (Homebrew Cask)
brew install --cask block-goose

# Linux（スクリプト）
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash

# または公式ダウンロードページから
# https://goose-docs.ai/docs/getting-started/installation/
```

デスクトップアプリ版（Electron製）も配布されており、macOS / Linux / Windowsで動作します。

### 初期設定

インタラクティブなプロンプトが起動し、LLMプロバイダーとAPIキーを設定します。設定は `~/.config/goose/config.yaml` に保存されます。

```
# ~/.config/goose/config.yaml（設定例）
provider: anthropic
model: claude-sonnet-4-6
api_key: sk-ant-xxxxx
```

### Gooseを起動する

```
# インタラクティブモード（デフォルト）
goose

# タスクを直接指定して実行（-t はショートフラグ）
goose run --task "このリポジトリのREADMEを更新して"
goose run -t "テストを実行してエラーを修正して"
```

---

## プロバイダー設定

### Anthropic (Claude) の設定

```
# 環境変数で設定
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxx

# または configure コマンドで対話的に設定
goose configure
# → Provider: anthropic
# → Model: claude-sonnet-4-6
# → API Key: sk-ant-xxxxxxxx
```

利用可能なClaudeモデル：

```
claude-opus-4-6        # 高精度・複雑タスク向け
claude-sonnet-4-6      # バランス型（推奨）
claude-haiku-4-5-20251001  # 高速・軽量タスク向け
```

### Ollama（ローカルLLM・ゼロコスト）の設定

ローカル環境で完全無料のLLMを使う場合：

```
# Ollamaをインストール（https://ollama.com）
curl -fsSL https://ollama.com/install.sh | sh

# モデルをダウンロード
ollama pull qwen2.5    # 推奨: 高速・高性能
ollama pull llama3.2   # 代替選択肢

# Ollamaを起動
ollama serve

# GooseをOllama向けに設定
goose configure
# → Provider: ollama
# → Model: qwen2.5
# → Base URL: http://localhost:11434
```

Gooseはローカルで動作し、すべてのデータがマシン上に留まるため、機密コードや社内ドキュメントを安全に処理できます。

### Geminiの設定

```
export GEMINI_API_KEY=AIzaxxxxxxxx

goose configure
# → Provider: google
# → Model: gemini-2.5-flash   # コスト効率重視の場合
```

---

## MCP拡張機能の活用

### 既存のMCP拡張を追加する

MCP拡張は `~/.config/goose/config.yaml` の `extensions` セクションに追加します。

```
# ~/.config/goose/config.yaml
extensions:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: ghp_xxxxxxxx
```

設定後に `goose` を再起動すると拡張機能が認識されます。

### 拡張機能を使ったタスク実行

```
# GitHub Issueを自動クローズ
goose run --task "先週クローズされていないバグIssueを確認してトリアージして"

# Slackへの通知
goose run --task "デプロイ完了をSlack #dev-alertsチャンネルに通知して"
```

---

## カスタムMCP拡張の作成（Python）

GooseはMCPプロトコルを実装しているため、Python / TypeScript SDKを使ってカスタム拡張を作成できます。

### プロジェクト作成

```
# uvでプロジェクトを初期化（Python 3.13以上が必要）
pip install uv
uv init --lib mcp-myextension
cd mcp-myextension

# MCP Python SDKをインストール
uv add mcp
```

### カスタムツールの実装例

以下は、社内APIと連携するカスタムMCPサーバーの例です（低レベルAPIを使用。公式ドキュメントでは高レベルの `FastMCP` APIも推奨されています）。

```
# src/mcp_myextension/server.py
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import httpx

server = Server("my-extension")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_internal_data",
            description="社内APIからデータを取得します",
            inputSchema={
                "type": "object",
                "properties": {
                    "endpoint": {
                        "type": "string",
                        "description": "取得するAPIエンドポイント"
                    }
                },
                "required": ["endpoint"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_internal_data":
        endpoint = arguments["endpoint"]
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://internal-api.example.com/{endpoint}",
                headers={"Authorization": "Bearer TOKEN"}
            )
            return [TextContent(type="text", text=response.text)]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Gooseに拡張を登録する

```
# ~/.config/goose/config.yaml
extensions:
  my-extension:
    command: uv
    args: ["run", "python", "/path/to/mcp-myextension/src/mcp_myextension/server.py"]
    env:
      INTERNAL_API_TOKEN: your-token
```

---

## スケジュールタスクとDockerとの統合

### スケジュールタスクの設定

Gooseはcron形式のスケジュールタスクをサポートしており、定期的な自動化を実現できます。タスクをYAMLのレシピファイルとして定義し、`goose schedule` コマンドで登録します。

```
# スケジュール一覧表示
goose schedule list

# スケジュール削除
goose schedule remove <id>
```

### Dockerコンテナ内でGooseを実行

セキュアな実行環境が必要な場合、DockerコンテナでGooseを分離して実行できます。

GooseをDockerコンテナで分離実行することで、ホスト環境への影響を最小化できます。公式のDockerイメージを利用する方法と、カスタムDockerfileで構築する方法が提供されています。

```
# Docker Hub公式イメージを使う例（公式ドキュメントを参照）
docker run -e ANTHROPIC_API_KEY=sk-ant-xxx \
  block/goose run -t "テストを実行して"
```

構成例や最新のDockerfileはは[Docker公式ブログ](https://www.docker.com/blog/building-ai-agents-with-goose-and-docker/)を参照してください。

---

## デバッグとトラブルシューティング

| 問題 | 確認箇所 | 対処法 |
| --- | --- | --- |
| 拡張機能が認識されない | `~/.config/goose/config.yaml` | コマンドパスと環境変数を確認 |
| LLMに接続できない | ログ `~/.config/goose/logs` | APIキーと`base_url`を確認 |
| Ollamaでモデルなしエラー | `ollama list` | `ollama pull <model-name>` でモデルをダウンロード |
| タスクが途中で止まる | ログファイル | `--verbose`フラグで詳細ログを確認 |

```
# デバッグモードで実行
goose --verbose run --task "テストを実行して"

# ログを確認
tail -f ~/.config/goose/logs/goose.log
```

---

## Goose vs Claude Code — 使い分けの指針

| 観点 | Goose | Claude Code |
| --- | --- | --- |
| コスト | APIキーのみ（OSSは無料） | Claudeサブスクリプション必要 |
| LLM柔軟性 | 15+プロバイダーを切り替え可能 | Claude専用 |
| カスタマイズ | OSSゆえ深いカスタマイズ可能 | スキル/エージェント拡張のみ |
| セットアップ | やや手間（設定ファイル操作が必要） | シンプルな初期設定 |
| エコシステム | MCP標準、AAIF傘下 | Claude MCPと深い統合 |
| ローカル実行 | Ollamaでオフライン動作可能 | 不可（クラウドAPI必須） |

GooseはLLMを選ばない柔軟性とゼロコスト運用を重視するチームに、Claude CodeはClaude特化の高品質エージェント体験を重視するチームに適しています。

---

## まとめ

* **Goose**はBlock発のOSSエージェントで、AAIF/Linux Foundationのオープン標準プロジェクト
* 15以上のLLMプロバイダーを統一インターフェースで利用でき、コスト最適化が容易
* **MCP**対応により、GitHub・Snowflake・Slack等との連携をプラグイン形式で追加可能
* Python SDK で独自のMCP拡張を短時間で作成でき、社内ツールとの統合を実現
* スケジュールタスク・リードワーカーモデル・Docker対応など、本番運用に必要な機能を網羅

Claude CodeやCursorとは「競合」より「補完」の関係で、プロジェクトの特性に応じて使い分けることが現実的な選択です。

## 参考リンク
