---
id: "2026-07-11-ai-capabilities⑤-working-memoryいま何に注意を向けているのか-01"
title: "AI Capabilities⑤ | Working Memory:いま何に注意を向けているのか"
url: "https://note.com/konitan_ai/n/nb64b013394dd"
source: "note"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "LLM", "note"]
date_published: "2026-07-11"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

> このレッスンを終えると、次の4つができるようになります。  
>   
> 1. Working Memoryが、ほかの性質と違ってあるとき急に壊れる（cliff）理由を説明できる  
> 2. 長い入力では、真ん中に置いた情報が抜けやすいこと（lost in the middle）を、人間の記憶と対比して説明できる  
> 3. 渡す文脈しだいで結果が大きく変わることを踏まえ、大事な指示を先に置く・長い作業を分ける・要点を折り返し渡す、といった文脈の設計ができる  
> 4. 「文脈は多いほど良い」が誤りである理由を説明できる  
>   
> 所要時間の目安は25分です。

## 4つ目の問い: 「いま何に注意を向けているか」

AIがいま参照できるものは、**context window** という固定サイズの作業台に載っているものだけです。そこにあるものには注意を向けられ、ないものには向けられません。単純な話に聞こえますが、この性質には他の3つと決定的に違う点があります。

**この性質は cliff と呼ばれます。** ほかの性質はなだらかに悪くなります（ニッチになるほど知識が薄れる、など）。Working Memoryは違います。**上限までは普通に動き、超えた瞬間に急に壊れます**。坂道をだんだん下るのでなく、崖 （cliff）から落ちるように、という比喩です。超えたぶんは静かに切り捨てられ（silent truncation）、警告が出るとは限りません。

## 自分の記憶で見る serial position effect

原典コースの体験教材は、**受講者自身に15単語の記憶テストを受けさせます**。1.5秒ずつ表示される単語を覚えて、あとで書き出す。すると、ほぼ全員が同じパターンを示します。**最初のほうと最後のほうは思い出せて、真ん中が消える**というパターンです。

これは **serial position effect**（系列位置効果）という、100年以上研究されてきた人間の記憶の性質です。最初の項目は反復の機会があり（primacy）、最後の項目はまだ新しい（recency）。真ん中はどちらの恩恵もありません。

そして、**LLMも同じU字カーブを描きます**。2023年のスタンフォード大学の研究で、長いcontextの中の位置を変えながら重要な事実を置いてテストしたところ、**先頭と末尾では正答率が高く、中間に埋めると30%以上落ちました**。これが **lost in the middle**（真ん中の取りこぼし）です。quirk（偶然の癖）ではなく、transformerの注意の構造が窓の両端を重く扱うことから来る、**構造的な性質**です。

## 実務への翻訳: 置き場所の設計

20ページの文書を貼って、11ページ目の内容を尋ねると、1ページ目や20ページ目の内容より取りこぼされやすくなります。ここから実務の型が導かれます。

**危険な形**: 重要な指示が、長い履歴や資料の**中間に埋まっている**。

**安全な形**: **重要な指示は最初に述べ、末尾で繰り返す**。絶対に守らせたい制約は、システムプロンプトの早い位置に置き、入力の終わり近くでもう一度言う。間のすべてに均等な注意が払われると期待しない。

Claude Code [101のCLAUDE.md](http://xn--101CLAUDE-2f4h.md)（毎セッション、文脈の先頭側に入る）や、Claude Platform 101のcontext管理が、この構造の上に設計されていたことが見えてきます。

## 「多いほど良い」の誤り

素朴な直感は「全部貼れば間違いない」です。この直感は手放す必要があります。

**足したcontextの1つ1つが、他の何かを「注意の届かない場所」へ押し込みます。** 全文書を貼る行為は、重要な1段落を、無関係な19ページで**薄める**行為でもあるのです。context engineering（文脈の設計）の核心は、何を入れるかだけでなく、**どこに置き、何を入れないか**にあります。

原典の要約を引いておきます。**「More context ≠ better results. Curate ruthlessly, place strategically, and repeat what matters.」**（多い文脈＝良い結果、ではない。容赦なく選び、戦略的に置き、大事なことは繰り返す。）

あわせて、忘れがちな2つの事実も再確認します。

## 限界を押し広げる道具（再整理）

この性質の対策は、これまでのレッスンでほぼ出そろっています。役割を再整理します。

* **memory /** [**CLAUDE.md**](http://CLAUDE.md) **/ Projects**: セッションを越える継続の穴を埋める
* **compaction（/compact、context\_management）**: 長い会話を要約して上限から遠ざける
* **Skills**: 必要になるまで読み込まない省スペース設計
* **大きいwindow**: 上限を遠くへ動かす（消しはしない）
* **subagents**: 探索の記憶を別の作業台に隔離する

## 演習: ビフォーアフター実験

30分の実習です。

1. **cold start vs 文脈供給**: タスク一覧から「自分だけが持つ文脈（スタイルガイド、過去の良い実例、固有の制約）が効くタスク」を選ぶ。まず文脈ゼロの素の依頼で実行し、保存。次に新しい会話で、文脈を前置きして同じ依頼を実行。2つを「良い出力の定義」に照らして採点し、**差の大きさ**を測る。文脈がどれだけ結果を左右するかを、数字で見る実験です
2. **lost in the middleの再現**: 数段落の資料を用意し、重要な指示を1つ**真ん中に埋めて**、その指示に依存する質問をする。捕まえたか。次に同じ指示を**先頭に移して**再実行し、差を観察する
3. **白紙の確認**: 短い会話でAIに自分の仕事の事情をひとつ教える（または誤りを訂正する）。会話を閉じ、新しい会話でそれを前提にした質問をする。ゼロから始まることを自分の目で確認する
4. タスク一覧に注釈。各タスクは「**常設の文脈（Project・保存済み指示・参照資料）を組んでから回すべき**」か「**その場の供給で足りる**」か

## まとめ

* Working Memoryは**あるとき急に壊れる（cliff）**。silent truncationで、警告なく壊れる
* 人間もLLMも**真ん中を取りこぼす**（serial position effect / lost in the middle。中間で正答率30%以上低下）
* 型は、**重要な指示は先頭に、末尾で繰り返す。中間を信用しない**
* 「多いほど良い」は誤り。足すたびに何かが注意の届かない場所へ押される。**容赦なく選び、戦略的に置き、大事なことは繰り返す**
* セッション間の記憶はゼロが初期値。訂正はモデルでなくcontextを変えるだけ

## 英語のまま覚える用語

* **cliff** — なだらかに悪くなるのでなく、あるとき急に壊れる性質（崖から落ちるイメージ）
* **silent truncation** — 警告なしの切り捨て
* **serial position effect** — 人間の系列位置効果（最初と最後が残る）
* **lost in the middle** — LLMの中間取りこぼし。構造的な性質
* **context engineering** — 何を・どこに置き・何を省くかの設計

## 確認クイズ

**Q1.** Why is Working Memory described as a "cliff" while the other properties are gradients?

A) Because it is the least important property.  
B) Because things work until the window is exceeded, and then fail via silent truncation — often without warning — rather than degrading gradually.  
C) Because it only affects mobile devices.  
D) Because it improves suddenly with each new model.

【日本語訳】他の性質が「勾配」なのに、Working Memoryだけ「崖」と呼ばれるのはなぜですか。

A) もっとも重要度の低い性質だから。  
B) windowを超えるまでは動き、超えた瞬間にsilent truncation（警告なき切り捨て）で壊れるから。徐々に劣化するのではない。  
C) モバイル端末にしか影響しないから。  
D) 新しいモデルが出るたびに突然改善するから。

**正解: B**  
「昨日まで動いていた自動処理が、資料が1件増えた今日から黙って壊れる」。これが cliff の難しさで、エラーが出ない失敗はデバッグも遅れます。だから設計段階で上限から距離を取る（分割・要約・選別）ことに価値があるのです。

**Q2.** A Stanford study found that a key fact placed in the middle of a long context was recalled over 30% less accurately than at the edges. What practical rule follows?

A) Put critical instructions at the beginning and repeat them near the end.  
B) Always put critical instructions exactly in the middle.  
C) Make all documents longer so the middle grows.  
D) Avoid instructions entirely.

【日本語訳】スタンフォードの研究で、長いcontextの中間に置かれた重要な事実は、両端に置いた場合より正答率が30%以上低いことが示されました。ここから導かれる実務の型はどれですか。

A) 重要な指示は最初に置き、末尾近くでも繰り返す。  
B) 重要な指示は必ずちょうど真ん中に置く。  
C) すべての文書を長くして、真ん中を育てる。  
D) 指示を書くこと自体を避ける。

**正解: A**  
注意が厚い両端に大事なものを置き、薄い中間には頼らない。人間の記憶テストで自分が体験したのと同じU字を、配置の設計に使うわけです。BとCは研究結果の正反対の適用で、Dは適切ではありません。

**Q3.** "Just paste in everything — more context means better answers." What is wrong with this instinct?

A) Nothing; more context is always better.  
B) Every added piece pushes other pieces toward the attention dead zone — so the goal is curating and placing context, not maximizing it.  
C) Pasting is slower than typing.  
D) Long contexts are cheaper, so quality drops.

【日本語訳】「全部貼ってしまえ。文脈は多いほど答えが良くなる」。この直感の何が間違っていますか。

A) 何も間違っていない。文脈は常に多いほど良い。  
B) 足した1つ1つが、他の何かを注意の死角へ押し込む。だから目標は文脈の最大化でなく、選別と配置である。  
C) 貼り付けは入力より遅いから。  
D) 長い文脈は安いので品質が下がるから。

**正解: B**  
「容赦なく選び、戦略的に置き、大事なことは繰り返す」が結論です。Claude Code 101の「曖昧な指示は探索を増やして高くつく」、Claude Platform 101の「正しいものを入れる」と、三たび同じ思想に到達しました。道具は変わっても、context engineeringの核心は一貫しています。

---

**次のレッスン**: Steerability。「自分はどこまで制御できているのか」。指示が文字通り守られて意図が外れる letter over spirit など、制御の隙間で起きる失敗を扱います。

このコースの全レッスンは AI Capabilities and Limitations（<https://note.com/konitan_ai/m/m1795df1750c5> ）に、ほかのコースはシリーズ目次（ <https://note.com/konitan_ai/n/nd267433454ab> ）にまとめています。

---

本シリーズはAnthropic非公式の独自教材です。2026年7月時点の公式コース構成に基づいています。

本コースはAnthropicのAI Capabilities and Limitations（リック・デイカン／ジョセフ・フェラー両教授のAI Fluency Frameworkを土台にAnthropicが制作、CC BY-NC-SA 4.0）に基づく独自解説です。

[#生成AI](https://note.com/hashtag/%E7%94%9F%E6%88%90AI) [#Claude](https://note.com/hashtag/Claude) [#ClaudeAI](https://note.com/hashtag/ClaudeAI) [#Anthropic](https://note.com/hashtag/Anthropic) [#AI活用](https://note.com/hashtag/AI%E6%B4%BB%E7%94%A8) [#AIリテラシー](https://note.com/hashtag/AI%E3%83%AA%E3%83%86%E3%83%A9%E3%82%B7%E3%83%BC) [#Claude検定対策](https://note.com/hashtag/Claude%E6%A4%9C%E5%AE%9A%E5%AF%BE%E7%AD%96) [#基礎から独学で身につけるAIの教科書](https://note.com/hashtag/%E5%9F%BA%E7%A4%8E%E3%81%8B%E3%82%89%E7%8B%AC%E5%AD%A6%E3%81%A7%E8%BA%AB%E3%81%AB%E3%81%A4%E3%81%91%E3%82%8BAI%E3%81%AE%E6%95%99%E7%A7%91%E6%9B%B8)
