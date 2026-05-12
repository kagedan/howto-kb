---
id: "2026-05-09-riku720720-これみてhtml-outputっていうskills作ってみたけどすげー良い-個-01"
title: "@riku720720: これみて/html-outputっていうskills作ってみたけどすげー良い 個人用のS3ストレージに静的HTMLを保"
url: "https://x.com/riku720720/status/2053028068395270558"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-05-09"
date_collected: "2026-05-12"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

これみて/html-outputっていうskills作ってみたけどすげー良い

個人用のS3ストレージに静的HTMLを保存
↓
URL返す

ってだけのシンプルなSkills

月に1000個のHTML保存してもコスト1円くらい。
md読むより疲れないし、URLでパッと共有できる https://t.co/CiRZ0DyoZ2

参考になれば
https://t.co/fGAajYXAN5

公開範囲制限したければCloudflare R2使うのが良さそうだね
https://t.co/QpFeqOY5ez

速さが課題。html生成-&gt;URL出力に2分くらいかな。

コンポーネントとかテンプレ配置して、選択するような形にすれば早くなるけど、その分自由度が減る。自由度を上げた方が汎用性が増えるのでとりあえずはこれで使ってみよう

HTMLを単なる人間に見やすいドキュメントとして捉えない方が良くて、 たとえばこんな感じで少し工夫すると動的なインターフェースにもなる
https://t.co/F1TZyWRRXs

出力トークン増えるのと、コンテキスト圧迫するからsubagentで分離してメインの会話セッションとは独立させるといい感じ

記事内でも言われてる通り、htmlファイルローカル出力するのはskills作る意味ないんだけど
クラウドストレージにアップロードしてURL出力をさせるっていうフローをやりたいからSkills作った。
なんでわざわざアップロード毎回するかっていうと、ローカルで保存してコンテキスト圧迫させたくないのとccpocketでスマホからすぐに確認できて便利だから


--- 引用元 @trq212 ---
HTML is the new markdown. 

I've stopped writing markdown files for almost everything and switched to using Claude Code to generate HTML for me. This is why.

You can also see example HTML documents I've generated here: https://t.co/QuTMbHtdlc
