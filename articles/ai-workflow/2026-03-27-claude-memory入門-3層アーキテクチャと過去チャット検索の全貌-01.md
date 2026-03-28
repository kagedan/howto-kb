---
id: "2026-03-27-claude-memory入門-3層アーキテクチャと過去チャット検索の全貌-01"
title: "Claude Memory入門 — 3層アーキテクチャと過去チャット検索の全貌"
url: "https://qiita.com/kai_kou/items/c5c3d7a04fec298a9e2c"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Gemini", "GPT", "qiita"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

## はじめに

2026年3月、AnthropicはClaude Memoryを**全プラン（Free含む）へ展開**しました。これまでは有料プラン限定だったメモリ機能が、無料ユーザーも含めた全ユーザーに開放されています。

Claudeのメモリシステムは単なる「会話履歴の保存」ではなく、目的の異なる**3層のアーキテクチャ**で構成されています。本記事では、各レイヤーの仕組みと実装方法を公式ドキュメントをもとに解説します。

### この記事で学べること

- Claudeのメモリ3層アーキテクチャの全貌
- Chat Memory（メモリ合成）の動作原理
- 過去チャット検索（RAGベースのツールコール）の使い方
- API Memory Toolの実装方法
- エンタープライズ環境での管理・制御方法
- ChatGPT / Gemini / Grok からのメモリインポート

### 対象読者

- AnthropicのAPIやClaudeを開発に使っているエンジニア
- AIエージェントに長期記憶を持たせたい開発者
- エンタープライズでClaude利用ポリシーを管理してい
