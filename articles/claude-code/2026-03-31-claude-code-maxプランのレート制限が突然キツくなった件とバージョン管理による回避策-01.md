---
id: "2026-03-31-claude-code-maxプランのレート制限が突然キツくなった件とバージョン管理による回避策-01"
title: "Claude Code Maxプランのレート制限が突然キツくなった件と、バージョン管理による回避策"
url: "https://zenn.dev/ryosuke_ando/articles/a1f673d0905a6d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

何が起きているのか
2026年3月23日頃から、Claude Code Maxプラン（5x / 20x）のセッション制限が異常に早く消費される問題が発生しています。以前は5時間持ったセッションが1〜2時間で枯渇し、GitHub Issue #38335 には229件超のコメントが集まっています。
主な症状：

同じ作業量なのにセッションが1〜2時間で枯渇
1回のプロンプトで使用量が21%→100%に跳ね上がる
使っていないのに使用量が増える「ゴーストトークン」現象


 原因（推定）
3つの要因が重なっていると思われます。


3/28で2倍キャンペーンが終了 — 平日オフピーク・週...
