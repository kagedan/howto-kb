---
id: "2026-04-10-figma-makeのモックアップをclaudeが全然再現してくれないので一発で解決するchrome-01"
title: "Figma MakeのモックアップをClaudeが全然再現してくれないので、一発で解決するChrome拡張を作った。"
url: "https://zenn.dev/t09tanaka/articles/0822a50701f0e6"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## 悩み: Claude CodeがFigma Makeを全然再現してくれない問題

Figma Makeなどで生成したデザインモックアップを、実際のコードに落とし込む作業を行うことが度々あります。しかし、Claude CodeにURLを渡したりモックアップのファイルを渡しただけではデザインの再現がどうしてもうまくいきません。

* 背景色が無視される
* ボーダーが無視される
* フォントスタイルが無視される
* など

修正項目が多すぎて結局手作業と変わらないような時間がかかっていました。

## 原因: 描画に必要な情報が分散しているから

モックアップをClaudeに渡す方法は複数ありますが、どの手法でも、Claudeだけで再現するには至りませんでした。

* CSSの継承を追い切れない
* Component単位のソースコードだけを見てもどのスタイルが適用されるか追い切れない
* スクリーンショットでの差分チェックが難しい

などの理由があると推測できます。

## 解決: 描画結果から生成したHTML + Tailwind CSSで渡す

そこで作ったのが **Reversewind** です。  
<https://chromewebstore.google.com/detail/reversewind/nacafidpnkedkhhefdpkhjcijdabgolj>

Reversewindは、ブラウザの描画結果（computedStyle）を計算してHTML + tailwindcss に変換するので、元サイトのCSS手法に関係なく統一されたTailwind utilityクラスで出力されます。

* computedStyleなので継承・カスケード・CSS変数がすべて解決済み
* Tailwindクラスなので、Claudeが普段生成しているコードと同じ語彙

つまり「Claudeが読める形式」＋「曖昧さゼロ」の組み合わせでClaudeにスタイルの情報を渡すことができます。

### 使い方

1. 対象のデザインモックアップをChromeで開く
2. コピーしたい要素を右クリック
3. **Reversewind: Copy** を選択
4. エージェントにペーストして「これと同じデザインにして」と伝える

### 使った結果

**Original) モックアップ**

![](https://static.zenn.studio/user-upload/2fcf14bb1d2f-20260408.png)

**Copied) ReversewindでコピーしたHTMLをClaudeに渡した結果生成されたコンポーネント**

![](https://static.zenn.studio/user-upload/c71a0b998742-20260408.png)

## 終わりに

デザインモックアップの再現で同じような悩みを持っている方はぜひ試してみてください。

<https://chromewebstore.google.com/detail/reversewind/nacafidpnkedkhhefdpkhjcijdabgolj>

<https://github.com/t09tanaka/reversewind>
