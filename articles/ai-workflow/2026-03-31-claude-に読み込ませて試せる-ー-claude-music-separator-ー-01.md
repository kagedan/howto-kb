---
id: "2026-03-31-claude-に読み込ませて試せる-ー-claude-music-separator-ー-01"
title: "Claude に読み込ませて試せる ー Claude music separator ー"
url: "https://zenn.dev/morc_b13/articles/4a9d3d47209c09"
source: "zenn"
category: "ai-workflow"
tags: ["Python", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

B13で音楽信号を分離する ー Claude music separator　ー

 Claude に読み込ませて試せます
B13phaseを使った音楽信号分離器です。
この記事の Python コード（面倒なら記事全体でもよい）を Claude に読み込ませ、手持ちの楽曲をアップロードすると、楽器ごとに分離したWAVデータが生成できます。

 楽器とボーカルの分離ではなく、音楽から、楽器を引き算していくイメージです。

 最後に残ったrest.midには、主に、ボーカルや打楽器などの信号が残ります。
現状は、最小限の学習しかしてないので、楽器の分離も不充分です。
このClaude ...
