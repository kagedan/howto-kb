---
id: "2026-04-14-openclawをraspberry-piで動かす手順claudeopenaiの切替付き-01"
title: "OpenClawをRaspberry Piで動かす手順（Claude→OpenAIの切替付き）"
url: "https://qiita.com/tatsuya1970/items/13d34ae0d00fd640361e"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

# はじめに

話題のOpenClawですが、  
自分のPCをセキュリティリスクにさらしたくなく、  
これまで導入を躊躇していました。

そこで、Raspberry Piのような独立したデバイス上でOpenClawを動かすことにしました。  
これなら、万が一何かあってもリスクは最小限に抑えられます。

# 使用機器

Raspbery pi 5

[![IMG_2889.jpg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F291592%2F8c257660-7b58-4567-8273-e6c258e83783.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ba57a30903accfc2d6c00dabbc74ec9f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F291592%2F8c257660-7b58-4567-8273-e6c258e83783.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ba57a30903accfc2d6c00dabbc74ec9f)

# Raspberry Piの設定

こちらの記事を参考に設定しました。  
<https://raspi-school.com/getting-started-with-raspberrypi/>

# OpenClaw のインストール

ラズパイのターミナルで以下実行

```
$ curl -fsSL https://openclaw.ai/install.sh | bash
```

インストールできました。

[![IMG_2901.jpg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F291592%2F2ba8efce-c73d-4f9b-ab53-d663465f53b0.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=207e6ec354a89c77c367fa5199193a87)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F291592%2F2ba8efce-c73d-4f9b-ab53-d663465f53b0.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=207e6ec354a89c77c367fa5199193a87)

セキュリティに関する注意事項が表示されるので、内容を確認して「Yes」を選択します。

[![IMG_2903.jpg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F291592%2Fa8ed691a-12d6-4f90-92cf-e62c404e5c74.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7364423acf1baef9321060c6a7d476be)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F291592%2Fa8ed691a-12d6-4f90-92cf-e62c404e5c74.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7364423acf1baef9321060c6a7d476be)

以下は私の設定例です。

AIモデル：Anthropic API  
認証方法：Anthropic API Key  
（APIキーは以下から取得）  
<https://console.anthropic.com/>

## Telegram

チャットツールは  
Telegram（Bot API）  
を選びました。

Telegramはあまり良いイメージを持たれないこともありますが、  
「誰でも簡単にBotを作れる」ため、結果的に悪用されるケースがあるだけで、  
本質的には普通のチャットツールです。  
（電話や自動車、包丁も使い方次第ですよね）

### Bot作成手順

スマホでTelegram開く  
設定 → デバイス → デスクトップデバイスをリンク

ラズパイのブラウザでテレグラムのログイン画面を開き、  
そこに現れたQRコードをスマホにかざす。

テレグラムにログインできたら、  
「BotFather」検索

BotFather開く  
/start  
/newbot

名前入力  
username入力（必ず最後に bot　をつける）

で、トークンが発行されます。

次からいろんな質問がくるけど、  
とりあえずは、全部「No」か「Skip」して、  
  
  
最後  
「How do you want to hatch your bot?」  
という質問に  
「Hatch in TUI」  
を選択する。

すると、  
Wake up, my friend!  
とメッセージが出る。

めでたく、OpenClawのAIエージェントが起動。

そして、ラスパイで開いてるテレグラムのBotに  
/start　を入力。

下の画像で赤で囲んだコマンドを、ラズパイのターミナルで実行します。

[![スクリーンショット 2026-03-29 18.10.32.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F291592%2Ff262d3cd-8849-4431-a682-89adf8e4f08c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=35dde8f4b8d9ace54e131376927cb10e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F291592%2Ff262d3cd-8849-4431-a682-89adf8e4f08c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=35dde8f4b8d9ace54e131376927cb10e)

おお、やっと接続完了！！

[![IMG_3089.jpg](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F291592%2F35a2cdaf-22fb-4d33-991e-9ed54245a36b.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3a7556a51ab61dc01b426b35e768b300)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F291592%2F35a2cdaf-22fb-4d33-991e-9ed54245a36b.jpeg?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3a7556a51ab61dc01b426b35e768b300)

## 再起動方法

で立ち上がります。

## おまけ（モデルをClaudeからOpenAIに変更する場合）

ClaudeはAPI料金が結構高いので、OpenAIに変更しました。

### ① OpenAI APIキーを作成

OpenAIの管理画面で作成

### ② .envの設定

環境変数を入力

.env

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
```

### ③API単体テスト

```
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

JSONが返ればOK

---

### ④ OpenClaw設定変更

```
nano ~/.openclaw/openclaw.json
```

Claudeになっているので、OpenAIに書き換えます。

```
"model": "anthropic/claude-sonnet-4-6"
```

↓

```
"model": "openai/gpt-4o-mini"
```

---

### ⑤ OpenClaw再起動

---

### ⑥ Telegramトークン確認

BotFatherで

取得したトークンを設定する。

```
"telegram": {
  "enabled": true,
  "token": "123456:xxxx"
}
```

---

### ⑦ 最終確認

OpenClaw起動時に以下が出ればOK

```
openai/gpt-4o-mini
connected | idle
```

Telegramで  
「こんにちは」と入力し、  
何か返答があれば成功 ！！

以上です。
