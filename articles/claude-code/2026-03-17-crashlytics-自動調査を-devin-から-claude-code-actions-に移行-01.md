---
id: "2026-03-17-crashlytics-自動調査を-devin-から-claude-code-actions-に移行-01"
title: "Crashlytics 自動調査を Devin から Claude Code Actions に移行できるか検証"
url: "https://qiita.com/mgre_tanabe/items/b9c2230c5cb343365876"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## はじめに

> 注: 本記事の料金・モデル・機能の比較は 2026年3月時点 のものです。AIエージェントの進化は非常に速く、料金改定や新モデルのリリースで状況が変わる可能性があります。最新の情報は各サービスの公式ドキュメントをご確認ください。

[前回の記事](https://qiita.com/mgre_tanabe/items/74752d1ba32b54fad954)では、Devin + GitHub Actions で Crashlytics クラッシュ調査を自動化する仕組みを紹介しました。検知から調査・判定までを自動化し、エンジニアの一次調査工数をゼロにできた一方で、運用を続ける中で コストが課題になってきました。

前回記事では1件あたり約2ACU（数百円相当）と紹介しました。Devin の Billing ダッシュボードで実ACUを確認したところ、平均約2.5ACU/件（1.1〜3.4の幅あり）でした。前回記事の見積もりよりやや重く、PR作成を含むケースで特にACUが増える傾向があります。実作業時間は 10〜20分程度（スタックトレースN/Aの簡易調査で約10分、
