---
id: "2026-04-15-claude-codeが落ちた時の保険ローカルllmqwen35で完全代替する環境を構築した話-01"
title: "Claude Codeが落ちた時の保険：ローカルLLM(Qwen3.5)で完全代替する環境を構築した話"
url: "https://qiita.com/ryun818/items/a2f7fa6d76d2d48b121a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "LLM", "qiita"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Codeが障害で使えない時のフォールバックとして、ローカルLLMで置き換える仕組みを構築しました。

ネット上の情報は断片的で、実際にやってみると**既知のバグや設定の罠が大量**にあり、動くまでに半日溶かしました。同じ道を辿る人のために、ハマりポイントと最終的な動作する構成をまとめます。

**結論**: llama.cpp + Qwen3.5-35B-A3B (Unsloth GGUF) + 適切な環境変数で、Claude Code CLIの対話モードがローカルLLMで動きます。

## 環境

- Apple MacBook Pro M2 Max (64GB統合メモリ、38GPUコア)
- Claude Code v2.1.104
- llama.cpp (最新)
- zsh

## 最終的な性能

| 項目 | Ollama (最初の試み) | llama.cpp (最終構成) |
|------|---------------------|---------------------|
| 初回応答 | 2分40秒〜8分24秒 | **1分30
