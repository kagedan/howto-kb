---
id: "2026-03-25-cc-safe-setup-v2026個のexample-hookで守備範囲を5倍にした-01"
title: "cc-safe-setup v2.0——26個のexample hookで守備範囲を5倍にした"
url: "https://qiita.com/yurukusa/items/ce9a7c0490a59b6cfc37"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-25"
date_collected: "2026-03-26"
summary_by: "auto-rss"
---

Claude Codeの安全装置、v2.0にした。

最初は8個の基本フックだけだった。1ヶ月GitHub Issueを見続けて、実際に起きた事故からhookを作り続けた結果、26個のexample hookが溜まった。

## 何が変わったか

v1.0: `npx cc-safe-setup` → 8個のフックをインストール

v2.0: 8個 + 26個のexample hookが同梱。ワンコマンドでインストール可能。

```bash
# 基本の8フック
npx cc-safe-setup

# 追加のexampleを個別インストール
npx cc-safe-setup --install-example block-database-wipe

# 一覧表示（5カテゴリに分類）
npx cc-safe-setup --examples
```

## 5カテゴリ

### Safety Guards（11個）

| hook | 防ぐもの | 元になったIssue |
|---|---|---|
| allowlist | 許可リスト以外を全ブロック | [#37471](h
