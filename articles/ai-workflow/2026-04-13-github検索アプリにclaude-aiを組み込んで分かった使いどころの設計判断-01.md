---
id: "2026-04-13-github検索アプリにclaude-aiを組み込んで分かった使いどころの設計判断-01"
title: "🔍GitHub検索アプリにClaude AIを組み込んで分かった、使いどころの設計判断"
url: "https://zenn.dev/yumazd/articles/4324440fc3c7ec"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

はじめに
とある用事でGitHub リポジトリを検索・閲覧できる Web アプリを Next.js 16（App Router）で作りました。その中で Claude AI を3箇所に組み込んだのですが、「どこに・いつ・どう入れるか」の設計判断が一番難しく、学びも多かったので共有します。
https://github.com/yumazd/search-github


 技術スタック



カテゴリ
技術




フレームワーク
Next.js 16 (App Router) / React 19 / TypeScript


スタイリング
Tailwind CSS 4 / shad...
