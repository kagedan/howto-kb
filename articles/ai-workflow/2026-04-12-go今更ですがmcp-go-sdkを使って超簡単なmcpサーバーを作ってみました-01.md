---
id: "2026-04-12-go今更ですがmcp-go-sdkを使って超簡単なmcpサーバーを作ってみました-01"
title: "【Go】今更ですが、MCP Go SDKを使って超簡単なMCPサーバーを作ってみました。"
url: "https://zenn.dev/tmyhrn/articles/ab1ce27980f91b"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "Python", "zenn"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

はじめに
最近、『MCP完全入門 業務効率化のためのAIエージェントの作り方』を読み、MCPの概念から実践まで学習しています。書籍ではPythonを使ったMCPサーバーの作成が紹介されていましたが、「GoでもMCPサーバーを作りたい！」と思い、シンプルな実装に挑戦しました。本記事はその備忘録です。

 今回作ったもの
本記事では、Go言語でMCPサーバーを実装する方法を紹介します。MCP Go SDKへの入門が目的のため、「入力された文字数とバイト数をカウントする」というシンプルなツールを持つMCPサーバーを実装しました。

Unicode文字単位でカウントするため、日本語などのマル...
