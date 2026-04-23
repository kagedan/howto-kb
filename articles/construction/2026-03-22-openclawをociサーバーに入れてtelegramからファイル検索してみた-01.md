---
id: "2026-03-22-openclawをociサーバーに入れてtelegramからファイル検索してみた-01"
title: "OpenClawをOCIサーバーに入れてTelegramからファイル検索してみた"
url: "https://zenn.dev/mezzopiano/articles/d2d8ed15a7633c"
source: "zenn"
category: "construction"
tags: ["zenn"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

## はじめに

「ファイルどこ行ったっけ？」という問題、世界中の人が毎日時間を費やしているはずです。これをAIエージェントで解決できないか、という思いから **OpenClaw** を触ってみました。

この記事では、Oracle Cloud Infrastructure（OCI）のサーバーにOpenClawをインストールし、Telegramのスマホアプリから自然言語でファイルを検索できるようにするまでの手順を紹介します。

LINEとの連携も試みましたが、かなり苦労しました。同じ道を歩む人のために、その顛末も詳しく書いておきます。

---

## OpenClawとは

[OpenClaw](https://openclaw.ai) は、オープンソースの自律型AIエージェントです。LLMを頭脳として使い、シェルコマンドの実行・ファイルの読み書き・Webブラウジングなどを自律的にこなしてくれます。

TelegramやLINE、Discordなどのメッセージングアプリをインターフェースとして使えるのが特徴で、スマホから自然言語で指示を出せます。

---

## なぜOCIサーバーに入れるのか

最初はMac miniにインストールしようと思っていましたが、やめました。理由はこうです。

OpenClawはLLMにファイルの内容を送ります。Mac miniには個人情報・写真・パスワードが大量にあるので、それがGeminiなどのクラウドLLMに送られるのはリスクがあります。

今回使った `minibar` というOCIサーバーは実験用なので個人情報がなく、万が一何かあっても本番サーバーに影響しません。**実験用サーバーに隔離する**というのが安全な使い方のポイントです。

---

## 環境

* サーバー: Oracle Cloud Infrastructure（Oracle Linux 8.10、aarch64）
* メモリ: 24GB
* ディスク: 89GB（空き35GB）
* AIプロバイダー: Google Gemini 2.5 Flash Lite（無料枠）
* チャンネル: Telegram

---

## インストール手順

### 1. Node.jsのバージョン確認

OpenClawはNode.js v22以上が必要です。

### 2. 古いNode.jsの削除（必要な場合）

Oracle Linux 8にはデフォルトでNode.js v10が入っていることがあります。そのままだとバージョン競合でインストールが失敗します。

```
sudo dnf remove -y nodejs nodejs-full-i18n
```

### 3. nvmでNode.js v22をインストール

nvmが入っている場合は古いデフォルトバージョンが使われることがあります。

```
nvm install 22 && nvm use 22 && nvm alias default 22
```

ターミナルを再接続して確認：

```
node --version
# v22.22.1
```

### 4. OpenClawのインストール

```
curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash
```

---

## セットアップ（オンボーディング）

インストールが完了するとオンボーディングが始まります。

### AIプロバイダーの選択

今回は **Google Gemini** を選択しました。無料枠で使いたいので、モデルは **gemini-2.5-flash-lite** にしました（1日1,000リクエストまで無料）。

### チャンネルの選択 ─ ここからが本題

チャンネル選択画面でLINEを選びました。ここから長い戦いが始まります。

---

## LINEとの格闘（読み飛ばし可）

### 最初の警告：「line does not support onboarding yet」

チャンネルにLINEを選ぶと、こんなメッセージが出ました：

```
line does not support onboarding yet.
```

「オンボーディング未対応」とはっきり書いてあります。ここで諦めれば良かったのですが、設定ファイルを手動で編集すればいけるはず、と思って続けました。

### nginx + HTTPSの準備

LINEのWebhookはHTTPSが必須です。`line.pontalk.com` というサブドメインを取得し、Let's Encryptで証明書を取得、nginxでリバースプロキシを設定しました。

```
location /webhook {
    proxy_pass http://127.0.0.1:18789/line/webhook;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 認証情報を手動設定

LINE DevelopersでMessaging APIチャンネルを新規作成し、チャンネルアクセストークンとチャンネルシークレットを設定しました。

```
openclaw config set channels.line.channelAccessToken "..."
openclaw config set channels.line.channelSecret "..."
openclaw config set channels.line.channelId "..."
```

### GETは200なのにPOSTだけ404

ここで謎の現象が起きました。

```
# GETは200
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18789/line/webhook
# 200

# POSTは404
curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:18789/line/webhook
# 404
```

GETは200を返すのに、LINEが実際に送ってくるPOSTは404になります。LINE DevelopersのWebhook検証ボタンを押すと、nginxのアクセスログにこんな記録が残りました：

```
"POST /webhook HTTP/1.1" 404 9 "-" "LineBotWebhook/2.0"
```

nginxまでは届いているのに、OpenClaw側が404を返しています。

### webhookPathのデフォルトが `/slack/events` だった

ソースコードを掘り下げてみると、`webhookPath`のデフォルト値がなんと `/slack/events` になっていました。SlackプラグインのコードがLINEに流用されていたようです。

```
grep -o 'webhookPath[^,}]*default[^,}]*' dist/auth-profiles-DDVivXkv.js
# webhookPath: z.string().optional().default("/slack/events")
```

`/line/webhook`を明示的に設定しました：

```
openclaw config set channels.line.webhookPath "/line/webhook"
```

しかし404は変わらず。

### `plugins.allow is empty` の警告が消えない

ログを見ると、こんな警告が繰り返し出ていました：

```
[plugins] plugins.allow is empty; discovered non-bundled plugins may auto-load: line
```

設定には `plugins.allow: ["line"]` が入っているのに、起動するたびに「allowが空」と言い続けます。

### 「running, works」なのに「token not configured」という矛盾

```
openclaw channels status --probe
```

の結果がこうでした：

```
- LINE default: enabled, configured, running, mode:webhook, token:config, works
Warnings:
- line default: LINE channel access token not configured
- line default: LINE channel secret not configured
```

「running, works」と「token not configured」が同時に出る謎の矛盾。設定は正しく入っているのに、doctorは「設定されていない」と言い続けます。

### LINEプラグインにコンパイル済みファイルがない

プラグインのディレクトリを確認すると：

```
ls ~/.nvm/.../openclaw/extensions/line/
# index.ts  openclaw.plugin.json  package.json  src/
```

`.ts`ファイルしかありません。コンパイル済みの`.js`ファイルが存在しないのです。他のチャンネル（Telegramなど）はOpenClaw本体の`dist/`に内蔵されているのに、LINEだけTypeScriptのソースのままでした。

### 全パス総当たりで全部404

最終確認として全パスを総当たりしました：

```
for path in /webhook /line /line/webhook /channels/line/webhook; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:18789$path)
  echo "$path -> $code"
done
# /webhook -> 404
# /line -> 404
# /line/webhook -> 404
# /channels/line/webhook -> 404
```

**Webhookルート自体がGatewayに登録されていない**という結論に至りました。

### 結論：LINEは現時点では使えない

ログには `[default] starting LINE provider (Ken's OpenClaw)` と表示されるので、プロバイダーは起動しています。しかしWebhookのHTTPルートが一切登録されていません。オンボーディング時の「line does not support onboarding yet」というメッセージは、文字通り「LINEはまだ完成していない」という意味だったようです。

約2時間を費やして出た結論：**LINEは諦めてTelegramを使いましょう。**

---

## Telegramの設定（あっさり完了）

LINEで2時間消耗した後、Telegramに切り替えたら**10分で動きました。**

### Telegramボットの作成

1. Telegramアプリを入れてアカウント作成
2. `@BotFather` を検索して開く
3. `/newbot` を送信
4. ボット名（例：Ken's Claw）を入力
5. ユーザー名（`_bot`で終わる、例：`kens_claw_minibar_bot`）を入力
6. APIトークンをコピー

### OpenClawにTelegramを追加

オンボーディングを再実行してTelegramを選び、APIトークンを貼り付けるだけです。

### ペアリング

スマホからボットにメッセージを送ると：

```
OpenClaw: access not configured.
Your Telegram user id: XXXXXXXXXX
Pairing code: XXXXXXXX
Ask the bot owner to approve with: openclaw pairing approve telegram XXXXXXXX
```

サーバー側で承認：

```
openclaw pairing approve telegram XXXXXXXX
```

以上で完了です。

---

## 実際に使ってみる

スマホのTelegramからこんなメッセージを送ってみました：

> minibarのホームディレクトリにあるSQLファイルを全部探して一覧にしてください。

するとKen's Clawが `find` コマンドを実行して、SQLファイルの一覧を返してくれました。

> ホームディレクトリで一番大きいファイルを10個教えてください。

これも即座に `du` コマンドを実行して結果を返してくれました。このとき、6.5GBあったMariaDBのビルドディレクトリ（ソースからビルドした作業残骸）を発見。削除してディスクを6.5GB解放できました。

---

## 仕組みを理解する

OpenClawの動きはこうなっています：

```
スマホ（Telegram）
    ↓ メッセージ送信
Ken's Claw（minibar上のOpenClaw）
    ↓ Geminiに送る
Gemini 2.5 Flash Lite（Googleのクラウド）
    ↓ 「findコマンドを実行して」と判断
Ken's Claw（minibar）
    ↓ シェルコマンドを実行
Gemini
    ↓ 結果を日本語でまとめる
スマホ（Telegram）
    ↓ 返答が届く
```

**「考える」のはGemini（クラウド）、「実行する」のはminibar**という役割分担です。

ここで重要なのは、**ファイルの内容がGeminiのクラウドに送られる**という点です。個人情報や機密情報があるマシンには入れないようにしましょう。

---

## セキュリティについて

OpenClawはシェルコマンドを実行できるので、使い方には注意が必要です。

今回設定したSOUL.md（エージェントの行動原則）：

```
1. 行動する前によく読み観察すること
2. 明示的な許可なくファイルを削除・移動しないこと
3. 不明な点は尋ねること
4. 直接的な行動よりもレポート作成を優先すること
5. 常に日本語で応答すること
```

特に **2番と4番** が重要です。最初は「読む・報告する」だけに留めて、信頼できたら少しずつ権限を広げていくのが安全な使い方だと思います。

また、`sudo` がパスワードなしで動くサーバーでは特に注意が必要です。

---

## 今後の展望

「ファイルを自然言語で探す」という体験は、OpenClawを使って初めて実感できました。

* 「あの確定申告の書類どこだっけ」
* 「先月作ったあのスクリプトどこにある？」
* 「容量食ってる古いファイルを教えて」

これらが全部スマホから自然言語で解決できる。SpotlightやWindows Searchが「なんとなく使える」止まりなのは、ファイル名や場所を覚えていないと検索できないからです。「あの犬が写ってる写真」「去年の確定申告の書類」のように**中身で探せる**のがAIの強みで、OpenClawはその入り口を見せてくれました。

---

## まとめ

* OCIの実験用サーバー（minibar）にOpenClawをインストール
* Google Gemini 2.5 Flash Liteを無料枠で使用
* Telegramからスマホで自然言語ファイル検索ができるようになった
* **LINEは2026.3時点では動かない（Telegramを推奨）**
* 個人情報があるマシンには入れない方がよい
* 最初は「読む・報告する」だけに限定して使うのが安全

OpenClawはまだbetaですが、AIエージェントの可能性を体感できるおもしろいツールです。ぜひ試してみてください。
