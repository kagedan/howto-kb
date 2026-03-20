---
id: "2025-12-10-oikon48-day10project-ルール-clauderules-claude-code-a-01"
title: "@oikon48: 【Day10】Project ルール `.claude/rules/`
#claude_code_advent_cale"
url: "https://x.com/oikon48/status/1998717425223872974"
source: "x"
category: "claude-code"
tags: ["claude-code", "API", "x"]
date_published: "2025-12-10"
date_collected: "2026-03-20"
summary_by: "auto-x"
---

【Day10】Project ルール `.claude/rules/`
#claude_code_advent_calendar  

Claude CodeはCLAUDE .md の他に、rulesを設定可能。`.claude/rules/` にMarkdownでプロジェクトルールを記載する。トピック別のプロジェクト指示が管理しやすい。

(例)
・コードスタイル
・テスト規約
・セキュリティ

YAMLフロントマターで特定のファイルのみに適用されるルールを定義可能:

(例)
---
paths: src/api/**/*.ts
--- 

検証の結果、Globパターンマッチングで動的にrulesがコンテキストにロードされる仕様と推察される。
