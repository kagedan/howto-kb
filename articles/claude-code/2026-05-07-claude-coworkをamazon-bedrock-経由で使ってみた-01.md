---
id: "2026-05-07-claude-coworkをamazon-bedrock-経由で使ってみた-01"
title: "Claude CoworkをAmazon Bedrock 経由で使ってみた"
url: "https://zenn.dev/fusic/articles/7ac5229f4d65f0"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-05-07"
date_collected: "2026-05-08"
summary_by: "auto-rss"
---

## はじめに

Fusicの[レオナ](https://x.com/xthixsl_ml)です。  
Anthropicのデスクトップアプリ「Claude Desktop」で、推論バックエンドに Amazon Bedrock を利用できる **Claude Cowork in Amazon Bedrock** が[発表](https://aws.amazon.com/blogs/machine-learning/from-developer-desks-to-the-whole-organization-running-claude-cowork-in-amazon-bedrock/)されました。

Claude Code がエンジニア向けのCLIツールであるのに対し、Claude Cowork はチャットUIベースで非エンジニアでも扱いやすいデスクトップアプリです。本ブログではClaude DesktopからAmazon Bedrockを推論バックエンドに設定する手順を試してみます。

## Amazon Bedrock とは

Amazon Bedrock は、AWS が提供するフルマネージドな生成AIサービスです。Anthropic Claude をはじめ複数の基盤モデルをインフラ管理不要で API 利用できます。詳細は[公式ドキュメント](https://docs.aws.amazon.com/bedrock/)を参照してください。

## 全体の流れ

1. Amazon Bedrock の API キー（短期）を取得する
2. Claude Desktop の開発者モードを有効化する
3. サードパーティ推論設定に AWS リージョンと API キー、推論プロファイル ID を入力する
4. 動作確認

## 準備

検証環境は macOS、Claude Desktop は[公式](https://claude.ai/downloads)から取得した最新版を使用します。

### Step 1. Amazon BedrockのAPI キーを取得

Amazon Bedrockの API キーには 短期キーと長期キーがあります。今回は短期キーを使用します。

取得手順は以下のブログにまとめています。  
<https://zenn.dev/fusic/articles/23f9bd726b3aee>

### Step 2. Claude Desktop の開発者モードを有効化

1. ヘルプ → トラブルシューティング → `開発者モードを有効にする`を選択します。  
   ![](https://static.zenn.studio/user-upload/ead368c4636f-20260507.png)
2. 確認ダイアログで`有効にする`を選択し、アプリを再起動します。メニューバーに開発者メニューが表示されます。  
   ![](https://static.zenn.studio/user-upload/bcf47120852c-20260507.png)
3. 開発 → `サードパーティ推論を設定...`を選択し、設定ウィンドウを開きます。  
   ![](https://static.zenn.studio/user-upload/fe254216863d-20260507.png)

### Step 3. Claude Desktop に Bedrock を設定する

1. `AWS region` に `ap-northeast-1`（東京）を入力します。
2. Step 1 で取得した API キーを `AWS bearer token` に入力します。  
   ![](https://static.zenn.studio/user-upload/fe58d7333548-20260507.png)
3. モデル ID には推論プロファイル ID を入力します。今回は 日本リージョン間（東京・大阪）クロスリージョン推論プロファイルの `jp.anthropic.claude-sonnet-4-6`を使用します。
4. `ローカルに適用`を押下し、再起動の確認ダイアログで`今すぐ再起動`を選択します。  
   ![](https://static.zenn.studio/user-upload/c38ae8bf093e-20260507.png)  
   ![](https://static.zenn.studio/user-upload/7af1e6f82633-20260507.png)

## 試してみる

設定が反映されると、画面に `Cowork 3P・Bedrock` の表示が出ます。プロンプトを送ると Amazon Bedrock 経由で応答が返ってきました。

![](https://static.zenn.studio/user-upload/1fcdedc3a20c-20260507.png)

## 最後に

Amazon Bedrock経由でClaude Coworkを利用すると、AWSの一括請求やCost Explorerでコスト管理ができ、データも国内リージョンに閉じる構成にできます。
