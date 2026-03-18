---
id: "2026-03-16-claude-code-actionでgithub-issue駆動ai開発-01"
title: "Claude Code ActionでGitHub Issue駆動AI開発"
url: "https://zenn.dev/kanahiro/articles/98dce92b922a9e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-03-16"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

はじめに
Issueを起点とした以下のようなフローを手に馴染ませていたところでした（手元のマシンで動かす前提）。

GitHub Issueでビジネス要求を記述
Claude CodeでIssueを読んで、Plan
納得いくまでPlanを叩く
実装

意外と悪くないなと思っていたのですが、「これをやるなら最早GitHub上でClaude Codeが動けばそれで良いじゃん」と気づいてしまったので、やってみた記事です。

 anthropics/claude-code-action

https://github.com/anthropics/claude-code-action
最初は...
