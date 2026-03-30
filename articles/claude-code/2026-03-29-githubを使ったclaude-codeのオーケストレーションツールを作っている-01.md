---
id: "2026-03-29-githubを使ったclaude-codeのオーケストレーションツールを作っている-01"
title: "GitHubを使ったClaude Codeのオーケストレーションツールを作っている"
url: "https://qiita.com/getty104/items/6a0c87ba3eeba999e673"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-29"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

## この記事は何

以前、Claude Codeへのタスク依頼やレビュー修正依頼をGitHub上で完結できるようにした「claude-task-worker」というツールについて記事を書きました。

https://qiita.com/getty104/items/8e705c9e9f781a28c176

この記事を書いた時点では、GitHub上のラベルをトリガーにしてIssueの実装やPRのレビュー修正を自動化する、というのが主な機能でした。

そこからさらに開発を進め、今ではIssueの作成・更新・トリアージからPRのマージまで、開発ワークフローのほぼ全体をGitHub上でオーケストレーションできるツールになっています。この記事では、現在のclaude-task-workerとclaude-code-marketplaceの全体像と、それを使った開発ワークフローを紹介します。

https://github.com/getty104/claude-task-worker

https://github.com/getty104/claude-code-marketplace
