---
id: "2026-03-27-自作mcpサーバー入門-fastmcpでclaudeの手足を作る-01"
title: "自作MCPサーバー入門 — FastMCPでClaudeの手足を作る"
url: "https://qiita.com/AI-SKILL-LAB/items/96142820b715d5498165"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "LLM", "GPT", "Python", "qiita"]
date_published: "2026-03-27"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

# 自作MCPサーバー入門 — FastMCPでClaudeの手足を作る

**対象バージョン**: `mcp>=1.3.0`（2026年3月時点）/ Python 3.10以上

---

## 1. MCPとは何か — "Claudeに道具を渡す"という発想の転換

正直に言いましょう。MCPという言葉を最初に聞いたとき、「また新しいプロトコルの仕様書か...」と思いませんでしたか。

でも、実態はもっとシンプルな話です。

MCP（Model Context Protocol）は、**LLMに「道具」を渡すための標準的な接続仕様**です。Anthropicが2024年末に公開して以来、Claude Desktopをはじめ、Cline、Continue、Cursor等、対応クライアントが急速に増えています。

ちょっと考えてみましょう。ChatGPTのFunction CallingやClaudeのTool useは、LLMが「この関数を呼んでください」とJSON形式でリクエストを出す仕組みですよね。MCPはそれを**クライアントとサーバーに分離した**ものです。

```
[Cl
