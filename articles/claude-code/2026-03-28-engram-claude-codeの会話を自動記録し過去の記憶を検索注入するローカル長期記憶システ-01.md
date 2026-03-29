---
id: "2026-03-28-engram-claude-codeの会話を自動記録し過去の記憶を検索注入するローカル長期記憶システ-01"
title: "Engram - Claude Codeの会話を自動記録し、過去の記憶を検索・注入するローカル長期記憶システム"
url: "https://zenn.dev/okamyuji/articles/engram-claude-code-local-memory"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

!
謝辞とインスピレーションについて
Engramは、noprogllamaさんの記事「Claude Codeに長期記憶を持たせたら、壁打ちの質が変わった」と、そこで公開されているsui-memoryに深くインスパイアされて開発されました。
記事で提唱されている設計原則（外部依存の排除、保存時トークン消費ゼロ、自動保存、常時参照、編集と削除、最小依存）は、Engramの設計の柱としてそのまま採用させていただいています。特に「常時参照」というアイデア——ユーザーが明示的に検索しなくてもhookによって過去の記憶が自動注入される——は、Claude Codeの長期記憶に対する考え方を根本から...
