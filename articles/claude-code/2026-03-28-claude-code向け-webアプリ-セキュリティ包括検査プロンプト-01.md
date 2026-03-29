---
id: "2026-03-28-claude-code向け-webアプリ-セキュリティ包括検査プロンプト-01"
title: "Claude Code向け Webアプリ セキュリティ包括検査プロンプト"
url: "https://zenn.dev/karou2rikon/articles/b05470d8ae6595"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

はじめに
Webアプリ診断用AIプロンプトを公開するにあたり、内容を整理しました。
本当はもっと単純化して、誰でもすぐ使える形にしたかったのですが、セキュリティ用途という性質上、権限確認や誤用防止の説明がどうしても長くなりました。
少し使い方は難しめですが、その分、安全側に倒れるよう整理しています。
一番のユースケースはClaude Code上でとりあえずWebアプリケーションを検査する、というのがよいと考えています。


 README

 ⚠️ 重要な注意事項（必ずお読みください）

 自分が管理するサイトにのみ使用してください
このプロンプトは 自分自身が所有・管理するWebサ...
