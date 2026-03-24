---
id: "2026-03-23-rust-で-devin-ai-の-mcp-サーバーを作った-01"
title: "Rust で Devin AI の MCP サーバーを作った"
url: "https://zenn.dev/mjinno/articles/devin-mcp-rust-mcp-server"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-03-23"
date_collected: "2026-03-24"
summary_by: "auto-rss"
---

作ったもの
Claude Code や Cursor などの AI コーディングツールから、Devin AI にタスクを委譲できる MCP サーバーを Rust で作った。
https://github.com/mjinno09/devin-mcp
MCP（Model Context Protocol）は、AI ツールに外部機能を追加するための標準プロトコル。このサーバーを入れると、Claude Code の会話中に「この作業は Devin にやらせて」と言うだけで、Devin のセッションが立ち上がり、結果は GitHub PR として返ってくる。

 モチベーション

 MCP ...
