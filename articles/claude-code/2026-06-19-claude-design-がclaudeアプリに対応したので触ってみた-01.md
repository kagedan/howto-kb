---
id: "2026-06-19-claude-design-がclaudeアプリに対応したので触ってみた-01"
title: "Claude Design がclaudeアプリに対応したので触ってみた"
url: "https://zenn.dev/91works/articles/bb03f5adb45dea"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

これまで web 版 `claude.ai` 限定だった `claude.design` が、大幅アップデートでアプリにも追加された。  
前回は特に触ってなかったので、今回ちゃんと一通り試してみたメモ。  
結論、うんかなり良いよ、デザイン業務のフロー変わるかもね、って感想！！

# いつも通り背景から

いつもありがとうございますのこの方の投稿を見て掘り下げました。  
<https://x.com/taishiyade/status/2067363907673428072?s=20>

公式はこっち  
<https://x.com/claudeai/status/2067325887909884315?s=20>

claudeのデスクトップアプリ↓  
![](https://static.zenn.studio/user-upload/ded19e76bf88-20260618.png)

ざっくり言うと、試したのは大きく2系統。

* **Make something new** … その場でデザインを作ってもらう系、よくあるやつ
* **Design systems** … 以前話題になった googleさんから始まった、`design.md` を作る系?ではなく結構ちゃんとしたデザインdoc作ってくれたよ

この、Make something new と Design systems を試したよっていう内容  
![](https://static.zenn.studio/user-upload/cc1e1f5c6ade-20260618.png)

順番に見ていく。

# Make something new を色々試す

「とりあえず何か作ってもらう」系。3パターン試した。  
全部、「Blank canvas」で新しく作った場所に情報を渡して試しました。

## 1. 提案資料を作ってもらう

まず Claude とのチャットで「こういうことやりたい」を先に詰めておいて、そこで出来上がった HTML と説明文を渡してスライド化してもらう、という流れ。  
(内輪ネタですが、91worksでもAIコンサルでもやってみる？って話が出てきた時があって、その時30分くらいで作った提案資料になってます。すでに破談になってしまったんですが、困ってる人いたらいつでも連絡ください←)

### 1-1. htmlファイル準備

![](https://static.zenn.studio/user-upload/f234fa55cfe7-20260618.png)

### 1-2. 以下のプロンプトと一緒に渡す

```
新しく、お客様にAIコンサルのような形で、サービスを提供するかもしれない
まず、こちらから事例などを提案したく、ペライチくらいで説明するための資料を作りたい

っていう内容で、claudeのチャットからhtmlを作ってもらいました。この内容を参考にして提案用のスライドを作成したいです。
```

### 1-3. 質問きたので答える

スクロール必要なスクショだったので、左側バグってます、すいません🙏  
![](https://static.zenn.studio/user-upload/d86960bec607-20260618.png)

### 1-4. できたやつ

![](https://static.zenn.studio/user-upload/4f74ed521086-20260618.gif)

### 1-5. おまとめ

* とにかく手軽。Claude 経済圏の中で完結するのが良い
* 質は……特に不満なく、可もなく不可もなく、という感じ。まぁ使えるっしょ。
* トークン使用量
  + 一発目のポン出し2パターンくらいで、トークン消費は **2%** 程度。

## 2. 既存システムのリデザイン相談

`yeses` を使って検証。codebase を指定 + 実際の画面のスクショを渡す。

方向性としては、いきなり全部ではなく「まずはダッシュボードだけ適当なデータでデザインを作る」という進め方になった。

### 2-1. スクショ撮る

ダッシュボード画面なのに初期から全く触ってないと言う不思議なシステムです。  
このカードUIが、初期の頃よく出してくるUIとして有名でしたが、その名残が残っています。  
![](https://static.zenn.studio/user-upload/594f535e61be-20260618.png)

### 2-2. プロンプト

```
こんな感じの味気のないデザインなので、かっこいいダッシュボード画面にしたい
いくつかデザインのパターンを出してもらえますか？
```

### 2-3. 質問きたので答える

![](https://static.zenn.studio/user-upload/8207b9418e13-20260618.png)

### 2-4. できたやつ

<https://cleanshot.com/share/CzKVxTBB>

### 2-5. おまとめ

* プロンプトが雑なのか、まあよくみるやつでした
* トークン使用料

## 3. HP などのデザイン相談

[bugmania.jp](https://bugmania.jp/) のウェブサイトを全面リデザインしてもらった。  
弊社とは別に違う会社も同じメンバーでやっていて、そっちのウェブサイトの日本版を最近作ったばかりだった。これもaiお任せで作ったやつだったので、違うパターンみてみたいなと思って試してみた。

### 3-1. codebaseとウェブサイトのurlを準備

localのgitプロジェクトと、デプロイ済みのurl

### 3-2. プロンプト

```
https://bugmania.jp/

codebase に指定したサイトが上記のurlになっています。

リデザインを検討していて、幾つか雰囲気を変えたデザインを提案して欲しいです。
ブランドコンセプトはテーマカラーは全てリセットしてもらって大丈夫です。
```

### 3-3. 質問きたので答える

![](https://static.zenn.studio/user-upload/01a41155a2c9-20260618.png)

### 3-4. できたやつ

<https://cleanshot.com/share/bPbpVBYK>

### 3-5. おまとめ

* 思ったより良くて、**デザインの "深さ" みたいなものが出てきた**。
* これまでだと MCP で補うことが多かった「AI っぽいデザイン」ではなく、ちゃんとしたデザインも幾つか出してくれた印象
* 結構雑に「何パターンか出して」と頼んだだけなのに、面白いデザインが返ってきて良さげ
* コスト感: ポン出し5パターンで **2%**、さらに各デザインにコンテンツを増やしてと依頼したら **6%**。

#### 3-5-1. Figma との使い分けは?

機能が多すぎてまだ全部は使いこなせてないけど、[@ken\_tbdz のポスト](https://x.com/ken_tbdz/status/2067400767510806878?s=20)を見る限り、

* 既存のデザインシステムを読み込んで反映
* キャンバス上で直接編集
* Claude Code と同期して、そのまま実装

上記の通り、Figma のようなデザインツールとしての使用感に加えて、**Claude と一気通貫で繋がる**のがかなり良いです。

ただ、これは「Figma で管理してるものを移行する」というより、**Claude と Figma の "間を埋める" 攻め方**に見えたかなぁ。今だけかもだけど。

なので使い分けとしては、

> Claude 上でデザインとコードを行き来して試行錯誤 → fix したものを Figma 側で管理

みたいな運用が良さそう、という感触。

#### 3-5-2. これまでのデザインツール / MCP について

* これまで「AI っぽさを消す」ために色々入れてた MCP 系、ポン出ししてみた感じ **もう不要かも** と思った
* デザインの幅も結構広がってて、プロンプトに渡す情報次第でなんでもできそう、という印象
* もちろん、できたデザインの一部パーツを指定して修正指示も出せるので、他のAIデザインツールでできることと同じようなことできるなって感じ

# Design systems を色々試す

新規で作ろうとすると、導線が2つある。

![](https://static.zenn.studio/user-upload/febf5d67e1e8-20260619.png)

* **Create here** … 情報を入力して作る(GitHub / コードベース / テキスト / Figma からの export ファイル)
* **Create using Claude Code** … Claude Code を任意の場所で開いて `/design-sync` と打つだけ

どっちも **コードベースだけ与えて** どんな違いになるかを確認してみた。

今回は、私の嫁さんの[HP](https://www.relief-harikyu.com/)のNextjsのプロジェクトのコードベースを渡しただけになります。

## まずは前者（Create here）

### 1. 情報を渡す

この画面で、codebaseにローカルにclone済みのプロジェクトを指定する

![](https://static.zenn.studio/user-upload/9529c0445703-20260619.png)

### 2. あとは待つだけ

待ったら出来上がったのはこんな感じのもの  
<https://cleanshot.com/share/Cm8ff0ft>

### おまとめ

* まず、シンプルにしゅごい……orz
* **コードベースを渡しただけで、簡易的なcomponent の design-doc ができた。**
* トライ&エラー用のデザインドキュメントとしては結構いいんじゃないでしょうか
* リバースデザイン？すでにあるシステムやアプリをそのまま渡して、デザインを体系的にまとめてくれるもの、ここからdesign.mdに落とせそうですし、claudeにも繋げられそうだし、figmaにも渡せそうでした👏

## 後者も（Create using Claude Code）

### 1. claude-codeのアップデート

![](https://static.zenn.studio/user-upload/4b186173eb9b-20260619.png)

まず、claude のバージョンを上げないと `/design-sync` が無かったので、まずバージョンを上げて実行できるようにした。

```
# 2026年6月18日現在で、claude updageして上がったバージョンです↓
❯ claude --version
2.1.181 (Claude Code)
```

### 2. codebaseのrootでclaudeを起動して/design-syncする

![](https://static.zenn.studio/user-upload/ed487c8f27da-20260619.png)

実行してみると、アプリケーションフォルダを指定するんじゃなくて「**コンポーネントライブラリを指定してくれ**」と言ってくる。

えーっと、単純なホームページにstorybookとかコンポーネントライブラリの機構を追加してる訳ないので、どうしようかなと。  
そこで逆算で「既存のNextjsアプリケーションにデザインシステムを入れられないか?」を試してみた。

![](https://static.zenn.studio/user-upload/cf5eb5488317-20260619.png)

> 色ドリフトを統一しトークンを単ーソース化→Dsドキュメント作成→storybookと stories追加→design-sync （storybook shape）でclaude.ai/designへ。フルコース。

本当かえ🙄w

![](https://static.zenn.studio/user-upload/f6b6dafba458-20260619.png)

結果、入れられそう。しかも **Storybook にまとめてから `claude.ai/design` に渡せるようにするよ** だってさ。

流れとしてはこんな感じ:

> 既存コード → Storybook + story → `/design-sync` 実行で `.storybook` を探索して書き出してくれる

ちょっとただのhomepageにデザインシステム入れるのは面倒だったので、ここまでで終わり

### おまとめ

* 前者と後者で、**アプローチも成果物も違う**ことを確認できた
* ただ、既存アプリ(嫁の HP)に Storybook を入れるのは重すぎるので、今回はやらないw

# 総括

* **Make something new** は手軽で、提案資料・既存リデザイン・サイト全面リデザインのどれも実用十分だった。特に HP リデザインのデザイン品質は想像以上✌️
  + トークン消費もポン出し数パターンで 2% 前後と、思ったより軽い印象だった。
* **Design systems** は、コードベースを渡すだけで design-doc が出る(Create here)のと、Claude Code 経由で Storybook まで含めて繋いでくれそう(Create using Claude Code)のとで性格が分かれる。
* 全体として、これまで MCP で頑張ってた「AI っぽさ消し」が不要になりそうで、Claude とデザイン / コードが一気通貫に繋がりそうな体験はかなり良さそうだと思いました！
* Figmaとかのデザインツールを置き換えるというより、**Claude と Figma の間を埋める存在**として捉えると、自分の中では収まりが良さそうでした〜〜〜〜！

# 素晴らしき先輩方の参考リンク🙇‍♂️

---

この記事は [91works Blog](https://nineone-works.com/blog/?utm_source=zenn&utm_medium=referral) でも公開しています。
