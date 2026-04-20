---
id: "2026-04-19-個人開発のバイクサイトにanthropic-apiで2000車種のaiコンテンツを自動生成してタブu-01"
title: "個人開発のバイクサイトにAnthropic APIで2,000車種のAIコンテンツを自動生成してタブUIに載せた話"
url: "https://qiita.com/ausssxi0/items/a224ae993850c39d3f7e"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

# 個人開発のバイクサイトにAnthropic APIで2,000車種のAIコンテンツを自動生成してタブUIに載せた話

## はじめに

バイクポータルサイト「[MotoHub](https://motohub.jp)」を個人開発しています。

Google March 2026コアアップデート（3/27開始、4/8完了）の影響で、DAUがピーク420から57〜100まで急落しました。回復のために**車種モデルページと車両詳細ページを根本的に作り変えた**1週間の記録です。

やったことは大きく5つ：

1. **Anthropic APIで車種コンテンツを自動生成**（enriched_content + model_history）
2. **価格.com参考のタブ式UIに全面リニューアル**
3. **年式分布グラフ・レビュー項目別評価の追加**
4. **買取予想V2（BuybackPriceCalculator）**
5. **クイズのAPI化 + Redis 50問プール**

:::message
この記事は2026年4月時点の情報です。
:::

---

## 環境
