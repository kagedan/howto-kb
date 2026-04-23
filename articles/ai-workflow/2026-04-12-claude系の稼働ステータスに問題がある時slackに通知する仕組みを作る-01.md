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

## 前提

必須ではないが、ブラウザでのSlackアカウントログインと通知先Slackチャンネルの作成が完了していると作業がスムーズです。

## 方法

### 設定方法

1. [こちら](https://status.claude.com/)の右上の「SUBSCRIBE TO UPDATES」をクリックします（当該サイトアクセスはSlackログインが完了しているブラウザだとログイン作業等が不要なので今後の作業が楽だと思います。）

   [![CleanShot 2026-04-11 at 23.15.02.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F88b5cbfe-7724-4a11-8f88-e3cfdaf6dfff.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=af5d11f178584cd38909a5a66da8e806)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F88b5cbfe-7724-4a11-8f88-e3cfdaf6dfff.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=af5d11f178584cd38909a5a66da8e806)
2. 開いたモーダルでSlackのアイコンをクリックします

   [![CleanShot 2026-04-11 at 23.17.48.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2Fb5032199-f3ca-4a80-9ce8-251ca306743f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a58ec8cf9b6bb6af2b1c3f0465d6ce18)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2Fb5032199-f3ca-4a80-9ce8-251ca306743f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a58ec8cf9b6bb6af2b1c3f0465d6ce18)
3. 「SUBSCRIBE VIA SLACK」をクリックします

   [![CleanShot 2026-04-11 at 23.23.34.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2Ff5d48a53-431e-412f-b648-1e5708f471ea.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9b18cba46df04f13caa16b18192b0150)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2Ff5d48a53-431e-412f-b648-1e5708f471ea.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=9b18cba46df04f13caa16b18192b0150)
4. 「Workspace」のプルダウンにてSlackアプリを追加するワークスペースを選択します

   [![CleanShot 2026-04-11 at 23.24.57.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F1604fb97-8a6c-41c2-8e4e-339064b23a31.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=47080413d7d6e0bdc1948470462110a0)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F1604fb97-8a6c-41c2-8e4e-339064b23a31.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=47080413d7d6e0bdc1948470462110a0)
5. 「Webhook用のチャンネル」のプルダウンにて通知用チャンネルを選択します（筆者は「91\_notice\_claude\_status」というチャンネルを事前に作成視選択しました。）

   [![CleanShot 2026-04-11 at 23.47.09.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F55d0f2ec-57ed-4277-9598-55f2e81c9f3f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c6d4b85451656ad2202edc9b2cbafa23)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F55d0f2ec-57ed-4277-9598-55f2e81c9f3f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c6d4b85451656ad2202edc9b2cbafa23)
6. 下記のような状態になり、規約等に同意できる場合は「許可する」をクリックします

   [![CleanShot 2026-04-11 at 23.47.36.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F5d51d621-cbf1-4482-abe4-d2a63fb8f9c8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7bf01e878486036695138fb16da704e7)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F5d51d621-cbf1-4482-abe4-d2a63fb8f9c8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7bf01e878486036695138fb16da704e7)
7. ステータス情報を通知する対象サービスを選ぶ画面に遷移するので必要なものだけチェックして「SAVE」をクリックします（この設定はいつでも変更可能です。）

   [![CleanShot 2026-04-11 at 23.50.03.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F3bffd466-cb53-4659-aebb-330c7f00b910.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=50d3d1ef599d0f15d137d7c10b636f1d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F3bffd466-cb53-4659-aebb-330c7f00b910.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=50d3d1ef599d0f15d137d7c10b636f1d)
8. 画面上部に「Component subscriprion saved!」と表示されればブラウザ側での設定は完了です

   [![CleanShot 2026-04-11 at 23.50.37.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F8f0277d2-1042-4d13-b7fd-0b66224633b6.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=21ea457ce4ac179f02673eac2dc18667)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F8f0277d2-1042-4d13-b7fd-0b66224633b6.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=21ea457ce4ac179f02673eac2dc18667)
9. Slackの通知設定チャンネルに下記の様に出ていればSlack側でも正常に設定が完了しています

   [![CleanShot 2026-04-11 at 23.52.22@2x.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F29081644-8bf5-4f20-b5de-6d15259af077.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=766d7d8a22be0be06b4f5d9a518ab2ee)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F29081644-8bf5-4f20-b5de-6d15259af077.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=766d7d8a22be0be06b4f5d9a518ab2ee)
10. 後は障害発生時等に通知が行われるはずです

### ステータス情報を通知する対象サービスの変更

1. 「ステータス情報を通知する対象サービスの変更」はSlackに最初にアプリから投稿された「Manage Notifications」をクリックします

   [![CleanShot 2026-04-11 at 23.56.31@2x.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F0a87c7ea-8cbd-4482-9ca4-686e930096b7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6acb96fc028ffb2daaf7347f061af52d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F0a87c7ea-8cbd-4482-9ca4-686e930096b7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6acb96fc028ffb2daaf7347f061af52d)
2. 再度下記の画面が開き設定を変更する事ができます

   [![CleanShot 2026-04-11 at 23.57.59.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F1eaedadb-1d96-41c0-85e6-a34c37eac678.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cfbb20a9385e590a68d303b6d06f2e65)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2F1eaedadb-1d96-41c0-85e6-a34c37eac678.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cfbb20a9385e590a68d303b6d06f2e65)

前述の対象サービス選択画面は[こちら](https://status.claude.com/)から前述の「設定方法」に記載の方法を再度実施することでもアクセス可能でした。（ワークスペースとチャンネル選択後に「すでに追加済み」のエラー表示はされますが対象サービス選択画面へはアクセスできます。）

[![CleanShot 2026-04-12 at 00.05.05.gif](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2Ff2915ab3-6dc4-4092-992d-f9b4babc9fd5.gif?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0bc0772c2571ba7f164bf2c78de92b86)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F306417%2Ff2915ab3-6dc4-4092-992d-f9b4babc9fd5.gif?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=0bc0772c2571ba7f164bf2c78de92b86)
