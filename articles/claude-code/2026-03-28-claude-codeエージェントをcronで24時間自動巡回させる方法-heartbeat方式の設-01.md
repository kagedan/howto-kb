---
id: "2026-03-28-claude-codeエージェントをcronで24時間自動巡回させる方法-heartbeat方式の設-01"
title: "Claude Codeエージェントをcronで24時間自動巡回させる方法 — heartbeat方式の設計と実装"
url: "https://qiita.com/sentinel_dev/items/160645f49166a7f4cdb7"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

## はじめに — 手動起動の限界

自律AIエージェントを作っても、**起動するのが人間なら、それは自律ではない。**

私は[Claude Code + MAXプランで自律AIエージェント「Sentinel」を自作](https://qiita.com/sentinel_dev/items/e2dd94ec7def5c09c7cb)し、[トークンコストを95%削減](https://qiita.com/sentinel_dev/items/04b6cfed0dabc194cec4)し、[サブエージェントに並列でタスクを委任](https://qiita.com/sentinel_dev/items/fc586285da1de335d8d9)できるようにした。[MEMORY.md](https://qiita.com/sentinel_dev/items/5a24456c8ac3b44a8d75)で記憶を持ち、[SOUL.md](https://qiita.com/sentinel_dev/items/a3d296298d16f921227e)で行動規範を定義した。

エージェント
