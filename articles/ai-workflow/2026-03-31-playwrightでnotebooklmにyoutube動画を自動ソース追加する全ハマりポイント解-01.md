---
id: "2026-03-31-playwrightでnotebooklmにyoutube動画を自動ソース追加する全ハマりポイント解-01"
title: "PlaywrightでNotebookLMにYouTube動画を自動ソース追加する【全ハマりポイント解説】"
url: "https://zenn.dev/ilumination1879/articles/17c16d55a4f4c7"
source: "zenn"
category: "ai-workflow"
tags: ["Python", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

PlaywrightでNotebookLMにYouTube動画を自動ソース追加する

 はじめに
あるYouTuberの動画90本を、NotebookLMに古い順に連番付きでソース追加したい——そう思ったことはありませんか？
手作業でやると気が遠くなる作業です。そこでPlaywright（Pythonブラウザ自動化ライブラリ）を使って全自動化に挑戦しました。
しかし、NotebookLMはAngular製のSPAで独特のDOM構造を持ち、Googleログインはセキュリティ上の理由でPlaywrightのChromiumをブロックします。数多くのハマりポイントを乗り越えた実装記録を共有...
