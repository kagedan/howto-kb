---
id: "2026-04-02-railsプロジェクトでハーネスエンジニアリングを実践しclaude-codeのルールを設計した話-01"
title: "Railsプロジェクトでハーネスエンジニアリングを実践し、Claude Codeのルールを設計した話"
url: "https://zenn.dev/dely_jp/articles/ccdf9b4cf2183f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

はじめに
こんにちは、クラシルでレシチャレの開発をしているkiyokuroです。
今回は、RailsプロジェクトでClaude Codeのルールファイル群を設計・構築した取り組みについて紹介します。
Claude Codeを日常的に使って開発していてセッションごとに設計提案や実装スタイルのブレが気になっていました。例えばあるセッションではサービスクラスにキーワード引数を使う実装を提案し、別のセッションでは位置引数で書いてくる。同じプロジェクトなのに、Claudeの提案に一貫性がありませんでした。
この問題を解決するために「ハーネスエンジニアリング」の概念を調査し、実際にルールファイル...
