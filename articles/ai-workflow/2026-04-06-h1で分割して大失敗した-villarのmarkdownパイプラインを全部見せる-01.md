---
id: "2026-04-06-h1で分割して大失敗した-villarのmarkdownパイプラインを全部見せる-01"
title: "H1で分割して大失敗した — villarのMarkdownパイプラインを全部見せる"
url: "https://zenn.dev/tyler0702/articles/64420c4334d249"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-06"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

この記事について
前回の記事で、AI(Claude)が出力する長文Markdownを読むためにTauri v2でリーダーアプリ「villar」を作った経緯を書きました。
今回はvillarの核心、Markdownの処理パイプラインについて書きます。カード分割、TL;DR自動生成、Mermaidの3段階フォールバック。この3つで開発時間の6割くらいを使いました。
https://github.com/tyler0702/villar

 Markdownパイプライン：ここが本体
villarのコードで一番量が多いのはReactのUIではなく、Markdownの処理パイプラインです。
M...
