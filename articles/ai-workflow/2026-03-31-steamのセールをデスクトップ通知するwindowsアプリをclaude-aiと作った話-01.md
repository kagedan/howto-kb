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
SaleSentry — Steamのウィッシュリストを監視してデスクトップ通知を送るWindowsアプリです。良ければ使ってください。https://github.com/momohir1919-dotcom/SaleSentry

![SaleSentry](https://github.com/user-attachments/assets/6c0799b0-a5bf-4fd6-b3aa-71bac369a971)

価格データはIsThereAnyDeal APIを使用しています。

## 機能
以下の感じで機能で実装してみました。ゲームごとに以下の条件を個別に設定できます。

過去最安値
最安値を更新したら通知
