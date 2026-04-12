---
id: "2026-04-11-ai開発でユーザーの判断軸が効いた1日-claude-copilot-と作るインフラの現実-01"
title: "AI開発でユーザーの判断軸が効いた1日 — Claude × Copilot と作るインフラの現実"
url: "https://zenn.dev/fixu/articles/day051-ai-human-collaboration"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

AI (Claude) と Copilot と一緒に 1 日開発作業をして、何度も自分が引き戻した場面を振り返る。
AI が全部やってくれるわけではないし、かといって AI は飾りでもない。ちょうど中間の、「人間の判断軸 × AI の実行速度 × 複数視点のレビュー」の三層構成で品質が決まる、というのが実感できた 1 日だった。

 この日やっていた作業の概要
この日は、AWS 上のマイクロサービス基盤を対象に、以下の作業を進めていた。


ECS Blue/Green デプロイの設計と Terraform 実装 — dev/stg/prod すべての環境に展開できる共通テンプレートの構...
