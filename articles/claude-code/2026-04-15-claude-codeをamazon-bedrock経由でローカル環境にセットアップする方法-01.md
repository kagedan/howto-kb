---
id: "2026-04-15-claude-codeをamazon-bedrock経由でローカル環境にセットアップする方法-01"
title: "Claude CodeをAmazon Bedrock経由でローカル環境にセットアップする方法"
url: "https://zenn.dev/runyan_tang/articles/db0b5b336d765e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

ターミナル型AIアシスタント「Claude Code」を、Anthropicの直接APIではなくAWSのAmazon Bedrock経由で利用するための手順をまとめました。
すでにAWS環境を利用していて、Bedrock経由でセキュアにClaudeを使いたいエンジニアの方におすすめです。

 0. 事前準備（前提条件）
設定を進める前に、以下の環境が整っているか確認してください。


AWSアカウント: Bedrockへのアクセスが有効になっていること。

モデルアクセス: Bedrock上で目的のClaudeモデル（例：Claude Sonnet 4.6）の利用申請が完了していること。...
