---
id: "2026-04-07-複数aiエージェントが記憶を共有する中央メモリをsqlitemcpで実装した-01"
title: "複数AIエージェントが記憶を共有する「中央メモリ」をSQLite+MCPで実装した"
url: "https://zenn.dev/takawasi/articles/2251a734745f60"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "cowork", "zenn"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

!
📺 この記事の内容はYouTubeライブ配信中にリアルタイムで作業しながら書いています
👉 https://youtube.com/watch?v=i6O_rjIDTnw


 はじめに
個人でAIサービス群を開発・運用していると、ある問題にぶつかる。
「Claude Code（CC）」「DeepSeek（DSC）」「Cowork（ブラウザ経由のレビュー担当）」——複数のAIエージェントがそれぞれ別のコンテキストで動いているとき、誰が何を知っていて、何をやったのかが散逸する。
gitのコミットログ？ あれは「何を変えたか」しか分からない。「なぜやったか」「次に何をすべきか」はそこにな...
