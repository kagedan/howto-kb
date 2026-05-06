---
id: "2026-05-05-claude-discordmcpでdiscordボットを自然言語で操作する方法claude-des-01"
title: "【Claude × Discord】MCPでDiscordボットを自然言語で操作する方法【Claude Desktop】"
url: "https://qiita.com/Yuffter/items/7e81ee604013de17bb63"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "qiita"]
date_published: "2026-05-05"
date_collected: "2026-05-06"
summary_by: "auto-rss"
---

# はじめに
意外と日本語記事が少なかったので備忘録として残しておきます。
私は開発系でDiscordを使うことが多く、毎回チャンネル作成やロール作成などの整備が面倒だと感じていました。最近Claude Proプランを登録したこともあり、DiscordにもMCPがないか調べたところ、非公式ではありますが、存在していたので試してみました。

# 出来ること
- チャンネル、ロールの作成
- 投稿内容の取得
- メッセージの投稿

# 環境
- Windows 11
- Claude Desktop
- Discord
- Node.js

# 接続方法
## Discord Botを作成
[**Discord Developer Portal**](https://discord.com/developers/applications)にアクセスしてボット(新しいアプリケーション)を作成します。
作成出来たら左の概要から「**Bot**」を選択し、
![スクリーンショット 2026-05-05 212311.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3313705/c2c8c03c-12ba-446a-afb7-ef632217b224.png)
「**トークンをリセット**」をクリックし、出てきたトークンをコピーしておきます。

:::note warn
**注意**
トークンはボットの操作を可能にする鍵のようなものなので、絶対に外部に漏らさないようにしましょう。
:::

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3313705/668ea8c0-cf14-45b9-ba74-fb1844a507b2.png)
この際、許可する権限として、「**Server Members Intent**」と「**Message Content Intent**」にチェックをつけておきます。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3313705/ed11846a-53c2-468e-a9fc-475fe6425ca3.png)
ここで一度変更を保存しておきましょう。

## Botをサーバーに招待
左の概要から「OAuth2」を選択し、
![スクリーンショット 2026-05-05 213531.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3313705/efdaee85-1412-415c-9167-4dc03ee5d2d2.png)
OAuth2 URLジェネレーターから「**Bot**」にチェックをつけます。
![スクリーンショット 2026-05-05 213829.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3313705/3451608e-b0a5-48ab-a819-69dfbb7b2f04.png)
ボットに付与する権限は必要に応じて選択してください。選択が終わり次第、一番下に招待用のURLが生成されているので、そこから招待したいサーバーを選択してボットを招待します。
これでDiscord側の準備はほぼ完了です。

## MCPサーバーをインストール
次にNode.jsからDiscord用MCPサーバーをインストールします。
ターミナルにて、以下のコマンドを実行しましょう。
```
npx @quadslab.io/discord-mcp init
```
対話形式で設定を進めていき、Discordトークンは先ほどコピーしたボットトークンを使用します。

## Claude Desktopの設定
いよいよ最後の工程です。Claude Desktopの設定から開発者タブを開き、「**設定を編集**」から「**claude_desktop_config.json**」の編集を行います。
以下の内容を記述します。
```
{
  "mcpServers": {
    "discord": {
      "command": "C:\\Windows\\System32\\cmd.exe",
      "args": [
        "/C",
        "C:\\Program Files\\nodejs\\npx.cmd",
        "-y",
        "@quadslab.io/discord-mcp"
      ],
      "env": {
        "DISCORD_TOKEN": "ボットのトークンを入力",
        "DISCORD_GUILD_ID": "サーバーIDを入力"
      }
    }
  }
}
```
サーバーIDについては、Discordにて該当サーバーを右クリックして「**サーバーIDをコピー**」からコピー出来ます。(項目がない場合は、ユーザー設定->開発者->開発者モードを有効にする必要があります。)
終わったら一度Claude Desktopを再起動して設定を反映します。この際、エラーメッセージが表示されていなければ連携完了です。

# 最後に
以上の手順を踏むことで、Claude DesktopからDiscordボットを自然言語で操作することが出来ます。チャンネル作成や投稿されているメッセージの解析など様々なことをAIに任せることが出来るのでぜひ試してみてください！
AIに任せられることは任せて楽をしよう！
