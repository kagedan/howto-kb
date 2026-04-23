---
id: "2026-03-19-claude-coworkで写真を整理した-01"
title: "Claude Coworkで写真を整理した"
url: "https://note.com/wag2021/n/naca80f4feea6"
source: "note"
category: "cowork"
tags: ["cowork", "note"]
date_published: "2026-03-19"
date_collected: "2026-03-19"
summary_by: "auto-rss"
---

スマホの写真がPCに溜まりに溜まっていました。かつデジカメの写真なんかもざっくばらんに「Photos」というフォルダに保存されていて、しかも年月日でフォルダ分けしていたから後で見返す時に例えば「2005」→「07」→「23」みたいにいちいち辿る必要がありました。

保存した当初はそれでいいと思っていたけど、10年20年経つと面倒で仕方ない。

そこでClaudeに頼んで整理することにしました。要点は以下の通り。  
- 「Photos」以下たくさんあるサブフォルダを全部巡回して画像ファイル(JPG/PNG/GIF)を「Photos」というフォルダにコピーする。  
- その際同じ写真があればサイズか解像度が大きい方を残す。残さない方は「deleted」というフォルダにコピーする。

一旦これでスタートします。念の為元のファイルはいじらせず、ダウンロードフォルダあたりに写真フォルダを丸ごとコピーしてきて、その下に「Photos」と「deleted」フォルダを作ってから実行します。

![](https://assets.st-note.com/img/1773886459-rq297Pvym4YbpNAIU5WzlFoL.png?width=1200)

プロンプトのスクショ

話し言葉だけどプロンプト文です：

> このフォルダのサブフォルダがたくさんあって、たくさん過去の写真があります。これを新しいフォルダ「Photos」にまとめたい。Photos/は今作ったので空のフォルダです。全ての写真をこのPhotosにコピーしていきたいんだけど、同じ写真があった場合は解像度が高い、もしくはファイルサイズが大きいものを残して、ファイルサイズもしくは解像度が小さい写真は削除するようにしたい。削除したファイルはdeleted/にコピーします。作業をお願いします。

大きいが誤変換されてるのにちゃんと処理してくれてた

20年分の写真だったので40GBぐらいあり、30-40分かかって整理が終わりました。

ちなみに処理でタイムアウト起こしたりすると自発的に考えて見直してくれ、自動で実行してくれます。

![](https://assets.st-note.com/img/1773886649-PLXfsaBoFO0wq8g9YnmHluhM.png?width=1200)

16,000枚以上の写真を35分で整理し終えました。

![](https://assets.st-note.com/img/1773886726-mzUQSRA8GZxheqMwBIsLrN4g.png?width=1200)

結果は満足いくものだったのですが、このままだと1万以上の写真ファイルがずらっと並ぶだけで視認性が悪い。そこで日付をファイル名にすることで、撮った時系列で表示できるようにします。

![](https://assets.st-note.com/img/1773886766-hYwb8KusIG30dreFinqa7lQz.png?width=1200)

プロンプト文：

> ではphotos/Photosのファイル名を以下のポリシーで変更してください。 \* YYYYMMDD\_HHMM.[jpg/png/gifなど] \* 重複する場合はYYYYMMDD\_HHMM\_1or2...と連番に。 \* EXIFの「撮影日時」が取得できる場合はそれをファイル名に \* EXIFから撮影日時が取得できない時やEXIFがない場合はファイルの「更新日時」をファイル名に

こちらは3分ほどで完了しました。

![](https://assets.st-note.com/img/1773886831-jGME7JZwcCg54lu8AhVYTHnD.png?width=1200)

いやー、圧倒的に見やすい写真フォルダになりました。

![](https://assets.st-note.com/img/1773886870-zyrnoIQXJsPauFAtfiUOhkEM.png?width=1200)

Windows版クイックルック(Microsoft Storeで「QuickLook」を検索、インストール)を入れているので、スペースバーを押してビュワーを開き、↓矢印キーで過去の写真をつらつらと見返していくのが楽しかったです。

![](https://assets.st-note.com/img/1773886974-q7dh5xAXyWwEgkHtBea3K4TL.png?width=1200)

ついでにAmazon Photosも一旦ローカルに全部ダウンロードして、同様の処理を行って整理しました。

長年「整理したいなぁ」と思っていたことが、Claude Coworkのおかげで1時間もかからずできてしまいました。
