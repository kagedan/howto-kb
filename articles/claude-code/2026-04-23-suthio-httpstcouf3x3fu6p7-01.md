---
id: "2026-04-23-suthio-httpstcouf3x3fu6p7-01"
title: "@suthio_: https://t.co/Uf3X3Fu6P7"
url: "https://x.com/suthio_/status/2047115352052801745"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "x"]
date_published: "2026-04-23"
date_collected: "2026-04-24"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/Uf3X3Fu6P7


--- Article ---
個人事業主や法人はとにかくバックオフィス業務が多いです。

・SaaSの請求書（領収書）を毎月集める
・クレジットカード明細と領収書を突合する
・取引先へ請求書を発行する
・入金された振込と自分が発行した請求書を突合する
・freeeに仕訳を切る
・出張旅費規程を整備する
・信用金庫や日本政策金融公庫からの借入を管理する
・決算期に税理士さんに資料を渡す

僕は法人を2社、経営しているのですが、こういう業務を「毎月手作業でやる」のが本当に嫌で、back-office専用のgitリポジトリを作って運用しています。

このリポジトリには、SaaSの一覧、領収書の取得手順、仕訳ルール、スクリプト、そして未来の自分への申し送りメモなどを全部集約していて、Claude CodeとfreeeのMCPサーバーを組み合わせれば、月次のバックオフィス業務がほぼ自動化できます。

今日はその構成を細かく紹介しつつ、「こういうこともリポジトリに入れておくといいよ」という話を書いていきます。

---

**読むのめんどくさい人はこの記事をコピペして依頼すれば簡単に依頼できるのでオススメ**

# なぜ専用リポジトリを作るのか

最初は「freeeに全部入れておけばいいでしょ」と思っていたのですが、実際に運用してみるとfreeeだけでは足りないことがたくさんありました。

・領収書の取得手順をどこかにメモしておかないと、毎月「あれ、Slackの領収書ってどこからダウンロードするんだっけ？」となる
・SaaSごとのアカウントとメールアドレスの対応を忘れる（どのGoogleアカウントでログインするんだっけ、みたいな）
・仕訳ルール（この支出は支払手数料？それとも通信費？）を毎回考え直すのがもったいない
・出張旅費規程のExcelや日本政策金融公庫の返済予定表みたいな書類の置き場が欲しい
・未来の自分への申し送りメモ（「来期からこのサービスは解約する」「次回決算で確認すること」など）を残す場所が欲しい

これらは「freeeに入れるにはノイズ」「Notionに入れるにはコード寄り」という中間にある情報なんですよね。

だったらgitリポジトリに全部入れてしまおう、というのが発想の出発点でした。Claude Codeからも参照しやすいし、バージョン管理もできるし、プライベートリポジトリなら情報漏洩リスクも最小化できます。

# ディレクトリ構成

僕のback-officeリポジトリはこんな構成になっています。

```
back-office/
├── README.md
├── docs/
│   ├── freee/
│   │   ├── freee_SaaS_領収書メール設定ガイド.md
│   │   └── freee_SaaS_未対応タスク.md
│   ├── freee-journal-rules.md
│   └── future-memo.md
├── receipts/
│   ├── AWS/
│   ├── GitHub/
│   ├── GoogleCloud/
│   ├── Slack/
│   ├── Vercel/
│   ├── スマートEX/
│   └── ...
├── references/
│   ├── services.md
│   └── 日本政策金融公庫_返済予定表.pdf
└── scripts/
    ├── monthly-billing-check.sh
    ├── billing-check-all-months.sh
    ├── upload-receipts.sh
    └── receipts/
        ├── README.md
        ├── _lib/
        │   ├── run-all.sh
        │   ├── run-service.sh
        │   ├── resume-next-session.sh
        │   ├── list-unmatched.sh
        │   └── find-existing.sh
        ├── aws/
        │   ├── README.md
        │   ├── prompt.md
        │   └── fetch.sh
        ├── github/
        ├── slack/
        ├── google-workspace/
        ├── claude/
        └── ...（2
