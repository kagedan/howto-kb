---
id: "2026-03-31-mcpサーバーを自分で作ってみる-hotpepper-api-01"
title: "MCPサーバーを自分で作ってみる / HOTPEPPER API"
url: "https://qiita.com/cecil_/items/c2a1fe09c47e9bc9700e"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "LLM", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

## はじめに

何かと話題のLLM（大規模言語モデル）。時代に置いていかれないよう、自分でも何か作ってみようと思い立ち、簡単にですがMCPサーバーを実装してみました。

## この記事でわかること

- MCPの概要
- 実装したもの

# MCPの概要

## MCPとは

MCPとは **Model Context Protocol** の略称で、AIモデルと外部システムを接続するための共通プロトコルです。

従来、AIに外部の情報や機能を使わせるためには、連携先ごとに個別のAPI設計と実装が必要でしたが、MCPの登場によりそんなめんどくさいことをする必要が無くなりました。

よく見かけるわかりやすい図↓
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3951996/b0fc7174-8ed4-4858-b659-28525f1989c8.png)
（引用：https://norahsakal.com/blog/mcp-vs-api-model-context-protocol-e
