---
id: "2026-05-04-google-cloud-next-26-体験記-3-anthropic-のセッションで聞いたソフト-01"
title: "[Google Cloud Next '26 体験記 #3] Anthropic のセッションで聞いた「ソフトウェアの先」のビジョン"
url: "https://qiita.com/koichim33/items/03748c6017fa578cec0f"
source: "qiita"
category: "cowork"
tags: ["API", "AI-agent", "LLM", "qiita"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

ラスベガスで開催された Google Cloud Next '26 の体験ブログ、第 3 弾です。

これまでの記事はこちら 👇
- 第 1 弾：[[Google Cloud Next '26 体験記 #1] Agentic Hack Zone でエージェント開発を体験してきた](https://qiita.com/koichim33/items/0e2883d847fd3abd3f11)
- 第 2 弾：[[Google Cloud Next '26 体験記 #2] EXPO で体験した 3 つのユニークなブース](https://qiita.com/koichim33/items/e1d1cd8eabcb3a84c381)

![IMG_1599のコピー.jpeg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1602803/f26c0483-c940-46f0-96e4-7ca5e2af32e9.jpeg)

第 1 弾・第 2 弾では EXPO 会場での体験を紹介してきましたが、今回は趣を変えて、**Next '26 で参加したセッション** の中から、特に印象に残った **Anthropic のセッション** をご紹介したいと思います。

---

## 参加したセッションの概要

私が聴講したのは **Spotlights** カテゴリのセッションです。

- **タイトル**：After software: Anthropic's vision for the next era of enterprise AI
  （ソフトウェアの先へ：エンタープライズ AI の次なる時代に向けた Anthropic のビジョン）
- **登壇者**：Eric Burns（Anthropic）
- **セッション ID**：SPTL021

### Spotlights とは？

Next の Session type の定義によると、Spotlights は以下のようなセッションです。

> Take part in these dedicated keynote-style sessions featuring live demos, new tech, and customer success stories, delivered by Google leaders and partners.

つまり、**ライブデモ・最新技術・顧客事例** を盛り込んだ、キーノートスタイルの特別セッション、というポジションになります。

セッション動画は Google Cloud Next のページから視聴することができます。

### セッションの趣旨

YouTube 動画の説明欄からの引用ですが、発表の趣旨は以下の通りでした。

> エンタープライズソフトウェアは、今後 2 年間で過去 20 年間よりも大きく変化するでしょう。モデルは逆転しつつあります。組織が構築するものを定義し、優先順位付けするトップダウン型の計画は、AI エージェントがチームが問題を発見次第迅速に解決するボトムアップ型の実行へと移行しています。Anthropic は、最先端の動向についてご紹介します。チームは既に Vertex AI 上で、自律的に定義、構築、反復を行うエージェントを導入しています。私たちは、このビジョンを実際の事例と実践的なフレームワークに基づいて具体的に説明します。

なかなかエッジの効いたメッセージと思います。ここからは、セッション中で印象に残ったポイントをいくつか取り上げていきます。

---

## 印象に残ったポイント

### Anthropic のコーディング市場でのプレゼンス

まず目を奪われたのは、**Anthropic は 2025 年のコーディング市場シェアの 54％** を占めているという数字でした。「開発者から支持を得ている」というなんとなくの感覚が、数字で裏付けられていることを感じました。

さらに、仕事における AI 活用の進化として、こんなキーワードが提示されていました。

- **2023 年：Chat**
- **2025 年：Code**
- **2026 年：Cowork**

そして、これからの世界観を象徴するのが **"No terminal"** というフレーズでした。Claude の恩恵がエンジニアだけにとどまらず、**非エンジニアの領域** にも広がっていく可能性を感じました。

### Claude の進化を 1 本の動画で

Claude の進化については、セッション中にこちらの YouTube 動画が流されました。

🎥 https://www.youtube.com/watch?v=PnX30ZXxKco

これは、**歴代の Claude モデルに「claude.ai をクローンしてみせよ」という同じ課題を与え、その結果を比較する** という内容の動画です。短い動画の中に Claude モデルの進化が詰まっていて、世代を経るごとに成果物のクオリティが上がっていく様子がわかりやすかったです。

---

## "The Intelligence Explosion" (AI の成長曲線)

次に紹介されたのが **"The Intelligence Explosion"** というセクションです。

ここでは "**The artificial intelligence exponential**（AI の指数関数的成長）" というタイトルで、年代ごとの象徴的な各社のプロダクト（LLM のモデル）を題材に、AI の成長について語られていました。

AI の成長カーブの捉え方には、

- **The Pure Exponential**（純粋な指数関数的成長）

という見方がある一方で、

- **The Sigmoid**（S 字曲線）
- **The Hard Ceiling**（明確な天井）

として捉える懐疑論もある、という整理が紹介されていました。今後 AI がどの曲線を描いていくのか、考えさせられる内容でした。

---

## "The Dawn of Agents" (Agent とは何か)

続く **"The Dawn of Agents"** のセクションでは、いよいよ Agent についての議論に入ります。

ここで紹介された Agent の定義が個人的にとても印象的でした。

> **Agent は、Large Language Model が loop の中で tools を使って goal を目指すもの**

シンプルですが、Agent の本質を端的に表していて、頭の中の整理にとても役立つ表現だと感じました。

---

## "The Solutions Machine" (Agent による問題解決の事例)

次の **"The Solutions Machine"** セクションでは、Agent の具体的な活用事例が紹介されました。

### 事例 1：複数 Agent による C コンパイラの並列構築

複数の Agent を並列に走らせて C コンパイラを構築するという事例。詳細はこちらの記事で読めます。

🔗 https://www.anthropic.com/engineering/building-c-compiler

### 事例 2：3 つの役割の AI Agent による段階的開発

役割を分けた 3 つの AI Agent が連携して、段階的にソフトウェアを開発していく事例。こちらも詳細を記事で読むことができます。

🔗 https://www.anthropic.com/engineering/harness-design-long-running-apps

### Solutions Machine のメンタルモデル

特に印象的だったのが、Solutions Machine のメンタルモデルの解説です。

> **Problems** と **Capital** を投入すると、**Work** と **Test** を繰り返し、**Self-improving solution** を生み出す

問題と資本さえ投じれば、Agent たちが自律的に試行錯誤しながら解を磨き続ける——という未来像が、はっきりとしました。

---

## "The Great Inversion" (価値の重心が反転する)

次は **"The Great Inversion"** のセクションです。

従来の問題解決は、

- **"Identify, define, and scope the problem; Decide to solve it"** に比べて、
- **"Implement, validate, deploy, and maintain the solution"** に高いコストがかかっていました。

しかし、**10x Scale** の新しいピラミッドでは、この **コスト構造が逆転** している、という指摘です。

伝統的な SI（システムインテグレーション）を得意としている企業に所属している身としては、少し耳の痛い話でもありました。**実装・デプロイ・運用といった工程の重みが軽くなる** 一方で、**「何を解くか」** を見極める力の重要性が増していく——状況の変化に合わせて、自分たちも変わっていく必要があると改めて学ばされました。

---

## "The Three Doors" (これからの 3 つの活用機会)

セッション後半の **"The Three Doors"** では、**"Three compounding opportunities"** として、これから AI を活用していくうえでの 3 つの方向性が提示されました。

1. **Empower every employee**（すべての従業員を強化する）
2. **Supercharge software development**（ソフトウェア開発を加速する）
3. **Create revenue streams**（新たな収益源を生み出す）

エンジニアリングの効率化だけでなく、**全社員のエンパワーメント** や **新たなビジネス価値の創出** までを射程に入れているのが印象的でした。今後の AI 活用の方向性を考える時の参考にしたいと思います。

というわけで、学びの多い、密度の濃いセッションでした。

---

## 番外編：EXPO の Anthropic ブースで聞いた "Introducing Cowork"

ところで、話は EXPO に戻ります。

**Anthropic は EXPO にもブースを出展** しており、ブース内でも独自のセッションが多数開催されていました。私もその中の 1 つに参加してきたので、こちらも簡単に紹介します。

参加したのは **"Introducing Cowork"** というタイトルのセッションです。内容は、 **Claude Cowork がどのように動くのか** の解説と **Cowork で Word・Excel・PowerPoint の資料を作成する** ライブデモ、というものでした。実際に資料が組み上がっていく様子がとても刺激的で、冒頭で紹介された「2026 年は Cowork」というキーワードを、まさに体現しているようなデモでした。

Anthropic ブースでは他にも様々なセッションが実施されており、立ち見が出るほど多くの方が聴講されていました。来場者の Anthropic への注目度の高さを肌で感じることができました。

---

## まとめ

今回ご紹介した Anthropic のセッションは、

- **これからの 2 年で起きる劇的な変化**
- **Agent の本質と "Solutions Machine" の考え方**
- **価値の重心が反転する "The Great Inversion"**
- **"The Three Doors" による具体的な活用機会**

と、非常に密度の濃い内容でした。「ソフトウェアの先」がどんな姿になるのか、自分の仕事のあり方を見直すきっかけにもなる、学びの多いセッションだったと思います。

セッション動画も公開されていますので、興味のある方はぜひ視聴してみてください。

#4に続きます。
