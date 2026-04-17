---
id: "2026-04-16-革命寝てる間もclaudeが働くroutinesでaiを24時間自動運転する完全ガイド-01"
title: "【革命】寝てる間もClaudeが働く！「Routines」でAIを24時間自動運転する完全ガイド"
url: "https://qiita.com/emi_ndk/items/116c1703e44bcfbc9b69"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

**「毎晩2時にバグを自動で直して、朝起きたらPRが届いてる」**

これ、もう夢じゃない。

2026年4月14日、Anthropicが**Claude Code Routines**を発表した。これはマジでゲームチェンジャーだ。

## 結論から言うと...

:::note info
Claude Codeが**クラウド上で24時間365日**、あなたの代わりにコードを書き続ける。しかも**ラップトップを閉じても**動く。
:::

「え、それってGitHub Actionsと何が違うの？」

全然違う。**AIがコードを理解して、自分で判断して、PRまで作る**んだ。

## Routinesとは何か？3つのトリガータイプ

Routinesには3種類のトリガーがある：

### 1. 🕐 Scheduled（スケジュール実行）

```
毎晩2時 → Linearから最優先バグを取得 → 修正を試みる → Draft PRを作成
```

cronジョブのAI版だと思ってほしい。ただし、このcronは**コードを理解している**。

### 2. 🔗 API（HTTP POS
