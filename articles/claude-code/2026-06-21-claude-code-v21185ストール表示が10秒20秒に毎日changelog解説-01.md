---
id: "2026-06-21-claude-code-v21185ストール表示が10秒20秒に毎日changelog解説-01"
title: "Claude Code v2.1.185｜ストール表示が10秒→20秒に｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/9cafe58f1e98d3af2599"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-06-21"
date_collected: "2026-06-21"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.185 はストール表示まわりの 1 点だけ。API の応答を待っているときに出るヒントが、文言と発火タイミングの両方で変わった。10 秒の沈黙で出ていた警告が 20 秒まで引き延ばされ、文面も「応答なし」から「応答待ち」へトーンダウンしている。

## 今回の注目ポイント

1. **ストール表示の発火が 10 秒 → 20 秒に** API 無応答ヒントが出るまでの猶予が倍に。長考や大きめコンテキストの初回トークン待ちで誤発火しにくくなる (v2.1.185)
2. **文言が「No response」から「Waiting」へ** エラーに見える `No response from API` を、正常な待機を示す `Waiting for API response` に置き換え (v2.1.185)

## 表示文言はこう変わった

変更前後を並べるとこうなる。

```diff
- No response from API · Retrying in …
+ Waiting for API response · will retry in …
```

`No response from API` は字面が完全にエラー。実際にはサーバーが応答を組み立てている最中でも出るので、「落ちたのか?」と身構える表示だった。`Waiting for API response · will retry in …` なら、待っているだけで自動リトライも入ると読める。内部の挙動は変わっていない。変えたのは伝わり方だけ。

## 「10 秒で警告」が早すぎた問題

長いプロンプトや大きなコンテキストを投げると、最初のトークンが返るまで 10 秒を超えることは珍しくない。旧版はその 10 秒の沈黙でストール表示を出していたため、正常に処理が進んでいる最中に「応答なし」が点灯していた。要は誤発火。

閾値が 20 秒になったことで、この空振りが減る。本当に詰まったときだけ表示が出るようになった。changelog の原文でも発火条件をこう書いている。

> triggers after 20s of silence instead of 10s

表示が出ないあいだも処理は走っているので、待ちの長いプロンプトでも途中で手を止めずに済む。

:::note info
対象読者: 大きめのコンテキストや重いツール実行で、たまに「応答なし」表示を見て手を止めていた人。
:::

## まとめ

v2.1.185 は機能追加ではなく、待ち時間の見せ方を整えた 1 リリース。発火は 10 秒から 20 秒へ、文言は「応答なし」から「応答待ち」へ。表示が変わっても、内部のリトライ挙動そのものは変わっていない。
