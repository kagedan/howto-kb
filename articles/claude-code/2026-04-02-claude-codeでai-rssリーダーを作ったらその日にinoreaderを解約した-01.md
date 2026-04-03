---
id: "2026-04-02-claude-codeでai-rssリーダーを作ったらその日にinoreaderを解約した-01"
title: "Claude CodeでAI RSSリーダーを作ったら、その日にInoreaderを解約した"
url: "https://zenn.dev/caphtech/articles/feed-curator-ai-rss-with-claude-code"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

TL;DR
Claude Code自身をAIキュレーターとして使うRSSツール「Feed Curator」を作った。APIキー不要。トピックを入力するだけでRSSフィードを検索・おすすめしてくれて、既読・スキップの履歴から嗜好を自動学習し、毎朝パーソナライズされた技術ブリーフィングを生成する。
https://github.com/rizumita/feed-curator
npx feed-curator serve
!
技術的な話題: なぜClaude Codeサブプロセスか / トークン消費の内訳 / 3段階パーソナライズ / head+tail戦略・スコア×鮮度ブレンド / ...
