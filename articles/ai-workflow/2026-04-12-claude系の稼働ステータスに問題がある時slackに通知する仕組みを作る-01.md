---
id: "2026-04-12-claude系の稼働ステータスに問題がある時slackに通知する仕組みを作る-01"
title: "Claude系の稼働ステータスに問題がある時Slackに通知する仕組みを作る"
url: "https://qiita.com/miriwo/items/21b1055016850810253e"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-12"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## 概要

利用者の増加も相まって2026年4月現在、若干Claude系サービスが不安な時があります。
都度都度下記を見に行ってもいいのですが、事前に障害情報を知れると「使いたい時に運悪く使えない」が防げるのでClaude系で障害が発生した時にSlackに通知する仕組みを簡単に作ってみます。公式が通知用Slackアプリを作ってくれているので導入は簡単でした。

https://status.claude.com/

## 前提

必須ではないが、ブラウザでのSlackアカウントログインと通知先Slackチャンネルの作成が完了していると作業がスムーズです。

## 方法

### 設定方法

1. [こちら](https://status.claude.com/)の右上の「SUBSCRIBE TO UPDATES」をクリックします（当該サイトアクセスはSlackログインが完了しているブラウザだとログイン作業等が不要なので今後の作業が楽だと思います。）

    ![CleanShot 2026-04-11 at 23.15.02.png](https://qiita-image-sto
