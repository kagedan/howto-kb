---
id: "2026-03-27-bedrock-claude-46-環境における-pre-fill-廃止と代替手段の整理-01"
title: "Bedrock (Claude 4.6) 環境における pre-fill 廃止と代替手段の整理"
url: "https://qiita.com/enumura1/items/d0f53e82ed6b59668b67"
source: "qiita"
category: "ai-workflow"
tags: ["Python", "qiita"]
date_published: "2026-03-27"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

# はじめに

Lambda（Python）から Bedrock 経由で Claude を呼んでいる構成で、モデルを Sonnet 4.5 → Sonnet 4.6 に差し替えたところ、今まで動いていたコードが 400 エラーで落ちました。

```text:モデルID
- 旧：jp.anthropic.claude-sonnet-4-5-20250929-v1:0
- 新：jp.anthropic.claude-sonnet-4-6
```

原因は pre-fill（アシスタントメッセージのプリフィル）の廃止です。
Claude 4.6 では、`messages` の末尾に `role: "assistant"` を置く書き方がエラーになります。

Anthropic の [マイグレーションガイド](https://platform.claude.com/docs/en/about-claude/models/migration-guide) に Breaking changes として記載されている内容です。

この記事では、変更の内容と対応策をまとめています。

# pre-f
