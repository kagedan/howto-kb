---
id: "2026-04-17-claude-code-cli-を-api-代わりに使うのを諦めた話-01"
title: "Claude Code CLI を API 代わりに使うのを諦めた話"
url: "https://zenn.dev/0xliclog/articles/ea315228166c56"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "LLM", "OpenAI", "Gemini", "GPT"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

AutoCAD 上で動作する AI エージェントを個人で開発しています。
このエージェントは LLM モデルを選べる設計にしていて、OpenAI の ChatGPT、Google の Gemini、ローカルの LLM、そして Anthropic の Claude の4系統に対応する計画です。
通常、これらの API を使うと従量課金になります。使えば使うほどコストがかさむため、できれば避けたい。ユーザー目線でも API キーを取得するよりサブスクアカウントでログインする方が導入の壁が低くなります。
そこで目を付けたのが Claude Code CLI です。ちょうど自分が Claude ...
