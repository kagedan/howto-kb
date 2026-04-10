---
id: "2026-04-09-sqliteからcockroachdbに移行してaiの記憶が本物になった話-iphoneアプリ-cl-01"
title: "SQLiteからCockroachDBに移行して、AIの記憶が「本物」になった話 —— iphoneアプリ Claush"
url: "https://zenn.dev/claush/articles/6bcd60524fccfe"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

Claushとは
Claushは、iPhoneからVPS上のClaude CodeをSSH経由で操作するiOSアプリだ。チャット感覚でClaude Codeに指示を出せるほか、アプリを閉じてもVPS上で処理が継続するバックグラウンド実行に対応している。
https://apps.apple.com/jp/app/claush/id6760445443
AIキャラクターが会話を担当し、会話の長期記憶を保持する。記憶システムはVPS上で動作するmemory-server.jsがMCPサーバーとして機能する設計だ。
メモリDBの選択肢は以下の2つ：



DB
特徴




SQLite（...
