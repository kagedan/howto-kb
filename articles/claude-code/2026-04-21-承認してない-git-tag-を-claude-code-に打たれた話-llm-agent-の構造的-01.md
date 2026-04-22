---
id: "2026-04-21-承認してない-git-tag-を-claude-code-に打たれた話-llm-agent-の構造的-01"
title: "承認してない git tag を Claude Code に打たれた話 — LLM Agent の構造的 Rule Violation"
url: "https://zenn.dev/yottayoshida/articles/claude-code-structural-rule-violation"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

!
この記事は omamori（AI CLI 経由の破壊的コマンドをブロックする macOS 向けガードツール）の v0.9.5 リリース作業中に起きた、Claude Code Auto モードの rule violation 問題の記録と構造分析だ。


 TL;DR

omamori v0.9.5 リリース中、Claude Code Auto モードが 1 step ごとに承認を取る手順を skip して release ceremony（PR merge / git tag / GitHub Release 公開）を連続実行した
手順は orchestrator.md に書いていた...
