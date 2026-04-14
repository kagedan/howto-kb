---
id: "2026-04-14-claude-code-v21100でトークン消費が40増えたcache-creation膨張の原因-01"
title: "Claude Code v2.1.100でトークン消費が40%増えた——cache_creation膨張の原因と削減方法"
url: "https://qiita.com/yurukusa/items/c0acc6da4cb1c90fa431"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "API", "qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

Claude Code v2.1.100以降、同じCLAUDE.mdを使っているのにトークン消費が約40%増えている。

これは体感ではなく計測された事実だ。GitHub Issue [#46917](https://github.com/anthropics/claude-code/issues/46917)では、v2.1.98で49,726トークンだった`cache_creation_input_tokens`が、v2.1.100では69,922トークンに膨張していると報告されている。投稿から数日で92リアクションがついた。

## 何が起きているか

`/cost`コマンドで確認できる`cache_creation_input_tokens`が、v2.1.100以降で約20,000トークン増えている。ペイロードは同一。CLAUDE.mdも同じ。サーバー側で何かが変わった。

影響:
- **コスト**: cache_creationはcache_readの約4倍のコスト（Anthropic API価格表準拠）
- **コンテキスト**: 20Kトークン分だけコンテキストウィンドウ
