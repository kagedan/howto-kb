---
id: "2026-03-30-weztermでclaude-codeの実行状態をまとめて監視する仕組みを作った-01"
title: "WezTermでClaude Codeの実行状態をまとめて監視する仕組みを作った"
url: "https://zenn.dev/soramarjr/articles/7d9ea81fe643dd"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

一人前食堂のYoutubeが更新されなくなって早1年ですね。
fujitani soraです。
WezTermでもAgentの実行/待機 の状態をまとめて確認できる仕組みを実装したので、
その概要と技術的詳細についてまとめました 👀

 Agentの実行状態を監視する
モチベーションになったのはcmuxです。
Agentの実行状態をまとめて監視できる仕組みは便利そうでしたが、WezTermに引き篭りたかったので今回の実装を考えました。
体験的にはそれを売りに作られているcmuxなどの方がリッチかもしれませんが、自分にとっては自作の仕組みでも十分にAgentの実行状態監視を効率化できている...
