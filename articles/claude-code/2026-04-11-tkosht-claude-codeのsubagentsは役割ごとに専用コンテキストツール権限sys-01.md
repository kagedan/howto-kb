---
id: "2026-04-11-tkosht-claude-codeのsubagentsは役割ごとに専用コンテキストツール権限sys-01"
title: "@tkosht: Claude Codeのsubagentsは、役割ごとに専用コンテキスト・ツール権限・system promptを分離で"
url: "https://x.com/tkosht/status/2043087251178164530"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-x"
---

Claude Codeのsubagentsは、役割ごとに専用コンテキスト・ツール権限・system promptを分離できるのが本質。ExploreはHaikuで探索専用、custom subagentはmodel・tools・hooks・memoryまで個別設定できる。

長い調査やテスト出力を本線から切り離しつつ、結果だけ戻せるので、文脈汚染と権限過多を同時に抑えやすい。なおsubagentは別のsubagentを起動できない。
https://t.co/ksAgXUqN0f
