---
id: "2026-05-29-claude-codeのpasted-text-n-m-linesを編集したい-01"
title: "Claude Codeの[Pasted text #N +M lines]を編集したい！"
url: "https://zenn.dev/uchunanora/articles/cc-edit-pasted-text"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

Claude Codeで複数行テキストをペーストしたときに`[Pasted text #N +M lines]`として畳まれてしまうことがあります。

長文で編集せずにそのまま送信するときは視認性的にとっても良いです。  
しかし、少し編集したいときに、そのままだと編集できずに困っていたので解決方法をまとめておきます。

## `[Pasted text #N +M lines]`になるタイミング

いろいろやってみた結果、おそらく畳み込み発動条件は以下のどちらかです。

* 801文字以上のテキスト
* 4行以上（改行コードが3個以上）

（ドキュメントには1万文字以上と書いているけど🤔）  
<https://code.claude.com/docs/en/terminal-config#paste-large-content>

## 編集方法

`[Pasted text #N +M lines]`を編集する方法は2つあります。

### 1. ペースト → ペースト

2回連続でペーストすると表示されます。  
よく見るとペーストしたときに`paste again to expand`って書いてますね（全然気づかなかったけど...）

![paste2paste](https://static.zenn.studio/user-upload/f95f48215e3a-20260529.webp)

### 2. 外部エディターで編集

小さめのものはClaude Codeのプロンプト入力欄で編集しちゃえばよいですが、大きくなると編集しにくい...  
そこで、`Ctrl + G`で外部エディターが開くので、プロンプトを指定のエディターで修正することができます。  
保存して閉じればClaude Codeのプロンプト入力欄に挿入されています。便利！

![外部エディター編集](https://static.zenn.studio/user-upload/13fe02ffcaad-20260529.webp)

Claude Codeの編集がちょっぴり快適になったね。やったぜ
