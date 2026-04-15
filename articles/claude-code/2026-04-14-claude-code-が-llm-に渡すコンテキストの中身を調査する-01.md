---
id: "2026-04-14-claude-code-が-llm-に渡すコンテキストの中身を調査する-01"
title: "Claude Code が LLM に渡すコンテキストの中身を調査する"
url: "https://qiita.com/megmogmog1965/items/2fe6c20e9ea0f4ca89b6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

## はじめに

Claude Code は CLI ツールですが、裏で動いているのは Anthropic の LLM（Claude）です。ターミナルで入力した文字列や、実行したツールの結果は、そのままの形で LLM に届くわけではありません。Claude Code 本体（以下「ハーネス」と呼びます）が整形・注入・ラップをしてから、1 本のメッセージ履歴として LLM に渡しています。

この記事のテーマは「**どんなシチュエーションで、LLM にはどんな原文メッセージが渡されているのか**」を具体的に解析することです。例えば、ユーザーがプロンプトを入力したとき、Skills や Subagent を起動したとき、ツールを実行したとき、hook が発火したとき——それぞれの場面で `Messages` コンテキスト・カテゴリに流れ込む原文はどう違うのか。実測で確かめていきます。

進め方は次の 3 段です。

1. まず公式ドキュメントの **エージェントループ** を概観し、Claude Code の動作モデルを押さえる
2. `/context` コマンドで見えるカテゴリ別の使用量
