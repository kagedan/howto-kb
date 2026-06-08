---
id: "2026-06-08-chatgptclaudecursorからedinet-dbのmcpで日本株データを引く接続まとめ-01"
title: "ChatGPT/Claude/CursorからEDINET DBのMCPで日本株データを引く(接続まとめ)"
url: "https://qiita.com/edinetdb/items/34248bb85b13faf53811"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "LLM", "GPT", "Python"]
date_published: "2026-06-08"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

日本の上場企業約3,800社の有価証券報告書データを、ChatGPTやClaude、Cursorから自然言語で引けるMCPサーバー(EDINET DB)の接続方法をまとめます。財務・大株主・セグメント・沿革など約60のツールを、AIアシスタントから直接呼べます。

リモートMCP(HTTPS + OAuth)なので、ローカルでプロセスを立てる必要はありません。無料プラン(100リクエスト/日)から使えます。

## 前提: APIキー or OAuth

- エンドポイント: `https://edinetdb.jp/mcp`
- 認証: OAuth 2.0(対応クライアント)またはAPIキー
- APIキー発行(無料): https://edinetdb.jp/developers

## Claude Desktop(カスタムコネクタ)

設定 → コネクタ → カスタムコネクタを追加。

- 名前: EDINET DB
- URL: `https://edinetdb.jp/mcp`
- 認証: OAuth 2.0(`https://edinetdb.jp/signup` のアカウントでサインイン)

OAuthなので、ブラウザでサインインするだけでキーの手動設定は不要です。

## Claude Code(CLI)

```bash
claude mcp add edinetdb https://edinetdb.jp/mcp --transport http
```

## Cursor

`.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "edinetdb": {
      "url": "https://edinetdb.jp/mcp",
      "transport": "streamable-http"
    }
  }
}
```

## Codex CLI

```bash
codex mcp add edinetdb https://edinetdb.jp/mcp
```

## ChatGPT(MCP / カスタムアプリ)

ChatGPTのMCP対応は、プランやワークスペース設定によって利用可否や画面名が変わります。管理者がDeveloper modeやカスタムアプリを有効化したうえで、`https://edinetdb.jp/mcp` をMCPアプリとして追加し、OAuthでサインインします。

## Pythonから直接叩く(MCP SDK)

クライアントを介さず、MCP SDKの`streamablehttp_client`で直接接続することもできます。

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "https://edinetdb.jp/mcp"
HEADERS = {"Authorization": "Bearer YOUR_API_KEY"}  # /developers で発行

async def main():
    async with streamablehttp_client(URL, headers=HEADERS) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("tools:", [t.name for t in tools.tools])

            # 例: 企業を検索
            res = await session.call_tool("search_companies", {"query": "キーエンス"})
            print(res.content)

asyncio.run(main())
```

## どんなツールがあるか

約60のツールが用意されています。代表的なもの:

- `search_companies` / `search_companies_batch` — 企業名・証券コード・業種・財務条件で検索
- `get_company` / `get_financials` — 基本情報と最大6年分の財務時系列
- `get_ranking` — 指標別ランキング(ROE・売上高・営業利益率など)
- `screen_companies` — 100以上の指標でスクリーニング
- `get_segments` / `get_detailed_expenses` — セグメント別業績・販管費内訳
- `get_shareholders` / `get_cross_shareholdings` — 大量保有報告書・政策保有株式
- `get_text_blocks` / `get_text_blocks_structured` — 有報の本文テキストと構造化データ
- `get_company_history` — 沿革タイムライン

全ツール一覧は接続後の`list_tools`で取得できます。

## 数値の信頼性について

財務数値は有報のXBRLから決定論的に抽出していて、抽出・マッピング・集計にLLMを使っていません。各データにはdocIDやEDINET書類への導線が含まれるため、必要に応じて元の有価証券報告書まで確認できます。AIエージェントに財務数値を扱わせる場合、出典まで追跡できる設計は重要です。

## 使ってみる

- APIキー発行: https://edinetdb.jp/developers
- MCPガイド: https://edinetdb.jp/docs/mcp-guide

ChatGPTやClaudeに「キーエンスの過去5年のROE推移は?」と聞くだけで、有報ベースの数字が返ってくる状態を、数分で作れます。

※ ツール構成や無料プランの上限(本記事執筆時点で100リクエスト/日)は変わることがあります。最新は開発者ページ(https://edinetdb.jp/developers)で確認してください。本記事は接続方法の紹介であり、投資判断を推奨するものではありません。
