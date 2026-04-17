---
id: "2026-04-17-claude-code-マルチインスタンス並行開発で-web版-を廃止した話-3インスタンス制への復-03"
title: "Claude Code マルチインスタンス並行開発で WEB版 を廃止した話 — 3インスタンス制への復帰"
url: "https://qiita.com/kanta13jp1/items/c6ee22c28d83903e6c3f"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "VSCode", "qiita"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

# Claude Code マルチインスタンス並行開発で WEB版 を廃止した話

## はじめに

「自分株式会社」という Flutter Web + Supabase のライフマネジメントアプリを個人開発している。競合21社 (Notion/Evernote/MoneyForward/Slack など) を1つに統合することを目指していて、現在 AI大学コンテンツは **66社** まで積み上がった。

開発体制は **Claude Code を4インスタンス同時起動** して並列で回していた:

- **VSCode版**: `lib/` (Flutter UI) と `supabase/functions/` 担当
- **Windowsアプリ版** (Claude Desktop): `docs/` と `supabase/migrations/` 担当
- **PowerShell版**: `.github/workflows/` と CI/CD 担当
- **WEB版** (claude.ai/code): ブログ英語翻訳・GitHub MCP 経由の PR レビュー担当
