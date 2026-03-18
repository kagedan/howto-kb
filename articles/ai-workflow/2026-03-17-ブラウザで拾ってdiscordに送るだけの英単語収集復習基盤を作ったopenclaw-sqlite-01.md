---
id: "2026-03-17-ブラウザで拾ってdiscordに送るだけの英単語収集復習基盤を作ったopenclaw-sqlite-01"
title: "ブラウザで拾ってDiscordに送るだけの英単語収集＆復習基盤を作った（OpenClaw × SQLite）"
url: "https://zenn.dev/dokusy/articles/58840a6c21e548"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

はじめに
最近英語学習に力を入れています。
学習の時に知りたい単語を保存する仕組みは簡単に作れるが、実際には見返さなくなる問題が起きやすいと思います。
なので今回はOpenClawを活用して次のような仕組みを構築しました！

ブラウザで選択した単語をDiscordへ送信
Discord投稿してOpenClawがSQLiteに記録
保存時に意味や例文を自動で返信
保存後は定期的にOpenClawがリマインダーをしてくれる

この記事ではブラウザ拡張とOpenClawを組み合わせた実装についてまとめました。

 まずはどんな感じのやつか紹介

ブラウザで知りたい単語を選択して、shift...
