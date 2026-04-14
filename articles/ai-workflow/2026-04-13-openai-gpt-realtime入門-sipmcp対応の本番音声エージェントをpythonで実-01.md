---
id: "2026-04-13-openai-gpt-realtime入門-sipmcp対応の本番音声エージェントをpythonで実-01"
title: "OpenAI gpt-realtime入門 — SIP・MCP対応の本番音声エージェントをPythonで実装する"
url: "https://zenn.dev/kai_kou/articles/191-gpt-realtime-sip-mcp-production-guide"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

はじめに
OpenAIが2026年4月、Realtime APIをGeneral Availability（GA）に昇格させ、新モデル gpt-realtime を正式リリースしました。
従来のプレビュー版と比べて大きな変化点が3つあります。


SIP電話対応 — Twilioなどを経由して公衆電話網に直接接続できる

リモートMCPサーバー対応 — ツールをURL一本で接続できる

非同期関数呼び出し — 長時間処理中も会話を途切れなく続けられる

!
移行期限あり: プレビュー版（gpt-4o-realtime-preview系）は 2026年4月30日 に非推奨化され、200...
