---
id: "2026-04-09-aiエージェントの自律性は安全な箱が決めるclaude-managed-agentsが埋めるランタイ-01"
title: "AIエージェントの自律性は「安全な箱」が決める──Claude Managed Agentsが埋めるランタイム層"
url: "https://zenn.dev/slate_infra/articles/2f4831bf38b740"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "OpenAI", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

はじめに：自律性とセキュリティのジレンマ
第1回では、OpenAIとAnthropicの公開事例をもとにharness engineering──モデルの外側にある環境設計が生産性を決める──という概念を整理した。その中で「permissionsを緩める代わりに環境側で爆発半径を制限する設計」が先進事例に共通していると書いた。第2回では、レビューの自動化と人間判断の境界線を3層モデルで再設計した。
どちらの記事でも繰り返し浮上したのは、「エージェントの自律性を上げるほどセキュリティリスクが増大する」というジレンマだ。Boris Chernyは--dangerously-skip-pe...
