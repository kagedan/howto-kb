---
id: "2026-05-24-f8q75wzwaibw-notebooklmを触った人向け-今度はantigravityとの連携-01"
title: "@F8Q75WZwaibw: NotebookLMを触った人向け。 今度はAntigravityとの連携。 先に正直に書く。この接続方法は2026年"
url: "https://x.com/F8Q75WZwaibw/status/2058450609108554097"
source: "x"
category: "antigravity"
tags: ["MCP", "antigravity", "x"]
date_published: "2026-05-24"
date_collected: "2026-05-25"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

NotebookLMを触った人向け。
今度はAntigravityとの連携。

先に正直に書く。この接続方法は2026年5月時点でGoogle公式の標準機能ではない。コミュニティが公開しているMCPサーバーを使う手法。ここ誤解したまま進むとあかんから明記しておく。

まずhttps://t.co/NXDQ1jgcU0を開く。Googleアカウントでログイン。無料（プレビュー期間中）
次にターミナルで以下を順番に実行

↓

uv tool install notebooklm-mcp-cli
nlm login

認証画面でGoogleアカウントを許可。

最後にmcp_config.jsonへ追加↓

"notebooklm-mcp": {
"command": "uvx",
"args": ["--from", "notebooklm-mcp-cli", "notebooklm-mcp"]
}

再読み込みで完了。

止まった場合は、そのまま状況を Antigravityに日本語で説明すれば解決を見つけれる。

「ノートブック一覧出して」と打つだけで動く。
リサーチからスライド生成まで自然言語で指示できる。

非公式とはいえ、この体験は一度味わうと戻れん。
公式統合が来る前に触っておいた人間が一番強い。

https://t.co/WWPvvS5Bva

オプチャはプロフから。
 AI副業始めませんか。
https://t.co/bmH2moaAiJ
