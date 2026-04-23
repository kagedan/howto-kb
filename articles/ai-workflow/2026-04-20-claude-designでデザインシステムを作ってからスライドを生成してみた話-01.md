---
id: "2026-04-20-claude-designでデザインシステムを作ってからスライドを生成してみた話-01"
title: "Claude Designでデザインシステムを作ってからスライドを生成してみた話"
url: "https://qiita.com/ogaryo/items/7b3136fd2a8efe7a1a83"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Design みなさん試しましたか？  
もちろん私も試しました。  
一先ず、適当な仮PJの画面をリデザインしてもらって満足していたんですが、  
このClaude Design、スライドも作れるんです。

元々NoteBookLMを使ってスライドを作成していたんですが、細かな修正がしづらく、結局Reactで作った自作スライドを使ってました。

ですが、Claude DesignにはEditモードがあるじゃないですか！  
しかもデザインシステムとしてスライドのテンプレート（テーマ）も作ってもらえて、流用できる…！

これは良さそうだと思いさっそくスライドを作ってみました。

## Claude Designってなに？

Claude Designは Anthropic 公式のAIデザインツールです。

チャット形式でUI・資料・スライドを生成できます。  
「指示書を書くだけでデザインが出てくる」体験をAnthropicのエコシステムの中で完結させようとしているイメージです。

特徴をざっくりまとめると：

* チャットで指示するだけでスライドやUI/ワイヤーフレームが出力される
* デザインシステムをプロジェクト横断で再利用できる
* 出力はHTML単体ファイル、PPTXエクスポートも可能
* Editモードで要素を直接クリックして細かく調整できる
* DrawモードでUI上に手書きで指示できる
* Commentモードで各コンポーネントに対して指示できる

デザインシステムの再利用ができるのが特に強いですね。  
これについては後ほど詳しく。

## Step 1: 「デザインシステム作って」と言うだけ

まずはデザインシステムを作成します。ここで何かテーマがある方はプロンプトを作ってください。  
私の場合はよく使うPPTXがあったのでそれを添付しました。

「このPPTXをもとにデザインシステムを作って」。

すると Claude が以下をやってくれました。

* フォント（うちの場合はMurecho）をPPTXから自動抽出
* ブランドカラーを画像から直接サンプリング
* ロゴ・ボートマーク画像を抽出
* CSS変数ファイル（`colors_and_type.css`）まで生成

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F5315a41e-35b4-43ea-aab5-c1e85cf97602.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b1091f5862162d3996ee108e3711f90d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F5315a41e-35b4-43ea-aab5-c1e85cf97602.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=b1091f5862162d3996ee108e3711f90d)

カラートークンもタイポグラフィも全部 CSS 変数として整理されるので、スライド全体のブランド一貫性が自動で担保されます。  
自分でやると地味に時間がかかる作業なんですよね、これ。

## 地味にすごい：色を間違えても自己修正してくる

最初、Claudeはメインカラーを赤（`#C8102E`）と誤認識していました。

実際は画像をサンプリングし直した結果、コーラルピンク（`#F19793`）に自己修正してきました。

「AIが自分の間違いを画像のピクセル単位で直してくる」という体験、地味に新鮮です。  
人間がレビューして「この色ちがくない？」とつっこむ工程を自分でやってくれる感じ。

最終的にカラートークンもタイポグラフィも整理されて、デザインシステムとして使える状態になりました。  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F59aa42a9-f791-4356-9c6c-55f247ad18ca.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d6d865e785618f911b40486c8ee5b8a8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F59aa42a9-f791-4356-9c6c-55f247ad18ca.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d6d865e785618f911b40486c8ee5b8a8)

最初のチェックだけは人間がやること。ここさえ抑えれば、あとはかなり信頼できます。

## 生成されたスライドコンポーネント一覧

デザインシステムが出来上がると、スライドコンポーネントも自動で生成されます。

| コンポーネント | バリアント |
| --- | --- |
| TitleSlide | light / dark / accent |
| ChapterSlide | - |
| ContentSlide | - |
| ClosingSlide | - |
| MemberIntroSlide | hero / duo / grid |

MemberIntroSlideは後から「メンバー紹介も欲しい」と追加要望しただけで実装されました。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2Fafdc7ed5-c57b-4f8a-9a33-3ac002983d84.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e8892541a69fa9b4588a54b8dafc01d8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2Fafdc7ed5-c57b-4f8a-9a33-3ac002983d84.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e8892541a69fa9b4588a54b8dafc01d8)

メンバー数に応じてhero / duo / gridのレイアウトを自動で切り替えてくれます。

アバター画像を指定しない場合は、頭文字と決定論的な背景色で自動生成されます。  
Slackのプロフィールアイコンっぽい感じのやつです。  
細かいところまで気が利いてますよね。

## 途中で起きた「ダーク背景にダークロゴ」事件

TitleSlideのdarkバリアントで、視認性がゼロになる問題が発生しました。

ダーク背景にダークロゴを置いてしまっていて、ロゴが背景に溶け込んで見えない状態です。

この不具合を右上のcommentから指示しました。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F4752aea4-de70-48d0-b813-cdf1b2530ed3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=8583e3e941eb5308eb36cbd113d653da)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F4752aea4-de70-48d0-b813-cdf1b2530ed3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=8583e3e941eb5308eb36cbd113d653da)

ClaudeはこれをさっさとFixして、背景バリアント（light / dark / accent）に応じてwhite / darkのロゴを自動で切り替えるロジックを追加してきました。  
ClosingSlideもaccentをやめてdark variant + 白ロゴに刷新。

## Step 2: 作成したデザインシステムを活用しスライドを作成する

新しいスライドプロジェクトを作成します、さっき作った Design System を選択します。  
あとは 資料を添付し「スライドにして」と指示するだけ。

今回は以前紹介したQiita記事「社内RAGチャットボットを作ってみた」をURLを添付しました。

すると Claude からいくつか質問が来ます。

* 聴衆は？
* フォーカスしたいポイントは？
* スピーカーノートは必要？
* タイトルスタイルは？
* 図解の方向は？

今回の回答例：

* 社内LT
* RAGの基礎・Embedding
* ですます調で入れて
* アクションタイトル
* 横長フロー

あとは待つだけ。

## 出てきたスライド

生成されたスライドを選出しました、こんな感じです。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2Fcf855d6d-9fe2-4cf7-a4db-7c9d530c9f39.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=de7530811c3306b5740fd006e63ff9e6)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2Fcf855d6d-9fe2-4cf7-a4db-7c9d530c9f39.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=de7530811c3306b5740fd006e63ff9e6)

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F96ae0f80-31f0-408a-90bc-f3f5d0b1045c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ed15acaa20afc76e289c62e8c51df150)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F96ae0f80-31f0-408a-90bc-f3f5d0b1045c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ed15acaa20afc76e289c62e8c51df150)

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F4c6b92ad-438e-44dd-a72a-7a2f008016fe.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6f3b8b42398bcadfa90976293ce9d504)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F4c6b92ad-438e-44dd-a72a-7a2f008016fe.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6f3b8b42398bcadfa90976293ce9d504)

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F977d7611-1732-42d4-9587-3e37cb0969e4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=28cfae48d8b68cd7ab81a7bf8f51c11a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F977d7611-1732-42d4-9587-3e37cb0969e4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=28cfae48d8b68cd7ab81a7bf8f51c11a)

いかがでしょうか、個人的にNoteBookLMは一枚のスライドの中に情報量が多い印象がありましたが、Claude Designは要点だけをうまくまとめている印象でとても質がいいと感じました。

各スライドにスピーカーノートも同梱されていて、「何を話すか」まで設計されています。  
記事の論理構造をそのままスライドの流れに変換してくれる感じで、構成を考える手間がほぼゼロです。

画面右上のPresent→In this tabからプレゼン用のタブを用意してくれます。  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F175d1242-a5d6-4b6b-99cc-4aa7b607feff.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5cf139a67e5068f13a7e798fd1164cd8)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F175d1242-a5d6-4b6b-99cc-4aa7b607feff.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5cf139a67e5068f13a7e798fd1164cd8)

## FigmaのようにEditで細かく直せる（NotebookLMとの違い）

似たようなスライド自動生成機能、NotebookLMにもありますよね。  
あっちと比べて Claude Design がいいと感じたのが、Editモードの存在です。

NotebookLMのスライド生成は、paddingや文字サイズなどの細かい調整ができないんですよね。  
「もう少し大きく」と指示するしかなくて、微妙なズレが積み重なるとストレスになります。

Claude DesignのEditモードは、Figmaと同じ感覚で要素を直接クリックしてサイズや余白を調整できます。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F216d1a44-7b1e-4fe8-be41-0cd1f10a466a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c3196bc38c5948cb7c06b02302906f91)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4367945%2F216d1a44-7b1e-4fe8-be41-0cd1f10a466a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c3196bc38c5948cb7c06b02302906f91)

## 使ってみて感じたこと

良かった点：

* プロンプト＆既存資料 → デザインシステム化の自動化が想像以上に強い
* スライド,資料化のゼロ→イチ工数が大幅削減
* 一度デザインシステムを作れば次回以降の投資対効果が爆上がり
* デザインシステムを学習（修正）させることでよりベストな構成にできる
* Comment,Edit,Drawモードのおかげで「AIに任せきり」にならなくて済む

## まとめ：スライド作成はClaude Designで良い！

今回はClaude Designの数ある機能の中のデザインシステム作成とスライド作成に絞りましたが  
Claude Design、デザインシステム × 生成AI の体験として完成度高い感じだと思いました。

あとちょっと気になったのが、待ち時間が増えたかも…？  
今回は軽い作業しかさせませんでしたが、機能豊富な画面デザインではそこそこ時間がかかった印象でした。

次は本命のデザインやWireframeなどを詳しく調べていきます。
