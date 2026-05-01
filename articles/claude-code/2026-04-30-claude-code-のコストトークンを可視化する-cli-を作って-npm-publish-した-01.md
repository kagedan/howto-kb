---
id: "2026-04-30-claude-code-のコストトークンを可視化する-cli-を作って-npm-publish-した-01"
title: "Claude Code のコスト・トークンを可視化する CLI を作って npm publish した話"
url: "https://zenn.dev/kojihq/articles/66ca3fca6df2a0"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-30"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

はじめに
Claude Code を使い始めて 3 ヶ月、コストとトークン消費が気になってきました。Anthropic Console で月の合計は見えますが、「どのプロジェクトに何時間費やしたか」「どのモデルがコストを支配しているか」のような粒度では見えません。
ただ、ローカルには答えがあります。Claude Code はセッションログを ~/.claude/projects/&lt;project&gt;/&lt;session&gt;.jsonl に JSONL で書き出していて、トークン数・モデル・ツール呼び出し・コスト計算に必要な情報がほぼ全部入っています。これをローカルだ...
