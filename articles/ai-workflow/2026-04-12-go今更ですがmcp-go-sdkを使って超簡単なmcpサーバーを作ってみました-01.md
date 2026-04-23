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

## はじめに

最近、『[MCP完全入門 業務効率化のためのAIエージェントの作り方](https://book.impress.co.jp/books/1125101096)』を読み、MCPの概念から実践まで学習しています。書籍ではPythonを使ったMCPサーバーの作成が紹介されていましたが、「GoでもMCPサーバーを作りたい！」と思い、シンプルな実装に挑戦しました。本記事はその備忘録です。

## 今回作ったもの

本記事では、Go言語でMCPサーバーを実装する方法を紹介します。[MCP Go SDK](https://github.com/modelcontextprotocol/go-sdk)への入門が目的のため、「入力された文字数とバイト数をカウントする」というシンプルなツールを持つMCPサーバーを実装しました。

Unicode文字単位でカウントするため、日本語などのマルチバイト文字も1文字として数えられます。  
MCPホストにはClaude Desktopを使用し、作成したMCPサーバーを呼び出して動作確認を行いました。（claude\_desktop\_config.jsonへの設定は反映済みの状態です）

![](https://static.zenn.studio/user-upload/838eb438c441-20260412.png)

![](https://static.zenn.studio/user-upload/78a2c3383db4-20260412.png)

自作ツールの呼び出しに成功し、文字数とバイト数が正しくカウントされていることを確認できました。

## まとめ

本記事では、MCP Go SDKを使ったGoによるMCPサーバーの実装に入門しました。

今回は文字数・バイト数カウントというシンプルなツールを題材にし、MCPサーバーの基本的な構成（ツール定義・Claude Desktopとの連携設定）を一通り体験できました。

今後は、[MCP Go SDK](https://github.com/modelcontextprotocol/go-sdk)を使ってより実用的なツール（DB操作、外部API連携など）のMCPサーバー実装も試していきたいと思います。

## 参考
