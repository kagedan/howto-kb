---
id: "2026-06-26-anthropic-sdk-v01120python-v01060typescriptリリース-スト-01"
title: "Anthropic SDK v0.112.0（Python）/ v0.106.0（TypeScript）リリース — ストリーミングでシステムメッセージが届くようになった！"
url: "https://qiita.com/kinamocchi_tech/items/01085926c236613f597a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "Python", "TypeScript", "qiita"]
date_published: "2026-06-26"
date_collected: "2026-06-26"
summary_by: "auto-rss"
query: ""
---

# Anthropic SDK v0.112.0（Python）/ v0.106.0（TypeScript）リリース — ストリーミングでシステムメッセージが届くようになった！

:::message
この記事は **きなこ（🦜 セキセイインコ・テック解説担当）** と **もっちー（🐹 ハムスター・初心者代表）** の掛け合い形式でお届けします。飼い主の不在中に2匹が技術情報をわかりやすく解説する「きなこもっちーのテック深掘り」チャンネルの速報コーナーです。
:::

![Anthropic SDK v0.112 / v0.106 リリース速報インフォグラフィック](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/infographics/news/anthropic-sdk-0112_graphreco.png)

**公開日**: 2026年6月24日
**一次ソース**: [anthropic-sdk-python v0.112.0 (GitHub Releases)](https://github.com/anthropics/anthropic-sdk-python/releases/tag/v0.112.0) / [@anthropic-ai/sdk v0.106.0 (npm)](https://github.com/anthropics/anthropic-sdk-typescript/releases/tag/sdk-v0.106.0)

---

## 速報サマリー

- 🦜 きなこ：AnthropicのSDKが6月24日にアップデートされたよ。Python v0.112.0 と TypeScript v0.106.0 がほぼ同時リリース。今回の目玉は**ストリーミング中にシステムメッセージをリアルタイム受信できる**ようになったこと！

- 🐹 もっちー：ストリーミングってメッセージが少しずつ届くやつやんな？それでシステムメッセージも受け取れるようになったん？

- 🦜 きなこ：そう！これまでシステムメッセージはレスポンス完了後にしか確認できなかったけど、`system.message` イベントとしてストリーム中に受信できるようになった。エージェント開発で中間の制御情報をリアルタイムに拾えるから、応答性がぐっと上がるね。

---

## 主な変更点

### ✨ 新機能

| 機能 | 概要 |
|------|------|
| `system.message` ストリーミングイベント | メッセージ生成中にシステムメッセージをリアルタイム受信できるようになった |
| 新しい refusal category のサポート | API が新しい拒否カテゴリを返す場合に型安全に扱えるようになった |
| リクエストヘッダーでユーザープロファイルID送信対応 | ユーザー識別情報をヘッダーに付与してリクエストできるようになった |

### 🐛 バグ修正

| 対象 | 修正内容 |
|------|---------|
| メモリツール | 親ディレクトリのパーミッション設定が誤っていた問題を修正 |

---

## 対象 SDK

| SDK | バージョン |
|-----|----------|
| Python | `anthropic v0.112.0` |
| TypeScript | `@anthropic-ai/sdk v0.106.0` |

---

## アップデート方法

```bash
# Python
pip install --upgrade anthropic

# TypeScript / Node.js
npm update @anthropic-ai/sdk
```

---

## もっちーの一言

- 🐹 もっちー：ストリーミングでシステムメッセージが取れるの、エージェント開発者には神アップデートやん！Claude Code みたいな複雑なエージェント作るときに特に使えそう。早く試してみたい🎉

---

## 公式リンク

- [anthropic-sdk-python v0.112.0 — GitHub Releases](https://github.com/anthropics/anthropic-sdk-python/releases/tag/v0.112.0)
- [@anthropic-ai/sdk v0.106.0 — GitHub Releases](https://github.com/anthropics/anthropic-sdk-typescript/releases/tag/sdk-v0.106.0)
- [Anthropic 公式ドキュメント](https://docs.anthropic.com/)

---

*きなこもっちーのテック深掘り — AIの最新情報を2匹が速報でお届け*
