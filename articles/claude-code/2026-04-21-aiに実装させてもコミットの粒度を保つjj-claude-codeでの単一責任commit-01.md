---
id: "2026-04-21-aiに実装させてもコミットの粒度を保つjj-claude-codeでの単一責任commit-01"
title: "AIに実装させてもコミットの粒度を保つ〜jj × Claude Codeでの単一責任Commit〜"
url: "https://zenn.dev/sun_asterisk/articles/jj-hook-with-lefthook"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

はじめに
Spec Driven や Issue Driven を
Claude Code などのAIエージェントに実行させ、機能実装や修正をしていく
という方法が定着しつつあるように見えます。
しかし、AIに実装させて、いざ git でコミットさせてみると
AIエージェントの使い方によっては
あらゆる変更が1つの巨大なコミットにまとまりがちです。
この記事では、jj（Jujutsu） の Change という概念と
Claude Code を組み合わせることで
AIが実装してもコミットの単一責任を維持する方法を紹介します。
前提環境
この記事では以下のツールを使用します。



ツ...
