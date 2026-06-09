---
id: "2026-06-08-2026年版生成-ai-でスライドを作成-gemini-と-chatgpt-と-claude-の特徴-01"
title: "2026年版！生成 AI でスライドを作成！ Gemini と ChatGPT と Claude の特徴を比較してみた"
url: "https://qiita.com/ta-ito0611/items/79458f11d10bcb153459"
source: "qiita"
category: "ai-workflow"
tags: ["Gemini", "GPT", "qiita"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは！KDDIアイレットの伊藤です。

資料作成は、多くのビジネスパーソンにとって「時間がかかる業務」の代表格ではないでしょうか。構成を考え、文字を打ち込み、レイアウトを整え、配色を悩む。1 枚のスライドに思いのほか時間を取られた経験は誰しもあるはずです。

ここ最近、生成 AI のスライド・画像生成は急速に進化し、「それっぽいもの」から「そのまま使えそうなもの」へと品質が一段上がってきました。とはいえ、ツールごとに得意・不得意ははっきり分かれます。

そこで今回は、いま話題の 3 つの生成 AI に **まったく同じお題・同じプロンプト** でスライドを作らせ、横並びで比較してみました。

- **Gemini 3.1（Canvas）**
- **ChatGPT (5.5 Thinking)**
- **Claude (opus-4-8)**

「どれが一番きれいに作れるのか」だけでなく、「指示どおりに作ってくれるか」「実務で使ううえでの手数はどうか」まで踏み込んで見ていきます。

> ※本記事で使用しているバージョン表記・名称は執筆時点のものです。各ツールは更新が速いため、最新情報は公式の案内もあわせてご確認ください。

## 検証方法

公平に比べるため、以下の条件を統一しました。

▪️ **指示内容**
<strong>・お題：KDDIアイレットを紹介するスライドを作成してください。</strong>
<strong>・引用元：https://www.iret.co.jp/company/outline.html</strong>
<strong>・生成枚数 ：3枚</strong>

▪️ **評価軸**
・デザイン品質
・指示への忠実さ
・使い勝手・速度
・修正のしやすさ
・要点を掴めているか

> 本記事の評価は、上記の簡易的な指示を出した場合の個人的な所感です。入力するプロンプトの細かさや用途、また使用者の感覚によって評価は変動する点をご了承ください。

## ツール別レビュー

### Gemini 3.1（Canvas）
<strong>&lt;1度の指示で作成したスライド&gt;</strong>
<img class="alignnone size-large wp-image-198828" src="https://iret.media/wp-content/uploads/2026/06/e0bc1dda181952860951f8c5e6467d95-720x391.jpg" alt="" width="720" height="391" />
<img class="alignnone size-large wp-image-198829" src="https://iret.media/wp-content/uploads/2026/06/575d2ae69f8c19979076e324af2ebcfd-720x405.png" alt="" width="720" height="405" />
<img class="alignnone size-large wp-image-198830" src="https://iret.media/wp-content/uploads/2026/06/817c116e4526725516c14081a995dbff-720x409.jpg" alt="" width="720" height="409" />

内容や見やすさは、とてもいいですね！！2枚目、３枚目の下の方が見切れていたのが気になったので、修正するように指示をします。
<img class="alignnone size-large wp-image-198838" src="https://iret.media/wp-content/uploads/2026/06/1df713228c799c3ba8cda874d9db8f6a-720x405.jpg" alt="" width="720" height="405" />

<strong>&lt;修正指示後のスライド&gt;</strong>
<img class="alignnone size-large wp-image-198839" src="https://iret.media/wp-content/uploads/2026/06/185b80e2a81933d70056e39263f3f85a-720x356.png" alt="" width="720" height="356" />
<img class="alignnone size-large wp-image-198841" src="https://iret.media/wp-content/uploads/2026/06/485f61ae8dffd02c29950b1a5bff01a2-1-720x376.jpg" alt="" width="720" height="376" />

たった一回、チャットで指示しただけで綺麗に修正がされています。
かなり使いやすく最初の指示からシンプルで洗練されたスライドを作成してくれたと思っております。

ただし、指示していないにも関わらずスライド内の画像まで変更されてしまいました。
(他の部分は変更しないように別途指示する必要がありそうです)

各評価軸に対する採点は以下となります。(あくまで個人的観測で条件によって評価は変わります)

▪️ **評価軸**(個人的観測で、5段階評価で採点)
・デザイン品質：5
・指示への忠実さ：4
・使い勝手・速度：5
・修正のしやすさ：5
・要点を掴めているか：4

・総合：23

### ChatGPT (5.5 Thinking)
<strong>&lt;1度の指示で作成したスライド&gt;</strong>
<img class="alignnone size-large wp-image-198847" src="https://iret.media/wp-content/uploads/2026/06/592ff6c7f411dccc08f8b3f6fccf0a5c-720x407.jpg" alt="" width="720" height="407" />
<img class="alignnone size-large wp-image-198848" src="https://iret.media/wp-content/uploads/2026/06/2409deaf765899cc690792afdacbe3fd-720x406.png" alt="" width="720" height="406" />
<img class="alignnone size-large wp-image-198849" src="https://iret.media/wp-content/uploads/2026/06/c8b5c06d47127761022f6800743ebb76-720x404.png" alt="" width="720" height="404" />

こちらも内容や色使いがよく、みやすいスライドを作成してくれました。
スライド2・3ともに枠に収まっていない記述が目立つので修正指示を出します。
<img class="alignnone size-large wp-image-198850" src="https://iret.media/wp-content/uploads/2026/06/f134013761492a941c022f216c65d6ca-720x277.png" alt="" width="720" height="277" />

<strong>&lt;修正指示後のスライド&gt;</strong>
<img class="alignnone size-large wp-image-198851" src="https://iret.media/wp-content/uploads/2026/06/78df0f8775a881d037034f57e63bd927-720x404.png" alt="" width="720" height="404" />
<img class="alignnone size-large wp-image-198852" src="https://iret.media/wp-content/uploads/2026/06/028e48edf56f6acd8910a48cc09dca1e-720x405.png" alt="" width="720" height="405" />

指示通りに、しっかりと枠に収まり綺麗にしてくれました。

画像や色、ブロックを細かく分けることでメリハリのあるスライドを作成してくれました。
各評価軸に対する採点は以下となります。(あくまで個人的観測で条件によって評価は変わります)

▪️ **評価軸**(個人的観測で、5段階評価で採点)
・デザイン品質：3
・指示への忠実さ：5
・使い勝手・速度：5
・修正のしやすさ：5
・要点を掴めているか：4

・総合：22

### Claude(opus-4-8)
<strong>&lt;1度の指示で作成したスライド&gt;</strong>
<img class="alignnone size-large wp-image-198856" src="https://iret.media/wp-content/uploads/2026/06/fd107a2b8a15f3576cf923b213c7a04c-720x542.png" alt="" width="720" height="542" />
<img class="alignnone size-large wp-image-198857" src="https://iret.media/wp-content/uploads/2026/06/faef5e79c7dbb1f0e8cb0115daa30716-720x542.png" alt="" width="720" height="542" />
<img class="alignnone size-large wp-image-198858" src="https://iret.media/wp-content/uploads/2026/06/0c51bcc7161aa5ffda6848b5e6e1024f-720x540.png" alt="" width="720" height="540" />

内容や色使いは良いのですが、スライド2・3ともに文字が重なっていたり、枠内に全てが収まっていないことがわかります。こちらも修正の指示をしていきます。
<img class="alignnone size-large wp-image-198859" src="https://iret.media/wp-content/uploads/2026/06/0486be0c1d1ecc2f1962fb6c75f4ef97-720x130.png" alt="" width="720" height="130" />

<strong>&lt;修正指示後のスライド&gt;</strong>
<img class="alignnone size-large wp-image-198862" src="https://iret.media/wp-content/uploads/2026/06/f8ca0a8c7c400c6d6d41591d879b11f2-720x523.png" alt="" width="720" height="523" />
<img class="alignnone size-large wp-image-198863" src="https://iret.media/wp-content/uploads/2026/06/e840f31449cfdd26743edf73485110fe-720x555.png" alt="" width="720" height="555" />

指示内容に正確に従い非常に見やすく再作成してくれました。
各評価軸に対する採点は以下となります。(あくまで個人的観測で条件によって評価は変わります)

▪️ **評価軸**(個人的観測で、5段階評価で採点)
・デザイン品質：5
・指示への忠実さ：5
・使い勝手・速度：2
・修正のしやすさ：3
・要点を掴めているか：5

・総合：20

## 横並び比較

3 軸 + 補足項目で一覧にまとめました (5段階評価)

| 項目 | Gemini 3.1（Canvas） | ChatGPT (5.5 Thinking) | Claude(opus-4-8) |
| --- | :---: | :---: | :---: |
| デザイン品質 | 5 | 3 | 5 |
| 指示への忠実さ | 4 | 5 | 5 |
| 使い勝手・速度 | 5 | 5 | 2 |
| 修正のしやすさ | 5 | 5 | 3 |
| 要点を掴めているか | 4 | 4 | 5 |
| 総合 | 23 | 22 | 20 |

> 本記事の評価は、上記の簡易的な指示を出した場合の個人的な所感です。入力するプロンプトの細かさや用途、また使用者の感覚によって評価は変動する点をご了承ください。

## 結論：どういう人にどれがおすすめか
実際に触ってみて、それぞれに「向いている使い方」をピックアップしてみました。

<strong>▪️Gemini 3.1 (Canvas)</strong>
・とりあえず丸投げしてみて、ある程度のスライドを完成させた後に微修正していきたい人 (抽象的な指示でもかなり綺麗で構成もちゃんと作ってきます)
・コマンド操作などに慣れていない人(自然言語のチャットのみで作成できます。)
・シンプルで洗練されたデザインを好む人

<strong>▪️ ChatGPT (5.5 Thinking)</strong>
・指示したレイアウトや枠の中に、きっちり情報を収めてほしい人（型崩れが少ないです）
・テキストの要素をロジカルにブロック分けして、メリハリをつけたい人
・画像やブロックを積極的に使うような複雑めなデザインを好む人

<strong>▪️Claude(opus-4-8)</strong>
・ある程度構想は固まっていて、細かく指示した上で完成度の高いスライド作成をしたい人
・AIから提案を受けながら修正していきたい人(こちらの要望に対して+αで提案をいくつか出してくれたりします)

## 補足：別視点での感想 (筆者による利用方法)
私は、普段から3つの生成 AIを使ってスライドを作成しています。あくまで一例ですが、私が最も使う場合の使い方を紹介します。

<strong>①Claudeにて初版スライド資料を作成</strong>
作成したいスライドの内容のすり合わせを行います。(スライド作成の目的、どんなシチュエーションか、内容、ターゲット等)すり合わせができたら、Claudeからの提案を受けながらスライド作成を依頼します。

<strong>②Geminiによりデザイン統一</strong>
Claudeで作成したスライドのデザインをGeminiを使って自分好みになるまで修正を繰り返します。(Gemini 3.1のデザインが、とても洗練されていて最もみやすいと考えているため)

<strong>③ChatGPTによる図の作成</strong>
最後に、構成図や図解したいスライド部分について、ChatGPTを使って作成してもらい、要所要所のスライドに埋め込みます。(構成図や細かい図をシンプルでみやすいものにする場合、ChatGPTが最も適していると考えているため)

私の場合は、普段このようにスライド作成をしております。生成AIそれぞれの特徴と強みをいかしてスライドを作成することで、作成速度や精度が大幅に向上しました。
また、登壇などに使うスライド作成の場合は、時間を指定することでスライドの枚数やスピーカーノートの作成までしてくれてとても便利です。

## まとめ
いかがでしたでしょうか。今回は Gemini、ChatGPT、Claude という 3 つの生成 AI を使い、まったく同じ条件でスライド作成の比較を行いました。
検証を通して、どの AI も実務で十分に活用できるレベルに進化していることがわかりました。一方で、それぞれに明確な個性や得意分野があることも見えてきました。

生成AIをうまく活用するポイントとしては、用途や自分の作成スタイルに合わせてツールを選択することです。
補足で紹介したように「Claude で構成案を練り、Gemini でデザインを整え、ChatGPT で図解を補う」といった各 AI のいいとこ取りをするハイブリッドな使い方も、非常に効果的でおすすめです。

資料作成は時間がかかる業務ですが、生成 AI をうまく活用することで、作業時間を大幅に短縮しつつ、品質を向上させることができます。

ぜひ今回の比較を参考に、ご自身の業務スタイルに合った AI を見つけて、明日の資料作成から役立ててみてください！
