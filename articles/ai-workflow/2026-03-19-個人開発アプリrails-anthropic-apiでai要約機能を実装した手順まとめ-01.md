---
id: "2026-03-19-個人開発アプリrails-anthropic-apiでai要約機能を実装した手順まとめ-01"
title: "【個人開発アプリ】Rails × Anthropic APIでAI要約機能を実装した手順まとめ"
url: "https://qiita.com/masa_tech_0326/items/9506e0ca3c975f308e9d"
source: "qiita"
category: "ai-workflow"
tags: ["API", "qiita"]
date_published: "2026-03-19"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

## はじめに

個人開発をしているRailsアプリ「[MabaTalk](https://mabatalk.com/)」では、利用者のメッセージ履歴をログとして蓄積しています。

しかし、ログが増えるにつれて「どのような傾向があるのか」を人手で振り返ることが難しくなるという課題がありました。

そこで、Anthropic APIを利用し、ログの内容を**AIで要約する機能**を実装しました。


本記事では、AI要約機能の実装手順に加えて、外部APIとの連携処理をService Objectとして切り出し、Controllerの責務を肥大化させない設計についても解説します。

RailsでAI機能を組み込んでみたい方の参考になれば幸いです。


MabaTalkを開発した背景は下記note記事で紹介しています。

["伝えたいのに伝えられない"を減らしたい。未完成のまま「MabaTalk」を公開しました。](https://note.com/prime_snail5740/n/n02d9f797d46a?from=notice)


## 想定読者

- Railsで外部API連携を
