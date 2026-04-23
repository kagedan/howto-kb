---
id: "2026-04-05-chatgptやclaudeからformlovaを触り始める最短ガイド-01"
title: "ChatGPTやClaudeからFORMLOVAを触り始める最短ガイド"
url: "https://qiita.com/lovanaut/items/15fb6f0703f114000b78"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "Gemini", "GPT", "qiita"]
date_published: "2026-04-05"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

[![Gemini_Generated_Image_9wdgew9wdgew9wdg.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4385658%2F1292b1df-9415-41db-8ba2-19b0e4570f8f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=311d4162b80508d9245113ee07e59d7e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4385658%2F1292b1df-9415-41db-8ba2-19b0e4570f8f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=311d4162b80508d9245113ee07e59d7e)

この記事では、ChatGPTまたはClaudeからFORMLOVAを触り始めて、フォーム下書きから公開前レビューまで進める最短手順をまとめます。

フォーム作成に時間をかけるのはナンセンスです。短いプロンプトで下書きを出し、そこから直していくのが正しい使い方です。

## この記事でやること

1. MCP接続を済ませる（Step 0）
2. 短いプロンプトでフォーム下書きを作る
3. 公開前レビューをかける
4. 指摘を見てそのまま直す

## Step 0: MCP接続を済ませる

FORMLOVAはMCPサーバー経由で動きます。最初にAIクライアントとの接続設定が必要です。

**接続手順はこちら:**

クライアントごとの設定手順は[セットアップガイド](https://formlova.com/ja/setup)にまとまっています。Claude Desktop、ChatGPT、Cursor、Windsurfなど、MCP対応クライアントであればどこからでも接続できます。OAuth認証が走るので、FORMLOVAアカウントでログインすれば接続完了です。

ここさえ終われば、あとは自然言語で会話するだけで進みます。

## Step 1: 短いプロンプトでフォームを作る

最初から仕様書のような長文は要りません。FORMLOVAは先回りして必要なことを聞いてくれる設計なので、一文で十分です。

まずはこれをコピーして送ってみてください。

もう少し具体的にしたい場合はこちら。

```
3月15日の社内サミット用に参加登録フォームを作って。名前、メールアドレス、会社名、役職、食事制限、Tシャツサイズを聞きたいです。
```

大事なのは完璧に書くことではなく、まず[下書きを出す](https://formlova.com/ja/blog/one-shot-form-draft)ことです。会話のラリーの中で足りない部分を補えます。

[![Gemini_Generated_Image_9wdgew9wdgew9wdg.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4385658%2F9363ab4c-2fa9-45fc-800d-b18535f5f569.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=49c3bd0141021f7de02c59a957af3324)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4385658%2F9363ab4c-2fa9-45fc-800d-b18535f5f569.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=49c3bd0141021f7de02c59a957af3324)

## Step 2: 下書きが出たら、公開前レビューをかける

下書きが出た時点で終わった気になるのが最大の落とし穴です。FORMLOVAの価値はここから先にあります。

次の一文を送ってください。[公開前レビューの詳細はこちら](https://formlova.com/ja/blog/publish-review-guide)。

レビューでは次の観点がチェックされます。

* 必須項目に漏れがないか
* ラベルが分かりにくくないか
* 公開して困る文言がないか
* 入力者が迷いそうな箇所がないか

## Step 3: 指摘が出たら、そのまま続けて直す

レビュー結果を見たら、会話を切らずにそのまま修正できます。

```
必須項目だけ残して、Tシャツサイズは任意にしてください
```

最初から完璧なプロンプトを書くより、「下書き → レビュー → 微調整」のサイクルを回すほうが速いです。

## 躓きやすいところ

### MCP接続の初回設定

一番多い詰まりポイントです。各クライアントの設定場所が分かりにくいので、Step 0の表を参照してください。接続さえ終われば、あとは普通のチャットと同じです。

### 最初のプロンプトを長く書きすぎる

短くて大丈夫です。フォームの種類さえ伝わればあとから直せます。FORMLOVA側が足りない情報を聞いてくるので、会話のラリーで進めてください。

### 下書きが出た時点で終わった気になる

ここが一番重要です。FORMLOVAはフォーム作成だけでなく、公開前レビューや公開後の運用（[回答管理](https://formlova.com/ja/blog/response-status-guide)、メール送信、分析）に価値があります。最初の体験でも「公開前レビュー」までは必ず通してください。

## まとめ

最初に必要なのは4ステップだけです。

1. MCP接続を済ませる（[セットアップガイド](https://formlova.com/ja/setup)）
2. 短いプロンプトでフォームを作る
3. 公開前レビューをかける
4. 指摘を見て微調整する

次に進むなら、公開後の運用まで試すのがおすすめです。

FORMLOVAは無料で始められます。フォーム数も回答数も無制限です。

---

FORMLOVAの思想や技術設計の背景はこちらで書いています:

最後にFORMLOVAは4月15日にProduct Huntでローンチします。共感いただけたら、応援いただけると嬉しいです: <https://www.producthunt.com/products/formlova?launch=formlova>
