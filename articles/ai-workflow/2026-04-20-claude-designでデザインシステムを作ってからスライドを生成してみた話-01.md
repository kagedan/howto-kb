---
id: "2026-04-20-claude-designでデザインシステムを作ってからスライドを生成してみた話-01"
title: "Claude Designでデザインシステムを作ってからスライドを生成してみた話"
url: "https://qiita.com/ogaryo/items/7b3136fd2a8efe7a1a83"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

## はじめに
Claude Design みなさん試しましたか？
もちろん私も試しました。
一先ず、適当な仮PJの画面をリデザインしてもらって満足していたんですが、
このClaude Design、スライドも作れるんです。

元々NoteBookLMを使ってスライドを作成していたんですが、細かな修正がしづらく、結局Reactで作った自作スライドを使ってました。

ですが、Claude DesignにはEditモードがあるじゃないですか！
しかもデザインシステムとしてスライドのテンプレート（テーマ）も作ってもらえて、流用できる…！

これは良さそうだと思いさっそくスライドを作ってみました。
## Claude Designってなに？

Claude Designは Anthropic 公式のAIデザインツールです。

https://claude.ai/design

チャット形式でUI・資料・スライドを生成できます。
「指示書を書くだけでデザインが出てくる」体験をAnthropicのエコシステムの中で完結させようとしているイメージです。

特徴をざっくりまとめると：
- チャットで指
