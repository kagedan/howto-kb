---
id: "2026-07-11-ai-capabilities①-生成aiとは何か-01"
title: "AI Capabilities① | 「生成AI」とは何か"
url: "https://note.com/konitan_ai/n/n6271c313e51e"
source: "note"
category: "ai-workflow"
tags: ["LLM", "note"]
date_published: "2026-07-11"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

> このレッスンを終えると、次の3つができるようになります。  
>   
> 1. 生成AIと、日常で出会う分類・予測型AIを区別できる  
> 2. 「AIの性質は連続体である」という、このコースの中心思想を説明できる  
> 3. これから深掘りする4つの性質を、問いの形で言える  
>   
> 所要時間の目安は15分です。

## このコースの狙い: どこまで信じてよいか

AI Fluencyが人間側の技量を扱うのに対して、このコースが扱うのは機械側の仕組みです。両者は対になっていて、原典コースも互いを参照し合っています。

なぜ仕組みまで踏み込むのか。AIへの態度は、そのままにしておくと両極に振れやすいからです。「なんでもできる」と過信するか、「一度間違えたから信用しない」と全否定するか。どちらも仕事の役には立ちません。このコースが目指すのは **calibrated trust** です。任せてよい場所と検証すべき場所を、根拠を持って見分けられる状態を指します。

## まず線引き: 生成AIと分類・予測型AI

「AI」という言葉は広すぎます。最初に整理しておきます。

スパムフィルタ、動画のおすすめ、クレジットカードの不正検知、写真の顔認識。こうした機能はすべてAIですが、**生成AIではありません**。既存のデータを**分類・順位づけ・予測**するAIです。

このコースが扱うのは、**新しいコンテンツをトークン単位で生成する、transformerベースのテキストモデル**です。つまりClaudeのようなLLMです。分類AIの信頼性の議論と生成AIの信頼性の議論は別物なので、この線引きを最初に引いておきます。

## 中心思想: 性質の連続体

このコースでいちばん大事な考え方を、先に述べておきます。

**生成AIは、一様に有能なのでも、一様に当てにならないのでもありません。4つの性質のそれぞれについて、「得意ゾーン」から「限界ゾーン」への連続体の上にいます。**

同じ道具が、あるタスクでは十分に頼れて、別のタスクでは危ういことがあります。それは、タスクが連続体の**どこに座るか**が違うからです。だから calibrated trust とは、「信じる／信じない」の二択ではなく、**タスクの座標を読んで、検証の強度をそこに合わせる**技術になります。座標が右（限界側）に寄るほど、検証と補いを厚くします。

## 4つの性質、問いの形で

これから4つのレッスンで深掘りする性質を、それぞれ**問いの形**で示します。問いの形にしておくと、実務でそのまま使えます。

1. **Next Token Prediction**: その答えは**どこから来る**のか
2. **Knowledge**: AIは実際のところ**何を知っている**のか
3. **Working Memory**: AIは**いま何に注意を向けている**のか
4. **Steerability**: 自分は**どこまで制御できている**のか

それぞれの性質に、得意ゾーン（例: 要約や書式変換はNext Token Predictionの得意側）と限界ゾーン（例: 前例のない話題、cutoff後の知識、超長文の中間、長い推論の連鎖）があります。そして、**同じ仕組みが得意と限界の両方を生んでいます**。この「同じ仕組みの表と裏」という見方は、このコースを通じて繰り返し登場します。

## 演習

15分の準備実習です。このコースは、この実習で作る「タスク一覧」を軸に進みます（AI Fluencyの「自分のプロジェクト」方式と同じ設計です）。

1. **今週AIに触れた場面を5つ**書き出してください。幅広く挙げます。予測変換、写真の自動タグ、スパムフィルタ、チャットの回答、翻訳、商品のおすすめ、音声アシスタントなど
2. それぞれに「**生成か、分類か**」の判定を付けます。新しいコンテンツを作っているのか、既存のものを仕分け・順位づけしているのか
3. 判定に迷ったものをClaudeに見せて確認します。「間違っていたものについて、区別を1文で説明して」と頼みます
4. 次に、**自分がAIにやらせたい（またはやらせている）タスクを5〜10個**書き出し、それぞれに「いちばん関係しそうな問い」のタグを付けます

   * 答えの出どころが心配 → Next Token Prediction
   * 知っているかが心配 → Knowledge
   * ちゃんと読んでくれるかが心配 → Working Memory
   * 指示通りやってくれるかが心配 → Steerability
5. このタグは予想で構いません。**当たっているかどうかを、この先4つのレッスンで検証していきます**。一覧は保存しておきます

## まとめ

* このコースの目標は **calibrated trust**。信じる／信じないの二択でなく、タスクの座標に検証の強度を合わせる
* 世の中のAIの大半（フィルタ・おすすめ・不正検知）は分類・予測型。このコースの対象は**新しいコンテンツを生成する**transformerベースのモデル
* 中心思想は、性質が**連続体**であること。同じ仕組みが得意と限界の両方を生む
* 4つの性質を問いで覚える。どこから来るのか（NTP）／何を知っているのか（Knowledge）／何に注意しているのか（Working Memory）／どこまで制御できているのか（Steerability）

## 英語のまま覚える用語

* **calibrated trust** — 信頼を相手の確かさに合わせて調整すること。calibrate（較正）＝計器の目盛りを合わせる意味。検証の強度をタスクの座標に合わせる
* **generative AI** — 新しいコンテンツを生成するAI（分類・予測型と区別）
* **Next Token Prediction / Knowledge / Working Memory / Steerability** — このコースの4つの性質
* **continuum** — 連続体。得意ゾーンから限界ゾーンへの座標軸

## 確認クイズ

**Q1.** Which of the following is generative AI, as defined in this chapter?

A) A spam filter that sorts incoming email.  
B) A fraud-detection system that flags suspicious transactions.  
C) A text model that drafts a new product announcement one token at a time.  
D) A recommendation engine that ranks videos you might like.

【日本語訳】この章の定義で、生成AIに当たるのはどれですか。

A) 受信メールを仕分けするスパムフィルタ。  
B) 不審な取引に印を付ける不正検知システム。  
C) 新しい製品発表文をトークン単位で書き起こすテキストモデル。  
D) 好みそうな動画を順位づけするレコメンドエンジン。

**正解: C**  
分かれ目は、「新しいコンテンツを**作っている**か、既存のものを**仕分け・順位づけ**しているか」です。A・B・Dはすべて後者で、優秀なAIですが生成AIではありません。この線引きができると、「AIは信用できるか」という漠然とした問いが、「どの種類のAIの、どの性質の話か」という答えられる問いに変わります。

**Q2.** What does "calibrated trust" mean in this chapter?

A) Trusting AI completely once it passes an initial test.  
B) Never trusting AI outputs for important work.  
C) Locating each task on the capability-limitation continuum and matching your verification effort to where it sits.  
D) Trusting only the most expensive models.

【日本語訳】この章での「calibrated trust（どこまで信じてよいか）」の意味はどれですか。

A) 最初のテストに合格したら、以後AIを完全に信頼すること。  
B) 重要な仕事ではAIの出力を決して信頼しないこと。  
C) タスクを得意〜限界の連続体の上に位置づけ、その座標に検証の労力を合わせること。  
D) もっとも高価なモデルだけを信頼すること。

**正解: C**  
信頼を全体に与えたり取り上げたりするのではなく、**タスク単位で座標を読む**のが calibrated trust です。AとBは二択思考の両極で、どちらも座標を読んでいません。Dはモデルの階級と信頼性を混同しています。Claude 101のevals、AI FluencyのDiscernmentが、この見極めの実技だったことにも気づけると理解が深まります。

**Q3.** "The same mechanism gives you both the capability and the limitation." What does this recurring idea prepare you to expect?

A) That capabilities and limitations come from unrelated parts of the system.  
B) That fixing a limitation always removes a capability.  
C) That, for example, the process that makes AI fluent is the same one that makes it hallucinate — so you manage the trade-off rather than eliminate it.  
D) That limitations disappear in newer models.

【日本語訳】「同じ仕組みが得意と限界の両方を生む」。この繰り返し登場する考え方は、何を予期させるものですか。

A) 能力と限界はシステムの無関係な部分から来ている、ということ。  
B) 限界をひとつ直すと、能力が必ずひとつ失われる、ということ。  
C) たとえばAIを流暢にしている仕組みそのものがhallucinationも生んでいる、ということ。だから限界は消すのでなく、トレードオフとして管理する。  
D) 新しいモデルでは限界が消える、ということ。

**正解: C**  
次のレッスン以降の予告になっている考え方です。流暢さと捏造は、同じ「次を予測する」仕組みの表と裏です。だから「捏造だけを完全に消す」ことはできず、座標を読んで検証を当てる管理が正解になります。Dについては、性質の**線は動く**が、「線がある」こと自体は当分変わらない、というのがこのコースの立場です。

---

**次のレッスン**: AIの性格はどう作られたか。2段階の訓練が残す4つの「指紋」（同調・冗長・過剰な慎重さ・自信と中身のズレ）を学びます。

このコースの全レッスンは AI Capabilities and Limitations（<https://note.com/konitan_ai/m/m1795df1750c5> ）に、ほかのコースはシリーズ目次（ <https://note.com/konitan_ai/n/nd267433454ab> ）にまとめています。

---

本シリーズはAnthropic非公式の独自教材です。2026年7月時点の公式コース構成に基づいています。

本コースはAnthropicのAI Capabilities and Limitations（リック・デイカン／ジョセフ・フェラー両教授のAI Fluency Frameworkを土台にAnthropicが制作、CC BY-NC-SA 4.0）に基づく独自解説です。

[#生成AI](https://note.com/hashtag/%E7%94%9F%E6%88%90AI) [#Claude](https://note.com/hashtag/Claude) [#ClaudeAI](https://note.com/hashtag/ClaudeAI) [#Anthropic](https://note.com/hashtag/Anthropic) [#AI活用](https://note.com/hashtag/AI%E6%B4%BB%E7%94%A8) [#AIリテラシー](https://note.com/hashtag/AI%E3%83%AA%E3%83%86%E3%83%A9%E3%82%B7%E3%83%BC) [#Claude検定対策](https://note.com/hashtag/Claude%E6%A4%9C%E5%AE%9A%E5%AF%BE%E7%AD%96) [#基礎から独学で身につけるAIの教科書](https://note.com/hashtag/%E5%9F%BA%E7%A4%8E%E3%81%8B%E3%82%89%E7%8B%AC%E5%AD%A6%E3%81%A7%E8%BA%AB%E3%81%AB%E3%81%A4%E3%81%91%E3%82%8BAI%E3%81%AE%E6%95%99%E7%A7%91%E6%9B%B8)
