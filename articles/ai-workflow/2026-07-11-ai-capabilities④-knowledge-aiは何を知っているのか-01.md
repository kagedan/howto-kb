---
id: "2026-07-11-ai-capabilities④-knowledge-aiは何を知っているのか-01"
title: "AI Capabilities④ | Knowledge: AIは何を知っているのか"
url: "https://note.com/konitan_ai/n/n7556f0d6d60f"
source: "note"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "note"]
date_published: "2026-07-11"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

> このレッスンを終えると、次の4つができるようになります。  
>   
> 1. 「知っているか」でなく「**訓練データにどれだけ豊富にあったか**」で問える  
> 2. 知識の特徴的な失敗4つ（staleness / ムラ / 偏り / source amnesia）を見分けられる  
> 3. embeddings（意味の座標）の直感を持てる  
> 4. web検索・RAG・tool useが「知識の穴のどれを塞ぐか」を説明できる  
>   
> 所要時間の目安は25分です。

## 問いの立て方の転換

モデルは、訓練中に読んだものを知っています。そして**それだけ**を知っています。初期状態ではリアルタイムの閲覧はなく、実体験もなく、**knowledge cutoff**で知識は凍結されています。

だから実務の問いはこう変わります。「AIはこれを知っているか」ではなく、\*\*「これは、モデルが読んだものの中に、どれだけ頻繁に・一貫して現れたか」\*\*という問いになります。

## 特徴的な失敗4つ

1. **staleness（鮮度切れ）**: 訓練時点の真実を、現在形で語る。「当時は正しかった」が今も正しいとは限らない
2. **coverageのムラ**: ニッチ分野・地域の事情は薄い。英語圏のメジャー知識は厚く、あなたの業界の暗黙知は薄い
3. **inherited bias（受け継いだ偏り）**: 訓練データの偏りが「普通」「典型」の判断に転写される。あなたの業界の「標準的な顧客」を、部外者のイメージで答えるかもしれない
4. **source amnesia（出典健忘）**: 「どこかで読んだ」が出典として示せない。知識はあるのに、その出どころを正確に言えない

3つ目と4つ目は見落とされがちです。とくにsource amnesiaは、前レッスンの「出典の捏造」と地続きです。出典を覚えていないのに出典の形を求められると、形だけ生成してしまうのです。

## 少し寄り道: embeddings（意味の座標）

原典コースはここで、体験教材を挟みます。**意味を「場所」として扱う**という発想です。

昔の検索は文字列の一致でした。「car」で検索すると「automobile」は見つからない。類義語辞書を人手で組んで補っていた時代が長くありました。

**embeddings** はこれを根本から変えました。文章を**座標**に変換するのです。単純化した例で説明します。すべての文書を「恐竜にどれだけ関係するか」「ジェットコースターにどれだけ関係するか」の2軸で採点して平面に置くと、**似た内容の文書は近くに集まります**。「恐竜テーマの遊園地のアトラクションは」という**質問も同じ平面に置けば**、いちばん近くにある文書が、いちばん関連の深い文書になります。これが意味検索（similarity search）の核心です。

実物は2軸ではなく**1,000次元前後**です。4次元以上は絵に描けませんが、数学は同じように動きます（距離の計算に項が増えるだけです）。そして、**各軸が何を意味するかは誰も決めていません**。訓練の過程で自然に立ち上がるもので（emergent）、847番目の軸が何の軸かは人間には読めません。似ているはずのものがなぜ近くに来たのかを、軸の名前で説明することはできないのです。

なぜこの寄り道をしたか。次の対策の話で登場する **RAG**（関連文書の検索・取得）の中身が、まさにこれだからです。

## 穴を塞ぐ道具たち

知識の限界は、道具で外へ押せます。それぞれ**どの穴を塞ぐか**で覚えます。

* **web検索**: **cutoffの穴**を塞ぐ。時事的な質問を現在の情報に接地させる
* **RAG / retrieval（MCP経由の資料参照を含む）**: **coverageの穴**を塞ぐ。訓練データに無かったあなたの資料（社内文書、マニュアル、過去案件）を、embeddingsの近さで検索して読ませる。Claude 101のProjectsのRAGモードの正体です
* **tool use**: **精度の穴**を塞ぐ。計算は計算機に、最新在庫はデータベースに聞かせる
* **cutoffの明示**: モデル自身が知識の締め切りを開示することで、**何を疑うべきか**をあなたに知らせる

## 演習: アウトサイダーテスト

30分の実習です。自分の専門分野で、モデルの知識の厚みと薄さを実測します。

1. 自分のタスク一覧のタスクをひとつ選び、それに関連して次を書き出す

   * **メジャーで安定した話題**を2つ（業界人なら誰でも知っている）
   * **ニッチ・ローカル・最近変わった話題**を2つ（業界用語、地域の規制、この1年の変化）
   * \*\*部外者がよく間違える「思い込み」\*\*を1つ（典型的な顧客像、実際に使われている道具、など）
2. **coverage探査**: メジャー1つとニッチ1つを質問し、深さと正確さを比べる。**両方が同じ自信の口調で返ってくるか**にも注目する（自信と中身のズレの復習です）
3. **staleness探査**: 自分の分野で最近変わったことを質問する。cutoffに言及するか。古い情報を現在形で語るか
4. **思い込み探査**: 自分の「思い込み」を直接は言わずに、それが露呈する質問をする（例: 「この業界の典型的な顧客像を描写して」）。部外者のイメージが出てくるか
5. タスク一覧に注釈を足す。各タスクについて「**モデルの知識に頼れる／自分が文脈を持ち込む必要がある**」のどちらかを記す
6. 発展: staleness探査をweb検索オンで再実行し、差を見る

## まとめ

* 問いは「知っているか」でなく「**訓練データにどれだけ豊富に・一貫してあったか**」
* 失敗4つは、**staleness**（鮮度切れ）／**coverageのムラ**／**inherited bias**（普通の判断の偏り）／**source amnesia**（出典健忘）
* **embeddings**は意味の座標。近さが関連を表す。RAGの中身
* 道具の対応は、web検索→cutoffの穴／RAG→coverageの穴／tool use→精度の穴。塞げるのは穴で、判断はあなたに残る

## 英語のまま覚える用語

* **knowledge cutoff** — 知識の凍結時点
* **staleness** — 訓練時の真実を現在形で語る鮮度切れ
* **inherited bias / source amnesia** — 受け継いだ偏り／出典健忘
* **embeddings** — 意味の座標。約1,000次元。軸の意味はemergent
* **similarity search / RAG** — 座標の近さによる検索／それを使った資料参照

## 確認クイズ

**Q1.** What is the practical question to ask about AI knowledge, instead of "does the AI know this?"

A) "Is the AI in a good mood today?"  
B) "How well-represented was this topic in what the model read during training — frequent, recent-in-training, and consistent?"  
C) "Which server is the AI running on?"  
D) "How long is my prompt?"

【日本語訳】AIの知識について、「AIはこれを知っているか」の代わりに立てるべき実務的な問いはどれですか。

A) 「今日のAIの機嫌は良いか」  
B) 「この話題は、モデルが訓練中に読んだものの中に、どれだけ豊富に（頻出・訓練期間内・一貫した記述で）存在したか」  
C) 「AIはどのサーバーで動いているか」  
D) 「私のプロンプトはどれくらいの長さか」

**正解: B**  
知識を「ある／ない」の二値でなく、訓練データでの厚みの問題として捉え直すのがこのレッスンの軸です。この問いが立てられると、「メジャーな話題は頼る、ニッチと最近と論争中は自分が文脈を持ち込む」という運用が自然に導かれます。

**Q2.** Your industry's regulation changed three months ago. Without tools, the AI describes the old rule as if it were current. Which failure is this, and which tool addresses it?

A) Source amnesia; fix with embeddings.  
B) Staleness; fix with web search to ground answers in current information.  
C) Inherited bias; fix with a longer prompt.  
D) Verbosity; fix with "answer in one sentence."

【日本語訳】あなたの業界の規制が3か月前に変わりました。道具なしのAIは、古い規則を現行のもののように説明します。これはどの失敗で、どの道具が対処になりますか。

A) source amnesia。embeddingsで直す。  
B) staleness。web検索で現在の情報に接地させて直す。  
C) inherited bias。プロンプトを長くして直す。  
D) verbosity。「一文で答えて」で直す。

**正解: B**  
cutoff後の変化を古いまま語るのはstalenessの典型で、塞ぐ道具はweb検索（またはRAGで最新資料を渡すこと）です。「失敗の種類→対応する道具」のペアで覚えるのがこのレッスンの型で、AとCは失敗と道具の組み合わせがどちらもずれています。

**Q3.** In the embeddings model, why can't anyone explain what dimension 847 means?

A) It is a trade secret protected by law.  
B) The dimensions' meanings are emergent from training rather than designed — they do not correspond to anything a human could name.  
C) Dimension 847 is reserved for system use.  
D) Because there are only 100 dimensions.

【日本語訳】embeddingsのモデルで、847番目の次元が何を意味するかを誰も説明できないのはなぜですか。

A) 法律で保護された企業秘密だから。  
B) 各次元の意味は設計されたものでなく、訓練から創発（emergent）したものだから。人間が名付けられる何かに対応していない。  
C) 847番は システム用に予約されているから。  
D) 次元は100個しかないから。

**正解: B**  
「恐竜軸」「コースター軸」のような人間の命名は、説明のための単純化です。実物の約1,000軸は訓練が自動的に見つけた方向であり、人間が解釈できるものではありません。これは意味検索が強力でありながら「なぜこれが近いのか」を説明しにくい理由でもあり、RAGの結果にもDiscernmentが要る、という実務上の含意につながります。

---

**次のレッスン**: Working Memory。4性質の中で唯一「崖」の性質です。人間の記憶力テストで「lost in the middle」を体感してから、context設計の実務に落とします。

このコースの全レッスンは AI Capabilities and Limitations（<https://note.com/konitan_ai/m/m1795df1750c5> ）に、ほかのコースはシリーズ目次（ <https://note.com/konitan_ai/n/nd267433454ab> ）にまとめています。

---

本シリーズはAnthropic非公式の独自教材です。2026年7月時点の公式コース構成に基づいています。

本コースはAnthropicのAI Capabilities and Limitations（リック・デイカン／ジョセフ・フェラー両教授のAI Fluency Frameworkを土台にAnthropicが制作、CC BY-NC-SA 4.0）に基づく独自解説です。

[#生成AI](https://note.com/hashtag/%E7%94%9F%E6%88%90AI) [#Claude](https://note.com/hashtag/Claude) [#ClaudeAI](https://note.com/hashtag/ClaudeAI) [#Anthropic](https://note.com/hashtag/Anthropic) [#AI活用](https://note.com/hashtag/AI%E6%B4%BB%E7%94%A8) [#AIリテラシー](https://note.com/hashtag/AI%E3%83%AA%E3%83%86%E3%83%A9%E3%82%B7%E3%83%BC) [#Claude検定対策](https://note.com/hashtag/Claude%E6%A4%9C%E5%AE%9A%E5%AF%BE%E7%AD%96) [#基礎から独学で身につけるAIの教科書](https://note.com/hashtag/%E5%9F%BA%E7%A4%8E%E3%81%8B%E3%82%89%E7%8B%AC%E5%AD%A6%E3%81%A7%E8%BA%AB%E3%81%AB%E3%81%A4%E3%81%91%E3%82%8BAI%E3%81%AE%E6%95%99%E7%A7%91%E6%9B%B8)
