---
id: "2026-04-17-今日のclaude-code-v21112-リリース毎日changelog解説-01"
title: "今日のClaude Code v2.1.112 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/6a21a6b76828fc7529af"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-17"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.112 はホットフィックス1件のみ。Auto modeでOpus 4.7が使えなかった可用性の不具合修正です。

## 今回の注目ポイント

1. **Auto mode + Opus 4.7の可用性修正** - 4時間前リリースの v2.1.111 で入った組み合わせの不具合を即日で潰したパッチ

---

## Auto modeでOpus 4.7が引けない問題を修正

:::note info
対象読者: Maxプラン契約者でAuto modeを常用しているユーザー
:::

1つ前の v2.1.111 で、Maxサブスクライバー向けのAuto modeがOpus 4.7を使うようになりました。xhighというeffort levelも追加され、Auto mode自体も `--enable-auto-mode`
