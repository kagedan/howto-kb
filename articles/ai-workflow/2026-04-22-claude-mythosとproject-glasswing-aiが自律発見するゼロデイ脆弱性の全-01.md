---
id: "2026-04-22-claude-mythosとproject-glasswing-aiが自律発見するゼロデイ脆弱性の全-01"
title: "Claude MythosとProject Glasswing — AIが自律発見するゼロデイ脆弱性の全容"
url: "https://qiita.com/kai_kou/items/aff3ab094d2bea3cc7f0"
source: "qiita"
category: "ai-workflow"
tags: ["API", "LLM", "qiita"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

## はじめに

2026年4月7日、Anthropicは一般公開しないことを前提とした新しいフロンティアモデル **Claude Mythos Preview** と、それを活用したサイバーセキュリティ連合 **Project Glasswing** を発表しました。

このモデルは「公開できないほど強力」とされ、すべての主要OSとWebブラウザに存在するゼロデイ脆弱性を自律的に数千件発見するという前例のない能力を持ちます。本記事では、Claude Mythos Previewの技術的な仕組み、Project Glasswingの概要、そして開発者やセキュリティエンジニアが知るべき影響について、公開情報をもとに解説します。

### この記事で学べること

- Claude Mythos Previewが達成したゼロデイ脆弱性発見の実績
- 自律的なエクスプロイト構築の技術的な仕組み
- Project Glasswingの参加企業・資金・アクセス方法
- APIアクセスの料金と取得方法

### 対象読者

- セキュリティエンジニア・ペネトレーションテスター
- AI/LLMの
