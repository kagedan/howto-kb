---
id: "2026-04-10-claude-code-に開発フローを守らせるsuperpowersを使った-skills-設計パタ-01"
title: "Claude Code に開発フローを守らせるsuperpowersを使った Skills 設計パターン"
url: "https://zenn.dev/dk_/articles/1f3fbc506827ac"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

はじめに
Claude Codeは強力なAIコーディングアシスタントですが、何も制約を設けずに使うと「テストを書かずに実装した」「PRテンプレートを無視した」「設計判断を記録しなかった」といった品質のブレが発生します。
人間の開発者にコーディング規約やレビュープロセスがあるように、AIにも「開発フローを守らせる仕組み」が必要です。
本記事では、Claude Code のSkills機能を使って、プロジェクト固有の開発フローをAIに強制する方法を、実際の運用例とともに紹介します。
!
Claude CodeのSkills機能については割愛します


 superpowersプラグイン
...
