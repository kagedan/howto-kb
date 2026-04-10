---
id: "2026-04-09-claude-code-でobsidian-上に-wiki-を作る-01"
title: "Claude Code で、Obsidian 上に Wiki を作る"
url: "https://zenn.dev/wfukatsu/articles/a70a311f5a7b51"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "LLM", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

Andrej Karpathy が提唱した LLM Wiki パターン（LLM にソースドキュメントを読ませ、構造化された wiki ページを自動生成・維持させる手法）を Obsidian プラグイン + Claude Code スキル として実装した話です。
実際にプロジェクト資料 15 本を食わせて 28 ページの wiki を自動生成し、品質監査まで回した結果を交えて解説します。

 対象読者

Obsidian でナレッジ管理をしているが「書く気力がない」方
LLM を「おしゃべり相手」以上に使いたいエンジニア
Karpathy の LLM Wiki パターンに興味があるが実装方...
