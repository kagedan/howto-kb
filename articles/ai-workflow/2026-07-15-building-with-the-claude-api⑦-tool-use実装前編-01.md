---
id: "2026-07-15-building-with-the-claude-api⑦-tool-use実装前編-01"
title: "Building with the Claude API⑦ | tool use実装（前編）"
url: "https://note.com/konitan_ai/n/ne3840172f6b6"
source: "note"
category: "ai-workflow"
tags: ["API", "note"]
date_published: "2026-07-15"
date_collected: "2026-07-15"
summary_by: "auto-rss"
query: ""
---

この記事は、有料マガジン「Claude検定：Building with API」の1本です。Claude APIで作るための全11レッスンを、マガジン（¥1,980）でまとめて読めます。Anthropic公式の修了クイズ「Claude検定」に日本語で備えるための一冊です。

<https://note.com/konitan_ai/m/m2a0f30242e35>

> Claudeに道具を持たせるtool useの前編です。ツールにする関数の書き方、Claudeへ渡すschema、text＋tool\_useが混在する応答の扱い方を実装します。この記事は、Anthropic公式コース「Building with the Claude API」の第7回を、原典を読まなくても学べる日本語教材として書き直したものです。シリーズの入口は[はじめに](https://note.com/konitan_ai/n/nbb4b9f79ebda)、全体の地図は[対策マップ](https://note.com/konitan_ai/n/nd267433454ab)から。

このレッスンを終えると、次の4つができるようになります。

1. tool関数を実装の作法（検証・エラーメッセージ）込みで書ける
2. tool schemaを書ける（Claudeに書かせる近道も知っている）
3. multi-blockの応答（text＋tool\_use）を正しく扱える
4. tool\_resultをIDで対応づけて返せる

所要時間の目安は30分です。
