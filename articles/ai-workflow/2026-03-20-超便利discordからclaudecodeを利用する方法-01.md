---
id: "2026-03-20-超便利discordからclaudecodeを利用する方法-01"
title: "【超便利】DiscordからClaudeCodeを利用する方法"
url: "https://note.com/luck_ai_/n/n1e5da4b41f6e"
source: "note"
category: "ai-workflow"
tags: ["note"]
date_published: "2026-03-20"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

※本機能は2026/03/20時点で実験的な機能となるので正式リリース後には使えなくなる可能性があります。

  

## 1. DiscordでBotを作成する

### 1.1 新規アプリケーションを作成

### [こちら](https://discord.com/developers/applications)にアクセスして右上の「新しいアプリケーション」からボットを作成してください。

名前を入力するメニューが表示されるので入力してください。

![](https://assets.st-note.com/img/1773962377-kWcxvhdwRKUT6e1zZlEHbIXJ.png?width=1200)

Discord 新しいアプリケーション

### 1.2 Botの設定

その後の画面で左メニューから「Bot」をクリックして遷移

![](https://assets.st-note.com/img/1773962597-lQoMB1H7r5LUJnECN6SXR0VY.png?width=1200)

Botメニュー

### 1.3 メッセージコンテンツインテントをONにする

画面スクロールしていくと「**Message Content Intent**」というメニューが表示されるのでONにしてください

![](https://assets.st-note.com/img/1773962730-xwP594XhErVmGvCQlRaNiyUo.png?width=1200)

Message Content Intent

### 1.4 トークンを生成

画面上部にスクロールして「**トークンをリセット**」をクリックしてトークンの再生成を行ってください。  
※ こちらのトークンは後ほど使用するのでいつでも参照できるようにしておいてください

### 1.5 BotをDiscordサーバーに招待

Discordで新規のチャンネルもしくは既存のチャンネルにBotを追加していきます。  
まずはフレンドを招待で招待リンクをコピーします。

リダイレクトに先ほどコピーしたリンクを入力します。

先ほどのDiscordアプリケーション設定画面に戻ります。  
左メニューから「OAuth2」を選択し画面下部のOAuth2 URLジェネレーターから"bot"をクリックします。

![](https://assets.st-note.com/img/1773976597-ae6Atw5LCx1EIkZp8cbJo3ju.png?width=1200)

Botの権限に👇を追加

![](https://assets.st-note.com/img/1773976621-2lnBksEzSApY39uRUhMKqyxb.png?width=1200)

生成されたURLにアクセスする

URLにアクセスしたら下記のような承認画面が現れます。  
インストールするサーバーを選択して進めていってください。

![](https://assets.st-note.com/img/1773976701-ORXgu268dCqM5LU3TbjHhyV9.png?width=1200)

## 2. ClaudeCodeの設定

> もしBunをインストールしてない方はインストールしてください。  
> curl -fsSL https://bun.sh/install | bash

### 2.1 ClaudeCodeにプラグインをインストール

ここでClaude Codeを起動させて下記コマンドを実行

```
/plugin install discord@claude-plugins-official
```

### 2.2 プラグインのリロード

```
/reload-plugins
```

### 2.3 トークンの設定

先ほどのトークンを設定します  
※ /discord:configureが機能しない場合はclaudeを起動し直してください

```
/discord:configure MTIz...
```

そのままclaudeに従ってYesを続けてください

### 2.4 チャンネルフラグを付けて再起動

1度セッションを終了して、再起動して下記コマンドを実行

```
claude --channels plugin:discord@claude-plugins-official
```

### 2.5 DiscordのDMでClaudeにチャットを送る

チャットを送るとペアコードが送られてくるのでそれをClaude Codeに打ち込めば連携完了です。

![](https://assets.st-note.com/img/1773976874-2IW4qkg7hwxiMXGAfPydEYVs.png?width=1200)

下記になれば接続完了です

![](https://assets.st-note.com/img/1773976990-EVjCKYL5Q3yeG4tHIMwNmRPh.png?width=1200)

### まとめ

まぁOpenClawと同じですね笑  
でも公式で出してくれるのはありがたいですね。  
ClaudeCodeはこういった痒い所に手が届く機能を追加していってくれるのが嬉しいですね。今後のアップデートにも期待です。

---

X（Twitter）もやってるのでよろしければフォローお願いします！！  
[@luck\_ai\_](https://luck_ai_/)
