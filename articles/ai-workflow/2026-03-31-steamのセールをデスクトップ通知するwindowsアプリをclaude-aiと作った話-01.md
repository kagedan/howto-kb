---
id: "2026-03-31-steamのセールをデスクトップ通知するwindowsアプリをclaude-aiと作った話-01"
title: "Steamのセールをデスクトップ通知するWindowsアプリをClaude AIと作った話"
url: "https://qiita.com/momohir/items/d950f37de798515c7526"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

## なぜ作ったか

Steamのセールって、私みたいに普段Steam自体を落としている人は気づかないですよね。ITADのメールアラートも仕事用と個人用でアカウントを分けていると、気づいたらセールが終わっていた……ということが何度もありました。

「ブラウザもメールも見なくていい、デスクトップに直接通知が来るアプリが欲しい」と思ったので作りました。

## 作ったもの

SaleSentry — Steamのウィッシュリストを監視してデスクトップ通知を送るWindowsアプリです。良ければ使ってください。<https://github.com/momohir1919-dotcom/SaleSentry>

[![SaleSentry](https://qiita-user-contents.imgix.net/https%3A%2F%2Fgithub.com%2Fuser-attachments%2Fassets%2F6c0799b0-a5bf-4fd6-b3aa-71bac369a971?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4b35c4807548103095c0d6549d41d222)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fgithub.com%2Fuser-attachments%2Fassets%2F6c0799b0-a5bf-4fd6-b3aa-71bac369a971?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4b35c4807548103095c0d6549d41d222)

価格データはIsThereAnyDeal APIを使用しています。

## 機能

以下の感じで機能で実装してみました。ゲームごとに以下の条件を個別に設定できます。

過去最安値  
最安値を更新したら通知します。

セール開始  
割引が始まったタイミングで１度だけ通知するセール開始通知機能

目標価格  
「○○円以下になったら買う」という価格を設定しておくと、その価格を下回ったときに通知。

割引率  
「50%以上割引になったら通知」という設定もできます。セールが終了する24時間前に、終了24時間以内になったら1度だけ終了通知を出してくれる機能もつけてみました。

定価が歴史的最安値と同じゲームは除外しています。

通知抑制時間  
22時〜9時など日をまたぐ時間帯も正しく動作します。設定した時間は通知が来ません。

ウィッシュリスト自動インポート  
SteamIDを設定するだけでウィッシュリストを自動取得。100件超でも50件ずつバッチ処理するのでレート制限に引っかかりません。

多言語対応  
EN / JA / ZH / RU / FR に対応。OSのロケールから自動判定します。

技術スタック  
Electron 30  
IsThereAnyDeal API（価格データ）  
Steam Web API（ウィッシュリスト取得）  
node-fetch

技術スタックはすべてClaudeに提案してもらいました。

## 終わりに

プログラミングはほぼ未経験です。Claude Pro（契約時レートで月約3,200円）を使って、ほぼ会話しながら作りました。作ってる最中は特に詰まることはありませんでした。強いて言えば不具合を何回も探させました。もっと効率のいいやり方があるんでしょうか・・・

その他はAPIの使用量上限に引っかかって何度も中断したくらいです。

「こういう機能が欲しい」と伝えると実装してくれて、エラーが出たらログを貼ると直してくれる。このサイクルで完成まで持っていけました。

「AIで開発してみたいけど自分にできるか不安」という方の参考になれば。
