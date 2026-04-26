---
id: "2026-04-26-claudemcpsalesforceslackでパイプラインマネジメントやってみた-01"
title: "Claude+MCP+Salesforce/Slackでパイプラインマネジメントやってみた"
url: "https://note.com/nueshima/n/nbff77c176ec8"
source: "note"
category: "ai-workflow"
tags: ["MCP", "note"]
date_published: "2026-04-26"
date_collected: "2026-04-26"
summary_by: "auto-rss"
---

### 目的

このページはClaudeからMCPで各SaaS（SalesforceやGoogle、Notionなど）を使ってみたらあまりにも凄すぎたので、その動作検証を残し多くの人に知ってほしいために書いています。

ということで今回はSFAの定番であるパイプラインマネジメントの流れをClaudeから試してみたいと思います。

大まかな検証の流れは次のとおりです

* Salesforceから商談を取得する
* チェックする
* 指示する

---

### デモデータを修正する

データはデベロッパーエディションに最初からあるサンプルデータを利用しますが、現実的にするための完了予定日を近い日付に変更したいとおもいます。

![](https://assets.st-note.com/img/1777106663-Pit4YzGkw7hsTZFuybUBOeWN.png?width=1200)

![](https://assets.st-note.com/img/1777106689-GdVxq0oYI3SFCi9lDeK7wEc5.png?width=1200)

えーと、、次のセクションで分析しようと思ってたのですが、すでにサマリーされています。。。。うーん、自分の思考よりも先を行き過ぎてます。。

完了予定日の修正を曖昧な指示で行います。

![](https://assets.st-note.com/img/1777107094-qkMpreKAcPYnh8V6b01JEB2Q.png?width=1200)

![](https://assets.st-note.com/img/1777107018-GHPI9Wx68VFu7s2ja3niyeRT.png?width=1200)

恐ろしいくらい簡単に完了しました。  
今までデータを準備してデータローダーでアップロードしていた作業がなくなります。

### 商談を取得する

先ほど商談一覧のサマリーを見たので今月（2026年4月）クローズ予定の商談を表示を指示します

![](https://assets.st-note.com/img/1777107486-nHoX0FGUxEC8M9Tdt1pisfuP.png?width=1200)

### 進捗状況のチェック

マネジャーが聞きそうなことを色々聞いていきます

次のステップが未記入の商談

![](https://assets.st-note.com/img/1777107877-dVcPTWtZ7HiLE0Ub16hGKkxw.png?width=1200)

![](https://assets.st-note.com/img/1777108026-U2BM8qyvrslgdtZkDfeOjKEu.png?width=1200)

それぞれ説明つきで結果を教えてくれます。  
  
**さすがにスリップ商談のチェックはできないだろうと思ったのですが、定義の説明までしてリストアップしてくれました。すごい！！！**

スリップ商談をダッシュボードで表示するためには数式とか使って工夫していたのですが、、、そもそもその言葉すら知らない人が大多数だとおもうのですが、、出力できるとは本当に驚きです。人がチェックしているようです。

![](https://assets.st-note.com/img/1777108188-LQ7ynsKAmpqIaBTDXWOP8dUN.png?width=1200)

### チームへの指示

では、スリップ商談リストに基づいて商談所有者に次のアクションはどうなっているのか確認してみましょう。

![](https://assets.st-note.com/img/1777108918-F9iw4KuxLOkQAzYbhmI5EcJs.png?width=1200)

![](https://assets.st-note.com/img/1777108969-0eZ9OpXFx2Dl6IdRkiQGujtv.png?width=1200)

文書まで考えてくれてますね。Sendを押しSLackを確認します

![](https://assets.st-note.com/img/1777109197-CDhItEFV9BlyOeYbRM7XJ6uv.png?width=1200)

画面のようにSlackに受信されました。これを返信するとあとはSlackでのやりとりとなります。

![](https://assets.st-note.com/img/1777109436-O4jIy18Zq6GFbJhNLalus9iE.png?width=1200)

テストアカウントが送信者も受信者も同一のためわかりにくいですが、成功しています。返信後はSlackでのやりとりになります

---

### ここまででわかったこと

* **レポートダッシュボードの作成が不要になる。Claudeに問うだけでSalesforceマネジャーと同じ価値観が手に入る**
* **スリップや停滞商談の定義も不要となる。これは大きな意味がある。システム開発時の要件定義が少なくなるということ。お客様もITベンダーも打ち合わせ時間を大きく減らせる。ベンダーは売上も減る。**
* **Slack、Google、Salesforce、SaaS間の連携開発なしで使えるようになり、時間とコストが大きく短縮できる**

### まとめ

前の投稿でも記載しましたが、Claudeに対して処理に対する定義を与えたりはしていませんし、当然コードを追加したりしていません。MCPサーバーに接続しただけなのです。

それでこれだけのことが実現できるのですから、我々システムインテグレータの今後の立ち位置を本当に真剣に考えていく必要があると思います。

最後までお読みいただきありがとうございました
