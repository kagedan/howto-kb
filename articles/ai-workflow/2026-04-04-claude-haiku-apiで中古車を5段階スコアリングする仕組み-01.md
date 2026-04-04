---
id: "2026-04-04-claude-haiku-apiで中古車を5段階スコアリングする仕組み-01"
title: "Claude Haiku APIで中古車を5段階スコアリングする仕組み"
url: "https://qiita.com/bit-sap/items/cc5b41aacb3d0f11ab98"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-04-04"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

## はじめに

[中古車ウォッチ](https://car-watch.jp/)という、中古車サイト15社を自動巡回してLINEに新着通知するサービスを個人開発しています。

新着が見つかるたびに、**Claude Haiku APIで車両を分析し、5段階スコアをつけてLINEに通知**します。スコア5の「要チェック」物件だけ見れば、毎日何十件もの新着を全部チェックする必要がなくなります。

この記事では、スコアリングの仕組みとClaude APIの使い方、月$2-3で運用するコスト設計を紹介します。

## 通知の実例

LINEに届く通知はこんな感じです：

```
🎯 トヨタ プリウス 1.8 S
  ★★★★★ 🔥 要チェック
  💰 185万円
  📏 走行2.3万km / 2021年式
  🔧 車検2026年8月
  📊 価格は下位25%の割安ゾーン
  💡 ✓低走行、高年式、車検長い
  💡 △修復歴あり
  💡 中央値220万円比-16%
  💡 🤖 修復歴ありだが走行2.3万kmで車検も長く、
     同条件比-16%は割安。内容次第で買い
  🔗 https:/
