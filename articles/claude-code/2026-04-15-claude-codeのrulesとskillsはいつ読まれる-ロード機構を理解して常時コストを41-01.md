---
id: "2026-04-15-claude-codeのrulesとskillsはいつ読まれる-ロード機構を理解して常時コストを41-01"
title: "Claude Codeのrulesとskillsはいつ読まれる？ — ロード機構を理解して常時コストを41%削減した話"
url: "https://zenn.dev/yottayoshida/articles/claude-code-context-cost-structure"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

この記事は2026年4月時点の code.claude.com 公式ドキュメント に基づいています。


 この記事で伝えたいこと
Claude Codeの設定ファイルには3つのロード層がある。全部が毎回読まれているわけではない。


Always: CLAUDE.md と paths:なしの rules → セッション開始時に読み込まれ、以降ずっとコンテキストに残る

Conditional: paths:付きの rules/skills → マッチするファイルを触った時だけ

On-demand: skills の本文 → 使う時だけ（通常はname と descriptionだけ...
