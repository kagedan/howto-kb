---
id: "2026-03-27-unitygithubgithubでバージョン管理に触れてみよう-01"
title: "【Unity＆GitHub】GitHubでバージョン管理に触れてみよう"
url: "https://qiita.com/kamaboko_0716/items/95cdd69e68042a135d61"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

# はじめに
こんにちは。
今回は、GitHubを使ったUnityの共同開発をClaudeを使って学んだので、その学んだことをまとめて、

:::note
- 共同開発でGitHubを使ってみたい
- GitHubに触れてみたい
:::

と思う人向けに記事を書きました。
また、今回の記事はあくまで「**初心者向け**」かつ「**触れる**」ことに重点を置いているので、

:::note alert
- 本格的な運用を学びたい
- GitHubについてちゃんと学びたい
:::

という人には向いていない内容です。予めご了承ください。

また、かなりの長文になってしまいました。(教材として作成したので長いです)
後々内容を分割して、今回のこの記事はそれらのまとめ記事として出すかもしれません。

# 今回使用した環境
- Windows 11(25H2)
- GitHub Desktop
- Git LFS(Git Large File Storage)
- Unity Hub & Unity Editor(6000.3.11f1)

# そもそも「Git」「GitHub」とは？
一応前提
