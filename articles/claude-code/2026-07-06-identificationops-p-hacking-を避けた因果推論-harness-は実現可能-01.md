---
id: "2026-07-06-identificationops-p-hacking-を避けた因果推論-harness-は実現可能-01"
title: "IdentificationOps: p-hacking を避けた因果推論 harness は実現可能か"
url: "https://zenn.dev/takyone/articles/identificationops-2026-07"
source: "zenn"
category: "claude-code"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "LLM", "Python"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

## はじめに

「LLM agent は因果推論を正しくできるか」という問いは、能力の問題として framing されがちです。  
この framing の下では、より賢い model が出るたびに問題は解決へ近づくはずです。

agent の能力不足による誤りは今後も起こります (本記事自身、自分の実験の測定バグと誤った結論を 1 件ずつ見つけて直しています)。  
それでも、能力の向上だけでは埋まらない別の欠落が今の agent-native な分析にはあります。  
agent に分析を任せると、探索と検定が同じ loop の中で回ります。  
仮説はデータを見た後に湧き、分析計画は結果を見た後に変わり、検定は何度でも走ります。  
「固定サンプルを 1 回だけ検定する」前提で設計された p 値の契約は、この loop の中では初めから成立していません。  
人間の研究者であれば pre-registration や査読が外側から縛りますが、agent の分析 loop には対応する外部拘束がありません。  
agent の行儀に期待しない限り、agent-native な分析は構造的に p-hacking です。

であれば、標準化すべきは「agent がどう分析を実行するか」ではなく、「どの実行結果を licensed な主張として認めるか」という契約です。  
本記事では、この契約づくりの規律を **IdentificationOps** と呼びます。  
MLOps が model の運用を、DataOps が pipeline の運用を規律化したように、IdentificationOps は identification strategy の宣言から、その宣言が licensed な主張になるまでの手続きを運用に落とします。  
estimation でも inference でもなく identification を冠するのは、規律化の対象が「どう推定するか」ではなく「何を仮定し、何を主張してよいか」だからです。

以下では、この規律の最初の実装である因果推論プロトコル **explysis** (v1 は操作変数法 / LATE に限定) について、設計、現実の研究 loop との対応、実データ (Card 1995) での 1 周、合成データでの誤報率の実測までを報告します。

## 本記事の要点 (TL;DR)

* 実証研究の規範 (identification の議論、事前登録、robustness、査読、replication) を machine-enforceable な契約に転記する規律を IdentificationOps と呼び、その最初の実装として explysis を設計しました
* 分析は **world** (型付きの仮定集合) と **estimand** (推定対象の汎関数) を宣言し、手法は catalog が引く対応で決まります (数学的に一意な導出ではなく、設計者が選んだ policy です)。estimator 名を書く場所がありません (Thesis A)
* agent の分析 loop は逐次的なので、fixed-n の p 値の代わりに append-only な **evidence ledger** で α 資産を会計します。強制するのは決定論的 CLI で、LLM 呼び出しはゼロです (Thesis B)
* Card (1995) の実データで Plan→Do→Check→Act を 1 周回しました。実装側と別 context で走る referee agent が、spec 側の証拠の oversell と、monotonicity 仮定への疑義をそれぞれ検出しました (後者が本物の違反か診断の偽警報かは §6 の実験で測ります)
* 合成データで、プロトコルに正直に従った場合の claim rate を実測しました (簡易 closed-form 実装、regime 間比較用、参照実装値ではありません)。帰無の下での claim rate は naive / AR とも約 5% (strong IV) です。weak IV では F 単独では naive は壊れず、F×ρ (識別の弱さ × 内生性の強さ) の joint で naive 0.202 vs AR 0.052 に分かれました
* ρ は観測不能な構造誤差間の相関なので、「ρ が低ければ naive で十分」という結果を分析者は行動に変換できません。weak-IV-robust な推論を protocol rule として宣言させる理由がここにあります

上の claim rate は「プロトコルに正直に従った分析」のものであり、ledger を作り直したり不都合な run を破棄したりする行動まで含めた誤報率ではありません (§2 末尾と §7 で扱います)。

## 1. 設計: 実行ではなく契約を標準化する

### 先行プロジェクトとの違い

因果推論を agent で自動化する試みは既にあります。  
Causal-Copilot は自然言語 query から algorithm 選択、推定、解釈までを全自動化し、IV Co-Scientist は multi-agent で操作変数の候補を発見します。  
どちらも実行の自動化です。

explysis はこれらと直交していて、実行を自動化する代わりに実行の契約を標準化します。  
先例のパターンで言えば、計算の中身を標準化しようとした規格は、PMML のように定着しないか、ONNX のように限られた交換用途に留まりました。  
一方、契約を標準化した規格 (LSP、OpenAPI、dbt、MCP) は、それぞれの領域で職能ごと定着しています。  
dbt は SQL の semantics を発明せず、workflow の契約だけを固定して analytics engineering という職能を成立させました。  
explysis が dbt の位置に入るとすれば、成立させたい職能の側の名前が IdentificationOps です。  
実装言語 (R / Python / Julia) は規格の外に置き、interface と検証だけを規格に含めます。

### Thesis A: 手法名ではなく仮定を宣言する

分析の宣言 (spec) には estimator 名を書く場所がありません。  
書くのは world と estimand です。

world は統制語彙による仮定集合で、v1 では {relevance, exclusion, monotonicity, sutva, overlap, unconfoundedness} の 6 語だけを認めます。  
各仮定には `testable | partially_testable | untestable` の型が付き、testable なら診断 (diagnostics) の registry ID を、untestable なら根拠文献 (`argued_via`) を必ず紐付けます。  
estimand は LATE や ATE といった汎関数として宣言し、method とは区別します。

手法はこの宣言から一意に導かれる定理ではなく、宣言に対して catalog が引く対応です。  
仮定集合と estimand の組に対して許容される estimator と必須診断を列挙した **derivation catalog** (引用付きの lookup table) があり、たとえば {relevance, exclusion, monotonicity} + LATE の行は Wald / 2SLS に解決されます。  
同じ仮定集合の下でも LIML や Fuller、CLR といった代替の妥当な手法は存在するので、catalog は設計者が採用した policy であって、数学的に一意な導出ではありません。  
その代わりに、catalog に載っている行を選んだ以上は method 名を宣言から書かなくてよい、という約束です。  
診断の registry は数学的定義と引用を entry ごとに pin し、v1 では 8 entry に hard cap しています。  
定義の曖昧さを残すと「診断を実行した」という主張自体が検証不能になるので、hard cap は分析者の自由度を減らす代わりに規格側の判断が及ぶ範囲を明確にする trade-off です。  
9 個目の診断が必要になったときに何が起こるかは v0.2 以降の課題として残ります。

estimator 名を書く場所がなくなっても、分析者の自由度が消えるわけではありません。  
covariate\_adjustment の選択、AR の grid 解像度、robustness\_matrix の dimensions 構成、確証的 claim の書きぶりは、この宣言の別の場所に残ります。  
Thesis A が閉じるのは「method 名を先に決めて後から正当化する」経路であって、宣言全体を通じた自由度そのものではありません。

### Thesis B: evidence ledger が分析 loop を licensed にする

逐次的な分析 loop に対する多重検定の統制は、agent への指示文 (prompt) ではなく会計として実装します。

`exl` CLI (Python 製、決定論的、LLM 呼び出しゼロ) が append-only の ledger (prev-hash chain 付き JSONL) を管理します。  
`exl init` はデータを exploration / confirmation に分割し、confirmation 側の SHA-256 hash を ledger の genesis に封印します (機械化された blind analysis)。  
`exl spec lock` は spec の内容 hash を ledger に追記し、以後の書き換えを検出可能にします。  
確証的な主張は `exl ledger spend` で α 資産を支払ったものだけが成立し、残高ゼロでは CLI が拒否します。  
v0 の会計は固定 α 資産の spending (初期 0.05、earn-back なし) で、alpha-investing や e-process への拡張 seam を持ちます。

保証はすべて CLI の code 側に置き、agent 向け指示文の prose には置きません。  
prose の指示は agent が読み飛ばせますが、提出された ledger の内部整合性は読み飛ばせないからです。  
ただし hash chain が守るのは提出された 1 本の trail の中の書き換え検出だけで、そもそも trail を提出しない、あるいは不都合な ledger を丸ごと作り直すという ledger の外側の行動までは防げません (この限界は §2 で立ち返ります)。

この構成を agent 開発の語彙に載せ直すと、explysis の実体は **identification harness** です。  
test harness が対象 code を包んで入力と合否判定を機械側に固定するように、この harness は agent の分析 loop を包み、cell の列挙、成果物の受け取り、主張の合否 (licensed か否か) を機械側に固定します。  
IdentificationOps が職能の名前だとすれば、identification harness はその道具の形の名前です。  
ただし test harness の pass/fail と違い、この licensed は「正しい」の保証ではありません。  
後述の Card 分析では、未解決の referee 指摘を抱えたまま claim が licensed になっています。  
licensed は手続きを通ったことの印であって、真偽の判定ではないという点で、この analogy は途中までしか効きません。

### プロトコルの実体

抽象論だけでは契約の粒度が伝わらないので、後述する Card (1995) の実 run から spec と ledger をそのまま抜粋します (注記と data\_contract は省略)。

```
design: iv_late

world:
  relevance:
    status: testable
    diagnostics: [effective_F, AR_confidence_set]
  exclusion:
    status: untestable
    argued_via: ["card1995#sec5"]
    diagnostics: [placebo_outcome]
    placebo_outcome_ref: dad_education
  monotonicity:
    status: partially_testable
    diagnostics: [first_stage_sign_by_subgroup]
  sutva:
    status: untestable
    argued_via: ["card1995#sec3"]

estimand:
  type: LATE
  treatment_ref: years_of_schooling
  outcome_ref: log_wage
  instrument_ref: nearby_4yr_college
  covariates: [experience, experience_sq, black, region_south, urban, urban_age14]
  covariate_adjustment: linear

robustness_matrix:
  dimensions:
    controls: [base, +parental_education]
    sample: [full, black_only, nonblack_only]
    instrument_definition: [nearc4_any, nearc4a_public_only]

ledger_config:
  backend: alpha_spending_v0
  initial_alpha: 0.05
  matrix_cell_policy: descriptive_only
```

読み方を 3 点だけ。  
estimator 名はどこにもなく、wald\_2sls はこの宣言に対して catalog が引く対応の結果です。  
untestable と型付けた exclusion には、文献参照 (`argued_via`) と placebo に使う列の binding が強制されます。  
robustness\_matrix は 2×3×2 = 12 cell に機械展開されます。

ledger は append-only の JSONL で、この run では 3 つの event だけが刻まれています (hash と長文の reason は省略表記)。

```
{"seq": 0, "event": "genesis",
 "confirmation_hash": "f40ac08f...", "confirmation_rows": 2107,
 "initial_alpha": 0.05, "prev_hash": null, "hash": "2d8fa4c4..."}
{"seq": 1, "event": "spec_locked",
 "content_hash": "8f106349...",
 "prev_hash": "2d8fa4c4...", "hash": "ec600983..."}
{"seq": 2, "event": "alpha_spend",
 "amount": 0.05, "remaining_alpha": 0.0,
 "artifact_ref": "est-confirmatory-late",
 "reason": "Confirmatory LATE claim ... referee の未解決 finding 2 件を明記 (後述)",
 "prev_hash": "ec600983...", "hash": "8a090b1f..."}
```

genesis が confirmation partition の封印、spec\_locked が宣言の固定、alpha\_spend が確証的主張の会計です。  
各 event は直前の hash を保持するので、途中の書き換えは連鎖ごと壊れて検出されます。

agent が提出する成果物 (artifact) も型付きです。  
DiagnosticResult (pin された定義 ID を持つ診断結果)、EstimateResult (推定値と区間)、RefereeReport、CodeBundleManifest (環境 lockfile、seed、入出力 hash) など 6 型があり、`exl artifact validate` が schema と相互参照 (診断 ID の実在、estimand との一致) を検査します。

### 検証は成果物に対して行う (proof-carrying analysis)

agent が書く推定 code は opaque な成果物として扱います。  
人間が code を読んで正しさを保証する代わりに、(a) spec の内部整合性 (仮定と診断と catalog 行の相互参照) を validator が検査し、(b) 報告される診断が pin された定義と一致するかを registry が固定し、(c) 推定 code そのものは LATE の真値を構成的に知っている合成 DGP の conformance suite に通します。  
conformance suite には「OLS を IV と偽った実装を必ず落とす」test が入っていて、これは suite 自身の unit test です。  
proof-carrying という名前は proof-carrying code からの借用で、数学的な証明を運ぶという意味ではありません。  
成果物が自分の検証材料 (宣言との整合、pin された定義への参照、conformance の通過記録) を同梱している、という意味の比喩です。

## 2. 現実の econometrician の loop を protocol に写す

このプロトコルは新しい統計手法を導入していません。  
写し取りの元は、実証系の econometrician が普段から回している研究 loop です。  
対応を並べると、protocol の各要素がどこから来たかが見えます。

| 研究者の loop | protocol での対応 | 何が変わるか |
| --- | --- | --- |
| 先行研究から identification strategy を仕立てる | `papers/` の抽出 claim と spec の `argued_via` 参照 | 引用が装飾から機械検査可能な参照に変わる |
| 仮定の棚卸し (セミナーで詰められる identification の議論) | `world` 宣言 (testable / untestable の型付け + 診断 binding) | 検定できない仮定ほど文献根拠の明示が必須になる |
| 推定対象の確定 (誰の、何の効果か) | `estimand` 宣言 | method 名を書く場所がなくなる |
| pre-analysis plan (RCT 文化の事前登録) | `exl spec lock` | ledger 内での順序が hash で検査できる (外部登録の限界は後述) |
| blind analysis という理想 | `exl init` の exploration / confirmation 分割と封印 | 規範が努力目標から既定値に変わる |
| first stage と F 統計量の確認 | diagnostics registry (`effective_F` は Montiel Olea–Pflueger 定義を pin) | 「F は見た」の F がどの定義かで曖昧にならない |
| robustness table 作り | `robustness_matrix` + `exl matrix expand` | 宣言した dimensions の内部では都合の良い cell だけ載せる自由が消える (全 cell 提出、dimensions 自体の選択は残る) |
| 学会の discussant、投稿後の referee | `ca-referee` (別 context の subagent、typed report) | 査読に相当する攻撃が loop 内の Check 工程に入る (制度的独立性の代替ではない、後述) |
| 「本命の結果は 1 本」という規範 | evidence ledger の α 会計 (`ledger spend`) | 規範が残高になり、超過した主張は CLI が拒む |
| replication package の公開 | CodeBundleManifest と conformance suite | 再現材料が事後の善意から成果物の型に変わる |

右列に共通するのは、規範の置き場所の移動です。  
人間の research loop でこれらを支えているのは、研究者個人の自制と、referee の目や事前登録の文化といった共同体側の実装です。  
agent の loop にはその共同体がないので、同じ規範を CLI の検査と artifact の型に転記します。  
IdentificationOps の新しさは統計にではなく、この転記先にあります。

転記のついでに位置が改善されるのが査読の工程上の位置です。  
人間の loop では referee は投稿後に一度だけ、しかも書き手の修正 incentive が働きにくい位置で会います。  
protocol では referee は PDCA の Check 工程として loop 内で走り、typed な report を artifact trail に残します。  
この位置の効果は §4 の実走で確認できます (spec の oversell を、書いた本人たちより先に referee が突きました)。

ただし移ったのは工程上の位置だけで、人間の査読制度が持つ独立性そのものではありません。  
学会の discussant や journal の referee は、専門性、書き手とは別の評判上の利害、複数人の合議、採否を左右する権限を伴う社会制度です。  
`ca-referee` は別 context の subagent であって、別の専門家でも別の利害を持つ主体でもありません。  
Check 工程として loop の中に置いたことの価値は §4 で確認した通りですが、それは人間の査読を機械が代替したという意味ではなく、書き手が見落としを自分で塞ぐ機会を loop の早い位置に用意したという意味です。

一方で、この写像に乗らないものも明示しておきます。  
第一に、identification の筋の良さ (どの instrument なら攻められるか) を見立てる直感は protocol の外に残ります。  
仮定を宣言するのは人間か、人間が sign-off した agent です。  
第二に、データを見て仮説を変える行き来は、禁止されるのではなく exploration partition の中に閉じ込められます。  
探索の自由は残り、licensed な主張になれないだけです。  
第三に、追試や論争といった学界の事後検証 loop は protocol の外にあります。  
ledger が保証するのは 1 つの分析の内側の会計までです。

なお表の左列は stylized な要約で、現実の研究 loop はここまで整然と工程に分かれていません。  
分かれていないからこそ、機械に写すときには層を分けて強制する必要がある、というのがこの表の読み方です。

### 多重検定と p-hacking への姿勢

多重検定への配慮というと、通常は「やらないことの誓約」(補正した、事前登録した) として書かれます。  
このプロトコルの姿勢は一段踏み込んでいて、p-hacking を禁止の対象からまず観測の対象に変えます。

p-hacking が厄介なのは、行為そのものより、最終成果物からそれが見えないことです。  
Gelman と Loken が garden of forking paths と呼んだように、公表された 1 本の分析 path の裏にあった分岐は論文からは数えられず、読者は「何回試したのか」を原理的に検証できません。

protocol の下では、この分岐が残ります。  
matrix の全 cell、探索側の診断、確証的 claim の spend 理由が typed artifact と append-only ledger に記録され、hash chain が事後の書き換えを壊します。  
すると「spec は結果より先に lock されたか」「展開された cell と提出された推定結果の数は一致するか」「α の総支出は初期資産の範囲内か」「confirmation を使ったと主張する artifact は封印 hash と整合するか」が、すべて trail への機械的な query になります。  
監視を性善説や抜き打ちの再解析にではなく、常駐の検査として置けるということです (現状は `exl artifact validate` と `exl ledger status` が部分を担い、trail 全体の相互参照検査は backlog にあります)。

観測可能になると、棄却の判断材料も揃います。  
CLI が保証できるのは trail の内部整合性の検査結果までで、それを理由に unlicensed な分析を実際に拒むかどうかは、査読者、社内の review gate、メタ分析の inclusion rule といった人間側の運用ルール次第です。  
それでも、判断材料が「疑う側が異常を立証する」から「主張する側が trail を示す」に変わる点は技術的な性質で、運用ルールを敷く組織にとっての導入コストを下げます。  
査読やメタ分析の側から見ると、分析単位の再現性 badge を機械検査可能な材料に置き換える動きに相当します。

ただし、この監視が届くのは提出された 1 つの ledger の内側までです。  
hash chain は提出された trail の書き換えを検出しますが、trail をそもそも提出しない、不都合な ledger を丸ごと破棄する、通る assumption や診断の組み合わせが見つかるまで spec を書き直して `init` からやり直す、といった ledger の外側の行動 (ledger shopping) は、内部整合性の検査では原理的に捕まえられません。  
線を引いておくと、新しいデータや新しい問いに対して新しい ledger を始めること自体は正常な運用です。  
shopping と呼ぶべきは、同じデータと同じ問いについて都合の良い結果が出るまで ledger を引き直す操作の方です。  
これを縛るには genesis hash を外部に登録する層 (公開 registry や timestamp authority、つまり事前登録簿の機械版) が必要です。  
v1 の scope 外ですが、封印を「外部に公表された hash」に差し替えるだけなので seam は既にあります。  
外部登録がない現状では、この protocol が保証するのは「遵守された分析の内部無矛盾性」であって、「遵守されたこと」そのものではありません。

## 3. 想定ユースケース

第一に、応用計量経済の replication と拡張です。  
IV design の論文を agent に再現させ、頑健性チェックを広げる作業は、agent が書いた code を人間が全部読む前提では割に合いません。  
explysis の下では、読む対象が code から artifact trail (宣言、診断、ledger) に変わります。

第二に、事業データでの施策効果検証です。  
「この施策は効いたか」を会話の中で逐次的に問い直す環境は、まさに多重検定が壊れる環境です。  
ledger の残高という形で「あと何回、確証的な主張ができるか」が明示されるので、探索は自由に、主張は有償に、という運用が成立します。

第三に、教材としての catalog です。  
仮定集合から estimator への対応は教科書では散文に埋まっていますが、catalog はそれを機械可読な表として明示します。

逆に、explysis は因果構造の発見 (causal discovery) を自動化するものではなく、estimator library でもありません。  
仮定を宣言するのは人間 (または人間が sign-off した agent) で、プロトコルはその宣言に対する誠実さだけを保証します。

## 4. 実ワークフロー: Card (1995) で 1 周回す

設計だけでは、referee や ledger が実際に仕事をするかは分かりません。  
そこで実データで PDCA を 1 周回しました。

なお、この節の診断値と推定値も簡易 closed-form 実装によるものです (§5 冒頭の caveat と同じ)。

### 題材とデータ分割

題材は Card (1995)、大学近接性を instrument として就学年数の賃金収益率を推定する古典です。  
データは著者本人の公式 replication archive から取得した N=3010 で、codebook の統計量と一致することを検証済みです。  
`exl init` が exploration 903 / confirmation 2107 に分割し、confirmation 側を hash で封印しました。

### instrument の強さと AR 信頼集合とは

Card の instrument は「4 年制大学の近くで育ったかどうか」です。  
これが手がかりとして使えるのは、近くに大学があるほど進学しやすい (就学年数と相関する) が、家庭背景等を調整すれば賃金に直接は影響しない (exclusion) と仮定できるからです。

**first stage** は、instrument (近接性) で treatment (就学年数) を説明する回帰です。  
この関係が弱い、つまり近接性が就学年数をほとんど説明しない場合、instrument は事実上「効いていない」に近く、2SLS の点推定はわずかな弱い変動だけに頼って計算されるため不安定になります (**weak instrument problem**)。  
**effective F** はこの first stage の強さを測る統計量 (heteroskedasticity-robust な F 統計量) で、Montiel Olea–Pflueger の臨界値 (instrument が 1 本なら約 23.1) を下回ると、通常の正規近似に基づく信頼区間の被覆は信用できなくなります。

**AR (Anderson–Rubin) 信頼集合** は、first stage の強さに依存せず正しい被覆を保つ代替の区間構成法です。  
発想は「点推定 ± SE」とは逆で、候補となる効果 β₀ を一つずつ試します。  
β₀ が真の効果だと仮定して Y から β₀×D を引いた残差が instrument と無相関に見えるなら、その β₀ は棄却しません。  
この検定を棄却しない β₀ をすべて集めた集合が AR 信頼集合で、instrument がどれだけ弱くても (弱いほど集合が広がるだけで) 正しい被覆を保つのが利点です。

### Plan: spec を書いて lock する

spec は §1 に抜粋したものです。  
estimand は LATE、instrument は 4 年制大学の近接性、共変量は経験年数とその 2 乗、人種、南部、都市部などの 6 個です。  
world の宣言では relevance を testable (診断: effective F と AR 信頼集合)、exclusion を untestable (placebo: 父親の教育年数)、monotonicity を partially\_testable (subgroup 別 first-stage 符号)、sutva を untestable としました。

instrument が弱いことは事前に分かっていたので、spec の段階で weak-IV-robust な経路 (AR 信頼集合) を宣言しています。  
数値を見る前に `exl spec lock` で内容 hash を ledger に固定しました。

### Do: 12 cell を機械的に全部走らせる

頑健性 matrix は仕様族 {base, +両親の教育} × sample {全体, black のみ, nonblack のみ} × instrument 定義 {全 4 年制, 公立のみ} の 12 cell です。  
`exl matrix expand` が cell を機械的に列挙し、agent は全 cell を exploration 側で実行して artifact として提出します。  
宣言済みの dimensions の内部では、気に入った cell だけ報告する cherry-picking は起きません。  
12 cell はすべて記述的な報告であり、α は消費しません。

診断の結果はこうなりました。

| 診断 | partition | 値 | verdict |
| --- | --- | --- | --- |
| effective F | exploration | 5.46 | fail |
| effective F | confirmation | 9.03 | fail |
| AR 95% 信頼集合 | exploration | [-0.301, 0.285] | 0 を含む |
| AR 95% 信頼集合 | confirmation | [0.017, 0.404] | 0 を除外 |
| placebo (父親の教育) | exploration | coef=0.060, p=0.813 | pass |
| subgroup 別 first-stage 符号 | exploration | black: −0.042 / nonblack: +0.489 | fail |

effective F は両 partition で臨界値 (1 instrument の 10% bias 基準で約 23.1) を大きく下回り、weak-IV regime であることを機械が検知しました。  
first-stage 符号診断は black subgroup で符号が反転しており、fail です。

### Check: referee agent の攻撃

**ca-referee** は実装側と別の context で走る subagent で、spec と artifact trail だけを見て攻撃し、型付きの RefereeReport を返します。  
今回は 5 本の攻撃 (high 2 本、medium 3 本) が出て、verdict は revise でした。

high の 2 本は relevance と monotonicity に向いています。  
relevance への攻撃は「レビュー時点の artifact には、0 を除外する weak-IV-robust な証拠がまだ無い」というもので、実際この時点で filed されていたのは 0 を含む exploration 側の AR 集合だけでした (扱いは次の Act 節)。  
monotonicity への攻撃は first-stage 符号の反転を突いたものです。  
符号反転は LATE の識別に使う「defiers がいない」仮定への疑義であり、spec の monotonicity 注記は subgroup 異質性に触れていませんでした。  
これが本物の defiers の証拠なのか診断自体の偽警報なのかは、この時点の artifact だけでは決められません (§6 で診断の誤報率を実測して評価し直します)。

medium の 3 本のうち 1 本は、書き手の筆の滑りを突いた検出でした。  
spec の注記は生相関 0.12 を、referee の家庭背景攻撃と同じ向きの「実在する非自明な signal」として書いていました。  
しかし実際に走った registry 準拠の placebo 診断 (共変量調整済み) は p=0.81 で帰無を棄却せず、spec 側はこの食い違いを一度も整理していませんでした。  
生の相関を、実際に走った診断の結果より強く語る、という spec を書いた側 (実装 agent と筆者) の癖を、別 context の referee が突いた形です。  
残る medium 2 本は、Card の within-region 論法がこの spec の狭い共変量集合でも生きるかという疑義と、母親の教育を使った追加 placebo の提案でした (後者はこの run で追加実行し、こちらも null)。

### Act: locked spec は書き換えない

診断の fail と referee の指摘を見た後で spec を直したくなりますが、それをやると「結果を見てから仮定を選び直す」という、このプロトコルが禁止したい操作そのものになります。  
spec は locked のまま残し、report に未解決のまま記載しました。  
relevance への攻撃は確証ステップ以前の artifact を対象にしていたため、確証側の AR 集合 (0 を除外) が出た後も verdict は revise のまま上書きしていません (referee が見ていない artifact で verdict を無効化しない)。

### 確証的 claim と ledger

確証的な主張は、封印されていた confirmation partition で 1 回だけ実行しました。

> 就学の収益率は正である。95% の weak-IV-robust (Anderson–Rubin) 信頼集合は [0.017, 0.404]。

点推定の精度を主張しない sign claim です。  
naive な正規近似の区間 [0.011, 0.289] の方が狭いのですが、effective F が 9.03 で fail している以上、その被覆は信用できません。

この [0.017, 0.404] は grid 上の受容点の凸包 (min と max) で報告されています。  
§6 で、weak IV の下では AR の受容域が単一区間にならないことがあり、その場合は凸包が誤った claim を生む場合があることを確認します。  
そこでこの confirmation partition についても、1 点直接評価 (grid を使わない AR(β₀) の評価) で受容域の形を検算しました。  
結果は 30001 点の grid 中 7737 点が連続して受容される、両端に接しない有界区間で、AR(0) の統計量は 4.64 (臨界値 3.841 を上回り 0 を棄却) でした。  
この confirmation partition では凸包と直接評価が一致しており、報告した区間は健全です。  
この検算は本記事の執筆時点で `analysis.py` に組み込み済みで、以後この worked example を再実行すれば、区間が bounded interval でない partition に当たった場合はコードが気づいて止まります。  
`exl ledger spend` で α 0.05 を全額支払い、残高は 0 になりました。  
spend の理由欄には、referee の high-severity 指摘 2 本 (relevance と monotonicity) が spec 改訂では解決されていないことを明記してあります。

black subgroup の符号反転が本当に monotonicity 違反なのか、それとも小 sample の偽警報なのかは、この 1 周では決められません (該当係数の t 値は −0.14 で、0 と区別が付きません)。  
この問いは §6 で診断そのものの誤報率として測ります。

## 5. 実験計画: 検定手続きの誤報率を測る

### なぜ合成データか、そして何を測らないか

ここで測るのは、宣言、診断、claim の書きぶりを 1 回だけ正直に決めた分析者が、帰無が真のときに約 95% の確率で黙るかどうかです。  
言い換えると、AR や naive Wald という検定手続き自体の size が、この protocol が想定する使い方の下で名目通りかという問いです。

これは Thesis B にとって必要条件であって、十分条件ではありません。  
検定手続き自体の size が名目からずれていれば、その上に ledger や hash chain をいくら積んでも会計は意味を持たないので、まずここを確認する必要があります。  
一方で、ledger を作り直す、通る結果が出るまで spec を変える、複数 run から都合の良いものだけ提出するといった、宣言や提出そのものを操作する行動の発生率はここでは測っていません (この論点は §2 の限界の節と §7 で扱います)。  
実データには ground truth がないので、上記の size の性質は真値を構成的に知っている合成 DGP でしか測れません。  
真陽性 (効果があるとき claim できるか) だけでなく、偽陽性、weak IV での挙動、診断自身の誤報率までを 1 つの実験で押さえます。

先に方法上の caveat を置きます。  
推定量と診断は Card の分析と同じ簡易 closed-form 実装 (numpy 直書き) で、registry が参照実装として pin している Montiel Olea–Pflueger や Andrews–Stock–Sun の実装そのものではありません。  
シナリオ間の比較には有効ですが、個々の数値は参照実装に置き換えると微動します。

### DGP

中核のデータ生成過程は、未観測交絡 U を共有する 1 instrument の線形系です。

\begin{aligned}
Z &\sim \mathrm{Bernoulli}(0.5), \qquad U \sim N(0,1) \\
D &= \pi Z + 0.8\,U + \varepsilon\_D, \qquad \varepsilon\_D \sim N(0,\ 0.5^2) \\
Y &= \beta D + 1.2\,U + \varepsilon\_Y, \qquad \varepsilon\_Y \sim N(0,\ 1^2)
\end{aligned}

π が instrument の強さ、β が真の効果です。  
β=0.08 は Card の点推定の近傍に合わせました。  
後で効いてくるのですが、この固定 loading は Y 方程式と D 方程式の構造誤差の相関 ρ を約 0.65 に暗黙のうちに固定しています。

exclusion 違反のシナリオでは、地域因子 L が instrument を決め (Z = \mathbf{1}\{0.8L + \eta > 0\})、違反時のみ L が Y に直接入り (+0.3L)、placebo 変数は常に P = L + noise で生成されます。  
monotonicity のシナリオでは、人口の 11% (Card の black subgroup 比率に一致、n≈220) を占める subgroup a の first-stage 係数 π\_a を本体 (π\_b=0.6) と別に動かします。

### シナリオ grid と測定量

| シナリオ | π | β | 何を測るか |
| --- | --- | --- | --- |
| S1 strong × effect | 0.5 | 0.08 | 検出力 |
| S2 strong × null | 0.5 | 0 | 偽陽性の統制 (Thesis B の直接テスト) |
| S3 weak × effect | 0.1 | 0.08 | 「分からない」と言えるか |
| S4 weak × null | 0.1 | 0 | naive な検定の size |
| S5 / S5c | exclusion 違反あり / なし | 0.08 | placebo 検出力と、その検出が証明しないこと |
| S6 / S6c | π\_a = −0.2 / 0 | 0.08 | 符号診断の検出力 / 誤報率 |

n=2000、各シナリオ R=1000 反復、seed は決定論的に固定しています。  
測定量は 2SLS の bias (median と IQR を主、mean も併記)、naive Wald (2SLS 点推定 + delta-method 正規近似) の被覆と claim rate、AR の被覆と claim rate、effective F の flag rate、placebo flag rate、符号診断の fail rate です。  
ここで claim rate は「95% 信頼集合が 0 を除外した割合」、つまり帰無シナリオでは偽陽性率そのものです。

事前に立てた仮説は 4 本で、うち 2 本 (S4 で naive の size が膨れる、S6c の対照設定) はデータと接触して死にました。  
死んだ仮説は結果が合うまで再調整せず、死んだまま報告します。  
この報告方式自体が、本プロトコルが分析 agent に要求している規律の自己適用です。

## 6. 実測の結果

### 帰無で黙るか

| シナリオ | naive claim rate | AR claim rate | mean effective F | effective F flag rate |
| --- | --- | --- | --- | --- |
| S1 strong × effect | 0.123 | 0.092 | 142.1 | 0.000 |
| S2 strong × null | 0.040 | 0.046 | 140.7 | 0.000 |
| S3 weak × effect | 0.081 | 0.045 | 6.8 | 0.994 |
| S4 weak × null | 0.065 | 0.066 | 6.6 | 0.987 |

S2 が Thesis B の直接テストです。  
帰無の下で naive 0.040、AR 0.046 と、どちらも名目 5% に収まりました。

検出力側 (S1/S3) は 9〜12% と薄いままです。  
これは β=0.08 という「現実の応用研究に合わせた効果量」が、この DGP の n=2000 では小さい効果だからで、現実的な効果量を選ぶことと検出力の高いデモを作ることは両立しませんでした。  
数字を盛れる場所ですが、盛らずにそのまま出します。  
一方で effective F の flag rate は weak シナリオで 0.99 前後であり、「weak IV を検知して robust 経路へ倒す」という機械的な routing は安定して機能します。

### weak IV だけでは naive は壊れなかった

事前の仮説は「S4 (weak × null) で naive Wald の偽陽性が膨れ、AR との差が開く」でした。  
結果は naive 0.065 で、膨れませんでした。  
π を 0.01 (effective F ≈ 1.1) まで下げる補足 sweep でも、naive の claim rate は 5〜7% で flat のままです。

きれいすぎる帰無結果はまず疑うべきなので、2 つの独立実装で確認しました。  
別 code path で書いた素朴な 2 段階回帰は点推定が 1e-12 の精度で一致し、頑健 SE を古典的 (等分散) SE に差し替えても claim rate は 4 桁一致でした。  
つまり実装バグではなく、この DGP のこの較正では本当に壊れていません。

最初に付けた説明は「単一 instrument では壊れず、Bound–Jaeger–Baker が示した破綻は many weak instruments の現象なのだろう」でした。  
この説明は撤回済みです。  
S1〜S4 と補足 sweep のすべてが、DGP の固定 loading が暗黙に決める ρ≈0.65 の上で走っており、weak-IV の size distortion を実際に駆動するパラメータを一度も動かしていなかったからです。

### F×ρ の joint 現象

ρ を陽に動かせるよう DGP を一般化し、F と ρ の 2 元 sweep (帰無、単一 instrument) を回しました。

| 目標 F | ρ | 実現 mean effective F | naive claim rate | AR claim rate |
| --- | --- | --- | --- | --- |
| ~1.5 | 0.65 | 1.48 | 0.058 | 0.057 |
| ~1.5 | 0.85 | 1.64 | 0.156 | 0.061 |
| ~1.5 | 0.95 | 1.70 | 0.220 | 0.056 |
| ~1.5 | 0.99 | 1.70 | 0.202 | 0.052 |
| ~3 | 0.65 | 2.33 | 0.061 | 0.062 |
| ~3 | 0.85 | 2.63 | 0.106 | 0.054 |
| ~3 | 0.95 | 2.74 | 0.120 | 0.057 |
| ~3 | 0.99 | 2.79 | 0.125 | 0.052 |
| ~6.5 | 0.65 | 6.38 | 0.045 | 0.046 |
| ~6.5 | 0.85 | 7.75 | 0.078 | 0.044 |
| ~6.5 | 0.95 | 8.48 | 0.096 | 0.050 |
| ~6.5 | 0.99 | 8.82 | 0.095 | 0.047 |

ρ=0.65 の行では F をどこまで下げても naive は 5% 近傍のままです。  
同じ weak F のまま ρ を 0.99 へ上げると naive の偽陽性率は 0.202 (名目の 4 倍) まで立ち上がり、AR は全域で 5% 近傍から動きません。  
naive Wald の破綻は F 単独の現象ではなく、識別の弱さと内生性の強さの joint 現象で、単一 instrument で再現します。

この sweep の ρ=0.65、F≈6.5 の行 (naive 0.045) と、前節の S4 (naive 0.065、F≈6.6) は同じ regime を指した数値ですが一致しません。  
両者は同じ ρ≈0.65 相当を狙っていても、DGP の calibration (noise scale を ρ の目標値から逆算する経路と、S4 が使う固定 loading) と乱数 seed が別なので、独立な Monte Carlo 標本です。  
R=1000 での claim rate の標準誤差は 5% 近傍で 1 ポイント弱あり、この程度の差は同じ regime の別サンプルとして起こり得る範囲ですが、数字だけを並べて「同一条件」と読ませるのは不正確なので、ここで独立試行であることを明記しておきます。

この結果は当初の想定より筋の良い設計論拠になります。  
ρ は Y 方程式と D 方程式の観測不能な構造誤差の相関であり、これを直接推定するには、まさに問題になっている外生性の仮定が要ります。  
「ρ が低い領域なら naive で十分」は真であっても、自分が低 ρ 領域にいることを分析者は検証できないので、行動には変換できません。  
検証不能な条件に依存する安全性は、protocol の設計では「安全でない」と同じ扱いになります。  
weak-IV-robust な推論 (AR 集合) を分析者や agent の事後判断ではなく宣言時の rule として強制する理由が、この表に出ています。

### 測る側のバグ: AR 集合は区間とは限らない

この実験自体にも、review で見つかった測定バグが 1 つありました。  
当初の実装は AR の claim / 被覆判定を「grid 上で棄却されなかった点の凸包 (min と max)」で行っていました。  
しかし weak IV の下では AR の受容域はしばしば単一区間になりません (half-line や補区間になり得ることは Dufour 1997 が示しています)。  
実測でも S4 の 1000 反復中、有界区間になったのは約 10% だけで、73% は half-line、17% は grid 全域、残り 0.4% は空集合でした。  
0 を除外する非区間の受容域を凸包で潰すと 0 が「含まれる」ことになり、数えたいはずの帰無棄却が静かに消えます。

判定を AR(β₀) の 1 点直接評価に置き換えたところ、旧実装が見せていた「instrument が弱いほど AR が conservative になる (2〜3% へ drift)」という模様は消え、全域 flat な 5% になりました。  
drift は AR の性質ではなく凸包の artifact でした。  
上の money table はすべて修正後の直接評価によるものです。

### 診断自身の誤報率

| シナリオ | π\_a | 符号診断 fail rate |
| --- | --- | --- |
| S6 defiers あり | −0.2 | 0.942 |
| S6c defiers なし (境界) | 0 | 0.469 |

defiers が本当にいるとき (S6)、first-stage 符号診断の検出力は 0.94 と高い一方、subgroup の真の係数がちょうど 0 のとき (S6c、monotonicity は成立) の誤報率は 0.469 で、統計的にはコイントスです。  
§4 の Card の符号反転 (t=−0.14) はまさにこの境界域の観測であり、referee の high-severity 指摘は v0 の符号 rule (符号だけを見て有意性を見ない) の偽警報だった可能性が高い、と事後に測定できたことになります。  
指摘自体は当時の情報では正当で、locked spec を守って report に残した判断も変わりませんが、診断 rule の v0.2 改訂 (反転した符号に個別の有意性も要求する) が backlog に入りました。

placebo 診断は、違反あり (S5) と違反なし (S5c) の両方で flag rate 1.000 でした。  
これは構成上の必然で、placebo と instrument が共通因子 L を共有する限り、その因子が Y に直接入ったかどうかを placebo は区別できません。  
placebo の flag は「交絡 channel が存在する」ことの証拠であって、「その channel が outcome に入った」ことの証明ではない、という限界が定量で確認された形です。  
基準として、P と Z が真に独立なときの flag rate は 0.098 (名目 10%) でした。

最後に、Card の実分析が使った共変量残差化 (FWL) の code path も、共変量入りシナリオで median bias 0.014、被覆 0.957 / 0.961 と確認しています。

## 7. Limitations

* 全数値が簡易 closed-form 実装によるものです。pin された参照実装に置き換えても regime (どこで壊れ、どこで壊れないか) は保たれる想定ですが、個々の値は動きます
* many weak instruments (Bound–Jaeger–Baker の実際の設定) は未検証です。F×ρ の上に別の破綻 mode が乗るかは、過剰識別 DGP を建てて測るまで分かりません
* v1 の scope は IV / LATE のみです。DiD や RDD は enum の予約席しかありません
* 頑健性 matrix の cell 群は記述的報告のみで、specification curve 全体に対する joint inference はしません
* ledger v0 は固定 α 資産の spending 会計です。earn-back のある alpha-investing や e-process による anytime-valid 化は拡張 seam の段階です
* 符号診断 v0 は noise-blind で、境界域の誤報率 0.469 は測定済みの欠陥です (これ自体が v0.2 の設計入力になります)
* 実データの worked example は 1 本だけで、プロトコルの使い勝手に関する外部妥当性は n=1 です
* §6 の claim rate はプロトコルに正直に従った場合の数字です。ledger を破棄して都合の良い分割が出るまで `init` をやり直す、通る診断や argued\_via の言い回しを探して spec を書き換える、といった protocol の外側での回避行動そのものの発生率は測っていません。外部登録なしでは、この protocol は「遵守された分析の内部無矛盾性」しか保証しません (§2)
* 統制語彙 (world の 6 assumption) は表現力に上限があります。agent が自分の実際の仮定ではなく、validation を通りやすい assumption や診断の組み合わせへ言い換える risk は、v1 では防げていません
* weak-IV-robust な推論として AR 集合のみを rule 化しています。CLR や conditional likelihood 法など他の robust 手法との比較、many-instrument 設定での相対優劣は検討していません
* 診断 registry の hard cap や統制語彙のような governance 上の判断 (何を entry として追加するか、誰が判定するか) は v1 に含まれていません。運用が広がれば必要になる課題です
* §4 の AR 区間の健全性は、この記事の執筆時点で Card の実装 (`analysis.py`) に §6 の直接評価と set\_type 分類を移植し、両 partition が genuine な bounded interval であることをコード側でも確認済みです (`zero_rejected: true`, `set_type: "bounded_interval"` を診断 artifact に追加)。ただし、この修正は今回の worked example 1 本のみに適用したもので、`exl` 本体の registry や conformance suite には昇格させていません
* conformance suite v0 は 3 つの合成 DGP を持ちますが、うち 2 つ (weak instrument、exclusion 違反) の検査は現状「推定値が有限で暴走しない」程度の弱いチェック止まりです。§6 で測った性質を pass/fail 条件へ昇格させるのは backlog です

## おわりに

手法は選ぶものではなく、宣言した仮定に対して catalog が引く対応になりました。  
そして agent 時代の統計的推論では、逐次的な分析 loop を前提にした会計 (anytime-valid 方向の契約) が native な形になります。  
この 2 つを運用として束ねる職能の名前が IdentificationOps で、explysis はその最初の道具立て、形としては agent の分析 loop を包む identification harness です。

このプロトコルの価値は、賢い分析を生成することではなく、生成された分析のどこまでが licensed かを機械が判定できることにあります。  
実データ 1 周では referee が spec の oversell を捕まえ、合成データの実測では自分の実験の測定バグと誤った結論を 2 つ見つけて直しました。  
その修正履歴ごと残すことが、このプロトコルの想定する分析の姿です。

リポジトリは [github.com/takyone/explysis](https://github.com/takyone/explysis) で公開しています。  
本記事の実験は `experiments/article_replication.ipynb` で再現できます (Card の artifact trail の検証、F×ρ の money table を含め、seed 固定で本記事の数値と完全一致することを実行結果として commit 済みです)。  
次の段階は skills とプロトコルを対にした plugin 化で、agent にこの契約を最初から読ませる配布形を作ります。
