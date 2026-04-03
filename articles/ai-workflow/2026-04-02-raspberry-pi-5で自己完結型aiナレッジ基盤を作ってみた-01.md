---
id: "2026-04-02-raspberry-pi-5で自己完結型aiナレッジ基盤を作ってみた-01"
title: "Raspberry Pi 5で自己完結型AIナレッジ基盤を作ってみた"
url: "https://zenn.dev/nanora/articles/20260330-2d3be5f2"
source: "zenn"
category: "ai-workflow"
tags: ["API", "GPT", "zenn"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

TL;DR

Raspberry Pi 5 (16GB) で完全オンプレのRAGナレッジ基盤を構築
構成: FastAPI + Ollama (Gemma3 7B) + ChromaDB + Redis（Docker 4コンテナ）
月額コスト: 電気代のみ（約100円/月）
RAG応答速度: 約8秒（量子化で3〜4秒）
クラウドAPI代を減らしたい・データを外に出したくないエンジニア向け




 クラウドAI、高くない？
「GPT-4oのAPI代、今月いくらだっけ…」って明細見て冷や汗かいたことない？
なのらもそうだった。毎月じわじわ増えていくAPIコスト、しかも自分のドキュメントや...
