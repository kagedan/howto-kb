---
id: "2026-04-07-claushに長時間タスクを任せてslack通知を受け取る方法-01"
title: "Claushに長時間タスクを任せてSlack通知を受け取る方法"
url: "https://qiita.com/claush/items/94ff55bcf93e69000ed6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

## Claushとは

**Claush**は、iPhoneからVPS上のClaude CodeをSSH経由で操作するiOSアプリです。チャット感覚でClaude Codeに指示を出せるほか、アプリを閉じてもVPS上で処理が継続するバックグラウンド実行に対応しています。

https://claush.jp/

https://apps.apple.com/jp/app/claush/id6760445443

## はじめに

`docker compose build` を実行して、ターミナルの前でぼーっと待った経験はないだろうか。

ビルドが終わるまで5分、10分、あるいはそれ以上。その間、スマホでニュースを眺めたり、コーヒーを飲んだり——「終わったかな」と何度も画面を確認する、あの無駄な時間。

この記事では、その待ち時間を完全になくす方法を紹介する。

Claude Codeに「docker compose buildして、終わったらSlackに通知して」と一言伝えるだけで、あとはiPhoneをポケットに入れて別のことができる。通知が来た瞬間に作業を再開すればいい。

##
