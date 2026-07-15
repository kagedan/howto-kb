---
id: "2026-07-15-building-with-the-claude-api⑧-tool-use実装後編-01"
title: "Building with the Claude API⑧ | tool use実装（後編）"
url: "https://note.com/konitan_ai/n/nc9267d9170ac"
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

> tool useの後編です。ツールを頼まなくなるまで回す会話ループをstop\_reasonを軸に組み、組み込みツールの「仕様だけ組み込み」と「実行まで込み」の二段階の違いを整理します。この記事は、Anthropic公式コース「Building with the Claude API」の第8回を、原典を読まなくても学べる日本語教材として書き直したものです。シリーズの入口は[はじめに](https://note.com/konitan_ai/n/nbb4b9f79ebda)、全体の地図は[対策マップ](https://note.com/konitan_ai/n/nd267433454ab)から。

このレッスンを終えると、次の4つができるようになります。

1. stop\_reasonを軸にした会話ループを実装できる
2. 複数ツールのルーティングとエラー処理を書ける
3. 組み込みツール（text editor / web search）の特殊な性質を説明できる
4. tool useとstreamingの合流点（fine-grained tool calling）を理解できる

所要時間の目安は30分です。
