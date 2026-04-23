---
id: "2026-03-22-実践claude-code-channelsでzennqiita自動投稿システムを作ってみた-01"
title: "【実践】Claude Code ChannelsでZenn・Qiita自動投稿システムを作ってみた"
url: "https://qiita.com/kenji_harada/items/b9d81dbb70643711a83e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

この記事は自社ブログ([nands.tech](https://nands.tech/posts/claude-code-channels-cross-post))の要約版です

## はじめに：スマホからAI開発できる時代

先日、AnthropicのClaude Code Channelsを使って、自社ブログ記事を自動でZenn・Qiitaにクロスポストするシステムを作りました。

「記事を展開して」とDiscordに一言投げるだけで、AIがリライトから投稿まで全部やってくれる仕組みです。実際に作って動かしてみたので、開発プロセスを共有します。

## なぜ自動化したかった？

### 手動運用の辛さ

ブログ記事を書く度に：

1. Zenn用にリライト
2. Qiita用にもリライト
3. それぞれのフォーマットに整形
4. 手動で投稿

これを毎回やるのは現実的じゃないですよね...

### SEO戦略としてのクロスポスト

自分の場合、SEO観点でマルチプラットフォーム展開が必要でした：

* 外部プラットフォームからのバックリンク獲得
* ドメインパワー向上
* ただし、コピーコンテンツペナルティ回避のため各プラットフォーム向けに大幅リライト（重複率30%以下）

## 実装したシステム構成

Claude Codeが生成したファイル構成はこんな感じ：

```
lib/cross-post/
  ├── types.ts              # 型定義
  ├── rewriter.ts           # Claudeリライト
  ├── zenn-publisher.ts     # Zenn投稿
  ├── qiita-publisher.ts    # Qiita投稿  
  ├── thumbnail-generator.ts # サムネイル生成
  └── pipeline.ts           # メインロジック
scripts/
  └── cross-post.ts         # CLIエントリーポイント
```

約1,500行のTypeScriptコードが一気に生成されました。

## 技術実装のポイント

### プラットフォーム別リライト

各プラットフォームの特性に合わせてClaude APIでリライト：

```
// Zenn向けシステムプロンプト例
const zennPrompt = `
あなたはZenn向けの技術記事リライターです。
- 実装コード例を重視
- type: tech で技術記事として公開
- 構成、切り口、具体例を変えてリライト
`

// Qiita向けシステムプロンプト例  
const qiitaPrompt = `
あなたはQiita向けの技術記事リライターです。
- タグ重視（最大5つ）
- 実践的な「やってみた」トーン
- コードブロック多用
`
```

### XML形式での安定した出力解析

当初JSONで出力していましたが、Markdown内の特殊文字でパースエラーが頻発。XML形式に変更：

```
<title>記事タイトル</title>
<tags>tag1, tag2, tag3</tags>
<body>
マークダウン本文をそのまま格納
```
