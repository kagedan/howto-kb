---
id: "2026-04-12-claude-api-fine-grained-tool-streaming入門-低遅延エージェント-01"
title: "Claude API Fine-Grained Tool Streaming入門 — 低遅延エージェントをPythonで実装する"
url: "https://qiita.com/kai_kou/items/8e1d151031acc1851445"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

<!-- IMAGE_SLOT: hero
description: "Fine-grained tool streaming concept diagram showing Claude API streaming tool parameters character by character with low latency"
aspect: 16:9
-->

## はじめに

Claude API でツールを使ったエージェントを構築すると、ツール呼び出しの**パラメータが大きいほど応答開始までの時間が長くなる**という問題に直面します。

これは従来、Claude がパラメータを完全に生成してからクライアントへ送信する「バッファリング」が行われていたためです。ファイル書き込みツールに渡す長いテキストや、検索クエリが完成するまで待機が発生していました。

**Fine-Grained Tool Streaming** は、このバッファリングを取り除き、ツールパラメータを**生成しながら即座にストリーミング**する機能です。2026年2月5日に全モデル・全プラットフォームで正式リリ
