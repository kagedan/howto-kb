---
id: "2026-07-10-個人開発anubis-zone-of-enderリスペクトの3dシューティングゲームを作ってみた-01"
title: "【個人開発】ANUBIS ZONE OF ENDERリスペクトの3Dシューティングゲームを作ってみた"
url: "https://qiita.com/K_san0219/items/d3770163a7c765963ba3"
source: "qiita"
category: "ai-workflow"
tags: ["Gemini", "qiita"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

## はじめに
最近、個人でClaudeを課金してみました。
1か月お試しのつもりで課金したらなんと年間プランに…！
もう泣いててもしゃあないので使い倒そうと思います。

今までGeminiだけで開発していたのですがまるでレベルが違いますね、すごい、すごすぎる。
特に今話題のFableってやつはよくわかんないけどすごいです。語彙力のなさ！

せっかくいっぱい使えるんだから何に使おうかと考えたところ、とりあえず過去に作ってみたものを改良することにしました。

記念すべき最初の改良元はこちらです。
👉 **[【個人開発】ブラウザで動く！質量変動・マルチロック搭載のフライトアクションプロトタイプを作ってみた](https://qiita.com/K_san0219/items/f351052f6deb7b6b90fd)**
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/789979/1607134c-b536-417f-9b51-21352a2f8991.png)

これを「3D化して！！！」という無茶ぶりをClaudeにかましてみました。すると…

## GRAVITY ZERO — 3D フライトシューター
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/789979/21140849-b620-4115-96a2-ebea22031ab2.png)
👉 [実際に遊べるURL](https://ksan260307.github.io/gravity-zero-app/www/index.html)

できちゃった。すごい！！！

## こだわったところ
もちろん一発出しでここまで作ったわけではないですが、基礎となる3Dの部分は最初に作ってもらえました。
すごい時代になりましたね。
その後何度か改良を重ね、今の形になっています。
以下の点が個人的こだわりポイントです。

### ANUBIS ZONE OF ENDERのジェフティの浮遊感を追求
ふわりとした宇宙的な感覚ながらも高速戦闘が魅力なこのゲーム、とても大好きです。
あのジェフティの動きを頑張って再現してみました。
もともと改良前でもある程度再現できていたと思いますが、3Dにしても変わらず浮遊感を再現できています。
Claudeすごいよほんとに。
また、ジェフティのマルチロックレーザー、ゼロシフト、サブウエポンなどの魅力的な機能もできる限り再現しています。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/789979/6f24a6ad-927d-4188-9a37-a0d39338c510.png)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/789979/9fab4be1-b8bf-4022-b973-3455631f3c3b.png)


### 充実のUIやシステム
操作説明画面、キーコンフィグ、チャレンジモード、レベル調整、スコア記録など、遊びやすい/遊んでみたくなる機能をできる限り盛り込みました。
このあたりはまだまだ試行錯誤の余地ありです。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/789979/11e66edd-fda7-4f55-a301-26f5c4f205aa.png)


### 品質を担保するテストスイート
200件以上ものテストを実施するテストスイートを作成し、品質の担保を図っています。
基本的には全機能網羅テスト。
Claudeで回答を出すたびに毎回全パスすることを確認したり、新機能を追加する際にも必ずテストを追加するよう指示しています。
体感ですがある程度出力の質が担保され、バグが減っている気がします。
テストはとても大事。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/789979/dbc86494-25e7-455d-b2d1-b57d43f5152c.png)


## おわりに
頑張って作りました！！ぜひ遊んでみてください！！！！！！！
今まで記事はAIで頼りきりだったのですが、久々にすべて手打ちしました。
熱い気持ちが伝わると幸いです。
また、このゲームはこれからも随時改良予定ですので、温かく見守っていただけると幸いです。

👉 [ソースコード](https://github.com/Ksan260307/gravity-zero-app)
