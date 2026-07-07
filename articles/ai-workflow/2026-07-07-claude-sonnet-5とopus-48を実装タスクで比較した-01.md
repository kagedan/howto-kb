---
id: "2026-07-07-claude-sonnet-5とopus-48を実装タスクで比較した-01"
title: "Claude Sonnet 5とOpus 4.8を実装タスクで比較した"
url: "https://zenn.dev/localai_lab/articles/e8d6586231664e"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-07-07"
date_collected: "2026-07-08"
summary_by: "auto-rss"
query: ""
---

Claude Sonnet 5とOpus 4.8を、同じ実装タスクで比較しました。

題材はAI関連ではなく、防災備蓄管理アプリです。水・食料・簡易トイレの必要量計算、期限管理、買い足しリスト、localStorage保存、CSV出力、スマホ対応まで含めた単一HTMLアプリを作らせました。

今回の比較は、この実装タスク1本での所見です。文章作成や要約など、別のタスクでは傾向が変わる可能性があります。

## 条件

| 項目 | 内容 |
| --- | --- |
| 実行環境 | Claude Desktop |
| 比較モデル | Sonnet 5 / Opus 4.8 |
| effort | どちらもHigh |
| セッション | 毎回新規タスク |
| 出力 | 単一HTML |
| 確認 | 実ブラウザで表示確認 |

最初に同じプロンプトでアプリを生成し、その後、同じ改善指示を出しました。

## 改善指示で見たポイント

* 水を「容量 × 本数」で入力できるか
* 食料を「何食分」、簡易トイレを「何回分」として扱えるか
* 家族人数と備蓄日数から必要量を計算できるか
* 不足、期限切れ、期限間近、未登録カテゴリをリスト化できるか
* 入力バリデーションがあるか
* 既存機能を壊さないか
* スマホ幅で横崩れしないか

## 結果

点数のような厳密なベンチマークではなく、同じ条件で生成したHTMLを見比べた評価メモです。主に、指示の反映、UIのまとまり、入力バリデーション、スマホ表示、既存機能が壊れていないかを見ました。

改善指示後の画面例です。どちらも実用域ですが、画面の整理の仕方に少し違いが出ました。

![Sonnet 5 改善後のサンプル投入画面](https://res.cloudinary.com/zenn/image/fetch/s--4sf1Rx9v--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://localailab.org/wp-content/uploads/2026/07/sonnet5_v2_sample_clean.png?_a=BACMTiAE)

![Opus 4.8 改善後のサンプル投入画面](https://res.cloudinary.com/zenn/image/fetch/s--iVv-HkW4--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://localailab.org/wp-content/uploads/2026/07/opus48_v2_sample_clean.png?_a=BACMTiAE)

| 観点 | Sonnet 5 | Opus 4.8 |
| --- | --- | --- |
| 初回生成 | 実用域 | 実用域 |
| 改善後 | 水の入力が直感的 | UIの整理が自然 |

改善指示まで含めると、Opus 4.8が僅差で上でした。

理由は、アプリ全体を「使う画面」として整理する力が強かったためです。ダッシュボード、買い足しリスト、フォームのまとまりはOpus 4.8のほうが自然でした。

一方で、Sonnet 5も十分に実用域です。特に、水の「容量 × 本数」入力はSonnet 5のほうが初心者向けでわかりやすいと感じました。

## 実表示チェック

生成されたHTMLをブラウザで開き、画面崩れやエラーの有無を確認しました。

| 項目 | Sonnet 5 | Opus 4.8 |
| --- | --- | --- |
| コンソールエラー | なし | なし |
| ページエラー | なし | なし |
| サンプル投入 | 正常 | 正常 |
| 空保存時エラー | 表示あり | 表示あり |
| スマホ幅390px | 横はみ出しなし | 横はみ出しなし |

## 使い分け

Sonnet 5は、まず動くものを作る用途にかなり向いています。実装のたたき台として十分強いです。

Opus 4.8は、仕上げやUIのまとまりを上げたいときに強い印象でした。改善指示を出した後の完成品感が少し上です。

## まとめ

今回の範囲では、初回生成では大差なし、改善指示まで入れるとOpus 4.8が僅差で優勢、という結果でした。

ただし、Sonnet 5でも実用的なアプリは作れます。普段使いはSonnet 5、仕上げや重要な改善はOpus 4.8、という使い分けが現実的だと思います。

興味ある方は、画面キャプチャや細かい検証メモもあわせてどうぞ。

<https://localailab.org/claude-sonnet-5-opus-4-8-app-comparison/>
