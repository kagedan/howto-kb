---
id: "2026-03-30-claude-codeとcodexの連携をmcpからskillに変えたら体験が劇的に改善した-01"
title: "Claude CodeとCodexの連携をMCPからSkillに変えたら体験が劇的に改善した"
url: "https://zenn.dev/owayo/articles/63d325934ba0de"
source: "notebooklm"
category: "claude-code"
tags: ["claude-code", "skill", "MCP", "codex", "zenn"]
date_published: "2026-01-14"
date_collected: "2026-03-30"
summary_by: "auto-notebooklm"
---

## 概要

Claude CodeとCodex CLIの連携方式をMCP（Model Context Protocol）からSkillに変更した際の劇的な改善について解説した記事（著者: owayo）。

## MCPでの課題

- **進捗が見えない** — 実行中の状況が不明瞭
- **長時間待機** — 数十分〜1時間以上の無応答が発生
- **デバッグが困難** — エラーの原因特定が難しい

MCPツールは結果が返るまでブラックボックスになるため、長時間実行されるタスクには向いていない。

## Skillへの移行による改善

- リアルタイムの進捗表示
- ターミナル出力による可視化
- スラッシュコマンド（`/codex`）での即座の呼び出し
- エラー内容の即座の把握

実行状況を監視でき、必要に応じて早期に処理を中断できるようになった。
