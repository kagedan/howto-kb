---
id: "2026-06-23-メモclaude-design-frontend-designを使ってみる-01"
title: "[メモ]Claude Design + frontend-designを使ってみる"
url: "https://zenn.dev/teraco/articles/98767caef91c5c"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-06-23"
date_collected: "2026-06-24"
summary_by: "auto-rss"
query: ""
---

自分用メモです。

使ってみる、といっても難しいことはなく、

> frontend-designのプラグインをインストールして、Claude Designを利用してこのLPを改善して

から、Claude Codeと対話をし始めるだけです。なお私はデザイナーではなく一般のClaude Code利用者です。

### 修正前

ただ「LPを作って」と言って作ってくれたのがこちら。frontend-designもClaude Designも使ってません。

![](https://static.zenn.studio/user-upload/d218c1795b8f-20260623.png)

### 修正後

> frontend-designのプラグインをインストールして、Claude Designを利用してこのLPを改善して

と指示したもの。

![](https://static.zenn.studio/user-upload/567d09761e53-20260623.png)

### 使ってみた感想

確かに、ぱっと見は修正後の方がよくなっています。frontend-designの過程で適切なフォントの提案があったり、LPのメッセージをもとにした背景画像の提案があったりしました。

ただ思ったのは、**自分の中にデザイン意図がないと結局AIぽさは抜けないな**ということ。これ、文章作成でも同じですが、自分の文体や自分の意図がないと、結局AIに寄ってしまう。

素人ながらここまでのLPが秒速で作れるのはよいのだが、プロとの差は隠せないと思いました。

### Claude Designは?

今回、Claude Designはデザイン向上にほぼ寄与していません。なぜなら私がClaude Designの利用を指示しただけで、Claude Designを利用して確認・修正は行っていないから。

以下、Claude Designの画面

![](https://static.zenn.studio/user-upload/5348a4dae686-20260623.png)

LPのセクション毎に画面を表示でき、対話的に修正ができる。私が勘違いしていただけですが、Claude Designはデザイン向上のツールではなく、デザインを見ながら対話的に修正ができるツールだったのです(理解不足かもしれない)

### 結論

一発撮りのLP作成ならfrontend-designだけで十分だと思います。一方、Claudeが作ってくれたデザインを画面をみながらあーだこーだ指摘したいならClaude Designを使うべきだと思いました。
