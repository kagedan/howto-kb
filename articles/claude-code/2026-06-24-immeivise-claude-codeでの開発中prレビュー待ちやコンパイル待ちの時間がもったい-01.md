---
id: "2026-06-24-immeivise-claude-codeでの開発中prレビュー待ちやコンパイル待ちの時間がもったい-01"
title: "@immeivise: Claude Codeでの開発中、PRレビュー待ちやコンパイル待ちの時間がもったいなくて、git worktreeで並列"
url: "https://x.com/immeivise/status/2069586501277712775"
source: "x"
category: "claude-code"
tags: ["claude-code", "LLM", "x"]
date_published: "2026-06-24"
date_collected: "2026-06-24"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

Claude Codeでの開発中、PRレビュー待ちやコンパイル待ちの時間がもったいなくて、git worktreeで並列開発を試してみた。結果、効率が劇的に向上した。worktreeを使うことでブランチ切り替え時のコンテキスト喪失がなくなり、別ディレクトリで独立してタスクを進められる。特にClaude Codeのエージェント実行をworktree単位で分離できるのが良い。ccmanagerのようなツールでセッション状態を可視化しながら複数タスクを管理すると、待ち時間を完全に埋められる。ただ、メモリ使用量とディスク容量の増加が気になるところ。大きなプロジェクトだと複数worktreeの維持コストがどこまで許容できるかは要検証だと思う。

#Claude #LLM

参考リンク:
https://t.co/hUIEJM8wp1
https://t.co/VXpGQS0KbY
https://t.co/8kZaO91lED
