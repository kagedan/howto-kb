---
id: "2026-04-21-bunwebview-で作る軽量e2eテスト基盤-claude-codeとの連携で画面テスト証跡取得-01"
title: "Bun.WebView で作る軽量E2Eテスト基盤 ― Claude Codeとの連携で画面テスト・証跡取得まで自動化"
url: "https://zenn.dev/omeroid/articles/df728f3a985b8e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

はじめに
Vue 3 + Element Plus で構築した業務システムのE2Eテストを、Bun + Bun.WebView というミニマルな構成で実現しました。Playwright や Cypress のような大型フレームワークではなく、Bun本体に組み込まれたブラウザ自動化APIだけで動く軽量アプローチです。
さらに Claude Code と組み合わせることで、テスト作成の自動化、スクリーンショットのAIレビュー、リリースごとの証跡管理まで一気通貫で回せる仕組みを紹介します。

 なぜ Bun なのか

 Anthropic が Bun を買収した
2025年12月、Anth...
