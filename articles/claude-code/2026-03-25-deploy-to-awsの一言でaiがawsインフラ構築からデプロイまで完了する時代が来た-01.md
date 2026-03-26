---
id: "2026-03-25-deploy-to-awsの一言でaiがawsインフラ構築からデプロイまで完了する時代が来た-01"
title: "「Deploy to AWS」の一言でAIがAWSインフラ構築からデプロイまで完了する時代が来た"
url: "https://qiita.com/miruky/items/74af8cae780f50f1a7f8"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "AI-agent", "qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

## はじめに

こんばんは、mirukyです。

2026年2月17日、AWSが**Agent Plugins for AWS**を公開しました。Claude CodeやCursorに「Deploy this app to AWS」と一言伝えるだけで、AIエージェントが**アーキテクチャ設計 → コスト見積もり → IaCコード生成 → デプロイ実行**まで自動で行ってくれるという、衝撃的なツールです。

初回リリースの`deploy-on-aws`プラグインに続き、サーバーレスやAmplify等の追加プラグインも順次公開。さらに2026年3月にはMicrosoftも**Azure Skills Plugin**を公開し、AWS・Azure両クラウドで「AIにインフラ構築を任せる時代」が本格的に始まりました。

本記事では、Agent Plugins for AWSの仕組み・使い方・注意点をコンパクトにまとめます。

出典：[Introducing Agent Plugins for AWS - AWS Blog](https://aws.amazon.com/blogs/devel
