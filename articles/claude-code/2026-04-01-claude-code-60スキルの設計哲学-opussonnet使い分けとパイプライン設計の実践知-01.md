---
id: "2026-04-01-claude-code-60スキルの設計哲学-opussonnet使い分けとパイプライン設計の実践知-01"
title: "Claude Code 60+スキルの設計哲学 — Opus/Sonnet使い分けとパイプライン設計の実践知"
url: "https://zenn.dev/takish/articles/skill-philosophy"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-04-01"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

60以上のスキルを破綻させない5つの設計原則
Claude CodeにはAgent Skills（エージェントスキル）という仕組みがあります。YAMLフロントマター付きのMarkdownファイルを1つ書くだけで、AIの振る舞いを定義できる機能です。最初の数個は直感で作れます。「コードレビュー用」「コミット用」「実装用」——用途ごとにスキルを分ければいい、それだけの話です。
しかし10個、30個、60個と増えるにつれて、設計判断が積み重なっていきます。「このスキルはOpus（高性能モデル）とSonnet（高速モデル）のどちらで動かすべきか？」「レビュー系スキルにBash実行を許可すべ...
