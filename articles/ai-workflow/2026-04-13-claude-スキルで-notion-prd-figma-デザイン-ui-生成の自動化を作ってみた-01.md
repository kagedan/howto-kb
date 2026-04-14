---
id: "2026-04-13-claude-スキルで-notion-prd-figma-デザイン-ui-生成の自動化を作ってみた-01"
title: "Claude スキルで Notion PRD → Figma デザイン → UI 生成の自動化を作ってみた"
url: "https://zenn.dev/superstudio/articles/8a5822110fbeb7"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

はじめに
Notion の PRD を起点に、AI がデザインシステムのコンポーネントを使った React コードを自動生成するワークフローを作りました。この記事では、その設計と仕組みを紹介します。

 解決したかった課題
従来のフロントエンド実装フローには、3つの課題がありました。

 コンテキストの断絶
PRD → Figma → コードの間で情報が抜け落ちます。PRD に「ローディング状態を表示する」と書いてあっても、実装時にその要件を見落とすことがあり、Figma のコンポーネント名がデザインシステムの名前と一致しない時は手探りで対応表を確認する時間が発生します。
→ このワ...
