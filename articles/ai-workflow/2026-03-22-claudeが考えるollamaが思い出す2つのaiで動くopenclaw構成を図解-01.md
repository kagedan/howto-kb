---
id: "2026-03-22-claudeが考えるollamaが思い出す2つのaiで動くopenclaw構成を図解-01"
title: "Claudeが「考える」。Ollamaが「思い出す」。2つのAIで動くOpenClaw構成を図解"
url: "https://zenn.dev/kobarutosato/articles/b305465f8dd4e0"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

「設定は通った。でも何が動いてるかわからない…」

OpenClawをセットアップしたあなたへ。
Slackで返事は返ってくる。Claude APIも動いてる。でも 裏側で何が起きてるか 知らないと、エラーが出た瞬間に詰む。

メモリが拾われない
2回目以降レスポンスが返らない
Ollamaが勝手に落ちる

こんなトラブルに遭遇したとき、アーキテクチャを知ってるか知ってないか で対応時間が5倍変わります。
このガイドは、OpenClawの内部構造を完全図解 します。読み終わったとき、あなたは：
✅ なぜ2つのAIが必要か理解できる
✅ 5つのコンポーネントの役割が把握できる
✅ デー...
