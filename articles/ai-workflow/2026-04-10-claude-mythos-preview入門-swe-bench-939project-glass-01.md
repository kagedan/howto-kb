---
id: "2026-04-10-claude-mythos-preview入門-swe-bench-939project-glass-01"
title: "Claude Mythos Preview入門 — SWE-bench 93.9%・Project Glasswingの全貌"
url: "https://qiita.com/kai_kou/items/01ccaf201882ecec2c68"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

<!-- IMAGE_SLOT: hero — Claude Mythos Previewのコンセプト図。AIがゼロデイ脆弱性を自律発見し、大手テクノロジー企業が参加するProject Glasswingの防衛的サイバーセキュリティ連合を表現する。 -->

## はじめに

2026年4月7日、Anthropicは史上最も強力なモデル「**Claude Mythos Preview**」を限定公開しました。SWE-bench Verifiedで93.9%を達成し、全主要OSと全主要ブラウザでゼロデイ脆弱性を数千件自律発見したこのモデルは、通常のAPI公開なしに**防衛的サイバーセキュリティ専用**として提供されています。

Amazon、Apple、Microsoft、Googleなど12社以上が参加する「**Project Glasswing**」という連合の中核を担うClaudeの新モデルについて、公開情報をもとに詳しく解説します。

### この記事で学べること

- Claude Mythos Previewのベンチマーク性能と他モデルとの比較
- ゼロデイ脆弱性自律発見能
