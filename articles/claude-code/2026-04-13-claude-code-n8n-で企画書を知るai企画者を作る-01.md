---
id: "2026-04-13-claude-code-n8n-で企画書を知るai企画者を作る-01"
title: "Claude Code + n8n で企画書を知るAI企画者を作る"
url: "https://zenn.dev/harada_ha/articles/3a50843a793634"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

1. なぜ作ったのか？
モバイルアプリを開発していると、繰り返しつまずく瞬間がある。

「この機能、ポリシーってどうなってたっけ？」

フィード投稿の通報処理基準、コメント作成条件、プロフィール編集制限 — こういったものはコードに埋め込まれておらず、Confluenceの企画ドキュメントのどこかに書いてある。だから毎回ドキュメントを漁るか、企画者にSlackで聞く必要があった。
そこで作った。「Confluenceの企画ポリシードキュメントをもとに即答するAIチャットボット」。開発者でも企画者でも、ブラウザひとつで使えるものとして。
結果物がn8n + Claude + Confl...
