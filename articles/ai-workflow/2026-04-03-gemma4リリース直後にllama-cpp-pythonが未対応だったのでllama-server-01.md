---
id: "2026-04-03-gemma4リリース直後にllama-cpp-pythonが未対応だったのでllama-server-01"
title: "Gemma4リリース直後にllama-cpp-pythonが未対応だったので、llama-server.exeを直叩きした話"
url: "https://zenn.dev/ena_dri/articles/340edb0d490bfa"
source: "zenn"
category: "ai-workflow"
tags: ["Gemini", "Python", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

はじめに
Gemma 4がリリースされた直後、「ローカルで動かしてみたい」と思って llama-cpp-python を確認したら未対応だった。そらそう。
待つのもアリだが、せっかくなのでllama.cpp本家のバイナリ（llama-server.exe）を直接叩く設計で遊んでみることにした。作ったのは「日本語の情景描写をStable Diffusion用の英語タグに変換するツール」。テキストだけでなく、画像を渡してタグを抽出させることもできる。
なお筆者は設計職（建築系）でコードは書けないため、GeminiとClaudeと一緒に作っている。
なんならこの記事もClaudeに書いても...
