---
id: "2026-04-04-aiハーネスoss-4選比較superpowerstakteccoh-my-claudecodeを試-01"
title: "AIハーネスOSS 4選比較：superpowers・TAKT・ECC・oh-my-claudecodeを試してTAKTを選んだ理由"
url: "https://zenn.dev/purple_matsu1/articles/20260402-takt-adoption"
source: "zenn"
category: "ai-workflow"
tags: ["LLM", "zenn"]
date_published: "2026-04-04"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

はじめに
前回の記事では、AIエージェントを活用した開発ワークフローを「ハーネス」として設計する考え方（ハーネスエンジニアリング）を紹介し、6フェーズの要件定義を行いました。
要件のポイントは4つ。厳格なワークフロー（フェーズスキップ不可）、サブエージェント活用、LLM非依存、人手なしの自動ループです。
この要件を持って4つのOSSを調査しました。この記事では、その比較とTAKT採用の経緯、実装したpieceを整理します。


 比較した4つのOSS

 superpowers
スキル駆動の「プロセス強制型」ハーネスです。brainstorming → planning → suba...
