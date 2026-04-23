---
id: "2026-04-20-figmaの株価を一夜で7下落させたclaude-designがやばすぎたので徹底解説します-01"
title: "Figmaの株価を一夜で7%下落させた「Claude Design」がやばすぎたので徹底解説します"
url: "https://qiita.com/ot12/items/92ec6ea6e5a3a0b57226"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

2026年4月17日、AnthropicがAIデザインツール「Claude Design」をリリースしました。

リリース当日には、Figmaが7%・Adobeが2.7%・Wixが4.7%と、デザイン／Web制作系の株価が軒並み下落するほどのインパクトでした。

実際に触ってみた感想としては、現状では**めっちゃすごい！！！でもトークン量エグすぎて、本格運用はまだかなー**という感じです！

そこも含めて、この記事では何ができるかや実際に触ってみた感想を解説していきます！

こちらも合わせてどうぞ！

## Claude Designとは

[![スクリーンショット 2026-04-20 10.38.54.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F54d38854-f82f-48a5-9268-d6fc9e7b071d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4213ad0517a0f2967f36d9ed652d0c58)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F54d38854-f82f-48a5-9268-d6fc9e7b071d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4213ad0517a0f2967f36d9ed652d0c58)

ひとことで言うと、**チャット形式でアプリやLPのデザインが作れるAIツール** です。Anthropic社内の新部門 **「Anthropic Labs」** 発の初プロダクトで、2026年4月20日現在は **リサーチプレビュー** として提供されています。

AIに対話でデザインを作らせるツール自体は、v0、Lovable、Bolt、Stitchと、すでに選択肢がいろいろあります。それでもClaude Designが騒がれているのは、**デザインからそのまま本番コードまで繋がる** 点です。

モックで終わらず、Claude Codeへ1コマンドで渡せば、そのまま実装に入れます。「企画→プロトタイプ→実装」をAnthropicのスタックひとつで完結させる。これがClaude Designの、いちばん大きい違いです。

### どこで使える？使えるプランは？

[![005-where-use.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F990c0296-2d80-4a10-bbd2-3676f985e0ae.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4850e3a03d888972bc00f044ab5ef71f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F990c0296-2d80-4a10-bbd2-3676f985e0ae.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4850e3a03d888972bc00f044ab5ef71f)

Claude Designは現在、**Webブラウザ専用** です。デスクトップアプリ版やターミナル版はありません（Claude Codeとは別ツールです）。

Webブラウザ版のClaudeにアクセスして、左のメニューバーから開けます。

対応プランは以下のとおりです。

| プラン | 月額の目安 | Claude Design |
| --- | --- | --- |
| Free | 無料 | ❌ 使えない |
| **Pro** | 20ドル〜 | ✅ 使える |
| **Max** | 100〜200ドル | ✅ 使える |
| **Team** | 25ドル／人〜 | ✅ 使える |
| **Enterprise** | 要問合せ | ✅ 使える |

無料プランは対象外なので、まだ触ったことがない人は **Pro（月額20ドル）が最安の入り口** です。

## Claude Designでできること

ざっくり、以下の流れを全部Claude側が引き受けてくれます。

1. 「**こういう画面が欲しい**」と自然言語で伝える
2. Claudeが **5〜15秒で初版を生成** してキャンバスに出す
3. 会話・直接編集・インラインコメント・スライダーで **仕上げる**
4. PDF・PPTX・HTML・Canva・Claude Codeなどに **エクスポート** する

Figmaのように「ツールを選んで、矩形を引いて、塗りを指定して…」という手順は、一切いりません。チャットで指示すれば、もうできています。

もう少し具体的に、できることを3つの軸で整理します。

### ① 何を渡せるか（Context入力）

チャットの指示文に加えて、以下を全部読ませられます。

[![スクリーンショット 2026-04-20 9.35.03.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fb7f3f0d8-b615-4366-81c8-3fdfe3386e37.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=95356d6fb50808b3e2e169e8b775bea1)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fb7f3f0d8-b615-4366-81c8-3fdfe3386e37.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=95356d6fb50808b3e2e169e8b775bea1)

* **スクリーンショット**：参考にしたいUIや雰囲気を画像で渡す
* **コードベース**：GitHubリポジトリを読ませて、自社のコンポーネントで組ませる
* **Figmaファイル**：既存のデザインをドラッグで投入
* **デザインシステム**：色・タイポ・コンポーネントを事前に登録しておくと、以降のプロジェクトに自動適用
* **手描きスケッチ**：napkinに描いたラフをそのまま添付できる

私が試したときも、雑な手描きナビ＋グラフを描いてドロップしたら、「こんなダッシュボードが欲しい」の意図をほぼ汲んでくれました。

### ② 生成したあとの調整機能が4種類

出したデザインを「ここだけ直して」と指示できるパターンが4つあります。

[![スクリーンショット 2026-04-20 9.37.31.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fb0bf94ad-e8e4-45db-b5e5-6f8f55993cd5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=98e5eca65a8f5711b8067f94d5a2207d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fb0bf94ad-e8e4-45db-b5e5-6f8f55993cd5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=98e5eca65a8f5711b8067f94d5a2207d)

* **チャット追加指示**：「右のカードを2カラムに」のような構造変更
* **インラインコメント**：キャンバス上の要素をクリックして、その要素だけ直す
* **直接編集**：テキストや色を手で書き換える（Figma感覚）
* **カスタムスライダー**：Claudeが「この要素動かすならスライダー出しました」と、勝手に調整UIを作ってくる

[![スクリーンショット 2026-04-20 9.40.14.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F0f6d6414-248b-4611-9300-da8bda3f70f6.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d0d91bc8a044c08edc26289302754eda)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F0f6d6414-248b-4611-9300-da8bda3f70f6.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d0d91bc8a044c08edc26289302754eda)

直接編集はFigmaに近い操作感です。テキストをダブルクリックで書き換え、色はカラーピッカーで選び、フォントはNoto Sans JPなどプルダウンから選択します。

### ③ エクスポート先が5種類

[![スクリーンショット 2026-04-20 9.40.41.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F60506f0b-5388-4fe9-8f8d-9eaa986ec776.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cca85d034ffe34710d9e9f147f59ffe4)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F60506f0b-5388-4fe9-8f8d-9eaa986ec776.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cca85d034ffe34710d9e9f147f59ffe4)

* **PDF / PPTX / スタンドアロンHTML / ZIP**
* **Canva**：Canva側で引き続きチームで共同編集できる（CanvaはClaude Designの公式連携パートナー）
* **Claude Code**：ワンコマンドで実装コードに変換

## 何が作れるのか

### ① プレゼン資料

まず、汎用的な使い方として一番有益なのはスライド作成ができることです。  
しかもスピーカーノートの作成もしてくれます!

[![スクリーンショット 2026-04-20 9.51.57.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fdbd741a1-ee19-4405-a82d-8e0b3f5404fd.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d8000ac96d450a56b569098f53d5789c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fdbd741a1-ee19-4405-a82d-8e0b3f5404fd.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d8000ac96d450a56b569098f53d5789c)

スライド作成する前に色々とヒアリングをしてくれるので、まず何をやりたいかざっくり伝えて、あとは質問に答えていくだけでスライドが完成します

[![スクリーンショット 2026-04-20 9.54.42.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F8f21f262-e707-47a4-8e2c-ff77688dec5d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4031fc7d79a6cd2c381e0d4dc9db77eb)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F8f21f262-e707-47a4-8e2c-ff77688dec5d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=4031fc7d79a6cd2c381e0d4dc9db77eb)

実際に作成したスライドがこちらです

[![スクリーンショット 2026-04-20 10.22.25.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fc31a4d39-7171-4a6f-8abf-8a9390dc050a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=43ec66bb6ac97ee7886ed4651a80a86d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fc31a4d39-7171-4a6f-8abf-8a9390dc050a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=43ec66bb6ac97ee7886ed4651a80a86d)

pptxとして出力できるのでそのまま編集も可能です

### ② アプリのプロトタイプ作成

アプリやLPの叩き台を作ることもできます

試しに私も**マーケティング分析ツールのダッシュボード**を作らせてみました。

[![05-dashboard-complete.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fb0c5adcb-4eb6-4c50-a8c9-068a1753bc4a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e6719c658693291c6d592ccae1c319a4)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fb0c5adcb-4eb6-4c50-a8c9-068a1753bc4a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=e6719c658693291c6d592ccae1c319a4)

サイドナビ・KPIカード・媒体別パフォーマンス・シミュレーションAIまで、「こういうSaaSが欲しい」と伝えただけで数分で出てきました。

面白いのは、いきなり生成するんじゃなくて、まずヒアリングから始まることです。

[![03-hearing-variation.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fc9f06291-aa96-4216-bade-6ab60a5b28f4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=13397c8cda9013faeb5fe712ebd05aca)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fc9f06291-aa96-4216-bade-6ab60a5b28f4.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=13397c8cda9013faeb5fe712ebd05aca)

「メニュー構成はどうする？」「バリエーションは何パターン欲しい？」「軸は何で切る？」と、先方担当者みたいな質問が続きます。ここで適当に答えると、そのまま「普通のダッシュボード」が出てきます。私はこの段階で **「ROAS測定」「媒体別分解」「AIシミュレーション」の3軸が欲しい** と具体的に伝えました。

[![スクリーンショット 2026-04-20 10.28.36.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F3f8e02c6-529a-478e-9898-dbbe5c83f67e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=898ef5c8bdd9f7545736f985735550c4)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F3f8e02c6-529a-478e-9898-dbbe5c83f67e.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=898ef5c8bdd9f7545736f985735550c4)

結果、複数画面にまたがるナビゲーションも、ちゃんと繋がった状態で生成されます。**最初のヒアリングでどれだけ具体的に答えるか** が、仕上がりの8割を決めると感じました。

### ③ LP作成

LPの作成も、同じ流れで量産できます。

[![スクリーンショット 2026-04-20 10.30.48.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F7918ee60-a0c4-42a5-85ab-ab1ca5247773.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=8b6456616dada90e1f842130fe72c025)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F7918ee60-a0c4-42a5-85ab-ab1ca5247773.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=8b6456616dada90e1f842130fe72c025)

私は株価予測AIのLPを試しに作ってみました。プロダクト名、ターゲット層、トーン、言語を3分で答えて、次に「Hero画像、特徴3つ、使用シナリオ、料金表、FAQ、登録CTA」を選ぶ画面に進みます。答え終わると、もうLPが動いています。

LP内で動くアプリのモックも作ってくれており、驚きしかなかったです

[![スクリーンショット 2026-04-20 10.31.55.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fc202adab-db5a-48df-91eb-215283cfafce.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cb43b647790e8b79322691a46e23e6ad)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2Fc202adab-db5a-48df-91eb-215283cfafce.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cb43b647790e8b79322691a46e23e6ad)

### ③ そのまま本番コードへ

[![スクリーンショット 2026-04-20 10.33.06.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F19f18b00-7177-42c1-8faf-2229e1dc626f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=caa1ec512e614f6c545efa8528a56e9f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F19f18b00-7177-42c1-8faf-2229e1dc626f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=caa1ec512e614f6c545efa8528a56e9f)

そして、ここが他のAIデザインツールと決定的に違う点です。**Claude Codeへのハンドオフ** 機能で、できあがったデザインをワンコマンドで本番コードに変換できます

つまり、「企画→プロトタイプ→実装」が、全部Anthropicの中で完結します。

## 今すぐ使う方法

対応プランは Section 1 にまとめた通りです。ここでは「ログインしてから、初キャンバスを出すまで」の最短ルートを見ていきます。

### ① 最初の画面

アクセスすると、左側に4つのタブが並んでいます。

[![スクリーンショット 2026-04-20 10.07.05.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F414e5274-30ff-4ccd-9444-bc74df7337c0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=575b974e35f2f90c56d0a404f5a36215)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F414e5274-30ff-4ccd-9444-bc74df7337c0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=575b974e35f2f90c56d0a404f5a36215)

| タブ | 作るもの |
| --- | --- |
| **Prototype** | アプリ・Webサイトの動くモック |
| **Slide deck** | スライド・ピッチデッキ |
| **From template** | テンプレからスタート |
| **Other** | LP・ワンページャーなど |

Prototype タブを選ぶと、次に **Wireframe**（ラフ）か **High fidelity**（本番ライク）の2択が出てきます。最初は「いったんラフで複数案出してもらう → 気に入った案を本番ライクに昇格」の流れが楽です。

[![スクリーンショット 2026-04-20 10.05.48.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F2453749d-8912-4e23-81ec-496180db44a3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5cef478a2f0fe65ca3f7d416d1d10979)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F2453749d-8912-4e23-81ec-496180db44a3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5cef478a2f0fe65ca3f7d416d1d10979)

右側の **Examples** タブを開くと、公式のプロンプト例が10種類ほど並んでいます。`Use this prompt` ボタンでそのまま流用できるので、最初の1発目はこれで体感するのがいちばん早いです。

### ② 最初のプロンプト例（コピペOK）

**ピッチデッキ用**

```
AIでSNS運用を自動化するSaaSのシードラウンド用ピッチデッキを
10枚で作って。課題・ソリューション・プロダクト画面・競合比較・
チーム・トラクション・市場規模・ビジネスモデル・Ask・ビジョンを含めて。
```

**LP用**

```
フリーランスデザイナー向けの請求書SaaSのLPを作って。
ダークモード、ヒーローにスクリーンショット、特徴3つ、
料金表、FAQ、登録CTAを含めて。
```

**アプリUI用**

```
読書記録アプリのモバイルUIを3画面で。
ホーム、本の詳細、読書ログ入力画面。
温かみのあるベージュ系のトーンで。
```

### ③ 生成後の4つの修正方法

[![スクリーンショット 2026-04-20 9.37.31.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F6b11a710-44ed-41e9-b2d6-b52c770a7912.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=fd734152ff6cbf42fa661a316123e036)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F6b11a710-44ed-41e9-b2d6-b52c770a7912.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=fd734152ff6cbf42fa661a316123e036)

初期デザインが生成されたら、そこからは以下の4つの修正方法で理想のデザインに近づけていきます

1. **チャットで追加指示**：「右のカードを2カラムに」
2. **インラインコメント**：キャンバス上の要素を直接クリックして指示
3. **直接編集**：テキストを選択して書き換え
4. **カスタムスライダー**：Claudeが用意した調整UIで数値を動かす

### ④ 書き出し

[![スクリーンショット 2026-04-20 10.03.16.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F862d481e-454c-4459-9f4a-db555b43ffdc.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3f271e06e8e3d1913a4a3fd93cb4b890)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F862d481e-454c-4459-9f4a-db555b43ffdc.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=3f271e06e8e3d1913a4a3fd93cb4b890)

完成したら、右上のExportから**PDF / PPTX / HTML / Canva / 社内URL / Claude Codeへのハンドオフ** から選べます。Canva連携は強力で、Canva側で引き続きチームで共同編集できます。

## 触る前に知っておきたい3つの落とし穴

ここからは、触る前に知っておくと事故らずに済む話です。

### ① トークン消費が激しい

[![スクリーンショット 2026-04-20 10.01.23.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F173c413a-7ec9-46b1-8723-61f9f385a299.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f90e86deec28c5762b075a1c84af969d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3356814%2F173c413a-7ec9-46b1-8723-61f9f385a299.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f90e86deec28c5762b075a1c84af969d)

Claude Designは通常のチャット1ターンよりも、圧倒的にトークンを食います。

実際に、私もダッシュボードとLP、スライド作成を1日で試したら、MAXプランでその週に使えるトークンをほぼ消費してしまいました

ただ、Claude Designは通常のチャットやClaude Codeとはトークン消費量が分かれているので、使いすぎても普段の利用には支障は出ません

### ② Undoで全消し事故

Undoボタンを「戻るボタン」と誤解して、全作業を失った報告があります。Claude Designの Undo は「1ステップ戻る」ではなく、**セッション単位で巻き戻る** 挙動のケースがあるようです。  
真面目に作業する時は、こまめに PDFや Canva へ書き出して、外部に状態を逃がしておくのが一番安全です。

### ③ 放っておくと「Anthropicっぽい」見た目になる

ブランドの指示を出さないと、Claudeの標準的なテイストに寄っていきます。紺×白×サンセリフの、いかにも「テック企業のサイト」が量産されます。

最初に「このブランドのトーン」「このカラーパレット」「参考にしたい既存サイト」を指定するだけで、仕上がりが大きく変わります。

## まとめ：今日踏み出す一歩

* Claude Designは2026年4月17日リリース、Opus 4.7搭載のAIデザインツール
* チャット形式でデッキ・プロトタイプ・LPが数秒で作れる
* 自社デザインシステムの自動適用＋Claude Codeへのハンドオフが決定的な差別化
* Pro以上なら今日から触れる

試し方はシンプルです。

1. Claude Proにログイン
2. [claude.ai/design](https://claude.ai/design) にアクセス
3. 右の **Examples** タブから気になるプロンプトで `Use this prompt`
4. 出てきた絵をTweaksで触る

Figmaの株価が落ちた意味は、30分触れば体感できます。最初は Examples の「Pitch Deck」か「Landing Page」を1つ選んで、**Use this prompt** をそのまま走らせてみてください。1回動かすだけで、デザインに対する自分の速度感が、確実にアップデートされるはずです。

こちらも合わせてどうぞ！

---

## 参考ソース
