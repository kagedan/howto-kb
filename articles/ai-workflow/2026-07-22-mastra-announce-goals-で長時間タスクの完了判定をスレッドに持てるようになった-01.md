---
id: "2026-07-22-mastra-announce-goals-で長時間タスクの完了判定をスレッドに持てるようになった-01"
title: "[Mastra Announce] Goals で「長時間タスクの完了判定」をスレッドに持てるようになった"
url: "https://zenn.dev/shiromizuj/articles/1333dcccc34169"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "zenn"]
date_published: "2026-07-22"
date_collected: "2026-07-23"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で公開された [Features](https://mastra.ai/blog/category/features) 記事をもとに、今回の発表が何を解決するのかを整理します。今回はモデル追加ではなく、**長時間実行エージェントの完了条件を運用可能にするための実装アップデート**です。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

2026年7月15日、Mastra は **Introducing Goals for Mastra Agents** を公開しました。

ひとことで言うと、今回の追加は **「目標（objective）を毎回プロンプトへ再注入せず、スレッド状態として保持し、ループ内で判定できる仕組み」** です。

---

## 先に結論

今回うれしいのは、Mastra の長時間タスクが「がんばって続ける」から **「いつ終えるかを機械的に判断できる」** に進んだことです。

特に大きいのは次の 4 点です。

1. `setObjective()` で目標をスレッドに永続化できる
2. 各ループで LLM judge が `pass/fail` を返し、継続/終了を決められる
3. `goal` chunk によって、進捗理由と判定根拠をストリームで観測できる
4. `maxRuns` 到達後も objective が保持され、後続 run で再開できる

結果として、**「長いタスクを途中で取りこぼさず、条件付きで回し続ける」** ことが実装しやすくなります。

---

## 背景: これまで何が課題だったのか

### 1. 目的が呼び出し単位で蒸発しやすかった

Goals 以前の代表パターンは次のどちらかでした。

* `.generate()` / `.stream()` のたびに成功条件を再注入
* `isTaskComplete` などを都度組み合わせて判定

この方式だと、長い会話や中断再開を挟む運用で、次の問題が起きます。

* 呼び出しごとに「目的文」を再構成する必要がある
* 条件の再注入漏れで、同じスレッドでも完了基準がぶれる
* 目的管理ロジックがアプリ層に散在し、保守が難しくなる

### 2. 「完了判定」の責務がアプリ側に寄りすぎていた

エージェントを複数回ループさせるとき、本当に必要なのは次の意思決定です。

* もう目標達成したから止めるか
* まだ未達なので次の手を打つか
* 予算到達だが、状態を保って次回再開するか

従来はこの状態遷移を自前実装しがちで、プロンプト設計とアプリ制御が密結合しやすいのが課題でした。

### 3. 進捗観測が「最終テキスト偏重」になりやすかった

長時間タスクでは、最終回答だけでなく次が重要です。

* 今の iteration でなぜ fail したのか
* 次の再試行で何を改善するのか
* 何回目で収束したのか

`goal` chunk がない場合、これらを後から追跡するのは難しく、評価運用がブラックボックス化しやすくなります。

---

## 今回の対応でどう嬉しくなったのか

### 1. objective が「プロンプトの文字列」から「スレッド状態」に昇格した

`setObjective()` で thread/resource に紐づけることで、目的は呼び出し引数ではなく状態として管理されます。これにより、

* セッション断絶に強くなる
* 再開時に目的の整合性を保ちやすい
* 実行制御をコードで扱いやすい

という効果が出ます。

### 2. judge によるループ判定が標準化された

各ループで `1`（pass）か `0`（fail）を返し、fail 時はフィードバックを注入して次の試行へ進みます。これで、

の制御がフレームワークの責務に寄ります。アプリ側は orchestration に集中できます。

### 3. `goal` chunk で運用可観測性が上がった

`goal` chunk には `objective`、`iteration`、`status`、`results`、`reason` などが含まれます。つまり、

* どこで詰まったか
* 何が評価されたか
* いつ完了と見なされたか

をストリーム時点で記録できます。後追いデバッグの難易度が大きく下がります。

### 4. run 予算枯渇時の「持ち越し」ができる

`maxRuns` 到達でただ失敗終了するのではなく、objective が active のまま残るため、次 run で再開できます。長い調査タスクや人間承認を挟むフローで扱いやすくなります。

---

## 周辺知識: Goals を使う前提条件

### Storage と Memory-backed thread が必要

公式のとおり、Goals は永続状態を扱うため、次が前提です。

* storage backend の設定
* memory-backed thread

ここがないと objective の保存・取得・再開が成立しません。逆に言うと、Goals は「単発応答最適化」ではなく「継続実行最適化」の機能です。

### `goal.judge` は「評価モデル」を分離する設計

`goal` 設定では、実行モデルとは別に judge モデルを指定できます。たとえば、生成は高性能モデル、評価は軽量モデルという分離が可能です。これにより、

* 評価コストを抑える
* 反復回数を増やしても運用しやすい

という現実的な設計ができます。

### 既存の Evals / Gates との関係

Goals の judge は「この objective を満たしたか」をループ内で判定します。以前の `gates/verdicts` が CI 側の最終品質判定を強化したのに対し、Goals は実行中の反復制御を強化します。

* Goals: 実行中に「続ける/止める」を判断
* Gates/Verdicts: 実行結果に対して「通す/落とす」を判断

この分業で、オンライン制御とオフライン品質判定の境界が明確になります。

---

## 実装イメージ 1: Goal を設定してストリームを監視する

```
import { Agent } from "@mastra/core/agent";
import { Memory } from "@mastra/memory";
import { exaSearchTool } from "../tools/exa-search-tool";

export const researchAgent = new Agent({
  id: "research-agent",
  name: "Research Agent",
  instructions:
    "あなたは調査エージェントです。検索ツールを使って根拠を集め、未達なら改善点を反映して再試行してください。",
  model: "anthropic/claude-opus-4-8",
  tools: { exaSearchTool },
  memory: new Memory(),
  goal: {
    judge: "anthropic/claude-haiku-4-5",
    // 評価コストを抑えるため、judge は軽量モデルを利用
    maxRuns: 10,
  },
});

async function runGoalLoop() {
  const threadId = "research-2026-llm-release";
  const resourceId = "acme-research-agent";
  const objective = "2026年の主要LLMリリースを網羅した詳細レポートを作成する";

  await researchAgent.setObjective(objective, { threadId, resourceId });

  const stream = await researchAgent.stream(objective, {
    memory: { thread: threadId, resource: resourceId },
  });

  for await (const chunk of stream.fullStream) {
    if (chunk.type === "goal") {
      // 目標判定イベントを運用ログに残す
      console.log("[goal]", chunk.payload);
    }

    if (chunk.type === "tool-call" || chunk.type === "tool-result") {
      console.log(`[${chunk.type}]`, chunk.payload);
    }
  }

  const record = await researchAgent.getObjective({ threadId });
  console.log(`objective=${record?.objective} status=${record?.status}`);
}
```

この構成だと、目標・進捗・ツール呼び出しを同じ run で追えるため、長時間タスクの挙動を追跡しやすくなります。

---

## 実装イメージ 2: 予算到達後に再開可能な運用

```
async function resumeIfNeeded(threadId: string, resourceId: string) {
  const current = await researchAgent.getObjective({ threadId });

  if (!current) return;

  // maxRuns 到達後でも active なら、次 run で継続できる
  if (current.status === "active") {
    await researchAgent.stream(current.objective, {
      memory: { thread: threadId, resource: resourceId },
    });
  }

  // 人手確認が必要な運用では paused を検知して通知する
  if (current.status === "paused") {
    console.log("目標は一時停止中です。承認後に再開してください。");
  }
}
```

ここで嬉しい点は、失敗で状態を捨てるのではなく「未完了状態を保持したまま次 run につなげられる」ことです。

---

## 導入時の設計ポイント

1. objective は「完了条件」を明確に書く
2. judge モデルはコスト/精度で分けて選ぶ
3. `goal` chunk を必ずログに残す
4. `maxRuns` はタスク粒度に応じて調整する
5. paused / active / done を UI と運用手順に結びつける

objective が曖昧だと、判定の一貫性が崩れます。まずは「何を満たせば done か」を文章で固定することが重要です。

---

## まとめ

Goals は、Mastra エージェントにおける「長時間タスクの完了判定」をスレッド状態へ移し、ループ内判定と進捗観測を標準化するアップデートです。

これまでの課題は、目的の再注入・完了判定の自前実装・進捗のブラックボックス化でした。今回の対応で、

* 目的は durable に保持され
* 判定は run ループで自動化され
* 進捗は `goal` chunk で可視化される

ようになりました。

長時間実行エージェントを本番運用するうえで、今回の追加はかなり実務的な一歩です。
