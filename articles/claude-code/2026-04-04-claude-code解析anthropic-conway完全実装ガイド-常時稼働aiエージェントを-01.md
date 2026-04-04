---
id: "2026-04-04-claude-code解析anthropic-conway完全実装ガイド-常時稼働aiエージェントを-01"
title: "【Claude Code解析】Anthropic Conway完全実装ガイド - 常時稼働AIエージェントを作ってみた"
url: "https://qiita.com/kenji_harada/items/76e1ccd0a1cd14ea1a7f"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "TypeScript", "qiita"]
date_published: "2026-04-04"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

この記事は自社ブログ([nands.tech](https://nands.tech/posts/anthropic-conway-persistent-agent-guide))の要約版です

## はじめに🚀 リーク情報から判明したConwayの全貌

2026年3月31日、Claude Codeのnpmパッケージから59.8MBのソースマップがリークし、Anthropicの隠しプロジェクト「**Conway**」が発覚しました。

従来のAIは「呼び出し待ち」でしたが、Conwayは**24時間365日稼働し続ける自律エージェント**です。メール受信、GitHub更新、Slack通知など外部イベントに自動反応し、人間が寝ている間も作業を継続します。

僕自身、同様のシステムを手作りで構築・運用しているので、実装者の視点からConwayの仕組みを解説し、実際に動かせる常時稼働エージェントを作ってみます。

## Conway の3つのコアエリア

リーク情報から判明したConwayの構成：

### 1. Search エリア
```typescript
// 実験的なホットキー機
