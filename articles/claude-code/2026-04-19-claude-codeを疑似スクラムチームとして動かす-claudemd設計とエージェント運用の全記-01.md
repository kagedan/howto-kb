---
id: "2026-04-19-claude-codeを疑似スクラムチームとして動かす-claudemd設計とエージェント運用の全記-01"
title: "Claude Codeを疑似スクラムチームとして動かす — CLAUDE.md設計とエージェント運用の全記録"
url: "https://zenn.dev/rurihari/articles/a1a3252b8d8f43"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

はじめに
Claude Codeは「1人のAIアシスタント」として使うだけでなく、チームのメンバー全員として使うことができます。
本記事では、1つのリポジトリに対してProduct Owner・Scrum Master・Developerx2・QAの5ロールをClaude Codeに担わせ、実際にPyQt5製AIエディタを3スプリントかけて開発した経験をまとめます。

「CLAUDE.md に何を書けば、Claude Code はチームっぽく動くのか？」
その答えを、設計思想・実際のファイル構成・運用の流れとともに解説します。



 なぜ疑似スクラムなのか

 通常の使い方の限界...
