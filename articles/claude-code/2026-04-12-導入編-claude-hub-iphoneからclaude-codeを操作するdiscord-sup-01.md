---
id: "2026-04-12-導入編-claude-hub-iphoneからclaude-codeを操作するdiscord-sup-01"
title: "【導入編】: claude-hub — iPhoneからClaude Codeを操作するDiscord Supervisorシステム"
url: "https://zenn.dev/harieshokunin/articles/c6ba085ed070e3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

## 記事メタ情報

---

### はじめに — OpenClaw に憧れて、自分で作ることにした

きっかけは [OpenClaw](https://github.com/anthropics/claude-code) のようなリモートエージェント基盤を触りたかったことだ。外出先からAIエージェントに指示を出して、コードを書かせたり、レビューさせたりしたい。

ただ、セキュリティ面で少し及び腰だった。自分のMacにリモートアクセスを開けるのは怖い。

ちょうどその頃、Claude Code に `--channels` オプションが追加された。Discord や Slack 経由でClaude Codeを操作できるようになる機能だ。「これを使えば、フルリモートアクセスを開けなくても、擬似的に似たものが作れるのでは？」——ここからプロジェクトが始まった。

最初に作ったのは [前作の GitHub Actions 版](https://zenn.dev/harieshokunin/articles/1014158226dd76) だ。GitHub Actions × Claude Code × Tailscale で、iPhoneからIssueを立てるだけでAIが実装してくれる環境を作った。

夢は叶った。でも金が溶けた。

GitHub Actions の従量課金、Tailscale の常時接続、CI/CD のランナー代。「動くけど維持できない」という現実に直面した。

そこで作り直したのが **claude-hub** だ。

**Discord Bot + ローカルMac常駐** という構成に切り替えて、ランニングコストをほぼゼロにした。iPhoneのDiscordアプリからメッセージを送るだけで、自宅のMacで動いているClaude Codeが応答する。しかもリアルタイムで。

!

**この記事で作れるようになるもの**

* iPhoneのDiscordから `/session start` でClaude Codeセッションを起動
* スレッド内でメッセージを送ると、ローカルのClaude Codeにリレーされる
* ツール実行の進捗がリアルタイムでDiscordに表示される
* 生成されたファイルが自動でスレッドに添付される
* Mac再起動しても自動復帰（launchd）

---

### なぜDiscord？

「なぜSlackじゃなくて？」「なぜWebアプリじゃなくて？」

答えはシンプルで、**iPhoneで一番手軽にリアルタイム通信できるクライアントがDiscord**だったから。

* プッシュ通知が確実に届く
* スレッド機能でセッションを分離できる
* ファイル添付（画像・ログ）が簡単
* Bot APIが無料で使い放題
* モバイルアプリの完成度が高い

Slack でもできるが、無料プランの制約がきつい。自前のWebアプリを作るのはオーバーキル。Discordが「ちょうどいい」。

---

### アーキテクチャ全体像

1つのメッセージが Claude Code に届いて応答が返るまでの流れ:

### マルチプロジェクト管理 — 1つのSupervisorで複数リポジトリを操る

claude-hub の核心は「1 Supervisor Bot が複数プロジェクトをオーケストラのように指揮する」構成だ。Discord のチャンネルがプロジェクトに対応し、スレッドがセッションに対応する。

**ポイント:**

* **1チャンネル = 1プロジェクト**: Discordのチャンネル名がそのままプロジェクトに対応
* **1スレッド = 1セッション**: `/session start` のたびに新スレッドが作られ、独立したClaude Codeセッションが立ち上がる
* **同時10セッション**: 異なるプロジェクトを並列で操作できる。team-salary のバグ修正をしながら、convert-service のテストを回す、といった使い方
* **Supervisor は指揮者**: メッセージの振り分け、セッションのライフサイクル管理、リソース監視をすべて1プロセスでこなす

| コンポーネント | 役割 |
| --- | --- |
| **Supervisor Bot** | 指揮者。Discord ↔ Claude Code の仲介、セッション管理、リソース監視 |
| **tmux** | Claude Code にTTYを提供。1セッション = 1 tmux session |
| **HTTP Relay Server** | Claude Code の hook からレスポンスを受け取る中継サーバー |
| **launchd** | macOS のプロセス管理。クラッシュしても自動復帰 |
| **caffeinate** | Mac のスリープを防止 |

---

### セットアップ

#### 前提条件

* macOS（Apple Silicon推奨）
* Claude Code CLI インストール済み（`claude` コマンドが使える状態）
* Bun ランタイム
* tmux
* Discord アカウント

#### Step 1: リポジトリクローン

```
git clone https://github.com/miyashita337/claude-hub.git
cd claude-hub/supervisor
bun install
```

#### Step 2: Discord Bot を作成

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」→ アプリ名を入力
3. 左メニュー「Bot」→「Reset Token」→ トークンをコピー
4. 「Privileged Gateway Intents」で **Message Content Intent** を ON

![Bot Intents 設定](https://res.cloudinary.com/zenn/image/fetch/s--ZNEazWeu--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://github.com/miyashita337/claude-hub/blob/main/docs/zenn-screenshots/discord-bot-intents-permissions.png%3Fraw%3Dtrue)

5. 左メニュー「OAuth2」→「URL Generator」
   * Scopes: `bot`
   * Permissions: View Channels, Send Messages, Send Messages in Threads, Read Message History, Attach Files

![OAuth2 URL Generator](https://res.cloudinary.com/zenn/image/fetch/s--nXpfxc9r--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://github.com/miyashita337/claude-hub/blob/main/docs/zenn-screenshots/discord-oauth2-url-generator.png%3Fraw%3Dtrue)

6. 生成されたURLを開いて、自分のサーバーにBotを追加

#### Step 3: 環境変数を設定

```
# Supervisor Bot のトークン（セッション管理用、1つだけ）
SUPERVISOR_BOT_TOKEN=ここにStep2でコピーしたトークン

# プロジェクト専用Botのトークン（チャンネルごとに1つ）
MY_PROJECT_BOT_TOKEN=...
```

なぜBotが複数必要なのか？

claude-hub は **1 Supervisor Bot + N 専用Bot** の構成を取っている。

* **Supervisor Bot（1つ）**: `/session start` などの slash command を受け付け、セッション管理を行う指揮者。全チャンネルを監視する
* **専用Bot（プロジェクトごと）**: 各チャンネルでClaude Codeの応答を中継する実行者。Discord の Gateway 制約（1トークン = 1接続）のため、チャンネルごとに別Botが必要

1つのBotで全チャンネルを見ることも技術的には可能だが、Discord のレート制限やトークン管理の観点から、プロジェクトごとに分離した方が安定する。最小構成（プロジェクト1つ）なら Bot 2つで始められる。

#### Step 4: チャンネルマッピングを設定

`supervisor/src/config/channels.ts` を編集して、Discord のチャンネル名とローカルのプロジェクトディレクトリを紐づける。

```
export const CHANNEL_MAP = new Map<string, ChannelConfig>([
  ["my-project", {
    channelName: "my-project",
    projectDir: "/Users/yourname/my-project",
    botTokenEnvKey: "MY_PROJECT_BOT_TOKEN",
  }],
]);
```

#### Step 5: launchd で常駐化

```
# plist をコピー
cp com.claude-hub.supervisor.plist ~/Library/LaunchAgents/

# パスを自分の環境に合わせて編集

# 起動
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claude-hub.supervisor.plist

# 確認
launchctl list | grep com.claude-hub
```

#### Step 6: 動作確認

Discordサーバーで `/session start` を実行。

![/session start でスレッド作成](https://res.cloudinary.com/zenn/image/fetch/s--GyBPPIaO--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://github.com/miyashita337/claude-hub/blob/main/docs/zenn-screenshots/discord-session-start.png%3Fraw%3Dtrue)

スレッド内でメッセージを送ると、Claude Code が応答する。

![セッション内の会話](https://res.cloudinary.com/zenn/image/fetch/s--7yTe1xbh--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://github.com/miyashita337/claude-hub/blob/main/docs/zenn-screenshots/discord-session-conversation.png%3Fraw%3Dtrue)

---

### セキュリティに関する注意

この構成は「ローカルMacを外部（Discord）から操作可能にする」ものだ。以下の点に注意してほしい。

!

**Bot トークンの管理**

* Discord Bot のトークンは `.env` に保存し、**絶対にgitにコミットしない**（`.gitignore` に含める）
* トークンが漏洩した場合、第三者がBotを通じてあなたのMacでClaude Codeを実行できてしまう
* 定期的に Developer Portal からトークンをリセットすることを推奨

**Discord サーバーのアクセス制御**

* Bot を追加するサーバーは**プライベートサーバー**にする（公開サーバーに追加しない）
* サーバーへの招待リンクを不用意に共有しない
* 必要に応じてサーバーの「認証レベル」を引き上げる

**Claude Code の実行権限**

* `--dangerously-skip-permissions` で起動するため、Claude Code はファイルの読み書き・コマンド実行を制限なく行える
* 信頼できるプロジェクトのみを `CHANNEL_MAP` に登録すること

---

### 前作からの改善点

| 項目 | 前作（GitHub Actions版） | claude-hub（Discord版） |
| --- | --- | --- |
| ランニングコスト | GitHub Actions 従量課金 + Tailscale | **ほぼゼロ** |
| レイテンシ | Issue作成 → Actions起動で数十秒 | **リアルタイム** |
| 双方向性 | Issue → 実装のみ（一方向） | **対話的** |
| 進捗確認 | Actions ログを見に行く | **プッシュ通知** |
| セッション管理 | なし（都度起動） | **常駐 + マルチセッション** |
| 復帰性 | Actions は毎回クリーン | **launchd 自動復帰** |

---

### 次回: 運用編

導入が完了したら、次は実際の運用で使う機能を解説する。

* リアルタイム進捗表示
* ファイル自動添付
* マルチプロジェクト対応
* クラッシュ耐性・リソース管理
* メタ依存ガード（claude-hub自身を管理対象にしない理由）

→ **[運用編]** に続く

<https://github.com/miyashita337/claude-hub>
