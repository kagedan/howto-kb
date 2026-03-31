---
id: "2026-03-31-rubric-llm-as-a-judge-でllmアプリの回帰テストを行う-01"
title: "Rubric × LLM-as-a-Judge でLLMアプリの回帰テストを行う"
url: "https://zenn.dev/elyza/articles/954e7c76e68340"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

はじめに

はじめまして、ELYZAで機械学習エンジニアのインターンをしている梶本です。
ELYZAのソリューション事業では、コールセンター向け通話要約作成・メール回答草案生成など、異なるタスクの多数のLLMアプリを共通基盤システム上で開発・運用しています。共通基盤システムのコードベースには機能追加やリファクタリングが頻繁に入るため、各アプリの動作と出力品質を確認する回帰テストが欠かせません。本システムでは各アプリのAPIインターフェースは共通化されているため、end-to-endの回帰テストの実行基盤自体も共通化できており、動作することの確認までであれば簡単に実現できています。
し...
