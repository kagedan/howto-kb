---
id: "2026-03-16-分析パイプライン構築5antigravity運用の改善deny-list-と-workflow-と-01"
title: "分析パイプライン構築（5）〜Antigravity運用の改善：Deny List と Workflow と rules"
url: "https://zenn.dev/pdata_analytics/articles/46d0a9abfad90c"
source: "zenn"
category: "antigravity"
tags: ["Gemini", "antigravity", "zenn"]
date_published: "2026-03-16"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

分析パイプライン構築（5）

 Antigravity運用の改善：Deny List と Workflow と rules
この連載では、実務でデータ分析基盤を立ち上げる中で、
「どのようにして分析パイプラインを構築してきたか」を、
実際の試行錯誤を交えて書いています。
筆者は、プロダクトのログを扱いながら、
分析・データ基盤の整備を行っている実務担当者です。
前回の記事では、Antigravityをデータ分析パイプライン開発に使う中で
AIエージェントの挙動を安定させるため、次の3層構造のルールを整理しました。
GEMINI.md
↓
AI_RULES.md
↓
AWS_GLUE_...
