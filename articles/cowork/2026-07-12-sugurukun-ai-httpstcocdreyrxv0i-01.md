---
id: "2026-07-12-sugurukun-ai-httpstcocdreyrxv0i-01"
title: "@SuguruKun_ai: https://t.co/CdrEYRXV0I"
url: "https://x.com/SuguruKun_ai/status/2076213509839573206"
source: "x"
category: "cowork"
tags: ["OpenAI", "GPT", "cowork", "x"]
date_published: "2026-07-12"
date_collected: "2026-07-14"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/CdrEYRXV0I

Codexのアプリ統合なども起こっており、結構追っておく必要がある事項が多いです。
こちらの記事もオススメ：
https://t.co/TWBizVqJ4s


--- Article ---
![](https://pbs.twimg.com/media/HNAxI3UaoAAkwJK.jpg)

OpenAIが「ChatGPT Work」を出しました（発表は日本時間7月10日、投稿は2万いいね級）。Codexを内蔵したエージェントで、あなたのアプリやファイルをまたいで、仕事を丸ごと実行する。

見逃せないのは日付です。Anthropicが「Claude Cowork」をwebとモバイルに広げたのが7月8日。その翌日にOpenAIがChatGPT Work。つまりこの1週間で、**両陣営の「AIに仕事を任せる場所」が出揃った**。コーディングエージェントの戦争が、ついにオフィス業務に本格的に波及した形です。

この記事では、ChatGPT Workの中身、Claude Cowork側の実像、そして「実際に人はAIエージェントに何を任せているのか」のデータまで、公式情報ベースで全部整理します。どっちの陣営で仕事を組むか考える材料として、保存して使ってください。

## ChatGPT Workとは — 「チャット」ではなく「作業者」

![](https://pbs.twimg.com/media/HNAxJE4bYAAD1ko.jpg)

実際に自分のChatGPT（Proプラン）を開いたら、もう来てました。画面上部に「Chat / Work」の切り替えが出ます。

![](https://pbs.twimg.com/media/HNAxJR0bsAAFwa0.jpg)

*自分のアカウントの実画面。入力欄の下に「プロジェクトを選択」「プラグイン」（Slack・Google Drive・Gmailのアイコン）、右に「Open desktop app」。さらにGmailやGoogleカレンダーの中身を読んで「このタスクやりましょうか」と具体的に提案してきます（内容は案件情報なのでぼかしました——逆に言うと、そのレベルで実データに食い込んでくる）。*

ChatGPT Workは、一言でいうと**Codexを内蔵したChatGPTのエージェント**です。公式の説明を要約すると、できることはこう。

- **複数ステップのタスクを丸ごと実行**する（指示への回答ではなく、作業の完了が単位）
- **ローカルのファイルやアプリを使って**作業する
- **内蔵ブラウザ**でWebサイト・ツール・オンラインのファイルにアクセスする
- **スケジューリングで独立して動く**（人が見ていない間も進む）
- web・モバイル・デスクトップのどこからでもタスクを管理できる
さらに「**Sites**」というベータ機能があって、レポートやライブダッシュボードを**インタラクティブなWebサイト/Webアプリとして生成**できます。成果物が「文章」じゃなくて「動くページ」で返ってくる、というのは提出物の形として結構な変化です。

提供は、公式ページによると**デスクトップ版はすべてのプランで利用可能**、WebとモバイルはPlus・Pro・Business・Enterprise・Eduに数日かけて順次展開です。

![](https://pbs.twimg.com/media/HNAxJbNbsAAhCrD.jpg)

## 裏側はCodexとGPT-5.6 — 「開発ツールの技術」が事務に来た

![](https://pbs.twimg.com/media/HNAxJlxbQAAir3K.jpg)

![](https://pbs.twimg.com/media/HNAxJ3basAAc-2V.jpg)

*実画面その2。モデルは「5.6 Sol」で、タップすると**推論の深さが5段階のスライダー**になってます。「軽」から重い方までダイヤルを回す感覚で、この段階UIは新鮮でした。*

ChatGPT Workの発表で個人的に一番重要だと思うのは、**エンジンがCodex**だということです。同日に出たGPT-5.6（Sol/Terra/Luna）で駆動して、コーディングエージェントとして磨かれた「計画→実行→検証」の仕組みを、そのまま事務作業に向けた。

デスクトップでは**CodexアプリがChatGPTアプリに統合**され、既存のChatGPTデスクトップは「ChatGPT Classic」という扱いになります。つまりOpenAIの中では、チャットが主でエージェントが従、という関係が逆
