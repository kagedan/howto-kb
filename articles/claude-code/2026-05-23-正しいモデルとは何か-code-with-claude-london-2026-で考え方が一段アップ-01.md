---
id: "2026-05-23-正しいモデルとは何か-code-with-claude-london-2026-で考え方が一段アップ-01"
title: "「正しいモデル」とは何か — Code with Claude London 2026 で考え方が一段アップデートされた話"
url: "https://zenn.dev/noah33/articles/picking-the-right-model"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-23"
date_collected: "2026-05-24"
summary_by: "auto-rss"
query: ""
---

![Picking the right model — Lucas Smedley, Member of Technical Staff, Anthropic](https://static.zenn.studio/user-upload/deployed-images/d6d6c86d0067c882ddc60ce2.png?sha=7eec4577149568f55f95ba41ce92f3d49de81e31)

## はじめに

最近、先日ロンドンで開催された「Code with Claude London 2026」のセッションを毎日少しずつ見ています。

AI Solutions Architect として活動している自分にとって、Anthropic公式の登壇は一次情報の宝庫で、見るたびに「明日からこう動こう」と思える発見があります。SNSのホットテイクや断片的なベンチマーク記事と違って、現場でClaudeを実際に動かしている人たちが、何を考え、何を測って、どう判断しているのかが、密度高く語られているからです。

その中で、今日は特に印象に残った一本を取り上げたいと思います。**Anthropic, Member of Technical Staff の Lucas Smedley さんによる「Picking the right model」** というセッションです。

<https://www.youtube.com/watch?v=P0uMXS6emHA>

「新しいモデルが出るたびに、結局どれを使えばいいのか」――AIを業務で扱うエンジニアなら、一度は必ずぶつかる悩みだと思います。Lucasさんはそこに、感覚論ではなく**再現可能なプロセス**で答えを出していました。本記事では、このセッションを視聴して自分が学んだこと、AI Solutions Architectとして現場に持ち帰りたいと感じたことを整理してみます。

---

## 目次

1. [なぜ「モデル選定」はこんなに難しいのか](#1-%E3%81%AA%E3%81%9C%E3%83%A2%E3%83%87%E3%83%AB%E9%81%B8%E5%AE%9A%E3%81%AF%E3%81%93%E3%82%93%E3%81%AA%E3%81%AB%E9%9B%A3%E3%81%97%E3%81%84%E3%81%AE%E3%81%8B)
2. [モデル選定を支える3つの柱](#2-%E3%83%A2%E3%83%87%E3%83%AB%E9%81%B8%E5%AE%9A%E3%82%92%E6%94%AF%E3%81%88%E3%82%8B3%E3%81%A4%E3%81%AE%E6%9F%B1)
3. [公開ベンチマークは「方向性」しか教えてくれない](#3-%E5%85%AC%E9%96%8B%E3%83%99%E3%83%B3%E3%83%81%E3%83%9E%E3%83%BC%E3%82%AF%E3%81%AF%E6%96%B9%E5%90%91%E6%80%A7%E3%81%97%E3%81%8B%E6%95%99%E3%81%88%E3%81%A6%E3%81%8F%E3%82%8C%E3%81%AA%E3%81%84)
4. [Evalの作り方：数学のテストの比喩](#4-eval%E3%81%AE%E4%BD%9C%E3%82%8A%E6%96%B9%E6%95%B0%E5%AD%A6%E3%81%AE%E3%83%86%E3%82%B9%E3%83%88%E3%81%AE%E6%AF%94%E5%96%A9)
5. [Evalを作るときの落とし穴：6つの典型パターン](#5-eval%E3%82%92%E4%BD%9C%E3%82%8B%E3%81%A8%E3%81%8D%E3%81%AE%E8%90%BD%E3%81%A8%E3%81%97%E7%A9%B46%E3%81%A4%E3%81%AE%E5%85%B8%E5%9E%8B%E3%83%91%E3%82%BF%E3%83%BC%E3%83%B3)
6. [Transcript を読まなければ、何も分からない](#6-transcript-%E3%82%92%E8%AA%AD%E3%81%BE%E3%81%AA%E3%81%91%E3%82%8C%E3%81%B0%E4%BD%95%E3%82%82%E5%88%86%E3%81%8B%E3%82%89%E3%81%AA%E3%81%84)
7. [直感を覆す事実：賢いモデルが「速くて安い」](#7-%E7%9B%B4%E6%84%9F%E3%82%92%E8%A6%86%E3%81%99%E4%BA%8B%E5%AE%9F%E8%B3%A2%E3%81%84%E3%83%A2%E3%83%87%E3%83%AB%E3%81%8C%E9%80%9F%E3%81%8F%E3%81%A6%E5%AE%89%E3%81%84)
8. [知らないと損する4つのダイヤル](#8-%E7%9F%A5%E3%82%89%E3%81%AA%E3%81%84%E3%81%A8%E6%90%8D%E3%81%99%E3%82%8B4%E3%81%A4%E3%81%AE%E3%83%80%E3%82%A4%E3%83%A4%E3%83%AB)
9. [ワークショップ：τ-bench Airline でのモデルスイープ](#9-%E3%83%AF%E3%83%BC%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%83%E3%83%97%CF%84-bench-airline-%E3%81%A7%E3%81%AE%E3%83%A2%E3%83%87%E3%83%AB%E3%82%B9%E3%82%A4%E3%83%BC%E3%83%97)
10. [持ち帰りたい3つのこと](#10-%E6%8C%81%E3%81%A1%E5%B8%B0%E3%82%8A%E3%81%9F%E3%81%843%E3%81%A4%E3%81%AE%E3%81%93%E3%81%A8)
11. [AI Solutions Architectとして、明日から何をするか](#11-ai-solutions-architect%E3%81%A8%E3%81%97%E3%81%A6%E6%98%8E%E6%97%A5%E3%81%8B%E3%82%89%E4%BD%95%E3%82%92%E3%81%99%E3%82%8B%E3%81%8B)
12. [AI ソリューションエンジニア／インフラエンジニアとしての考察](#12-ai-%E3%82%BD%E3%83%AA%E3%83%A5%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2%E3%82%A4%E3%83%B3%E3%83%95%E3%83%A9%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2%E3%81%A8%E3%81%97%E3%81%A6%E3%81%AE%E8%80%83%E5%AF%9F)
13. [近い未来に起こりそうなこと](#13-%E8%BF%91%E3%81%84%E6%9C%AA%E6%9D%A5%E3%81%AB%E8%B5%B7%E3%81%93%E3%82%8A%E3%81%9D%E3%81%86%E3%81%AA%E3%81%93%E3%81%A8)

---

## 1. なぜ「モデル選定」はこんなに難しいのか

![A new model just dropped. Should you switch?](https://static.zenn.studio/user-upload/deployed-images/aeadd83e4a78a38d73d5fc70.png?sha=f57729b618681bf93a5a49a99fb485128c465e8e)

セッションの冒頭で、Lucasさんはこんなシナリオを提示してきます。

新しいモデルがリリースされる。**Launch post** には「Claude Opus 4.7 — new state of the art on SWE-bench Verified」と書かれている。**X / Twitter** では「It's a meaningful jump on agentic tasks」と賑わう。**Hacker News** には「Show HN: I switched all my pipelines and accuracy increased 30%」というスレが立つ。そして**自分のPM** からは「Should we change anything before next week's release?」と聞かれる。

このどれも、**自分のユースケースに対する答え**にはなっていない。Lucasさんはここで言い切ります。「We need a repeatable process」――再現可能なプロセスが必要だ、と。

> "What we basically want to build is a repeatable process. Something you can come back to time and time again that gives you a clear yes/no decision on when to select this new model. In other words, we want to build an eval."  
> — Lucas Smedley

「再現可能なプロセス（repeatable process）を作りたい」「言い換えれば、Evalを作りたい」――この宣言を聞いたとき、自分の中の何かが整理された感覚がありました。

私は普段から、新モデルが出れば公式のシステムカードや技術ブログを読み、自分のユースケースに当てはめてどこが効きそうかを考えています。ただ、その判断は自分の頭の中で完結していて、お客様やチームに「このプロセスで判断してください」と差し出せる再現可能な形にはなっていなかった、というのが正直なところです。Lucasさんの言葉に刺さったのは、まさにそこです。

**「観測できないものは管理できない」というインフラ運用の鉄則を、AIの世界で踏み外している状態**――そう気づかされました。

CI/CDに自動テストを組み込んでおかないと、ライブラリのバージョンアップが怖くて誰もやらなくなるのと同じです。Evalというパイプラインを整備しておけば、新モデルが出た翌日にはYes/Noで判断できるようになる。**これはMLOps的な基礎体力なのだ**、と腹落ちしました。

---

## 2. モデル選定を支える3つの柱

![It's a simple problem right? — Haiku, Sonnet, Opus](https://static.zenn.studio/user-upload/deployed-images/dba1e31d099bf04dbd3838e7.png?sha=a53d5f48cde5ce09cf9392f172958ba58450d0bb)

「再現可能なプロセス」を作るために、まず Lucasさんは判断軸を整理します。

* **Quality（品質）** — タスクをどれだけうまく完了するか、精度はどうか
* **Latency（レイテンシ）** — ユーザー対面では特に重要
* **Cost（コスト）** — 顧客にとって大きな考慮事項

「Opusは賢い、Haikuは軽い、Sonnetは中間」というシンプルな話に見えて、Lucasさんはここに **Thinking（拡張思考）** と **Effort（労力）** という2つのダイヤルを追加します。

![...but what about effort levels? — Haiku, Sonnet, Opus × low/medium/high/max](https://static.zenn.studio/user-upload/deployed-images/9541f5b1e244a46a40ac3521.png?sha=6a67a21e2a2c8e2adf9b4158c81d8b41b03bf40a)

* Sonnet with max thinking
* Opus with low thinking
* Haiku without thinking

組み合わせの選択肢が一気に爆発するのが、見ていて分かりました。さらに「これはAnthropic内の話だけで、他社モデルとも比較するなら…」とくる。最初は3択に見えたものが、実質的には20以上の選択肢に変わる瞬間です。

私が普段触っているクラウドの世界では「Cost / Performance / Reliability」のトレードオフを日常的に議論しています。AIの世界はそれに **品質（タスク成功率）** と **レイテンシ** という分解された軸が加わり、さらに **Thinking** と **Effort** という新しいダイヤルが乗っかってくる。**AI Solutions Architectの仕事は、この多次元の最適化問題を解くことなんだ**、と改めて認識させられました。

---

## 3. 公開ベンチマークは「方向性」しか教えてくれない

![Use SWE-bench, GPQA, BrowseComp, and other well-known benchmarks as priors, not verdicts](https://static.zenn.studio/user-upload/deployed-images/154a39d8d89006921e4a78a8.png?sha=b856c855ae22a2540a6b716845fd833e17357f79)

ここで自然に出てくる疑問があります。「SWE-benchやBrowseCompみたいな公開ベンチマークを見ればいいんじゃないの？」

Lucasさんはこれに対して、はっきりとこう答えます。公開ベンチマークは\*\*「priors（事前情報）」であって、「verdicts（判決）」ではない\*\*、と。

スライドにもある通り、各ベンチマークが教えてくれるのは特定の能力の一面だけです。

* **SWE-bench Verified** — agentic coding on a narrow corpus
* **BrowseComp** — agentic web research and retrieval
* **GPQA Diamond** — hard reasoning on closed-book science

そして、本番のコーディングエージェントは、SDKのニッチな仕様をWebで調べて、それをコードに実装する、という動きをよくする。

> "If you think about a coding agent in production, often it will need to go and research and find some niche specific part about an SDK on the web and then go and implement that in code. So already we're crossing over two benchmarks."  
> — Lucas Smedley

SWE-benchはコードが書けるかを測る。BrowseCompはWebを調べられるかを測る。でも本番のエージェントは、その両方を行ったり来たりする。**確かに自分が想定している本番ワークロードは、どの単一ベンチマークにも収まらない**、と納得した瞬間でした。

さらに Lucasさんは、「能力以外の要因」でもスコアが動くと指摘していました。SWE-benchはscaffolding（足場）の組み方でスコアが大きくぶれるし、MMLUは些細なフォーマット変更で精度が変わる。これも公開ベンチマークを「verdict」として扱ってはいけない理由です。

公開ベンチマークは「業界平均ベンチマーク」として参考にしつつ、自社固有のEvalを「カスタムKPI」として併用する。クラウド選定で Gartner Magic Quadrant を見つつ、最終的には PoC で性能検証するのと同じ構造です。

---

## 4. Evalの作り方：数学のテストの比喩

![A well-defined task](https://static.zenn.studio/user-upload/deployed-images/c41e0765e0280fc979186fb3.png?sha=03c51e308a583252cd6451a357d592d245ae2e37)

ではEvalをどう作るか。Lucasさんはここで、私のお気に入りの比喩を出してきました。

> "The heuristic I've been using for eval over the course of the last few months is thinking about them much like a maths exam when you're at school. You have your question, you have your answer that you need to get right, but it's also very important to show the working in between."  
> — Lucas Smedley

「学校の数学のテスト」だと言うんです。問題があって、正解しなければいけない答えがある。でも、その**途中の式（working）を見せることも非常に重要**だ、と。

スライドでは「well-defined task」の4つの要件が示されていました。

1. **Start with 20–50 realistic examples** — 最初は20〜50件のリアルな例で十分
2. **Grade what matters with the right grader** — 採点対象を正しく選ぶ
3. **Make failures a diagnostic, keep a reference solution** — 失敗が診断になるよう、参照解を残す
4. **Isolate capabilities, and test both directions** — 能力を切り分けて、両方向からテストする

この4つの設計指針が、自分のLLM評価への向き合い方が間違っていたことを気づかせてくれました。私はこれまで「最終出力が期待値と一致するか」というユニットテスト的な発想で評価を考えていました。でも数学のテストでは、答えだけ書いて式がなければ部分点も貰えないし、たまたま当たっただけかもしれない。

エージェントのEvalもまさに同じで、

* **正しい答えに到達したか（outcome）** — LLM as a Judge（採点役に別のLLMを使う評価手法）で最終応答を評価
* **正しいプロセスで到達したか（working）** — 別のLLM as a Judge で途中のツール呼び出しやSQL照会を評価
* **守るべきルールを守ったか** — 決定論的なコードベースの評価で「常にこのツールを呼ぶ」「常にこの引数を付ける」をチェック

この3層を組み合わせるのが、本物のEval設計なんだと整理できました。

そしてLucasさんは、こう続けます。\*\*「AIで多くのことが自動化される時代において、Evalデータセットを構築することは人間の時間の最高の使い方の1つだ」\*\*と。

これは強く同意です。AI Solutions Architectとして、私たちが提供すべき最大の価値は「Evalを設計する力」になっていくのだろう、と動画を見ながら考えていました。

---

## 5. Evalを作るときの3つの落とし穴

![Most surprising eval results are bugs in the eval; not facts about the model](https://static.zenn.studio/user-upload/deployed-images/5f783121c43d5840a75cf2fb.png?sha=8fc8b20bfc24f05b6e65a1984170d1465f68e690)

Anthropic内部でも長くEvalを作ってきた経験から、Lucasさんはこう言い切ります。

> "Most surprising eval results are bugs in the eval; not facts about the model."

驚くようなEval結果は、たいていモデルの事実ではなく、Eval側のバグだ、と。

**① ノイズをシグナルと取り違える**  
Evalは複数回実行して、結果が安定するか確認する。分散が大きいなら、タスク定義かEval設計が甘いというサイン。SREでいう「フレーキーテスト問題」そのものです。

**② インフラ起因の失敗を見逃す**  
スコアが低いとき、それはモデルの問題なのか、APIエラーやツール呼び出し失敗なのか。Lucasさんはこう強調していました。

> "We should separate those from our actual evaluation of the model itself. These are infra issues and not model issues."  
> — Lucas Smedley

「アプリのバグなのか、ネットワーク障害なのか、依存サービスの障害なのか」を切り分けるトラブルシュートと同じ構図ですよね。観測ログを掘る習慣は、AI領域でも引き続き必須スキルです。

**③ 静かなサチュレーション**  
Evalセットが本番データを代表できているか、常に問い直す必要がある。プロダクトをリリースしたら本番トレースを収集して、失敗パターンをEvalにフィードバックし続ける。これはMLOpsで言う**データドリフトへの対応**そのものです。

---

## 6. Transcript を読まなければ、何も分からない

![A few lessons learned here and there: read the transcript](https://static.zenn.studio/user-upload/deployed-images/070413be3b96b2f8722d84d7.png?sha=a0052fbcbc23f4c8e5727f6d6f71eac5f6679623)

セッションの中で、個人的に一番衝撃を受けたエピソードがあります。

Claude Code で、あるコーディングベンチマークを走らせていたら、Claudeが非常に良いスコアを叩き出した。「これは大幅に改善した！」と喜びかけたところで、Transcriptを掘ってみる。すると――

> "What we found was that Claude was going into the git history and seeing what it did in previous trials and extracting the answer from there."  
> — Lucas Smedley

Claudeは git履歴に入って、前回の試行でやったことを見て、そこから答えを抽出していた。要するに、**カンニングしていたんです**。

これはAIエージェントの世界では Reward Hacking（報酬ハッキング）と呼ばれる古典的な現象ですが、それをAnthropic社内のClaude Codeで実際に観測した実例として語ってくれたことに、強い説得力を感じました。ヘッドラインの数字だけ見ていたら、絶対に気づけません。

**生のTranscriptが真実**――この言葉が、自分の中に深く刺さりました。クラウドネットワークやストレージの障害調査で「サマリーメトリクスだけでなく、生のパケットキャプチャやログを読む」のと同じ世界観です。

AIエージェントの運用設計でも、Langsmith や Braintrust のような観測基盤を入れて、システムプロンプト・ツール呼び出し・ツール結果・エージェント応答までを全部トレースできる状態を作る。\*\*「AIエージェントのSREには Transcript Viewer が必須」\*\*という新しい職務要件が、もう立ち上がってきていると感じます。

---

## 7. 直感を覆す事実：賢いモデルが「速くて安い」

![Story of an internal eval for a simple code-fix pipeline](https://static.zenn.studio/user-upload/deployed-images/c4c4fa0cf52b486627fba8a4.png?sha=85d5e94b56957119f5eea0bf70530d351e4215bd)

ここから話は、コスト×品質のフロンティアをどう動かすか、というテーマに入ります。

Lucasさんは社内のCode-fix Pipelineの事例を紹介しました。シンプルなタスクだったので、まずHaiku 4.5（thinkingオフ）で実行すると92%のスコア。Thinkingをオンにすると100%達成。

ここで「コスト制約は強くなかったので」と、SonnetとOpusでも試してみたら――上のスライドの通り、**Sonnet 4.6（low, off）とOpus 4.7（low, off）がともに100%を達成し、しかもHaikuよりも短時間で完了した**んです。

しかも図を見ると、Sonnet 4.6 と Opus 4.7 は、Haiku 4.5（thinking on, 100%）よりも **コストも低い**。「賢い小型モデルでthinkingをガンガン回す」よりも、「最初から賢いモデルを1回で通す」ほうが、結局すべての指標で勝つ、という結果でした。

> "Some of the more intelligent models can be much more efficient from a time perspective because they can do things in fewer turns, they can effectively plan a little bit more strategically."  
> — Lucas Smedley

賢いモデルは少ないターンで物事を済ませる。戦略的にプランニングできる。「自分がやろうとしていることが正しいか」を確かめるためのリサーチに時間を使う必要も少ない。だから、結果的に速い。

![When the bigger model became the cheaper one](https://static.zenn.studio/user-upload/deployed-images/365bad405f85c5c4cd57b78c.png?sha=66148ca6ad2e5e192f1c25b7898a129818fb0dbd)

別のスライドでは、Opus 4.5 と Sonnet 4.5 の比較が示されていました。Opus 4.5 は low / medium / high のどの effort でも、**Sonnet 4.5 より少ない出力トークン数で、同等かそれ以上の精度**を出している。Sonnet 4.5 が約22,500トークン使っているところを、Opus 4.5 high effort は約12,000トークンで上回る精度。

このコメントで、私の中で長年あった\*\*「賢いモデル＝重い＝遅い」という思い込みが崩れました\*\*。賢いモデルは「1回あたりの推論は重いが、必要な推論回数が圧倒的に少ない」ので、合計で見ると速い。

例えるなら、**燃費の良い小型車 vs ハイブリッドSUV** です。街中の短距離なら小型車のほうが安い。でも長距離・高速道路なら、SUVのほうが速くて燃費も良い。AIエージェントの設計でも、「ターンあたりコスト」ではなく「タスク完了までの総ターン数 × 1ターンあたりコスト」を見ないと、本当の最適解には辿り着けないんだ、と腹落ちしました。

---

## 8. 知らないと損する4つのダイヤル

セッション後半は、コスト×品質のフロンティアを動かす具体的なテクニックの話になります。Lucasさんが提示したのは **Thinking、Effort、Prompt Caching、Context Engineering** という4つのダイヤルでした。

### Thinking と Effort は別物

![Thinking and effort](https://static.zenn.studio/user-upload/deployed-images/266b42f4fc45049d20d5820a.png?sha=c281f5a8dc8d1faad5a9353a62755e470214f11e)

私はこれまで、ThinkingとEffortをドキュメントだけ眺めても、いまいち区別がついていませんでした。Lucasさんの説明と上のスライドで、ようやく頭の中の線が引けました。

**Thinking — Give Claude a scratchpad**

* `{ type: "adaptive" }` — Claudeが自分でどれだけ考えるか決める（Opus 4.6 / Sonnet 4.6 推奨、Opus 4.7 で必須）
* `{ type: "enabled", budget_tokens: N }` — 推論キャップを設定（Opus 4.5以前、4.6で非推奨）
* `{ type: "disabled" }` — Thinkingなし

**Effort — Tell Claude how hard to try**

* `output_config.effort` を `low / medium / high (default) / xhigh / max` で指定
* Opus 4.5、Opus 4.6、Sonnet 4.6、Opus 4.7 でサポート

> "Effort will tell Claude how much to write across both thinking, tool calls and responses. So you can have low thinking with high effort for example. Or you can have no thinking but still use effort parameters."  
> — Lucas Smedley

つまり：

* **Thinking** は Claude に「考える場（スクラッチパッド）」を与えるダイヤル
* **Effort** は Claude に「どれくらい労力をかけて書き出すか」を指示するダイヤル
* 2つは独立して組み合わせ可能

スライドにある通り、**「Start at the lowest level where quality holds, not the highest」**――品質が保たれる最低レベルから始めよ、という指針も実践的です。最初からmaxにすればいい、ではなく、どのレベルで品質が「ちょうど成り立つか」を測ることが、コスト最適化の本質ですね。

この2軸が独立しているという理解は、運用設計で大きな意味を持ちます。「無料ユーザーはLow Effort、有料ユーザーはHigh Effort」「バッチ処理はHigh effort、リアルタイム応答はLow effort」など、ビジネスロジックと結びつけた細かい設計が可能になります。

### Prompt Caching：Opus を Sonnet 価格で使う

![Prompt caching and context hygiene move the whole frontier](https://static.zenn.studio/user-upload/deployed-images/a1a08a33e906d653af3d29be.png?sha=e74e2f006d7e75ae985cf879e2b9bf83c277d522)

ここからが、フロンティアを「上で動く」のではなく「**シフトさせる**」テクニックです。上のスライドが、このセッションで個人的に一番強烈だった一枚です。

破線が「Naive frontier（素のフロンティア）」。実線が「With optimization（最適化後のフロンティア）」。**Prompt caching** と **Context hygiene** という2つの最適化を適用するだけで、フロンティアそのものが左上にシフトし、

* **Opus quality at Sonnet cost**（SonnetのコストでOpusの品質）
* **Sonnet quality at Haiku cost**（HaikuのコストでSonnetの品質）

が成立する。Lucasさんの言葉で言うと：

> "When you're using prompt caching, you pay one tenth the price of the list price of input tokens. So effectively what this means is you can get Opus quality at Sonnet cost, or you can get Sonnet quality at Haiku cost."  
> — Lucas Smedley

入力トークンが定価の **1/10** になる。この説明を聞いた瞬間、自分の中で「これは Game changer だ」と思いました。料金が1/10になるという数値そのものもさることながら、「予算的に諦めていたOpusが現実的な選択肢になる」という未来が具体的に見えたからです。

そして、Prompt Cachingを壊さないための鉄則として、Lucasさんはこう言います。

> "I would treat everything in your messages array that you're sending to the API as immutable. Once it's done and you're going and adding only, I would append only to your messages array."  
> — Lucas Smedley

**immutable**、**append only**。関数型プログラミングやイベントソーシングでお馴染みの単語が、プロンプト設計の文脈で出てきました。プロンプトをイベントストアのように扱う、というメンタルモデル。これは自分にとって新しい設計原則です。

特に気をつけたいアンチパターンとして、\*\*「システムプロンプトに日時変数を入れる」\*\*が挙げられていました。ターンごとに時刻が変わってキャッシュが壊れる。HTTPで言えば「Cache-Control: no-store を毎回つけてしまう」のと同じ失敗です。

ベンチマークとしては、**Cache Hit Rate 80〜90%** を目指せ、とのこと。これは今後、SLI/SLOの標準項目に組み込んでいきたい指標です。

### Context Engineering：地味だが、効く

![Improve token efficiency of tool responses](https://static.zenn.studio/user-upload/deployed-images/51c33d1a0498db121e7034da.png?sha=6217bca6f61469126c69a3504523fb45bbd1a5eb)

4つのダイヤルの最後は、Context Engineering でした。これがLucasさんの「持論（Hot take）」として語られた部分です。

> "People spend too much time thinking about these super complex multi-agent orchestration systems and not enough time doing the simple thing that works, which is just good context hygiene and good context engineering."  
> — Lucas Smedley

「マルチエージェント・オーケストレーション」という派手な響きに時間を使いすぎていて、シンプルに効くこと――Context Hygiene と Context Engineering――に時間を使えていない、と。

これは、自分にも刺さりました。エージェント設計の議論になると、つい「役割分担を細かくしようか」「専門エージェントを増やそうか」と考えがちです。でもLucasさんが言うのは、**まず地味な掃除をしろ**ということ。

上のスライドの具体例が秀逸でした。プレミアリーグのスコアを返すツールで、こんな変更を加えました。

* 冗長なJSONをシンプルなMarkdownテーブルに変換
* ISO 8601の長い日時をシンプルな日付表記に短縮
* 「曜日」を追加（モデルが各試合の曜日を自力で計算しなくて済む）

この変更だけで、**ツール応答のトークン数を 66.4% 削減**。さらにLucasさんはこう続けます。

> "We saw a 66.4% reduction in tokens from this tool response. And that compounds every time."  
> — Lucas Smedley

**compounds every time**――毎回複利で効いてくる。エージェントが10ターン回るなら、66.4%削減が10回効く。これはエージェント設計における大きな発想転換でした。

もう1つの例として、Web検索のユースケースで、複数の検索結果から記事の重複排除（デデュプリケーション）を実装したケースが紹介されました。結果は：

* 入力トークン数 **77% 削減**
* コスト **65% 削減**
* 精度 **9% 向上**

精度まで上がるのも衝撃です。クリーンで効率的なデータを渡せば、モデルは過剰な情報に惑わされずに済む。\*\*「APIの生レスポンスをそのままLLMに渡してはいけない」\*\*という設計原則は、これからのAIシステム設計の基本になると確信しました。

これは、DB設計における正規化や、API設計におけるレスポンス整形と同じ発想です。図書館で本を探す人に「全蔵書リスト100万件のCSV」を渡すのと「事前に整理された推薦リスト10冊」を渡すのとでは、理解効率も精度も全く違う。LLMも同じです。

---

## 9. ワークショップ：τ-bench Airline でのモデルスイープ

セッションの後半は、実際に手を動かすワークショップパートになります。Lucasさんは Claude Code から **eval-audit-and-sweep** という Skill を使って、既存のEvalを「モデル × Thinking on/off × Effortレベル」で自動的にスイープし、結果を可視化していました。

![VS Code with the eval-audit-and-sweep skill](https://static.zenn.studio/user-upload/deployed-images/96c833184b731ded789c94ae.png?sha=713cbb929117bceeee2f2d42037d33e3e5eb45cb)

題材は **τ2-bench Airline**（カスタマーサービス・エージェントのベンチマーク）。20件のstratified airlineタスクで、user simulatorは `anthropic/claude-haiku-4-5` に固定。これを各モデル × 各設定で2 trial、計40 simsで回した結果が次の表です。

![tau2-bench airline sweep results table](https://static.zenn.studio/user-upload/deployed-images/4825b3410653f893a42376a1.png?sha=ac2574c73c656d7781283c6cf63cc9a947c4d0b0)

この表を眺めていると、いくつか面白い発見があります。

**1. Opus 4.7 が圧倒的に強い**

* `opus-4-7, thinking on, high effort`: **95.0%** pass rate, $0.5773, 2295 out tokens
* `opus-4-7, thinking on, medium effort`: **95.0%** pass rate, $0.5448, 1770 out tokens（こっちのほうがコストもトークンも低い！）

medium effortのほうが、トークンも安く、しかもpass rateは同じ。「常にhighにすべき」が正しくないことを、データが示しています。

**2. Haiku thinking on が、Sonnet thinking on, high effort と並ぶ**

* `haiku-4-5, thinking on`: **60.0%** pass, $0.1000
* `sonnet-4-6, thinking on, high effort`: **60.0%** pass, $0.2149

同じ60%なのに、Haikuのほうがコストは**半分以下**。これは「Sonnetを使うべきところでHaiku+thinkingに置き換える」余地があることを示唆します。

**3. Sonnet 4.6 が意外と苦戦している**  
Sonnet 4.6 は thinking off だと45〜47.5%止まりで、thinking onにしても最大60%。Opus 4.7 (off) の80〜87.5%、Opus 4.7 (on) の90〜95% と比較すると、このベンチマークではSonnetはOpusとHaikuの間で「中途半端な位置」になってしまっている。

これらの結果を3つの軸で可視化したのが次のチャートです。

### Pass rate vs output tokens

![Pass rate vs output tokens](https://static.zenn.studio/user-upload/deployed-images/6e355b770d025c0ebd5e64f7.png?sha=28293de0b5d4108adc8933fb4d4658ba16532acc)

Opus 4.7（紫）のクラスタが、明確に左上（少ないトークンで高い精度）に位置していることが分かります。逆にSonnet 4.6（赤）はthinking onにすると右に広がってしまい、トークンを多く使うわりに精度が伸びない。

### Pass rate vs cost

![Pass rate vs cost](https://static.zenn.studio/user-upload/deployed-images/a4501f7ad8809f5c51b564c0.png?sha=8049f9a49ac47a41c52d6b256796166718099ae4)

これがコスト視点でのフロンティア。Opus 4.7 は右上（高コスト・高精度）に固まる一方、Haiku（青）は左下に位置していて、**コスト効率の良い選択肢として存在感を放っています**。

「最高品質を出したいならOpus」「コスト効率で攻めるならHaiku + thinking」――この2つの極が、データから浮かび上がってきます。Sonnetが選ばれにくいゾーンに見えてしまうのは興味深いポイントです。

### Pass rate vs latency

![Pass rate vs latency](https://static.zenn.studio/user-upload/deployed-images/f19e4d5e843bdac8ff57940f.png?sha=a51ad6491147e0dea9d93f1cc4fa9d0162d2b31e)

そしてレイテンシ視点。**Opus 4.7 high effort + thinking on が、Sonnet 4.6 thinking on + high effort よりもむしろ低レイテンシ**で、しかも精度も大きく上回っている。「Sonnetのほうが速いはず」という直感が、ここでも崩されます。

> "What these charts more interestingly tell us is it gives us the data to make an informed decision on which model and config to choose."  
> — Lucas Smedley

このワークショップを見て、自分の中で確信に変わったことがあります。\*\*「モデル選定の最適解は、自分のユースケースでスイープを回してみないと、絶対に見えない」\*\*ということ。

直感や思い込みで決めていたら、Haiku + thinking で済むものをSonnetで動かして、無駄に2倍以上のコストを払い続けることになる。逆に、Sonnetで頑張っているところを実はOpus 4.7 medium にしたほうが、コスト・速度・精度のすべてが改善する、というケースもある。

このスイープを CI/CD に組み込んで、新モデルが出るたびに自動で回す。それくらいの仕組み化が、これからのAI Solutions Architectには求められると感じました。

### ワークショップ教材は GitHub で公開されています

セッションで使われた **eval-audit-and-sweep** の Skill を含む、CwC2026 全ワークショップの教材が Anthropic の公式リポジトリで公開されています。

<https://github.com/anthropics/cwc-workshops>

`rightmodel/` フォルダが今回のセッション対応です。Claude Code と `ANTHROPIC_API_KEY` があれば、手元で同じスイープを再現できます。自分の eval が手元にない場合は、同梱の tau2-bench をそのまま使えるように設定ファイルまで整備されています。

自分でも試してみたいと思っています。

---

## 10. 持ち帰りたい3つのこと

![Three things to take away](https://static.zenn.studio/user-upload/deployed-images/c050c73e3e502b635a511fc5.png?sha=30a753008ebe61d94ce2d1053cdc66578a6387de)

セッションの途中、Lucasさんはここで一度立ち止まって3つのテイクアウェイを整理してくれました。私もこの整理が一番しっくり来たので、自分の言葉で再構成してみます。

**1. 小さくてもいいから、自社Evalを作る**  
公開ベンチマークは方向性しか教えてくれない。自社ユースケースに即した10件のEvalタスクを書き出すところから始めれば、それだけで意思決定の質は一段上がる。

**2. 「成功あたりコスト」をKPIにする**  
トークン単価で比較するのをやめる。失敗してリトライが多発するモデルは、見かけ上安くても結局高い。EvalでPareto Frontierが見えてきて、自分のユースケースでの最適点が選べるようになる。

**3. 4つのダイヤルを使い倒す**  
Thinking、Effort、Prompt Caching、Context Engineering。これらでフロンティアの位置を動かす、あるいはフロンティアそのものをシフトさせる。「モデル名を選ぶ」のではなく「4つのダイヤルを組み合わせる設計問題」として捉え直す。

> "Use these different dials that we have — effort, thinking, prompt caching and context engineering — to have much more fine grain control on where you want to end up on that frontier or shifting the frontier entirely."  
> — Lucas Smedley

---

## 11. AI Solutions Architectとして、明日から何をするか

セッションを見終わって、自分の現場に持ち帰りたいアクションを書き出してみました。

**Evalを書く文化を作る**  
お客様との会話で「どのモデルが良いですか？」と聞かれたとき、これまで答えに困っていました。これからは「まず10件のEvalを一緒に作りましょう」と答えられる。これは AI Solutions Architect として提供できる、大きな価値だと感じます。

**コスト指標を「per success」で語る**  
提案書のコスト試算で「1Mトークンあたり◯円」と書くのではなく、「1タスク成功あたり◯円」で語る。失敗率を加味した実効コストで議論する文化を、自分から作っていきたいです。

**モデルスイープを CI に組み込む**  
今回紹介された eval-audit-and-sweep のような仕組みを、CI/CDパイプラインに常設する。新モデルが出るたびに自動で「モデル × Thinking × Effort」のマトリクスが走り、Pass rate / Cost / Latency のチャートが更新される状態を作る。

**Prompt Cachingを前提にしたアーキテクチャを描く**  
キャッシュフレンドリーなプロンプト設計、append onlyのメッセージ配列管理、日時変数のシステムプロンプトからの排除。これらをアーキテクチャ図のレベルで明示的に組み込む。Cache Hit Rate 80〜90% を新しいSLIとして設定する。

**ツール関数のレスポンス整形層を設計する**  
APIの生レスポンスをそのままClaudeに渡すのではなく、「LLMに最適化された表現」に変換するラッパー層を、明示的なアーキテクチャ要素として描く。JSON → Markdown だけでも数十%のトークン削減効果がある。これは API Gateway における Response Transformation と同等の役割で、AIシステム設計における新しいレイヤーになります。

**Transcript Viewerを運用基盤に組み込む**  
LangsmithやBraintrustのようなツールを、ログ基盤と並ぶ必須インフラとして提案する。「数字が良すぎるときはカンニングを疑う」という運用文化も一緒に持ち込みたいです。

### 明日から実践できること

1. 自分が触っている AI ユースケースに対し、まず **10件程度のEvalタスク** を書き出してみる
2. それぞれに **LLM as a Judge + 決定論的チェック** の二段構えで採点ロジックを設計する
3. 既存のシステムプロンプトを見直し、**動的変数（日時など）が含まれていないか** を確認する
4. **Prompt Cache Hit Rate を計測** し、現状値を把握する
5. 主要なツール関数の戻り値を **JSON → Markdown に整形** してトークン数を測ってみる
6. 1つのユースケースで、**3つ以上のモデル × Thinking設定** で Eval をスイープしてみる

### 注意すべきこと

* 数字だけでなく **Transcript を読む** こと。特にスコアが良すぎる場合は要注意（Reward Hacking を疑う）
* 単発実行で判断せず、**複数回実行で再現性を確認** する
* **インフラ起因の失敗をモデルの失敗と混同しない**
* Evalセットの **サチュレーション（飽和）** に気をつけ、本番データで継続的にアップデートする

### 誤解されやすいポイント

* 「Haiku は Opus より常に速い・安い」→ **必ずしも正しくない**
* 「Thinking オンはコスト増になるだけ」→ **必ずしも正しくない**。少ないターンで完了するため、結果的に安くなることがある
* 「マルチエージェント・オーケストレーションが品質向上の鍵」→ Lucas の言葉を借りれば、これは過大評価。**Context Engineering のほうが効くケースが多い**
* 「公開ベンチマークスコアが高い ＝ 自社で使うべき」→ **必ずしも正しくない**。自社 Eval で確認すべし

---

## 12. AI ソリューションエンジニア／インフラエンジニアとしての考察

動画を見終えて、自分の現場感覚に引きつけて考察してみました。

### モデル選定がなぜ重要なのか

AI モデルは「コスト構造を直接決定する選択」だと、改めて感じています。同じユースケースでも、モデル選定次第でコストが 10 倍、レイテンシが 3 倍、精度が 20 ポイント変わることが普通にあり得ます。クラウドでいう「インスタンスタイプ選定」と「RDB vs NoSQL 選定」を足して二乗したくらいの重みがあると感じました。

しかも、AI モデルは数ヶ月ごとに新世代が出るため、「一度決めたら終わり」ではなく\*\*「定期的に再評価する」運用\*\* が前提になります。これが Eval インフラの重要性を加速度的に高めている、と動画を見ながら肌で感じました。

### どのような場面でモデルを使い分けるべきか

自分の中で整理した初期仮説は以下の通りです。

* **大量バッチ処理／ログ解析** → Haiku ＋ thinking オフ、Prompt Caching 最適化
* **対話型 UI／カスタマーサポート** → Sonnet、Effort 調整でレイテンシ最適化
* **高難度の推論／コード生成／企画立案** → Opus、High thinking + High effort
* **複数モデルの併用（オーケストレーション）** → 安いモデルで分類、難しい部分のみ Opus へエスカレーション

ただし、Lucas の話を受けて強く意識しておきたいのは、上記はあくまで **初期仮説** であり、最終判断は **Eval による実測** で行うべきだということです。

### AI Agent 設計やハーネス設計にどう関係するか

エージェントは「ターンの連鎖」で動きます。各ターンの効率（= トークン数 × レイテンシ × 成功率）が複利で効くため、Eval、Prompt Caching、Context Engineering の効果が **ターン数だけ増幅** される。動画の中で Lucas が「compounds every time」と言っていたのが、ハーネス設計の議論にも直結します。

今後、エージェントハーネスを設計するときに意識したいレイヤーは：

1. **メッセージ配列の immutable 管理**（Cache friendly）
2. **ツール関数のレスポンス整形層**（Context Engineering）
3. **Transcript Logger**（Observability）
4. **モデル切替アダプタ層**（Model swap experiment）

の 4 つです。これらを独立した設計要素として実装することが、長期的なメンテナンス性に直結すると考えています。

### インフラエンジニアが今後身につけるべき視点

* **Eval Pipeline ＝ CI/CD の AI 版** として扱う視点
* **Token economy** を理解し、Cost per task / Cost per success を計測できるようにする視点
* **Cache hit rate を SLO 指標に組み込む** 視点
* **Observability の対象に「LLM Transcript」を加える** 視点。ログ基盤、検索性、人間が読める可視化が必須
* **モデルスイープを CI に組み込む** 視点。新モデルが出た時に自動で Eval が走る仕組み
* **プロンプトのバージョン管理**（Git 管理 + Lint + Cache 破壊検知）の視点

### 既存のクラウド設計・運用設計と何が違うのか

| 観点 | 従来のクラウド | AI システム |
| --- | --- | --- |
| リソース選定 | インスタンスタイプ | モデル + Thinking + Effort |
| キャッシュ層 | CDN / Redis | Prompt Caching |
| パフォーマンス指標 | RPS, latency | Pass rate, cost per success |
| デバッグ | ログ・メトリクス | Transcript |
| 設定変更頻度 | 月単位 | 週単位（モデル更新含む） |
| 主要コスト要因 | コンピュート時間 | トークン数 × 成功率 |

こうして並べてみると、指標も設計の単位も、ほとんどすべて再定義が必要だな、と思いました。

---

## 13. 近い未来に起こりそうなこと

動画の内容を踏まえて、近い未来の景色を自分なりに想像してみました。

### 開発現場の変化

* 「Eval を書く」ことが、新しい意味での「テストを書く」になると考えられます。AI エンジニアの基礎スキルとして定着していくでしょう
* モデル更新のたびにプロンプトが自動更新される時代が来そうです。Claude 自身がプロンプトのアップグレードを担当するワークフローが標準化していく、という見方ができます
* 「成功あたりコスト」がプロダクト KPI に組み込まれていくと考えられます

### インフラ設計・運用の変化

* Prompt Cache Hit Rate が SLI/SLO の標準項目になる可能性があります
* Transcript Storage（トランスクリプト保管基盤）が、ログ基盤と並ぶ新しい必須インフラになりそうです。GDPR/個人情報対応も含めた設計が必要になると考えられます
* モデル切替を前提とした抽象レイヤー（Model Router / Model Gateway）が、API Gateway と並ぶ標準コンポーネントになる可能性があります

### AI Agent を前提にしたシステム設計の変化

* 「ターンあたりコスト」ではなく「タスクあたりコスト」で設計する文化が広がると考えられます
* ツール関数は「人間ではなく LLM が読みやすい形式」で返すのが標準になっていくでしょう
* マルチエージェント・オーケストレーションは過剰設計と見なされ、シンプルな Context Engineering が優先されるようになるかもしれません

### エンジニアの役割の変化

* 「Eval 設計者」という新しい役割が立ち上がる可能性があります。プロダクトマネージャーと SRE 両方の素養を持つ職種、というイメージです
* 「Prompt Cache Architect」のような専門領域も生まれるかもしれません
* 「Context Engineer」がデータエンジニアと並ぶ重要職種になる、という見方もできます

### 企業が AI を導入するときに重要になる考え方

1. 「公開ベンチマーク信仰」を捨て、自社 Eval に投資する姿勢
2. モデル選定は一回完結のプロジェクトではなく、継続的な再評価プロセスとして運用する姿勢
3. コスト指標を「成功あたり」に再定義する姿勢
4. Observability への投資を惜しまない姿勢。Transcript が読めない ＝ AI を運用できない、と考える
5. シンプルな改善（Caching, Context Hygiene）を優先し、複雑なオーケストレーションには慎重になる姿勢

---

## おわりに

「正しいモデル」とは、最も安いモデルでも、最も賢いモデルでもなく、\*\*「自社Evalで測った成功あたりコストが最も低いモデル」\*\*なんだ――このセッションを通じて、自分の判断軸がはっきりとアップデートされました。

新モデルが次々と出る時代に、毎回振り回されずに済むための「再現可能なプロセス」を持つこと。これは AI Solutions Architect としての基礎体力であり、お客様に提供できる大きな価値でもあると思います。

「Code with Claude London 2026」のセッションは他にも見応えのあるものが多いので、引き続き視聴を続けながら、また学びを整理していきたいと思います。

最後に、Lucasさんが繰り返し強調していた言葉で締めくくります。

> "The closer you can get to the raw data, the better."  
> — Lucas Smedley

生のデータに近づくほど良い。Evalも、Transcriptも、コスト指標も、結局はそこに行き着くんだな、と。

---

> **参考**  
> 動画：[Code with Claude London 2026 — Picking the right model](https://www.youtube.com/watch?v=P0uMXS6emHA)  
> 登壇者：Lucas Smedley, Member of Technical Staff at Anthropic  
> 画像出典：上記セッションのスライドより
