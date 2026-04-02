---
id: "2026-04-01-claude-codeのskillsでハーネスエンジニアリングを実装した-ルール自動生成でコード品質-01"
title: "Claude CodeのSkillsでハーネスエンジニアリングを実装した — ルール自動生成でコード品質を継続改善する"
url: "https://zenn.dev/shintaroamaike/articles/df3ecc0ddee047"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

はじめに
CLAUDE.md にプロジェクトのルールを書けば Claude Code は守ってくれます。
でも、そのルールを書くのは結局あなた自身です。
pathlib.Path を使うこと、Decimal で金額計算すること、bare except を避けること——
チームの暗黙知をすべて文章に起こし、漏れなく管理し続けるのは意外と手間がかかります。
AutoHarness スキルはそのルール生成と改善を自動化します。


/autoharness-init を一度実行するだけで、プロジェクトを解析して
型チェック・lint・命名規則を .claude/rules/harness....
