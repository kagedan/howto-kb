---
id: "2026-04-09-claude-agent-sdk入門claude-codeをライブラリとして使う実践ガイド-01"
title: "Claude Agent SDK入門：Claude Codeを「ライブラリ」として使う実践ガイド"
url: "https://qiita.com/relu_whale/items/bac9e02d3c4ddd3be84f"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "Python", "TypeScript", "qiita"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

## TL;DR

- Anthropic が Claude Code SDK を **Claude Agent SDK** に改名した（2025年末）
- `query()` 1行で Claude Code と同じエージェントループを Python/TypeScript から呼び出せる
- セッション継続・サブエージェント並列実行・カスタムツール追加が標準搭載
- コードレビューをサブエージェント3本で並列化したら所要時間が **4分30秒 → 47秒** に縮まった

---

## Claude Code SDK が「Agent SDK」に変わった理由

2025年末、Anthropic は静かに Claude Code SDK を **Claude Agent SDK** に改名した。[マイグレーションガイド](https://platform.claude.com/docs/en/agent-sdk/migration-guide)には一行こう書かれている。

> "We realized the same agent loop powering our coding to
