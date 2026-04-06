---
id: "2026-04-05-claude-codeのセッションログをaiに読ませたら引き継ぎより検証に使うようになった-01"
title: "Claude CodeのセッションログをAIに読ませたら、引き継ぎより検証に使うようになった"
url: "https://zenn.dev/ken992/articles/bddddd561ff630"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-04-05"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

はじめに
AIに自分の過去のセッションログを読ませています。セッションの引き継ぎ目的で始めましたが、運用するうちに用途が変わっていきました。AIが書いたIssueの背景を後から確認させる、作業パターンの漏れを検証させる。むしろこちらの方に価値を感じています。
この記事はその実践報告です。

 やっていること
セッションの会話ログはJSONLで自動保存されます。それを読み出すCLIツールを作り、CLAUDE.mdに書いておきます。
## セッションログ検索（推奨）

session search "keyword"
session list --since 2025-12-20
ses...
