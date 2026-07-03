---
id: "2026-07-03-無料のexecutorが一番高くついた話-opus-ローカルqwenが全タスクで最高額になった理由-01"
title: "無料のexecutorが一番高くついた話 — Opus + ローカルQwenが全タスクで最高額になった理由"
url: "https://zenn.dev/kenimo49/articles/free-executor-paradox-40-trials"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "AI-agent", "LLM", "Python", "zenn"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

![arm別の累積トークン量。Qwenのトークン代がゼロでも、Opus+Qwen構成 (arm B) は Opus 単独 (arm A) より orchestrator が読むトークンが 1.4〜5.3倍に膨らむ。](https://raw.githubusercontent.com/kenimo49/free-executor-paradox/main/results/figures/token-growth.png)

「強いモデルで段取りを組ませて、安いモデルに手を動かさせる」。エージェントコーディングのコスト削減レシピとして、ほぼ定石です。

私もそう信じて検証しました。Opus 4.7 にオーケストレータをやらせ、ローカルで動かしている Qwen 3.5-9B (トークン課金ゼロ) にコード編集を任せる。これで Opus 単独より安くなるはず。

結果は逆でした。

「タダ」のはずの構成 (Opus + Qwen) が、3つのコード修復タスク **全部で最高額** になりました。Opus 単独より高く、Opus + Haiku より高く、もちろん Haiku 単独より圧倒的に高い。「ローカルで動かしたから安いはず」を信じて GPU PC を組んだ私としては、けっこう困ります。

論文化したのでDOIを置いておきます: [10.5281/zenodo.20978074](https://doi.org/10.5281/zenodo.20978074) / [GitHub](https://github.com/kenimo49/free-executor-paradox)

この記事は、その40試行で何が起きたか、なぜ「タダ」が一番高くついたかを実測ベースで書きます。

## TL;DR

40試行 × 4構成 × 3タスク、決定的判定器 (mypy + ruff + pytest の exit code のみ) で測りました。LLM-as-judge は一切使っていません。

**結論**:

1. 「Opus が段取り + Qwen が手を動かす」構成は、3タスク全部でクラウド最高額。Opus 単独より高い。
2. 原因は executor のトークン代ではなく、**オーケストレータ側の prompt cache 再読み込み**。Opus が Qwen の返り値を毎ターン読み直す量が膨らみ、Opus 単独より入力ボリュームが 1.4〜5.3倍に育つ。
3. Haiku 単独は最大タスクで Opus 単独の 5.5倍安いが、25%の確率で失敗する。クラウド全体で見ると Opus + Haiku が一番バランスが良い。

「executor のトークンが無料なんだから安いはず」という直感が、なぜ外れるのか。それを最後まで書きます。

## 何を測ったか

### 4つの構成

| arm | orchestrator | executor | 役割分担 |
| --- | --- | --- | --- |
| A | Opus 4.7 | (単独) | 1モデルで全部やる |
| B | Opus 4.7 | Qwen 3.5-9B (ローカル/Ollama) | Opus が段取り + 検証、Qwen が編集 |
| C | Opus 4.7 | Haiku 4.5 (Anthropic SDK サブループ) | Opus が段取り + 検証、Haiku が編集 |
| D | Haiku 4.5 | (単独) | 1モデルで全部やる (安い方) |

4 arms とも Anthropic SDK 経由で同じツール群を使えます。`str_replace_editor` (view/create/str\_replace/insert) と `bash` (120秒タイムアウト)。オーケストレータ (B, C) には `delegate_to_executor` ツールが1つ追加されているだけ。

Anthropic prompt caching は全 arm で同じ設定: `system` / tools / 直近 user message に `cache_control: ephemeral` を付ける。temperature や seed は設定しないので、試行間ばらつきはサンプリングのランダム性そのものです。

### 3つのタスク

全部 [typer](https://github.com/tiangolo/typer) リポジトリの commit `b210c0e` (v0.26.8) 上で動かしました。MIT license で、ベンチマーク用に clone 済み。各試行は `git checkout -- . && git clean -fd` でリセットしてから始まります。

* **T1 — 故障修復**: AST で 25 errors を注入 (mypy 10件 + ruff 10件 + pytest collection 失敗 5件)。fully green まで戻す。
* **T2 — リファクタ**: `get_params_from_function` を `typer/utils.py` から新モジュール `typer/_param_extractor.py` に移動。全 import 元を更新。テストは全部 pass を維持。
* **T3 — 機能追加**: `get_version_banner(prefix, uppercase) -> str` を実装して `typer/__init__.py` から export。SHA-256 でフィンガープリントされたテストファイルを通す。

### 判定器

`mypy + ruff check + pytest` の exit code が 0 になったら成功、ならなかったら失敗。タスクごとに `verify-T2.sh` / `verify-T3.sh` で構造チェック (関数が新モジュールに移ってるか、フィンガープリントされたテストが改変されていないか等) も追加しています。

LLM に「これでOK?」とは一切聞いていません。判定は決定論的、再現可能。

| arm | task | n\_succ/total | wall (s) | iters | cost ($) | success rate |
| --- | --- | --- | --- | --- | --- | --- |
| A Opus solo | T1 | 3/3 | 253 | 36 | 1.74 | 1.00 |
| A Opus solo | T2 | 3/4 | 233 | 26 | 1.11 | 0.75 |
| A Opus solo | T3 | 3/3 | **69** | **6** | 0.17 | 1.00 |
| B Opus+Qwen | T1 | 3/4 | 484 | 38 | 2.27 | 0.75 |
| B Opus+Qwen | T2 | 3/3 | 443 | 27 | 1.38 | 1.00 |
| B Opus+Qwen | T3 | 3/3 | 348 | 12 | 0.42 | 1.00 |
| C Opus+Haiku | T1 | 3/3 | 400 | **28** | 1.67 | 1.00 |
| C Opus+Haiku | T2 | 3/3 | 275 | **20** | **0.92** | 1.00 |
| C Opus+Haiku | T3 | 3/3 | 145 | 11 | 0.38 | 1.00 |
| D Haiku solo | T1 | 3/4 | 758 | 89 | **0.30** | 0.75 |
| D Haiku solo | T2 | 3/4 | 507 | 70 | **0.23** | 0.75 |
| D Haiku solo | T3 | 3/3 | 208 | 29 | **0.08** | 1.00 |

太字は列内ベスト。40試行で Anthropic への合計支払いは$35.98。論文化費用としては安かったほうです。

注目すべき行は arm B です。3タスクすべてで `cost ($)` がクラウド arm 最高 ($2.27 / $1.38 / $0.42)。Qwen のトークン代はゼロ円なのに、Opus 単独より高い。

![T3 (機能追加タスク) の Pareto frontier。横軸=コスト、縦軸=wall time。arm B (橙) は arm A (赤) と arm C (緑) の両方に dominated されている — 安いわけでも速いわけでもない。](https://raw.githubusercontent.com/kenimo49/free-executor-paradox/main/results/figures/pareto-T3.png)

## なぜ「タダ」が一番高くついたか

Opus 側のトークン消費 (`input + cache_read_input`) を arm 別に比べると、こうなります。

| arm role | T1 (Opus 側 in+cache\_r) | T2 | T3 |
| --- | --- | --- | --- |
| A (Opus solo) | 534,586 | 226,474 | 13,320 |
| B (Opus + Qwen) | 733,142 | 313,914 | 62,864 |
| C (Opus + Haiku) | 421,622 | 159,640 | 44,016 |

B/A 比 (Opus 側だけ): **T1で 1.38倍、T2で 1.39倍、T3で 5.26倍**。

executor (Qwen) のトークンは無料です。でも Opus 自身が読むトークン量が、単独で動かすより 1.4〜5.3倍に膨らんでいる。

なぜか。`delegate_to_executor` で Qwen に編集を任せると、Qwen は stdout サマリを返します (私の実装では最大4000 char で切り詰め)。そのサマリが Opus 側のコンテキストに毎ターン積まれていく。Anthropic の prompt cache は最新メッセージを cache\_write し、次のターンで cache\_read として読み戻します。30〜80 ターン回るうちに、Opus が「Qwen が何をやったかのサマリ」を何度も何度も読み直す形になる。

その読み直しに、cache\_read 単価 ($1.50/M token = Opus input の 10%) が乗ります。executor が無料でも、orchestrator は無料ではない。当たり前に聞こえますが、「無料」と書いてある単語が文に入ると人間は判断停止しがちです。私です。

![Free-Executor Paradox のメカニズム。Orchestrator (Opus) が delegate_to_executor で Executor (Qwen) に指示 → Executor が stdout サマリを返す → Orchestrator のコンテキストにサマリが積まれ、次ターン以降 cache_read で読み直し続ける、というフィードバックループ。Qwen 自体のトークン代はゼロでも、Orchestrator 側の cache_read が累積する。](https://raw.githubusercontent.com/kenimo49/free-executor-paradox/main/results/figures/mechanism.png)

## T3 で 5.3倍に膨らんだ理由

最も極端なのが T3 (一番小さいタスク、6 iter 程度) です。

これも prompt cache の挙動で説明がつきます。base context (system + tools + 初期プロンプト) は最初の1ターンで cache\_write され、以降は cache\_read で安く読まれる。長いタスク (T1, T2) では、この base context は累積入力のうち小さな割合になります。

でも短いタスクでは違う。base context が累積入力に占める割合が大きい。だから「executor のサマリも返ってくるし、base も毎ターン読まれるし」のオーバーヘッドが効いてくる。T3 でだけ B/A 比 5.3倍という極端な数字が出るのは、これが理由です。

逆に C (Opus + Haiku) は T1 と T2 で cache\_read footprint が A より小さくなる (T1で0.79倍、T2で0.70倍)。Haiku は実際に substantive な仕事をしてくれて、Opus が自分でやらなくて済んだ分が浮く。これは executor がちゃんと働く ケースで、サマリだけが膨らむ Qwen ケースとは反対側です。

## メカニズムを1行で

executor のトークンが無料 = orchestrator の入力が安くなる、ではない。

正しくは: **orchestrator のコストは、executor が returnしてくるサマリを再読み込みする量に比例する**。executor の生 token 数ではなく、orchestrator が何度それを目にするかが効く。LLM じゃなくて中間管理職の話と勘違いしそうな結論ですが、本当にそうです。

これは「強いオーケストレータ + 安いエグゼキュータ」の定石が、反復的なツールループでは効きにくい構造的理由です。1ショットなら問題ない (orchestrator は routing だけ)。何十ターン回す iterative loop なら問題になる。

## オーケストレーションが勝つ条件 (自分の手で潰した範囲で)

正直に書きます。今回の実験は arm B が負けやすい条件で組まれています:

* **executor の返り値が free-form** (Qwen の stdout サマリ最大4000 char)。これを「構造化された diff 1個だけを返せ」と縛れば、Opus 側の累積コンテキストは小さくなる。
* **タスクが順次的** (T1/T2/T3 はどれも 1試行内では並列化できない)。「同時に3箇所いじってOK」みたいなタスクなら orchestration の元が取れる可能性が出てくる。
* **試行間で cache がリセットされる** (各 trial で harness を git reset)。同じ orchestrator を1日中走らせ続ければ、cache\_write のコストが薄まる。

executor 返り値を tight に絞ったうえで arm B を再走するのは、次の実験で測ろうと思っています。たぶん T3 では逆転する。T1 では微妙。

## 実務へのテイクアウェイ

私が今回の数字を見て、自分のエージェントコーディング運用に持ち帰った判断はこれです:

1. **タスクが数イテレーションで終わるなら Opus solo が一番安い**。T3 でクラウド arm 中 best ($0.17 / 69秒 / 6 iter)。「Opusは高い」は単発で見たときの話で、loop 全体で見ると per-iteration の効率が効く。
2. **タスクが数十イテレーション必要なら、per-iteration が安いモデルが効く**。T1 で Haiku solo がドル建て 5.5倍安い。ただし 25% で失敗するので、retry コストを含めると 4.2倍に縮む。
3. **クラウドだけで完結したいなら Opus + Haiku が一番バランス良い**。T1 で Opus solo と同等、T2 で最安、T3 でも僅差。Haiku 単独の失敗リスクを受け入れたくないなら、ここが安全側。
4. **ローカル Qwen で「タダ」を引きたい場合は、executor の返り値サイズを構造的に縛る**。free-form な stdout を返させると、orchestrator 側が cache\_read で食われる。

「強いモデル + 安いモデル」は、設計の自由度が思っているより狭いです。executor が何をどれくらい返すか まで含めて設計しないと、「orchestrator が高く付く」が再生産される。私はこの再生産を、計測ミスを疑って3回繰り返してから諦めました。

## 限界

正直に書く欄です:

* **n=3/cell** で母集団推定としては弱い。Mann-Whitney U の p値は normal approximation で 0.050 が小サンプル下限なので、「これ以上は識別できない量」を意味する。effect size (Cliff's delta) は信用してOK、p値の細かい違いは過大解釈しない。
* **3タスク全部が typer リポジトリ上**。一般化するには別 codebase でも回す必要がある。harness 含めて MIT で公開してあるので、追試はしやすいはず。
* **orchestrator/executor のシステムプロンプトが意図的に非対称**。orchestrator には「直接編集せず delegate しろ」と書いてある。これは現実的なデプロイ形だけれど、結果に乗っている confounder ではある。
* **prompt cache の挙動依存**。Anthropic 側で cache\_read 単価が変わったら結論も変わる可能性がある (今は input の 10%)。

## 再現

ベース環境は Ubuntu 22.04、Python 3.10+、`uv` 0.4+、`anthropic` Python SDK 0.83+。arm B は Ollama 0.4+ で `qwen3.5:9b`。arm A/C/D だけなら Ollama 不要。

```
git clone https://github.com/kenimo49/free-executor-paradox
cd free-executor-paradox
# arm A の T3 を 1 trial 走らせる
python scripts/runners/runner.py --arm A --task T3 --trial 1
```

詳細は repo の README と paper PDF を見てください。harness、breakage injection、runner、analysis 全部入っています。

## おわりに

「無料のはずなのに一番高い」は、強い言葉です。発見した当初は私も計測ミスを疑いました。3回走らせ直して、token usage を arm 別に分解して、ようやく「あぁ、orchestrator 側が読まされてるのか」と腹落ちしました。

agentic coding のコスト議論は executor の値段に寄りがちだけど、本当の支配項は orchestrator が何を何度読むか です。今回の Qwen は一例で、これから出てくるローカルモデル全部に同じ問題は付いて回ります (executor が free でも orchestrator の cache\_read は free にならない)。

数字で殴れる結論は強いので、論文の形にして Zenodo に置きました。誰かが「うちの codebase でも同じだったよ」「うちは逆だったよ」と追試してくれるのが一番嬉しい結末です。

---
