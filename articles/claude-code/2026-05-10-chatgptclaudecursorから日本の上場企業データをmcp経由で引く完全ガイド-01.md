---
id: "2026-05-10-chatgptclaudecursorから日本の上場企業データをmcp経由で引く完全ガイド-01"
title: "ChatGPT/Claude/Cursorから日本の上場企業データをMCP経由で引く完全ガイド"
url: "https://zenn.dev/edinetdb/articles/edinetdb-mcp-japan-stock-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "LLM", "OpenAI", "GPT"]
date_published: "2026-05-10"
date_collected: "2026-05-11"
summary_by: "auto-rss"
query: ""
---

# 概要

ここ半年で生成 AI からデータベースに接続する方法は大きく変わりました。MCP (Model Context Protocol) という、Anthropic が提唱しその後 OpenAI も対応した標準が、ChatGPT・Claude・Cursor といった主要クライアントから「外部データを取りに行く」共通の入口になっています。

EDINET DB では、日本の上場企業 約3,800社分の有価証券報告書データを 37 の MCP ツールで公開しました。本記事では各クライアントでの接続手順と、実際に使われている質問パターンを整理します。

詳細な解説と業務フロー例: <https://edinetdb.jp/blog/mcp-japan-stock-financial-data-complete-guide>

## できること

* ChatGPT デスクトップアプリから「○○社の ROE 推移は」と聞ける
* Claude (claude.ai / Claude Code) から「同業他社と比べて何位」と分析させられる
* Cursor のコーディング中に「この銘柄の前年比は」と即聞ける

REST API でも取れますが、MCP の利点は **LLM が自分でツールを選んで連鎖実行する** 点です。ROE が低い企業を screen → その中で営業利益率が改善している社を抽出 → 有報の MD&A セクションで原因を確認、といった一連の作業を、ユーザーが API 設計を意識せず自然言語で依頼できます。

## 接続: Claude Desktop / Claude Code

`~/Library/Application Support/Claude/claude_desktop_config.json` に以下を追加:

```
{
  "mcpServers": {
    "edinetdb": {
      "command": "npx",
      "args": ["-y", "mcp-remote@latest", "https://edinetdb.jp/mcp"]
    }
  }
}
```

OAuth 画面が出るので、edinetdb.jp アカウントでログインして承認すれば接続完了。

## 接続: ChatGPT デスクトップ

設定 → Connectors → 新しい MCP サーバー → URL に `https://edinetdb.jp/mcp` を入力。

## 接続: Cursor

`.cursor/mcp.json` (プロジェクト root) に追加:

```
{
  "mcpServers": {
    "edinetdb": {
      "url": "https://edinetdb.jp/mcp"
    }
  }
}
```

## ツール定義の重要性 (実装側の話)

技術的には、MCP サーバー側で「ツールの説明文・パラメータ仕様・利用例」を厳密に書くことが命です。LLM はその説明を見てツールを選ぶので、説明が曖昧だと正しいツールが呼ばれません。EDINET DB では 1 ヶ月以上ツール定義を磨き込みました。

具体例として、`get_financials` ツールの定義抜粋:

```
{
    "name": "get_financials",
    "description": (
        "企業の財務時系列データを最大6年分取得します。"
        "売上高・営業利益・純利益・ROE などの主要指標を年度別に返します。"
        "個社分析や同業他社との比較に最適。"
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "edinet_code": {"type": "string", "description": "EDINETコード (例: E02144)"},
            "fiscal_year": {"type": "integer", "description": "特定年度のみ取得 (省略時は最新6年)"},
        },
        "required": ["edinet_code"],
    },
}
```

description に「使い分けの示唆」を入れると、LLM が他のツール (`get_company`, `get_ranking`) と混同しなくなります。

## データ品質の方針

学術用途で MCP 経由データを引用する研究室も増えてきました。データ品質を「不正確より NULL」のスタンスで設計しているのも、その流れの中での選択です。誤った値で書かれた論文は撤回不能ですが、欠損なら補完できる、という非対称性を前提にしています。

## まとめ

LLM クライアントから日本の上場企業データを引く場合、まず MCP を考える。REST API は MCP の下にあるレイヤーとして使う、というのが現時点で取りやすい選択肢です。

接続手順の詳細とよく使われる質問パターンは公式ガイドへ:
