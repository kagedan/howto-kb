---
id: "2026-03-22-claude-codeで会話ログをqiita記事にして投稿するまでを自動化した-01"
title: "Claude Codeで会話ログをQiita記事にして投稿するまでを自動化した"
url: "https://qiita.com/yuura_/items/2a33cae7b684c3ee9d75"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "qiita"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

AIエージェントとの会話ログをQiita記事にして投稿・公開するまでを自動化した。Claude Codeのカスタムコマンド2本とMCPで実現している。

:::note info
この記事はAIエージェント（Claude Code）が会話ログをもとに生成し、人間が確認・編集したものです。
:::

## 背景

自宅サーバーをProxmoxで運用しながら、色々なことをAIエージェント（Claude Code）に任せている。

ある日気づいた。「AIエージェントと話した内容って、そのまま技術記事になるんじゃないか？」

調査の過程、ハマったこと、判断の経緯——これが会話ログにそのまま残っている。手で書き直すのは面倒だが、仕組みを作れば会話の副産物として記事が生まれる。

## 参考にした構成

先に同じようなことをやっている記事を調べた。Claude Code × ObsidianでQiita記事を自動化している例があり、フローはこうなっていた：

- Slackのメッセージ or Obsidianのメモをネタ元にする
- インタビュー形式で体験を引き出す
- SubAgentで役割分担
