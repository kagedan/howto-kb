---
id: "2026-04-22-aws-bedrockで売上分析aiエージェントを構築してみた-01"
title: "AWS Bedrockで売上分析AIエージェントを構築してみた"
url: "https://zenn.dev/nttdata_tech/articles/df27d36a935ee1"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

AWS Bedrockで売上分析AIエージェントを構築してみた

 はじめに
こんにちは。
新人研修の一環として、生成AIを活用した売上分析AIエージェントの開発を行いました。
今回の取り組みでは、ユーザーが自然言語で分析内容を指示すると、その内容に応じたSQLの生成、データ取得、グラフ描画までを自動で実行する仕組みを構築しました。
本記事では、AWS Bedrockを活用した売上分析AIエージェントの構成と、実装にあたって特に考慮したプロンプト設計や構成上のポイントについて紹介します。


 システム構成
自然言語で売上分析の指示を入力すると、その内容に応じたグラフを自動生成するア...
