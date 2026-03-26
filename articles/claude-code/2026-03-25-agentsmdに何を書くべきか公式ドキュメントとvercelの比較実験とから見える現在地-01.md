---
id: "2026-03-25-agentsmdに何を書くべきか公式ドキュメントとvercelの比較実験とから見える現在地-01"
title: "AGENTS.mdに何を書くべきか？公式ドキュメントとVercelの比較実験とから見える現在地"
url: "https://zenn.dev/rai0/articles/15622bbd1ac823"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "OpenAI", "zenn"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

AI コーディングエージェント向けの指示ファイルとして AGENTS.md が広まりつつある。
ただ、実務で悩むのは「何をどこまで書くべきか」だ。
全部まとめて大きな AGENTS.md を作るべきなのか。
それとも、最低限だけ書いて詳細は docs/ に逃がすべきなのか。
この記事では、OpenAI の公式事例、Vercel の比較実験、Claude Code の公式ドキュメントを並べて、AGENTS.md の実務的な落としどころを整理する。

 結論
先に結論を書くと、現時点では次の方針がかなり有力だ。

AGENTS.md は「百科事典」ではなく「地図・目次」にする。
詳細な規約・...
