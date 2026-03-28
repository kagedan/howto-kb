---
id: "2026-03-26-コドモンのメール通知をclaude-apiで自動解析してgoogleカレンダーに登録した-01"
title: "コドモンのメール通知をClaude APIで自動解析してGoogleカレンダーに登録した"
url: "https://zenn.dev/nori_sasa_dev/articles/codomon-gas-claude-calendar"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

TL;DR

保育園から届くコドモンのメールを Google Apps Script + Claude API で自動解析
休園・早帰り・給食なし・行事などをGoogleカレンダーに自動登録
サーバー不要・GASは無料枠内で動く（Claude APIの利用料は別途発生）



 背景：子どもの予定が複数アプリに分散していた
子育て中、こんな状況になっていました。

保育園の連絡 → コドモンのアプリ通知 + メール
小学校の連絡 → スクリレのアプリ通知
習い事の連絡 → BANDのグループ投稿

それぞれ別のアプリで通知が来るため、「今日、給食あったっけ？」「来週の早帰りはいつだっ...
