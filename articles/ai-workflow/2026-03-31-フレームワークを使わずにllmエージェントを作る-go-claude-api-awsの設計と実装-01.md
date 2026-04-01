---
id: "2026-03-31-フレームワークを使わずにllmエージェントを作る-go-claude-api-awsの設計と実装-01"
title: "フレームワークを使わずにLLMエージェントを作る — Go + Claude API + AWSの設計と実装"
url: "https://zenn.dev/dysksh/articles/27617be34cc336"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

はじめに
Discordから自然言語でタスクを投げると、LLMがリポジトリを読み、コードを生成し、GitHub PRとして返すエージェント「Nemuri」を作った。PRに限らず、新規リポジトリの作成、S3へのファイルアップロード、Discordへのテキスト返信にも対応している。LangChainやCrewAI等のフレームワークは使わず、Claude APIを直接叩いてGoで実装している。
フレームワークを使わなかった理由は、Nemuriのエージェントループが「1エージェントが2フェーズを順次実行＋レビューループ」というシンプルな構造で、複数エージェントの並列実行や動的ルーティングとい...
