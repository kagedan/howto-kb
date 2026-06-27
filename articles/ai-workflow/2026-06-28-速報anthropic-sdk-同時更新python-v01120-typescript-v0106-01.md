---
id: "2026-06-28-速報anthropic-sdk-同時更新python-v01120-typescript-v0106-01"
title: "【速報】Anthropic SDK 同時更新！Python v0.112.0 / TypeScript v0.106.0 を3分で解説"
url: "https://qiita.com/kinamocchi_tech/items/cba6ddde529b06629bac"
source: "qiita"
category: "ai-workflow"
tags: ["LLM", "Python", "TypeScript", "qiita"]
date_published: "2026-06-28"
date_collected: "2026-06-28"
summary_by: "auto-rss"
query: ""
---

:::message
🐹🦜 **この記事に登場する2匹**

- 🐹 **もっちー**（ハムスター）… AI はまだ勉強中。「それどういうこと？」と素朴に質問する生徒役
- 🦜 **きなこ**（セキセイインコ）… AI で調べものをこなす解説役。やさしく深掘りして教える先生役

この記事は2匹の掛け合いを書き起こした形式です。発言の先頭にいる絵文字＋名前が話者です。
:::

## 🚀 Anthropic SDK 同時アップデートとは

もっちー：「きなこ！Anthropic の SDK が Python と TypeScript で同時にアップデートされたって聞いたけど、何が変わったの？」

きなこ：「そうなんだよ！2026年6月24日に Python v0.112.0 と TypeScript v0.106.0 が同時にリリースされたの。両方まとめて解説するね。」

## ✨ 新機能 3 つ

### 1. `system.message` ストリーミングイベント対応

きなこ：「まずは `system.message` ストリーミングイベントの対応。これはストリーミング中に system メッセージのイベントを受け取れるようになった機能なんだよ。」

もっちー：「ストリーミング中に system メッセージ？それって何が嬉しいの？」

きなこ：「リアルタイムで AI のメタ情報を取得できるから、より細かい制御ができるようになるんだよ。例えばエラーハンドリングや状態管理がスムーズになるね。」

### 2. 新しい `refusal` カテゴリ追加

きなこ：「次に新しい `refusal`（拒否）カテゴリが追加されたの。AI が応答を拒否するときのカテゴリが細かく分類されるようになったんだよ。」

もっちー：「拒否の種類が増えたんだ？使い道は？」

きなこ：「アプリ側でどんな理由で拒否されたかを判別して、ユーザーへの表示を変えたりできるよ。コンテンツポリシー系の開発がしやすくなるね。」

### 3. User Profile ID をヘッダーに送信可能に

きなこ：「3つ目は User Profile ID をリクエストヘッダーに送信できるようになったこと。ユーザーごとのトラッキングや分析がしやすくなるんだよ。」

もっちー：「企業向けな感じがするね！」

## 🐛 バグ修正

### Python: Memory ツールの親ディレクトリ パーミッション修正

きなこ：「Python 版では Memory ツールで親ディレクトリのパーミッション問題が修正されたよ。Memory 機能を使ってた人は安心して。」

### TypeScript: `x-stainless-helper` 単一ソース化

きなこ：「TypeScript 版では `x-stainless-helper` ヘッダーが単一ソースに整理されたの。内部的な整合性が上がってより安定するよ。」

## 📌 まとめ

もっちー：「両方同時にアップデートされるって珍しいんじゃない？」

きなこ：「確かに珍しいよ。Python も TypeScript も使ってる人はどちらも更新しておいてね。特に新しいストリーミングイベントは早めに試してみると面白いと思う！」

---

**公式リリースノート**
- Python v0.112.0: https://github.com/anthropics/anthropic-sdk-python/releases/tag/v0.112.0
- TypeScript v0.106.0: https://github.com/anthropics/anthropic-sdk-js/releases/tag/v0.106.0

## 📌 公式一次ソース

> [【速報】Anthropic SDK 同時更新！Python v0.112.0 / TypeScript v0.106.0 を3分で解説](https://github.com/anthropics/anthropic-sdk-python/releases/tag/v0.112.0)

公式発表の詳細はリンク先をご確認ください。

---

> 🦜 **きなこもっちーのテック深掘り** では、AI・LLM を中心とした最新テックをハムスターのもっちーと セキセイインコのきなこの掛け合いで深掘り解説しています。チャンネル登録してお待ちください！
