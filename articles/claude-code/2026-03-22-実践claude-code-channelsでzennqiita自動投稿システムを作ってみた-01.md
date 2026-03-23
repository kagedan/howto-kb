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

- 外部プラットフォームからのバックリンク獲得
- ドメインパワー向上
- ただし、
