---
id: "2026-03-28-claude-codediscordからclaude-codeを使うchannels-01"
title: "【Claude Code】DiscordからClaude Codeを使う「Channels」"
url: "https://zenn.dev/nylon66/articles/d37f97dd9734d1"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

## 概要

Claude Code には Discord チャンネルと連携するプラグイン機能が組み込まれています。  
設定することで、Discord の DM やサーバーチャンネルから Claude Code を操作できるようになります。

## 前提条件

* Claude Code v2.1.80 以降がインストール済みであること
* claude.ai アカウントでログイン済みであること
* [Bun](https://bun.sh) がインストール済みであること（`bun --version` で確認）
* Discord アカウントを持っていること

## セットアップ手順

### 1. Discord Bot の作成

[Discord Developer Portal](https://discord.com/developers/applications) にアクセスし、**New Application** をクリックしてアプリ名を入力します。

**Bot** セクションでユーザー名を作成し、**Reset Token** をクリックしてトークンをコピーします。

次に **Privileged Gateway Intents** までスクロールし、**Message Content Intent** を有効にします。

### 2. ボットをサーバーへ招待

**OAuth2 > URL Generator** を開き、以下を設定します。

**Scopes:**

**Bot Permissions:**

* View Channels
* Send Messages
* Send Messages in Threads
* Read Message History
* Attach Files
* Add Reactions

生成された URL をブラウザで開き、招待先サーバーを選択して **認証** します。

### 3. プラグインをインストールする

Claude Code のターミナルで以下を実行します。

```
/plugin install discord@claude-plugins-official
```

プラグインが見つからない場合は、マーケットプレイスを追加・更新してから再試行します。

```
/plugin marketplace add anthropics/claude-plugins-official
/plugin marketplace update claude-plugins-official
```

インストール後、プラグインの設定コマンドを有効化します。

### 4. Bot トークンを設定する

コピーしたボットトークンで設定コマンドを実行します。

```
/discord:configure <token>
```

設定は `~/.claude/channels/discord/.env` に保存されます。

### 5. チャネルを有効にして再起動する

Claude Code を終了し、`--channels` フラグで再起動します。

```
claude --channels plugin:discord@claude-plugins-official
```

### 6. アカウントをペアリングする

Discord でボットに DM を送信します。ボットがペアリングコードを返信します。

Claude Code に戻り、ペアリングコードで承認します。

```
/discord:access pair <code>
```

最後に、自分のアカウントだけがアクセスできるようポリシーを設定します。

```
/discord:access policy allowlist
```

## 使い方

設定完了後は、Discord のボットに DM またはサーバーチャンネルでメッセージを送信すると Claude Code が応答します。

![image.png](https://static.zenn.studio/user-upload/deployed-images/10d55251232de923f1a85145.png?sha=3842ce9e78d7885a16cdb83e858ac105662b03ab)

## 参考リンク
