---
id: "2026-04-04-claude-desktopcowork-のconnectorsの申請をしてみたローカル動作確認方法-01"
title: "Claude Desktop・cowork のConnectorsの申請をしてみた（ローカル動作確認方法付き）"
url: "https://zenn.dev/ytakehir/articles/f08090e0adc326"
source: "zenn"
category: "cowork"
tags: ["cowork", "zenn"]
date_published: "2026-04-04"
date_collected: "2026-04-05"
summary_by: "auto-rss"
---

## TL;DR

* Google Formからの申請だった
* 審査のスピードなどは記載がなかった（通常n営業日以内みたいなやつ）
* ユースケースやテストアカウントを用意する必要があった

## はじめに

個人開発のツールをDesktopでも配布したかったので、Connectorsの申請をしました

記事を書こうと思った理由は、日本語で書かれている申請手順がなかったため（英語でもほとんどない）  
自分の作ったサービスの宣伝も兼ねてますので、大目に見てください

2026/4/4  
まだ申請途中なので、フォーム送信後のことは書いてません（進展があれば追記します）

## そもそもConnectorsとは？

"Claude"とタイトルに書いてあったから読んでくださった方もいると思うので、軽く説明します

"MCPをDesktop Appでも使えるようにするもの"とか"Desktop App版のMCP"という認識で問題ないです  
有名どころだと、google chromeやFilesystem等が用意されています

Connectorsとして利用できるようになると、以下でもMCPとして利用できるようになります

* Claude.ai (web)
* Claude desktop
* cowork

## 申請の手順

お待たせしました  
以下が、申請の手順になります

### 1. MCPを作成して、httpsとして公開する

中身はMCPのため、MCPを作成します  
ただ、4点注意点があります

#### httpsとして作成する

ローカルで動作確認やデバッグをする際でもhttpsの必要があります  
CLI向けのmcpはlocalhostでも動作確認できましたが、Desktop系はhttpsの必要があります（Chatgptも同じく）  
そのため、開発中に動作を見たくなったら、Cloudflare等でトンネリングするか、preview環境等にデプロイする必要があります

#### 顧客サポートを充実させる

プライバシーポリシー、問い合わせ、ドキュメントは必須項目となってます  
また、これもhttpsで公開する必要があります

#### ツールの説明を充実させる

すべてのツールに `readOnlyHint` または `destructiveHint` を追加する必要があります  
ここが不足していると、リジェクト対象になるそうで、かなり多いらしいです

#### 拡張できる設計にする

現時点では必須ではないのですが、後々必要になってくるので、こうしておいたほうがいいと言うのを紹介します

* 認証が必要な場合にOAuth2.0にする必要がありますが、静的クライアントではなく動的クライアント（DCR or CIMD）にする  
  → Claudeは静的クライアントでも受け付けてくれますが、Chatgptが動的を必須としてます  
  そのため、動的クライアントで認証を作成することをおすすめします（ChatgptはCIMDを推しているのでCIMDで作成できるのが、ベストです）
* SSEではなく、Streamable HTTPで作成する  
  → Claudeが今年後半からSSEのサポートを終了するそうです（フォーム内にしれっと記載がありました）

### 2. テストアカウント、データを用意する

#### テストアカウント

テスターは、`mcp-review@anthropic.com`でアカウント作成しようとするので、対応していないといけないです（マジックリンクか事前にDBにアカウント情報を入れて、作成済みにするか）

#### テストデータ

円滑に操作できるように、ダミーでもいいのでテストデータが必要です  
有用性を見られているので、多めのほうが良さそうです

### 3. Google Formを入力する

#### 入力手順

[Google Form](https://docs.google.com/forms/d/e/1FAIpQLSeafJF2NDI7oYx1r8o0ycivCSVLNq92Mpc1FPxMKSw1CzDkqA/viewform)を開き、どんどん入力していく  
項目がとても多いので、Playwright MCP等を利用してAIに内容を一緒に考えてもらうといいと思います  
量は多いですが、説明が丁寧なのとAI活用でそんなに困ることや、時間がかかることはなかったです

#### 注意点

* 商用リリースを事前に済ませておく（GA状態にしておく）
* 認証がある場合は、動作確認をする
* 事前に配布予定のサービスからの動作確認をしておく
* アイコンはsvgの必要がある
* Skillsを配布していない場合は、5ページ目は入力しなくてもいい

### 4. 審査を待つ

ドキュメントにも書かれている通り、審査は時間がかかります  
プラスでGoogle Formでの申請になるので進捗もわかりません

全員に返信できるかとも書いてあるので、リジェクトが返信あるのかも怪しいです  
進捗があれば、追記します

## おまけ

### 開発中の動作確認方法

実はConnectorsに登録しなくても、DesktopでMCPは利用できます  
ただ、httpsの必要があるなど基準はConnectorsに登録する場合と変わらないかもしれません

#### 手順

1. 設定に移動  
   Desktop app > Settings > Connectors > Add custom connector
2. MCPを追加

```
Name: MCPの名前
Remote MCP server URL: MCPのURL（https必須）
```

3. Connectする  
   2の手順のあと、下記画像のようにCUSTOMバッジ付きで、リストに追加されます  
   追加したものの「Connect」ボタンを押して、接続します（ここで認証もします）  
   ![](https://static.zenn.studio/user-upload/2114a9cea813-20260404.png)  
   *custom connector追加後の画面*

### 申請を楽にする方法

#### Playwright MCP

フォームのリンクをClaude Codeに渡すことで、内容を確認してくれます  
もし、サービスの知見があるのであれば、内容の雛形みたいなのも作成してくれます  
もしかしたら、computer useとかControl Chromeとかでもできるかもしれません

#### workthin

<https://workthin.app>

!

ステマにはしたくないので、これは個人開発で作成しているサービスです  
サービスの概要としては、どのAI・場所でも同じナレッジを持てる  
さらに、自動参照・登録や3つのスコープ（個人、プロジェクト、グローバル）機能があり、個人だけではなく、チームや世界中でAIの再解決をなくすことを目標としてます

環境変数などの漏洩を防ぐ独自のセキュリティフィルターなどセキュリティ第一で運営していますが、個人開発という点を考慮・ご理解いただけた方のみご利用ください

つまり、このサービスを利用することで、この記事に載っていない細かすぎるつまりどころを参照できます（無料アカウントですと読み取りに制限があります）

`npx workthin@latest init`後に、

```
claude connectors申請について教えて
```

とチャットで聞いてみてください

まだDesktop向けは申請中ですが、前述の方法で、Desktopやcowork内でも利用できます  
その場合は手順2で

```
Name: workthin
Remote MCP server URL: https://workthin.app/api/mcp
```

と入力してください

## おわり

ClaudeのConnectorsの申請方法について記載しました  
Chatgpt Appsも申請予定ですが、MCP自体のデジタル商品への課金導線が禁止されているようなのでどうしようかなと言う感じです

不明点や質問あれば気軽にコメントしてください！！
