---
id: "2026-04-02-claude-code-から-github-copilot-cli-を呼び出してaiを使い分ける開発-01"
title: "Claude Code から GitHub Copilot CLI を呼び出して、AIを使い分ける開発フロー"
url: "https://zenn.dev/geeknees/articles/829542e8b243b4"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "Gemini", "zenn"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

はじめに
Claude Code でコーディングしていて、「この判断は GitHub Copilot にも聞いてみたい」「Copilot のコードサジェストを今すぐ使いたい」と感じたことはありませんか?
claude-plugin-opinionated は、Claude Code のセッション内から /delegate-copilot コマンドで GitHub Copilot CLI を直接呼び出せるようにするプラグインです。Claude を起点に、GitHub Copilot・Gemini・Codex へタスクを委譲できます。
https://github.com/geeknee...
