---
id: "2026-04-23-mcpmodel-context-protocol完全入門-2026-aiエージェントとツールを繋ぐ-01"
title: "MCP（Model Context Protocol）完全入門 2026 — AIエージェントとツールを繋ぐ新標準"
url: "https://qiita.com/agdexai/items/6ba0889696a3f7e4911f"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-04-23"
date_collected: "2026-04-24"
summary_by: "auto-rss"
query: ""
---

# MCP（Model Context Protocol）完全入門 2026 — AIエージェントとツールを繋ぐ新標準

2024年末、Anthropicが発表した**MCP（Model Context Protocol）**は、AIエージェント開発の風景を一変させました。「AIのためのUSB-C」とも称されるこのオープン標準は、2026年現在、OpenAI・Google・Microsoftも採用を表明し、エージェントエコシステムの共通基盤になりつつあります。

本記事では、MCPの仕組み・実装方法・主要なMCPサーバー・ユースケースを体系的に解説します。

👉 **関連ツールを探すなら → [AgDex.ai](https://agdex.ai) — 400以上のAIエージェントツールを網羅したディレクトリ**

---

## MCPとは何か？

**MCP（Model Context Protocol）**は、LLM（大規模言語モデル）とデータソース・ツールを標準化された方法で接続するためのオープンプロトコルです。

従来の課題：
```
各アプリが独自実装
LLM → [独自API実装A] → ファイルシステム
LLM → [独自API実装B] → データベース  
LLM → [独自API実装C] → GitHub
```

MCPによる解決：
```
標準化されたプロトコル
LLM（ホスト） ←→ MCPクライアント ←→ MCPサーバー ←→ データソース
                  （標準プロトコル）
```

### 主要概念

| 概念 | 役割 |
|------|------|
| **MCP ホスト** | LLMを実行するアプリ（Claude Desktop、Cursor等） |
| **MCP クライアント** | ホスト内でサーバーと通信するコンポーネント |
| **MCP サーバー** | データソースへのアクセスを提供する軽量プログラム |
| **トランスポート** | 通信方式（stdio / SSE / HTTP） |

---

## MCPの3つのプリミティブ

MCPサーバーが提供できる機能は3種類に整理されます：

### 1. Tools（ツール）
LLMが呼び出せる関数。副作用あり（データ変更・API呼び出し等）。

```python
@mcp.tool()
def create_github_issue(
    title: str,
    body: str,
    repo: str
) -> str:
    """GitHubにIssueを作成する"""
    # 実装
    return f"Issue #{issue_number} を作成しました"
```

### 2. Resources（リソース）
LLMが読み取れるデータ。副作用なし（ファイル・DB・APIレスポンス等）。

```python
@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    """ローカルファイルの内容を返す"""
    with open(path) as f:
        return f.read()
```

### 3. Prompts（プロンプト）
再利用可能なプロンプトテンプレート。

```python
@mcp.prompt()
def code_review_prompt(code: str, language: str) -> str:
    return f"""
    以下の{language}コードをレビューしてください：
    
    ```{language}
    {code}
    ```
    
    セキュリティ・パフォーマンス・可読性の観点で評価してください。
    """
```

---

## MCPサーバーの実装：Python SDK入門

```bash
pip install mcp
```

### シンプルなMCPサーバー例

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

app = Server("my-mcp-server")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_weather",
            description="指定した都市の天気を取得する",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "都市名"
                    }
                },
                "required": ["city"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "get_weather":
        city = arguments["city"]
        # 実際にはAPIを呼ぶ
        return [types.TextContent(
            type="text",
            text=f"{city}の天気: 晴れ、気温22°C"
        )]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Claude Desktopへの設定

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
// %APPDATA%\Claude\claude_desktop_config.json (Windows)
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/my_server.py"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/username/Documents"]
    }
  }
}
```

---

## 主要なMCPサーバー一覧

### 公式サーバー（Anthropic提供）

| サーバー | 機能 |
|---------|------|
| `@modelcontextprotocol/server-filesystem` | ローカルファイルの読み書き |
| `@modelcontextprotocol/server-github` | GitHub操作（PR/Issue/コード） |
| `@modelcontextprotocol/server-postgres` | PostgreSQLクエリ実行 |
| `@modelcontextprotocol/server-brave-search` | Brave Search API |
| `@modelcontextprotocol/server-sqlite` | SQLiteデータベース操作 |
| `@modelcontextprotocol/server-puppeteer` | ブラウザ自動化 |
| `@modelcontextprotocol/server-google-maps` | Google Maps API |

### コミュニティサーバー（人気上位）

| サーバー | 機能 | GitHub |
|---------|------|--------|
| **Composio MCP** | 150以上のSaaS統合 | composiohq/composio |
| **Toolhouse MCP** | クラウドツール実行 | toolhouseai/toolhouse |
| **Zapier MCP** | Zapierアクション | — |
| **Obsidian MCP** | Obsidian Vault操作 | ガイドあり |
| **Linear MCP** | Linear課題管理 | — |
| **Notion MCP** | Notionページ操作 | — |
| **Slack MCP** | Slackメッセージ | — |
| **Jira MCP** | Jira課題管理 | — |

---

## MCP vs Function Calling：何が違うのか？

よく混同される「OpenAI Function Calling」とMCPの違いを整理します：

| 観点 | Function Calling | MCP |
|------|-----------------|-----|
| **標準化** | OpenAI独自 | オープン標準 |
| **再利用性** | アプリ固有 | 任意のホストで再利用 |
| **状態管理** | ステートレス | セッション/状態管理あり |
| **リソース提供** | ツールのみ | Tools + Resources + Prompts |
| **採用** | OpenAIエコシステム | マルチベンダー対応 |

**実践的な使い分け：**
- **Function Calling** → OpenAI API直接利用、シンプルなツール呼び出し
- **MCP** → 複数ホスト横断、開発環境統合、長期運用ツール

---

## ユースケース別：MCPの活用パターン

### パターン1：開発者ツール統合

```
Claude / Cursor
    ↓ MCP
GitHub + Linear + Sentry + Slack
→ 「バグを調査してIssue作成し、担当者に通知」を1プロンプトで完結
```

### パターン2：社内データアクセス

```
社内LLMアシスタント
    ↓ MCP
PostgreSQL + Notion + Google Drive
→ セキュアなコンテキスト内でデータ横断検索
```

### パターン3：エージェントへのツール配布

```python
# LangChainでMCPツールを使う例
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

async with MultiServerMCPClient({
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
        "transport": "stdio"
    }
}) as client:
    tools = await client.get_tools()
    agent = create_react_agent(ChatAnthropic(model="claude-sonnet-4-5"), tools)
    result = await agent.ainvoke({"messages": [("user", "srcディレクトリの構造を教えて")]})
```

---

## MCPのエコシステム：2026年の現状

### ホスト対応状況

| ホスト | MCP対応 | 状態 |
|--------|---------|------|
| **Claude Desktop** | ✅ | 公式（最初期から） |
| **Cursor** | ✅ | 完全対応 |
| **Windsurf** | ✅ | 対応済み |
| **Zed Editor** | ✅ | 対応済み |
| **VS Code (Copilot)** | ✅ | Microsoft公式対応 |
| **OpenAI ChatGPT** | 🔄 | 対応予定発表 |
| **Gemini** | 🔄 | Google検討中 |

### MCPサーバーのディレクトリ

- **mcp.so** — 最大のMCPサーバーディレクトリ、2000以上のサーバー掲載
- **mcpservers.org** — コミュニティキュレーション
- **GitHub awesome-mcp-servers** — 厳選リスト

---

## セキュリティ上の注意点

MCPを本番環境で使う際に考慮すべきリスク：

### 1. ツール呼び出しの承認
```python
# 危険な操作には確認を挟む
@mcp.tool()
def delete_file(path: str, confirmed: bool = False) -> str:
    if not confirmed:
        return f"⚠️ {path} を削除します。confirmed=true で再実行してください"
    os.remove(path)
    return f"削除完了: {path}"
```

### 2. スコープ制限
```json
// ファイルシステムアクセスは特定ディレクトリに限定
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y", "@modelcontextprotocol/server-filesystem",
        "/Users/username/workspace"  // ← スコープを限定
      ]
    }
  }
}
```

### 3. プロンプトインジェクション対策
- 外部データ（ファイル内容、Webページ等）経由の指示に注意
- ツール実行前のサマリー表示を推奨
- Lakera Guard等でリソース出力をスキャン

---

## まとめ：MCPが変えるエージェント開発

MCPの登場により、「ツール統合」の問題は一度解けば再利用できるようになりました：

**Before MCP（2024以前）：**
- 各エージェントフレームワーク独自のツール定義
- 同じGitHub統合を何度も書き直す
- ホストが変わると全部やり直し

**After MCP（2025〜）：**
- MCPサーバーを一度書けば全ホストで使える
- コミュニティサーバーを組み合わせてすぐ使える
- 標準化されたセキュリティモデル

2026年現在、MCPはすでに「AIエージェント開発のデファクト標準」になりつつあります。早めに習得しておく価値は高いです。

---

## 関連リソース

- [MCP公式ドキュメント](https://modelcontextprotocol.io/)
- [Anthropic MCP GitHub](https://github.com/modelcontextprotocol)
- [mcp.so — MCPサーバーディレクトリ](https://mcp.so)
- 👉 **[AgDex.ai](https://agdex.ai) — MCPを含む400以上のAIエージェントツールを探す**

---

*AgDex.aiはAIエージェントエコシステムのキュレーションディレクトリです。フレームワーク、LLM API、クラウド、開発ツールを横断的に比較・探索できます。*
