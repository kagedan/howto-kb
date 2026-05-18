---
id: "2026-05-17-gogcliを使ってclaude-codeのスキル管理を自動化する-01"
title: "gogcliを使ってClaude Codeのスキル管理を自動化する"
url: "https://zenn.dev/masarufuruya/books/f5000d1e4d5273"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "zenn"]
date_published: "2026-05-17"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

# gogcliを使ってClaude Codeのスキル管理を自動化する

Claude CodeのAgent Skillは便利ですが、20個、50個と増えていくと 「何があるか分からない」「使っていないスキルを消せない」という管理の課題に直面します。
本書では、CLIツール「gogcli」を使ってGoogleスプレッドシートと連携し、スキルの登録・使用回数の集計を自動化する仕組みをハンズオン形式で構築します。
本書で構築するもの
- gogcliのセットアップとOAuth認証
- スキル一覧をスプレッドシートに自動登録するAgent Skill
- 使用回数の集計・未登録スキルの差分検出
- CLAUDE.mdによる運用ルールの設定
想定読者
- Claude Codeを日常的に使っている方
- Agent Skillを自分で作ったことがある方
- スキルが増えてきて管理に困り始めている方
サーバー不要・DB不要。ローカルのClaude Code + Googleスプレッドシートだけで完結します。
著者が100個以上のスキルを管理する中で実際に使い続けている仕組みです。
