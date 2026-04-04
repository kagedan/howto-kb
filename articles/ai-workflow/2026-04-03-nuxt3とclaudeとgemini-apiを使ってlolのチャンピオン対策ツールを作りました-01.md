---
id: "2026-04-03-nuxt3とclaudeとgemini-apiを使ってlolのチャンピオン対策ツールを作りました-01"
title: "Nuxt3とClaudeとGemini APIを使ってLoLのチャンピオン対策ツールを作りました"
url: "https://zenn.dev/otuy/articles/2d27b6d3f710de"
source: "zenn"
category: "ai-workflow"
tags: ["API", "Gemini", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

実際のツールはこちら！
爆速マッチアップ攻略くん



 はじめに
普段はLeague of Legends（LoL）というゲームをプレイしているエンジニアです。
今回は、Nuxt 3、Supabase、そしてGemini APIを活用して、LoLのマッチアップ（対面）攻略情報をロード画面の間にサクッと確認できるツール「爆速マッチアップ攻略くん（※仮名）」を開発しました。
本記事では、なぜこのツールを作ったのか、そして「APIのコスト」と「パフォーマンス」の壁をどう乗り越えたのかというアーキテクチャの話を書きたいと思います。

 1. なぜ作ろうと思ったのか？
LoLプレイヤーなら共感し...
