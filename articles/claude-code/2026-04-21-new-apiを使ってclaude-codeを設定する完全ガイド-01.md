---
id: "2026-04-21-new-apiを使ってclaude-codeを設定する完全ガイド-01"
title: "New APIを使ってClaude Codeを設定する完全ガイド"
url: "https://qiita.com/ai-8tb-cc/items/d4aa9c39d76868e2b062"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

> **New API**（ai.8tb.cc）はAnthropicの公式APIと完全互換のエンドポイントを提供しています。Base URLとAPI Keyを置き換えるだけで、Claude Codeですぐに使い始めることができます。

## 前提条件

- Claude Codeがインストール済み（`npm install -g @anthropic-ai/claude-code`）
- [ai.8tb.cc](https://ai.8tb.cc) でアカウントを作成し、API Keyを取得済み

---

## 方法1：環境変数（推奨）

最もシンプルな方法で、すべてのOSに対応しています。

### macOS / Linux

ターミナルで以下を実行：

```bash
export ANTHROPIC_BASE_URL=https://api.8tb.cc/v1
export ANTHROPIC_AUTH_TOKEN=あなたのAPIKey
```

その後、Claude Codeを起動：

```bash
claude
```

**永続化する場合**（シェル設定ファイルに追加
