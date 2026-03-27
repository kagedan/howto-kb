---
id: "2026-03-26-claude障害時でも止まらないtelegramボットgeminiollamaへのllmフォールバッ-01"
title: "Claude障害時でも止まらないTelegramボット：Gemini・OllamaへのLLMフォールバック実装"
url: "https://zenn.dev/acropapa330/articles/llm_fallback_bot"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "Gemini", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

Claude障害時でも止まらないTelegramボット：Gemini・OllamaへのLLMフォールバック実装
以前の記事でWSL上にClaude CLIを使ったTelegramボットを構築しました。ところが2026年3月25日、Anthropic側でPartial Outageが発生し、ボットが完全に応答不能になりました。
この反省から、Claude障害時でも動き続ける冗長構成を実装しました。


 構成
Claude CLI（メイン）
    ↓ 障害・タイムアウト時
Gemini API（フォールバック1）
    ↓ これも失敗時
Ollama ローカルLLM（フォールバック...
