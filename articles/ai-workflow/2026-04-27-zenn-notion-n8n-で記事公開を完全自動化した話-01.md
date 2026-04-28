---
id: "2026-04-27-zenn-notion-n8n-で記事公開を完全自動化した話-01"
title: "Zenn × Notion × n8n で記事公開を完全自動化した話"
url: "https://zenn.dev/guida/articles/2026-04-27-zenn-notion-n8n-automation"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-27"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

## はじめに

この記事は Notion で書いて n8n + GitHub Actions 経由で Zenn に自動公開された記事です。記事の企画から本文執筆、画像生成、公開までを Notion 1 つで完結させる仕組みを構築しました。

## 構成

* Notion: 記事の企画 / 執筆 / メタ情報管理
* n8n (Mac on Docker): 1 分毎に Notion をポーリング
* Cloudflare Tunnel: n8n を n8n-zenn.guida.jp で公開
* GitHub Actions: Notion を Markdown に変換 → zenn-content リポジトリに push
* Zenn: GitHub 連携で自動公開

## フロー

Notion で Status を「公開予定」に変更 → 1 分以内に n8n が検出 → GitHub Actions 起動 → Zenn に反映、という流れです。所要 30 秒〜 2 分。

## おわりに

これは公開フロー検証用のテスト記事です。
