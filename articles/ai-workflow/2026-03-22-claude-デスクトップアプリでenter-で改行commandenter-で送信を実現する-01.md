---
id: "2026-03-22-claude-デスクトップアプリでenter-で改行commandenter-で送信を実現する-01"
title: "Claude デスクトップアプリで「Enter で改行、Command+Enter で送信」を実現する"
url: "https://qiita.com/nate3870/items/51b196de9a07717d3952"
source: "qiita"
category: "ai-workflow"
tags: ["GPT", "qiita"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

## はじめに

Claude の Web 版を使っていたとき、Chrome 拡張機能「[ChatGPT Ctrl+Enter Sender](https://github.com/masachika-kamada/ChatGPT-Ctrl-Enter-Sender)」を愛用していた。Enter で改行、Ctrl+Enter で送信という操作に慣れると、もう Enter 一発送信には戻れない。

ところが Claude デスクトップアプリに移行したところ、Chrome 拡張機能は当然使えない。デスクトップアプリは Enter 単体でメッセージが送信されてしまうため、**長文を書いている途中で誤送信**してしまうことが何度かあった。

そこで、macOS のネイティブ機能だけを使って同等の動作を実現するツール **ClaudeRemap** を作成した。

:::note info
本記事は macOS 専用です。
:::

---

## 作ったもの

**ClaudeRemap** — Claude デスクトップアプリ専用のキーボードリマッパー。

| キー操作 | 動作 |
|--
