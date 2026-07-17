---
id: "2026-07-17-claude-code-のサブエージェント全部-opus-にしていませんか品質ファーストの自動ルーテ-01"
title: "Claude Code のサブエージェント、全部 opus にしていませんか？——「品質ファースト」の自動ルーティングをつくった話"
url: "https://zenn.dev/dupi/articles/claude-code-smart-dispatch"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "zenn"]
date_published: "2026-07-17"
date_collected: "2026-07-18"
summary_by: "auto-rss"
query: ""
---

Claude Code をガッツリ使っていると、`Agent`（サブエージェント）をいくつも飛ばす場面が増えます。並行で調べさせたり、ファイルを分割して処理させたり。便利で手放せない機能なのですが、ひとつだけ厄介な問題があります。

**サブエージェントは、親と同じ（＝一番強くて、一番高い）モデルをそのまま引き継いでしまう**のです。

つまり「設定ファイルを1行読むだけ」みたいなタスクにも、最強モデルの料金がまるまるかかります。気づけばトークン残高が溶けていく……。自分もこれに何度か心を痛めました。

## 「安くすればいい」に潜む、見えない罠

「じゃあ安いモデル（`sonnet` / `haiku`）に切り替えればいいじゃん」と考えたくなります。実際、世の中の「モデルルーター」の多くはそうします——**コストを削るために作られていて、品質の低下を黙って許容する**。

でも、ここには見えない罠があります。

アーキテクチャを練るタスクや、新しいコードを書くタスクを `haiku` に任せると、**品質が静かに落ちます。** しかも厄介なことに、出力を最後まで読むまで、その劣化に気づけないことが多いのです。

つまり「節約したつもりが、知らぬ間に品質を落としていた」という事態が平気で起きます。これ、こわくないですか？

## ひっくり返した前提：コストより、品質を先に

`smart-dispatch` は、この「コスト優先」の前提をあえて逆転させました。方針は一言です。

「難しそうだったら、とりあえず一番強いモデルを使っておく。本当に簡単だと自信を持てるときだけ、安いモデルに下げる」——少しだけ損をしてでも、安全側に倒す割り切りです。

コストを無駄にするのは許容する。そのかわり、**難しいタスクを安いモデルに振って品質を落とす事故だけは、ゼロに近づける。** これがこのプラグインの赤線です。

## どう動くのか

実際の流れはこうなります。

```
Agent ツール呼び出し
        │  (PreToolUse フックが傍受)
        ▼
 ┌──────────────────────────────┐
 │ 1. model が既に指定されている?  │  → Yes: 尊重して通す（上書きしない）
 └──────────────────────────────┘
        │ No
        ▼
 ┌──────────────────────────────┐
 │ 2. タスクを分類               │   tier + confidence を得る
 │    (ヒューリスティック or Haiku)│
 └──────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────┐
 │ 3. policy 適用 (decide-model) │   default opus
 │    自信があって簡単なら下げる   │
 └──────────────────────────────┘
        │
        ▼
 ┌──────────────────────────────┐
 │ 4. ダウングレード時のみ        │   updatedInput で model を書き換え
 │    さもなくば素通し            │
 └──────────────────────────────┘
```

いくつか、こだわった設計上の決定があります。

* **自動で動く。** コマンドを覚える必要はありません。インストールしたら、裏で勝手に振り分けてくれます。
* **明示的にモデルを指定したら、それを尊重する。** 上書きしません。
* **迷ったら強いモデル。** 判断に迷うタスクは、安全のため強いモデルを使います。
* **絶対に呼び出しを壊さない。** 何かエラーが起きても、フックは黙って通します。ルーティングのせいで作業が止まるようなことはありません。

## 判断のルール：たった1つのファイルが真実

ルーティングの判断は `src/decide-model.js` という1つのファイルに集約しています。すべての経路がここを通る、**唯一の真実（single source of truth）** です。

```
export const DOWNGRADE_THRESHOLD = 0.8 // opus を離れるのに必要な confidence
export const BUDGET_FLOOR = 0.1        // 残予算がこの割合を下回ると opus→sonnet

const TIER_MODEL = {
  Trivial: 'haiku',
  Routine: 'sonnet',
  Hard: 'opus',
  Unknown: 'opus',
}

export function decideModel({ tier, confidence = 0, userOverride = null, budgetRemaining = null } = {}) {
  // 1. ユーザーの明示指定が常に優先
  if (userOverride) {
    return { model: userOverride, downgraded: false, reason: 'user override' }
  }

  // 2. tier を正規化。不明 → 安全デフォルトの opus
  const safeTier = TIER_MODEL[tier] ? tier : 'Unknown'

  // 3. confidence を正規化。非有限値/負値は 0（自信なし）として扱う
  const safeConfidence = Number.isFinite(confidence) && confidence >= 0 ? confidence : 0

  // 4. 品質ファースト: 自信を持って簡単/日常のときだけ opus を離れる
  const confident = safeConfidence >= DOWNGRADE_THRESHOLD
  const downgradeable = (safeTier === 'Trivial' || safeTier === 'Routine') && confident

  const model = downgradeable ? TIER_MODEL[safeTier] : 'opus'

  // 5. 予算モード: opus を下げる唯一の許された例外
  if (model === 'opus' && budgetRemaining !== null && budgetRemaining < BUDGET_FLOOR) {
    return { model: 'sonnet', downgraded: true, reason: `budget low (${budgetRemaining}) → opus→sonnet` }
  }

  return { model, downgraded: downgradeable, reason }
}
```

tier とモデルの対応は、こんなにシンプルです。

| tier | 例 | モデル |
| --- | --- | --- |
| Trivial | grep、ファイル一覧、設定ファイルを読む | haiku |
| Routine | 定型編集、要約、フォーマット | sonnet |
| Hard | 設計、デバッグ、新規コード、アーキテクチャ | opus |
| 不確定 | 判定が曖昧なもの | opus（フォールバック） |

## 「分類器の意見は、あえて聞かない」

ここで、ちょっと面白い設計をひとつ。

分類器は `model` というフィールドも返してくるのですが、**これを、あえて無視します。**

「は？」と思ったかもしれません。せっかく分類器が「これは Hard だから `opus` がいい」と言っているのに、なぜ聞かないのか。

理由はこうです——**最終的な決定権を、品質ファーストの policy にだけ持たせたいから。** policy は分類器の `tier` と `confidence` だけを受け取って、自分でもう一度判断を組み立て直します。分類器がどんなに主張しても、最後の一押しは policy が握る、というわけです。

こうしておくと、「分類器が調子に乗って `haiku` を推奨しても、それで勝手に品質が落ちることはない」という保証ができます。

## 2つのルートが、同じルールを共有する

`smart-dispatch` には、モデルを選ぶ経路が2つあります。**どちらも同じ `decide-model.js` を使って、同じログに書き込みます。**

### 経路A：フック（自動・保守的）

インストールするだけで動きます。`Agent` ツールが呼ばれるたびに `PreToolUse` フックが発火して、**ヒューリスティック分類器**でタスクを分類します。

ここが大事なのですが、このヒューリスティックは**意図的に狭く**作ってあります。理由はこのあとすぐ。

### 経路B：`/smart-dispatch` スキル（明示・高精度）

もう少し精度が欲しいときは、`/smart-dispatch` を明示的に呼びます。こちらは **Haiku でタスクを分類**し、構造化出力 `{tier, confidence, ...}` を得てから同じ policy に通します。

両者は「どう分類するか」が違うだけで、**「どう決めるか」は完全に同じ**です。だからこそ `decide-model.js` を1つの真実にできますし、ログも `/smart-dispatch-report` でまとめて見ることができます。

## なぜ分類器を、信じられないほど狭くしたのか

フックが使う分類器は、徹底的に保守的です。**安全だと確信できる相手——読み取り専用の `Explore` エージェント——しか下げません。**

```
// MVP scope: 読み取り専用の Explore エージェントだけがダウングレード安全。
// general-purpose / Plan / code-reviewer / カスタムエージェントは opus に残す。
if (subagent_type !== 'Explore') {
  return { tier: 'Unknown', confidence: 0, reason: 'non-Explore → leave at opus' }
}
```

なぜそこまで慎重にするのか。答えは単純で、**ヒューリスティックは誤判定するから**です。「絶対に品質を落とさない」と決めた以上、誤って Hard タスクを安いモデルに振るリスクは極小化しないといけません。だからこそ、一番安全な表面（読み取り専用の検索エージェント）だけでしか下げない、という思い切った絞り込みにしました。

判定ルールは素朴なキーワードマッチです。

* **「難しいタスク」を示すキーワード**（`implement` / `design` / `refactor` / `debug` / `write` / `create` / `build` / ...）が1つでも入っていたら `Hard` 判定 → `opus` に留める
* **「探す・読む」を示すキーワード**（`find` / `search` / `grep` / `list` / `read` / ...）があって短ければ `Trivial` → `haiku`
* プロンプトの長さ（600 / 1500 / 4000 文字）で Trivial / Routine / Unknown を切り分け

### 実際にハマった：キーワードの「部分一致」

素朴な話をひとつ。分類器は `.includes()` で部分一致させるのですが、これが**禁則語の部分文字列にも引っかかります。**

デモを作っていたとき、プロンプトに `rewrite` という単語を入れたら、なぜか `Hard` 判定されました。しばらく悩んだのですが、原因は `re**write**` の中に「難しい」キーワードの `write` が含まれていたからです。

結果的には**安全側への誤判定**（簡単なものを Hard とみなして `opus` を使う）なので、品質への影響はゼロでした。とはいえ意図通りに動いていないのは事実なので、デモのプロンプトは `rewrite` を避けて書き直しました。

部分一致ベースの分類器を作るときは、禁則語の**部分文字列**にも気を使う——地味ですが、ハマりがちなポイントです。

## デモ

実際のヒューリスティック分類器と policy を動かしたデモです（API キー不要・再現可能）。

```
  Task                                            Tier      Conf    Model
  ───────────────────────────────────────────────────────────────────────
  Explore · grep usages of decideModel            Trivial   0.85    haiku   ↓ downgrade
  Explore · walk through hooks/ control flow (v…  Routine   0.80    sonnet  ↓ downgrade
  Explore · "design a caching layer…"             Hard      0.60    opus    kept (quality-first)
  general-purpose · implement login + tests       Unknown   0.00    opus    kept (quality-first)
  Explore · explicit model: sonnet                override  —       sonnet  respected, not routed

  Hard tasks, uncertain tasks, and non-Explore agents stay on opus.
  Only confident read-only tasks downgrade — never lose quality to a routing mistake.
```

5行で方針が全部見えます。`grep` は `haiku` に、やや長めの読み取りタスクは `sonnet` に下がり、設計・実装・非Explore は `opus` に留まり、明示指定は尊重されます。

## 節約額について、正直に

ここは大きく見せたくないので、嘘をつかずに書きます。

`smart-dispatch` には評価用のハーネス（`eval/run-eval.js`）があって、2つの数値を出します。

* **`falseDowngradeRate`** —— Hard タスクが `opus` 未満に振られた割合。**赤線はほぼゼロ。**
* **`savingsRate`** —— all-opus ベースラインに対する支出の削減率。**目標は 0.3〜0.5。**

ただし、**節約額は経路によってだいぶ違います。**

* `/smart-dispatch`（Haiku 分類器）を明示的に使う経路では、目標域に届きます。
* 一方、**フック単体は意図的に保守的**（Explore 読み取り専用のみ）なので、フックだけで見ると節約は小さくなります。

なので「〇〇% 節約！」のような絶対値で謳うのは、正直ではない気がしています。**節約は（明示/分類器パスの）条件付きの評価値**であって、フックは「品質を優先した結果、副産物として少しだけ安くなる」と捉えるべきだろう、というのが自分の考えです。README でもそのように扱っています。

## プライバシーも、ちゃんと考えてあります

ルーティングの判断は `~/.smart-dispatch/log.jsonl` に記録しますが、**書き込むのは `tier`, `confidence`, `model`, `timestamp` のみ**です。タスクの本文は絶対に書きません。

```
{"ts":"2026-07-17T00:00:00Z","tier":"Trivial","confidence":0.85,"model":"haiku"}
```

`npm run report`（またはセッション内で `/smart-dispatch-report`）で、モデル分布・推定節約額・予算モードのダウングレード回数を集計表示できます。ログのパスは `SMART_DISPATCH_LOG` で上書き可能です。

## バッチ処理用のもう一つのモード

`workflows/batch-route.js` は、[Workflow](https://docs.claude.com/claude-code/workflows) 上でバッチ処理しつつコストを制御するモードです。同じ品質ファーストの policy に**予算の感度**を足したもので、残予算が `BUDGET_FLOOR`（0.1）を下回ると `opus` タスクが `sonnet` に一段下がります。これが `opus` を下げる唯一の許された例外で、すでに下げたタスクをさらに上げることはありません。

## インストール

```
claude plugin marketplace add dudupii/smart-dispatch
claude plugin install smart-dispatch@smart-dispatch
```

インストール後、ルーティングは**自動かつ透過**です。`Agent` ツールを呼ぶたびにフックがモデルを書き換えるので、コマンドを覚える必要はありません。モデルを明示すれば尊重してスキップします。

## おわりに

`smart-dispatch` が解きたかったのは、「コストを削りたい、でも品質は絶対に落としたくない」という、両立が難しそうに見えるジレンマでした。答えは割り切っています——**難しいタスクには絶対 `opus`。簡単なタスクだけ、自信があるときだけ、安いモデルに下げる。**

「品質を落としていないこと」を数値で証明できる仕組み（データセット＋評価ハーネス＋赤線指標）と、コアがゼロ依存であること——地味ですが、自分が一番こだわったところです。

Claude Code ユーザーの方、ぜひ試してみてください。特に「このタスクで変な振り分けになった」という実例をもらえると、分類器としきい値の調整に直結します。Issues でも、記事のコメントでも。
