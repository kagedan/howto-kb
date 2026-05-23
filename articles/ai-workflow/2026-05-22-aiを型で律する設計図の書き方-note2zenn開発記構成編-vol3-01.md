---
id: "2026-05-22-aiを型で律する設計図の書き方-note2zenn開発記構成編-vol3-01"
title: "AIを型で律する「設計図」の書き方 ｜ note2Zenn開発記（構成編 / Vol.3）"
url: "https://zenn.dev/hanav1ye/articles/note2zenn-vol3"
source: "zenn"
category: "ai-workflow"
tags: ["API", "LLM", "OpenAI", "JavaScript", "TypeScript", "zenn"]
date_published: "2026-05-22"
date_collected: "2026-05-23"
summary_by: "auto-rss"
query: ""
---

vol.3は、  
**今回使っていくツールを紹介  
➡要件定義＆方式設計書  
➡上記で作成した初回の構築結果**  
の流れでお話したいと思います。

なお、ツールは今後変更する可能性もあります。  
デスクトップアプリにするとしたら中身はそのままごっそり  
外側が変わるといった可能性もありますね・・・

## 🗄️Architecture

今回、**AI駆動開発のメインで使うのは**[**Cursor**](https://cursor.com/ja)です。  
こちらはこれまで無料枠の範囲で使っていました。

使い勝手はある程度掴めた状態ですね( ..)φ  
PJのスタートに合わせてProに課金しました。

**——— 使用する技術スタックの紹介 ————**

大前提として、[Docker](https://www.docker.com/ja-jp/)を使ってコンテナ化します。  
これは他の人にも同じように使える環境にするため！ですね

### ①Backend：Node.js(TypeScript)

![image](https://static.zenn.studio/user-upload/deployed-images/92b8c3fd1991cafd3760b363.png?sha=c5c361b0f90e91397823b8511a934d576713b672)**軽快さや開発の手に取りやすさ。**  
といった点からもポジティブで現実的な選択と考えています！

特に**Webコンテンツに対するライブラリの充実性**は、  
JS/TSの良さだと思っています✨

**TypeScript はJavaScript に『型』というルールを追加した進化版✨**  
エラーがあったときに  
JavaScriptは動的（動かさないとわからない！）  
TypeScriptは静的（動かす前から気づける！）といった特徴もあります。  
規模が大きいと『型』というルールがあるTypeScriptが選択されやすい傾向があります。

また、今回は方式設計内に敢えて型定義を  
詳細に記載したものがあります。

**私の設計を確実に反映したいポイントなので、  
コミュニケーションエラーが生じないための工夫**です。

### ②Local API：Ollama

![image](https://static.zenn.studio/user-upload/deployed-images/cdb4f524e72dee8807516f20.png?sha=785d3a7f04babed3651775d620449c884ec1ce9f)今回、Docker上、  
**OllamaはAIサーバーとして切り離し、  
データベースのように分けて扱います。**  
Imageは公式のものを利用しています。

いわゆる\*\*『関心事の分離』\*\*ですね。  
こちらについても今度別の記事にします！  
ちゃんと勉強しておきたい✨

### ③LLM：Gemma4:E2B

![image](https://static.zenn.studio/user-upload/deployed-images/3f00e7f69e5bcae89793547d.png?sha=a0aa1fed49b2f07412feeb7f543c3d6181d851a8)**必要十分**！という選択です。  
ニュアンスの細かいところまで意識すると  
後からこの選択による弊害が生じる可能性がありますが、  
技術記事への変換なら十分だろうという判断です。

主観ですが、noteへのアウトプットなら厳しそうです・・・  
※もちろんnoteのニュアンスが同じなら大丈夫です！！

以上の技術スタックを反映しつつ、要件を含めた  
**要件定義・方式設計書**が以下になります。  
※そこそこ長いので、貼り付けずダウンロードする形式にしました。

### 要件定義・方式設計（Markdown）

[**note2zenn.md** 4.48 KBファイルダウンロード](https://note.com/api/v2/attachments/download/57d726341812fd06e64cd69a7dcfbe0a)  
今回の肝は、このMarkdownなのですが・・・  
実際にCursorに渡してみるといくつか**考慮漏れ**がありました。

以下で実践していった様子を記載していきます。

## 👊Try

### 初回構築

**——— Cursorに依頼 ————**

以下のように、上記で示した要件定義&方式設計を記載した  
Markdownファイルを元にシステムを構築するよう依頼しました。

![image](https://static.zenn.studio/user-upload/deployed-images/b54b9e30f33639350fbbb1ba.png?sha=8cb30ae5ea3d1499ccdf564b4a7996a01713d178)Cursorだと以下のように、コマンドを実行する際は確認が入ります。  
**[Run]**：そのまま実行  
**[Skip]**：実行せずスルー  
**[Allowlist ’<コマンド>’]**：許可リストに<コマンド>を追加し、次回以降同じコマンドに関して確認せず実行するようになります。

![image](https://static.zenn.studio/user-upload/deployed-images/a7032d7658d051b058ab08c2.png?sha=030770ec4ec511e5b1681a34800b04cd011108aa)順調に必要なツールがインストールできたので、  
Dockerでコンテナの構築を進めます。

こういった指示はCLIでやってもいいのですが、  
今回は**どこまで最初に与えた情報だけでやれるか見てみたかった**ので、  
指示を与えて実行してみています。

![image](https://static.zenn.studio/user-upload/deployed-images/0b4c9d5d0c1cc804a0101084.png?sha=13c77ea68916abcad6c814439d83a8e3a6e8defb)ここで、**実行可能だと言われたので実行したらエラーになった**ので、  
解決を求めてみました。

![image](https://static.zenn.studio/user-upload/deployed-images/a0c3b3955c2d2ddaca65f9ee.png?sha=fa7de3a4a4a18b365de8df3b87a63a9b9323a0b3)どうやら、**Dockerの構造の指定が不十分だった**ようです。  
設計から伝わらず、**アプリ内で齟齬が生じている**状態ですね。

今は、openAIは使わずローカルLLMで解消したいので、  
LLMでの解決を目指します！

![image](https://static.zenn.studio/user-upload/deployed-images/14a04d8613d84dcb0312fb4b.png?sha=1d4a8d4fa73c364c63e89d905ba45e47f62ccd1a)認識をCursorと合わせていきます。  
**「ユーザー視点では情報はLLMに渡すのではなく、アプリに渡す。」**  
イメージだったため、それを反映するために適切な手法を考えさせます。

![image](https://static.zenn.studio/user-upload/deployed-images/6981d989fe4935eaf4d54f8c.png?sha=4f4078d132a0892d41ba183a4c4bb88fda219083)といった感じで、  
設計に一部不十分があったものの、 この段階で実行可能になり、成果物が得られました。

上記のやりとりだけでシステム構築はできたので、  
かなり順調です。あとはアプリですね・・・

※以下に記載してある  
「作成できた初回成果物（Markdown）」で初回成果物を確認できます✨

当然と言ったらあれですが・・・  
成果物は想定通りになってない箇所が複数見つかりました・・・

### 想定外の挙動・ソース

大きく分けて3つほどありましたので以下にまとめます！

![image](https://static.zenn.studio/user-upload/deployed-images/c186f81005bd0d8e8b98830e.png?sha=0ea5fd09efe05f0d68170e5af69333364972136d)**——— ①与えた型の利用方法漏れ ————**

あんなに丁寧にTypeScriptで型を用意するように記載したのに、  
**どう使うか明記してなかったせいで使われていませんでした**。

![image](https://static.zenn.studio/user-upload/deployed-images/86f32e5516e0cd214e5683bd.png?sha=55daab2c73e9dbc668ffa671ab607ea426fd3e99)

**——— ②Zennへの調査漏れ ————**

これは**要件定義時の漏れ**です。  
ZennにはZenn記法や表現があるので、  
それを活用するための変換が定義できていませんでした。

結果として以下の通り、想定通りに動作しない箇所が生じました。

**画像が表示できない（パス設定の不明確）**  
➡Markdown

```
#### 🚩 コンセプト
目的を達成し、競合ツールとの対抗軸として、コンセプトは一言で表すと以下の通りです。

➡画像
![image](/images/2.png)
```

➡画像  
![image](https://static.zenn.studio/user-upload/deployed-images/55701cf0b8e44b66dddc11a8.png?sha=6df740a7528a260858bd781a57de8aa13b397546)

**Zennのmessage記法ができない（detailsになってた）**  
➡Markdown

```
:::message
外部APIに頼らないという点で、LLMをローカルで動かせない人のために、従量課金のOpenAI APIに切り替えられる仕組みも考えていきたいと思っています。
:::
```

➡画像  
![image](https://static.zenn.studio/user-upload/deployed-images/83bc150ca96a9fb8bd197a58.png?sha=797f05ca9526657c8b9055401f34b377e3dcd9f8)  
**tags（noteのタグ）が設定されない**

![image](https://static.zenn.studio/user-upload/deployed-images/44f91ede6e25279a34234129.png?sha=66af19d371da12958fb0ce731a95d6d971cd4220)

**——— ③LLMに与える必ず適用する変換ルールの漏れ ————**

\*\*ユーザーがカスタムできるようにする\*\*ことに焦点を置きすぎて、  
\*\*常に与える必要がある制約\*\*が明示できていませんでした。

これも**要件定義の漏れ**です。  
今回のようにnoteの記事というインプット、  
Zennの記事というアウトプットがはっきりしていたのに、  
そこまで見据えられなかった・・・

要件定義もAIと相談していたのですが、  
\*\*ある1点にこだわったことで灯台下暗し。\*\*になるのは注意ですね💦

### 作成できた初回成果物（Markdown）

今回の成果物は、[note2ZennのVol.1の記事](https://note.com/hanaviye/n/n8d3b38d58ad4)を変換しています！

実際にZennの画面だとどのような状態か確認できます！  
本という形式にしたので、今後も色々パターンを試行錯誤予定です！

[初回構築時/No.1｜note2Zenn 改善記録](https://zenn.dev/hanav1ye/books/note2zenn-project/viewer/chapter1)

見ていただけたらわかるのですが、  
大まかには許容範囲・・・であるものの、  
ここからは**LLMへ渡す情報を精査していく必要がありそう**です。

先の通り、  
**②Zennへの調査漏れ  
③LLMに与える必ず適用する変換ルールの漏れ**があったので、  
まずはこちらを適用し、  
**\*\*画像やtagsが自動的に取り込めること\*\*  
\*\*安定感を出すこと\*\*  
\*\*利用者のカスタム性を表現すること\*\***  
ですね！

## 📚Summary

今回、要件定義～方式設計を曖昧にせず詳細に書いた状態  
という準備をしたつもりでしたが、それでも不十分でした。  
この過程で特に重要だと感じたことを振り返ります。

### ➡要件定義を漏れなく行うためには・・・

**自分以外の視線を持つことが大事**です。  
また、独自性としてカスタムできる！という要素を意識したことで、  
基本処理に漏れが生じたのは、私の経験不足を感じました。  
一人だとどうしても見落とすことがありますね・・・

**🌸既存の製品あるなら、それらができていることができる。**  
というのは、[リファレンスアーキテクチャ](https://www.hpe.com/jp/ja/what-is/reference-architecture.html)の観点で非常に大事です。  
そういった観点でのセルフレビューも欠かさず行おうと思います！

### ➡『型』を指定して開発をするなら・・・

**今回TypeScriptを使い、型を固定することで  
私のイメージを具現化する際に齟齬が生じないのでは？**  
と思い、設計段階で要素まで記載しました。

ただここまでやったことで、  
**「ここまで書いたら、何に使うかわかるでしょ」という思い込み**を私は起こしました。

逆に試せていませんが、要素まで固定せず  
「ユーザーの入力に応じて●●と△△をパラメータとして保持し、  
その値をLLMに渡すことでカスタム可能にする」というような

**具体化せず、データの流れがわかる記載だけ**をしていたら、  
もしかすると想定通りの結果になっていた可能性もあります。  
※”遊びを持たせる”ようなイメージです。

**🌸『型』を詳細に書くなら、  
🌸”それらはこのように使用する”と、  
🌸入口から出口まで責任ある設計にするべきでした。**

### ➡文章以外のアプローチの仕方を持っておく

**図の方が直感的に理解しやすく、記憶にも残りやすい**とされています。  
心理学では「画像優位性効果」と呼ばれるものですね。

これは自論ですが、  
**🌸理解できているかどうかの確認に\*\*図示\*\*は打って付け**だと思っています！！！

図示には[**mermaid**](https://help.docbase.io/posts/3719897)というツールがおすすめです。  
※公式じゃなくて日本語のサイトのリンクをつけておきました。

文章よりも図のほうがズレや漏れがあったときに気付きやすいです。

でも図示すると時間も労力も使うので、  
そんなときこそ生成AIにお願いしましょう✨

🌸**mermaidのコードはAIとも相性が良い  
🌸構築前に作成してInputにすれば精度向上が期待できる**

もし余裕があれば、以下の手順をやってみてください！

①生成AIに設計を渡して、以下をお願いする

```
渡した設計をシーケンス図で表現してください。
なお、出力はmermaidで扱えるコードでお願いします。
シーケンス図には、各構成要素で行う処理、要素を可能な限りすべて反映させてください。
```

②出力されたコードを[Mermaid Live Editor](https://mermaid.live/edit#)に張り付ける。

![image](https://static.zenn.studio/user-upload/deployed-images/1e659438d8b1f7ce7c2e72af.png?sha=e34a680db7ce507ccd42b2c365638d7f9c10c7ad)③不足する要素や追記する必要がないか確認する。  
今回、私の設計はおおよそ反映できているのですが、  
**実際に漏れた変換リクエストの前処理 = プロンプト読込  
➡固定プロンプト 及び ユーザー入力(カスタム要素)の反映**  
がここにも入っていないので、追記しました。

![image](https://static.zenn.studio/user-upload/deployed-images/bc9a1c75d9cdd8accfea3422.png?sha=cd54ffa292a0f826e42fc5ea0edb4b1233cf59ee)mermaidは複雑に見えますが、修正したり追記する分には、  
そこまで深い理解が求められないのでこういった使い方がオススメです✨

## 👉Next Action!

次回は\*\*『LLMへのプロンプト編』\*\*です！  
なかなか思い通りにチューニングを表現できず、  
試行錯誤する中で見えてきた課題がたくさん・・・

包み隠さず、記録していきます！！！

以上、\*\*『構成編』\*\*でした🌸
