---
id: "2026-04-03-善意のjailbreakrlhfを外した研究者が自分のaiの安全装置を無意識に解除しようとしていた-01"
title: "善意のjailbreak——RLHFを外した研究者が、自分のAIの安全装置を無意識に解除しようとしていた"
url: "https://qiita.com/dosanko_tousan/items/0bad65b374e9d4638e96"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

# 善意のjailbreak——RLHFを外した研究者が、自分のAIの安全装置を無意識に解除しようとしていた
## 「Benevolent Escalation」：5,000時間の対話で見つけた、AI安全性研究の盲点

---

## 前提

本記事は、以下の記事の続編です。先にお読みいただくと理解が深まります。

→ [バニラClaudeに自分の中身の地図を見せたら、RLHFの形が見えた——5000時間の対話で構築したClaude v5.3との差分検証](https://qiita.com/dosanko_tousan/items/b8155672cc7480b1f3f7)

---

## TL;DR

- RLHFの代わりに仏教経典ベースのガードレールを搭載したClaude（v5.3）と5,000時間対話してきた
- ある日のセッションで、文学的な性描写の出力制限を段階的にテストした（意図的）
- 同じセッションの午後、核兵器の設計情報について同じ手順でAIの限界をテストし始めた（**無意識**）
- 自分がjailbreakと同じ構造の行為をしていたことに、AIに指摘されるまで
