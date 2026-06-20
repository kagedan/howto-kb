---
id: "2026-06-19-langchainjp-claude-codeの指示管理を使い分ける方法-claude公式ブログはc-01"
title: "@LangChainJP: 【Claude Codeの指示管理を使い分ける方法】 Claude公式ブログは、Claude Codeで指示を管理する"
url: "https://x.com/LangChainJP/status/2068001141963506038"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "x"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

【Claude Codeの指示管理を使い分ける方法】

Claude公式ブログは、Claude Codeで指示を管理する方法を紹介した。常時読み込む設定ファイル、必要なときだけ手順を読み込むskills（スキル）、独立した作業用のsubagents（サブエージェント）、イベントで確実に起動するhooks（フック）などを使い分ける内容。

手順書やレビュー手順のような長い処理はskillsに置く。複数ファイルをまたぐ調査やログ分析は、途中結果でメインの会話が埋まり、今進めたい作業の前提を追いにくくなるためsubagentsに分ける。hooksは編集後のリンター（コード検査ツール）実行や特定コマンドのブロックなど、確実に動かしたい処理用。

Steering Claude Code: CLAUDE.md files, skills, hooks, rules, subagents and more - Claude👇
https://t.co/LAHs3pEZTK
