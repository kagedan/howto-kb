---
id: "2026-06-25-ccdeckでマシン内のclaudeセッションを横断検索してresumeを簡単に-01"
title: "ccdeckでマシン内のClaudeセッションを横断検索してresumeを簡単に💫"
url: "https://zenn.dev/sonono/articles/db68cb992b078a"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-06-25"
date_collected: "2026-06-26"
summary_by: "auto-rss"
query: ""
---

...というツールを作成してみました。  
<https://github.com/Sonono1103/claude-deck>

## 背景

マイクロサービスよりの環境で開発しているので、レポジトリが大量にあります。  
またプロジェクトも複数あるので、このレポジトリでClaude開いて、今度はこっちのレポで開いて、雑談はホームディレクトリでClaude開いてみたり...と言うことをしていると、「あのセッションどのレポジトリだったっけ？」と言うことが頻発していました。  
簡単にセッションタイトルで検索してセッションを再開したい！と言う気持ちでこのツールを作成してみました。

## 使い方

`ccdeck`でセッションのリストが開くので、`/検索ワード`でセッションを検索し、Enterを押してそのセッションに入る（=resume）というのが私のよくしている使い方です！  
セッション削除、ピン留め機能やアラート機能もあります。  
Claudeのセッション内で`/rename セッション名`とするとセッション名を変更できるので、それでわかりやすい名前を設定しておくと検索が捗ります。  
![demo](https://raw.githubusercontent.com/Sonono1103/claude-deck/main/docs/demo.gif)

## インストール方法

```
go install github.com/Sonono1103/claude-deck/cmd/ccdeck@latest
```

でインストールできます。あとは

するだけ。

自分があまりhomebrew使っていないので入れていないのですが、対応した方がいいのかな...？  
何か不備があれば教えていただけると幸いです！
