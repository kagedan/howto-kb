---
id: "2026-04-23-非エンジニアでも利用できる-claude-design-で-lt-会の告知-lp-を作ってみる-01"
title: "非エンジニアでも利用できる Claude Design で LT 会の告知 LP を作ってみる"
url: "https://qiita.com/leomarokun/items/81101a9afa181d526948"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-23"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

## はじめに

2026年4月17日 Anthropic Labs から発表された **[Claude Design](https://www.anthropic.com/news/claude-design-anthropic-labs)** を触ってみました。

本記事は **実際の題材を1本決めて、プロンプト投入から仕上げまでを時系列で追う**形で進めてみます。  
読みながら「こういうことに使える、こういうこともできるかもな」とイメージを持てたら目的達成です。

## Claude Design とは

Claude Design は Claude Opus 4.7 を内部で動き、会話しながらビジュアルを作り込めるツールです。Claude Design は \*\*Web 版（`claude.ai/design`）\*\*で利用可能ですう。

## 今回作るもの

具体的な題材が無いと操作の話がふわっとしてしまうので、以下の架空イベントを想定します。

**架空の社内 LT 会「AI Lab Meetup Tokyo #3」の告知 LP**

| 項目 | 設定 |
| --- | --- |
| イベント名 | AI Lab Meetup Tokyo #3 |
| テーマ | Claude を業務で使い倒す |
| 日時 | 2026年5月20日（火）19:00〜21:00 |
| 会場 | 渋谷のコワーキングスペース（オフライン + オンライン配信） |
| 対象 | LLM を業務に組み込みたいエンジニア・PdM |
| トーン | エンジニア寄り、落ち着いたダーク基調、派手すぎない |

1ページの告知 LP で、以下のセクションを含める想定です。

プロンプトで初版を出し、会話／スライダー／コメント／直接編集の4手段で詰める流れを実演します。  
「ざっくり作って → 細部を連続的に動かして → 最後に自分の言葉に書き換える」というちょっとやってみるイメージです。

## 先に Claude Design の位置づけについて理解

触る前に「Claude Design はどこにある何なのか」だけ軽く押さえておきます。

* Claude.si は **会話特化の UI** で、テキストベースのやりとりに向いている
* Claude Design は **ビジュアル制作特化の UI** で、デザインの細部を会話とインタラクションで詰めるのに向いている
* Claude Code は **コーディングエージェント** で、実装フェーズでコード生成やリファクタリングを任せるのに向いている

といったところでしょうか。

## やってみる

ここからが本題です。以下の5ステップで LP を仕上げていきます。

### Step 1 — プロンプトで初版を生成する

左ペインのチャットに、題材のアウトラインをそのまま投げ込みます。  
最初から細かく指定しすぎず、**雰囲気と骨格** だけを伝えてみます。  
（後から連続的に動かせる手段が豊富なので、初版は叩き台で十分かという想定です）。

実際に投げたプロンプトはこんな感じです。

```
社内 LT 会の告知 LP を 1 ページで作ってください。

イベント: AI Lab Meetup Tokyo #3
テーマ: 「Claude を業務で使い倒す」
日時: 2026年5月20日(火) 19:00〜21:00
会場: 渋谷のコワーキングスペース（オフライン + オンライン配信）
対象: LLM を業務に組み込みたいエンジニア・PdM

含めたいセクション:
- ヒーロー（タイトル・キャッチコピー・申込 CTA ボタン）
- イベント概要（日時・場所・対象）
- タイムテーブル（LT 3 本 + パネルディスカッション）
- 登壇者紹介カード 4 枚
- 申込 CTA

トーン: エンジニア向け。ダーク基調、アクセントはブルー系。
技術カンファレンス寄りで落ち着いた印象に。派手な装飾は避ける。
```

送信後、右ペインのキャンバスに初版が出てきます。  
このタイミングでタイムテーブルの LT タイトルやなどはダミーで入っている想定ですが、**レイアウトとトーンの方向性** を確認するのが主目的です。

[![スクリーンショット 2026-04-22 20.12.48.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2Fdc95a553-ccb1-40b4-aad5-3a96466beafa.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=27ff37dfaac85a158b3ce5fa1813466d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2Fdc95a553-ccb1-40b4-aad5-3a96466beafa.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=27ff37dfaac85a158b3ce5fa1813466d)  
[![スクリーンショット 2026-04-22 20.13.32.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F36cf42f9-8d29-4b3f-bc10-06ac9f8e97df.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=71108b21e360685a2a0483507c71e55d)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F36cf42f9-8d29-4b3f-bc10-06ac9f8e97df.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=71108b21e360685a2a0483507c71e55d)  
[![スクリーンショット 2026-04-22 20.14.17.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F3a243d2e-b09f-4b64-a98b-b7a3de1f28d3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=12480514e99aa545da80180af2211fd0)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F3a243d2e-b09f-4b64-a98b-b7a3de1f28d3.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=12480514e99aa545da80180af2211fd0)  
[![スクリーンショット 2026-04-23 0.52.22.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F3666f15f-a5fb-4272-b115-db39b9aff925.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7a9afe99d95d48acf48f6d50d71b44af)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F3666f15f-a5fb-4272-b115-db39b9aff925.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7a9afe99d95d48acf48f6d50d71b44af)  
[![スクリーンショット 2026-04-22 20.15.38.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F3a21beb8-5c4b-4470-950f-e93ae673451b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=736bcb850436683ef2fd5815cc3d4905)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F3a21beb8-5c4b-4470-950f-e93ae673451b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=736bcb850436683ef2fd5815cc3d4905)

### Step 2 — 会話で全体トーンを整える

初版の印象で気になる点を、**大きな粒度**の言葉で指示します。  
この段階はスライダーやコメントより先に、**全体の方向性** を一気に動かすのに向いています。

指示が反映されたら、右ペインがそのまま変わります。  
「整っているけど味気ない」と感じたら次のステップでスライダーへ。  
逆に「方向性はこれで OK、あとは細部」と感じたらコメントピンに進む、という分岐になるかと思います。

[![スクリーンショット 2026-04-23 0.58.53.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F8f73db68-d7ea-420e-89aa-4cc080e82dd5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d9d641b69d01062a031191263ddd7dad)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F8f73db68-d7ea-420e-89aa-4cc080e82dd5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d9d641b69d01062a031191263ddd7dad)  
[![スクリーンショット 2026-04-22 20.22.39.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F0e6300de-ac9e-4615-b1b3-a084e7cd2998.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6a095c78dd11e141a1a56bb2483c7b99)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F0e6300de-ac9e-4615-b1b3-a084e7cd2998.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=6a095c78dd11e141a1a56bb2483c7b99)

なんとなく、概要セクションの頭が上がったのかがわかりますかね。。。

### Step 3 — スライダーで色と余白などを微調整する

「この値を動かすとどう変わるか」を Claude が理解した上で、その場で動かせる軸を提案してくれるのがカスタムスライダーとのことのようです。

スライダーの良いところは、**数値で厳密に詰める前の「このくらいかな」という感覚探し** に向いていそうな点です。  
数字で指定する前に、目で見て納得できる値を探れるのは手戻りを減らしてくれそうです。

[![スクリーンショット 2026-04-22 20.31.28.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F405e3475-436d-48c1-9fda-76ff0d1b3ac0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=40f1cfac476cb2767aeeea39608c639a)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F405e3475-436d-48c1-9fda-76ff0d1b3ac0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=40f1cfac476cb2767aeeea39608c639a)

カラーが爽やかな緑になったのがわかりますかね。

### Step 4 — コメントで個別要素を直す

全体のトーンが整ったら、気になる**個別要素**としてピン留めでコメントを打ちます。  
**この部分だけ**のスコープで Claude に指示できるのが便利そうです。

会話モードだと「どの CTA ボタン？」と曖昧になりがちですが、コメントピンだと **場所の特定とセットで指示できる**のがありがたいところです。

[![スクリーンショット 2026-04-23 1.11.56.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F8c2baf66-87f6-4e01-a64f-6ba737ba8ac1.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=50a3969b0590b59e6701bbb6e431fb17)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F8c2baf66-87f6-4e01-a64f-6ba737ba8ac1.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=50a3969b0590b59e6701bbb6e431fb17)

### Step 5 — 直接編集でコピーを自分の言葉に書き換える

レイアウトと配色が固まったら、**テキストだけを自分の言葉で書き直す** フェーズです。  
Claude の生成は綺麗にまとまりがちですが、社内イベントの場合は **主催者の温度感**を入れたい箇所が出てきます。

テキストをクリックしてその場で書き換えるだけなので、**チャットに戻る手間がない** のが作業テンポ的に良さそうです。

[![スクリーンショット 2026-04-23 1.15.14.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F0b7839da-4e73-4069-ab34-74a5de5dca3a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=93792bca1743d362f737cdf66378bff7)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F0b7839da-4e73-4069-ab34-74a5de5dca3a.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=93792bca1743d362f737cdf66378bff7)

上記では「業務で使い倒そうぜ！！！！！」に編集してみました。

### Step 6 — エクスポートする

仕上がったらエクスポートです。ここでは単純に用途に応じて選択すればいいと思ます。

* **スタンドアロン HTML** として書き出し、社内 Wiki や静的ホスティングに貼る
* **組織内 URL** で共有し、共同主催者に見てもらう
* **PDF** にして Slack や Teams に流す
* **Canva** に送って、最後のロゴ挿入や印刷素材化を任せる

[![スクリーンショット 2026-04-23 1.16.57.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F681b72a1-220a-47ea-9755-1f4004f6013f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ba9a4695d23f7d92a16b9b1586d4471c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2F681b72a1-220a-47ea-9755-1f4004f6013f.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=ba9a4695d23f7d92a16b9b1586d4471c)

## おまけ — Claude Code へのハンドオフ

告知 LP 止まりではなく、そのまま **Next.js コンポーネントとしてリポジトリに組み込みたい** というシナリオも考えられます。その時に使えるのが Claude Code へのハンドオフです。

エクスポートからハンドオフを選択すると下記の図の通り、ハンドオフ時に **「Send to local coding agent」と「Send to Claude Code Web」** の2択が出ます。  
手元のリポジトリで動かしたいならローカル版、サクッと試すだけなら Web 版、と使い分けができるのかと思います。

[![スクリーンショット 2026-04-23 1.18.03.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2Ffbb6854f-94b0-4f51-b843-293857ac6cb8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=57fe55d1d48c5c738d95847ff4cc5d43)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F280929%2Ffbb6854f-94b0-4f51-b843-293857ac6cb8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=57fe55d1d48c5c738d95847ff4cc5d43)

## 良さそうに見える点

* **雑なプロンプトでも、それっぽい形がまず出てくる** ので、議論の叩き台を作るまでが早そう
* **スライダーで連続的に試せる** のは、数値を決める前の段階で相性が良さそう
* **コメントピン** で場所と指示をセットにできるので、会話だけでは曖昧になりがちな「この部分」が伝わりやすそう
* **Claude Code へのハンドオフ** で、実装フェーズへの繋ぎが一本化される

## 詰まりそうな点

* **本番コードそのまま投入は想定外** のようなので、ハンドオフ後のコードは当たり前ですがレビュー前提
* **リアルタイム共同編集は非対応**（複数人で同時に触るフェーズは Canva 等に流してから）
* **利用枠の消費が多め** との観察があり、長時間の反復作業はプラン選定時に意識しておく
* **ブランドガイドラインの厳密遵守には不向き** — 推論ベースで色や書体を当てるため

## 参考リンク
