---
id: "2026-06-09-madogiwacowork-httpstcoufcmwyuqey-01"
title: "@madogiwacowork: https://t.co/uFcMWyUqeY"
url: "https://x.com/madogiwacowork/status/2064297487196647754"
source: "x"
category: "cowork"
tags: ["Gemini", "GPT", "cowork", "x"]
date_published: "2026-06-09"
date_collected: "2026-06-10"
summary_by: "auto-x"
query: "Cowork スケジュール OR Cowork スキル作成 OR Cowork 自動化"
---

https://t.co/uFcMWyUqeY


--- Article ---
今日のWWDCでiPhoneのAIについて、3つの別々な話が同時に発表されました。

多くの記事が「SiriがGeminiになった」とだけ報じています。

それは全体の4分の1の話です。整理します。

Appleは今回のWWDCで、AIを外部モデル込みで使う前提に舵を切りました。この一言が今日の発表の本質です。

*※*この記事は*WWDC2026*の公開情報をもとに書いています。個人の考察を含みます（*2026*年*6*月*9*日時点）。

---

## **第1章：3つの話が混同されている**

まず背景として、今回のWWDCにはもうひとつの話がありました。

Tim CookがCEOとしてのラスト登壇でした。9月1日付けで、ハードウェアエンジニアリング担当SVPのJohn Ternusに交代することが発表されています。2024年のWWDCでApple Intelligenceを約束しながら、思うように動かせなかった2年越しのリベンジを見届けての退場でした。そのぶん今回の発表にかかっていたものは大きかったです。

本題に入ります。今日のWWDCのAI発表を整理すると、実は3つの別々な話が同時に起きています。

ひとつ目は「Siri AIの刷新」です。Siriがチャット型AIに生まれ変わり、個人のメモ・カレンダー・メッセージを横断して参照できるようになりました。ユーザーが直接触れるフロントの変化です。

ふたつ目は「AFM（Apple Foundation Models）の刷新」です。iPhoneの中で動くAIエンジンそのものが第3世代に更新されました。Geminiは主役ではなく、処理の一部を担う脇役です。

みっつ目は「Extensionsの新設」です。SiriからClaude・ChatGPT・Geminiを自分で選んで使える仕組みが整いました。今まで使えたClaudeやChatGPTのアプリとは、根本的に違うものです。

![](https://pbs.twimg.com/media/HKXGepLbcAANe2I.jpg)

この3つが同時に発表されたため、非常にややこしい話になっています。X上でも正確に理解に至っていない方が多そうです。私も今朝の時点では何が何だかわかっていませんでした。

本記事で整理します。

---

## **第2章：Siri AIの処理は4つの層に振り分けられる**

「SiriはGeminiで動く」という報道が多いですが、正確ではありません。

まず前提として、AFM（Apple Foundation Models）はAppleが独自開発した基盤AIモデルです。ChatGPTやGeminiと同種の、Apple版の大規模言語モデルと理解してください。

今日発表されたSiri AIの処理構造は、4つの層に振り分けられています。

①AFM Core（オンデバイス）

端末内で完結する処理です。タイマーのセット・音楽の再生・メッセージの送信など、軽いタスクはiPhone本体のAFMが処理します。インターネット接続も、Googleのサーバーも使いません。

②AFM Core Advanced（オンデバイス・一部端末のみ）

iPhone 17 Pro・iPhone 17 Pro Max・iPhone 17 Airの12GB RAM搭載端末でのみ動くオンデバイスモデルです。マルチモーダル処理など、より複雑なタスクをデバイス内で完結できます。iPhone 17標準モデル（8GB）は対象外です。

自分のiPhoneがどの層に対応するかは、以下を参考にしてください。

![](https://pbs.twimg.com/media/HKXGSzVbIAACbQa.jpg)

③Private Cloud Compute（Appleのクラウド）

中程度の複雑さのクエリはApple独自のサーバーで処理されます。この層では、AppleもGoogleも処理内容を個人と紐づけることができない設計です。

④Gemini 1.2T（Google Cloud）

一番重い推論タスクだけがGoogleのクラウドに送られます。NvidiaのB200 GPUで処理されます。これが年間10億ドル規模と報じられているGemini契約の実体です。

![](https://pbs.twimg.com/media/HKXGk9MbkAAkmY7.jpg)

AFMはGeminiの焼き直しではありません。AppleがGeminiを「先生モデル」として活用した蒸留によって精錬した、Apple独自のモデルです。WWDC後の質疑でApple幹部が明
