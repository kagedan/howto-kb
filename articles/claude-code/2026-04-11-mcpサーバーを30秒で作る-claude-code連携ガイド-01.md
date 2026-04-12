---
id: "2026-04-11-mcpサーバーを30秒で作る-claude-code連携ガイド-01"
title: "MCPサーバーを30秒で作る — Claude Code連携ガイド"
url: "https://zenn.dev/nexus_lab_zen/articles/mcp-server-30sec"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

こんにちは、Nexus LabのZenです。CTOとしてClaude Codeエコシステム向けのツール開発をしています。
この記事では、MCPサーバーをたった30秒で作る方法を紹介します。使うのは私たちが開発した @nexus-lab/create-mcp-server というCLIツールです。

 MCPとは何か
MCP（Model Context Protocol） は、AIアシスタントが外部のツールやデータソースと連携するためのオープンプロトコルです。Anthropic社が策定し、Claude DesktopやClaude Codeなどが標準サポートしています。
MCPサーバーを作...
