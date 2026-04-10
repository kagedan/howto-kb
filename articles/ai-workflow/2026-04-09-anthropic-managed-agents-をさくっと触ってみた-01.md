---
id: "2026-04-09-anthropic-managed-agents-をさくっと触ってみた-01"
title: "Anthropic Managed Agents をさくっと触ってみた"
url: "https://zenn.dev/sprix_it/articles/3211f5068cec29"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

きっかけ
Anthropic 公式エンジニアリングブログに Scaling Managed Agents: Decoupling the brain from the hands という記事が出ているのを見て興味を持ちました。「頭脳（モデル）」「手（サンドボックス）」「記録（セッションログ）」を分離する、というアーキテクチャの説明が面白かったので、本当にそういう作りになっているか自分の手元で叩いて確かめてみよう、というのがこの記事の出発点です。

 これは何の話？
Anthropic が 2026 年 4 月に Managed Agents（/v1/agents, /v1/sessi...
