---
id: "2026-04-28-claudemcpsalesforceのダッシュボードが衝撃的だった-01"
title: "Claude＋MCP＋Salesforceのダッシュボードが衝撃的だった！"
url: "https://note.com/nueshima/n/n9f3eab93cdec"
source: "note"
category: "ai-workflow"
tags: ["MCP", "note"]
date_published: "2026-04-28"
date_collected: "2026-04-28"
summary_by: "auto-rss"
query: ""
---

![](https://assets.st-note.com/img/1777335977-GAv6RSXpydfTWBkV9HEatqos.png?width=1200)

今回はSalesforceの人気機能、ダッシュボードがClaudeだとどこまでできるのか試してみたいと思います。

**結論を先にお伝えすると、かなり衝撃的な内容で、クオリティとコスト、両面から大きく改善が期待できる内容になっていますので読んでいってください。**

大まかな検証の流れは次のとおりです

  

### ダッシュボードの作成と実行

商談一覧からグラフ化してと指示を出します

![](https://assets.st-note.com/img/1777119193-4BhHbUdCkWp2n0RLAYGs37XT.png?width=1200)

![](https://assets.st-note.com/img/1777119239-Ktr0B67WlwARqui9YaMLsdzy.png?width=1200)

![](https://assets.st-note.com/img/1777119254-WcJVyGbDNgumhHax8tkwLAzQ.png?width=1200)

また、出ました恐ろしい結果です。今まで時間を費用を頂いて作榮していてものが一瞬で作成されました。

次の別のグラフ、パイプライン管理用のグラフの表示を指示する

![](https://assets.st-note.com/img/1777119508-YDRhWKCH19zqJ57xXwNS3nEg.png?width=1200)

![](https://assets.st-note.com/img/1777119540-uhARbjtZfPQXwsYzBpeyO6i5.png?width=1200)

じょうごのグラフのイメージとは少し違いますが、分析も返してくれました

次の分析の集計方法を切り替えてみます

![](https://assets.st-note.com/img/1777119661-fIlEyv7kUWYxz6ZN90nDb8AM.png?width=1200)

営業担当別に切り替えてみると、各数値の集計もそれぞれ行い、比較グラフも追加。そのうえ二人の特徴と傾向も返してきました。

![](https://assets.st-note.com/img/1777122985-p9KiMaj0og7XZJ8f5N6d3yeR.png?width=1200)

そして、赤枠の詳細を見るというリンクを押すと営業担当者を絞ったドリルダウンが実行されました

### ドリルダウン

![](https://assets.st-note.com/img/1777119947-0Emh5OH7oNL6aly9ndiuUVA4.png?width=1200)

![](https://assets.st-note.com/img/1777120033-hdrYMHLlQf1oumc849q2kKyp.png?width=1200)

![](https://assets.st-note.com/img/1777123011-lvkifSYJ1HgmUxjD8AzK7sdt.png?width=1200)

営業担当者を絞り込んだグラフと分析結果が表示されました。  
注目すべきは上のグラフに**「注意事項」**です。

**注意事項には抜けているタスクが記載されています。これは私がClaudeの指示したり、事前に定義したものでもありません。事前学習していたものと思われます。何から学習しているのか不明ですが、すでにSalesforce利用ノウハウが入っていることが伺えます。**  
そして、注意事項記載の「次のステップ未記入」のため、次のステップ入力ボタンが表示されている。赤線部分。これをクリックすると次の画面となる

![](https://assets.st-note.com/img/1777120683-s07d58R9xtkz4cW32HLZpgey.png?width=1200)

次のステップ入力を促され、入力すると商談が更新されました。

凄すぎる！　  
「次のステップの入力は商談管理する上で重要なので入力を促すべき」というのはどこで学習しているののでしょう？  
  
これは人のマネジメントするより正確になりそうです！！！

---

### 表示できるグラフを聞いてみる

取引先別金額の円グラフを他にできるグラフが何か聞いてみました

![](https://assets.st-note.com/img/1777121286-I7CtwHNVmOcU3WTyFBZPk15x.png?width=1200)

Claudeが表示できるグラフの種類を聞いていました

![](https://assets.st-note.com/img/1777121559-jaqczgB1xOoQEdsHlVM4FNiT.png?width=1200)

![](https://assets.st-note.com/img/1777121581-GFIsUgQAR4ECNPjMekKuZdYL.png?width=1200)

これはもうtableauなどのBIと比べると数は少ないですが、これだけあればSaleseforceのダッシュボード以上のことはできます

---

### ここまででわかったこと

* ダッシュボード（レポート含む）は作成しなくてもよくなる。
* Claudeが作成したグラフは人が作成するより高度である。
* BIが提供できる価値と同じことがプロンプトだけで可能になる

### まとめ

今回の検証もかなり衝撃的な内容でした。

今まで我々ITエンジニアがお金をもらっていた行っていた仕事が不要になることを実感しました。

我々専門家が作成する以上ものをClaudeは一瞬で作成できるのです。同じ領域で戦えなくなります。立ち位置を変える必要があります。データを整形する仕事が求められるようになると思われます

最後までお読みいただきありがとうございました。
