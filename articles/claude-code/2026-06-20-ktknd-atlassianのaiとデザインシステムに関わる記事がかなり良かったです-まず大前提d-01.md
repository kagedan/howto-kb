---
id: "2026-06-20-ktknd-atlassianのaiとデザインシステムに関わる記事がかなり良かったです-まず大前提d-01"
title: "@ktknd: AtlassianのAIとデザインシステムに関わる記事がかなり良かったです。 まず大前提、DESIGN.mdは、デザイ"
url: "https://x.com/ktknd/status/2068156556513050971"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "AI-agent", "x"]
date_published: "2026-06-20"
date_collected: "2026-06-21"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

AtlassianのAIとデザインシステムに関わる記事がかなり良かったです。

まず大前提、DESIGN.mdは、デザインシステムの文脈をMarkdownで持ち運ぶための形式。

色、タイポグラフィ、余白、コンポーネントの考え方などを1つのファイルにまとめてAIに渡すことで、生成されるUIがそのプロダクトらしくなりやすい。

いわば「AIに渡せる、ポータブルなデザインシステムの説明書」です。

実際、AtlassianもTeam ’26のデモで試したところ、DESIGN.mdなしだと汎用的だったUIが、DESIGN.mdを渡すことで色、余白、形、タイポグラフィ、elevationなどがAtlassianらしいUIに近づいたそうです。

プロトタイプ、新しいAIデザインツール、外部環境、顧客ごとのブランドを反映したダッシュボード生成。こういう用途では、DESIGN.mdはかなり強い。

ただ、この記事の本質はその先。

本番コードベースでDESIGN.mdを唯一のデザインシステム文脈として使うと、MCP serverやskillsよりトークン消費が増え、時間もかかり、結果のばらつきも大きくなった。

もちろん、これは研究論文ではないので数字だけを一般法則として受け取るべきではありません。でも、示している方向性は重要です。

DESIGN.mdは入口として便利。でも、大規模なデザインシステムをAIに扱わせるには、1枚のMarkdownに全部詰めるだけでは足りない。

本質は「文脈のルーティング」です。(CLAUDE.mdでもそうなように。後述します)

Buttonを作るならButtonの仕様だけ。Tableを作るならTableの仕様だけ。実装後はlintやtype checkで確認する。必要な文脈を、必要なタイミングで、必要な粒度でAIに渡す。

既存のデザインシステムがある場合、AIにコンポーネントを「再現」させたいわけではありません。既存のButtonを正しく使ってほしい。

既存コンポーネントを使うから、保守できる。一箇所の変更が全体に反映される。レビューもしやすい。デザインシステムの意味が残る。

だから、DESIGN.mdはSource of Truthというより、Export Formatとして見るのがよさそうです。

Source of Truthは、デザイントークン、コンポーネントコード、Figma、実装ドキュメント、lint rules、skills、MCP server側にある。DESIGN.mdは、そこから外部ツールやプロトタイプ環境に持ち出すためのスナップショット。

これはClaude CodeのCLAUDE.mdの話とも似ています。

常に必要な情報はCLAUDE.mdに置く。特定作業の手順はskillsに分ける。決定論的に守らせたいことはhooksやlintにする。必要な情報はMCPで取りにいけるようにする。

デザインシステムでも同じです。

常に必要なブランドの大枠はDESIGN.mdに置く。正確な値はtokensやcontractsに置く。コンポーネントごとの使い方は必要なときに取りにいく。禁止パターンはlintやCIで検出する。

この記事を読んでいて、melta-uiもかなり近い思想を体現しているように感じました。

melta-uiは、DESIGN.mdを入口にしつつ、正確な値やルールはdesign/contracts/に置いている。コンポーネント仕様はJSON contractになっていて、MCPで必要な情報だけ取得できる。生成後はcheck_htmlやCIで検証する。CLAUDE.mdも薄く保ち、Claude Code固有の設定だけを書く。

まさに「1枚のMarkdownに全部詰める」のではなく、「AIが必要な文脈へ辿り着けるようにする」設計です。

これからのデザインシステムは、人間が読むドキュメントであり、人間が使うコンポーネント集であり、同時にAI agentが参照するcontext engineにもなる。

AIにデザインを再現させる方法は、1枚の完璧なMarkdownを作ることではなく、文脈の通り道を設計することなんだと思います。
https://t.co/QNwia7YIye

melta UIはこれです。

https://t.co/XbBYSzUeUS
