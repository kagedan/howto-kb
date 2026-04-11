---
id: "2026-04-10-gemini-enterprisegemini-31-x-claude-46-を連携させて企画マージ-01"
title: "【Gemini Enterprise】Gemini 3.1 x Claude 4.6 を連携させて「企画→マージ」を自動化してみた"
url: "https://zenn.dev/google_cloud_jp/articles/412b26038374a9"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

はじめに
「在庫数を商品リストの画面に追加してほしい」── たった一言の要件から、PRD の作成、GitHub Issue の起票、コードの実装、Pull Request の作成、そしてマージまで。通常であれば、要件を PRD にまとめ → Issue を起票し → エンジニアが既存のコードを解析 → 実装 → レビュー → マージという多段階のプロセスを経るため、1 つの機能追加に数時間〜数日を要します。
本記事では、Gemini Enterprise をエージェントハブとして、Agent Designer で作成した PRD Agent（Gemini 搭載）と、ADK で開発し...
