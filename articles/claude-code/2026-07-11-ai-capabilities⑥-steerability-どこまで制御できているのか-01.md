---
id: "2026-07-11-ai-capabilities⑥-steerability-どこまで制御できているのか-01"
title: "AI Capabilities⑥ | Steerability: どこまで制御できているのか"
url: "https://note.com/konitan_ai/n/nf6a9e9aae0b5"
source: "note"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "LLM", "note"]
date_published: "2026-07-11"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

> このレッスンを終えると、次の4つができるようになります。  
>   
> 1. steerability（操縦性）がなぜ効き、なぜ限界を持つのかを説明できる  
> 2. 制御が効く場面（短い・具体的・検証可能）と緩む場面（長い連鎖・抽象・生の精度）を見分けられる  
> 3. reasoning drift と letter over spirit という2つの失敗を診断できる  
> 4. 「指示を強く繰り返す」でなく「目的を言い直す」対処を使える  
>   
> 所要時間の目安は20分です。

## 操縦できる理由と、残る「隙間」

最後の性質です。モデルはあなたの指示によく従います。表で出すよう頼めば表で出し、100語以内と言えば短くまとめ、ペルソナを与えれば保ち続けます。

ただし、従い方の仕組みを知っておく必要があります。**モデルは指示にも「パターンの続き」として従います**。理解して従うのではなく、指示付きの文脈のもっともらしい続きを生成しているのです。だからこそよく操縦でき、だからこそ**あなたの言葉と意図の間には常に隙間**があります。特徴的な失敗のほとんどは、この隙間で起きます。

## 代表的な2つの失敗

### 1. reasoning drift（推論のズレが積み重なる）

多段の依存関係がある仕事で、**序盤の小さな誤りが、連鎖の果てに大きくなる**現象です。ステップ2の軽い取り違えが、ステップ5では結論を狂わせている。1つ1つのステップの精度が高くても、掛け算で劣化します。

対処は\*\*checkpoint（途中確認）\*\*です。「ステップ2の結果を見せてから先へ進んで」。連鎖を短い区間に切れば、ズレは早い段階で捕まります。Claude Code 101のplan mode承認、AI Fluencyの「手順に分割」と同じ思想です。

### 2. letter over spirit（文字どおりで、意図を外す）

**指示は文字通り満たされたのに、意図は外れている**失敗です。構成に問題があるメールに「短くして」と頼むと、律儀に語数だけ削られて、問題の構成はそのまま残る。「もっとプロフェッショナルに」と頼むと、敬語は増えたが、肝心の依頼は埋まったまま残ります。

ここで、このレッスンでいちばん大事な対処を示します。

**文字通りで役に立たない結果が返ってきたときは、同じ指示を強く繰り返しても隙間は埋まりません。目的を言い直すのが有効です。**

「短くして」→「短くして。**狙いは、役員が2ページ目の要点まで集中を切らさず読めること**」。指示（形式）に目的（意図）を添えると、モデルは「何のための短縮か」に沿って判断できるようになります。隙間は言葉を強くしても埋まらず、意図を明示して初めて埋まります。

なお、この「文脈内の指示に従う」性質には安全上の裏面もあります。**prompt injection**（文書の中に紛れ込ませた指示にまで従ってしまう）という問題で、外部から来た文書をAIに処理させるときの重要な注意点です。

## 限界を押し広げる道具

* **system prompt / カスタム指示**: 会話が伸びても薄まらない常設の指示置き場
* **code execution**: 数値と論理の精度は、本物の実行環境に外注する（Claude Platform 101）。「LLMに暗算させない」
* **思考の可視化（extended thinkingなど）**: ズレをステップ2の時点で見つける
* **構造化出力**: 出力の形を機械的に縛り、letter-over-spirit的な迷走の余地を減らす

## 演習: 目的の書き直し実験

30分の実習です。タスク一覧から、**複数ステップまたは特定の形式が要るタスク**を選びます。

1. まず、そのタスクの**目的**を1文で書く。「〜という形式で」ではなく「何を達成したいか」。（「3行の箇条書き」は形式です。「チームにこの日程が現実的だと納得してもらう」が目的です）
2. **tight control探査**: 短く具体的で検証可能な指示を出す（「3列の表で」「ちょうど5項目」）。守られたか確認する。これが得意ゾーンの感触です
3. **drift探査**: 4〜5ステップの依存関係がある形で依頼し、出力をステップごとに検品する。序盤の小さなズレが後段に波及していないか。次に「ステップ2まで出して、私の確認を待って」と checkpoint を入れて再実行し、比べる
4. **letter vs spirit探査**: 文字通りには満たせるが意図を外しうる指示をわざと出す（構成に難のある文章への「短くして」など）。結果を見る。次に**目的を添えて**再依頼し、違いを見る
5. タスク一覧の総仕上げ注釈: 多段のタスクには「checkpointをどこに入れるか」、形式だけ指定していたタスクには「添えるべき目的文」を書き込む

## まとめ

* モデルは指示に「パターンの続き」として従う。だから操縦できるし、言葉と意図の隙間が残る
* 得意は短い・具体的・検証可能。限界は長い連鎖・抽象・生の精度
* 代表的な2つの失敗は、**reasoning drift**（序盤の小さな誤りが連鎖で拡大→checkpointで区切る）と **letter over spirit**（文字どおりで意図を外す→**指示でなく目的を言い直す**）
* 精度は道具に外注する。計算はcode execution、形は構造化出力、常設の指示はsystem promptへ
* 外部文書を扱うときは prompt injection に注意する

## 英語のまま覚える用語

* **steerability** — 操縦性。指示にどれだけ従うか、という性質
* **reasoning drift** — 多段の推論で、序盤の誤りが連鎖して大きくなること
* **letter over spirit** — 文字通りに守って意図を外す失敗
* **checkpoint** — 連鎖を区切る途中確認
* **prompt injection** — 文書内に仕込まれた指示に従ってしまう問題

## 確認クイズ

**Q1.** You ask for a 5-step analysis. Step 2 contains a small misreading, and by step 5 the conclusion is far off. Which failure is this, and what is the recommended countermeasure?

A) Letter over spirit; restate the goal.  
B) Reasoning drift; insert a checkpoint — have the model stop and show intermediate results before continuing.  
C) Staleness; enable web search.  
D) Sycophancy; remove your opinion from the prompt.

【日本語訳】5段階の分析を頼んだところ、ステップ2に小さな読み違いがあり、ステップ5では結論が大きく外れていました。これはどの失敗で、推奨される対策はどれですか。

A) letter over spirit。目的を言い直す。  
B) reasoning drift。checkpointを入れる。途中結果を見せて止まらせ、確認してから先へ進ませる。  
C) staleness。web検索を有効にする。  
D) sycophancy。プロンプトから自分の意見を外す。

**正解: B**  
小さな誤りの連鎖的増幅はdriftの定義そのものです。対策は連鎖を短く切ること。5段を一気に走らせず、2段目で一度着地させます。Claude Code 101のplan mode承認やAI Fluencyの「手順に分割」と同じ設計思想が、ここでは失敗モードの言葉で正当化されました。

**Q2.** You tell the AI to "make this email more professional." It adds formal language, but the buried request stays buried, and the email still fails. What does this lesson recommend next?

A) Repeat "MORE PROFESSIONAL" in capital letters.  
B) Restate with the goal explicit: "Make it more professional — my goal is that the recipient sees the request within the first three lines and acts on it."  
C) Give up on AI for email tasks.  
D) Make the email longer to include everything.

【日本語訳】「このメールをもっとプロフェッショナルに」と頼んだところ、丁寧な言い回しは増えたものの、埋もれていた依頼事項は埋もれたままで、メールとしては相変わらず機能しません。このレッスンが勧める次の一手はどれですか。

A) 「もっとプロフェッショナルに」を大文字で繰り返す。  
B) 目的を明示して言い直す。「もっとプロフェッショナルに。狙いは、受け取った人が最初の3行で依頼に気づいて動けることです」。  
C) メール作業へのAI利用を諦める。  
D) すべてを盛り込めるようメールを長くする。

**正解: B**  
letter over spiritの処方箋は「強く繰り返す」ではなく「目的を添える」です。「プロフェッショナルに」は形式の言葉で、達成したいことを含んでいません。目的が入った時点で、モデルの判断基準が変わります。Aは同じ隙間に同じ言葉を強くぶつけるだけで、隙間は埋まりません。

**Q3.** Which task sits deepest in Steerability's limitation zone, requiring you to offload rather than instruct harder?

A) "Format the answer as a two-column table."  
B) "Respond in exactly 100 words."  
C) "Compute the compounded totals across these 40 rows precisely" — native numerical precision, best offloaded to code execution.  
D) "Use a formal tone throughout."

【日本語訳】Steerabilityの限界ゾーンのもっとも深いところにあり、「指示を強める」のでなく「外注する」べきタスクはどれですか。

A) 「答えを2列の表の形式にして」。  
B) 「ちょうど100語で答えて」。  
C) 「この40行の複利合計を正確に計算して」。生の数値精度が要る仕事で、code executionに外注するのが最善。  
D) 「全体をフォーマルな口調で」。

**正解: C**  
A・B・Dは短く具体的で検証可能、つまり得意ゾーンの指示です。Cだけは性質が違います。数値の厳密さはパターンの再現では保証できず、どれだけ丁寧に指示しても「LLMの暗算」の域を出ません。本物の計算機に処理を移します。Claude Platform 101のcode executionが、この性質の観点から再び正当化されました。

---

**次のレッスン**: When Properties Collide。4つの性質が出そろったので、実際の失敗を「どの2つの衝突か」で診断する技術に進みます。このコースの実務面での到達点です。

このコースの全レッスンは AI Capabilities and Limitations（<https://note.com/konitan_ai/m/m1795df1750c5> ）に、ほかのコースはシリーズ目次（ <https://note.com/konitan_ai/n/nd267433454ab> ）にまとめています。

---

本シリーズはAnthropic非公式の独自教材です。2026年7月時点の公式コース構成に基づいています。

本コースはAnthropicのAI Capabilities and Limitations（リック・デイカン／ジョセフ・フェラー両教授のAI Fluency Frameworkを土台にAnthropicが制作、CC BY-NC-SA 4.0）に基づく独自解説です。

[#生成AI](https://note.com/hashtag/%E7%94%9F%E6%88%90AI) [#Claude](https://note.com/hashtag/Claude) [#ClaudeAI](https://note.com/hashtag/ClaudeAI) [#Anthropic](https://note.com/hashtag/Anthropic) [#AI活用](https://note.com/hashtag/AI%E6%B4%BB%E7%94%A8) [#AIリテラシー](https://note.com/hashtag/AI%E3%83%AA%E3%83%86%E3%83%A9%E3%82%B7%E3%83%BC) [#Claude検定対策](https://note.com/hashtag/Claude%E6%A4%9C%E5%AE%9A%E5%AF%BE%E7%AD%96) [#基礎から独学で身につけるAIの教科書](https://note.com/hashtag/%E5%9F%BA%E7%A4%8E%E3%81%8B%E3%82%89%E7%8B%AC%E5%AD%A6%E3%81%A7%E8%BA%AB%E3%81%AB%E3%81%A4%E3%81%91%E3%82%8BAI%E3%81%AE%E6%95%99%E7%A7%91%E6%9B%B8)
