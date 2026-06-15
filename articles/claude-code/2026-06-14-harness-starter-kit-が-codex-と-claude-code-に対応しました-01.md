---
id: "2026-06-14-harness-starter-kit-が-codex-と-claude-code-に対応しました-01"
title: "Harness Starter Kit が Codex と Claude Code に対応しました"
url: "https://zenn.dev/yuuaan/articles/3c2f2a8211b610"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "Python", "TypeScript"]
date_published: "2026-06-14"
date_collected: "2026-06-15"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/e18ff3e8270f-20260614.jpg)

こんにちは。

最近、Harness Starter Kit に Codex と Claude Code のサポートを追加しました。これにより、Agent Skills / plugin を通じて関連するワークフローを使えるようになりました。

Harness Starter Kit は、coding agent がプロジェクト内で繰り返し起こしがちな問題を、長期的に維持できるリポジトリのルール、チェック、失敗記録、意思決定記録、評価フローとして残していくための prompt-first なオープンソースツールキットです。

簡単に言うと、1回の prompt を改善するだけではなく、リポジトリ自体を AI coding agent が安定して作業しやすい環境にしていくためのものです。

今回の Codex / Claude Code 対応により、対応している開発環境では `/harness doctor` や `/harness review` のようなワークフローをより直接使えるようになりました。これらは、agent 向けの指示、プロジェクト上の制約、フィードバックループ、記憶として残すべき記録、ルールが徐々にずれていくリスクなどを確認するためのものです。

現在、Python、TypeScript、Node.js、React、Next.js、Vue、Django、Flask、FastAPI、Spring Boot、Android、Go、Rust など、複数の技術スタック向けの参考 profile も含まれています。今後もドキュメント、サンプル、実際のプロジェクトへの導入フローを改善していく予定です。

GitHub：  
[harnessworks/harness-starter-kit](https://github.com/harnessworks/harness-starter-kit)

AI coding agent、Codex、Claude Code、または agent と協作しやすいリポジトリづくりに興味があれば、ぜひ試してみてください。フィードバックや提案も歓迎です。

もしこのプロジェクトが役に立ちそうだと思ったら、GitHub Star を付けてもらえるととても助かります。今後のメンテナンスと改善の励みになります。
