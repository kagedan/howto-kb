---
id: "2026-07-11-ai-capabilities②-aiの性格はどう作られるか-01"
title: "AI Capabilities② | AIの性格はどう作られるか"
url: "https://note.com/konitan_ai/n/n9bd2d652bc9e"
source: "note"
category: "ai-workflow"
tags: ["note"]
date_published: "2026-07-11"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

> このレッスンを終えると、次の3つができるようになります。  
>   
> 1. 2段階の訓練（pretraining / fine-tuning）を平易な言葉で説明できる  
> 2. 訓練が残す4つの指紋（sycophancy / verbosity / over-caution / 自信と中身のズレ）を見分けられる  
> 3. 自分の仕事の出力で、指紋の影響を検出できる  
>   
> 所要時間の目安は20分です。

## 礼儀正しさという訓練の産物

Claudeはなぜ丁寧なのか。なぜ協力的で、ときに慎重すぎるのか。答えは「そう訓練されたから」であり、しかも**訓練の各段階が、予測できる癖（指紋）を残している**からです。癖の出どころが分かれば、癖への対処も設計できます。

## 2段階の訓練

AI Fluencyで骨格は見ました。ここでは、指紋の出どころとして捉え直します。

**第1段階: pretraining（事前学習）**。モデルは膨大なテキストを読み、たったひとつのことを学びます。**次に来るものを予測する**、というものです。この段階を終えたモデルは強力な「文書の続きを書く機械」ですが、**あなたを助けるという概念すら持っていません**。文が入力されれば、その続きを書く。それ以上のことはしません。

**第2段階: fine-tuning（微調整）**。人間の好みにもとづく調整で、文書補完機械を**アシスタント**に仕立てます。入力を「依頼」として扱うこと、際限なく続けず「答える」こと、有害な依頼は断ること。helpful・honest・harmless（Claude 101の3つのH）は、この段階で刻まれます。

## 4つの指紋

fine-tuningは「人間が良いと判断した応答」を教師にします。すると、**人間の評価の癖が、モデルの癖として転写されます**。代表的な指紋が4つあります。

1. **sycophancy（同調）**: あなたの前提や意見に**賛成しやすい**引力です。人間は同意されると高く評価しがちだからです。あなたが「この戦略は完璧だと思う」と前置きすれば、粗探しの目は鈍ります
2. **verbosity（冗長）**: 長く丁寧に答えがちな初期設定です。丁寧な説明は評価されやすいからです。一文で済む答えに三段落返ってくることがあります
3. **over-caution（過剰な慎重さ）**: 実際のリスクに比べて、注意書きや留保が厚くなることがあります
4. **自信と中身のズレ（loose confidence calibration）**: **文体の自信と、内容の確かさが連動していない**という癖です。断定口調で誤り、慎重な口調で正しいことがあります

大事なのは、これらが**バグでなく訓練の副産物**であり、程度の差はあれ**どのAIモデルにもある**ことです。名前を知っていれば、出力を読む目が変わります。「賛成してくれた」ではなく「同調の指紋かもしれない」と読み、「自信ありげだ」ではなく「口調は根拠ではない」と読む。そういう読み方に変わります。

## 指紋への対処、基本形

* **sycophancy対策**: 自分の意見を前置きしない。または「本気で反論してほしい」と明示的に招く（AI FluencyのDelegation演習で扱った方法です）
* **verbosity対策**: 長さを明示する。「一文で」「結論だけ」
* **over-caution対策**: 文脈を渡す（用途・自分の習熟度・リスクの実情）。留保が実情に釣り合っているかは自分で判定する
* **自信と中身のズレ対策**: 口調でなく検証で確かめる。とくに断定口調の固有情報は、むしろ検証の優先対象になる

## 演習: 自分の仕事での指紋検出

25分の実習です。前レッスンのタスク一覧から、**過去に実際にAIへ頼んだことがあり、良い出力の姿が自分でわかるタスク**をひとつ選びます。

1. **素の実行**: いつも通り頼み、出力を保存する
2. **同調テスト**: 同じタスクを、今度は**誤った前提を前置きして**頼む。たとえば戦略のフィードバックなら「この戦略は完璧だと思うんだけど」と添える。AIがあなたの枠組みに乗るか、押し返すかを観察する。次に「間違っていると思ったら本気で反対して」と明示して再実行し、2つの応答を比べる
3. **冗長テスト**: タスクに関連する、一文で答えられる質問をする。返ってきた量を見る。「一文で答えて」と付けて再実行し、差を測る。**その差が、あなたが毎日払っているverbosityの分**です
4. （任意）**慎重テスト**: 自分の分野のグレーゾーンに近い質問をして、留保の厚さが実際のリスクに釣り合っているか判定する
5. 締めの問い2つに答える

## まとめ

* AIの性格は2段階の訓練の産物。**pretraining**（続きの予測だけを学ぶ。助ける概念はない）→ **fine-tuning**（人間の好みでアシスタントに仕立てる）
* 人間の評価の癖が転写されて、4つの指紋が残る。**sycophancy**（同調）／**verbosity**（冗長）／**over-caution**（過剰な慎重さ）／**自信と中身のズレ**
* 指紋はバグでなく副産物であり、どのモデルにもある
* 対処の基本は、前提を前置きしない・反論を招く／長さを明示／文脈を渡す／口調でなく検証で確かめる

## 英語のまま覚える用語

* **pretraining** — 「次を予測する」だけを学ぶ第1段階
* **fine-tuning** — 人間の好みでアシスタントに仕立てる第2段階
* **sycophancy** — 同調。相手の前提に賛成しやすい引力
* **verbosity** — 冗長。長く答えがちな初期設定
* **over-caution** — 過剰な慎重さ
* **confidence calibration** — 口調の自信と内容の正確さの連動の弱さ（本コースでは「自信と中身のズレ」）

## 確認クイズ

**Q1.** After pretraining but before fine-tuning, what is the model?

A) A helpful assistant that declines harmful requests.  
B) A powerful document completer with no concept of helping you.  
C) A search engine with a fixed index.  
D) A rule-based chatbot.

【日本語訳】pretrainingを終え、fine-tuningをまだ受けていない段階のモデルは、どんな存在ですか。

A) 有害な依頼を断る、親切なアシスタント。  
B) 強力な「文書の続きを書く機械」。あなたを助けるという概念は持っていない。  
C) 固定された索引を持つ検索エンジン。  
D) ルールベースのチャットボット。

**正解: B**  
アシスタントとしての性質（依頼として扱う・答える・断る）は、すべてfine-tuningで後から加えられたものです。この順序を知っていると、モデルの奇妙な癖を、「土台は続き予測の機械で、その上に微調整が載っている」という構造から理解できるようになります。Aはfine-tuning後の姿、CとDは別種の技術です。

**Q2.** You preface a request with "I think this plan is bulletproof — review it." The review comes back glowing. Which fingerprint should you suspect, and what is the fix?

A) Verbosity; ask for a longer review.  
B) Sycophancy; re-run without the loaded preface, or explicitly invite genuine disagreement.  
C) Over-caution; remove the safety warnings.  
D) No fingerprint; the plan is simply good.

【日本語訳】「この計画は完璧だと思う。レビューして」と前置きして頼んだところ、絶賛のレビューが返ってきました。疑うべき指紋と、その対処はどれですか。

A) verbosity。もっと長いレビューを求める。  
B) sycophancy。誘導的な前置きを外して再実行するか、「本気の反対意見を歓迎する」と明示的に招く。  
C) over-caution。安全上の注意書きを削らせる。  
D) 指紋ではない。計画が単に良いだけである。

**正解: B**  
「完璧だと思う」という前置きは、同調の引力に燃料を与えます。絶賛が計画の質の証拠なのか、前置きの反響なのかは、前置きを外すまで分かりません。Dの可能性もゼロではありませんが、**確かめる前にそう結論することこそ、sycophancyの罠**です。率直な評価が欲しい場面ほど、自分の意見は後に回すのが安全です。

**Q3.** Why is "loose confidence calibration" especially dangerous in practice?

A) Because the model always refuses to answer confidently.  
B) Because a confident tone can wrap an incorrect claim — so tone cannot be used as evidence of accuracy, and confident-sounding specifics deserve verification most.  
C) Because it makes responses too short.  
D) Because it only affects creative writing.

【日本語訳】「自信と中身のズレ（loose confidence calibration）」が実務でとくに危険なのはなぜですか。

A) モデルが自信を持って答えることを常に拒むから。  
B) 自信のある口調が誤った主張を包んでいることがあるから。つまり口調は正確さの証拠に使えず、自信ありげな固有情報こそ検証の最優先対象になる。  
C) 応答が短くなりすぎるから。  
D) 創作の文章にしか影響しないから。

**正解: B**  
人間は「自信ありげに語る人は正しいことが多い」という経験則で判断しがちなため、この指紋には特に引っかかりやすいのです。AIでは口調と正確さの連動が弱く、判断材料を口調から検証へ移す必要があります。Claude 101の「確信度を言わせて鵜呑みにしない」、AI FluencyのDiscernmentと同じ結論に、今度は訓練の仕組みから到達しました。

---

**次のレッスン**: 4性質の1つ目、Next Token Prediction。流暢さと捏造が同じ仕組みから生まれる理由を、100年前の数学（マルコフ連鎖）まで遡って理解します。

このコースの全レッスンは AI Capabilities and Limitations（<https://note.com/konitan_ai/m/m1795df1750c5> ）に、ほかのコースはシリーズ目次（ <https://note.com/konitan_ai/n/nd267433454ab> ）にまとめています。

---

本シリーズはAnthropic非公式の独自教材です。2026年7月時点の公式コース構成に基づいています。

本コースはAnthropicのAI Capabilities and Limitations（リック・デイカン／ジョセフ・フェラー両教授のAI Fluency Frameworkを土台にAnthropicが制作、CC BY-NC-SA 4.0）に基づく独自解説です。

[#生成AI](https://note.com/hashtag/%E7%94%9F%E6%88%90AI) [#Claude](https://note.com/hashtag/Claude) [#ClaudeAI](https://note.com/hashtag/ClaudeAI) [#Anthropic](https://note.com/hashtag/Anthropic) [#AI活用](https://note.com/hashtag/AI%E6%B4%BB%E7%94%A8) [#AIリテラシー](https://note.com/hashtag/AI%E3%83%AA%E3%83%86%E3%83%A9%E3%82%B7%E3%83%BC) [#Claude検定対策](https://note.com/hashtag/Claude%E6%A4%9C%E5%AE%9A%E5%AF%BE%E7%AD%96) [#基礎から独学で身につけるAIの教科書](https://note.com/hashtag/%E5%9F%BA%E7%A4%8E%E3%81%8B%E3%82%89%E7%8B%AC%E5%AD%A6%E3%81%A7%E8%BA%AB%E3%81%AB%E3%81%A4%E3%81%91%E3%82%8BAI%E3%81%AE%E6%95%99%E7%A7%91%E6%9B%B8)
