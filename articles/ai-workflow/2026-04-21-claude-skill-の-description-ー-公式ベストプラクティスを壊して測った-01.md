---
id: "2026-04-21-claude-skill-の-description-ー-公式ベストプラクティスを壊して測った-01"
title: "Claude Skill の description ー 公式ベストプラクティスを壊して測った"
url: "https://zenn.dev/shoki_sato/articles/c6a7c39b3b513c"
source: "zenn"
category: "ai-workflow"
tags: ["LLM", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

!

Anthropic 公式の Skill authoring best practices の「Writing effective descriptions」セクションにある 4 つの主張（三人称 / What+When / 具体性 / 曖昧さ回避）を、100 クエリ × 3 runs × 6 variants の binary LLM judge で検証した
インパクトは一律ではなく 具体性（C3） &gt;&gt;&gt; 曖昧さ回避（C4）≈ 一人称違反（C1-1st） &gt;&gt;&gt; 二人称違反（C1-2nd）≈ When 節削除（C2） の順。C3 を壊すと tr...
