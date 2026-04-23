---
id: "2026-04-23-非エンジニアでも利用できる-claude-design-で-lt-会の告知-lp-を作ってみる-01"
title: "非エンジニアでも利用できる Claude Design で LT 会の告知 LP を作ってみる"
url: "https://qiita.com/leomarokun/items/81101a9afa181d526948"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-23"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

## はじめに

2026年4月17日 Anthropic Labs から発表された **[Claude Design](https://www.anthropic.com/news/claude-design-anthropic-labs)** を触ってみました。

本記事は **実際の題材を1本決めて、プロンプト投入から仕上げまでを時系列で追う**形で進めてみます。
読みながら「こういうことに使える、こういうこともできるかもな」とイメージを持てたら目的達成です。

## Claude Design とは

Claude Design は Claude Opus 4.7 を内部で動き、会話しながらビジュアルを作り込めるツールです。Claude Design は **Web 版（`claude.ai/design`）**で利用可能ですう。

## 今回作るもの

具体的な題材が無いと操作の話がふわっとしてしまうので、以下の架空イベントを想定します。

**架空の社内 LT 会「AI Lab Meetup Tokyo #3」の告知 LP**

| 項目 | 設定 |
|---|---|
