---
id: "2026-04-17-claude-api-の請求書を見て焦った話prompt-caching-で月額を-6-割削減-01"
title: "Claude API の請求書を見て焦った話：Prompt Caching で月額を 6 割削減"
url: "https://zenn.dev/jixiaopan/articles/claude-prompt-caching-cost"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "API", "zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

TL;DR

静的な system prompt に cache_control: { type: "ephemeral" } を 1 行足すだけで大きなコスト削減が可能
100 クエリ/日のケースで $28/月 → $12/月（約 60% 削減）、キャッシュ対象部分だけ見れば 90% 減
落とし穴は「TTL 5 分」と「cache_control の配置順序」




 結論
Claude API の月額コストを見直したとき、Prompt Caching を正しく組み込むだけで全体コストが 6 割近く下がったのが一番の発見でした。
工業向け AI アシスタント（エラーコード手册 + ...
