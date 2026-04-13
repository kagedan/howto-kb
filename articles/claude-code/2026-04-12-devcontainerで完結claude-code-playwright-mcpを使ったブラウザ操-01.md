---
id: "2026-04-12-devcontainerで完結claude-code-playwright-mcpを使ったブラウザ操-01"
title: "DevContainerで完結！Claude Code + Playwright MCPを使ったブラウザ操作自動化の構築手順"
url: "https://zenn.dev/secondselection/articles/claude_playwright"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

はじめに
Claude Code + Playwright MCPを使うと、自然言語でブラウザを操作し、その操作をそのままRPAスクリプトとして自動生成できます。
イメージとしては、RPAのコードをClaude Codeに作らせるイメージです。
Playwrightの知識がなくても、操作を見せるだけでスクリプトを作れる点が最大のメリットです。
本記事では、この環境をDevContainer内で完結させる構築手順をまとめます。
動作確認として、NotebookLMのソース同期を自動化した例も紹介します。

 Playwright とは
Microsoftが開発したオープンソースのブラウ...
