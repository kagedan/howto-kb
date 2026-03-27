---
id: "2026-03-25-norihikoamano-最近の自分のclaude-codeワークフローメモ-準備-グローバルのc-01"
title: "@NorihikoAmano: 最近の自分のClaude Codeワークフローメモ 【準備】 ・グローバルのCLAUDE.mdには「余計な機能はつけず"
url: "https://x.com/NorihikoAmano/status/2036777334657986880"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "x"]
date_published: "2026-03-25"
date_collected: "2026-03-27"
summary_by: "auto-x"
---

最近の自分のClaude Codeワークフローメモ

【準備】
・グローバルのCLAUDE.mdには「余計な機能はつけずにシンプルに実装せよ」「指示があるまで勝手に開発に着手するな」を書いておく
・MCPはPlaywrightくらい。使わないMCPは無効化してコンテキスト節約

【計画】
・/initでやりたいことを伝えてプロジェクトのCLAUDE.md生成
・GitHubにプライベートリポジトリ作成
・specsフォルダを作ってMarkdown置き場に
・計画、リサーチ結果、仕様、タスク、進捗、使用方法など、とにかくMarkdownファイル化する
・大きい開発ではspecsを階層化。上位の資料だけ参照必須にして、下位は必要に応じて参照。段階的開示でコンテキスト節約
・planモードでプロジェクト計画。必要に応じてウェブリサーチさせる
・計画はMarkdown出力し、納得いくまで練り直す

【開発】
・開発着手前に必ずcommit。開発中もこまめにcommit。ブランチも適宜切る
・コンテキスト消費はステータスバーに表示
・開発中のコンテキスト枯渇を避けるために、開発前には/clear
