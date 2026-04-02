---
id: "2026-04-01-electronアプリの中にchrome組み込んでmcpサーバーにしたらclaude-codeが自分-01"
title: "Electronアプリの中にChrome組み込んでMCPサーバーにしたら、Claude Codeが自分でブラウザ操作できるようになった"
url: "https://zenn.dev/patapim/articles/e69b0d644d4ea8"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

タイトルの通りなんだけど、もう少し詳しく書く。
自分が作ってるターミナルIDE（PATAPIM）に、Chromeブラウザを丸ごと組み込んで、それをMCPサーバーとして公開した。Claude CodeがこのMCPツールを使って、Webページを開いたり、要素をクリックしたり、フォームに入力したり、スクリーンショットを撮ったりできる。
これがどういうことかというと、Claude Codeに「このWebアプリのログインフォームをテストして」って頼むと、本当にブラウザを操作してテストしてくれる。ヘッドレスじゃなくて、画面にブラウザが見えてて、リアルタイムでClaude Codeが操作してるのが分か...
