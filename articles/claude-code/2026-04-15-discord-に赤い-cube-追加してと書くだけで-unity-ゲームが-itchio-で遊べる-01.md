---
id: "2026-04-15-discord-に赤い-cube-追加してと書くだけで-unity-ゲームが-itchio-で遊べる-01"
title: "Discord に「赤い Cube 追加して」と書くだけで Unity ゲームが itch.io で遊べるようになる仕組みを作った~Claude Code + Unity MCP + GitHub Actions で完全自動化~"
url: "https://qiita.com/kumi0708/items/679097d959d211d59a96"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

## はじめに

Discord のチャットに `!build シーンに赤い Cube を位置 (0, 0, 0) に追加して、シーンを保存してください` と書きます。5〜10 分後、同じ Discord のチャンネルに `🎮 ビルド完成しました!` というメッセージと itch.io の URL が来ます。URL をクリックすると、ブラウザで指示通りの Unity シーンが WebGL で動いています。

淡々と書いてしまったので画像がはいっていないのでわかりずらいですが、
後日スクショ貼るようにします。

[ 時間のない方へ: 最短実装手順](#時間のない方へ-最短実装手順)


### 誰のための記事か

- Unity で作ったゲームを AI に触らせてみたい人
- Discord bot と AI エージェントの連携を作ってみたい人
- GitHub Actions でセルフホストランナーを使った自動ビルドを構築したい人
- 「自然言語で指示すると AI がゲームを書き換えてくれる」環境が欲しい人
- 自分がやってみたのだけど、やったことを忘れちゃうから自分の為←ここ大事
