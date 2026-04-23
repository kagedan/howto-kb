---
id: "2026-04-22-claude-haiku-45-skill-で-opus-47-を超えた-skillsbench-追-01"
title: "Claude Haiku 4.5 + skill で Opus 4.7 を超えた ― SkillsBench 追試とモデル選定の設計図"
url: "https://zenn.dev/ai_arai_ally/articles/20260422-0401-claude-haiku-4-5-skill-opus-4-7"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

SkillsBench（84タスク / 7モデル / 7,308試行）で 61.2% → 84.3%、Opus 4.7（80.5%）を上回った。
数字の意味はこうだった。Opus の出力を読み切る方が疲れる日があり、Haiku + skill に降ろした翌日、読み終えた後に時間が余っていた。
モデルを替えたんじゃない。モデル選定の判断軸を、1個ずらしただけだ。
このノートで分かることSkillsBench 論文が示した「skill を挟むと小型モデルが跳ねる」現象の核心
skill が小型モデルに効く「3つのメカニズム」
僕の Claude Code 環境（brain）での再現検証結果
...
