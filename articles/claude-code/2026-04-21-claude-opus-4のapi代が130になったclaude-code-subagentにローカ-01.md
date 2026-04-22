---
id: "2026-04-21-claude-opus-4のapi代が130になったclaude-code-subagentにローカ-01"
title: "Claude Opus 4のAPI代が1/30になった。Claude Code subagentにローカルのQwen3を繋いだだけだ"
url: "https://zenn.dev/ai_arai_ally/articles/20260420-2053-claude-code-subagentllm-opus"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

夜間バッチ1回で$3.60だったOpus課金が、$0.12に落ちた。Opus 4は今も毎晩、同じ本数だけ回している。止めていない。削ったのは「Opusに投げる必要がなかったタスク」だけだ。
月$108が$3.60になった計算になる。Orchestrationだけ残して、他を全部ローカルに逃がしただけだ。
このノートでわかることClaude Code subagentにLM Studio経由のローカルモデルを繋ぐ具体設定
どのタスクをローカルに落としどれをOpusに残すかのルーティング設計
実測のトークン削減と、品質を落とさないための線引き
課金不安ゼロで自律システムを回すための構成判断
...
