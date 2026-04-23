---
id: "2026-04-17-gemma4をollamaで使いvirtualboxからclaudeのvscode拡張機能で呼び出す-01"
title: "Gemma4をOllamaで使い、VirtualBoxからclaudeのVScode拡張機能で呼び出す"
url: "https://zenn.dev/okpisokapi/articles/2f7db6a320d24d"
source: "zenn"
category: "antigravity"
tags: ["GPT", "VSCode", "zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-18"
summary_by: "auto-rss"
query: ""
---

もともとローカルでChatGPTみたいにAIと会話することはできるというのは知っていたけど、claudeやcodexのようにエージェントとして使えることは最近友人から教えてもらった  
ローカルでエージェント使えるのは面白そうだということでものは試し

いろいろ調べてるとMacとかでホスト上で作業するときにエージェント利用している例はたくさん見つかるけど、vmからホスト上のモデルを使うパターンは見かけなかったからメモ程度に残しておく

最初に自分のPCのスペックを紹介  
CPU:i9-13900KF  
GPU:RTX4090  
メモリ:32GB  
OS:windows11

## Ollamaのインストールからモデル起動まで

[Ollamaのダウンロードページ](https://ollama.com/download)からwindows用のインストーラーをダウンロードしてインストール

コマンドプロンプトを起動して、モデルをダウンロードして起動

チャットができるようになるのでモデルと話して処理の重さを見ておくとよいかも

## VMからVScode拡張機能で呼び出すまで

なんでもいいからvmを起動

拡張機能で「Claude Code for VS Code」をインストール

~/.claude/setting.json  
に以下のように書き込む

```
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "ollama",
    "ANTHROPIC_BASE_URL": "http://(ホストマシンのIP):11434",
    "ANTHROPIC_API_KEY": ""
  },
  "effortLevel": "high",
  "preferredLanguage": "japanese",
  "model": "gemma4:31b"
}
```

以下のように設定したモデル名が出ていればよい  
![](https://static.zenn.studio/user-upload/25d41af8fe9f-20260417.png)

あとは使ってみて問題がなければこれで終わり  
![](https://static.zenn.studio/user-upload/f6aec820d879-20260417.png)  
思ったより簡単にセットアップできた
