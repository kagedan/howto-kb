---
id: "2026-03-21-ai-agent-を-mcp-で別の-ai-agent-に相談させる-kiro-amazon-bed-01"
title: "AI Agent を MCP で別の AI Agent に相談させる (Kiro / Amazon Bedrock)"
url: "https://zenn.dev/kumagaias/articles/9f70ea31a66cd4"
source: "zenn"
category: "claude-code"
tags: ["MCP", "AI-agent", "Gemini", "zenn"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

背景
AI エージェントがアドホックな対応でループし続けることがあります。
そんなとき、別の AI（Claude や Gemini）に会話のログを渡して相談すると、同じモデルを使っていても的確な答えが返ってくることがあります。
コンテキストが多すぎるとループしてしまうのかもしれません[1]。
そこで、MCP (Model Context Protocol) を使って、AI エージェントが別の AI に自動で相談できる仕組みを試してみました。

 実装：Bedrock Advisor MCP Server
私の場合は Kiro (IDE) を使っていて、AWS アカウントもあり、AWS...
