---
id: "2026-03-17-ブラウザで拾ってdiscordに送るだけの英単語収集復習基盤を作ったopenclaw-sqlite-01"
title: "ブラウザで拾ってDiscordに送るだけの英単語収集＆復習基盤を作った（OpenClaw × SQLite）"
url: "https://zenn.dev/dokusy/articles/58840a6c21e548"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## はじめに

最近英語学習に力を入れています。

学習の時に知りたい単語を保存する仕組みは簡単に作れるが、実際には見返さなくなる問題が起きやすいと思います。

なので今回はOpenClawを活用して次のような仕組みを構築しました！

* ブラウザで選択した単語をDiscordへ送信
* Discord投稿してOpenClawがSQLiteに記録
* 保存時に意味や例文を自動で返信
* 保存後は定期的にOpenClawがリマインダーをしてくれる

この記事ではブラウザ拡張とOpenClawを組み合わせた実装についてまとめました。

## まずはどんな感じのやつか紹介

1. ブラウザで知りたい単語を選択して、`shift + cmd + E`

![](https://static.zenn.studio/user-upload/75522ab8fd86-20260317.png)

2. DiscordでOpenClawが受け取って解説

![](https://static.zenn.studio/user-upload/9b79ed9265e5-20260317.png)

3. cronで定期的にリマインダーを送ってくる（ちょっと腹立つのが答えはいきなり送ってこない）  
   ![](https://static.zenn.studio/user-upload/8033781f1d94-20260317.png)
4. メンションして答えを聞く  
   ![](https://static.zenn.studio/user-upload/98adaa25a445-20260317.png)

## 全体像

今回の仕組みは2つの役割で構成しています。

**フロント側**  
ブラウザ拡張が選択テキストを取得して送信  
（ブラウザで `shift + cmd + E` を押すとOpenClawが待ち構えているDiscordへ送信）

**バックエンド側**  
OpenClawとPythonで保存と復習を管理

## アーキテクチャ

```
# ブラウザから保存までの流れ
[Google Chrome拡張機能]
    ↓ (Discord Webhook)
[Discord チャンネル]
    ↓ (OpenClawをメンション)
[OpenClaw]
    ↓
save_capture.py (Discordで送った英単語を保存するため）
    ↓
[SQLite]
ここまで
------------------------------------------------------------
# 定期実行の流れ
OpenClaw Cron
    ↓
review_due.py（復習タイミングに達した単語を毎日選び出して、出題済みを記録するスクリプト）
    ↓
Discord通知
ここまで
------------------------------------------------------------
# 管理
Web UI (保存したデータ閲覧用でFlask + Reactでアプリも)
```

## 前提環境

今回の構成は次の環境で動かしています。

### 構成

### 使用技術

* Python
* SQLite
* OpenClaw
* Discord Bot / Webhook
* Flask + React（管理UI）

### 事前準備

* Discordサーバー
* Botトークン
* Webhook URL
* OpenClawの設定

以上のように構成にした理由としては

* Piで常時動かせる
* cronで復習を自動化できる
* Discordで入力と通知を一元化できる

からです。

## ブラウザ拡張

役割はシンプルで次の4つです。

* 選択した単語や文章を取得
* 前後の文脈を取る
* URLやタイトルを付与
* Discord webhookに送信

## 送信フォーマットの詳細

拡張機能は次の形式でDiscordに送信するようにしています。

以下は例です。

```
#capture

text: highlight
context: I highlighted this word while reading an article.
url: https://example.com/article
title: Sample Article
domain: example.com
```

各フィールドの意味は次の通りです。

* text  
  ユーザーが選択した単語やフレーズ  
  例: highlight / take for granted / sustainable
* context  
  その単語が使われていた文や前後の文章  
  単語単体ではなく文脈ごと保存するのが重要
* url  
  取得元のページURL  
  後から復習する時に元記事に戻れる
* title  
  ページタイトル  
  どの記事だったかを把握しやすくするため
* domain  
  ドメイン名  
  例: nytimes.com / medium.com  
  情報ソースの傾向を見るのに使える

この情報があったら正確な英単語の意味を拾ってくれます。

このフォーマットはユーザーに入力させるのではなく拡張機能が生成します。

具体的に言うとユーザーが単語を選択して、その後 `shift + cmd + E` でDiscordに送信してくれます。

フォーマットを固定したことでOpenClaw側の処理が安定すると思います。

## SQLite保存

保存はPythonスクリプトで行います。  
この辺はOpenClawがよしなに処理してくれます。

```
python3 ~/dev/lexipick/save_capture.py "<text>" "<context>" "<url>" "<title>" "<domain>"
```

DBは冒頭に書いた通りSQLiteです。

## 重複保存対策

Webhookや拡張は必ず再送が起きることが多いかと思います。  
例えばブラウザの拡張機能の送信コマンドを長押しとか。

同一データが5分以内に同じものがあれば保存しない対策などです。  
この辺の対策もOpenClawが良い感じ対応してくれました。

## Webhookが反応しない問題

ここが地味にハマったポイントです。

**現象**  
Webhook投稿してもOpenClawが反応しない

**原因**  
**”Webhookはbot扱い”**  
OpenClawはデフォルトでbotを無視します。

## 解決方法

設定でallowBotsを有効にする

```
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "DISCORD_BOT_TOKEN",
      "allowBots": true,
      "guilds": {
        "YOUR_GUILD_ID": {
          "requireMention": true,
          "channels": {
            "YOUR_CAPTURE_CHANNEL_ID": {
              "allow": true,
              "requireMention": true
            }
          }
        }
      }
    }
  }
}
```

ただしこれだけでは危険でして  
必ず制限とセットで使うことが大事なようです。

* mention必須
* チャンネル限定
* #captureのみ処理
* 重複排除

あと無限ループにも要注意です

## 保存時の返信

保存したあとに解説を返すようにしています。

```
Saved 📚 word

意味: ...
ニュアンス: ...
例文: ...
```

これで保存だけで終わらず理解まで進みます。

## 復習機能

タイミングは「エビングハウスの忘却曲線」にしました（この言葉使ってみたかった）

これで忘却しないはず

## 実装

review\_due.pyを作成してOpenClawから以下のように呼び出します。

```
openclaw cron add \
  --name "lexipick-review" \
  --cron "0 8 * * *" \
  --tz "Asia/Tokyo" \
  --session isolated \
  --no-deliver \
  --message "Run: python3 /home/kasa/dev/lexipick/review_due.py --limit 3 --mark-sent . If output is exactly NO_DUE, reply NO_REPLY. Otherwise send the output text to Discord channel channel:YOUR_CHANNEL_ID via message tool (channel=discord), then reply NO_REPLY."
```

## 管理Webアプリ

検証で単語を送りまくったのでFlaskとReactで簡易UIも一応用意しました。

機能としては

起動

```
python3 /home/kasa/dev/lexipick/webapp/app.py
```

この辺もOpenClawが良い感じに作ってくれます。

## まとめ

単語を保存する仕組み自体はそこまで難しくないと思いますが、難しいのは「続く形」にすることだと思います。

なので今回の構成で意識したのは次の2つで

* 何も考えずに保存できる導線
* 自然に思い出させる復習の仕組み

ブラウザで見つけた単語をその場で投げるだけで保存されて、あとで思い出すきっかけが届く。

この流れができると意識しなくても語彙が積み上がっていくと思います。

シンプルな仕組みですが、これからの英語学習体験がかなり変わるのではとワクワクしています！
