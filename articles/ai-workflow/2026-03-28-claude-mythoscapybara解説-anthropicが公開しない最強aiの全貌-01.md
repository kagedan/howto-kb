---
id: "2026-03-28-claude-mythoscapybara解説-anthropicが公開しない最強aiの全貌-01"
title: "Claude Mythos（Capybara）解説 — Anthropicが公開しない最強AIの全貌"
url: "https://qiita.com/kai_kou/items/778e1cee2a872e4a75c9"
source: "qiita"
category: "ai-workflow"
tags: ["LLM", "qiita"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

## はじめに

2026年3月26〜27日、AI業界に衝撃が走りました。AnthropicのCMS（コンテンツ管理システム）の設定ミスにより、約3,000件の内部ドキュメントが一時的に公開状態になるという情報漏洩事件が発生。その中に、同社がひそかに開発中の未発表モデルの存在を示す草稿ブログ記事が2バージョン含まれており、「**Capybara**」（新Tier名）と「**Claude Mythos**」（そのTier内のモデル名）という2つの名称が明らかになりました。

### この記事で整理すること

- Claude Mythosとはどのようなモデルか
- 何がリークされ、何が判明したのか
- なぜAnthropicは公開しないのか
- エンジニアが知っておくべき示唆

### 対象読者

- Anthropic / Claudeの最新動向を追うエンジニア
- LLMのサイバーセキュリティリスクに関心のある方
- AI安全性・リリース戦略に興味のある方

---

## TL;DR

- Anthropicが内部ドキュメントを誤公開、未発表モデル「Claude Mythos（C
