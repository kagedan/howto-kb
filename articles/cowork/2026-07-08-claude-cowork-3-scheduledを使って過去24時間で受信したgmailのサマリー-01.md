---
id: "2026-07-08-claude-cowork-3-scheduledを使って過去24時間で受信したgmailのサマリー-01"
title: "Claude Cowork (3) Scheduledを使って、過去24時間で受信したGmailのサマリーをSlackへ通知する"
url: "https://zenn.dev/kameoncloud/articles/abada19c23404e"
source: "zenn"
category: "cowork"
tags: ["cowork", "zenn"]
date_published: "2026-07-08"
date_collected: "2026-07-09"
summary_by: "auto-rss"
query: ""
---

<https://serverless.co.jp/blog/o-_yx04beqf7/>  
へ投稿した記事の微修正版です。

過去の記事で、Claude Cowork の Gmail コネクターと Google Drive コネクターを使って、Gmailのサマリーを作成し、Google Drive へ保存する手順を見ていきました。

今日はさらにScheduled機能を使って、1日1回自動で過去24時間で受信したGmailのサマリーを作成し、Slackへ通知させてみます。

![](https://static.zenn.studio/user-upload/68ce3f254763-20260708.png)

### さっそくやってみる

まずSlackへメッセージを通知するためにはClaude Cowork にSlackコネクターを入れる必要があります。

シンプルに slack への通知を行いたい。コネクターをインストールしてください。 とClaudeに指示を出します。

そうすると接続の許可を求めるダイアログが出てきますので Connect をクリックします。  
![](https://static.zenn.studio/user-upload/aa623114a8c2-20260708.png)  
ブラウザが起動しSlack側で接続を受け入れてよいか許可を求める画面が表示されますので、 許可する をクリックします。

Slack上でテスト用メッセージを受信する #gmail というチャネルを作成した後gmailというチャネルにテストメッセージを送信できますか？　と入力します。　　  
![](https://static.zenn.studio/user-upload/4f336b4fff35-20260708.png)  
そうすると 確認を求められますので Send をクリックすると無事メッセージを受信します。  
![](https://static.zenn.studio/user-upload/1b67f316bc07-20260708.png)  
これでClaude Cowork 環境が connectorを通じでGmailとSlackそれぞれと接続されました。では左ペインから Scheduled をクリックします。  
![](https://static.zenn.studio/user-upload/66ebe36e2bd7-20260708.png)  
Claude Desktop がスケジューラーとなってタスクを実行するため指定した時間で実行させるためにはClaude DesktopがインストールされたPCが起動中でなければならないことに注意してください。

New Task をクリックします。 過去24時間以内に受信したgmailのサマリーをSlackの#gmailへポストしてください。 と指示を出します。  
![](https://static.zenn.studio/user-upload/e106034be811-20260708.png)  
自動で動作させるために Act without askingモードを指定して毎晩23:59に実行するように指定します。  
![](https://static.zenn.studio/user-upload/1bbdbf956bc6-20260708.png)  
出来上がったタスクを開いて Run now をクリックして手動実行してみます。  
![](https://static.zenn.studio/user-upload/4b33f2f3397d-20260708.png)  
Slackに無事サマリーが投稿されました！  
![](https://static.zenn.studio/user-upload/4029ced30c51-20260708.png)
