---
id: "2026-04-10-aiazureclaude初心者向けazureだけでaiチャットwebアプリを作る-01"
title: "【AI】【Azure】【Claude】【初心者向け】AzureだけでAIチャットWebアプリを作る"
url: "https://qiita.com/yudai8155/items/7f85d1d9d7b60681ce0f"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

# はじめに
Azureを業務で使用するにあたり、学習目的でAzureのサービスを使用してシンプルなAIチャットを作ってみました
Claudeに手順を作成してもらい進めました。
下記の内容も全てClaudeに作ってもらっています。

### 使うサービス

| サービス | 用途 | 料金 |
|---|---|---|
| Azure VM (B1s) | Webサーバー | 12ヶ月無料 |
| Azure OpenAI Service | AIの応答生成 | 従量課金 |
| Flask (Python) | Webアプリフレームワーク | 無料 |

### 完成イメージ

ブラウザからメッセージを送ると、GPT-4oが返答してくれるチャットアプリです。

---

## 1. Azure VMの作成

Azureポータル（https://portal.azure.com）にログインして仮想マシンを作成します。

### 推奨設定

| 項目 | 設定値 |
|---|---|
| OS | Windows Server 2022 |
| サイズ | B1s（無料枠対象） |
