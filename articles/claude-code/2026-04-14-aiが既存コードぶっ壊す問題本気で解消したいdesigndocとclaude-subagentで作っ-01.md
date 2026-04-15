---
id: "2026-04-14-aiが既存コードぶっ壊す問題本気で解消したいdesigndocとclaude-subagentで作っ-01"
title: "「AIが既存コードぶっ壊す問題、本気で解消したい」——DesignDocとClaude Subagentで作った解決策"
url: "https://zenn.dev/mgdx_blog/articles/2ccfd55e2ac785"
source: "zenn"
category: "claude-code"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

「AIにコードを書かせているんだけど、ちょっと気を抜くとアーキテクチャ規約が崩れる…」「一定以上の規模感の開発になると手戻りが多い..」「既存機能がすでに豊富なので変更を加えると破壊してしまう..」そんな課題を感じたことはないでしょうか。
私たちのプロジェクトはDDD＋クリーンアーキテクチャで構成された20以上のGoマイクロサービスで動いています。既存機能が豊富に積み上がっており、新しい機能を加えるたびに既存コードへの影響を考慮しながら、各レイヤーの規約を守って実装しなければならない。通常のSpecDriven開発も軽微な修正であればよいのですが、変更範囲が大きい場合手戻りが発生すること...
