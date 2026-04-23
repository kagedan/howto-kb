---
id: "2026-03-23-メールの返信文をclaudeに自動生成させるgmailmakeclaudeで返信テンプレート量産-01"
title: "メールの返信文をClaudeに自動生成させる｜Gmail×Make×Claudeで返信テンプレート量産"
url: "https://note.com/bold_hebe170/n/n7638fb775269"
source: "note"
category: "ai-workflow"
tags: ["note"]
date_published: "2026-03-23"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

プログラミングできないのにAI自動化にハマったおじさんです。Make×Claudeで毎朝の作業をどんどん自動化しています。ノーコードでできた仕組みをそのまま共有していきます。

## はじめに

毎回似たような内容のメール返信、書くのが面倒ではないですか？

このシステムを作ってから、Gmailに届いたメールをClaudeが自動で読んで返信文の下書きを生成。Googleドキュメントに保存してくれます。あとはコピペして送るだけです。

## このシステムで何ができるか

```
Gmailに新しいメールが届く
        ↓
Makeが内容を取得
        ↓
Claudeが返信文を3パターン生成
        ↓
Googleドキュメントに自動保存
        ↓
Slackに「返信文ができました」と通知
```

## 必要なツールと費用

・Make：無料〜月9ドル ・Anthropic API：1通あたり数円 ・Gmail：無料 ・Googleドキュメント：無料 ・Slack：通知 → 無料

## 第1章｜Gmailの設定

MakeのGmailモジュールで新着メールを監視します。

・トリガー：「Watch Emails」 ・フィルター：特定のラベルまたは送信者に絞ることも可能 ・取得内容：件名・本文・送信者

## 第2章｜メールの前処理

長いメールは要点だけClaudeに渡します。

```
{{substring(stripHTML(1.body.text); 0; 500)}}
```

先頭500文字をHTMLタグ除去した上でClaudeに送ります。

※ここまで無料で読めます

📦 **購入するとコピペキットが使えます**

300円でメール返信自動化が30分で完成します。

【ここから有料・価格300円】
