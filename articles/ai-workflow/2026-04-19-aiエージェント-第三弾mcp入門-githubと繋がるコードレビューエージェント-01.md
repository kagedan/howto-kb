---
id: "2026-04-19-aiエージェント-第三弾mcp入門-githubと繋がるコードレビューエージェント-01"
title: "【AIエージェント 第三弾】MCP入門 ── GitHubと繋がるコードレビューエージェント"
url: "https://qiita.com/bit-tanghao/items/90e31851a97beee36fbe"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "LLM", "qiita"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

第2弾までのエージェントはローカルファイルしか読めなかった。実際の開発現場でレビューが必要なのはGitHubのPull Requestだ。

第3弾では自前のMCPサーバーを実装してGitHub APIをラップし、PRのdiffを自動取得してインラインコメント付きのレビューを投稿するパイプラインを作る。

---

## Tool UseとMCPの違い

第2弾ではAnthropicのTool Useを使ってツールを呼んでいた。Tool UseはAgentのコードの中に書いた関数をClaudeが呼ぶ仕組みだ。

MCPはそこから一歩進んで、ツールを**独立したサーバープロセス**として切り出す。サーバーとクライアントはJSON-RPC 2.0でstdio通信する。

```
Tool Use:  Claude → Agent内の関数（同一プロセス）
MCP:       Claude → AgentプロセスがMCPサーバープロセスを呼ぶ（プロセス間通信）
```

なぜMCPが生まれたのか。Tool Useでは同じツールを別のLLMやアプリケーションから使い回せない。MCPはツールを
