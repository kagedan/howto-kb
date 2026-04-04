---
id: "2026-04-03-claude-desktop-にコンテキスト残量メーターを生やした話-01"
title: "Claude Desktop にコンテキスト残量メーターを生やした話"
url: "https://zenn.dev/saqoosha/articles/ccdex-claude-desktop-context-indicator"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

なにを作ったか
Claude Desktop の Code タブのフッターバーに、リアルタイムのコンテキスト使用量とレートリミット状況を表示するインジケーターを注入する拡張 CCDEX (Claude Code Desktop Context Extension) を作った。

https://github.com/Saqoosha/CCDEX?tab=
表示されるのは 3 つ：


コンテキスト使用量 — プログレスバー + トークン数（46.7k / 200.0k とか 171.2k / 1.0M とか）

5 時間レートリミット — 使用率 + リセットまでのカウントダウン（5...
