---
id: "2026-04-16-wsl2にインストールしたplaywright-mcpをclaudedesktopから使えるようにす-01"
title: "WSL2にインストールしたPlaywright-mcpをClaudeDesktopから使えるようにする"
url: "https://qiita.com/snow_cornice_man/items/605cd3fa576681c7b269"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "qiita"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

# はじめに
最近Claudeが流行っているので色々試している中で、Playwright-mcpをClaudeDesktopから使えるよう設定するのに色々苦労したので同じように困っている人のためにメモとして残したいと思います。

# 環境
- Windows 11
- WSL v2.6.3.0 (Debian 13.4)
- Claude Desktop for Windows v1.2773.0 
- WSL側でNode.js, Playwright（本体、MCPサーバ、ブラウザ）はインストール済とする

# どんな問題が起きたか？
基本的にClaudeDesktopでPlaywright-mcpを使うためにやることは、各ツールのインストールと`claude_desktop_config.json`の設定です。
たったそれだけのはずが3つの問題に遭遇し、思いのほか時間がかかってしまいました。。
1. [公式](https://github.com/microsoft/playwright-mcp?tab=readme-ov-file#getting-started)通りに`claud
