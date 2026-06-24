---
id: "2026-06-23-figma-tips-claude-artifactsでdlしたhtmlファイルをfigma拡張機能-01"
title: "[Figma Tips] Claude ArtifactsでDlしたHTMLファイルをFigma拡張機能でFigmaデータ化する"
url: "https://qiita.com/kabechiyo13/items/227fd52ab52401b99b77"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-06-23"
date_collected: "2026-06-24"
summary_by: "auto-rss"
query: ""
---

## Figma Chrome拡張（公式）とは

先日Figmaからリリースされた、WebページをFigmaデータ化できるChrome拡張です。

編集可能なレイヤーとして取り込めるため、vibe codingで作ったページや既存ページをFigma化 → Figma上で調整 → Claude Codeに戻す、といったデザインとコードの往復がよりスムーズにできるようになります。

取り込んだフレームは「Send to Figma Make」でMakeのプロトタイプ起点にもできます。

## ClaudeのArtifactsをFigma化する

私はプロトタイピングに主にClaudeのArtifacts機能を使っています。  
ただ、Claude上で直接この拡張を使ってもArtifacts部分はレイヤー化できませんでした。

そこで、ArtifactをHTML形式でダウンロードしてファイルを開き、キャプチャを試しましたが動きませんでした。

原因は、拡張機能設定の「Allow access to file URLs」（ファイルの URL へのアクセスを許可する）がデフォルトでOFFになっていたことでした。  
これをONにすることで、localのHTMLファイルでもFigma Capture機能が使えるようになります。

[![拡張機能設定でAllow access to file URLsのトグルがONになっている画面](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F577501%2Fb93c1793-6cfd-4ba1-bb77-cdab5812de30.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=f8bec93080f79902264c1f25d1269362)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F577501%2Fb93c1793-6cfd-4ba1-bb77-cdab5812de30.png?ixlib=rb-4.1.1&auto=format&gif-q=60&q=75&s=f8bec93080f79902264c1f25d1269362)

これで、ClaudeのArtifacts機能で作成したプロトタイプをより簡単にFigmaデータ化できるようになりました。
