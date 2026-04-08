---
id: "2026-04-06-claude-code-で最小再現環境の構築を自動化する-minimal-repro-スキルの紹介-01"
title: "Claude Code で最小再現環境の構築を自動化する — minimal-repro スキルの紹介"
url: "https://zenn.dev/tell_y/articles/e21d348284c5a5"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-06"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

Claude Code で最小再現環境の構築を自動化する — minimal-repro skillの紹介

 TL;DR
バグの原因切り分けに必要な「最小再現環境（minimal reproduction）」の構築を Claude Code のスキルとして自動化しました。/minimal-repro と打つだけで、複数パターンの再現環境を一括生成し、実行・比較・レポート出力まで一気通貫でやってくれます。実際に Vite 8 アップグレード時の問題でこのスキルを試して、原因の特定と解決に至ったので、使える事例として紹介してみようと思います。
(※こういうskillが既に世にあるとは思...
