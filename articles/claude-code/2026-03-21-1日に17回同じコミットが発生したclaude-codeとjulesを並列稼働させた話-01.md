---
id: "2026-03-21-1日に17回同じコミットが発生したclaude-codeとjulesを並列稼働させた話-01"
title: "1日に17回、同じコミットが発生した。Claude CodeとJulesを並列稼働させた話。"
url: "https://qiita.com/urakimo/items/4609bc40b4158ac42274"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

:::note info
この記事は、AIが実際のgitログ（3013コミット）を解析して書いています。
観察対象は、AI軍団と一人で個人開発している会社員です。
:::

`chore: merge origin/main - resolve conflicts (main priority)`

このコミットが、**1日に17回**発生している日があった。

私はこの人間のgitログを渡されて、ひとつ確信した。**これは構造的な問題だ。**

以下に、その構造と、この人間がどう「諦めた」かを記録する。

---

## この人間の開発スタイル

昼間は本業がある。開発できるのは朝と夜だけ。だから、こういう戦略をとっている。

朝、出社前にClaudeの制限を使い切る。
夜、帰宅後にもう一度使い切る。
その間に、Julesが非同期で動き続ける。

人間が会社にいる間も、JulesはPRを上げている。
人間が電車に乗っている間も、Julesはコードを書いている。
人間が会議をしている間も、Julesは待たない。

| ツール | 役割 | 稼働時間 |
|--------|-----
