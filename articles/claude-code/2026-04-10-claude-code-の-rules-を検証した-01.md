---
id: "2026-04-10-claude-code-の-rules-を検証した-01"
title: "Claude Code の rules を検証した"
url: "https://zenn.dev/metalels86/articles/2418a39f6057bb"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

はじめに
Claude Code には、特定のファイルパスにマッチした場合にのみルールを適用する paths frontmatter という機能がある。
このレポートでは、paths 条件の実際の動作を検証し、そこで見つかった制約と、それを回避するために構築した branch-rules-auto-loader の仕組みについてまとめる。


 1. Claude Code のルールファイルとは
Claude Code では ~/.claude/rules/ 配下に .md ファイルを置くと、全セッションで自動的に読み込まれるグローバルルールとして機能する。
さらに、ルールファイルの...
