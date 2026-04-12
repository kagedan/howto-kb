---
id: "2026-04-10-figma-makeのモックアップをclaudeが全然再現してくれないので一発で解決するchrome-01"
title: "Figma MakeのモックアップをClaudeが全然再現してくれないので、一発で解決するChrome拡張を作った。"
url: "https://zenn.dev/t09tanaka/articles/0822a50701f0e6"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

悩み: Claude CodeがFigma Makeを全然再現してくれない問題
Figma Makeなどで生成したデザインモックアップを、実際のコードに落とし込む作業を行うことが度々あります。しかし、Claude CodeにURLを渡したりモックアップのファイルを渡しただけではデザインの再現がどうしてもうまくいきません。

背景色が無視される
ボーダーが無視される
フォントスタイルが無視される
など

修正項目が多すぎて結局手作業と変わらないような時間がかかっていました。

 原因: 描画に必要な情報が分散しているから
モックアップをClaudeに渡す方法は複数ありますが、どの手法で...
