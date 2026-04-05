---
id: "2026-04-04-claude-mcp-サーバーを-hono-cloudflare-workers-で実装した話-01"
title: "Claude MCP サーバーを Hono + Cloudflare Workers で実装した話"
url: "https://zenn.dev/scrpgil/articles/a770cb68a63826"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "GPT", "zenn"]
date_published: "2026-04-04"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

はじめに
私は個人プロジェクトとして、週次カンバンボード「LetWeek」を開発している。ポモドーロ、GTD、すきま時間予定表——これらのテクニックを一箇所で実践できるツールが欲しくて作り始めたものだ。
開発を進める中で、ひとつの設計判断をした。アプリ内にAIチャットを持たないということだ。
私自身がすでにChatGPTやClaudeを日常的に使っていたので、LetWeekのデータにそれらのAIからアクセスできるようにした方が自然だろうと考えた。そこで MCP (Model Context Protocol) を使ってClaude連携を実装した。stdioとStreamable HT...
