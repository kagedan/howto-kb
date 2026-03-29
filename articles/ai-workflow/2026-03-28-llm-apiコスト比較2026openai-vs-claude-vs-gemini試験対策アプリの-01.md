---
id: "2026-03-28-llm-apiコスト比較2026openai-vs-claude-vs-gemini試験対策アプリの-01"
title: "LLM APIコスト比較2026：OpenAI vs Claude vs Gemini（試験対策アプリの視点から）"
url: "https://qiita.com/takkenai/items/a367ea202f2e036c9517"
source: "qiita"
category: "ai-workflow"
tags: ["API", "LLM", "OpenAI", "Gemini", "GPT", "qiita"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

# LLM APIコスト比較2026：OpenAI vs Claude vs Gemini（試験対策アプリの視点から）

個人開発で宅建（宅地建物取引士）試験対策アプリ [takkenai.jp](https://takkenai.jp) を運営しています。1250問以上の過去問にAI解説を付けており、毎日かなりの量のLLM API呼び出しが発生します。

そこで2026年時点での実運用データをもとに、主要3社のLLM APIを比較してみました。

## はじめに：なぜこの比較が必要だったか

宅建アプリのAI解説機能では「結論→根拠→覚え方」の3段階で解説を生成しています。1問あたり約700トークンの出力が発生し、月間リクエスト数が増えるにつれてAPIコストが無視できなくなりました。

## トークン単価比較（2026年3月時点）

| モデル | 入力 (USD/1M) | 出力 (USD/1M) |
|--------|--------------|--------------|
| GPT-4o | $2.50 | $10.00 |
| GPT-4o mini | $0.15
