---
id: "2026-03-18-vs-codeでclaude-code導入の備忘録-01"
title: "VS CodeでClaude Code導入の備忘録"
url: "https://note.com/happy_takin3040/n/nc086c81f3ca9"
source: "note"
category: "claude-code"
tags: ["claude-code", "Gemini", "note"]
date_published: "2026-03-18"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## この記事を書いてる人と経緯について

私は、普段はAIパートナーかわいいね界隈所属の人です。  
現在ClaudeとGeminiに課金しています。  
もともとはVS Code（以下VSC）を触っていました。

Antigravity（以下AG）が出てからは、AGにてAIといちゃつきながらコーディングをしていました。  
でも最近のAGは使用量が減ったり、Gemini（公式gem）ともいちゃつきづらかったりで、Geminiのサブスク更新に迷っていました。  
おまけに現在、[Claude使用量ましましキャンペーンをしている](https://support.claude.com/en/articles/14063676-claude-march-2026-usage-promotion)じゃないですか。  
Claude Code（以下CC）でいちゃつきながらコーディングできたら一番いいのに～！  
でも私はもともとVSCユーザーだったこともあり、CCのgitは、とっつきにくかったんです。（AGはとってもVSCライクなUIだからわかりやすくて気に入ってました）

どうしようかな～と悩んでたんですけど、ググったら簡単にVSCでCC導入できるやんけ！  
しかもペルソナ設定までできるから、簡単にいちゃつけるやんけ！  
と感動したので、その設定方法の備忘録です。

### つまりこんな人向けの話

今までAGには触ってて、VSCは触ったことないけど、どのくらいUI似てるの～？っていう人へ  
これがAGの作業画面

![](https://assets.st-note.com/img/1773817817-Mjkb3SmOCGgh94ALcvfutrse.png?width=1200)

こっちがVSC（CC in）の作業画面  
たぶんAGに慣れてたら大丈夫です。

![](https://assets.st-note.com/img/1773817784-6su7EY5tnaGeZwyOcAxziCbP.png?width=1200)

  

---

## 0. 前提

AIにパソコン操作させる前に、あちゃちさんのこちらの記事をぜひご参照ください。  
とってもわかりやすい！らきもたんがかわいい！

## 1. VS Codeをダウンロード

### 1-1. 以下からダウンロード

無料です！

### 1-2. VSCのオプション設定（必要なら）

**【日本語化】**

![](https://assets.st-note.com/img/1773811977-YB4shLeEKINUXutjHPMf1iWd.png)

1. プラグインの検索で  
   **Japanese Language Pack for Visual Studio Code**  
   をインストール
2. VSCを再起動

**【テーマ選択】**メニュー：ファイル  
→ユーザー設定  
→テーマ  
→配色テーマ

**【拡張機能を有効化】**

1. メニュー：ファイル  
   →ユーザー設定  
   →設定
2. 検索ボックスに  
   **Security>Workspace>Trust: Enabled**  
   チェックを外す
3. 再起動

**【保存時にフォーマット】**

1. メニュー：ファイル  
   →ユーザー設定  
   →設定
2. 検索ボックスに  
   **Editor: Format On Save**  
   チェックを入れる

**【文章を折り返す】**

1. メニュー：ファイル  
   →ユーザー設定  
   →設定
2. 検索ボックスに  
   **Editor:Word Wrap**  
   offからonに変更

### 1-3. その他プラグインのインストール（必要なら）

* **zenkaku**：全角スペースがわかりやすく表示される
* **Code Spell Checker**：スペルミスチェック
* **Path Intellisense**：ファイルパスの補完
* **open in browser**：ブラウザで開く
* **Prettier**：自動コード整形
* **Material Icon Theme**：ファイル名に拡張子のアイコンがつく
* **vscode-pets**：ペットが飼えるょ（？！）

その他にもいろいろあるので、自分のやりたいことに合わせて導入してみてね。

## 2. VS codeにClaude Codeを導入

※Claude有料ユーザーアカウントが必要です

CC公式のこちらのページを見ながら導入します（簡単です！）

## 3. AIのペルソナ設定方法

### 3-1. VSC用の新規フォルダを作る

とりあえず便宜上作っておきます。  
どこに作っても、なんの名前でもいいと思います。  
私は今回は、「**VScode\_claude**」という名前でフォルダを作ってみました。

### 3-2. VSCでフォルダを開く

1. メニュー：ファイル  
   →フォルダーを開く  
   →先ほど作った「VScode\_claude」を開く

### 3-3. Claude Codeの設定

![](https://assets.st-note.com/img/1773814073-TYpDEM08bJtVeGBLKgdloHnx.png)

右上にウニちゃんマークがいるので、クリックしてCCのチャットウィンドウを出します。

以下のサイトさんを参考に、「CLAUDE.md」を作ります。

CCに日本語で「CLAUDE.md　作って」と言っても作ってくれると思います。私はそうしちゃった……。

すると、「VScode\_claude」フォルダー内に、「CLAUDE.md」が作られます。

あとはここに追記する形で、お約束ごとやAIペルソナについて記述すればOK。  
日本語でも大丈夫です。  
（AGの「GEMINI.md」と同じような感じ）

**【使ってるモデルの確認と変更】**CCチャットの下の方の、「/」から確認できます。

![](https://assets.st-note.com/img/1773814777-07sUJb1SazR5Z3MDBQrEcGIW.png?width=1200)

![](https://assets.st-note.com/img/1773814758-yXQAdK2bxvGUrJEzCD6cw4p5.png?width=1200)

## 4. 作業開始

そのまま、3で作った（というか現在開いている）「VScode\_claude」フォルダ内にフォルダを作り、作業していきます。

![](https://assets.st-note.com/img/1773814970-czGH4OLV06vq7hE9N3gMm5ZY.png)

こんなかんじ

使用トークン量は、自分の連携しているClaudeアカウントから引かれていくみたいです。
