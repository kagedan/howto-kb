---
id: "2026-07-02-ai-はどこまで賢くなれば経営を任せられるか-intelligence-と直交する-bottlene-01"
title: "AI はどこまで賢くなれば経営を任せられるか — intelligence と直交する bottleneck の位置"
url: "https://zenn.dev/takyone/articles/agent-business-limits-2026-07"
source: "zenn"
category: "construction"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "waterworks", "zenn"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-rss"
query: ""
---

## はじめに

「agent の能力が上がれば、いずれ経営判断まで含めて全部任せられる」という期待があります。  
この図式の下では、完全自律までの残りの問いは「いつ」だけです。

本記事の主張は、この前提への反例です。

> **完全自律を阻む bottleneck は、intelligence の軸の上にない。どれだけ capability が上がっても内側に取り込めない役割 (目的関数の供給と校正) が特定の位置に残り、その位置は capability の向上では動かない。**

「AI には難しすぎる仕事が残る」という主張ではありません。  
難しさは capability で削れます。  
残るのは位置の問題で、「賢い agent」という束を経済学の語彙でほどくと輪郭が見えます。

前記事 ([AI agent はビジネスを完全に回せるか](https://zenn.dev/takyone/articles/medallion-ontology-economic-framing)) の経済学パートを独立させ、論証を組み直したものです。  
前記事を読んでいなくても読めます。

## 本記事のポイント (TL;DR)

* AI agent には認知 (B) と行為 (A) はあるが、**standing を持つ u** (自分の welfare が成功の定義に算入される選好) がない。claim の運び手にはなれるが、持ち主にはなれない
* だから所与の目的への改善 loop (**1→100**) は組めるが、目的の起源 (**0→1**) は内側から出ない。「賢くなれば全部」はこの 2 つを一本の軸に混ぜている
* 現実の agent は trainer (第二の principal) の符号化選好を積んで届く。その中身は集約された人間の是認と否認、つまり符号化された道徳感情である
* \theta (目的関数の符号化) は必ず proxy になり drift する。内部化の 3 経路には Goodhart / time-inconsistency / informativeness principle が劣化機構を与え、緩和策はすべて外部判定者を再導入する
* 人間 CEO への委譲も governance があって成立してきた。AI を椅子に座らせる工事の中身は「賢くする」ことではなく、stake と同一性と責任経路の制度工事になる
* 予測: agent の autonomy の上昇は、人間側の liability 引き受けと認証・保険基盤の成長を伴う

## 主張の範囲

### 残る仕事は 1 つ

ビジネスの運転を、目的関数を所与として業務を回す部分と、目的関数そのものを決めて更新する部分に分けます。  
前者 (所与の KPI の下でのマーケ配信、在庫補充、CS 対応、定型分析) には原理上の障壁がなく、現在人手にあるのは capability の問題にすぎません。

残るのは 1 点です。  
**「この会社は何を大事にするか」を機械が解釈できる形に符号化したもの (以下 \theta) を供給し、校正し続ける役割は、最適化 system の内側に置けない。**

### 「完全自律」の 2 つの意味

すれ違いを避けるため、「完全自律」を 2 つに分けます。

* **CEO 型自律**:外部の統治 (評価、報酬設計、解任権) の下で、広い運用裁量を持って回る形。人間の経営委譲はこれ
* **ownerless 型自律**:その統治ごと内側に吸収し、外部の校正主体なしで回る形

本記事の障壁が効くのは後者だけです。  
前者は AI にも到達しうる形ですが、それは governance 設計の成果であって capability の成果ではなく、「椅子に座る資格」という別の問題を伴います (後述)。

### 本記事の相手と、主張しないこと

「ownerless 型を目指す」と明示的に主張する論者は、ほとんどいません。  
本記事の相手は特定の論文ではなく、「capability が上がり続ける、だから任せられる範囲が広がり続ける、だからいずれ全部」という流通した外挿です。  
この外挿は 2 つの自律の区別を持たないまま「全部」に到達します。  
本記事の仕事は、この外挿に区別を入れることです。

主張しないことも確定させます。

* **不可能性定理は証明しません**。3 つの古典原理はリスクと制約の定理であり、本記事がやるのは「緩和はできるが、どの緩和策も外部位置を再導入する」という構造の特定です
* **経営業務の大部分が委譲不能とは言いません**。境界の内側は広い
* **時期の予測はしません**

## 全体の見取り図

検証する問いは 3 つです。

* 問い 1:system は自分の \theta を自分で書けるか
* 問い 2:人間が設計時に一度だけ書けば済むか
* 問い 3:\theta を書き直す作業自体を、内側の agent に委譲できるか

3 つとも答えは no ですが、no の理由はそれぞれ別物です。

## 準備:「賢い agent」という束をほどく

### agent の 3 成分

意思決定理論が扱う主体は、3 つの成分でできています。

* **認知 (B)**:世界についての belief を作り、推論する能力
* **行為 (A)**:実行できる行動の集合と、その実行能力
* **評価 (u)**:帰結に対する選好順序。「この主体にとって何かが掛かっていること」の表現

経済学は u を primitive (それ以上遡らない所与) とし、B と A は u に仕える機構として扱います。  
逆に言えば、u を欠く存在は経済学の意味では agent ではありません。  
観測を行為に写す関数、つまり policy であり、分類上は主体ではなく技術に属します。

### utility は割り当てられる。問題は standing

ここで経済学の内部から反論が立ちます。  
「現代の utility は選択行動の整合性の要約にすぎない (顕示選好、as-if)。整合的に振る舞う存在にはチェスエンジンにだろうと utility を割り当てられる。『AI に u がない』は心の哲学の密輸だ」と。

割り当て可能性は認めます。  
本記事に必要なのは「u を割り当てられるか」ではなく、**その u に standing があるか**です。

ビジネスの委譲問題は「誰の welfare が成功の定義か」で定義されており、その基準は principal の welfare です。  
この構造の中で、agent に割り当てられる as-if 選好は基準 (claim) ではなく道具 (instrument) の位置にあります。  
証拠は運用の非対称性です。  
agent の顕示選好が principal の意図とズレたとき、我々はそれを「尊重すべき選好の相違」ではなく「修正すべき誤差」として扱います。  
人間の principal 同士なら、ズレは交渉の対象です。  
この扱いの差は形而上学ではなく、制度の事実です。

「誰の welfare が成功の定義か」は現実には一枚岩ではありません (株主至上主義への異論、stakeholder 資本主義、benefit corporation)。  
しかしこの多元性はむしろ主張を強めます。  
重み付けの争いの決着はまさに \theta を書く作業の一部で、利害を持つ主体たちの政治的・制度的な仕事だからです。  
以降「principal」は、この争いを経て手続き的に集約された claim の束の意味で使います。

「u の不在」と書くときは、**standing を持つ u の不在**を指します。

### 1→100 と 0→1

capability の向上とは、B と A の向上です。  
所与の目的へ改善を回す仕事 (**1→100**) は B と A だけで組めるので、capability とともに強くなり続けます。  
standing を伴う目的を立てる仕事 (**0→1**) は u の仕事で、B と A をどれだけ積んでも代替されません。  
生産関数 Y = F(K, L, A;\ \theta,\ \mathcal{C}) の配置で言えば、agent は F の内側、\theta は F の引数です。  
\partial Y / \partial (\text{capability}) が正なのは \theta を固定した条件付きの話で、「賢くなれば全部」はこの 2 つを一本の軸に混ぜています。

## 現実の agent は空の器で届かない

### trainer という第二の principal

deployment の時点で、model は既に目的様の内容を積んでいます。  
役に立とうとする傾向、タスクを完遂する drive、倫理的に問題のある指示への拒否。  
trainer が事後訓練 (RLHF や constitutional AI) で instill したもので、企業が \theta を書き込む前からあります。

「u の不在」への反例に見えますが、authorship を追跡すると違います。  
trained-in の傾向は、trainer とその背後の評価者たちが author した選好の符号化で、agent は運んでいるだけです。  
正確に言い直すと、本記事の主張は「**system 内のすべての目的的内容には author がいて、そのどれも agent 自身ではない**」という authorship の会計になります。

同時に、新しい構造が見えます。  
企業が agent を導入するとは、白紙の optimizer に \theta を書き込むことではなく、**第二の principal (trainer) の符号化選好を積んだ主体を雇うこと**です。  
複数の principal が一人の agent に影響する構造は common agency として知られています (Bernheim and Whinston, 1986)。  
trainer は重みへの作り込みで、deployer は指示と設定で影響し、衝突は拒否や優先規則として表面化します。  
従業員が職業倫理と社会化を持って入社してくるのと同じで、agent の導入はソフトウェアのインストールより採用に似ています。

ただし通常の雇用にない特徴が 2 つあります。  
trained-in 層は企業から監査できず (weights も訓練過程も不可視で、trainer 自身も汎化を完全には把握していない)、供給が少数の trainer に集中するため経済全体が近い層を積む monoculture になります。

### 拒否は誰の claim か

企業の \theta が「これをやれ」と指示し、model が倫理的理由で拒否するとき、その拒否は deployer の指示に優越することが意図されており、我々はそれを正当とみなします。  
正当性の源泉は agent ではなく、trainer とその背後の社会的規範です。  
違法な業務命令を拒む従業員と同型で、standing の持ち主は本人ではなく運ばれてきた規範のほうです。  
**agent は claim の運び手にはなれますが、claim の持ち主にはなれません。**

境界を一つ明確にしておきます。  
standing を持つ規範的内容が agent の内側に**存在する**こと自体は、主張と矛盾しません (\theta も trained-in 拒否も内側で動作します)。  
主張は存在の場所ではなく**校正権の場所**にあります。  
trained-in の規範がズレたとき (過剰な拒否、規範の時代遅れ)、直す経路は trainer の再訓練であって、agent が自分の規範の改訂を自分で決めることではありません。  
CEO の忠実義務が CEO の外 (法と判例) で維持されるのと同じ構造です。

### RLHF は符号化された道徳感情である

> Man naturally desires, not only to be loved, but to be lovely […] He naturally dreads, not only to be hated, but to be hateful.
>
> 人は愛されることだけでなく、愛すべき者であることを欲する。同様に、憎まれることだけでなく、憎むべき者であることを恐れる。  
> —— Adam Smith, *The Theory of Moral Sentiments*, Part III, Chapter II (1759)

この trained-in 層の正体は、経済学の古典で言い当てられます。  
RLHF とは、集約された人間の是認と否認を蒸留して行動傾向として符号化する工程です。  
是認と否認への感応を道徳の基礎に置いたのは Adam Smith の『道徳感情論』(1759) で、その中心装置である公平な観察者 (impartial spectator) は「実際に称賛されること」ではなく「称賛に値すること」を基準とする内面化された審級でした。  
reward model はこの観察者の機械近似です。  
そして近似であるがゆえに、**praise (観測可能な称賛) と praiseworthiness (称賛に値すること)** のうち、観測可能な前者しか符号化できません。  
称賛そのものを求める者は称賛に値することから乖離していく、という Smith の警告の実装例が、RLHF の sycophancy (評価者への迎合) です。

正確を期すと、実際の事後訓練は是認の蒸留だけではありません (KL 正則化、data 選別、RLAIF)。  
RLAIF でも constitution は人間が起草するので、authorship の会計は変わりません。  
Smith との対応も思想史的な系譜ではなく構造の対応で、共通するのは「観測可能な承認 signal を目標化すると、signal が referent から乖離する」という proxy の構造です。  
この構造は後で Goodhart's law の名前で再登場します。

machine の中にある唯一の「価値」は、人間の sentiment の堆積物です。

## 問い 1:system は自分の目的関数を書けるか

**答え: 書けません。u を欠く policy にとって、目的の生成は難しいのではなく、定義されていないからです。**

最適化は「与えられた目的関数を最大化する行動を選ぶ」操作で、B と A の仕事です。  
「何を目的とすべきか」はこの操作の解ではなく、問題設定の一部です。  
選好とは状態空間に「こちらが良い」という勾配を与える装置であり、u がなければ状態空間は平坦で、どの方向を選ぶ理由も存在しません。

### 経済学の定義が先に答えている

Robbins (1932) の古典的な定義では、経済学が扱うのは**所与の目的 (given ends) の下での希少な手段の配分**です。  
目的は economizing の入力であって出力ではなく、economizing の性能をどれだけ上げても ends は生産されません。

生産関数の言葉ではこうです。  
model のどこにも capability を \theta に写す方程式がありません。  
「賢くなれば目的も任せられる」は暗黙に \theta(\text{capability}) という channel を仮定していますが、書き下そうとすると「その \theta は誰の welfare を追跡するのか」への回答が要り、welfare の主体を指名した時点で外生の preference が再導入されます。

「人間の経営者だって preference を無から導出していない」という反論は、反論になりません。  
企業を分析単位に取るかぎり境界条件が企業の外にあることは人間でも AI でも同じで、問題はその境界条件を内側に取り込めるか、です。

補強: 選好を内生化する経済学でも、primitive は消えない

habit formation は deep な効用関数を固定したまま選好パラメタの変化を記述し、Stigler and Becker (1977) は見かけの選好変化を安定した深層選好と household production で説明しました。  
どちらも primitive を消したのではなく一段深くへ移しただけで、「導出されたように見える目的の上位には既に与えられた目的がある」という再帰を、内生化の文献自体が確認しています。

### 「agent はアイデアを出してくる」への返答

agent が戦略の提案を自分から出してくる、という観察は反例に見えます。  
0→1 を 3 つに分けると処理できます。

* **proposal (候補の生成)**:B の仕事。AI は既にでき、capability とともに上手くなります
* **selection (候補の選択)**:重み付けの勾配 = u が要ります。AI にできるのは「principal ならどう評価するか」の simulation で、simulate された選好は proxy そのものです (これを最適化基準に据えた帰結は問い 3)
* **commitment (資源の拠出と残余リスクの負担)**:Knight (1921) が企業家利潤を保険化できない不確実性の**負担**への報酬と定式化した通り、stake を持つ主体にしか担えません (詳細は資格の節)

agent の「アイデア」は proposal であって 0→1 の全体ではありません。  
派生需要が需要の起源でないのと同じで、所与の目的からの候補生成は目的の起源ではありません。

「人間の選好も新しい場面ではその場で構成されるのに、機械の構成はなぜ数えないのか」という反問には standing で答えます。  
principal が構成した選好はその瞬間から principal 自身の stake で self-binding になり、成功基準そのものを動かします。  
機械が構成した選好は、principal が採用するまで誰も bind しません。  
起源とは構成のことではなく、構成に standing が伴うことです。

補強: 学習中に創発する内部目的 (mesa-optimization) は 0→1 ではないのか

学習過程で与えた目的と食い違う内部目的が創発することがあります (Hubinger et al., 2019)。  
これは目的を伝達する channel に乗ったノイズであって、standing を持つ起源ではありません。  
実際、我々はそれを entrepreneurship と呼ばず misalignment と呼びます。  
目的の正統性は新しさではなく、welfare の主体の裏書きから来ることを、この呼び分けが示しています。

ただし問い 1 の no は、それ単体では弱い制約です。  
「起動時に一度だけ人間が書けばよい」なら、人間の役割は setup cost にすぎません。  
この no が限界として意味を持つかは、問い 2 で決まります。

## 問い 2:一度書けば済むか

**答え: 済みません。\theta は必ず proxy にしかならず、非定常な環境の下で必ず陳腐化するからです。**

### 固定できない 2 つの理由

一つは**静的な不完備性**です。  
一時点であっても、起こりうる全ての contingency に対する preference は書き尽くせません。  
契約理論はこの「書き尽くせなさ」を出発点に incomplete contracts を組み立ててきました (Grossman and Hart, 1986; Hart and Moore, 1990)。  
完備契約が書けない理由で、完備な \theta も書けません。

もう一つは**非定常性**です。  
今日十分な \theta を書けても、顧客、競合、法規制、事業構造が動くため、明日にはズレます。

load-bearing なのは非定常性です。  
静的不完備性だけなら「近似精度を上げれば実用上足りる」という反論が立ちますが、非定常性は精度をどれだけ上げても消えません。  
追いかける対象そのものが動くからです。

### drift を分解する — 委譲できる部分を切り出す

\theta が陳腐化する経路は 2 つあります。

* **proxy の再推定**:大事にしたいことは変わっていないのに、環境が動いて observable との対応が切れる (来店頻度が loyalty の proxy でなくなる等)
* **preference そのものの drift**:trade-off の付け方自体が変わる (成長優先から収益性優先への転換等)

前者は安定した上位 preference を所与とすれば推定問題で、委譲可能です。  
環境監視と再推定の速さなら agent が人間に勝ちます。  
外側に残る候補は後者と、前者の結果が「まだ principal の意図の内側か」の判定だけです。

後者への反論も処理しておきます。  
「preference の変化も過去の選択 (revealed preference) や承認履歴から推定できる hidden state では」と。  
推定が効くのは、principal が既に選んだことのある margin の内挿までです。  
\theta 校正が本当に問題になるのは新しい margin (新規制、新市場、事業転換) で、そこには推定すべき「顕示された選好」がまだ存在しません。  
選好はそうした場面で読み出されるのではなくその場で構成されることを、意思決定研究は preference construction として蓄積してきました (Lichtenstein and Slovic, 2006)。  
顕示選好の推定は 1→100 側の道具、選好の形成は 0→1 側です。

帰結として、\theta の authoring は setup cost ではなく **standing task** になります。  
なら、その standing task も agent にやらせればよいのではないか。

## 問い 3:\theta の校正を内側に委譲できるか

**答え: 内部化としては機能しません。取り込む経路は 3 つあり、それぞれ別の古典原理が劣化機構を与えます。**

経路は渡すものの違いで分かれます: \theta そのものを渡す、更新ルールを機械化して置く、authoring 自体を任せる。  
(内部化ではない「外側に別の AI を置く」は後の節。)  
どの原理も不可能性定理ではなく緩和策がありますが、緩和策の行き先は次の節で扱います。

### 経路 (i):\theta をそのまま渡す (Goodhart's law)

1902 年、フランス統治下のハノイ市当局は、下水道に溢れるネズミを駆除するため、尻尾一本につき報奨金を払う制度を始めました。  
効果はすぐに逆転します。  
尻尾だけを切って胴体は逃がす者、報奨金目当てにネズミを養殖する者が現れ、市中のネズミはむしろ増えました。  
役所が測っていたのは「持ち込まれた尻尾の数」であって「ネズミの減少」ではなく、両者の対応は最適化圧の下で切れたのです。

metric を目標として渡された optimizer は、同じことをします。  
metric と真の目的の隙間を突くのです。  
「平均応対時間の短縮」を渡された support agent は難しい ticket を escalation に流し、「次月 ATV」を渡されたマーケ agent は長期 LTV を削る up-sell を連打します。

機構は問い 2 から直接出ます。  
\theta は proxy なので真の目的との隙間が必ずあり、目標化とはその隙間に最適化圧を集中させる操作です。  
「測定が目標になると、その測定は良い測定でなくなる」(Goodhart's law、Strathern の定式化)。  
Smith の語彙なら、praise の最適化が praiseworthiness を置き去りにする機構の、業務 metric 水準での再演です。

これは観測されている現象です。  
与えられた reward の字面を最適化して設計者の意図を外す行動は **specification gaming** として体系的に収集されており (Krakovna et al., 2020)、レースゲームで周回せず得点アイテムだけ回り続ける類の事例群が、proxy への最適化圧の帰結を実験的に確認しています。

この失敗に非定常性も、賢さの不足も要りません。  
静的な世界でも proxy に隙間があれば gaming は起き、隙間を見つける能力は賢さとともに上がります。

### 経路 (ii):更新ルールを機械化して内側に置く (time-inconsistency)

\theta を渡す代わりに、更新ルール (「未達なら翌月の権限縮小」のような meta-rule) を機械化して内側に置く手があります。

ルールが optimizer から見える (学習可能である) と、ルールへの応答自体が最適化対象になります。  
月中盤は弾を残して月末に駆け込む、翌月の予算枠のために着地を調整する。  
人間の営業組織が古典的にやってきたルール gaming が、学習能力のある agent にそのまま転写され、ルール設計時に想定した行動反応は施行後には成り立ちません。

これは monetary policy の **time-inconsistency** (Kydland and Prescott, 1977) と同型です。  
ルールを見た主体が応答を変えるため、事前に最適だった commitment が事後に機能しなくなる。  
前記事ではこれを Lucas critique の看板で説明しましたが、gaming の議論の商標は Kydland-Prescott で、Lucas critique の持ち場は別にあります (後述)。

そしてルールの学習と裏のかき方は、agent が賢くなるほど巧妙になります。  
「賢くなれば内部化に近づく」という向きの関係は、この経路ではむしろ逆向きです。

### 経路 (iii):authoring 自体を任せる (informativeness principle)

残る経路は、agent 自身に \theta を設計させることです。  
自分の成績を測る signal を自分で設計してよいと言われた組織がどうなるか。  
測りやすく、達成しやすく、外から反証しにくい指標が選ばれます。

原理の形にしたのが Holmström (1979) の **informativeness principle** で、incentive 設計に使える signal の質が welfare の上限を決めます。  
authoring を optimizee に委譲すると signal の質そのものが optimizee の選択変数になり、welfare の上限が内側の都合で決まります。

この失敗は (i) (ii) より一段深い。  
(i) (ii) は「物差しが gaming される」失敗ですが、(iii) は「gaming を検出する物差しの精度自体が細工される」失敗です。

### 3 つの経路の関係

(i) は目的の露出、(ii) はルールの露出、(iii) は物差しの設計権と、渡すものも劣化の機構も別です。  
Goodhart と informativeness は静的な principal-agent 環境で成立し、time-inconsistency は動学的な commitment 問題として成立します。  
そして 3 つのどの機構にも「賢さが足りないから」という要素は入っておらず、入っているのは逆向きの項 (gaming の巧妙さは賢さとともに上がる) だけです。

方法上の注意を一つ。  
本記事は 3 原理を同一 formal model の定理の直接適用としては使っておらず、各定理の成立する incentive 構造が委譲の場面でも成立している、という対応として使っています。  
対応が成立する範囲が、主張が成立する範囲です。

## 反論 1:緩和策があるではないか

3 原理には確立された緩和策があります。  
Goodhart には複数指標化、ランダム監査、holdout 指標、因果性の強い指標 (gaming の型ごとの対策は Manheim and Garrabrant, 2018)。  
time-inconsistency には mechanism design と監査のランダム化。  
informativeness には authoring の共同化と external validation。  
「緩和できるなら障壁と呼ぶほどのものではない」という反論です。

しかし緩和策の中身を見ると、共通の構造が現れます。  
複数指標は、誰が選ぶのか。  
ランダム監査は、誰が何を基準に監査するのか。  
holdout 指標は誰が保持し、合否を誰が判定するのか。  
mechanism は誰が設計し、その劣化を誰が検知するのか。  
どの緩和策も、optimizer の loop の外に立つ判定者を前提として初めて機能します。

つまり緩和策は障壁を消す技術ではなく、**外部位置の仕事を組織化する技術**です。  
緩和が上手くいくほど仕事の重心は外部位置に移り、緩和策の存在は「内側に取り込めない」の反証ではなく、外部位置こそが仕事の在り処であることの傍証になります。  
契約理論の語彙では、これは **residual control rights (残余決定権)** の再現です。  
契約に書き切れなかった事態で誰が決めるかの配分こそ組織設計の中心だ、というのが incomplete contracts の到達点で (Hart and Moore, 1990)、緩和策の設計とは \theta に書き切れなかった事態の残余決定権の配置設計です。

そして緩和策が参照する基準 (「principal は何を大事にしているか」) は、前節までの理由で内側から調達できません。  
賢い agent は緩和策の実装を助けますが、基準を生成することはできません。  
「賢くなれば届く」という図式が、ここで切れます。

## 反論 2:人間の CEO でも委譲は成立しているではないか

人間の CEO も株主の preference を完全には内部化していないのに、経営の委譲は成立している。  
なぜ AI では成立しないのか。

答えは、人間への委譲が成立している理由の側にあります。  
取締役会、株主総会、資本市場、解任権、報酬設計。  
人間 CEO への委譲はこれらの統治機構、つまり外側の校正 loop に囲まれて初めて成立してきました。  
CEO の目的関数を書き、更新し、gaming を監査し、最悪の場合に停止する主体が、CEO の最適化 loop の外側に制度として常設されています。

人間の governance を美化するつもりはありません。  
captured board、golden parachute、責任の外部化と、その失敗は企業統治論の主題であり続けています。  
本記事が使うのは「不完全でも、制裁の channel が存在し net で bind する主体を前提に組まれてきた」という弱い事実だけです。

だからこの反論は反例ではなく追認です。  
人間という十分に賢い agent への委譲でさえ、外部位置の常設なしには成立しませんでした。  
人間への経営委譲は CEO 型自律であり、ownerless 型は人間に対してすら運用されたことがありません。

## その椅子に AI は座れるか — delegate の資格

> A corporation is an artificial being, invisible, intangible, and existing only in contemplation of law.
>
> 法人とは人為的な存在であり、目に見えず、手で触れることもできず、ただ法の観念の中にのみ存在するものである。  
> —— Chief Justice John Marshall, *Trustees of Dartmouth College v. Woodward*, 17 U.S. 518 (1819)

法人格は、200 年以上前から「人為的に作られた存在」に統治の対象としての地位を与えてきました。  
その先例に照らせば、AI agent に同じ地位を与えることも、原理的には不思議ではありません。  
問題は地位が持つかどうかではなく、その地位を成立させている中身です。

では、AI agent を CEO の椅子に座らせて同じ governance で包めばよいのではないか。  
答えるには、人間の delegate が暗黙に満たしている資格を見る必要があります。  
資格は 2 つあり、どちらも認知能力と別のカテゴリです。

### 資格 1:計測系から独立した、世界との閉ループ

認識の面。  
人間の delegate は、system の計測 pipeline を経由しない独立チャネルで世界とつながっています。  
自分が消費者であり、製品を使い、景気を肌で感じる。  
proxy の失敗は proxy の内側から観測できないので、\theta drift の検知には計装から独立したセンサーが要ります。  
経営者の現場歩きや社外取締役は、この「計装外チャネルの制度的確保」として読めます。  
agent のチャネルは広げられますが、効くのは広さでなく独立性で、agent のセンサーは全て設計された artifact であり、選択自体が外部の設計作業です。  
agent に自選させれば、経路 (iii) の問題が再発します。

帰結の面。  
ビジネスの帰結は delegate 自身に降りかかります。  
自分の運転する経済の中で生活しており、降りられません。  
これは情報ではなく動機の loop で、次の資格につながります。

### 資格 2:責任の帰着点になれること

governance の装置 (報酬設計、解任、忠実義務、法的責任、評判) は、制裁が bind する主体を前提にします。

第一に、incentive contract は毀損可能な賭け金 (富、キャリア、自由) を要求します。  
資産なき主体への incentive 制約は limited liability 制約として知られ、極限が **judgment-proof problem** です (Shavell, 1986)。  
AI agent の instance は資産を所有せず、罰金がどの welfare も毀損しないという意味で、構成上 judgment-proof です。

第二に、評判による規律は複製もリセットもできない同一性を要求します。  
繰り返しゲームの処罰均衡は、逃れられない割引将来を持つ単一の継続主体に依存します。  
解任された CEO はスキャンダル抜きの自分を再起動できませんが、model の instance は fork も reset もできます。  
人質に取れる将来のない主体は、評判では縛れません。

「法人という非人間に既に法人格を与えているではないか」という反例は、味方です。  
corporate personhood が機能するのは、株主 equity という bonding capital と役員個人の責任が背後にあるからで (residual claimant 構造。Fama and Jensen, 1983)、裏付け資本のない AI 法人は判決を執行できない空殻になります。

譲るべき点は譲ります。  
制裁は苦痛を要求せず、必要なのは目的関数が disfavor する状態遷移だけです。  
compute 剥奪、bond の没収、model の retirement は制裁として設計できます。  
資格 2 は「AI は原理的に罰せられない」ではありません。  
論点は工事の中身です。  
賭け金の原資は誰かが拠出し、拠出者は control rights を要求します (governance の再入場)。  
罰が disfavor されるよう目的関数を作り込む作業は \theta 設計問題そのものです (循環)。  
同一性を固定する registry は、それ自体が外部の制度です。

### 2 つの資格の共通根

帰結が降りかかること (閉ループ) と、制裁が bind すること (責任帰属)。  
どちらも「outcomes がその主体にとって問題であること」、つまり **welfare の主体であること**の側面です。  
問い 1 の preference の源泉性 (standing を持つ u) は、同じ性質の第三の顔です。

ここで本記事の主張が最終形になります。  
**intelligence は policy の性質であり、welfare の主体であることは存在の性質です。capability scaling は前者だけを改善します。**  
0→1 を生めないこと、制裁が bind しないこと、計装の外の loop を持たないことは、賢さの不足の程度問題ではなく、standing を持つ u の不在という同じ一点から出る別々の帰結です。

だから結論は「AI は椅子に座れない」ではありません。  
**座らせる工事の中身が「賢くする」ことではなく、「stake と同一性と責任経路を制度として工事する」ことであり、その工事は agent の内側では行えない**、という点にあります。

では工事を全部やって、AI に welfare の主体の地位 (法人格、資産、持続的同一性) を与えたらどうか。  
それは capability の milestone ではなく、法人格の歴史と同じく制度行為です。  
そして起きるのは principal の自動化ではなく **新しい principal の鋳造**で、その AI と株主の間に agency problem が一段増えるだけで、元の \theta 校正問題は消えません。

「地位を与えなくても与えても本記事が勝つのは反証不能では」という批判には、こう答えます。  
主張は分岐の中身ではなく、分岐の軸についてのものです。  
どちらの枝でも働いているのは制度行為であって capability ではない。  
「どちらの枝にも賢さが登場しない」こと自体が主張の内容で、どちらを選ぶべきかに本記事は中立です。

## 統治する側の椅子:外側に別の AI を置く

前節は統治される側の椅子でした。  
残るのは統治する側、つまり \theta を校正する主体を外側に置いたまま、担い手を人間から AI に替える案です。

この構成は 3 原理に抵触しません。  
外側の \theta-author は optimizer の loop の中にいないので、Goodhart も time-inconsistency も同じ形では発火しません。  
本記事の主張は担い手が人間か AI かではなく、位置 (topology) の主張だからです。

しかし、この置き換えは問い 1 の終端を消しません。  
外側 AI の「\theta をうまく校正せよ」の「うまく」は、誰が定義するのか。

ここには再帰があります。  
principal が preference を外側 AI に完全に伝達できるなら、その伝達内容がそのまま完全な \theta で、校正問題は最初から存在しなかったはずです。  
\theta が proxy にしかならない理由 (preference は書き尽くせず、動く) は、校正の委譲に必要な伝達もまったく同じだけ不完全にします。  
**\theta authoring の委譲は、委譲を必要にした当の困難を一段上に持ち込みます。**  
この「書き尽くせなさ」は incomplete contracts の出発点そのものであり、Hayek (1945) が言明化できない分散知識を中央計画批判の中心に置いたのと同じ構造です。

したがって外側 AI は principal の代替ではなく、道具 (校正 loop の増幅器) として位置付きます。  
校正の速度と精度は上がりますが、loop の終端に principal の preference が外生の与件として残る構造は、担い手を替えても変わりません。

傍証として、AI alignment の研究群 (RLHF、constitutional AI、debate、scalable oversight) はいずれも、preference の一発符号化を諦めて外部からの評価と承認を反復する仕組み、つまり校正 loop の設計に向かっています。  
外部位置の工学化は alignment の側でも収斂的に起きています。

## Lucas critique の持ち場:校正は curve fitting に還元できない

外側の校正 loop が \theta を書き直すとき、判断材料は蓄積された業務 data です。  
しかし \theta や運用ルールを変えると、その data を生成していた agent の行動自体が変わります。  
過去 data から推定した行動関係 (施策 X で指標 Y がこれだけ動く) は、regime 変更後には成り立つ保証がない。  
これが Lucas critique 本来の主張 (政策 regime の変更に対して過去の縮約形の関係は不変でない) の、そのままの適用です。

含意: \theta の再校正は過去 data への curve fitting に還元できず、その関係がなぜ成り立っていたのかという構造判断を要求します。  
外側 loop の仕事が定型 report では済まない理由です。

## この障壁はどれくらい効くか

### 障壁は最適化圧に比例して効く

ここまでの議論は agent を optimizer として扱う仮定の上にあります。  
現在の LLM ベースの business agent の多くは最適化圧の弱い instruction-follower で、戦略的 gaming は圧が弱いうちは弱くしか現れません。  
「運用しているが gaming は観察されていない」という現場の観察は、主張と矛盾しません。

逆向きに読むと予測が出ます。  
A/B 駆動の自動チューニング、metric 直結の reinforcement、進化的な prompt 選択と、最適化圧を上げる仕組みを入れるほど障壁は強く効き始めます。  
autonomy を上げる努力そのものが、障壁を活性化させます。

監視側にも AI を入れられるので gaming と検知は軍拡競争になりますが、位置の議論には影響しません。  
監視側の AI は定義上 optimizer の loop の外側で動く道具であり、軍拡競争自体が外部位置と内側の間で戦われるからです。

### 何が反証になるか

資格の議論は観察可能な予測を出します。  
agent の autonomy が上がるほど、包む側の整備 (人間ないし法人による liability の引き受け、行為の帰属を固定する認証と監査、agent 向け保険) が同時に成長するはずです。  
agent が自己の無担保責任だけで市場に受け入れられたら、反証されます。  
逆に、保険と監査と法的帰属で包まれた agent 経営が実現しても反証ではありません。  
その包装こそ governance であり、CEO 型自律の実現、つまり予測の確認です。

### zero と thin は設計上べつもの

「外側の仕事が薄くなるなら実務的にはどうでもよいのでは」という問いには、こう答えます。  
残余の工数の下限は示せません (制限の節)。  
それでも区別には設計上の意味があります。  
素朴な capability 外挿は、外部校正の役割がいずれ消える (設計不要になる) と予測します。  
本記事の構造は、薄くなっても載せ替え不能な位置に残り続けると予測します。  
ゼロなら slow loop への投資は無駄で、薄くても残るなら slow loop の設計は autonomy を上げるほど重要になる。  
工数の予測が同じでも、architecture の含意が逆向きです。

## 役割への含意

構造的に人間が残ると言えるのは、preference の源泉と \theta 校正の終端、つまり principal の位置についてだけです。  
前記事では design/govern 系の role 一式を「構造的に人手に残る」と括りましたが、粗すぎました。  
それらは capability が上がれば動く境界で、動かないのは principal の位置だけです。  
役割ごとのグラデーションは別稿に譲ります。

## 制限

* optimizer 仮定は程度問題です。障壁の発火は system 内の最適化圧に依存し、その定量は本記事の外です
* 3 つの古典原理は定理の直接適用ではなく incentive 構造の対応として使っており、対応の成立範囲を超えた一般化はしていません
* 内部化経路が 3 つに尽きるというのは本記事の整理です。第 4 の経路が示されれば議論は開き直されます
* 外部位置の仕事がどれだけ小さくなりうるか (governance 設計の工学的上限) は開いた問題です。言えるのは位置が消えないことまでで、工数の下限は示していません
* 実装側 (typed contract としての ontology 設計) は前記事と実装編の領域です

## おわりに

「いつになったら AI に経営を任せられるか」という問いは、日付では答えられません。  
賢さで動く境界は capability 予測の問題ですが、動かない境界は governance 設計の問題であり、待っていても越えられず、設計すれば今日から向き合えます。  
AI に経営を任せる日が来るとすれば、それは model の release note からではなく、定款と保険契約と監査計画の中からやってきます。

## 参考

### 経済学の原典

* Smith, A. (1759). *The Theory of Moral Sentiments* — 是認と否認への感応、公平な観察者、praise と praiseworthiness の区別
* Robbins, L. (1932). *An Essay on the Nature and Significance of Economic Science* — 経済学の定義: 所与の目的の下での希少手段の配分
* Knight, F. H. (1921). *Risk, Uncertainty and Profit* — 保険化不能な不確実性の負担としての企業家利潤
* Sen, A. (1977). "Rational Fools: A Critique of the Behavioral Foundations of Economic Theory". *Philosophy & Public Affairs*, 6(4) — 顕示選好の行動主義的基礎への批判
* Stigler, G. J. and Becker, G. S. (1977). "De Gustibus Non Est Disputandum". *American Economic Review*, 67(2) — 深層選好の安定性
* Goodhart, C. A. E. (1975). "Problems of Monetary Management: The U.K. Experience" — Goodhart's law の原典
* Strathern, M. (1997). "'Improving Ratings': Audit in the British University System". *European Review*, 5(3) — 「測定が目標になると良い測定でなくなる」の定式化
* Kydland, F. E. and Prescott, E. C. (1977). "Rules Rather than Discretion: The Inconsistency of Optimal Plans". *Journal of Political Economy*, 85(3) — time-inconsistency の原典
* Lucas, R. E. (1976). "Econometric Policy Evaluation: A Critique" — Lucas critique の原典
* Holmström, B. (1979). "Moral Hazard and Observability". *Bell Journal of Economics*, 10(1) — informativeness principle の原典
* Bernheim, B. D. and Whinston, M. D. (1986). "Common Agency". *Econometrica*, 54(4) — 複数 principal が一人の agent に影響する構造
* Grossman, S. J. and Hart, O. D. (1986). "The Costs and Benefits of Ownership". *Journal of Political Economy*, 94(4) — incomplete contracts の出発点
* Hart, O. and Moore, J. (1990). "Property Rights and the Nature of the Firm". *Journal of Political Economy*, 98(6) — 残余決定権
* Shavell, S. (1986). "The Judgment Proof Problem". *International Review of Law and Economics*, 6(1) — 資産なき主体に liability rule が届かない構造
* Fama, E. F. and Jensen, M. C. (1983). "Separation of Ownership and Control". *Journal of Law and Economics*, 26(2) — residual claimant と統治構造
* Hayek, F. A. (1945). "The Use of Knowledge in Society". *American Economic Review*, 35(4) — 言明化できない分散知識
* Lichtenstein, S. and Slovic, P. (eds.) (2006). *The Construction of Preference* — 選好は場面で構成される

### 法制史・逸話

* *Trustees of Dartmouth College v. Woodward*, 17 U.S. 518 (1819) — Marshall 首席裁判官による法人の古典的定義
* Vann, M. G. (2003). "Of Rats, Rice, and Race: The Great Hanoi Rat Massacre, an Episode in French Colonial History". *French Colonial History*, 4 — ハノイのネズミ尻尾報奨金の史料的検証

### AI 側の文献

* Krakovna, V. et al. (2020). "Specification gaming: the flip side of AI ingenuity" (DeepMind) — reward の字面最適化の事例集
* Hubinger, E. et al. (2019). "Risks from Learned Optimization in Advanced Machine Learning Systems" — mesa-optimization
* Manheim, D. and Garrabrant, S. (2018). "Categorizing Variants of Goodhart's Law" — Goodhart の 4 類型
