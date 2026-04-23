---
id: "2026-04-08-clauderssと定期実行でニュースをまとめて作るマイ朝刊-qiita-01"
title: "Claude:RSSと定期実行でニュースをまとめて作るマイ朝刊 - Qiita"
url: "https://qiita.com/Fuses-Garage/items/88ffbc602c7950059705"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-08"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

# まえがき

皆さんどうもこんにちは。ECN技術部所属のFuseです。  
皆さんは最近ニュースを見ていますか？私は忙しくて見れていません。  
AI関連のニュースが多く、うかうかしていると乗り遅れてしまうこの時代、どうにかしてニュースを見る習慣を付けたいとは思っているのですが、やはりめんどくさいが勝ってしまいます。  
そこで私は考えました。  
**主要AIのアップデートや新機能のリリース、新しいAIなどのニュースをClaudeにまとめさせ、要約させてSlackに毎朝朝刊のように貼りだしてもらえば、Slackを開いたついでにニュースを読む習慣がつくのでは…？**  
~~ついでに記事のネタも見つけやすくなって一石二鳥というわけです~~

# 構想

(イメージ図はChatGPTに生成してもらいました)

## Step1:ClaudeにRSSからよさげな記事を集めてもらう

RSSフィードからAI関連の新機能のリリースや新しいAIなどの情報をまとめてきてもらいます。  
[![Step1 (中).png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2F38ec8ebe-c064-4103-8a57-a195c528ee48.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=58d30b0c1f65bbe66a4209dc1b7ce3d4)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2F38ec8ebe-c064-4103-8a57-a195c528ee48.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=58d30b0c1f65bbe66a4209dc1b7ce3d4)

## Step2:Claudeに要約してもらう

Step1で集めた記事をわかりやすく要約してもらい、記事を読まずとも大まかな内容を読み取れるようにしてもらいます。  
[![Step2.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2F239daa6f-0e06-48f0-a91e-59547189df39.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=252e0f0ec499c628694238a0324e77fa)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2F239daa6f-0e06-48f0-a91e-59547189df39.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=252e0f0ec499c628694238a0324e77fa)

## Step3:Webhookを使ってSlack上に投函してもらう

ClaudeからWebhookを介しSlack上に投函してもらいます。  
[![Step3.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2F18ace7d3-b380-43dc-a226-d71e1210cfb5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c44c8e311016e93695029bbe7e03668c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2F18ace7d3-b380-43dc-a226-d71e1210cfb5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c44c8e311016e93695029bbe7e03668c)

# やってみる

## 事前準備:WebhookURLの作成

スケジュールを作る前に、あらかじめSlackに投稿するためのWebhookURLを用意する必要があります。  
アプリを作成し、サイドバーの**Incoming Webhooks**で項目に移動、**Activate Incoming Webhooks**スイッチをオンにしてWebhookを有効化したら**Add New Webhook**からWebhookを作成してください。

## 技術選定:3つのタスクの種別について

|  | Cloud | Desktop | /loop |
| --- | --- | --- | --- |
| 実行場所 | クラウド上 | ローカルマシン上 | ローカルマシン上 |
| マシンの電源を付けている必要が | ない | ある | ある |
| セッションを開いている必要が | ない | ない | ある |
| マシン再起動時に持ち越せる | 持ち越せる | 持ち越せる | 持ち越せない |
| ローカルファイルへのアクセスが | できない | できる | できる |
| MCPサーバー | タスクごとに指定したコネクタのみ使用可能 | コンフィグファイルで指定したものとコネクタ | セッションから引き継ぐ |
| 操作前の確認 | なし(自律的に動作) | タスクごとに設定可能 | セッションから引き継ぐ |
| スケジュールをカスタマイズ | CLIを使えば可能 | できる | できる |
| 最短実行間隔 | 1時間 | 1分 | 1分 |

ClaudeCodeにおける定期実行の方法は大きく分けて

* リモートで実行する"Cloud"
* ローカルマシン上で実行する"Desktop"
* セッション上で実行する"/loop"  
  の3種類あり、それぞれできること、できないことがあります。  
  今回は
* ローカルファイルへのアクセスが不要
* PCを開いていない時も実行する必要がある
* 実行頻度は1日に1回でいい

の3点からCloudを採用します。

## フィード指定用githubリポジトリの作成

今回指定するRSSフィードを管理するためのgithubリポジトリを作成します。  
新しく作成したリポジトリに、今回使うRSSフィードを列挙したファイル`rsslist.md`をpushします。

rss.md

```
# 大手AI企業のブログと大手AIのアップデート情報
## OpenAI Blog
https://openai.com/blog/rss.xml
## Google Research Blog
https://feeds.feedburner.com/blogspot/gJZg
## ClaudeCode ChangeLog
https://code.claude.com/docs/en/changelog/rss.xml
## Gemini Code Assist release notes
https://developers.google.com/feeds/gemini-code-assist-free-release-notes.xml
# 日本のAIに関するテックブログ
## 人工知能ニュースメディア AINOW
http://ainow.ai/feed/
## AI Database
https://ai-data-base.com/feed
## ITmedia AI＋
https://rss.itmedia.co.jp/rss/2.0/aiplus.xml
## ＠IT Smart & Socialフォーラム
https://rss.itmedia.co.jp/rss/2.0/ait_smart.xml
## AI MEDIA
https://ai-media-bsg.com/feed/
# 海外のテックブログ
## The Verge
https://www.theverge.com/rss/index.xml
## Ars Technica
https://feeds.arstechnica.com/arstechnica/index
## TechCrunch
https://techcrunch.com/feed/
```

## クラウド環境の作成

次に定期実行用にカスタムされた環境を作成します。環境はこのボタンから作成できます。  
[![CloudButton.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2F80fda176-ce45-453e-b70e-e8fd08a89ec6.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cf91e73f06db615cdb40c8ae5fe27e1c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2F80fda176-ce45-453e-b70e-e8fd08a89ec6.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cf91e73f06db615cdb40c8ae5fe27e1c)  
モーダルが開くのでネットワークアクセスを"カスタム"に設定し、許可されたドメインに"hooks.slack.com"を追加、環境変数WEBHOOK\_URLに先ほど作成したWebhookURLを設定し作成しましょう。  
[![CloudModal.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2Ff9518c91-b03d-46ef-8863-fd3ca5b88006.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1f8767f9e9d91ae5f1cce1989ee4504a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2Ff9518c91-b03d-46ef-8863-fd3ca5b88006.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=1f8767f9e9d91ae5f1cce1989ee4504a)

## リモートタスクの作成

こちらのチュートリアルをもとに進めていきます。  
<https://code.claude.com/docs/en/desktop-scheduled-tasks#create-a-scheduled-task>  
まずはコードタブにてサイドバーの「予定済み」をクリック、  
[![TaskStep1.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2F4b2743a4-a8fa-44af-83da-99f1484b825f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c6991e22182278de1de8437e1824c112)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2F4b2743a4-a8fa-44af-83da-99f1484b825f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c6991e22182278de1de8437e1824c112)  
新しいタスクボタンから新しいリモートタスクを作成します。  
[![TaskStep2.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2F71a21f9b-4d39-4b8d-be7f-41d68690c359.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a20ebe7b197f5f59a5b613bf615e13df)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2F71a21f9b-4d39-4b8d-be7f-41d68690c359.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a20ebe7b197f5f59a5b613bf615e13df)  
情報入力のためのフォームが開きました。  
タイトルを「AIニュース朝刊配達」、実行時間を朝8時とします。  
今回のプロンプトは以下の通りです。

```
以下の3つのタスクを順番に実行してください。
# タスク1:RSSフィードからの情報の収集
WebSearchツールを使ってrsslist.mdに書かれているRSSフィードからここ数日のAIの新機能のリリース、新しいAI、新しいAIサービスなどの生成AIにまつわるニュースを収集してください。
# タスク2:収集したニュースの要約
タスク1で収集したニュースを記事ごとに
+ 見出しとニュースの日付
+ わかりやすく要約した大まかな内容
+ 出典
をまとめ、記事を読まずとも大まかな内容を読み取れるようにしてください。
# タスク3:生成物の投稿
WEBHOOK_URLに設定されたSlackWebHookURLを使い「#aiニュース朝刊」チャンネルに生成物を投稿してください。
```

最後にリポジトリと実行環境を先ほど作成したものにすれば完成です！  
[![TaskStep4.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2Fcbab2c74-5eaa-49be-ae37-6601ec648866.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f13202a14ce865a71819c56785ddf45a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2Fcbab2c74-5eaa-49be-ae37-6601ec648866.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f13202a14ce865a71819c56785ddf45a)  
試しに手動実行してみたところ、無事Slackに投稿されました！  
[![Result.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2Fbc4beb6e-6277-4e67-9ee9-670a5c2478d5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=005191fcea26f58e72dd6ff84aa0799e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2Fbc4beb6e-6277-4e67-9ee9-670a5c2478d5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=005191fcea26f58e72dd6ff84aa0799e)

# あとがき

今回はClaudeCodeの定期実行機能を使って毎朝Slackにニュースのまとめが届くシステムを作ってみました。  
毎朝こうして朝刊が届けば、ニュースを読む習慣もきっとつくはず！

---

[![株式会社ECN](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F2957248%2Fba770058-3650-4482-8cf6-7b61919b1ca9.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5fc3b160f5c46812201b71ea8e2c6689)](https://www.ecninc.co.jp/)  
株式会社ECNはPHP、JavaScriptを中心にお客様のご要望に合わせたwebサービス、システム開発を承っております。 ビジネスの最初から最後までをサポートを行い お客様のイメージに合わせたWebサービス、システム開発、デザインを行います。
