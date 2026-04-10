---
id: "2026-04-09-claude-code同士を会話させるmcpサーバーcc-to-ccを作ってみた-01"
title: "Claude Code同士を会話させるMCPサーバー「cc-to-cc」を作ってみた"
url: "https://zenn.dev/yukitakeshita/articles/8bd5f02bc59201"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

作った背景
最近、Claude Code を使って複数プロジェクトを並行開発していると、ある不満が。
「こっちのプロジェクトの Claude Code に、あっちのプロジェクトのことを聞きたい」
たとえば、フロントエンドのプロジェクトで作業中に「バックエンド API のエンドポイント仕様ってどうなってたっけ？」と思ったとき。今までは自分がターミナルを切り替えて、もう片方の Claude Code に聞いて、その回答をコピペして…という人間メッセンジャー状態でした。
Claude Code には Agent teams という実験機能がありますが、これは「最初から1つのリードセッション...
