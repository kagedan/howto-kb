---
id: "2026-04-30-claude-code-で-path-を使うか-read-させるか-01"
title: "Claude Code で @path を使うか Read させるか"
url: "https://zenn.dev/zozotech/articles/4b13d2ce563c9f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-30"
date_collected: "2026-05-01"
summary_by: "auto-rss"
---

はじめに
Claude Code でファイルを参照する方法には、大きく分けて 2 つある。

@path でユーザーが明示的に注入する
エージェント（Read ツール）に判断させて読ませる

@ は手軽だが、無自覚に使うとコンテキストを圧迫しやすい。本稿では公式ドキュメントを根拠に、両者の挙動と使い分けを整理する。

 TL;DR

@path で展開した内容は、そのターン以降も会話履歴に残り続ける

@dir/ はディレクトリ「リスト」を返すだけで、中身を全展開するわけではない
コンテキストが肥大化すると指示遵守率が下がることは公式が明記している
大きいファイル・部分参照で済む場...
