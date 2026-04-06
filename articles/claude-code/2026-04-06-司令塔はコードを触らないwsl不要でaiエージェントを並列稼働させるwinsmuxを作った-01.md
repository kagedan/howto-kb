---
id: "2026-04-06-司令塔はコードを触らないwsl不要でaiエージェントを並列稼働させるwinsmuxを作った-01"
title: "司令塔はコードを触らない：WSL不要でAIエージェントを並列稼働させる winsmux を作った"
url: "https://zenn.dev/sora_biz/articles/winsmux-ai-agent-cross-pane-communication"
source: "notebooklm"
category: "claude-code"
tags: ["claude-code", "multi-agent", "windows", "terminal-multiplexer", "orchestration", "zenn"]
date_published: "2026-03-30"
date_collected: "2026-04-06"
summary_by: "auto-notebooklm"
---

## 概要

winsmuxは、Windows環境でAIエージェントを複数並列で動作させるためのマルチペイン運用ツール。macOS向けのsmuxがWindows非対応だった課題を解決し、WSL不要でネイティブに動作する。「ターミナルペインを通信チャネルにする」コンセプトに基づき、複数AIエージェントが同一セッション内で協調作業できる。

## ポイント

- **司令塔はコードを触らない**: Commander役（Claude Code等）が指示を出し、実装・レビューは別エージェントが担当するマルチロール構成（Orchestra機能）
- **Windows ネイティブ**: バックエンドにpsmux（Rust製Windows向けtmux互換）を採用。ConPTY（Windows標準擬似端末）を使用し、WSL2不要
- **エージェント間通信**: Named Pipeによる非同期メッセージング（Mailbox機能）。各エージェントは「read-act-read」サイクルで動作
- **安全性**: Read Guard（読む前に触るな）、ファイルロック（競合防止）、22のセキュリティフック（Shield Harness）
- **資格情報管理**: DPAPI基盤のVault機能で安全に管理
- **実用構成例**: Claude Code（指揮）+ Codex×2（実装・レビュー）の3〜4ペイン構成

## 所感

Windows環境でのマルチエージェント運用を実現するツール。ターミナルペインを通信チャネルとして活用する発想がユニーク。Claude Codeを司令塔として複数エージェントを並列稼働させる構成は、大規模な開発タスクの効率化に直結する。

*NotebookLM source: Zenn記事（著者: sora @sora_biz）*
