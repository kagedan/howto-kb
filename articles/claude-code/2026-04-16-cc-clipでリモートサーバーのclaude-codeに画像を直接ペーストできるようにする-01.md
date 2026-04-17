---
id: "2026-04-16-cc-clipでリモートサーバーのclaude-codeに画像を直接ペーストできるようにする-01"
title: "cc-clipでリモートサーバーのClaude Codeに画像を直接ペーストできるようにする"
url: "https://zenn.dev/zaico/articles/45bffcd94b5c68"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

株式会社ZAICOでCTOをやっている @fukata です。

 はじめに
リモートサーバー上でClaude Codeを使っていると、画像を貼り付けたい場面がありませんか？ローカル環境であればCtrl+Vで済むところが、SSH越しだとそうはいきません。これまではGyazoなどの外部サービスを経由したり、一度サーバーに画像をアップロードする必要がありました。
cc-clipを使えば、SSHトンネル経由でローカルのクリップボードをリモートに転送し、Ctrl+Vで画像を直接ペーストできるようになります。
筆者は自宅サーバーへの接続にTailscaleを使用しています。Tailscaleを使う...
