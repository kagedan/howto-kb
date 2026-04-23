---
id: "2026-03-20-無料公式ドキュメントをそっ閉じした人向けにclaude資格学習サイト作ったai認定試験claude-01"
title: "【無料】公式ドキュメントをそっ閉じした人向けにClaude資格学習サイト作った。AI認定試験「Claude Certified Architect（CCA）」に合格できる学習サイト"
url: "https://qiita.com/tak_yokoi/items/846527c69156ff8b0d06"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "AI-agent", "qiita"]
date_published: "2026-03-20"
date_collected: "2026-03-20"
summary_by: "auto-rss"
---

「Claude Certified Architect（CCA）」って知っていますか？

2026年3月にAnthropicがリリースした、初のAI公式技術資格です。

取得すれば「AIを使った仕組みを設計できる人」であることを公式に証明できる。履歴書に書ける。市場価値が上がる。

「おっ、これは取りたい」

そう思って公式の学習コンテンツを開いたんです。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F508305%2Fa1589114-50ba-4ac0-8501-38de5ec8adf0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d0e6fc5fa1789e5ef110ae3e4ed03090)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F508305%2Fa1589114-50ba-4ac0-8501-38de5ec8adf0.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=d0e6fc5fa1789e5ef110ae3e4ed03090)  
……英語でした。

しかもただの英語じゃない。「Agentic Loop」「MCP Protocol」「Hub-and-Spoke Architecture」——エンジニア向けの専門用語だらけ。

翻訳ボタンを押しても「エージェント的ループ」「ハブアンドスポーク構造」。

......こんなもの、わかるかい。

そっ閉じしました。

でも、資格は取りたい。

この矛盾を解決するために、日本語のCCA学習サイト「Claude Dojo」を作りました。

↓Claude Dojo（今なら無料）↓

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F508305%2F8ad96a57-fba8-44e8-bdec-0df88bb15e1d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7d7fb4e7fba2adf17690fa28675da6ad)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F508305%2F8ad96a57-fba8-44e8-bdec-0df88bb15e1d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7d7fb4e7fba2adf17690fa28675da6ad)

## 開発した背景

「AIを使える」と「AIで仕組みを設計できる」は違う

ChatGPTやClaudeを日常的に使っている人は増えています。でも、ほとんどの人は、AIに質問するところどまり。

一方で、企業が本当に求めているのは、AIを業務に安全に組み込む仕組みを設計できる人。

CCA資格は、まさにその設計力を証明する資格です。

### 問題：わかりやすく学ぶ手段がない

Anthropicは6本の公式コースを無料で公開しています。でも——

・全部英語  
・エンジニア向けの専門用語が前提  
・翻訳しても「MCPプロトコルのプリミティブが〜」で意味不明

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F508305%2Fa5b3618b-691b-4780-a5fa-30d7416670e5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=44d80c6dd4ff9c5a2e2038aa7b70e78e)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F508305%2Fa5b3618b-691b-4780-a5fa-30d7416670e5.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=44d80c6dd4ff9c5a2e2038aa7b70e78e)  
うーん、わからねぇ…

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F508305%2F305eabd7-eef7-4596-a139-2123284328f9.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f34be6d59f9207f5abf98b1905015773)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F508305%2F305eabd7-eef7-4596-a139-2123284328f9.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f34be6d59f9207f5abf98b1905015773)  
いやいや、翻訳ONにしてもさっぱりわからんぞ…

非エンジニアのビジネスパーソンがこれで勉強するのは、正直無理じゃないかな、と。

### だから作った

「**非エンジニアでも、日本語だけで、CCA試験の内容を理解できるサイト**」

これがClaude Dojoのコンセプトです。

## サービス概要

Claude Dojo（クロード・ドウジョウ）

・料金： 無料✨

・構成：

✅全7フェーズ・20レッスン

✅CCA模擬テスト20問（解説＋該当レッスンへのリンク付き）

✅進捗管理（ダッシュボード + フェーズ別進捗 + 完了チェック）

✅レスポンシブ対応（PC・スマホ）

## サービスの特徴

### 特徴1. 難しい言葉はその場で噛み砕く

公式コンテンツとの最大の違いはここ。

例えば「エージェントループ」。

#### 公式の説明：

The agentic loop is a pattern where the model iterates through tool use and response generation until a stop condition is met.（公式HP）

#### Claude Dojoの説明：

エージェントループ......って何？要するに「考える → やる → 確認 → 次どうする？」の繰り返し。あなたがお客様の問い合わせに対応するときと同じ。メールを読む → 顧客DBを調べる → 結果を確認 → 返信を書く。AIもこれと同じことをやっている。（Claude Dojo）

全ての専門用語を、出てきたその瞬間に、身近な例で説明します。

### 特徴2. 非エンジニアの目線で全文リライト

ペルソナは「35歳の営業マネージャー。プログラミング経験ゼロ。Claude Proは使い始めたばかり」。

この人が初見で理解できるかどうかを基準に、全レッスンのコンテンツを検証・リライトしました。

・APIは「レストランの注文窓口」

・MCPは「スマホにアプリを追加する仕組み」

・Hooksは「オフィスの自動ゲート」

・Hub-and-Spokeは「ハブ空港からの各方面便」

### 特徴3. 模擬テストで理解度をチェック

全20問の模擬テスト。不正解の場合は——

・なぜその答えが正解なのかを解説

・該当レッスンへのリンクで即復習

間違えた問題からレッスンに飛んで復習 → もう一度解く。このサイクルが一番効率的な学習法です。

### 特徴4. 進捗が見える

ダッシュボードで全体進捗とフェーズ別進捗を一覧表示。

フェーズを完了するとチェックマークがつく。全レッスン完了でお祝いメッセージ。

**ワクワクするサービス**というところは大事にしました。

地味だけど、「あと3レッスンで完了」が見えるとモチベーションが全然違いますよね。

## 実際の画面（一部抜粋）

ダッシュボード  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F508305%2F07762d4f-355c-493f-96f0-1384ef2901fb.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=81a0a7dd787ada4c046df4d474ceb6d9)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F508305%2F07762d4f-355c-493f-96f0-1384ef2901fb.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=81a0a7dd787ada4c046df4d474ceb6d9)

レクチャーの1ページ  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F508305%2F0e5c89aa-700c-43f5-8554-bcd7207f7bc8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=46ec1889a45961f930b00ec3ed5312c9)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F508305%2F0e5c89aa-700c-43f5-8554-bcd7207f7bc8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=46ec1889a45961f930b00ec3ed5312c9)

## 今後の予定（できるといいな）

・コンテンツの継続的なアップデート（CCA試験の出題傾向に合わせて）

・模擬テストの問題数拡充

・動画学習コンテンツの作成

・学習コミュニティの立ち上げ

## 最後に

「AIの資格なんて、エンジニアのものでしょ？」

そう思っている人にこそ使ってほしいです。

CCA試験はコードを書く試験ではありません。「AIをどう設計するか？」という判断力の試験です。

営業でも、マーケターでも、人事でも。AIを「なんとなく使ってる」から「設計できる」にステップアップしたい人へ。

↓無料でスタート↓

実際に触ってみて、感想やフィードバックがあれば、ぜひ [@tak\_yokoi](/tak_yokoi "tak_yokoi") までお願いします！
