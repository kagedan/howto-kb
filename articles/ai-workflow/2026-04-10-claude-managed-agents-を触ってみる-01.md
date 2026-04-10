---
id: "2026-04-10-claude-managed-agents-を触ってみる-01"
title: "Claude Managed Agents を触ってみる"
url: "https://qiita.com/ny7760/items/07af9d3facaf4af3d9f2"
source: "qiita"
category: "ai-workflow"
tags: ["API", "AI-agent", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

Anthropic が [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/quickstart) のパブリックβ版を公開しました。
ざっくり言うと、エージェントのマネージドな実行環境を提供するサービスです。

コンソールからも数クリックで試せたので、試した記録を共有します。

## 前提

- Claude API でクレジットは購入済み
 ※ Managed Agents はPro/Maxプランには含まれません。従量課金のみです。

## 手順

### エージェントの作成

- [Claude Console](https://platform.claude.com/) にアクセスすると Managed Agents のメニューが登場しています。Quickstart を選択すると、エージェントのテンプレートが選択できます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/
