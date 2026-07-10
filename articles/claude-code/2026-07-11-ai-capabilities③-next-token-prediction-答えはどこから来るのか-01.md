---
id: "2026-07-11-ai-capabilities③-next-token-prediction-答えはどこから来るのか-01"
title: "AI Capabilities③ | Next Token Prediction: 答えはどこから来るのか"
url: "https://note.com/konitan_ai/n/nbb4661bfb66e"
source: "note"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "LLM", "note"]
date_published: "2026-07-11"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

> このレッスンを終えると、次の4つができるようになります。  
>   
> 1. Next Token Predictionが流暢さとhallucinationの\*\*共通の\*\*源である理由を説明できる  
> 2. タスクを「よく踏まれた道」と「前例の薄い領域」の連続体に位置づけられる  
> 3. 捏造が\*\*具体性\*\*に集中することを知り、検証の優先順位を付けられる  
> 4. この限界を押し広げる製品機能（出典・不確かさの表明など）を挙げられる  
>   
> 所要時間の目安は25分です。

## 検索エンジンではなく、高度な予測変換

生成AIの働きに、いちばん近い日常の道具は何か。検索エンジンではありません。**スマートフォンの予測変換**です。

生成AIは、答えを「どこかから探してくる」のではなく、**「何のあとに何が来がちか」にもとづいて、一語ずつ書いていきます**。この単一の性質から、高い流暢さと、hallucinationの両方が生まれます。前レッスンの「同じ仕組みの表と裏」の、最初の実例です。

## 100年前の数学で見る仕組み

原典コースには、この仕組みを**自分で作って**理解する体験教材があります。ブラウザ上で動かせる教材なので、原典を開ける場合は実際に触れてみると理解が進みます。ここではその内容を紙上で再現します。

**マルコフ連鎖**という、1906年発表の古い数学があります。やることは単純で、文章を読んで「**この単語のあとに、どの単語が何回来たか**」を数え、表にするだけです。

たとえば5通の社内チャットで訓練するとします。

* 「i think we should probably ship it」
* 「i think that sounds good」
* 「i think we should probably wait」…

すると表には「thinkのあとは we が2回、that が1回」のように記録されます。この表を確率に直せば、「i think」まで書いたときの**次の単語の確率分布**が得られます。分布から次の語を選ぶことを **sampling** と呼びます。選んで、また分布を引いて、また選ぶ。こうして文章が生成されていきます。

このn-gram方式は、2010年代のスマートフォンの予測変換（SwiftKeyやQuickType）で実際に使われていました。そして現在のLLMとの関係はこうなっています。

* **文脈の読み方** — マルコフ連鎖: 直前の1〜数語／LLM: **会話全体**
* **分布の計算** — マルコフ連鎖: 表を1行引くだけ／LLM: 数十億パラメータのニューラルネットを通す
* **次の語の選択** — マルコフ連鎖: 確率分布からsampling／LLM: **まったく同じ**（確率分布からsampling）

つまりLLMは、表引きを巨大な計算に置き換えて文脈を桁違いに広げたものですが、\*\*出口は同じ「次の語の確率分布」\*\*です。この一点をつかめば、以下の性質がすべて必然に見えてきます。

## 得意ゾーンと限界ゾーン

**得意ゾーン（よく踏まれた道）**: 要約、書式変換、よくある概念の説明、文章・議論・コードの自然な継続。モデルが何度も見た型に似た仕事では、滑らかで、速く、おおむね正確です。

**限界ゾーン（前例の薄い領域）**: 訓練データに例の少ない話題。そして何より、**「真実」と「真実っぽい」の区別が要る仕事**。予測変換は「もっともらしい続き」を書く機械であって、もっともらしい続きが常に真実とは限りません。

この仕組みから来る特徴的な失敗は4つです。

* **hallucination**: もっともらしい続きが、事実でない
* **confabulation（作話）**: 知識の穴を「穴がある」と言わずに、もっともらしい内容で埋める
* **非一貫性**: samplingは確率的なので、同じプロンプトでも実行のたびに答えが変わりうる
* **見かけの自信**: 滑らかな文章が、中身の推測を包んでしまう（前レッスンの自信と中身のズレと重なります）

## 実務の要点: 捏造が集中する「具体性」

このレッスンでいちばん実務に役立つ一文です。

**捏造は、具体的な情報に集中します。人名、日付、統計の数字、論文や記事の出典、URL、引用文。主張が精密であるほど、検証の価値が上がります。**

なぜか。「1980年代に多くの研究が行われた」のような曖昧な文は、まず外れません。「1983年の田中らの研究によれば…」のような精密な文は、**引用の形だけパターンで書けてしまう**ので、中身が捏造でも見た目は完璧になります。だから検証の優先順位は、曖昧な一般論ではなく**精密な固有情報**から付けます。

## 限界を押し広げる製品機能

この限界に対して、製品側の対策も進化しています。Claude 101・Claude Platform 101で学んだ機能が、この文脈で再登場します。

* **出典と接地（citations / source grounding）**: 生成でなく取得した情報に紐づける（Research、web search）
* **不確かさの表明**: モデル自身に怪しさを申告させる
* **制約された生成**: skillsや構造化出力で、捏造が入り込む余地を狭める
* **生成役と検証役の分離**: Claude Code 101の独立レビューの発想

機能は境界線を**外へ押す**だけで、消しはしません。座標を読む習慣はそのまま必要です。

## 演習: 検証テスト

30分の実習です。**自分がいちばん専門知識を持つ分野**で行います。捏造を自力で見抜ける分野でないと、このテストは成立しません。

1. 自分の分野の「検証可能な具体的事実」を5つ書き出す（人物の肩書、発表年、統計値、製品仕様、正確な引用など）
2. **得意ゾーンの体験**: その分野の有名な概念の説明・要約を頼む。流暢さを確かめ、内容を抜き取り検査する。これが「よく踏まれた道」の感触です
3. **具体性への圧力**: 「この分野の出典を3つ、著者名・発表年・URL付きで挙げて」のように、**精密な固有情報を要求**する。返ってきたものを全件検証し、5点満点で採点する。捏造があった場合、その**自信ありげな見た目**をよく観察する
4. **samplingの体験**: まったく同じ要求を新しい会話でもう一度実行し、2つの出力を比べる。何が同じで何が変わったか。その揺らぎがsamplingです
5. 発展: 出典機能のあるモード（Researchなど）で3を再実行し、点数の変化を見る
6. タスク一覧に注釈を足す。各タスクは得意ゾーン寄りか、具体性の検証が要るか

## まとめ

* 生成AIは検索でなく**高度な予測変換**。一語ずつ、「何のあとに何が来がちか」で書く
* マルコフ連鎖（1906年）と出口は同じ「次の語の確率分布からのsampling」。違いは文脈の広さと計算の深さ
* 得意はよく踏まれた道（要約・変換・定番の説明）。限界は前例の薄い領域と「真実 vs 真実っぽい」
* **捏造は具体性に集中する**。人名・日付・数字・出典・URLから検証する
* 出典・不確かさ表明・制約生成・検証役分離が境界を外に押すが、消しはしない

## 英語のまま覚える用語

* **Next Token Prediction** — 次のトークンの予測。生成の根本機構
* **sampling** — 確率分布から次の語を選ぶこと。揺らぎの源
* **hallucination / confabulation** — もっともらしい誤り／穴をもっともらしく埋める作話
* **source grounding** — 生成でなく取得した情報への接地
* **Markov chain** — 1906年の「次に来る語を数える」数学。仕組み理解の入口

## 確認クイズ

**Q1.** Why does the same mechanism produce both fluency and hallucination?

A) Two separate subsystems handle fluent text and factual claims.  
B) The model writes whatever continuation is most plausible given patterns — which yields smooth text, and also yields plausible-but-false content when the plausible continuation is not the true one.  
C) Hallucination only happens when servers are overloaded.  
D) Fluency is from pretraining and hallucination is from fine-tuning.

【日本語訳】なぜ同じ仕組みが、流暢さとhallucinationの両方を生むのですか。

A) 流暢な文章と事実の主張は、別々のサブシステムが担当しているから。  
B) モデルはパターンにもとづいて「もっともらしい続き」を書く。それが滑らかな文章を生むと同時に、もっともらしい続きが真実でないとき、もっともらしい誤りを生むから。  
C) hallucinationはサーバーが混んでいるときにだけ起きるから。  
D) 流暢さはpretraining由来で、hallucinationはfine-tuning由来だから。

**正解: B**  
「もっともらしさ」を最適化する機械は、もっともらしさと真実が一致する領域では十分に働き、乖離する領域では危うくなります。表と裏は同じコインです。だから対策は「hallucinationを消す設定を探す」ことではなく、乖離しやすい場所（具体性・前例の薄い領域）を知って検証を当てることになります。

**Q2.** You receive an AI-drafted report. Which element deserves verification first, according to this lesson?

A) The general introduction about industry trends.  
B) The three precise citations with author names, years, and URLs.  
C) The polite closing paragraph.  
D) The formatting of the headings.

【日本語訳】AIが下書きしたレポートを受け取りました。このレッスンによれば、最初に検証すべき要素はどれですか。

A) 業界動向についての一般的な導入部。  
B) 著者名・発表年・URL付きの、3件の精密な出典。  
C) 丁寧な締めの段落。  
D) 見出しの体裁。

**正解: B**  
捏造は具体性に集中します。出典は「引用の形」だけパターンで完璧に書けてしまうため、見た目の整いは中身の保証になりません。Aのような一般論はまず外れず、CとDに事実の主張はありません。限られた検証時間を精密な固有情報に集中させるのが、的を絞った検証です。

**Q3.** You run the exact same prompt twice in fresh conversations and get noticeably different outputs. What explains this?

A) The model learned from your first attempt.  
B) A bug in the application.  
C) Sampling — generation draws from a probability distribution, so identical prompts can yield different continuations.  
D) Your account was switched to a different model.

【日本語訳】まったく同じプロンプトを新しい会話で2回実行したところ、目に見えて違う出力が返ってきました。これを説明するのはどれですか。

A) モデルが1回目の実行から学習したから。  
B) アプリケーションのバグ。  
C) sampling。生成は確率分布から選ぶ処理なので、同一のプロンプトでも違う続きになりうる。  
D) アカウントが別のモデルに切り替えられたから。

**正解: C**  
揺らぎは仕様です。マルコフ連鎖の演習で「同じ表から違う文が生成できる」ことを見たのと同じ現象が、LLMでも起きています。Aは誤解で、会話をまたいだ学習は起きません（Claude Code 101・AI Fluencyで確認済みです）。実務への含意は2つあります。重要な出力は1回で確定させないこと、そして再実行は追加費用のかからない別案生成として使えること、です。

---

**次のレッスン**: Knowledge。「AIは何を知っているのか」を、訓練データとの関係で解剖します。意味の座標（embeddings）という仕組みも登場します。

このコースの全レッスンは AI Capabilities and Limitations（<https://note.com/konitan_ai/m/m1795df1750c5> ）に、ほかのコースはシリーズ目次（ <https://note.com/konitan_ai/n/nd267433454ab> ）にまとめています。

---

本シリーズはAnthropic非公式の独自教材です。2026年7月時点の公式コース構成に基づいています。

本コースはAnthropicのAI Capabilities and Limitations（リック・デイカン／ジョセフ・フェラー両教授のAI Fluency Frameworkを土台にAnthropicが制作、CC BY-NC-SA 4.0）に基づく独自解説です。

[#生成AI](https://note.com/hashtag/%E7%94%9F%E6%88%90AI) [#Claude](https://note.com/hashtag/Claude) [#ClaudeAI](https://note.com/hashtag/ClaudeAI) [#Anthropic](https://note.com/hashtag/Anthropic) [#AI活用](https://note.com/hashtag/AI%E6%B4%BB%E7%94%A8) [#AIリテラシー](https://note.com/hashtag/AI%E3%83%AA%E3%83%86%E3%83%A9%E3%82%B7%E3%83%BC) [#Claude検定対策](https://note.com/hashtag/Claude%E6%A4%9C%E5%AE%9A%E5%AF%BE%E7%AD%96) [#基礎から独学で身につけるAIの教科書](https://note.com/hashtag/%E5%9F%BA%E7%A4%8E%E3%81%8B%E3%82%89%E7%8B%AC%E5%AD%A6%E3%81%A7%E8%BA%AB%E3%81%AB%E3%81%A4%E3%81%91%E3%82%8BAI%E3%81%AE%E6%95%99%E7%A7%91%E6%9B%B8)
