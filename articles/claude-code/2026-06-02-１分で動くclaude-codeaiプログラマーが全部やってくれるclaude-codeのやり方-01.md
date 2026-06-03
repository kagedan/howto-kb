---
id: "2026-06-02-１分で動くclaude-codeaiプログラマーが全部やってくれるclaude-codeのやり方-01"
title: "【１分で動くClaude Code】AIプログラマーが全部やってくれるClaude Codeのやり方"
url: "https://zenn.dev/mlboydaisuke/articles/99262840ea9b76fa8a7c"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-06-02"
date_collected: "2026-06-03"
summary_by: "auto-rss"
query: ""
---

# 雇ったらもうおまかせ

AIプログラマーが作ってくれたカメラアプリ。  
![](https://res.cloudinary.com/zenn/image/fetch/s--ld5FPS4a--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/235259/a195c97d-1481-4fcc-9667-9db3f67395d2.png?_a=BACMTiGT)

![スクリーンショット 2025-03-16 12.09.27.png](https://res.cloudinary.com/zenn/image/fetch/s--7LjyuzV---/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/235259/7f524904-a3c2-497a-84e2-633ac7d053b5.png?_a=BACMTiGT)

Claude Codeというやつを雇う。  
雇い方は以下。

# 雇い方

インストール。

```
npm install -g @anthropic-ai/claude-code
```

やって欲しいプロジェクトのディレクトリに移動。  
今回はアプリを作ってもらうことにしたので、xcodeプロジェクトのディレクトリに移動。

```
cd your-project-directory
```

claudeさん、お願いします。

初回はAPI keyの設定をお願いします、といって、anthrop\cのwebページが開いて、「API Key設定していいですか？」と言われるので、OKしてあげる。サインインとクレジットカード登録がまだなら、あらかじめしておく。

これでclaude codeくんを雇うことができた。

![スクリーンショット 2025-03-16 11.12.35.png](https://res.cloudinary.com/zenn/image/fetch/s--wq1ypJkW--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/235259/bb4cf1b8-94b5-47e3-bc91-6e741f53f509.png?_a=BACMTiGT)

あとはコンソールのプロンプト欄に指示をするだけで、プロジェクトの中の全てのファイルを読み取り、ファイルを追加し、コードを書いてくれる。  
今回は、**「カメラで撮影するアプリを作って」とお願いした。**

一応、ファイルを編集するときは「この内容で編集していいですか？」と聞いてくる。

何度かエラーが出たが、その度にエラーを伝え書き直してもらう。

そしてclaude codeくんが作ってくれたプロジェクトをxcodeでrunすると、

![](https://res.cloudinary.com/zenn/image/fetch/s--ld5FPS4a--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/235259/a195c97d-1481-4fcc-9667-9db3f67395d2.png?_a=BACMTiGT)

普通にカメラアプリができた。

プロジェクト全体のファイルを書き換えてくれるから便利だと思う。

# 料金

ちなみにclaude codeくんは有料で、このカメラアプリを作るのに1ドルぐらいAPI料金を使った。

🐣

---

フリーランスエンジニアです。  
お仕事のご相談こちらまで  
rockyshikoku@gmail.com

Core MLを使ったアプリを作っています。  
機械学習関連の情報を発信しています。

[Twitter](https://twitter.com/JackdeS11)  
[Medium](https://medium.com/@rockyshikoku)  
[GitHub](https://github.com/john-rocky)
