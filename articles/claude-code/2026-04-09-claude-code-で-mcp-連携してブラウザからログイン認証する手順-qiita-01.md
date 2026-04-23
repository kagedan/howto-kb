---
id: "2026-04-09-claude-code-で-mcp-連携してブラウザからログイン認証する手順-qiita-01"
title: "Claude Code で MCP 連携してブラウザからログイン認証する手順 - Qiita"
url: "https://qiita.com/YumaInaura/items/9fa42f020b3cac7a51bb"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-09"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

# 参考

以下ガイドを参考に  
<https://code.claude.com/docs/ja/mcp>

## MCPサーバーの追加

例: Figmaの場合

以下をClaudeコンソールではなく、端末のコンソールでそのまま実行する

```
claude mcp add --transport http figma-remote-mcp https://mcp.figma.com/mcp
```

## 認証

こんどはClaudeのコンソールで `/mcp` と入力する

画面イメージ

[![Image](https://qiita-user-contents.imgix.net/https%3A%2F%2Fgithub.com%2Fuser-attachments%2Fassets%2F90e09cca-6f79-43c0-9cd7-025eb2c87fe3?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cec2f5387f9dbfca0d89a352ed857c0a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fgithub.com%2Fuser-attachments%2Fassets%2F90e09cca-6f79-43c0-9cd7-025eb2c87fe3?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cec2f5387f9dbfca0d89a352ed857c0a)

## ブラウザ認証

連携先のサービスの仕様次第だが、ブラウザを通して認証ができる

# NOTE

調べてもブラウザからの認証方法がよく分からなかったので、ここに記した
