---
id: "2026-03-18-kagentをamazon-eksで動かしてみた-amazon-bedrock-kubernetes-01"
title: "KagentをAmazon EKSで動かしてみた - Amazon Bedrock × Kubernetes × Agentic AI"
url: "https://zenn.dev/aws_japan/articles/1916c8486dda8f"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "GPT", "zenn"]
date_published: "2026-03-18"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

はじめに
「Kubernetesクラスターで障害が起きたとき、エラーログをコピーしてChatGPTに貼り付けて…」という経験、ありませんか？
AIは賢いけれど、あなたのクラスターの中身は見えていません。ログもメトリクスも、Podの状態も知らない。あなたが「コピペの仲介人」になっているだけです。
この課題を解決するのが Kagent です。KubernetesネイティブなAgentic AIフレームワークで、AIエージェントがクラスター内部から直接操作・診断を行えます。
本記事では、Amazon EKS上にKagentをデプロイし、Amazon Bedrock経由のClaudeをLLM...
