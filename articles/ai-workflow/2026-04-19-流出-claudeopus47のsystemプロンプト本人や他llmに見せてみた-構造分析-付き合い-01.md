---
id: "2026-04-19-流出-claudeopus47のsystemプロンプト本人や他llmに見せてみた-構造分析-付き合い-01"
title: "流出? ClaudeOpus4.7のSystemプロンプト、本人や他LLMに見せてみた — 構造分析 + 付き合い方"
url: "https://zenn.dev/orangewk/articles/claude-system-prompt-structure-guide"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "zenn"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

TL;DR

CL4R1T4S に投稿された「Claude Opus 4.7 のシステムプロンプト」を、4.6 / 裸の 4.7 / Agent SDK 4.7 / Codex / Qwen の 6 モデル環境で対照実験した
構造・方針レベル（階層・検索ファースト・著作権ルール・フォーマット規定）は本物っぽい

一方、モデル名・日付・実装トリビア等の逐語レベルは捏造混入の可能性が高い

結論: おそらく実行時プロンプトの verbatim ではなく、Anthropic の内部ドキュメントの再構成

本稿はその構造解剖と日々の使い方 Tips 12 個。対話ログ全文は別記事



出典...
