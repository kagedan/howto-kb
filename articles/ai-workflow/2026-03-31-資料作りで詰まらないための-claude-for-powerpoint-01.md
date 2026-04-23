---
id: "2026-03-31-資料作りで詰まらないための-claude-for-powerpoint-01"
title: "資料作りで「詰まらない」ための Claude for PowerPoint"
url: "https://qiita.com/s-sakano/items/73e0eb3a5790806a155e"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-03-31"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

こんにちは！

「資料作りが捗らない」「いつも同じテンプレで、単調に見える」——資料づくりでそう感じたことはありませんか。

そんなあなたに試してほしいのが **Claude for PowerPoint** です。PowerPoint 上で動く AI アドインで、開いているファイルのスライドマスターやフォント・配色を読んだうえで作業してくれます。  
できることは幅広く、文章の整理・スライドの追加・箇条書きをグラフや図に変換するといった作業を短い指示で頼めます。しかも出力結果は画像ではなく PowerPoint のオブジェクトなので、数値や色を後から自分で編集できます。

この記事は **資料作りに困りがちな人** に向けて、**導入, 使い方, 使った感想**などをご紹介します。なお最新の情報は [Use Claude for PowerPoint（Claude Help Center）](https://support.claude.com/en/articles/13521390-use-claude-for-powerpoint) を確認してください。

## この記事の前提（環境・対象）

* **情報の基準日**: 2026年3月30日時点
* **利用条件**: **Pro / Max / Team / Enterprise** のいずれか。Claude アカウントでサインイン
* **対応環境**
  + PowerPoint on the web
  + Windows: Microsoft 365 サブスクリプション、**ビルド 16.0.13127.20296 以降**
  + Mac: **16.46 以降**
* **非対応**: 永続ライセンスの PowerPoint 2016/2019、iPad/Android、古い M365 ビルド など

beta のため、**チェックなしで提出する用途**や、**機密情報を扱う用途**は推奨されていません。必ず人によるレビューと社内ポリシーに従ってください。

## インストール方法

いちばん簡単な方法は、**Claude の Web 画面から直接インストールする**ことです。

1. [claude.ai](https://claude.ai) を開き、左下の **「アプリと拡張機能を入手」** をクリック
2. `claude.ai/downloads` が開くので、**Microsoft Office** セクションの **PowerPoint「インストール ↗」** をクリック
3. ブラウザに「Microsoft PowerPoint を開きますか？」と表示されたら確認
4. PowerPoint が起動し、アドインが自動でインストールされた状態になる
5. 右サイドバーの **「Log in to Claude」** から Claude アカウントでサインイン

Microsoft Marketplace の [Claude for PowerPoint のページ](https://marketplace.microsoft.com/en-us/product/office/WA200010001?tab=Overview) からも同様にインストールできます。

## 基本の使い方

ファイルを開いた状態でサイドバーに指示を書くと、Claude がそのファイルのスライドマスター・フォント・配色を読み、そのルールに沿って出力してくれます。空のファイルから始めることもでき、その場合はデザインの指定がないぶん、スタイルの調整が必要になることがあります。

**頼み方の例**

| 用途 | プロンプト例 |
| --- | --- |
| 新規セクションを追加 | 「市場規模のパートを3枚で。TAM/SAM/SOM と根拠のビジュアル付き」 |
| 1枚を直す | 「このスライドの文章を簡潔に」「四半期推移の棒グラフを追加」 |
| ゼロから構成を作る | 「10枚程度で市場参入の仮説を説明する構成にして」 |
| 箇条書きを図に変換 | 「この箇条書きをプロセス図に」「四半期比較の棒グラフを作って」 |

また、設定には **Instructions** と呼ばれるものがあります。ここに「箇条書きは1行」「強調色はブルー」などを書いておくと、以降のすべての会話に自動で適用されます。

チャット履歴はセッションをまたいで保存されません。長いやり取りをするときは、確定した方針をスライド側にメモしておくと安心です。

### Excel・Connectors・Skills との連携

* **Excel との連携**: Excel アドインと組み合わせると、開いているブックとプレゼンをまたいで作業できます。Pro / Max はデフォルトでオン。Team / Enterprise は組織オーナーの許可が必要です。
* **Connectors**: 接続ツールのデータをスライド作業に取り込めます。
* **Skills**: Claude で有効にした Skill がアドインでも使えます。`/` で一覧から選択できます。

## 実際に使ってみた

試しに、富士山を紹介する 1 枚のシンプルなスライドを用意しました。箇条書きと画像を並べただけの寂しいデザインのスライドです。  
これを選択した状態でサイドバーに「**このスライドを見やすいデザインに調整してください**」と送信してみます。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4156136%2F573e358a-5ccf-4da6-91fb-7b4bf1be3775.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a7bae5c556be3ced17d06d80bd182c82)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4156136%2F573e358a-5ccf-4da6-91fb-7b4bf1be3775.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=a7bae5c556be3ced17d06d80bd182c82)

結果はかなり良かったです。見た目は以下のとおりです。

バラバラだった 7 つの箇条書きが「基本情報」「登山ガイド」「文化的価値」の 3 セクションに整理され、タイトルもサブタイトルとメインに分かれて視覚的な階層ができました。画像も角丸になり、全体的にスッキリした印象になっています。

[![8のコピー.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4156136%2Fb3db71e3-845b-4e5f-917d-97ee5c806bdc.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=614ae680d7298b5f79b4814e66476314)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4156136%2Fb3db71e3-845b-4e5f-917d-97ee5c806bdc.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=614ae680d7298b5f79b4814e66476314)

すごいと思ったのは、途中でセクション見出しにアイコンを追加しようとしたものの、位置がずれていることをAI自身で確認して修正するというやり取りが起きたことです（最終的にアイコンはなくなりました）。

[![Pasted Graphic.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4156136%2Fc2bce25a-dacf-48d5-a6d8-670578c0dcd2.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c6138871375f4c35ade57f208fd9823f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4156136%2Fc2bce25a-dacf-48d5-a6d8-670578c0dcd2.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c6138871375f4c35ade57f208fd9823f)

一方で気になる点として、1 枚の処理にそれなりの時間がかかりました。Beta 版ということもあると思いますが、何十枚もまとめて修正してもらうのは今のところ現実的ではないかもしれません。今後のアップデートに期待です。

## まとめ

* **Claude for PowerPoint** は、スライドマスター・フォント・配色を読んで、レイアウト調整・セクション整理・グラフや図形の挿入までこなせる **PowerPoint 内の AI アドイン（beta）** です。
* **導入**は claude.ai 左下の「アプリと拡張機能を入手」→ PowerPoint「インストール」→ **Claude にサインイン** が最短です。**対応ビルドとプラン**を先に確認してください。
* **使うときは**、デザインが設定されたファイルを開いた状態で指示を書くと精度が上がります。**Instructions** に繰り返し使うルールを書いておくと指示も短くなります。
* **現時点の制約**として、処理に時間がかかるため大量のスライドをまとめて修正するのは難しく、**チャット履歴はセッションをまたいで保存されません**。beta 版のため、最終的な内容は必ず人の目で確認してください。

資料作りでつまずくのは、だいたい「構成」「言い回し」「見せ方」のどこかです。**Claude for PowerPoint** はその手前の工程を短くするのに向いています。

まずはインストールしてみて、**1 枚だけ**頼んでみるところから始めてみてください。

## 参考リンク
