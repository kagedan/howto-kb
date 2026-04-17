---
id: "2026-04-16-claude-haiku-45で投稿に自動タグ付けするsnsを作った話-01"
title: "Claude Haiku 4.5で投稿に自動タグ付けするSNSを作った話"
url: "https://zenn.dev/mukkimuki/articles/38222e692bf8ba"
source: "zenn"
category: "ai-workflow"
tags: ["TypeScript", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

はじめに
個人開発で「ailog」というSNSを作っています。
「書くだけでいい。整理はAIがやる。」——投稿するとAIが自動でタグを付け、ナレッジマップとして可視化してくれるサービスです。
この記事では、その中核機能である「AI自動タグ付け」をClaude Haiku 4.5で実装した話を書きます。実際のコード、ハマったポイント、コスト感まで含めて共有します。
!
技術スタック: Next.js 16 / React 19 / TypeScript / Supabase / Tailwind CSS 4 / Claude Haiku 4.5 / Vercel


 なぜ自動タグ付け...
