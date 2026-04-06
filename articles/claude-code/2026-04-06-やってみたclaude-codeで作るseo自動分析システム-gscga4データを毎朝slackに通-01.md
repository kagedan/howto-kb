---
id: "2026-04-06-やってみたclaude-codeで作るseo自動分析システム-gscga4データを毎朝slackに通-01"
title: "【やってみた】Claude Codeで作るSEO自動分析システム - GSC×GA4データを毎朝Slackに通知"
url: "https://qiita.com/kenji_harada/items/ce01ef8185b48da92013"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-06"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

この記事は自社ブログ([nands.tech](https://nands.tech/posts/claude-code-gsc-ga4-ai-seo-autonomous-analysis-406853))の要約版です

## はじめに

毎朝GSCを開いてパフォーマンスをチェックし、GA4で記事の直帰率を確認する...この作業、自分も毎週やっていましたが、100記事を超えるとさすがに限界でした。

そこでClaude Codeを使って、GSCとGA4のデータを自動取得し、全記事をAIがスコアリングして改善すべき記事をSlackに通知してくれるシステムを作ってみました。

結果：**月間4,000表示でCTR 0.02%の記事**をAIが発見し、手動では見落としていた致命的なボトルネックを検出できました。

## システム構成

```mermaid
graph TB
    A[GitHub Actions<br/>毎日6:00実行] --> B[GSC APIで検索データ取得]
    A --> C[GA4 APIでユーザー行動取得]
    B --> D[Supabase<
