---
id: "2026-04-27-kenta-akagi-anthropic-engineeringがagentic-codingにお-01"
title: "@kenta_akagi: Anthropic Engineeringがagentic codingにおけるHarness設計の手法を公開。フロント"
url: "https://x.com/kenta_akagi/status/2048779800320594300"
source: "x"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "x"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

Anthropic Engineeringがagentic codingにおけるHarness設計の手法を公開。フロントエンドデザインと長時間自律型ソフトウェアエンジニアリングの2領域でClaudeを前進させた具体的な設計知見で、「Harnessがフロンティアでのパフォーマンスの鍵」と明言してる。実装パターンとして参照できる内容になってそう

https://t.co/IJrzvRfhEG

技術的な肝はlong-runningタスクでのコンテキスト管理とエラーリカバリの設計。単発APIコールと違って複数ステップのエージェントは途中状態の保存・リトライ・プロセス境界の制御が必要になる。LangChainのAgentExecutorやTemporalと構造的に近い問題で、そこをAnthropicがどう解いてるかが見えてくる感じ

Claude Codeで実際にプロダクト開発してると、長時間タスクの途中中断とリカバリ設計がやっぱりキツい。このHarness設計パターンが参照できると、どのレイヤーに挟むか判断しやすくなる。コスト管理と途中エラー処理、ここが運用で一番詰まるポイントだったりするんですよね
