---
id: "2026-04-05-claude-codeにpmとctoを仕込んだらプロジェクト管理が変わった-01"
title: "Claude Codeに「PM」と「CTO」を仕込んだら、プロジェクト管理が変わった"
url: "https://qiita.com/kiyotaman/items/4a9523badbc08af35a93"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-05"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

## TL;DR

Claude Codeのカスタムスラッシュコマンドで `/pm`（プロダクトマネージャー）と `/cto`（技術責任者）を定義した。`.md` ファイル2つ置くだけ。

- `/pm` — マイルストーンの一貫性、リリース順序、イシュー優先度を分析
- `/cto` — 技術的負債、アーキテクチャリスク、ドキュメント健全性、バグ状況を診断

分析はAI、判断は人間。この分離が肝。

## 背景：1人開発でもプロジェクト管理は崩れる

OSSや個人開発でありがちな状態：

```
v0.8.0 "Integration, Connectivity & Docs"
├── #18  context sync export/import
├── #19  webhook notifications
├── #46  resource MCP tools
├── #47  resource UI
├── #104 sleep admin UI        ← これ Integration か？
├── #135 docs overhaul         ← これも？
└
