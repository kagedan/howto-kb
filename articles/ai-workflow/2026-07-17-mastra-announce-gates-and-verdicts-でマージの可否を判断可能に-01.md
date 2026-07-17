---
id: "2026-07-17-mastra-announce-gates-and-verdicts-でマージの可否を判断可能に-01"
title: "[Mastra Announce] Gates and Verdicts で「マージの可否」を判断可能に"
url: "https://zenn.dev/shiromizuj/articles/979eadd8c5bbaf"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "LLM", "zenn"]
date_published: "2026-07-17"
date_collected: "2026-07-18"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で公開された [Features](https://mastra.ai/blog/category/features) 記事をもとに、今回の発表が何を解決するのかを整理します。今回は新しいモデル機能ではなく、**AI エージェントのテストをソフトウェア開発の通常の品質ゲートに近づけるための追加**です。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

2026年7月13日、Mastra は **Introducing Gates and Verdicts for Mastra Evals** を公開しました。

ひとことで言うと、今回の追加は **「AI の評価結果を CI の判定信号へ変換する仕組み」** です。

Mastra にはもともと scorers がありました。回答の完全性やトーン、faithfulness のような品質を数値で測ることはできたわけです。しかし、そこから先の **「ではこの PR を落とすのか、通すのか」** は、開発者側で毎回ロジックを書く必要がありました。

今回追加された `gates` と `verdict` は、その最後のひと手間を標準化します。

---

## 先に結論

今回うれしいのは、Mastra の evals が単なる「スコア表示」から、**マージ可否を判断できるテスト基盤** に一段進んだことです。

具体的には次の 3 点が大きいです。

1. **必須条件** と **品質目標** を分けて書ける
2. `runEvals()` が **`passed` / `scored` / `failed`** の 3 値を返す
3. CI で「即落とすべき回帰」と「まず観測したい品質低下」を分離できる

この 3 点がそろうと、AI エージェントのテストがかなり実務的になります。

---

## これまで何が課題だったのか

### 1. AI のテストは「全部 boolean」にしにくい

普通のソフトウェアテストは、だいたい yes / no で切れます。

* この関数は正しい値を返したか
* この API は 200 を返したか
* この UI は特定の要素を描画したか

ところが AI エージェントは違います。

* 正しいツールを呼んだか
* ツール呼び出し中にエラーを出していないか
* 回答は十分に完全か
* 口調は適切か
* 幻覚は少ないか

このうち前半は比較的 **決定的** に判定できますが、後半は **非決定的** です。0/1 ではなく、「だいたい 0.82 だから許容」「0.61 だと怪しい」といった世界になります。

つまり AI テストは最初から、**ハードな pass/fail 条件** と **連続値の品質指標** が混ざっています。

### 2. 従来は scorer の結果を人間が束ねる必要があった

Mastra の scorer 自体は以前から強力でした。しかし困るのは、その先です。

たとえば次のような条件を考えます。

* weather agent は必ず `weatherTool` を呼ぶこと
* tool error は 0 件であること
* 回答の completeness は 0.7 以上
* tone は 0.5 以上

こうした条件を `runEvals()` で評価したあと、従来は開発者が

* どれを必須失敗にするか
* どれは警告に留めるか
* どの組み合わせなら CI を落とすか

を毎回自分で書く必要がありました。

言い換えると、**Mastra はスコアを返してくれるが、品質ゲートの意味づけは自前だった**わけです。

### 3. 品質低下を検知したいだけなのに、全部「失敗」に寄りがちだった

AI 開発ではよく次の悩みが出ます。

* ツールを呼ばないのは即バグなので落としたい
* でもトーンが少し下がっただけで毎回 CI を赤くすると運用が重い
* かといって品質低下を完全に無視したいわけでもない

従来のテスト設計だと、このあたりの表現が不器用でした。

* 厳しくしすぎると CI が壊れやすい
* 緩くしすぎると回帰を見逃す
* 結局、しきい値評価が「参考情報」で終わりやすい

今回の `scored` は、まさにこの中間地帯を扱うための答えです。

---

## 今回の対応で何が入ったのか

Mastra docs の表現を借りると、`gates` と `verdict` は `runEvals()` に **severity semantics** を与える仕組みです。

### `gates`

`gates` は **1.0 でなければならない hard requirement** です。

たとえば次のようなものを置きます。

* 正しいツールを呼んだか
* ツールエラーがなかったか
* 特定文字列を含むか
* 出力形式が決まったルールを満たすか

ここは「品質がちょっと低い」ではなく、**仕様を満たしたかどうか** を見る層です。

### `scorers` + `threshold`

一方で `scorers` は、もともと Mastra が得意だった品質評価です。

* completeness
* tone
* faithfulness
* hallucination

などを数値化し、そのスコアに対して `threshold` を置けます。

ここで重要なのは、threshold は gate とは違って「絶対に 1.0 であるべき」ではないことです。たとえば「faithfulness は 0.7 以上なら合格」といった **業務上の最低ライン** を表現します。

### `verdict`

そして最終的に `runEvals()` は `verdict` を返します。

* `failed`
  + 1 つ以上の gate が平均 `1.0` を下回った
* `scored`
  + gate は全部通ったが、1 つ以上の threshold を満たさなかった
* `passed`

この 3 値設計が非常に良いです。

なぜなら、AI エージェントの品質問題には

* **即座に止めるべき壊れ方**
* **検知はしたいが、すぐ全体停止にしなくてもよい劣化**

の 2 種類があるからです。

---

## いちばん嬉しいのは「必須失敗」と「品質ドリフト」を分離できること

今回の発表の本質はここだと思います。

### `failed` は「壊れた」

たとえば、

* 検索エージェントが検索ツールを呼ばない
* DB エージェントが SQL ツール実行でエラーを出す
* structured output が必要なのに形式を守らない

こういうのは品質というより **機能不全** です。ここは gate で止めるべきです。

### `scored` は「壊れてはいないが、怪しい」

一方で、

* 回答が少し冗長になった
* completeness が 0.72 から 0.64 に落ちた
* tone が期待より少しぶれた

こういうのは、すぐに deploy blocker にするかは文脈次第です。

ただし無視すると、あとでじわじわ品質が下がります。これが **quality drift** です。

`scored` はこの drift を拾うための状態です。つまり、

* 今すぐ壊れてはいない
* でも前より悪い
* だからログに残す、PR コメントする、Slack 通知する

という運用がしやすくなります。

これまではこの中間状態を自前で設計する必要がありました。今回からは Mastra が標準で持ちます。

---

## 周辺知識: そもそも `Quick Checks` は何なのか

今回のサンプルでは `checks.calledTool()` や `checks.noToolErrors()` が使われています。これは `Quick Checks` です。

Quick Checks は docs 上で **Zero-LLM micro-scorers** と説明されています。つまり、

* LLM judge を呼ばない
* 軽い
* 速い
* 決定的

という特徴を持つ小さな評価器です。

`gates` との相性が良いのは当然で、**「必須条件を CI で高速に落としたい」** という用途にぴったりです。

逆に、

のような評価は Quick Checks だけでは苦しいので、ここは scorer と threshold の領域になります。

要するに、今回の設計は次の住み分けです。

* 決定的・安価・高速: `gates` + `Quick Checks`
* 非決定的・意味評価: `scorers` + `threshold`

かなり筋が良い分担です。

---

## コードで見ると何が変わるか

公式サンプルの趣旨を、日本語の説明に寄せて書くと次のようになります。

```
import { describe, expect, it } from "vitest";
import { runEvals } from "@mastra/core/evals";
import { checks } from "@mastra/evals/checks";
import {
  createCompletenessScorer,
  createToneScorer,
} from "@mastra/evals/scorers/prebuilt";
import { weatherAgent } from "./weather-agent";

const data = [
  { input: "Paris の天気を教えて" },
  { input: "今日の東京の天気は？" },
  { input: "Seattle は雨？" },
];

describe("天気エージェントの回帰テスト", () => {
  it("必須の動作を満たす", async () => {
    const result = await runEvals({
      data,
      target: weatherAgent,
      gates: [
        checks.calledTool("weatherTool"),
        checks.noToolErrors(),
      ],
    });

    expect(result.verdict).not.toBe("failed");
  });

  it("品質低下は検知しつつ、即失敗にはしない", async () => {
    const result = await runEvals({
      data,
      target: weatherAgent,
      gates: [
        checks.calledTool("weatherTool"),
        checks.noToolErrors(),
      ],
      scorers: [
        { scorer: createCompletenessScorer(), threshold: 0.7 },
        { scorer: createToneScorer(), threshold: 0.5 },
      ],
    });

    // gate 失敗は即バグとして扱う
    expect(result.verdict).not.toBe("failed");

    // しきい値未達は品質低下として記録する
    if (result.verdict === "scored") {
      console.warn("品質しきい値を満たさない項目があります", result.thresholdResults);
    }
  });
});
```

このコードの重要点は、`expect` の書き方が簡単になっていることです。

以前なら、

* gate 相当の項目を自分で `every()` で確認する
* scorer ごとに threshold 判定を書く
* 最後にそれらをまとめて CI の成否へ変換する

という作業が必要でした。

今回からは `result.verdict` を中心に据えるだけでよくなります。

これは単なる省コード化ではありません。**「AI テストの意味論をチーム内で共有しやすくなる」** のが大きいです。

---

## 何が嬉しくなったのかを、開発フロー目線で整理する

### 1. PR で落とすべきものが明確になる

`gates` は hard requirement です。つまり、チームで

* これは仕様
* これは壊れたら merge してはいけない

というルールをコード化しやすくなります。

AI エージェント開発でよくある「たまたま今回は通った」「なんとなく雰囲気で見ている」を減らせます。

### 2. 品質改善を“赤か緑か”以外で扱える

`scored` があるので、

* しきい値未達をまず観測
* 数週間トレンドを見る
* 安定して悪化するなら gate 化する

という段階的運用ができます。

これは現実的です。AI 品質は最初から全項目を厳格 gate にすると、ノイズが多すぎて回りません。

### 3. CI との接続が自然になる

Mastra docs でも、gates と verdict は **CI で hard requirement を enforce する** ことを明確に想定しています。

つまり今回の追加で、Mastra evals は

* notebook 的な評価
* Studio 上の観察

だけでなく、

として扱いやすくなりました。

### 4. 「何がダメだったか」をログとして残しやすい

結果には `gateResults` と `thresholdResults` が返ります。

そのため、ただ `failed` と言うだけでなく、

* どの gate が落ちたか
* どの scorer が threshold 未達だったか

をそのまま CI ログや PR コメントへ流せます。

AI テストは opaque になりがちですが、ここが見えるのはかなり大事です。

---

## 今回の追加は「scorer の代替」ではなく「上位レイヤ」

誤解しやすい点ですが、gates / verdict が入ったから scorer が不要になったわけではありません。

関係は次のように整理すると分かりやすいです。

* scorer
* threshold
* gate
* verdict

つまり今回増えたのは、新しい計測器というより **計測結果の運用レイヤ** です。

Mastra の evals が「採点」から「意思決定」へ半歩進んだ、と言ってよいと思います。

---

## 実運用での勘所

### gate を増やしすぎない

gate は便利ですが、何でも gate にすると CI が brittle になります。

おすすめの切り分けは次の通りです。

* 仕様違反、ツール未使用、エラー発生、フォーマット破壊
* completeness、tone、faithfulness、verbosity

「壊れている」と「少し悪い」を混ぜないのが大事です。

### threshold は最初から理想値にしない

threshold は、理想値より **最低許容ライン** として決める方がうまく回ります。

最初から厳しすぎる値を置くと、`scored` だらけになってログが意味を失います。

### データセット品質の方が支配的なこともある

これは eval 全般の注意点ですが、どんなに仕組みが良くても、評価データが雑だと判定も雑になります。

* 代表的なケースを含んでいるか
* 失敗してほしいケースが入っているか
* 言い換えや typo を含んでいるか

の方が、しばしば gate/verdict の設計以上に重要です。

---

## 位置づけ: Mastra evals はどこへ向かっているのか

Mastra docs 全体を見ると、evals はかなりレイヤ分けされてきています。

* Quick Checks
* Built-in / custom scorers
* Gates and Verdicts
* Running in CI
* Studio / trace evaluations

この流れはかなり自然です。

AI エージェントの評価は、

1. 測る
2. 判定する
3. 開発フローへ組み込む

の 3 段が必要です。今回の `gates` と `verdict` は、その 2 と 3 の間をきれいにつないでいます。

---

## まとめ

今回の発表で本当に嬉しいのは、Mastra が「AI の品質を測れる」だけでなく、**「どの劣化なら止めるべきか」を標準 API で表現できるようになった**ことです。

これまでの課題は、scorer の結果を最終的なテスト判定へ変換する責務が利用者側に残っていたことでした。今回の対応で、

* hard requirement は `gates`
* 品質目標は `threshold`
* 最終判定は `verdict`

という役割分担が明確になりました。

特に `scored` が入ったことで、**即落とすバグ** と **追跡したい品質ドリフト** を分けて扱えるようになったのが大きいです。これは CI を壊しすぎず、かといって品質低下も見逃さない、かなり実務的な設計です。

派手な機能追加ではありませんが、Mastra を本番開発の品質ゲートへ一歩近づけた、地味に重要なアップデートだと思います。

---

## 関連リンク
