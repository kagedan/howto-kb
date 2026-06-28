---
id: "2026-06-29-claudeのdesignを利用してアプリをデザインする-01"
title: "ClaudeのDesignを利用してアプリをデザインする"
url: "https://qiita.com/me990928/items/05772282efe0507b882f"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-06-29"
date_collected: "2026-06-29"
summary_by: "auto-rss"
query: ""
---

## この記事でわかること
- Claude Designを利用してスマートフォンアプリのワイヤーフレームを作成する方法
- 実際に作成されたデザインの例

## 前提条件
Claude Designを利用するには
Pro、Max、Team、Enterpriseの有料プランに加入している必要があります。

## やりたいこと
今回はClaude Designを利用して継続維持を意識したTodoアプリのワイヤーフレームを作成してもらいます。

## 実際に使用した際のレポート

### プロンプトの入力
Design専用のチャット画面が用意されています。
Modelの選択やデザインする内容のテンプレートが用意されています。
今回はテンプレートにワイヤーフレームを選択しました。

![プロンプトの入力画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4456785/85a72f98-869b-4b3e-95d2-b6a5feb97ddb.png)

### ヒアリングについて
最初のチャット画面を入力後、作りたいものに対してのヒアリングが始まります。
- プラットフォーム
- 表現したい仕掛け
- 主要画面
- ホーム画面の構成パターン
- 今回一番確認したいこと
- アプリの雰囲気
- その他

上記の観点でヒアリングを行いワイヤーフレームを生成しました。

![ヒアリング中の画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4456785/9a146890-4779-40de-bd60-e98bb4d06c91.png)

### 生成されたワイヤーフレーム
手書き風のフォントでデザインされたワイヤーフレームが出力されました。
今回は
- オンボーディング（アプリ初回起動時の設定画面）
- ホーム画面
- コア画面

の内容で構成されました。

構成後はチャットUIとワイヤーフレームを編集するエディタをみながら作業を行います。
![チャット画面とエディタが映った画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4456785/248f22ff-ed32-4c77-b962-58d717495861.png)


#### オンボーディング
オンボーディングについては個人開発において後回しにしがちな内容なので、この箇所のデザインが生成されるのはとても助かる要素だと思います。

![オンボーディングが表示されている画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4456785/e8819e7b-1ece-4106-ae85-9eddeccdde7f.png)


#### ホーム画面
3パターンのホーム画面のデザインが出力されました。
画面それぞれのUXが付箋に書かれており、今回の継続したくなる要素がまとめられています。

![３つのホーム画面が提案されている画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4456785/77863fa4-daab-4a12-b5e7-5042aed42c01.png)

#### コア画面
アプリの構成に必要な機能を持った画面がいくつか出力されていました。
継続したくなる要素を実現するために、継続記録のカレンダーや報酬画面、データをまとめたダッシュボードなどが用意されており少ないプロンプトからこれだけの画面を作り出してしまい驚きました。
![コア機能を表現した画面の一覧](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4456785/77b104e4-69df-4c66-a13a-d0f94f6bb5a6.png)

## この機能の特徴

### Tweaks
ダークモードやカラーテーマ、フォントを手書きから普通のフォントへなどClaudeが調整可能と判断した箇所を簡単に切り替えることができる機能です。
![Tweaksを利用してテーマカラーを変更した画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4456785/0aa29106-8877-4e12-99a3-1d0083705ec9.png)

### Comments
特定の要素にピンを留めて、ピンポイントな変更を依頼する機能です。
Claude Codeだとプロンプトから変更する箇所をGUI越しに変更できるのは便利だと感じました。
![Commentsを利用してピンポイントな変更を行なっている画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4456785/188d2e05-ae78-4b98-98ba-a6f6ab7ddc00.png)

### Edit
自分で直接、要素のプロパティを切り替える機能です。
![Editのサイドバーが表示された画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4456785/2a4a906e-d827-4e98-a730-3c27db34af07.png)

### Mark up
キャンバスに直接書き込んで、視覚的にClaudeへ意図を伝えることができる機能です。
![Mark upで画面にまるを描写した画面](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4456785/240a56d9-99ee-4092-a33e-36b11f6081db.png)

## まとめ
作りたいものが決まっている時や、個人で利用するアプリの草案などを簡単に具現化して目に見える形で表現してくれる便利な機能だと感じました。ただ、トークンの使用量が激しい機能なのでモデルの細かな切り替えや機能をうまく利用してトークンの使用量を工夫する必要がありそうです。
