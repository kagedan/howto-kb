---
id: "2026-03-20-claude-code-channelsとはdiscordからclaude-codeをスマホで操作す-01"
title: "Claude Code Channelsとは？DiscordからClaude Codeをスマホで操作する設定方法【完全ガイド】"
url: "https://note.com/no_ai_no_life/n/nb8bfcc8c1687"
source: "note"
category: "claude-code"
tags: ["claude-code", "note"]
date_published: "2026-03-20"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

2026年3月20日、Anthropicが「**Claude Code Channels**」を発表しました。

これは、DiscordやTelegramからClaude Codeに直接メッセージを送れる仕組みです。「ターミナルを開かずに、スマホのDiscordからAIに指示を出せたら便利じゃない？」そう思った人は正解です。この設定を一度やっておくだけで、外出先からでもClaude Codeに作業を依頼できるようになります。

この記事では以下を解説しています。

* Claude Code Channelsの仕組みと概要
* 設定に必要な環境と事前準備
* Discord Botの作成からペアリングまでの5ステップ
* 設定でつまずく唯一の落とし穴（Bunのインストール）
* 常時稼働・Telegram連携などの応用設定

---

## Claude Code Channelsとは

Claude Code Channelsは、**DiscordやTelegramをClaude Codeのインターフェースとして使えるようにする機能**です。

仕組みを簡単に説明すると、DiscordにメッセージをするとMCPサーバーがそのメッセージをClaude Codeのセッションに転送して、Claudeが返信してくれます。

1. DiscordにメッセージをするとMCPサーバーがそれを受信
2. MCPサーバーがメッセージをClaude Codeのセッションに転送
3. Claude Codeが処理して返信

PCのターミナルが起動していれば、スマホのDiscordアプリから非同期でAIと協働できます。これは「仕事術」の話ではなく、AIを使った働き方として一段階上のレベルです。

> **注意：** Claude Code Channelsは現在リサーチプレビュー段階のため、仕様が変更される可能性があります。

---

## 設定に必要なもの

作業を始める前に、以下を用意してください。

![](https://assets.st-note.com/img/1773978057-c91JVtukbLavzKZU65O2Ghxo.png?width=1200)

なお、この機能を使うには**claude.aiへのログイン認証が必要**です。APIキーだけの認証では動作しません。あらかじめ `claude` コマンドでログイン済みかを確認しておいてください。

### Claude Codeのバージョン確認とアップデート

```
# バージョン確認
claude --version

# アップデート（推奨）
claude update
```

`claude update` が失敗する場合（npm環境など）は以下を試してください。

```
npm install -g @anthropic-ai/claude-code@latest
```

それでも `ENOTEMPTY` などのエラーが出る場合は、一度ディレクトリごと削除してから再インストールが確実です。

```
sudo rm -rf /opt/homebrew/lib/node_modules/@anthropic-ai/claude-code
npm install -g @anthropic-ai/claude-code
```

アップデート後、再度 `claude --version` でバージョンが上がっていることを確認してください。

---

## Claude Code Channels 設定方法：5ステップ

### STEP 1｜DiscordでBotアプリケーションを作成する

まずDiscordにBotを作ります。

[Discord Developer Portal](https://discord.com/developers/applications) にアクセスして、右上の「New Application」をクリックしてください。好きな名前を入力して作成します。

作成後、左サイドバーの「Bot」をクリックします。ここで2つの設定を行います。

**① Botトークンを発行する**

「Token」の項目にある「Reset Token」を押してください。トークンが表示されます。これは**一度しか表示されない**ので、必ずコピーしてメモしておいてください。

**② Privileged Gateway Intentsをすべてオンにする**

同じページを下にスクロールすると「Privileged Gateway Intents」という項目があります。以下の3つをすべてONにしてください。

「Message Content Intent」がオフのままだと、BotがメッセージをDiscordから受け取れません。必ずONにしてください。

---

### STEP 2｜BotをDiscordサーバーに招待する

DiscordはサーバーにいるBotにしかDMを送れない仕様です。なので、まず自分のサーバーにBotを招待する必要があります。

Developer Portalの左サイドバーから「OAuth2」→「URL Generator」を開きます。

生成されたURLをブラウザで開いて、招待したいサーバーを選んで追加してください。

---

### STEP 3｜Bunをインストールする【最重要・ここで詰まる人が多いです】

**ここが最大のつまずきポイントです。**

このDiscordプラグインのMCPサーバーは「**Bun**」というJavaScriptランタイム上で動きます。Bunが入っていないと、Claude Codeのターミナル上ではプラグインが動いているように見えても、BotはDiscordに接続できずオフラインのままになります。実際、僕もそこでかなり時間を溶かしました（笑）。

ターミナルを開いて、まずBunがインストール済みか確認してください。

```
bun --version
```

「command not found」と表示された場合は、インストールされていません。以下のコマンドでインストールしてください。

```
curl -fsSL https://bun.sh/install | bash
```

インストールが完了したら、パスを反映させます。zshを使っている場合（macOSのデフォルト）はこちらです。

```
source ~/.zshrc
```

bashを使っている場合はこちらです。

```
source ~/.bash_profile
```

もう一度 `bun --version` を実行して、バージョン番号が表示されれば成功です。

---

### STEP 4｜Claude Codeでプラグインを設定する

ターミナルでClaude Codeを起動します。

```
claude
```

起動したら、プラグインをインストールします。

```
/plugin install discord@claude-plugins-official
/reload-plugins
```

次に、STEP 1で発行したBotトークンを設定します。

```
/discord:configure MTQ4NDM...(自分のトークン)
```

設定が完了したら、一度Claude Codeを終了して、Discordプラグインを有効にした状態で再起動します。

```
claude --channels plugin:discord@claude-plugins-official
```

---

### STEP 5｜ペアリングしてロックダウンする

再起動後、DiscordでBotにDMを送ってください。内容は「こんにちは」でも「test」でも何でもOKです。

Botから**6文字のペアリングコード**が返ってきます。そのコードをClaude Codeのターミナルで入力して承認します。

```
/discord:access pair xxxxxx
```

承認が完了したら、第三者がペアリングできないようにポリシーをロックします。

```
/discord:access policy allowlist
```

これで自分だけがBotを使える状態になりました。基本設定はここで完了です。

---

## 応用設定：Claude Code Channelsをもっと使いこなす

### 特定チャンネルでBotと会話する

DMだけでなく、サーバーの特定チャンネルでもBotと会話できます。

まずDiscordの「設定」→「詳細設定」から「開発者モード」をONにします。連携したいチャンネルを右クリックして「IDをコピー」でチャンネルIDを取得してください。

```
/discord:access channel add <チャンネルID>
```

これでそのチャンネルでBotにメンションすることで会話できるようになります。

### メンションなしで反応させる

「毎回 @Bot名 って書くのが面倒くさい」という人は、メンションなしで全メッセージに反応させる設定ができます。

```
# 既存チャンネル登録をいったん削除
/discord:access group rm <チャンネルID>

# --no-mentionフラグをつけて再登録
/discord:access group add <チャンネルID> --no-mention
```

ただし1つ注意点があります。複数のメンバーがいるサーバーのチャンネルに設定すると、他のメンバーの発言にもBotが反応してしまいます。自分専用のプライベートチャンネルか、個人用サーバーで使うのがおすすめです。

### TelegramでClaude Code Channelsを使う

Claude Code ChannelsはTelegramにも対応しています。TelegramのBotFatherで `/newbot` コマンドを実行してトークンを取得してから、以下のコマンドでプラグインをインストールします。

```
/plugin install telegram@claude-plugins-official
```

起動コマンドもDiscordと似た形です。

```
claude --channels plugin:telegram@claude-plugins-official
```

DiscordとTelegramの2つを同時に使いたい場合は、`--channels` の後ろにカンマ区切りで両方を指定することもできます。

### 常時起動させたい場合

ここまでの設定では、ターミナルが開いている間しかBotは動きません。常時稼働させるための方法は、大きく3つあります。

**① ターミナルセッションを永続化する（一番手軽）**

macOS専用のターミナルアプリ「[cmux](https://github.com/manaflow-ai/cmux/releases/latest/download/cmux-macos.dmg)」がおすすめです。AIエージェントのワークフロー向けに作られており、ウィンドウを閉じてもセッションが維持されます。Claude Codeのタスク完了通知機能も搭載。無料で使えます。

```
claude --channels plugin:discord@claude-plugins-official
```

**② VPS（クラウドサーバー）で動かす（おすすめ）**

さくらのVPSやAWSなどのクラウドサーバーにClaude Codeを入れて、そこで常時起動させる方法です。初期設定はやや手間ですが、一度動かしてしまえば最も安定した運用ができます。

**③ 必要なときだけ起動する（現実的）**

「今日は外出するから起動しておく」という使い方です。まずはこの方法から始めて、使い勝手を確かめてから①や②に移行するのがおすすめです。

---

## よくある質問（FAQ）

**Q. Claude Code Channelsは無料で使えますか？**  
Claude Code自体の利用料（**claude.aiサブスクリプションの費用**）は発生しますが、Claude Code Channels機能自体に追加料金はありません。

**Q. APIキーだけで使えますか？**  
使えません。claude.aiへのログイン認証が必要です。`claude` コマンドでログイン済みか事前に確認しておいてください。

**Q. Windowsでも使えますか？**  
WSL2経由でも動作しますが、**Git for Windowsを使ったネイティブWindows（PowerShell / CMD）でも正式に動作します**。どちらを選ぶかはユーザーの好みと環境次第です。

**Q. BotがDiscordでオフラインのままになります**  
Bunがインストールされていない可能性が高いです。STEP 3に戻って `bun --version` を確認してみてください。

**Q. ペアリングコードが届きません**  
STEP 1の「Message Content Intent」がONになっているか確認してください。これがオフだとBotはメッセージを受け取れません。

---

## まとめ

設定で一番大事なポイントは「**Bunを先にインストールしておくこと**」です。これさえ知っていれば、他の手順はスムーズに進められます。

Claude Code Channelsはまだリサーチプレビュー段階ではありますが、スマホのDiscordからClaude Codeに指示を出せるようになるのは、AIを使った働き方として一段階上のレベルです。ぜひ試してみてください。

---

## AIを「使う」から「動かす」へ

Claude Code Channelsを設定できたということは、あなたはもうAIをただ「使う人」ではありません。エージェントを自分で動かせる側に踏み込んでいます。

ただ、ここから先が本当の話です。

ツールを動かすことと、自分のビジネスにAIを組み込んで実際に成果を出すことは、まったく別の話です。「AIを入れたけど何も変わっていない」「便利は便利だけど、仕事の構造は変わっていない」——そう感じている人は多いと思います。

僕が運営している[**THE SHIFT**](https://shift.no-ai-no.life/)は、その壁を越えるための3ヶ月伴走プログラムです。

汎用ツールを渡して終わりではありません。あなたのビジネス専用のAIエージェントを、設計・実装・定着まで一緒に作り上げます。3ヶ月後に「1人なのに、チームのように動ける」状態にして終わる。それがTHE SHIFTの約束です。

Claude Code Channelsで「スマホからAIに指示を出せた」という感動が、AIが本当に自分の仕事の中で機能し始めるとさらに大きくなります。その先を体験したい方は、ぜひ見てみてください。

→ [**THE SHIFT｜AIエージェント実装の3ヶ月伴走プログラム**](https://shift.no-ai-no.life/)

ではまた！
