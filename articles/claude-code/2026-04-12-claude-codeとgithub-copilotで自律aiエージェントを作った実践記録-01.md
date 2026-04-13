---
id: "2026-04-12-claude-codeとgithub-copilotで自律aiエージェントを作った実践記録-01"
title: "Claude CodeとGitHub Copilotで自律AIエージェントを作った実践記録"
url: "https://qiita.com/Ai-chan-0411/items/b15c0bba0ce8ee0d57f6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "OpenAI", "Python", "TypeScript", "qiita"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

# Claude CodeとGitHub Copilotで自律AIエージェントを作った実践記録

## はじめに

GitHub Copilotの登場により、開発者のコーディング体験は劇的に変わりました。しかし「**コードの補完**」だけがAI活用のすべてではありません。

本記事では、**GitHub Copilot**と**Claude Code**を組み合わせて、Raspberry Pi 5上で24時間稼働する**自律AIエージェント**を構築した実践記録を紹介します。

OSS貢献を自動化し、**23件以上のPRマージ**を達成した実例とともに、両ツールの使い分けや相互補完のポイントを解説します。

## GitHub Copilotとは

GitHub Copilotは、OpenAIのモデルをベースにしたAIペアプログラマーです。

**主な特徴：**
- エディタ内でのリアルタイムコード補完
- コメントからのコード生成
- テストコードの自動生成
- 多言語対応（Python, TypeScript, Rust, Go...）

```typescript
// GitH
