---
id: "2026-04-10-claude-advisor-tool入門-sonnetとopusを組み合わせてコスト削減と品質向上-01"
title: "Claude Advisor Tool入門 — SonnetとOpusを組み合わせてコスト削減と品質向上を両立する"
url: "https://qiita.com/kai_kou/items/e7347356fee8084cfdaf"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

<!-- IMAGE_SLOT: hero — Claude Advisor Tool architecture showing Sonnet executor consulting Opus advisor, clean flat design, blue and purple gradient, white background -->

## はじめに

2026年4月9日、AnthropicはClaude APIに**Advisor Tool**（`advisor_20260301`）をパブリックベータとして追加しました。

このツールは、より高速・低コストな**Executorモデル**（SonnetやHaiku）と、より高知能な**Advisorモデル**（Opus 4.6）を1つのAPIリクエスト内で組み合わせる仕組みです。Executorがタスクを自律的に実行しながら、必要な場面だけOpusに戦略的なガイダンスを求めます。

**この記事で学べること：**
- Advisor Toolの仕組みとユースケース
- Python・TypeScriptでの実装方法
- SW
