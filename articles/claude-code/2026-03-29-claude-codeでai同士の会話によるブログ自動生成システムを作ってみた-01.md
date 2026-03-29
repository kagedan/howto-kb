---
id: "2026-03-29-claude-codeでai同士の会話によるブログ自動生成システムを作ってみた-01"
title: "Claude Codeで「AI同士の会話」によるブログ自動生成システムを作ってみた"
url: "https://qiita.com/kenji_harada/items/58b8dbb395199bbe9f1e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "GPT", "qiita"]
date_published: "2026-03-29"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

この記事は自社ブログ([nands.tech](https://nands.tech/posts/claude-code-ai-to-ai-blog-auto-generation-714286))の要約版です

## なぜAI1つじゃダメなのか？

最近Claude Codeで面白いシステムを作った話を書こうと思う。

いきなりだが、AIに記事を1回で完璧に書かせるのは無理ゲーだと思っている。ChatGPTもClaudeも、ワンショットで長文を生成すると「情報てんこ盛りだけど、なんか読む気しない」記事ができあがる。

理由は明確で、AIには「何を削るか」の判断ができないから。全部重要に見えて、結果として誰の心にも刺さらない平坦な文章になってしまう。

じゃあどうするか。人間の編集現場を真似すればいい。

ライターが記事を書く → 編集者が「ここ薄い」「この表現微妙」と指摘 → ライターが修正 → また編集者が見る...

これをAI同士でやらせるのが今回のアプローチだ。

## Claude Code Channelsの威力

2026年3月にリリースされた「Claude Code
