---
id: "2026-04-11-stripe-webhook-claude-cli-で法律文書を自動生成した話nodejs-sqli-01"
title: "Stripe Webhook × Claude CLI で法律文書を自動生成した話（Node.js + SQLite）"
url: "https://qiita.com/Mildsolt2914491/items/e705e8da8eaf7808d3e6"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## 1. はじめに

契約書や利用規約などの法律文書って、テンプレートから何度も同じことを書き直したり、細かい表現を調整したりと、かなりの手作業がかかります。

数ヶ月前、「このプロセスを自動化できたら、もっと効率的に運用できるのでは？」と考え始めました。そこで目をつけたのが **Stripe Webhook** と **Claude CLI** の組み合わせです。

- **Stripe Webhook**: 支払い成功時などのイベントをリアルタイムに検知
- **Claude CLI**: AIに法律文書の生成タスクを委譲

この2つを組み合わせることで、顧客の支払い完了→自動的に法律文書生成という、**完全自動化のパイプライン**を実現できました。

## 2. システム概要（アーキテクチャ）

全体の流れは以下の通りです：

```
Stripe Payment Event
        ↓
    Webhook受信 (Express)
        ↓
   署名検証 (重要!)
        ↓
   Claude CLIに処理を委譲
        ↓
   生
