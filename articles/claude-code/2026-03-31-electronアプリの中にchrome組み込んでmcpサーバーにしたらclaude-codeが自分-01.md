---
id: "2026-03-31-electronアプリの中にchrome組み込んでmcpサーバーにしたらclaude-codeが自分-01"
title: "Electronアプリの中にChrome組み込んでMCPサーバーにしたら、Claude Codeが自分でブラウザ操作できるようになった"
url: "https://qiita.com/patapim/items/d36a759b4d4a2fe766dc"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

タイトルの通りなんだけど、もう少し詳しく書く。

自分が作ってるターミナルIDE（[PATAPIM](https://patapim.ai)）に、Chromeブラウザを丸ごと組み込んで、それをMCPサーバーとして公開した。Claude CodeがこのMCPツールを使って、Webページを開いたり、要素をクリックしたり、フォームに入力したり、スクリーンショットを撮ったりできる。

これがどういうことかというと、Claude Codeに「このWebアプリのログインフォームをテストして」って頼むと、本当にブラウザを操作してテストしてくれる。ヘッドレスじゃなくて、画面にブラウザが見えてて、リアルタイムでClaude Codeが操作してるのが分かる。

## なぜ作ったか

Claude CodeのMCPには`mcp__puppeteer`とか外部のブラウザ操作ツールがあるけど、いくつか不満があった。

ヘッドレスだと何やってるか見えない。「あれ、今なにしてんの？」ってなる。別ウィンドウで立ち上がると、ターミナルとブラウザを行き来するのがめんどい。あとPlaywrightとかPuppeteerだと
