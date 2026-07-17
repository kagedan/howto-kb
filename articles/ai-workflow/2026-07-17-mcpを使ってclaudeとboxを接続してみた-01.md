---
id: "2026-07-17-mcpを使ってclaudeとboxを接続してみた-01"
title: "MCPを使ってClaudeとBoxを接続してみた"
url: "https://qiita.com/DisneyAladdin/items/8911e99f9e9510fd47a2"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "qiita"]
date_published: "2026-07-17"
date_collected: "2026-07-18"
summary_by: "auto-rss"
query: ""
---

![スクリーンショット 2026-07-17 15.58.34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/377231/4d4e8d5c-d9f0-45ac-b9da-6b175ed2513a.png)


# 内容
**MCP**を使って**Claude**から**Box**へ接続するための手順書です

# ClaudeとBoxを接続してできること
Claudeをインタフェースとした、Box上のファイル・フォルダ操作が可能になります。

>具体例
ユーザ：「今度金融業界向けにこんなデモプレゼンするんだけど、それ用に資料と専用フォルダ用意して」
Calude：「承知しました。それではBox上に〇〇というフォルダとその中にプレゼン資料を用意し配置します」


# 手順

## box開発者コンソール
boxの**開発者コンソール** > **統合** > **Box MCPサーバ**の以下を**有効**にする。
- *ファイルとフォルダ*
- *コラボレーション*

これを有効にしないと、MCPサーバーとの接続ができてもファイルやフォルダの操作権限がないので何もできないです。
![スクリーンショット 2026-07-17 15.10.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/377231/65459af0-2440-4191-9d6b-6c155758af8c.png)

## boxユーザコンソール
boxの**ユーザ画面** > **統合** > **Calude**から**追加**を押下します
![スクリーンショット 2026-07-17 14.19.08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/377231/4c8405e2-5fba-4c16-b8b6-92b2c84273ef.png)

## Claude側での認証
Claudeの認証画面に切り替わるので認証します。
![スクリーンショット 2026-07-17 14.19.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/377231/1e9a0c6e-ce0e-43bd-bfa6-0fe20151ff56.png)
認証が完了したら以下のように**コネクタ**の画面になるので**連携/連携させる**を押下します。
![スクリーンショット 2026-07-17 14.26.16.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/377231/877b2af2-b0de-4c3b-95df-ffa4a9a0667f.png)

接続が完了したら、何か指示してみましょう。
![スクリーンショット 2026-07-17 15.35.56.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/377231/7527d86e-9e49-4333-954d-8f2d7101e100.png)
指示通りに作ってくれたので完了です。
![スクリーンショット 2026-07-17 15.37.42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/377231/744c7679-ca70-4809-8a52-5349767ba9b0.png)
