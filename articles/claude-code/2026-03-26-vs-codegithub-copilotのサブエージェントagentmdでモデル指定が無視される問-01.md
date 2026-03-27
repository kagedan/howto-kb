---
id: "2026-03-26-vs-codegithub-copilotのサブエージェントagentmdでモデル指定が無視される問-01"
title: "【VS Code】GitHub Copilotのサブエージェント(.agent.md)でモデル指定が無視される問題と最新動向"
url: "https://zenn.dev/headwaters/articles/b5d7d83a53b518"
source: "zenn"
category: "claude-code"
tags: ["AI-agent", "zenn"]
date_published: "2026-03-26"
date_collected: "2026-03-27"
summary_by: "auto-rss"
---

はじめに
VS CodeのCopilot Chatで .agent.md を使ったカスタムエージェント、便利ですよね。
特に runSubagent を使い、複数の専門エージェントをオーケストレーションする構成は、
VS Code公式ドキュメントでも推奨ユースケースとして紹介されています。

Subagents公式ドキュメント
https://code.visualstudio.com/docs/copilot/agents/subagents


一方で、実際に高度な構成を組んでみると、
「サブエージェント側（.agent.md）で指定したモデルが無視され、親エージェントのモデルが...
