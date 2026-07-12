---
id: "2026-07-12-claude-code-並列開発の実録-chrome拡張をアイデアからストア公開へ最後は48時間で4-01"
title: "Claude Code 並列開発の実録 — Chrome拡張をアイデアからストア公開へ、最後は48時間で4リリース"
url: "https://zenn.dev/oceanscreative/books/claude-code-parallel-dev"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-07-12"
date_collected: "2026-07-13"
summary_by: "auto-rss"
query: ""
---

# Claude Code 並列開発の実録 — Chrome拡張をアイデアからストア公開へ、最後は48時間で4リリース

Claude Code のサブエージェントと git worktree による並列開発で、Chrome 拡張
（Claude Code Context Capturer）を初コミットから約2ヶ月で Chrome Web Store 公開・
v1.2.1 まで育て、終盤は 48時間で v1.0.0 → v1.2.1 の4リリースを出荷した
実プロジェクトの記録です。マルチエージェントのオーケストレーション、MV3 の罠と解法、
リリース自動化、そして Show HN・Reddit の「新規アカウントの壁」に跳ね返された
失敗談まで、実際の git 履歴に残っている事実だけを書きます。
実際にエージェントへ投げたブリーフや監査指示の文面を章内に引用しており、
読了後すぐ自分のリポジトリで同じ並列開発ワークフローを再現し始められます。
