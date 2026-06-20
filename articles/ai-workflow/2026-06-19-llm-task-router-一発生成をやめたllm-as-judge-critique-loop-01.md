---
id: "2026-06-19-llm-task-router-一発生成をやめたllm-as-judge-critique-loop-01"
title: "llm-task-router 一発生成をやめた：LLM-as-Judge × Critique Loop で記事品質を底上げする"
url: "https://qiita.com/rex0220/items/6b906ebde7ffde5373a4"
source: "qiita"
category: "ai-workflow"
tags: ["API", "LLM", "TypeScript", "qiita"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

テーマから記事本文を一気に生成する「一発生成」は、実装が簡単です。まず出してみる、という意味ではとても強い手段でもあります。

ただ、運用に載せると次のような限界にぶつかりがちです。

- 論点の抜けがある
- 冗長な説明が混ざる
- 構成の流れが甘い
- 想定読者との前提がズレる
- 一見それっぽいが、読み終わると刺さらない

人間の執筆プロセスは、普通これを一発では終えません。

1. 企画する
2. 構成を考える
3. 書く
4. レビューする
5. 修正する

この分業と反復で品質を上げています。  
LLMでも同じ発想を持ち込むと改善しやすくなります。つまり、**「書くモデル」と「見るモデル」の役割を分ける**、ということです。

本記事では、生成物を別工程で評価し、明確な指摘に基づいて書き直す **自動推敲ループ（Critique Loop）** を、薄い設計変更で追加する方法を紹介します。題材は OSS CLI の `llm-task-router` にある `article:refine` です。

なお、ここで扱うのは **文章品質の改善ループ** です。  
**事実検証、RAG の精度向上、最新情報保証そのものは対象外** とします。

:::note info
本稿の関心は「より読みやすく、構成がよく、指摘に基づいて改善される記事」をどう安定的に作るかです。  
「内容が真実かどうか」を自動で保証する話ではありません。
:::

## 導入: なぜ「一発生成」では品質が頭打ちになるのか

一発生成の良さは明快です。

- 実装が簡単
- 速度が出る
- MVP を作りやすい
- まず成果物を見られる

しかし、品質をもう一段上げたいとき、プロンプト調整だけでは伸びが鈍ります。特に記事系タスクでは、以下が残りやすいです。

- 重要な観点が抜ける
- 同じことを言い換えて長くなる
- 見出し構成が読者の理解順になっていない
- 想定読者の前提知識がズレる
- 結論はあるが、途中の説得力が弱い

これは不思議ではありません。  
人間でも、初稿だけで完成度の高い記事になることは稀だからです。

そのため、「生成モデルをもっと賢くする」よりも、**生成物に対してレビュー工程を足す**ほうが現実的なことがあります。LLMに対しても、

- 書く役
- 評価する役
- 指摘をもとに直す役

を分けると、改善のレバーが増えます。

本記事のスコープはあくまでここです。  
**文章品質を上げるループ**であって、**事実性の担保や検索補強の設計**までは扱いません。

## 題材: `llm-task-router` の `article:refine` が解こうとしている問題

`article:refine` は、既にある生成済み記事に対して、

1. 別モデルまたは別タスクで評価する
2. 修正指示を作る
3. 書き直す
4. 必要なら繰り返す

という CLI コマンドです。

ここで重要なのは、**巨大な新フレームワークを増やしていない**ことです。方針はかなり Thin です。

- 既存の評価タスクを使う
- 既存の書き直しタスクを使う
- その間をループで束ねる

これにより、次の資産を再利用できます。

- 既存のプロンプト
- 既存のモデル選定
- 既存の API 呼び出し基盤
- 既存の運用ノウハウ

つまり、「新しい頭の良い仕組み」を大きく足すのではなく、**すでに持っている部品を再構成して品質改善ループを作る**発想です。

CLI として見ると、理論的な最適性よりも次が重要になります。

- 再実行できる
- 途中で落ちても追える
- 閾値を調整できる
- なぜ止まったか説明できる

このあたりは、実務で回すツールとしてかなり効いてきます。

## 全体設計: 1ラウンド = evaluate 1回、必要なら revise 1回

ループの基本単位はシンプルです。

- `evaluate`: 記事を採点し、問題点を抽出する
- `revise`: 指摘をもとに記事を書き直す

ただし、実装のラウンド定義は少し大事です。  
**1ラウンド = evaluate 1回** です。各ラウンドは、

1. 現在の記事を評価する
2. 停止条件を満たせばそこで終了する
3. まだ続けるなら、その評価から修正指示を作って 1 回だけ書き直す

という流れになっています。

つまり、**各ラウンドで「修正前評価」と「修正後評価」を 2 回まわす構造ではありません**。  
あるラウンドで作られた修正版は、**次ラウンドの evaluate が採点**します。前後比較も「同一ラウンド内の before/after」ではなく、**隣接ラウンドの score** で見ます。

この設計だと、

- `max-rounds` = evaluate の最大回数
- revise は最大で `max-rounds - 1` 回
- 総モデルコール数は最大 `2n - 1`

になります。たとえば `max-rounds = 3` なら、

- evaluate 3回
- revise 2回

で、合計 5 コールです。

これは「コスト最適化のための特殊版」ではなく、`article:refine` の標準動作そのものです。  
責務を明確に分けておくと、ループ部分は薄く保てます。

- 採点器: 評価・指摘抽出
- 修正器: 指摘に基づく書き直し
- オーケストレーション: 停止判定とファイル管理

この分離を守ると、評価プロンプトや修正プロンプトの改善と、ループ制御の改善を別々に扱えます。

## 停止条件の設計: 6種類に分けて判断を明示する

自動ループで大事なのは、「どう回すか」以上に **どう止めるか** です。  
停止理由を曖昧にせず、列挙型のように明示しておくと運用がかなり楽になります。

`article:refine` では次の 6 種類を使います。

- `clean`
- `approved`
- `regressed`
- `stalled`
- `max-rounds`
- `no-instruction`

そして判定順も重要です。実装の優先順位は次のとおりです。

1. `clean`
2. `approved`
3. `regressed`
4. `stalled`
5. `max-rounds`
6. ただし続行時に「次の修正指示が空」なら `no-instruction`

要点は、**成功条件である `clean` / `approved` を、悪化や停滞より先に見る**ことです。  
スコア比較だけを先にすると、実質的には十分公開可能な記事を不要に止めることがあります。

### `clean` の定義

`clean` は固定的に「critical / major / minor が 0 件」という意味ではありません。  
実装では **`--min-severity` 以上の指摘が 0 件** で判定します。

既定値は `major` なので、デフォルト運用では「major 以上が無ければ clean」です。  
しかしこれはオプションで変えられます。

たとえば:

- `--min-severity major`  
  → major / critical が 0 件なら clean
- `--min-severity minor`  
  → minor / major / critical が 0 件なら clean

という具合です。

### `approved` の定義

`approved` はスコア閾値で判定するわけではありません。  
**judge が返す `approved: true` という真偽値**で判定します。

つまり `--until approved` のときは、「スコアが何点以下なら承認」ではなく、**評価モデルが承認フラグを立てたか**を見ます。

### `regressed` / `stalled`

この 2 つは、ラウンドをまたいだ score の比較で判定します。

- `regressed`: 直前ラウンドより明確に悪化
- `stalled`: 改善とみなせないラウンドが 2 連続

後述しますが、ここでは単純な絶対差だけでなく、**相対 + 絶対の両方**を使います。

### `max-rounds`

`max-rounds` は、特別な文脈ではなくそのままです。  
**evaluate の回数が上限に達したら打ち切る**、という意味です。

「最後のラウンドが improved で継続した結果だけに起きる」といった説明は、実装の読みとしては強すぎます。実際には、評価回数が上限に達した時点で停止です。

### `no-instruction`

`no-instruction` は、judge が非承認でループを続けたいのに、**具体的な修正指示が空で次の revise を作れない**ときに止まる理由です。

これは特に `--until approved` で重要です。  
`approved = false` なのに指摘がゼロ、あるいは修正アクションに落ちない評価しか返らないと、ループがデッドロックします。そこを明示的に止めるための理由が `no-instruction` です。

## スコアの考え方: これは「品質スコア」ではなく「問題量スコア」

ここで使うスコアは、**高いほど良い品質スコアではありません**。  
評価で見つかった指摘の重み合計であり、言い換えると **「悪さの量」** です。

- 低いほど良い
- `0` が理想
- 増えるほど問題が多い
- 減るほど改善している

重みは次のとおりです。

- `critical = 8`
- `major = 4`
- `minor = 2`
- `suggestion = 1`

これは全指摘を対象に合計します。  
`suggestion` もスコアには入ります。

重みがほぼ倍々になっているのは、単に「深刻度が 1 段上がると、複数の軽微指摘より重く見たい」ためです。  
たとえば major 1件を suggestion 4件より重く見たい、といった運用感に合わせやすくなります。

```ts
type Severity = "critical" | "major" | "minor" | "suggestion";

type Finding = {
  severity: Severity;
  message: string;
};

type EvaluationResult = {
  approved: boolean;
  findings: Finding[];
  summary: string;
};

const SEVERITY_WEIGHT: Record<Severity, number> = {
  critical: 8,
  major: 4,
  minor: 2,
  suggestion: 1,
};

function issueScore(evaluation: EvaluationResult): number {
  return evaluation.findings.reduce((sum, finding) => {
    return sum + SEVERITY_WEIGHT[finding.severity];
  }, 0);
}
```

## LLM-as-Judge の揺れにどう向き合うか

LLM-as-Judge を使うと避けて通れないのが、**評価出力の揺れ**です。

同じ記事でも、実行タイミングやモデルの非決定性で次のような差が出ます。

- minor 指摘が 1 件増える
- 同じ問題を major と見る回と minor と見る回がある
- 表現の違いで件数だけ増減する
- 要約文は変わるが、本質的な評価は同じ

このとき、単純に「指摘件数が増えたら悪化」とすると、不要停止が多発します。  
特に minor が 1 件増えただけで `regressed` にすると、実運用ではかなりうるさいです。

そこで、severity 付きの重み合計に加えて、**改善・悪化判定にヒステリシスを入れる**のが効きます。  
実装の既定値は、絶対値だけではなく **相対 + 絶対の併用**です。

- 改善とみなす  
  → 直前ラウンド比で **5%以上** かつ **1以上** score が下がった
- 悪化 (`regressed`) とみなす  
  → 直前ラウンド比で **25%以上** かつ **2以上** score が上がった
- `stalled`  
  → **改善とみなせないラウンドが 2 連続**したら停止

ここで大事なのは、`stalled` が **1ラウンド内の before/after 差**ではないことです。  
実装では、**ラウンドをまたいだ連続非改善**で見ています。

たとえば score の推移がこうなら:

- r1: 12
- r2: 11
- r3: 11

r1→r2 の改善幅は 1 ですが、8.3% 改善なので「改善」とみなせます。  
一方で 5% 未満しか下がらない、または全く変わらないラウンドが続くと、2 連続で `stalled` になります。

以下は、その比較ロジックを表した最小例です。

```ts
type ScoreTrend = "improved" | "not-improved" | "regressed";

const MIN_IMPROVEMENT_RATIO = 0.05;
const MIN_IMPROVEMENT_ABS = 1;
const MIN_REGRESSION_RATIO = 0.25;
const MIN_REGRESSION_ABS = 2;

function classifyScoreTrend(previous: number, current: number): ScoreTrend {
  const delta = current - previous;

  const improved =
    delta <= -MIN_IMPROVEMENT_ABS &&
    (-delta / Math.max(previous, 1)) >= MIN_IMPROVEMENT_RATIO;

  if (improved) return "improved";

  const regressed =
    delta >= MIN_REGRESSION_ABS &&
    (delta / Math.max(previous, 1)) >= MIN_REGRESSION_RATIO;

  if (regressed) return "regressed";

  return "not-improved";
}
```

:::note warn
重みやしきい値は普遍的な正解ではありません。  
ただし `article:refine` の既定挙動を説明するなら、絶対差だけではなく「相対 + 絶対」を併用している点を落とさないほうが重要です。
:::

## 実装の中核: TypeScript で書く evaluate → revise ループ

ここからは、CLI 実装に近い形で型付きコードを見ます。  
I/O 補助や API 呼び出しラッパーは省き、制御フローに絞ります。

:::note info
以下のコードは、制御フローの骨子を説明するためのスタブです。  
そのままでは実行できません。ファイル I/O、モデル呼び出し、run ディレクトリ解決、`writeMeta` などは別途実装が必要です。
:::

まず、扱う型をそろえます。

```ts
type StopReason =
  | "clean"
  | "approved"
  | "regressed"
  | "stalled"
  | "max-rounds"
  | "no-instruction";

type Severity = "critical" | "major" | "minor" | "suggestion";

type Finding = {
  id: string;
  severity: Severity;
  message: string;
  section?: string;
};

type EvaluationResult = {
  approved: boolean;
  findings: Finding[];
  summary: string;
  model: string;
  createdAt: string;
};

type RevisionInstruction = {
  bullets: string[];
  preserve: string[];
  model: string;
  createdAt: string;
};

type RoundRefineRecord = {
  round: number;
  evaluation: {
    provider: string;
    model: string;
    elapsedMs: number;
    costUsd?: number;
    score: number;
    approved: boolean;
    findingsCount: number;
  };
  revision?: {
    provider: string;
    model: string;
    elapsedMs: number;
    costUsd?: number;
    instructionPath: string;
    beforePath: string;
  };
};

type RefineMeta = {
  task: "article:refine";
  maxRounds: number;
  minSeverity: Severity;
  refine: RoundRefineRecord[];
  stoppedReason?: StopReason;
};

type ScoreTrend = "improved" | "not-improved" | "regressed";

const SEVERITY_WEIGHT: Record<Severity, number> = {
  critical: 8,
  major: 4,
  minor: 2,
  suggestion: 1,
};

const MIN_IMPROVEMENT_RATIO = 0.05;
const MIN_IMPROVEMENT_ABS = 1;
const MIN_REGRESSION_RATIO = 0.25;
const MIN_REGRESSION_ABS = 2;

function issueScore(evaluation: EvaluationResult): number {
  return evaluation.findings.reduce(
    (sum, f) => sum + SEVERITY_WEIGHT[f.severity],
    0
  );
}

function severityRank(severity: Severity): number {
  return {
    suggestion: 1,
    minor: 2,
    major: 3,
    critical: 4,
  }[severity];
}

function isClean(
  evaluation: EvaluationResult,
  minSeverity: Severity
): boolean {
  const threshold = severityRank(minSeverity);
  return evaluation.findings.every((f) => severityRank(f.severity) < threshold);
}

function classifyScoreTrend(previous: number, current: number): ScoreTrend {
  const delta = current - previous;

  const improved =
    delta <= -MIN_IMPROVEMENT_ABS &&
    (-delta / Math.max(previous, 1)) >= MIN_IMPROVEMENT_RATIO;

  if (improved) return "improved";

  const regressed =
    delta >= MIN_REGRESSION_ABS &&
    (delta / Math.max(previous, 1)) >= MIN_REGRESSION_RATIO;

  if (regressed) return "regressed";

  return "not-improved";
}
```

続いて、ループ本体です。  
ポイントは次の 3 つです。

- 1ラウンドにつき evaluate は 1回
- revise 結果は次ラウンドで評価する
- `regressed` でも **巻き戻さず最新版を返す**

```ts
async function refineArticle(
  initialArticle: string,
  meta: RefineMeta
): Promise<{ article: string; stopReason: StopReason; meta: RefineMeta }> {
  let currentArticle = initialArticle;
  let previousScore: number | undefined;
  let consecutiveNotImproved = 0;

  for (let round = 1; round <= meta.maxRounds; round++) {
    const evaluation = await evaluateArticle(currentArticle);
    const score = issueScore(evaluation);

    await saveJson(`refine-r${round}-review.json`, evaluation);
    await saveText(`refine-r${round}-review.md`, renderReviewMarkdown(evaluation));

    const record: RoundRefineRecord = {
      round,
      evaluation: {
        provider: "judge-provider",
        model: evaluation.model,
        elapsedMs: 0,
        costUsd: 0,
        score,
        approved: evaluation.approved,
        findingsCount: evaluation.findings.length,
      },
    };

    meta.refine.push(record);
    await writeMeta(meta);

    if (isClean(evaluation, meta.minSeverity)) {
      await finalizeRun(currentArticle, evaluation, meta, "clean");
      return { article: currentArticle, stopReason: "clean", meta };
    }

    if (evaluation.approved) {
      await finalizeRun(currentArticle, evaluation, meta, "approved");
      return { article: currentArticle, stopReason: "approved", meta };
    }

    if (previousScore !== undefined) {
      const trend = classifyScoreTrend(previousScore, score);

      if (trend === "regressed") {
        await finalizeRun(currentArticle, evaluation, meta, "regressed");
        return { article: currentArticle, stopReason: "regressed", meta };
      }

      if (trend === "improved") {
        consecutiveNotImproved = 0;
      } else {
        consecutiveNotImproved += 1;
        if (consecutiveNotImproved >= 2) {
          await finalizeRun(currentArticle, evaluation, meta, "stalled");
          return { article: currentArticle, stopReason: "stalled", meta };
        }
      }
    }

    if (round === meta.maxRounds) {
      await finalizeRun(currentArticle, evaluation, meta, "max-rounds");
      return { article: currentArticle, stopReason: "max-rounds", meta };
    }

    const instruction = await buildRevisionInstruction(evaluation, currentArticle);

    if (instruction.bullets.length === 0) {
      await finalizeRun(currentArticle, evaluation, meta, "no-instruction");
      return { article: currentArticle, stopReason: "no-instruction", meta };
    }

    await saveText(`refine-r${round}-instruction.md`, renderInstructionMarkdown(instruction));
    await saveText(`refine-r${round}-before.md`, currentArticle);

    record.revision = {
      provider: "writer-provider",
      model: instruction.model,
      elapsedMs: 0,
      costUsd: 0,
      instructionPath: `refine-r${round}-instruction.md`,
      beforePath: `refine-r${round}-before.md`,
    };
    await writeMeta(meta);

    currentArticle = await reviseArticle(currentArticle, instruction);
    previousScore = score;

    await writeMeta(meta);
  }

  throw new Error("unreachable");
}
```

この流れだと、停止判定の順序が実装と揃います。

1. 評価結果を保存
2. `clean`
3. `approved`
4. 直前ラウンドとの比較で `regressed`
5. 連続非改善で `stalled`
6. 上限到達で `max-rounds`
7. まだ続けるなら instruction 生成
8. 空なら `no-instruction`
9. 書き直して次ラウンドへ

ここで特に重要なのは、**`regressed` でも `currentArticle` を巻き戻さない**ことです。  
そのラウンドで評価した最新版のまま止め、前の版は `refine-r<N>-before.md` として残します。

## 成果物の残し方: run ディレクトリ直下にフラット命名で保存する

実装では、成果物を `round-01/` のようなサブディレクトリに分けず、**run ディレクトリ直下にフラットなファイル名**で残します。

各ラウンドで主に出るのは次です。

- `refine-r<N>-review.json`
- `refine-r<N>-review.md`
- `refine-r<N>-instruction.md`
- `refine-r<N>-before.md`

全体としてはさらに:

- `refine-summary.md`
- `final-review.json`
- `final-review.md`
- `final.md`
- `meta.json`

が残ります。

`final-review.json` / `final-review.md` は、**最終ラウンドの評価の複製**です。  
また、履歴は `meta.json` の `refine` フィールドに逐次保存されます。ここには各ラウンドの evaluation / revision について、

- provider
- model
- elapsedMs
- costUsd
- score
- approved
- findingsCount

などが入ります。

概念図としてサブディレクトリを描くこと自体は分かりやすいのですが、実装説明としては「実際はフラット命名」と明記しておくほうが親切です。

## 中断耐性: meta を逐次書き、完了フラグは最後に立てる

CLI 運用では、中断耐性がかなり重要です。  
モデル呼び出しはネットワークやレート制限、タイムアウト、プロセス終了などで簡単に落ちます。

`article:refine` では、各ラウンドで少なくとも次のタイミングで `meta.json` を逐次更新します。

- 評価結果を追加した直後
- 修正結果を反映した直後
- 停止時

これにより、途中でプロセスが落ちても「どこまで進んだか」が追えます。

また、停止時の確定処理は順番が大事です。  
実装の考え方は次です。

1. 最終フィールドをローカルで算出する
2. 成果物 (`final.md` / `final-review.*` / `refine-summary.md`) を先に生成する
3. 完了状態の meta を最後に書き込む

こうしておくと、**meta だけ完了扱いなのに成果物が無い**状態を避けられます。

さらに、`meta.json` は `stoppedReason` の有無で状態判定できます。

- `stoppedReason` あり  
  → 完了済み
- `stoppedReason` なし  
  → 実行中または中断

最小イメージはこんな感じです。

```ts
async function finalizeRun(
  finalArticle: string,
  finalEvaluation: EvaluationResult,
  meta: RefineMeta,
  stopReason: StopReason
): Promise<void> {
  const summary = renderRefineSummary(meta, stopReason, finalEvaluation);

  await saveText("final.md", finalArticle);
  await saveJson("final-review.json", finalEvaluation);
  await saveText("final-review.md", renderReviewMarkdown(finalEvaluation));
  await saveText("refine-summary.md", summary);

  meta.stoppedReason = stopReason;
  await writeMeta(meta);
}
```

:::note info
この順番にしておくと、障害時の観測が楽になります。  
完了フラグだけ先に書いてしまうと、あとから見たときに「成功したのに成果物が無い」状態を作ってしまいます。
:::

## なぜミッドループで自動巻き戻ししないのか

悪化したら「前ラウンドの良かった版に自動で戻せばよいのでは」と考えたくなります。  
実際、発想としては自然です。

ただ、`article:refine` では**ミッドループで自動巻き戻ししない**設計にしています。

理由は 3 つあります。

### 1. 評価の揺れで、本当に悪化したか確実ではない

LLM-as-Judge の評価は揺れます。  
あるラウンドで悪化に見えても、別実行では同等か改善と出る可能性があります。

この状態で自動巻き戻しまで入れると、

- 悪化判定
- 巻き戻し候補の選定
- 再評価
- 再挑戦

という状態遷移が増え、制御が急に複雑になります。

### 2. 巻き戻し後の再挑戦戦略まで入れると設計が膨らむ

巻き戻すだけならまだしも、その後に

- 同じ指示で再試行するのか
- 別の指示を再生成するのか
- 評価モデルも変えるのか
- 何回までやるのか

といった論点が出ます。  
停止条件や履歴管理も一段難しくなります。

### 3. 最終責任は人が持つべき場面がある

記事品質は、最終的には人が責任を持つべきことがあります。  
そのため、悪化検知は「自動修復のトリガー」より、**人に渡すトリガー**として使うほうが安全です。

ここで実装上いちばん大事なのは、**止めるだけで巻き戻さない**ことです。

- `regressed` を検出したらループは停止する
- その時点の最新版が `final.md` になる
- 悪化前の候補は `refine-r<N>-before.md` として残る
- どれを採用するかは人が手で選ぶ

つまり設計としては、

- ミッドループでは `regressed` で止める
- 悪化前・悪化後の比較材料は残す
- ただし最終返却は常に最新版
- 採用判断は人に渡す

となっています。

この割り切りのおかげで、ループ制御は薄く保てます。

## `clean` と `approved` の役割分担

`clean` と `approved` は似て見えますが、役割が違います。

- `clean`  
  → `--min-severity` 以上の指摘が 0 件
- `approved`  
  → judge が `approved: true` を返した

つまり `clean` は、比較的機械的なルールです。  
一方 `approved` は、judge の総合判断を止める条件として使います。

この分離には実務上の利点があります。

- `clean` は厳密な下限として使える
- `approved` は媒体やタスクに応じた運用判断を載せられる
- ループの停止条件を「スコア一点張り」にしなくて済む

特に `--until approved` では、**スコア閾値を自前で再発明しなくてよい**のが扱いやすいです。

## `no-instruction` は連携不全のシグナル

`approved = false` なのに、修正指示が空。  
この `no-instruction` は地味ですが重要です。

典型例は次のようなものです。

- 指摘が抽象的すぎる
  - 例: 「全体に説得力が弱い」
- 修正対象が特定できない
  - 例: 「もっと読みやすく」
- judge は非承認だが、具体的な行動に落ちない
  - 例: 「やや説明不足」

こうなると修正器は、何をどこまで直すべきか判断できません。

特に `--until approved` では、approved されないのに次の revise も作れず、ループが前に進まなくなります。  
そのデッドロックを明示的に止めるのが `no-instruction` です。

対策としては、評価プロンプト側で以下を要求すると改善しやすいです。

- 問題箇所の見出しや段落を特定する
- 問題の理由を短く述べる
- 具体的な修正アクションに変換できる粒度で書く

## 運用上のコツと限界

この仕組みを実運用に載せるうえで、いくつかコツがあります。

### 評価プロンプトは観点を固定する

抽象的な感想を求めると、評価の揺れが大きくなります。  
たとえば次の観点を固定すると安定しやすいです。

- 読者前提は適切か
- 構成順は自然か
- 重複説明はないか
- 曖昧表現はないか
- 具体例は足りているか

「良い悪いを自由に述べて」より、チェックリスト型のほうが扱いやすいです。

### 修正プロンプトには破壊制約を入れる

修正器は、直すつもりで全体を壊すことがあります。  
そのため次のような制約が有効です。

- 元の良い点を壊しすぎない
- 指摘がない箇所はむやみに変えない
- 見出し構造を維持する
- 不確かな情報を勝手に追加しない

これだけで、不要な変形がかなり減ります。

### `min-severity` と `approved` は媒体ごとに変える

止め方は記事の種類で変わります。

- 個人ブログ: 多少 rough でも勢い重視
- 社内ナレッジ: 冗長でも取りこぼしが少ない方がよい
- 公開技術記事: 読者前提や誤解の少なさを重視

そのため、

- `--min-severity`
- `--until approved`
- judge プロンプトの承認基準

を記事種別ごとに持つほうが現実的です。

### `no-instruction` が多いなら judge 側を直す

`no-instruction` が多いなら、修正器より先に評価器を見直すべきです。  
抽象批評を増やすより、

- 問題箇所の特定
- severity の付与
- 修正アクションに落ちる表現

を強制したほうがループ全体は安定します。

### この仕組みが解決しないこともある

このループは、文章品質の底上げには効きます。  
ただし、次は別問題です。

- 事実誤認
- 最新情報の保証
- 一次情報確認
- 独自知見の不足
- 実経験の薄さ

つまり、**万能な AI 編集部**ではありません。  
現実的には、**人間編集の前段を整える自動推敲**として位置付けるのがちょうどよいです。

## まとめ: 薄いループ追加でも品質改善の余地は大きい

記事生成の品質を安定して引き上げるには、一発生成の賢さだけを追い続けるより、**evaluate → revise の反復**を薄く追加するほうが、実装効率と運用性のバランスが取りやすいです。

特に `article:refine` の実装で肝になるのは次の点です。

- 1ラウンド = evaluate 1回、必要なら revise 1回
- 停止条件は `clean → approved → regressed → stalled → max-rounds` を軸に判定する
- `clean` は `--min-severity` 以上の指摘が 0 件
- `approved` はスコア閾値ではなく judge の真偽値
- 改善・悪化判定は相対 + 絶対のヒステリシスで見る
- `stalled` はラウンドをまたいだ連続非改善で止める
- `regressed` でも自動巻き戻しはせず、最新版をそのまま返す
- 成果物と `meta.json` を逐次残して中断耐性を持たせる

`article:refine` の実務的な価値は、これを巨大な新機構ではなく、**既存タスクの組み合わせ**で実現している点にあります。

最初から全部盛りにする必要はありません。  
まずは小さく始めるのがおすすめです。

1. 1記事種別だけ対象にする
2. 評価軸を 1 つか 2 つに絞る
3. まずは `clean` と `approved` を安定させる
4. ログを見ながら judge と revise のプロンプトを調整する
5. 必要に応じて `stalled / regressed / no-instruction` の扱いを詰める

一発生成をやめる、というより、**一発生成を完成品扱いしない**ことがポイントです。  
生成のあとに「見る」「直す」の工程を薄く足すだけでも、記事品質の改善余地はかなりあります。
