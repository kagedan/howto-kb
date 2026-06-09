---
id: "2026-06-08-copilot-cli-モデル別コスパ比較-2026-年-6-月版-swe-bench-pareto-01"
title: "Copilot CLI モデル別コスパ比較 (2026 年 6 月版) — SWE-bench × Pareto frontier"
url: "https://zenn.dev/takyone/articles/copilot-cli-cost-2026-06"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-rss"
query: ""
---

## TL;DR — こう使うとお得

* GitHub Copilot CLI が 2026 年 6 月 1 日から **「使った分だけ課金」** 方式 (usage-based billing) に変わりました。`--model` で何を選ぶかが、そのまま月末請求額に効いてきます
* 性能を **SWE-bench Verified と Pro の 2 軸** で見たところ、Pro 軸 (高難度ベンチ) の frontier に乗る GA モデルは **GPT-5.4 mini → Gemini 3.5 Flash → GPT-5.4 → Claude Opus 4.8** の 4 段。これがコスパ起点として最初に検討したい候補です
* Verified のみ frontier 上に出る Preview モデル (Gemini 3 Flash / Gemini 3.1 Pro) も活用可能ですが、より難しい Pro では順位が変わるので Preview opt-in 時は SWE-Pro の方を判断材料にすると堅実です
* それ以外のモデルにも個別の強み (long-context、Anthropic/OpenAI 内の統合、cache 温度等) はあります。**SWE 性能 × コスト** の単純比較ではこの 3 段を出発点にして用途別に検討するのが効率的です

## はじめに — なぜ今このベンチか

2026 年 6 月 1 日、GitHub Copilot は premium-request 制から **AI クレジット制 (1 credit = $0.01) の usage-based billing** に切り替わりました。CLI で agent ループを回すと、tool 呼び出しの入力/出力トークンがそのままクレジット消費になります。

つまり Copilot CLI で `--model` を何にするかは、ベンチマークスコアと月末請求額の両方に直接効きます。

そこで「**性能をベンチで定量、コストを単価で定量、両者を 1 枚の散布図に並べる**」というアプローチを取りました。Copilot CLI の用途であれば、性能評価は SWE-bench でほぼ十分という前提です (後述の Caveat 参照)。

## Pareto frontier って何 — 経済学少々

このあと「Pareto frontier」という言葉を何度か使うので、最初に砕いて説明します。

> あるモデル X が **Pareto 最適** であるとは、「X より安く、かつ X より高性能」なモデルが他に存在しない、という意味です。

つまり Pareto frontier (パレートフロンティア) は **「買って後悔しない選択肢」の集合** です。frontier から外れたモデルには、必ず「同じ値段でもっと良い」または「同じ性能でもっと安い」代替があります。

LLM のように選択肢が膨大な領域では、まず frontier の数本に候補を絞ってから、用途に応じて選ぶと判断負荷が一気に下がります。

## 評価軸の定義

### 性能軸 ① SWE-bench Verified — 標準難度

[SWE-bench Verified](https://www.swebench.com/) は、人間が「再現できる」と検証済みの 500 タスクからなる、現実の GitHub issue 解決ベンチマークです。Copilot CLI は autonomous agent ループを回す前提のツールなので、コード補完用の MBPP/HumanEval ではなくこちらが妥当な指標です。本記事では「標準難度」と呼ぶことにします。

ただし frontier 級モデルが集中する飽和帯 (80-90%) に入っていて、モデル間の差が見えにくくなってきています。

加えて **memorization 懸念** が指摘されてきました。Anthropic 自身が Opus 4.7 release で「Verified の一部に memorization signal を flag した」と公表しており、ベンチデータが学習データに混入している可能性込みで読む必要があります。Anthropic は「memorization 分を除外しても improvement is holds」と主張していますが、ラボごとに評価方法も微妙に違うので、絶対値を額面通り取れる状況ではありません。

### 性能軸 ② SWE-bench Pro — 高難度

これを受けて **SWE-bench Pro** (Public) が代替指標として広まりつつあります。Pro は actively-maintained リポジトリの multi-file diff から構成され、public ground-truth が漏れていないように設計されています。Verified より絶対値は低く出ますが (frontier モデルでも 50-70% 帯)、モデル間の差がより clean に出ます。本記事では「高難度」と呼びます。

各ベンダーの最新 model card / announcement では Pro を併載するのが主流になりつつあり、Anthropic / Google / OpenAI / Microsoft いずれも Pro 値を公開しています (一部古いモデルは未公表)。

### 本記事の方針

両方を **独立した 2 つの scatter** にプロットします。両者で frontier に乗るモデルは「どちらの bench でも cost-performance が成り立つ」robust な選択肢、片方だけ frontier 上のモデルは「ベンチ依存」、と読みます。

### コスト軸: blended cost — 3 種類のタスクプロファイル

各モデルには input トークン単価と output トークン単価があり、agent ループでは一般に input >> output になります (コードを読みながら少しずつ書く構造のため)。

ただ実際の比率はタスク内容で大きく変わります。Aider polyglot benchmark の公開データを見ると、`gpt-5 (high)` は約 1:1、`gpt-5 (low)` で 3.25:1 と、**1.5–3 倍程度の幅**に収まっています。一方 Copilot CLI のような agentic loop はファイル再読み込みや tool 戻り値の蓄積で input がさらに膨らみます。

そこで本記事では 3 つのプロファイルを用意します:

| プロファイル | input:output | こんなタスク | 例 |
| --- | --- | --- | --- |
| **Light** | 1.5 : 1 | 短く焦点が定まった編集。1 ファイル内で完結 | コミットメッセージ生成 / 変数リネーム / 単一関数のリファクタ / コードレビューへの返答 |
| **Standard** ★ メイン | 4 : 1 | 典型的な Copilot CLI セッション。計画 → 数ファイル編集 → 検証 | 新機能の小規模実装 / バグ修正 (数ファイル) / テスト追加 |
| **Heavy** | 10 : 1 | リポジトリ横断の探索や長時間タスク | 大規模リファクタ / 複数モジュールに跨るデバッグ / 設計レビュー / アーキテクチャ把握 |

blended cost は以下の式で計算します:

\text{blended cost} = \frac{w\_{in} \cdot p\_{in} + w\_{out} \cdot p\_{out}}{w\_{in} + w\_{out}}

メインの散布図は **Standard プロファイル (4:1)** で描いています。Light / Heavy だと frontier の傾きが変わる、という話はあとの section で。

## データ — Copilot CLI で使えるモデル一覧

公式 billing ページ と supported-models ページから、CLI から呼べるモデルの単価・SWE-bench Verified / Pro スコア・availability (GA / Preview) を並べました。スコアは各社の公式 announcement / model card の値です。コストは 3 プロファイル全部の数値を載せています。

SWE スコアの各数値はクリックで出典 (脚注) に飛びます。

| Model | Status | input $/1M | output $/1M | Light (1.5:1) $/1M | **Standard (4:1)** $/1M | Heavy (10:1) $/1M | SWE-Verified | SWE-Pro |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.5 | GA | 5.00 | 25.00 | 13.0 | 9.0 | 6.8 | 80.9% | — |
| Claude Opus 4.6 | GA | 5.00 | 25.00 | 13.0 | 9.0 | 6.8 | 80.8% | — |
| Claude Opus 4.7 | GA | 5.00 | 25.00 | 13.0 | 9.0 | 6.8 | 87.6% | 64.3% |
| **Claude Opus 4.8** | GA | 5.00 | 25.00 | 13.0 | 9.0 | 6.8 | **88.6%** | **69.2%** |
| Claude Sonnet 4.6 | GA | 3.00 | 15.00 | 7.8 | 5.4 | 4.1 | 79.6% | — |
| Claude Haiku 4.5 | GA | 1.00 | 5.00 | 2.6 | 1.8 | 1.4 | 73.3% | — (35.2%‡) |
| Gemini 2.5 Pro | GA | 1.25 | 10.00 | 4.5 | 3.0 | 2.0 | 59.6% | — |
| Gemini 3 Flash | Preview | 0.50 | 3.00 | 1.5 | 1.0 | 0.7 | 78.0% | — |
| **Gemini 3.5 Flash** | GA | 1.50 | 9.00 | 4.2 | 2.7 | 2.0 | — | **55.1%** |
| Gemini 3.1 Pro (≤200K) | Preview | 2.00 | 12.00 | 6.0 | 4.0 | 2.9 | 80.6% | 54.2% |
| Gemini 3.1 Pro (>200K)¶ | Preview | 4.00 | 18.00 | 9.6 | 6.8 | 5.3 | 80.6% | 54.2% |
| **GPT-5.4 (≤272K)** | GA | 2.50 | 15.00 | 7.5 | 5.0 | 3.6 | 80.0%§ | **57.7%** |
| GPT-5.4 (>272K)¶ | GA | 5.00 | 22.50 | 12.0 | 8.5 | 6.6 | 80.0%§ | 57.7% |
| **GPT-5.4 mini** | GA | 0.75 | 4.50 | 2.3 | 1.5 | 1.1 | — | **54.4%** |
| GPT-5.5 (≤272K) | GA | 5.00 | 30.00 | 15.0 | 10.0 | 7.3 | 82.6%§ | 58.6% |
| GPT-5.5 (>272K)¶ | GA | 10.00 | 45.00 | 24.0 | 17.0 | 13.2 | 82.6%§ | 58.6% |
| MAI-Code-1-Flash | CLI N/A† | 0.75 | 4.50 | 2.3 | 1.5 | 1.1 | 71.6% | 51.2% |

* **太字** = Verified / Pro 両方で Pareto frontier 上の GA モデル (コスパ起点として最も robust)
* `—` = ベンダーが当該ベンチを公開していない
* `§` = OpenAI は GPT-5.4 / 5.5 とも Verified を公表しておらず (announcement では Pro と Terminal-Bench を強調)、Verified の数値は [vals.ai](https://www.vals.ai/benchmarks/swebench) の third-party 計測値です。Pro は OpenAI 公称
* `¶` = 長コンテキスト tier (GPT-5.4/5.5: input >272K、Gemini 3.1 Pro: input >200K)。OpenAI は input 2x / output 1.5x、Google は input 2x / output 1.5x。リクエスト全体に適用されるため typical な agentic CLI セッション (数十万 token 以下) ではほぼ短 tier 側
* `‡` = MAI の model card で Microsoft が再測した値 (independent harness、Anthropic 公称 Pro はなし)
* `†` = MAI-Code-1-Flash は launch 時点 (2026-06-02) で **CLI 未対応**、VS Code 限定。CLI rollout は今後のリリース予定
* このほか CLI では GPT-5 mini / GPT-5.3-Codex / Sonnet 4.5 / Raptor mini (Preview) も使えますが、SWE スコアが揃わないため本記事の比較からは除外しています

## 散布図 ① SWE-bench Verified (標準難度、Standard プロファイル)

![Copilot CLI models: SWE-bench Verified % vs blended cost ($/1M tokens, 4:1)。緑破線が Pareto frontier、薄赤シェードが dominated 領域。](https://static.zenn.studio/user-upload/deployed-images/c71ec38f145f908c6b5d4127.png?sha=286c48847a54783d6955b1e60de04deeb18d0caf)

緑破線が Pareto frontier、金リング ◯ が frontier 上の点、薄赤シェードが **dominated 領域** (このゾーンのモデルには「より安くて同等以上」または「同価格でより高性能」な代替が必ず存在する) です。frontier 各区間の **限界費用** (SWE スコアを 1 pt 改善するための追加コスト) は本文の table を参照してください。

### Verified からの読み取り

Preview 込み frontier: **Gemini 3 Flash → Gemini 3.1 Pro → Opus 4.8**

| 区間 | $/1M 増 | SWE-V +pt | $/pt |
| --- | --- | --- | --- |
| Gemini 3 Flash → Gemini 3.1 Pro | +3.00 | +2.6 | $1.15/pt |
| Gemini 3.1 Pro → Opus 4.8 | +5.00 | +8.0 | **$0.63/pt** |

GA only frontier: **Haiku 4.5 → GPT-5.4 → Opus 4.8** ※ Gemini 3.5 Flash は Verified 非公開のため除外

| 区間 (GA only) | $/1M 増 | SWE-V +pt | $/pt |
| --- | --- | --- | --- |
| Haiku 4.5 → GPT-5.4 | +3.20 | +6.7 | $0.48/pt |
| GPT-5.4 → Opus 4.8 | +4.00 | +8.6 | **$0.47/pt** |

Verified だけで見ると、Preview opt-in で Gemini 3 Flash (SWE-Verified 78%) を default にして、中位に Gemini 3.1 Pro (SWE-Verified 80.6%) を挟む形が最もコスパが出ます。Opus 4.8 への最終 escalate が 1 pt あたり最も安い区間。

ただし frontier の絶対値が 70-90% 帯にあって、memorization 懸念込みで読む必要があります。次に Pro 軸を見ます。

## 散布図 ② SWE-bench Pro (高難度、Standard プロファイル)

![Copilot CLI models: SWE-bench Pro % vs blended cost ($/1M tokens, 4:1)。緑破線が Pareto frontier、薄赤シェードが dominated 領域。](https://static.zenn.studio/user-upload/deployed-images/70d04bdae68a0d8ab9384bc4.png?sha=44f4e612996d1a7898e3339f950f4ed0de663e6d)

### Pro からの読み取り

CLI で使える Pro frontier (GA + Preview): **GPT-5.4 mini → Gemini 3.5 Flash → GPT-5.4 → Opus 4.8** (すべて GA、actionable な 4 段)。

| 区間 (CLI 実用) | $/1M 増 | SWE-Pro +pt | $/pt |
| --- | --- | --- | --- |
| GPT-5.4 mini → Gemini 3.5 Flash | +1.20 | +0.7 | $1.71/pt |
| Gemini 3.5 Flash → GPT-5.4 | +2.30 | +2.6 | $0.88/pt |
| GPT-5.4 → Opus 4.8 | +4.00 | +11.5 | **$0.35/pt** |

Pro 軸で目立つ発見:

* **GPT-5.4 mini ($1.5, 54.4%)** が Pro frontier 最安帯。Gemini 3.5 Flash まで 0.7pt 差しかなく、コスト約 1/2 の budget 選択肢
* **MAI-Code-1-Flash ($1.5, 51.2%) は GPT-5.4 mini に dominate** (同コスト、より高 score)。MAI が CLI 開放されても mini の方が cost-performance 上
* **Gemini 3.1 Pro Preview (SWE-Pro 54.2%, $4.0) は Gemini 3.5 Flash GA (SWE-Pro 55.1%, $2.7) に dominate される**。Verified の優位はここで消える
* **GPT-5.5 ($10.0, SWE-Pro 58.6%) は Opus 4.7 ($9.0, SWE-Pro 64.3%) に dominate** (より高く、より低 score)。Pro でも GPT-5.5 は圏外
* **Opus 4.7 → 4.8 は Pro で 5pt 差** (Verified は 1pt 差)。Pro の方が世代差を強く拾う

### 2 つの軸を統合した結論

**両 bench で評価可能な範囲で frontier に乗る CLI 用 GA モデル**:

| Model | SWE-Verified | SWE-Pro | Standard $/1M | 位置づけ |
| --- | --- | --- | --- | --- |
| GPT-5.4 mini | (非公開) | 54.4% | 1.5 | Pro frontier 最安、budget default |
| Gemini 3.5 Flash | (非公開) | 55.1% | 2.7 | Pro frontier、long-context や multimodal 兼ねた default |
| GPT-5.4 | 80.0%§ | 57.7% | 5.0 | 両 bench で中継点 (Verified は third-party) |
| Opus 4.8 | 88.6% | 69.2% | 9.0 | 両 bench で最上位、escalate 先 |

この **GPT-5.4 mini → Gemini 3.5 Flash → GPT-5.4 → Opus 4.8 の GA 4 段** が、ベンチ依存しない最も robust な選択肢です (上位 2 つは Verified 非公開のため Pro 軸での評価)。Preview opt-in (Gemini 3 Flash / Gemini 3.1 Pro) は Verified 上のみ有利で、Pro では Flash GA に劣るため、production 投入する場合は GA frontier に戻すのが堅実。

### frontier 外モデルの位置づけ

frontier に乗らないモデルも、特定の用途では選択肢になります。SWE 性能 × コストの単純比較ではどう見えるか、別の強みは何か、整理します。

* **Gemini 3.1 Pro Preview** ($4.0、SWE-Verified 80.6% / SWE-Pro 54.2%): **Verified では frontier に乗るが Pro では Gemini 3.5 Flash GA に dominate** という二面性。長 context (128K+) や reasoning effort の高さが効くタスクでは Verified スコア通りのコスパが出る一方、より厳しい Pro 評価では GA Flash で足りる、と読めます
* **Claude Sonnet 4.6** ($5.4、SWE-Verified 79.6%): Anthropic は Pro を公表していないため Pro 軸では plot 不可。Verified で見ると GPT-5.4 (SWE-Verified 80.0%) と近接位置。Anthropic stack 統一、Claude 系 tool 挙動の好み等の文脈で選択肢
* **Claude Opus 4.7** ($9.0、SWE-Verified 87.6% / SWE-Pro 64.3%): 同価格の Opus 4.8 (SWE-Verified 88.6% / SWE-Pro 69.2%) と Verified 1pt / Pro 5pt 差。Pro 差は無視できないが、cache 温度 / latency が安定しているなら継続も合理的
* **Claude Opus 4.5 / 4.6** ($9.0、SWE-Verified 80.9% / 80.8%): Pro は未公表。新規利用なら 4.7 / 4.8 が同価格で性能向上を享受できるのでおすすめ
* **GPT-5.5** ($10.0 短 tier、SWE-Verified 82.6%§ / SWE-Pro 58.6%): 両 bench で Opus 4.7-4.8 の方が安く高 score。OpenAI ecosystem との統合、reasoning 系の長考タスク、特定ドメインの精度が決め手になる場合は選択肢
* **Gemini 2.5 Pro** ($3.0、SWE-Verified 59.6%): 世代として古く、現行 Flash 系が性能・コストで上回ります。既存パイプラインで使っている場合の継続選択肢
* **Haiku 4.5** ($1.8、SWE-Verified 73.3%): Anthropic は Pro を公表していませんが、Microsoft の独立再測では SWE-Pro 35.2% と低め (harness 差を考慮しても frontier から外れる)。Anthropic API integration や Claude 系 prompt cache を活かしたい場合の軽量選択肢として
* **Gemini 3 Flash Preview** ($1.0、SWE-Verified 78.0%): Verified では最安。ただし Pro は未公表で、Verified の memorization 懸念込みで読む必要があり、安全側を取るなら GA の Gemini 3.5 Flash が本命です
* **GPT-5.4 mini** ($1.5、SWE-Verified 非公開 / SWE-Pro 54.4%): Pro frontier 最安帯。Gemini 3.5 Flash まで 0.7pt 差で約半額なので budget 重視の default 候補。Verified は OpenAI 非公開
* **MAI-Code-1-Flash** ($1.5、SWE-Verified 71.6% / SWE-Pro 51.2%): CLI 未対応 (launch 時 VS Code 限定)。同価格の GPT-5.4 mini に Pro で dominate されるので、CLI 開放されても主役には立ちにくい位置

### プロファイル別: frontier の形は変わるか

Light / Standard / Heavy の 3 プロファイルで Pro frontier 候補のコストを並べると:

| Model | Light (1.5:1) | Standard (4:1) | Heavy (10:1) |
| --- | --- | --- | --- |
| GPT-5.4 mini | 2.3 | 1.5 | 1.1 |
| Gemini 3.5 Flash | 4.2 | 2.7 | 2.0 |
| GPT-5.4 | 7.5 | 5.0 | 3.6 |
| Claude Opus 4.8 | 13.0 | 9.0 | 6.8 |

*(単位: $/1M tokens。ここでの token は input・output の合算、blended cost = (w\_in · p\_in + w\_out · p\_out) / (w\_in + w\_out) で計算した加重平均)*

* **どのモデルも Light → Heavy で単価が下がります** (input 単価が output より安く、Heavy では input 比重が大きいため)。これは frontier 上のモデルすべて共通で、Gemini 3 Flash も Opus 4.8 も Heavy 列では Light 列の半額前後になります
* **frontier の順序は 3 プロファイル全部で同じ** (GPT-5.4 mini → Gemini 3.5 Flash → GPT-5.4 → Opus 4.8)。順序が動かないので「プロファイルで model を機械的に切り替える」必要はあまりありません
* escalate の判断軸は **「タスクの失敗コスト」** で考えるのがおすすめです:
  + **Light タスク** (commit message、変数 rename、1 ファイル refactor): 失敗しても retry の token が小さい。多少 miss しても痛くないので GPT-5.4 mini or Gemini 3.5 Flash で OK
  + **Heavy タスク** (repo 横断 refactor、長時間 debug): 失敗 → retry の wasted tokens が大きい。高 score な Opus 4.8 (SWE-Verified 88.6% / SWE-Pro 69.2%) で一発通す方が、retry を含めた **期待コスト** で安く済むケースがあります

## お得な使い方 — 段階的 escalation

私が試している運用パターンを共有します。まず軽いモデルで試して、必要に応じてグレードアップする戦略です。

### A. Pro frontier の GA 4 段 (本命)

Pro 軸で frontier 上に乗る GA モデル 4 段。最も robust な構成です:

1. **最安 default**: `--model gpt-5.4-mini` ($1.5/1M @ Standard、SWE-Pro 54.4%)
   * 短い refactor / commit msg 等の Light タスク向け。Gemini 3.5 Flash と Pro 0.7pt 差で半額
2. **default**: `--model gemini-3.5-flash` ($2.7/1M @ Standard、SWE-Pro 55.1%)
   * long-context や multimodal が必要な日には Flash 側へ。GA Flash 帯で最も高い Pro 数値
3. **詰まったら中位へ**: `--model gpt-5.4` ($5.0/1M @ Standard、SWE-Verified 80.0% / SWE-Pro 57.7%)
4. **難所だけ最上位**: `--model claude-opus-4.8` ($9.0/1M @ Standard、SWE-Verified 88.6% / SWE-Pro 69.2%)
   * 失敗 retry の wasted tokens が痛い長時間タスクは、高 score で一発通す方が retry 込みの期待コストで安く済むケースがあります

### B. Preview を試したい場合の補足

* **Gemini 3 Flash (Preview)** は Verified 78% で frontier 最安ですが、Pro 値が未公開のため真の cost-performance は読み切れません。`--model gemini-3-flash` を試して挙動が良ければ default 候補に
* **Gemini 3.1 Pro (Preview)** は Verified 80.6% で GPT-5.4 を上回るものの、Pro 54.2% は Gemini 3.5 Flash GA に劣ります。reasoning 重め / 長 context のタスク以外で常用するメリットは限定的

Preview モデルは挙動変更や API 互換性のリスクがあるため、production pipeline には GA を、ローカル開発・実験用途には Preview を、と使い分けるのが堅実です。

Copilot CLI の Auto router (`--model auto`) は plan 制約の中で GPT-5.4 / 5.3-Codex / Sonnet 4.6 / Haiku 4.5 から選ぶ仕組みです。frontier 上の Gemini 3.5 Flash や Opus 4.8 を明示指定するとコスパが出やすい場面が多い、というのが個人的な感触です。

## Caveats — この比較が外す論点

* **Harness 差で ±5pt は揺れる**: SWE-bench スコアは各社それぞれ別の agent harness で計測されています。第三者ベンチ ([vals.ai](https://www.vals.ai/benchmarks/swebench) 等) で揃えると数値が動きます。例として Haiku 4.5 は Anthropic 公称 Verified 73.3% に対し、Microsoft の MAI 用 harness では同モデルが 66.6% Verified / 35.2% Pro と 7pt 程度低く出ます
* **Verified は memorization 懸念あり**: Anthropic 自身が Opus 4.7 release で「Verified の一部に memorization signal を flag」と公表。frontier 級モデルの差は学習データ混入の可能性込みで読む必要があり、より新しい Pro の方が信頼性が高い、という見方が広がっています
* **Blended cost の比率はあくまで近似**: 実 workload を測れば 2:1 〜 20:1 まで散らばります。cache を考慮しないモデルなので、Claude Code 系では実コストはさらに下がります
* **Tokenizer 効率差は補正していません**: OpenAI (tiktoken)、Anthropic、Google の各 tokenizer は同じテキストでも token 数が ±5-15% 程度ずれます。$/1M tokens 比較は本来 tokenizer-normalized で行うのが正確で、本記事の単純比較では微差 (例: GPT-5.4 80% と Sonnet 4.6 79.6% の 0.4pt 差) は逆転しうる範囲です。3 社とも token count を取れる API は公開されているので、自分のコーパスで測れば補正できます (OpenAI: `tiktoken` package、Anthropic: `count_tokens` API、Google: `countTokens` REST endpoint)
* **SWE-bench 以外の能力は無視**: long-context (Gemini 3.5 Flash の MRCR 128k)、multimodal、tool 使用の癖、JSON 出力の安定性、日本語コードコメントの自然さ等は別途評価が必要
* **MAI-Code-1-Flash は CLI 未対応**: launch 時点 (2026-06-02) で VS Code 限定、CLI 開放は今後。CLI 開放されても同価格 ($1.5) の GPT-5.4 mini に Pro で 3.2pt 差で dominate されるので主役にはなりにくい
* **GPT-5.4 mini / nano は SWE-Verified 公表値なし**: OpenAI は両モデルとも Pro のみ公表 (mini 54.4% / nano 52.4%)。mini は本記事の Pro scatter / table に追加していますが Verified 軸では plot 不可。nano は CLI 非対応のため掲載対象外
* **Annual subscriber は legacy 課金**: 2026-06-01 移行時に annual plan に居た user は premium-request multiplier 制が残っているため、本記事の単価計算は当てはまりません。Pro / Pro+ / Business / Enterprise の monthly 利用者が対象です

## まとめ

| 観点 | おすすめ |
| --- | --- |
| 最安 budget default (GA) | **GPT-5.4 mini** — Pro 54.4% / $1.5、Light タスク用 |
| Default (GA) | **Gemini 3.5 Flash** — Pro 55.1% / $2.7、long-context にも強い |
| 詰まったとき (mid、GA) | **GPT-5.4** — 両 bench frontier、Pro 57.7% / $5.0 |
| 難所だけ (hard) | **Claude Opus 4.8** — 1pt 改善あたりの限界費用が最も低い、両 bench frontier |
| Heavy タスク (長時間 agent) | Opus 4.8 を最初から選ぶのも合理的 |
| Preview 試したい | Gemini 3 Flash (Verified 78%、Pro 未公表)、Gemini 3.1 Pro (Verified frontier、Pro では Flash に劣る) |
| 別軸で評価 | Sonnet 4.6 (Anthropic 統合)、GPT-5.5 (OpenAI ecosystem)、Opus 4.7 (cache 温度) |

以上、2026 年 6 月時点での Copilot CLI のモデル別コスパでした。frontier の顔ぶれは半年もすれば変わっていそうです。

## 注意書き

本記事のスコア・単価は **2026 年 6 月時点** のものです。LLM の価格と性能は四半期スパンで動くため、半年後には frontier の構成が変わっている可能性が高いです。数値ソースは脚注に列挙しました。
