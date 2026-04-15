---
id: "2026-04-14-aiエージェントに権限を与えすぎると何が起きるexcessive-agencyを初心者向けに解説-01"
title: "AIエージェントに権限を与えすぎると何が起きる？Excessive Agencyを初心者向けに解説"
url: "https://zenn.dev/mapellion/articles/ae84ee4d8005d5"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

はじめに
「メールを整理しておいて」「このリポジトリのバグを調べて直して」
AIエージェントにこんなお願いをする日常が、すでに始まっています。GitHub CopilotやClaude Codeなど、自律的に動くAIエージェントは急速に普及しています。
でも、こんなことを考えたことはありますか？

「エージェントに任せっぱなしにして、想定外の操作をされたら？」

先日プロンプトインジェクションを紹介しましたが、今回はそれと組み合わさったときに特に危険になる脆弱性 「Excessive Agency（過剰な自律行動）」 を解説します。
著者についてはこちら！
https://zenn....
