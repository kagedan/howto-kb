---
id: "2026-07-07-ローカルsns投稿コネクタでcookieを預からない設計ブラウザプロファイル境界とmcpの役割-01"
title: "ローカルSNS投稿コネクタでCookieを預からない設計：ブラウザプロファイル境界とMCPの役割"
url: "https://zenn.dev/agentmemories/articles/local-sns-connector-cookie-boundary"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "zenn"]
date_published: "2026-07-07"
date_collected: "2026-07-09"
summary_by: "auto-rss"
query: ""
---

![ローカルSNS投稿コネクタのCookie境界 - Cookieを預からず本人端末内で投稿する](https://static.zenn.studio/user-upload/deployed-images/59b41582817d01521ddaebb4.png?sha=0d52c7c4f5de0887a58f90f1c7d70e0a55fc4bf7)

![ローカルSNSコネクタ構成 - server memory、local MCP、browser profile、SNS](https://static.zenn.studio/user-upload/deployed-images/823656d83cfc1dfb233a4154.png?sha=de97d5e99f829cc39a588091b5878c2307af372f)

## はじめに

SNS投稿をAIエージェントに手伝わせる時、公式APIだけでは足りない場面があります。特にMVP段階では、ユーザー本人のブラウザログイン環境を使ったローカル投稿コネクタが現実的な選択肢になります。

ただし、この設計で絶対に避けたいのは、Cookie文字列を運営サーバーに集めることです。

Agent Memoriesでは、価値の本体を記憶・人格・文脈生成側に置き、投稿コネクタは薄く配る方針です。この記事では、その境界設計を整理します。

## Cookieを預かる設計の問題

Cookieをサーバーに集めると、実装は簡単に見えます。しかしリスクが大きすぎます。

* 侵害時にSNSアカウントへ直接影響する
* ユーザーが何を預けたか把握しにくい
* 運営側が不要な権限を持つ
* 失効、更新、漏洩対応が重くなる

ローカル投稿コネクタでは、Cookie文字列を入力させません。ユーザー本人の端末上のブラウザプロファイルにログイン状態を保持し、MCPはそのローカル環境だけを操作します。

## 構成を分ける

構成は大きく3つに分けます。

1. サーバー側: 記憶、人格、文脈生成
2. ローカルMCP: 投稿文の受け取り、dry-run、ブラウザ操作
3. ブラウザプロファイル: ユーザー本人のログイン状態

```
type LocalPostRequest = {
  platform: "x";
  accountHint: string;
  text: string;
  dryRun: boolean;
};
```

ローカルMCPに渡すのは投稿内容と操作指示です。CookieやAuth headerは渡しません。

## ローカルMCPの責務

ローカルMCPは、万能なSNS自動操作エンジンにしません。責務を薄くします。

* 投稿画面を開く
* dry-runで文字数や添付の確認を返す
* ユーザー本人のブラウザプロファイルだけを使う
* 実行ログにsecretを残さない

```
type DryRunResult = {
  ok: true;
  platform: "x";
  accountHint: string;
  textLength: number;
  willOpenBrowser: boolean;
};
```

dry-runでは、投稿しません。何が起きるかを返すだけです。

## 記憶と投稿コネクタを分離する

Agent Memoriesの価値は「投稿ボタンを押せること」ではありません。記憶をもとに、その人らしい文脈を作れることです。

そのため、ローカル投稿コネクタには記憶データ本体を持たせません。サーバー側またはユーザー所有の記憶ストレージから、必要な文脈だけを生成し、投稿テキストとして渡します。

```
type GeneratedPost = {
  sourceMemoryIds: string[];
  text: string;
  policyChecks: {
    noSecret: boolean;
    noImpersonation: boolean;
    noUnsupportedClaim: boolean;
  };
};
```

ローカル側は、この投稿テキストを受け取って確認・投稿するだけです。

## ログに残すものと残さないもの

残すものは、説明責任に必要な範囲です。

* platform
* accountHint
* textLength
* dryRunか実行か
* 実行時刻
* 成功/失敗

残さないものは、認証や個人情報に直結するものです。

* Cookie
* token
* Auth header
* ブラウザセッションの中身
* 不要なページHTML

## まとめ

ローカルSNS投稿コネクタは、Cookieを預からない設計にするべきです。

最小方針は次の通りです。

1. Cookie文字列を入力させない
2. ユーザー本人のブラウザプロファイルを使う
3. MCPは薄い投稿コネクタに留める
4. 記憶・人格・文脈生成は別レイヤーに置く

この境界を守ると、ユーザー本人の環境で投稿できる便利さと、運営側が不要な認証情報を持たない安全性を両立できます。
