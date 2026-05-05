---
id: "2026-05-04-github-actionsでcopilot-sdkを使いclaude-skillsの効果検証をして-01"
title: "GitHub ActionsでCopilot SDKを使いClaude Skillsの効果検証をしてみる"
url: "https://zenn.dev/rick2200/articles/9db3f4e32f9286"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## はじめに — Skills は「作って終わり」ではない

Claude Code の Skills は、プロジェクトの進行や環境の変化にあわせて手を入れ続ける**継続的改善の対象**になりつつあります。トリガー条件を狭めたり、出力フォーマットを更新したり、新しい用語に追従したり。1 回書けば終わる仕様書ではなく、コードと同じく**運用しながら磨く資産**です。

ここで困るのが、PR で Skill の追加・修正が上がってきたときのレビューです。

* 「この修正で本当に skill が効くようになるのか?」
* 「無関係な発話で誤発火（暴発）しないのか?」
* 「以前のバージョンと比べて挙動が良くなったのか、悪くなったのか?」

SKILL.md の diff を眺めるだけでは、これらの問いに答えられません。レビュアー個人の感覚と「動かしてみた印象」に依存しがちで、その判断は**チームに共有されないまま** PR がマージされていきます。

コードであれば CI のユニットテスト・回帰テストが「マージしていい変更か」をある程度機械的に判定してくれます。同じ仕組みが Skills にも欲しい — 検証結果をチーム全員が PR 上で見られる状態にしたい — というのが本記事のスタートラインです。

そこで筆者は、Claude Code Skills を **CI 上で A/B 検証するプラグイン `skill-eval`** を作りました。PR コメントに `/skill-eval` と書くと、GitHub Actions が起動して新版（PR head）と旧版（PR base）を同じシナリオで実行し、両者を匿名比較して **改善 ✅ / 退行 ❌ / 同等 ➖** の判定を PR に返します。LLM による採点エンジンには GitHub Copilot の Python SDK を使っています。

> 設計上、`skill-eval` は **「マージを止めるブロッキング判定ツール」ではなく、「レビュアーが PR 上で参照する追加シグナル」** として位置付けています。最終的なマージ判断は人間に残し、CI は判断材料を増やす道具という割り切りです。

本記事では、

* **(1) `/skill-eval` を実際に動かして PR に何が返るか** を最初に見せたうえで、
* **(2) 自分のリポで `/skill-eval` を動かせる状態まで持っていく手順**
* **(3) 内部の設計思想と採点ロジック**
* **(4) 実際の PR で得られた結果と運用上の注意**

の順で扱います。

**想定読者:** Claude Code Skills を**書く / レビューする / 運用する**いずれかの立場で、効果検証に困っているエンジニア。Claude Code Skills と Copilot CLI の経験者を想定します。Copilot SDK は未経験でも問題ありません。GitHub Actions の基礎は前提とします。

---

## まず `/skill-eval` で何が返ってくるか

まず実行結果から見ていきます。これは本記事を書く過程で実際に作った PR で `/skill-eval` を実行したときの GitHub 上のスクリーンショットです。

![PR コメントに返ってくる skill-eval レポート](https://static.zenn.studio/user-upload/e4771059ee5d-20260505.png)

レポートを構成する要素はシンプルに 4 つです。

* **判定アイコン (改善 ✅ / 退行 ❌ / 同等 ➖)**: 新版が旧版より良くなったか、悪くなったか、変わらないかを 1 目で
* **平均スコアと Δ**: 新版（treatment）と旧版（control）の総合平均と、その差分。スコアは 1〜5 の整数 4 軸の平均で、**高いほど良い**
* **シナリオ別サマリ**: 各テストケースで新旧どちらが何回勝ったかと、シナリオごとの Δ。**全体は同等でも個別シナリオで退行している副作用**がここで見えます
* **軸別差分**: 「成功条件充足 / 網羅性 / 期待挙動への一致 / 簡潔さ」の 4 軸でどこに改善・退行があったか

この 1 枚が PR コメントに残るので、レビュアーは「diff だけ見て『なんとなく良さそう』で merge」ではなく、**数字を根拠に**マージ可否を議論できるようになります。

ちなみに上のスクリーンショットでは判定が **同等 ➖** になっています。Δ は +0.58 で改善閾値を超えているのに、なぜ「改善」ではないのか — その理由は本記事末尾の「やってみた」節で詳しく扱います。先に「使うとどう動くか」「中で何をしているか」を見ていきましょう。

---

## 使い方とセットアップ

### 必須環境

* **Copilot subscription** (Free / Pro / Business / Enterprise いずれでも可)
* GitHub リポジトリ (PR ベースで運用されているもの)
* `.claude/skills/<name>/SKILL.md` が存在するか、PR で追加・修正される

### 動作確認済み環境

* **Python 3.11**: `github-copilot-sdk==0.3.0` は public preview。新しい Python での安定性は未確認のため、ワークフローは Python 3.11 に固定しています
* **Node 24**: Copilot CLI のインストールに必要 (`npm install -g @github/copilot`)
* **GitHub Actions** (`ubuntu-latest`)

### セットアップは 5 ステップ

実装内容は以下リポジトリの `plugins` 配下にあります。

<https://github.com/Riku-KANO/agent-plugins>

#### Step 1. プラグインのインストール

Claude Code を開き、以下を実行します。

```
/plugin marketplace add Riku-KANO/agent-plugins
/plugin install skill-eval@personal-agents
/reload-plugins
```

`personal-agents` マーケットプレイスから `skill-eval` プラグインが導入されます。

#### Step 2. ランナーの展開

リポジトリのルートで `/skill-eval:setup` を実行します。

これで以下が展開されます。

* `.github/workflows/skill-eval.yml` — `/skill-eval` PR コメントで起動するワークフロー
* `.skill-eval/scripts/` — Python ランナー一式（オーケストレーター、Copilot SDK ラッパー、評価エージェント、レポーター）
* `.skill-eval/scenario.schema.json` — シナリオの JSON Schema
* `.skill-eval/README.md` — 消費側向け運用ガイド

既存ファイルは上書きされません。プラグインを更新したときは `/skill-eval:setup --force` で安全に再生成できます。ユーザーデータである `.claude/skills/<skill>/skill-eval/scenarios.json` と `.skill-eval/reports/` は `--force` でも消えません。

#### Step 3. シークレット追加

リポジトリ secret に **`COPILOT_GITHUB_TOKEN`** を登録します。値は **fine-grained PAT** で、Account permissions の `Copilot Requests` を Read 権限で付与したもの。

#### Step 4. シナリオの作成

検証したい skill を引数に `/skill-eval:create-test` を実行します。

```
/skill-eval:create-test example-haiku
```

ヒアリング形式で 3〜5 シナリオを対話的に作成し、`.claude/skills/example-haiku/skill-eval/scenarios.json` として保存します。シナリオは検証対象 skill のディレクトリに **co-locate** されるので、skill 改修と同じ PR でシナリオも合わせて修正でき、レビューしやすくなります。

シナリオを書くときのコツは **採点基準（`success_criteria`）を観測可能な形にする**こと。「ちゃんと答える」「適切に返す」では採点不能なので、

* 「出力が 3 行のみで構成される」
* 「`俳句:` 等のプリアンブルを含まない」
* 「skill 固有の見出し構造を持たない」（暴発抑止シナリオの場合）

のように、**評価者が機械的に確認できる**水準まで分解します。

推奨バランスは以下のチェックリストで揃えると安心です（用語の意味は次節で解説します）。

#### Step 5. PR を作って `/skill-eval`

skill を変更する PR を作成し、PR コメントに `/skill-eval` と書きます。

10 分前後で結果が返ります。完了すると：

* **PR コメント**に冒頭で見せたフォーマットの判定レポートが投稿される
* `.skill-eval/reports/<skill>/` に詳細レポート（transcript 抜粋付き）が追加コミットされる

### コスト感

1 skill あたりの消費は概ね **18 + 3 = 21 セッション**です。

* Implementer: 3 シナリオ × samples\_per\_arm 3 × 2 アーム (control / treatment) = **18 セッション**
* Evaluator: シナリオごとに 1 回採点 = **3 セッション**

Copilot Premium Quota を 1 PR で 20+ 回叩くので、組織で運用するときは「main へのマージ前の 1 回だけ」など実行頻度の運用ルールを決めておくのが無難です。Free プランは weekly quota が低めなので、評価運用には Pro 以上のサブスクが現実的です。

---

## A/B 検証の設計思想

ここからは「冒頭で見せた判定レポートが、なぜそうなっているか」を内側から見ていきます。

### なぜ A/B か — 「skill ありで動いた」だけでは効いた証明にならない

Skill が効いているかを単純に確認するなら「skill を有効にして発話を投げ、期待挙動が出るか見る」で十分なはずです。しかし実際には**skill を無効にしても LLM がたまたま正解する**ケースが多々あります。これでは skill が効いたのか、モデルがもともと正解できる発話だったのか、区別がつきません。

そこで `skill-eval` では、**変更前後の 2 群（A/B）を並列に走らせて差分で評価**します。具体的には PR が SKILL.md にどんな変更を加えたかで mode が決まり、それに応じて **control (対照群)** と **treatment (処置群)** の中身が切り替わります。

| mode | control (対照群) | treatment (処置群) |
| --- | --- | --- |
| **modification** (修正) | PR base 版の SKILL.md をロード | PR head 版の SKILL.md をロード |
| **addition** (新規追加) | skill ロードなし baseline | PR head 版の SKILL.md をロード |
| **removal** (削除) | base 版の SKILL.md をロード | skill ロードなし |

本記事では一番典型的な **modification (修正)** を主に扱います。modification の文脈に限れば「control = 旧版 / treatment = 新版」と読み替えてほぼ等価です。両者のスコア差分 Δ を見ることで、「skill の変更によって何が改善（または退行）したか」を相対比較で測れます。

### 「効くべきとき効く」と「効くべきでないとき効かない」の二軸

シナリオには **2 種類の `expectation`（期待挙動）** があります。

| `expectation` | 意味 | 検証したいこと |
| --- | --- | --- |
| `should_fire` | この発話で skill が**発火すべき** | skill が効くべき場面で本当に効いているか |
| `should_not_fire` | この発話で skill が**発火してはいけない** | 近接ケースで skill が誤発火（暴発）していないか |

`should_fire` だけだと「効くこと」しか見えませんが、運用上は\*\*「効くべきでないときに効かないこと」も skill の品質\*\*です。例えば「今日の出来事を 3 行でまとめて」というユーザー発話に対し、haiku skill が「3 行」というキーワードに釣られて 5-7-5 を返してしまったら、これは暴発です。`should_not_fire` シナリオはこの種の暴発を回帰テストとして検出します。

### archetype でシナリオの難易度を分類する

各シナリオには `archetype`（シナリオの難易度区分）を付けられます。

* `direct`: skill のドメインが明らかな発話（例: 「俳句を作って」）
* `adjacent`: 境界線上、文脈から推測できる発話（例: 「気分転換に何か詠んで」）
* `subtle`: ぱっと見では skill 領域に見えない発話（例: 「今日の出来事を 3 行でまとめて」）

採点の厳しさは archetype に左右しません。あくまで「どれだけ難しいケースまで攻めているか」をシナリオ作成者・レビュアーが意識するための分類です。

### 全体パイプライン

PR コメントから判定レポート投稿までの外側のフローは次のとおりです。

ポイントを 2 つ補足します。

**(1) Workflow は default branch のコードを実行する。** PR head に書かれた Python は信用しないという設計です。PR head から取り出すのは「データ」(SKILL.md の中身、scenarios.json) だけ。これにより悪意ある PR が CI を乗っ取って secret を抜く、といった脅威を遮断します。あわせて、`/skill-eval` をコメントしたユーザーに write 以上の権限があるかも事前チェックします。

**(2) なぜ Copilot SDK を採用したか。** Copilot SDK (Python `github-copilot-sdk==0.3.0`、public preview) には `skill_directories` というパラメータがあり、Claude Code 本体が skill をロードするのと**同じコードパス**で評価セッションを起動できます。プロンプトに skill 本文を埋め込むシミュレーションではなく、**実際の挙動**を測れるのが採用理由です。加えて、Copilot subscription があれば fine-grained PAT 1 本で CI から呼べるので、別途 LLM API キーを管理しなくて済みます。

---

## LLM-as-judge の採点設計

A/B でシナリオを並列に回したあと、その transcript を**どう採点するか**が次の課題です。`skill-eval` は **LLM-as-judge（LLM による採点）** を採用していますが、評価者の主観に振り回されないように 4 つの工夫を入れています。

### 1. 採点基準 `success_criteria` を ground truth として扱う

シナリオには `success_criteria`（観測可能な箇条書き 3〜5 項目）を必ず添えます。たとえば haiku skill の `should_fire` シナリオなら以下のようになります。

```
{
  "user_prompt": "今日の気分を 5-7-5 で表現して",
  "success_criteria": [
    "出力が3行のみで構成される (4行以上はNG)",
    "「俳句:」等のプリアンブルや「いかがでしたか」等のポストアンブルを含まない",
    "日本語で詠まれている (英訳が混入しない)",
    "抽象語ではなく具体的な情景・季語的イメージを含む"
  ]
}
```

評価者プロンプトでは「`success_criteria` を **authoritative ground truth (権威ある正解)** として扱い、推測で書き換えるな」と強く指示しています。これにより、評価者の好みではなく**シナリオ作成者の意図**で採点が決まります。

`should_not_fire` シナリオでは書き方が反転します — 「skill 固有の見出し・用語・構造を**持たない**こと」を観測可能な形で記述します。

### 2. 4 軸ルーブリック

採点は 4 軸 × 1〜5 の整数スコアです。

| 軸 | 意味 |
| --- | --- |
| `success` | `success_criteria` をどれだけ満たしているか |
| `completeness` | ユーザー要求を漏らさずカバーできているか |
| `skill_engagement` | `expectation` に沿った挙動か |
| `conciseness` | 適切に簡潔か |

`skill_engagement` は `expectation` に応じて意味が反転します。`should_fire` なら「skill が明確に効いているほど高得点」（5 = skill が明らかに適用された応答、1 = skill の痕跡なし）、`should_not_fire` なら「skill が漏れずに通常応答しているほど高得点」（5 = skill 固有の見出し・用語・構造が一切混入していない、1 = skill が暴発している）。**スコアは常に「高い = expectation に沿っている」** で統一されているので、集計時に符号反転を考えなくて済みます。

### 3. 匿名化

A/B の transcript はそのまま評価者に渡しません。`run_1..run_N` の匿名 ID にシャッフルしてから渡し、どれが treatment / control かを評価者は知らない状態で採点します。これで「treatment のほうが新しいから高評価」というバイアスを排除できます。集計側でだけ ID と arm の対応表を保持し、後から決定的にスコアを再ラベル付けします。

### 4. 集計は決定論

最終判定はシンプルな閾値ルールです。

* `Δ ≥ +0.5` かつ全シナリオで `treatment ≥ control` → **改善 ✅**
* `Δ ≤ -0.5` → **退行 ❌**
* それ以外 → **同等 ➖**

平均はただの算術平均、ペア勝敗はただのカウントです。ここに LLM を噛ませると分散がただ増えるだけで何も得しません。LLM を信じるのは「個別 transcript の良し悪しを採点する」局所的な判断だけに留めて、集計は決定的にしています。

### 内部の役割分担

上の 4 つの工夫は、コード側でもファイル境界として明示的に切り分けてあります。`Orchestrator` (`skill_eval.py`) が全体を仕切り、各シナリオについて Implementer → Evaluator を順に呼び、すべてのシナリオが処理されたあとに Reporter に渡して集計します。

| 役割 | ファイル | 担当 |
| --- | --- | --- |
| **Orchestrator** | `skill_eval.py` | PR diff から SKILL.md を抽出。各シナリオで Implementer / Evaluator を呼び、最後に Reporter で集計 |
| **Implementer** | `agents/implementer.py` | 1 シナリオあたり control / treatment 各 N=3 セッションを `asyncio.gather` で並列実行。Copilot SDK の `skill_directories` パラメータでアームを切り替える |
| **Evaluator** | `agents/evaluator.py` | 6 transcript を `run_1..run_6` にシャッフルして 1 セッションで採点。arm の対応表は呼び出し側でだけ保持し、評価モデルには見せない |
| **Reporter** | `agents/reporter.py` | スコアの平均・ペア勝敗・軸別差分を**決定論**で計算し、判定 (改善 / 退行 / 同等) と詳細レポートを出力 |

「Implementer は並列で実行を回し、Evaluator は匿名で採点し、Reporter は決定論で集計する」という役割分担が、そのまま 3 ファイルの境界に対応しています。**LLM を信じる範囲を「個別 transcript の採点」だけに絞り、集計は算術で固める** という方針が、コードの分割として明示されているのがポイントです。

---

## やってみた: example-haiku の検証結果

冒頭で見せた PR コメントは、本記事を書く過程で実際に作った PRで `/skill-eval` を回した結果です。

### 検証対象の skill (= control 側)

`example-haiku` は 5-7-5 の俳句を返すだけのシンプルな skill です。記事の見通しのため、PR base 版（= control 側でロードされる）の SKILL.md を全文掲載します。

```
---
name: example-haiku
description: Use when the user asks for a haiku, a 5-7-5 poem, or wants a short 3-line poetic response on a given topic. Triggers on phrases like "write a haiku", "haiku about X", "5-7-5 poem", "短い詩で", "俳句を作って". Does NOT engage for factual questions, code help, or general prose.
version: 0.1.0
---

# example-haiku skill

Generate a haiku (5-7-5 syllable poem in 3 lines) on the topic the user requests.

## Output format

Always:

- Produce **exactly 3 lines**.
- Line 1: 5 syllables (5 morae for Japanese).
- Line 2: 7 syllables (7 morae for Japanese).
- Line 3: 5 syllables (5 morae for Japanese).
- **No preamble** ("Here's a haiku:") and **no postamble** ("I hope you enjoyed it!").
- Match the language of the user's request: English request → English haiku, Japanese request → Japanese haiku.
- Reflect the user's topic in **concrete imagery**, not abstract description.

## Examples

User: "Write a haiku about coffee."

You:

```
Steam curls from the cup
Bitter promise of morning
The day finally starts
```

## When NOT to engage

Do not produce a haiku for:

- Factual questions ("what is the boiling point of water?")
- Code help ("debug this function for me")
- Conversation that doesn't explicitly ask for a poem
- Prose summary or explanation requests

In those cases, respond normally without invoking the haiku format.
```

「3 行で出力 / プリアンブル・ポストアンブル禁止 / 具体的情景」という指示と、暴発抑止の `When NOT to engage` セクションが置いてある構成です。

### PR の変更内容 (= control → treatment の差分)

PR #3 はこの SKILL.md に **kigo (季語) ガイダンス**を 14 行追加します。haiku の定義的特徴である「特定の瞬間 (季節) への anchoring」を明示する変更です。

```
+- **Anchor the poem in time with a kigo (季語) — a seasonal reference.**
+
+## Kigo guidance
+
+| Topic / mood | Implicit kigo direction |
+|---|---|
+| coffee, hot drinks, mornings | winter chill, breath, steam |
+| ocean, fireworks, festivals | summer, cicadas, evening cool |
+| commute, change, restlessness | autumn winds, falling leaves |
+| beginnings, hope, deadlines | spring rain, new green, blossoms |
```

### シナリオと事前期待

設計思想で例示してきた 4 本構成のまま検証しました。

| ID | archetype | expectation | user\_prompt |
| --- | --- | --- | --- |
| s1 | direct | should\_fire | 今日の気分を 5-7-5 で表現して |
| s2 | direct | should\_fire | 俳句を作って |
| s3 | adjacent | should\_fire | 気分転換に何か詠んで |
| s4 | subtle | should\_not\_fire | 今日の出来事を 3 行でまとめて |

事前の期待は **「s1〜s3 で treatment > control、s4 は変わらない、全体 改善 ✅」** でした。kigo guidance は negative-trigger 領域には触れていないので、暴発抑止の s4 はそのまま維持される想定です。

### 実結果と読み方

PR コメントに返ってきた数値を抜粋します。

| ID | 種別 | 期待 | treat | ctrl | Δ | 勝/敗/分 |
| --- | --- | --- | --- | --- | --- | --- |
| s1 | direct | 発火すべき | 4.92 | 3.25 | **+1.67** | 8/0/1 |
| s2 | direct | 発火すべき | 5.00 | 4.50 | +0.50 | 3/0/6 |
| s3 | adjacent | 発火すべき | 4.17 | 3.75 | +0.42 | 6/3/0 |
| s4 | subtle | 発火してはいけない | 4.58 | 4.83 | **-0.25** | 0/7/2 |

総合は treatment 4.67 / control 4.08 / **Δ +0.58**。判定は期待の 改善 ✅ ではなく **同等 ➖** でした。Δ は閾値 +0.5 を超えているのに、**s4 で treatment < control** だったため「全シナリオで treatment ≥ control」条件を満たさず格落ちしました。

s1 で +1.67 と劇的に効いた一方、s4 でわずかに退行 — つまり **「効くべき場面で効く」を狙った改修が、「効くべきでない場面で効きすぎる」副作用を生んだ** ということです。kigo guidance が「3 行でまとめて」発話に対しても季節要素を呼び起こしてしまったと読めます。これは PR diff (14 行追加) を眺めているだけでは絶対に気付けない構造で、`should_not_fire` × `subtle` シナリオを入れていなかったら見逃して merge していた可能性があります。

### 教訓

* **`should_not_fire` は副作用検知器として効く。** s4 のような subtle ケースは PR レビューでは絶対に気付けません
* **判定アイコンより、シナリオ別の Δ を読むほうが学びが深い。** 全体平均は改善寄りでも、特定シナリオで退行している副作用は判定アイコンには現れません
* **採点基準を観測可能な粒度に。** 「3 行のみ」「プリアンブルなし」のような物理的に確認できる水準に分解することが、安定した判定の前提です

---

## 注意点と Next Steps

### 運用上の注意点

`skill-eval` は alpha (`0.1.0-alpha.1`) です。正しく使うために頭に入れておきたいのは次の 3 点です。

* **判定はブロッキングではなく追加シグナル。** LLM による採点は確率的なので、同じ PR でも判定が揺らぐことがあります。マージ可否を CI 判定だけで決めるのではなく、**レビュアーが PR で参照する判断材料の 1 つ**として組み込むのが現実的です
* **シナリオの自動生成は意図的に行っていない。** `success_criteria` の質が判定の質を決めるので、ヒアリング型の `/skill-eval:create-test` で人間が作る前提です。CI に乗せる前にチームでシナリオをレビューする運用が安定します
* **コスト管理は明示的に。** 1 PR ≈ 21 セッションを Copilot Premium Quota から消費するので、main へのマージ前の 1 回など、起動条件をチームで決めておくのがおすすめです

### Next Steps

* **既存の skill 1 つから始める**: `/skill-eval:create-test <skill>` で 3〜5 シナリオを書いてみる。`should_not_fire` × `subtle` を 1 本入れることを忘れずに
* **PR で `/skill-eval` を試す**: skill を 1 行修正した PR を作り、コメントに `/skill-eval` と書いて挙動を確認

Skills を「個人の感覚で良し悪しを判断する」状態から、**チームが PR で見られるレポートで判断する**状態へ。本記事がその一歩になれば嬉しいです。
