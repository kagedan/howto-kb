---
id: "2026-04-20-claude-managed-agents-で自作ai開発オーケストレーターを組み直した-01"
title: "Claude Managed Agents で自作AI開発オーケストレーターを組み直した"
url: "https://zenn.dev/atsumell_blog/articles/0fdd4b1e07dd15"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

Claude Managed Agents で自作AI開発オーケストレーターを組み直した ー 何が消えて、何が残ったか
こんにちは。株式会社Atsumellのまつしたです。
弊社では、簡単な実装タスクを素早く処理するため、GitHub の Issue にラベルをつけると、Claudeが起動してPRを作成し、CodeRabbitのレビューに対して修正するような、GitHub Issue 駆動のシンプルな開発オーケストレーターを自前で実装していました。(ClaudeのGitHub Appも便利ですが、もう少し複雑なワークフローを組みたくて自前実装をしています。)
すぐエラーで詰まったりす...
