---
id: "2026-05-16-aws公式のナレッジmcpサーバーをclaudeに繋いでみる-01"
title: "AWS公式のナレッジMCPサーバーをClaudeに繋いでみる"
url: "https://zenn.dev/take5553/articles/aws-knowledge-mcp-on-claude"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

# AWS公式のMCPサーバー

## ナレッジMCP

そのまま、ナレッジを効率よく集めるMCPサーバー。公式ドキュメントや新着情報に加えて、AWS Blogやコードテンプレートなんかにもアクセスできるので、AIが出してくる情報の正確性が上がる。

<https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server/>

## CLI MCP

名前としてはAPI MCPとしているけど、CLIを介してAWSサービスやリソースにアクセスできるとあるので、まあほぼAIが裏でAWS CLIを使えるようにするMCPと思ってもいいかなー。使ってないから知らんけど。

<https://awslabs.github.io/mcp/servers/aws-api-mcp-server>

## AWS MCP

AWSを直接触らせるためのMCPサーバー。リリースされたばかり。東京リージョンではまだ利用可能ではないらしい。

<https://aws.amazon.com/jp/blogs/news/the-aws-mcp-server-is-now-generally-available/>

# ナレッジMCPを導入してみる

ちゃんと最新の、かつ正確な情報を取ってきてくれるのは非常にありがたいので導入してみる。Claudeのサブスクアカウントから入れてみる。

## MCPサーバーのURL

```
https://knowledge-mcp.global.api.aws
```

以下より引用

<https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server#configuration>

## 「コネクタ」として登録

claude.aiにログインして、左の「カスタマイズ」からコネクタの新規登録ボタンを押し、「カスタムコネクタを追加」に進む。

![CleanShot 2026-05-16 at 19](https://static.zenn.studio/user-upload/deployed-images/ea9f7b7bc11e2505d5d20e60.png?sha=aaa0c39f5ed7d8fae8fcb1eea7f173d8caff1340)

名前は分かれば何でもよくて、リモートMCPサーバーURLに上記URLを貼り付けて「追加」をクリック。

![CleanShot 2026-05-16 at 19](https://static.zenn.studio/user-upload/deployed-images/1aee195bab41c62d5a640270.png?sha=720b55dc871d87a088ea53cbe0027b4d21c4655d)

すると以下のように表示される。認識されている（はず）。

![CleanShot 2026-05-16 at 19](https://static.zenn.studio/user-upload/deployed-images/2faf1765d25e4ec68822d134.png?sha=4db9e76c098ff36eb5829ff812987442196904c0)

# テストしてみる

最新の情報だったら絶対知らないだろうと思って、今日発表された最新ニュースを調べるように言ったら普通にWebから引っ張ってきたので、MCP導入したことを伝えてもう一度調べさせた。

> コネクタ、ありがとうございます。AWS関連のツールが利用可能になっているか確認してみますね。
>
> （コネクタを確認する）
>
> はい、AWS Knowledge MCPのコネクタが認識できました。これはAWS公式ドキュメント・What's New・トラブルシューティング情報などを検索・取得できるツール群です。
>
> 実際に、本日付近のWhat's Newをこのコネクタから取れるか試してみますね。
>
> （実際に試してみる）
>
> 検索結果から、本日5月16日付ピンポイントの発表は出てきませんでした。AWS Knowledge MCPは日付では絞り込みにくい設計なので、もう少し試してみますね。
>
> （やり方を変えて試してみる）
>
> `recommend`は`docs.aws.amazon.com`配下しか受け付けないようなので、別の角度から最新のWhat's Newを引っ張ってみます。
>
> （もうちょっと頑張ってみる）
>
> なるほど、AWS Knowledge MCPは「日付指定で本日のリリースをリストする」という用途には向いていないようです。基本的にはトピックや機能名に対するセマンティック検索ベースで、すでに発表されたドキュメントを引き出す設計のようですね。
>
> 短くまとめると:
>
> **できること**
>
> このコネクタ（AWS Knowledge MCP）で取得できるのは、AWS公式ドキュメントに紐づいた情報です。具体的には:
>
> * AWS公式ドキュメント（`docs.aws.amazon.com`配下）の検索と本文取得
> * What's New ページ個別記事の検索（タイトル・要約が引ける）
> * トラブルシューティング・APIリファレンス・CDKサンプル・CloudFormationテンプレートの検索
> * AWS Knowledge Centerやブログ記事の取得
> * 「AWSスキル」と呼ばれる、ドメイン別のワークフロー知識パッケージ（Bedrock運用、IAM、コスト最適化、メッセージング系など）の取得
> * AWSリージョン一覧の取得
>
> たとえば「Bedrockのプロンプトキャッシュってどう設定する？」「DSQLって何ができる？」「このエラーコードの解消法は？」みたいな質問には、私の学習データ任せではなく、AWSの一次情報を直接引いて答えられるようになります。
>
> **できないこと（今日試した範囲で）**
>
> 「今日発表されたニュース」については、引き続きWeb検索のほうが日付軸では強いので、用途に応じて使い分ける形がよさそうです。一方で、たとえば「Terraformからのドリフト検知関連でAWS公式が推奨している運用パターン」みたいに**公式ドキュメントに根拠を求めたい質問**だと、このコネクタが効きます。

そうなんか🥹

とりあえず使ってくれていることは分かったので良しとする。
