---
id: "2026-06-25-mastra-announce-task-listsで長時間エージェントの計画と進捗を見える化-01"
title: "[Mastra Announce] Task Listsで長時間エージェントの計画と進捗を見える化"
url: "https://zenn.dev/shiromizuj/articles/28d74401e146c5"
source: "zenn"
category: "claude-code"
tags: ["MCP", "prompt-engineering", "AI-agent", "OpenAI", "GPT", "zenn"]
date_published: "2026-06-25"
date_collected: "2026-06-27"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で発表された [Announcements](https://mastra.ai/blog/category/announcements) を、関連ドキュメントも読みながら解説します。今回は単なる UI 小物ではなく、**長時間動くエージェントに「作業計画」と「進捗の見える化」を持ち込むための基盤機能**です。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## 今回の発表をひとことで言うと

**Mastra の Agent Signals 上に、「エージェント自身が作るチェックリスト」を標準機能として載せた発表**です。

すでに Mastra には Signals があり、実行中のエージェントへ途中でメッセージや state を送り込めました。しかしそれだけでは、エージェントが「いま何のために何をしているのか」を人間が追うにはまだ一工夫必要でした。計画を出す方法も、進捗を更新する方法も、画面に表示する方法も、アプリ側でばらばらに作りがちだったからです。

今回の `TaskSignalProvider` はそこを埋めます。エージェントが最初にやるべきことをタスクへ分解し、進行中・完了を更新し、その状態をストリームや state signal として扱えるようにします。つまり、**「長く動くが見えにくいエージェント」を、「何をしているか追えるエージェント」へ寄せる機能**だと捉えると分かりやすいです。

---

## 背景: なぜ Task Lists が必要だったのか

最近のエージェントは、単発の質疑応答よりも、数十秒から数分かけて調査・コーディング・検証を進める場面が増えています。Mastra もここ数か月で、Signals、Background Tasks、Observational Memory、SDK subagents など、**「長く動くエージェント runtime」** を支える部品をかなり強化してきました。

ただ、長時間エージェントには 1 つ厄介な問題があります。**内部では色々考えて進んでいても、外から見ると何をしているのか分かりにくい**ことです。

たとえば次のようなケースです。

* 調査エージェントが複数ソースを横断してレポートを書いている
* コーディングエージェントがコード探索、編集、テスト、再修正を繰り返している
* サポートエージェントが問い合わせ対応の裏で過去履歴や社内ナレッジを調べている

このとき人間が知りたいのは、最終回答だけではありません。

* いま何に着手しているのか
* どこまで終わったのか
* 次に何をするつもりなのか
* 途中で方向修正したほうがよいのか

従来はこれを、system prompt に「進捗を逐次報告せよ」と書いたり、ツール出力のログを無理やり UI に並べたりして対応しがちでした。しかしその方法だと、**計画が durable な状態として残らない**し、エージェントごとに進捗表現がぶれます。

Task Lists は、進捗を単なる文章ではなく、**構造化されたタスク状態**として扱うための機能です。

---

## Task Lists とは何か

Task Lists の中心は `TaskSignalProvider` です。これを agent の `signals` に登録すると、Mastra は次の 2 つをまとめて有効化します。

1. `task_write`、`task_update`、`task_complete`、`task_check` の 4 つの task tool
2. タスクリストを state signal として thread に反映する `TaskStateProcessor`

これが重要なのは、単に「タスク更新用ツールが 4 個増える」だけではない点です。Task list は thread に紐づく durable な状態として保存され、state-signal lane に投影されます。つまり、**Observational Memory で古い会話が圧縮・切り詰めされても、タスクリスト自体は消えにくい**し、毎回 system prompt を作り直してキャッシュを壊す必要もありません。

状態としてはかなり素直です。

* `pending`: まだ着手していない
* `in_progress`: いま取り組んでいる
* `completed`: 終わった

この単純さが逆に効きます。複雑な DAG や workflow 定義ではなく、**人間が見て直感的に理解できる粒度の進捗管理**に寄っているからです。

---

## 何がうれしいのか

### 1. 最初に計画が見える

エージェントが作業開始時にタスク一覧を出すので、ユーザーは「この依頼をどう分解したのか」を最初に確認できます。

これは地味ですが大きいです。長時間エージェントの不安の多くは、「本当にこちらの意図どおりに進めているのか分からない」ことから来ます。最初のプランが見えれば、その段階で「その順番でいい」「いや先にここを見て」と言えます。

### 2. 進捗更新が ad-hoc な文章で終わらない

「調査しています」「続けています」のような自然文だけでは、UI に載せても扱いづらいです。Task Lists なら、状態が構造化されているので、

* タスクリスト表示
* 完了率表示
* 現在の作業表示
* 未完了タスクの警告

といった UI を作りやすくなります。

### 3. Memory / Signals と素直につながる

Mastra はもともと thread を軸に会話と状態を持つ設計です。Task Lists はその上に載るので、別のタスク管理システムを無理やり横付けする感じではありません。

特に相性が良いのは次の 3 つです。

* Signals: ストリームに流れる `task_` tool call をそのまま画面へ反映できる
* Working Memory: ユーザーの好みや制約を保ちつつ、その上で今の作業計画を追える
* Observational Memory: 会話が長くなっても task state を別レーンで保ちやすい

### 4. 人間が途中で介入しやすくなる

Task Lists があると、途中参加する人間も指示しやすくなります。

* 「タスク 2 を先にやって」
* 「そのタスクは不要なので外して」
* 「完了扱いにする前に比較表を追加して」

長時間エージェントでは、人間が最後だけ確認するより、**進行中に軽く舵を切る** ほうが品質も速度も上がりやすいです。Task Lists はそのための共通の見取り図になります。

---

## 既存機能との位置づけ

ここは少し整理しておくと分かりやすいです。

### Signals との違い

Signals は thread にメッセージや状態や通知を入れるための汎用基盤です。Task Lists はその上で、「タスク管理」という特定用途を標準化した provider です。

つまり、

* Signals: 汎用の通信路
* Task Lists: 進捗管理用に定型化された実装

という関係です。

### Background Tasks との違い

Background Tasks は、時間のかかるツール実行をバックグラウンドで回す実行基盤でした。一方 Task Lists は、**何をやるか・どこまで終わったか** を表現する状態管理です。

実務では両方を一緒に使うはずです。

* Background Tasks: 実際の重い処理を走らせる
* Task Lists: その処理の計画と進捗を見せる

### Workflow との違い

Workflow は、開発者が事前に実行手順を設計する仕組みです。Task Lists は、エージェントが会話文脈の中でその場で作る作業計画です。

固定フローなら workflow、探索的な作業なら task list が向いています。

---

## 具体的な使い方

### 1. まずは `TaskSignalProvider` を追加する

最小構成はかなり単純です。`Memory` を持つ agent に `TaskSignalProvider` を登録します。

```
import { Agent } from "@mastra/core/agent";
import { TaskSignalProvider } from "@mastra/core/signals";
import { Memory } from "@mastra/memory";

export const researchAgent = new Agent({
  id: "research-agent",
  name: "Research Agent",
  instructions: `
あなたは調査エージェントです。
作業を始める前に、task_write を使って 3〜5 個の実行タスクへ分解してください。
着手したタスクは in_progress に更新し、完了したタスクは completed にしてください。
途中で必要な作業が増えたら task_update で一覧を更新してください。
最終回答の前に task_check を使って未完了タスクがないか確認してください。
`,
  model: "openai/gpt-5.5",
  memory: new Memory(),
  signals: [new TaskSignalProvider()],
});
```

重要なのは、**Task Lists は「勝手に賢く進捗を出す魔法」ではなく、モデルに使わせる設計が必要**だということです。実務では `instructions` に

* 最初に plan を出す
* 状態遷移をきちんと更新する
* 最後に取りこぼしを確認する

の 3 点を書くと安定しやすいと思います。

### 2. thread / resource を付けて呼び出す

Task tracking は memory-backed thread が前提です。つまり、`threadId` と `resourceId` を持つ呼び出しにしておく必要があります。

```
const stream = await researchAgent.stream(
  "競合 3 社を比較して、新しいデータ基盤の提案メモを作ってください。",
  {
    memory: {
      thread: "thread-123",
      resource: "user-123",
    },
  },
);
```

ここは Signals 系機能と同じです。単発実行より、**同じ thread 上で継続して進める会話**のほうが Task Lists の価値が出ます。

### 3. ストリームから task 更新を拾う

UI とつなぐなら、まずはここから始めるのが一番分かりやすいです。`fullStream` を読みながら `task_` tool call を拾えば、画面側で進捗表示を更新できます。

```
const stream = await researchAgent.stream(
  "社内向けに MCP 導入ガイドのたたき台を作ってください。",
  {
    memory: {
      thread: "thread-123",
      resource: "user-123",
    },
  },
);

for await (const chunk of stream.fullStream) {
  if (chunk.type === "tool-call" && chunk.payload.toolName?.startsWith("task_")) {
    // ここで task 一覧 UI や進捗バーを更新する
    console.log(chunk.payload.toolName);
    console.log(chunk.payload.args);
  }
}
```

この設計の良いところは、チャット本文を無理やりパースしなくてよいことです。進捗表示をテキストの書きぶりに依存させる必要がありません。

### 4. 保存された task state を参照する

アナウンスでは、`threadId` を使って保存済み task list を読む例も示されています。ライブストリームだけでなく、画面再読み込み後に現在状態を復元したいときに便利です。

```
const store = await mastra.getStorage().getStore("threadState");
const tasks = await store.getState({
  threadId: "thread-123",
  type: "task",
});

console.log(tasks);
```

記事と reference を合わせて読むと、内部的には task state は task 用の保存領域を source of truth としつつ、agent 側から扱いやすい state signal として投影される設計になっています。要するに、**画面の一時表示ではなく、thread に紐づく状態として保たれる**わけです。

### 5. Web search agent や coding agent と組み合わせる

今回のアナウンス本文でも、web research tool を持つ agent 例が示されています。Task Lists は特に次のようなエージェントで相性が良いです。

* Web search / deep research agent
* コーディングエージェント
* 調査してから提案書や要約を書くエージェント
* 複数ステップの顧客対応を行うサポートエージェント

たとえばコーディング用途なら、次のような task list に自然に落ちます。

1. 既存実装と関連ファイルを確認する
2. 変更方針を決める
3. コードを修正する
4. テストを実行する
5. 変更点を要約する

この粒度なら、人間が見ても納得しやすく、途中で修正指示もしやすいです。

---

## 導入時に気をつけたい点

### 1. タスク粒度を細かくしすぎない

Task Lists は便利ですが、10 個以上の細かすぎる項目を毎回並べると、かえって読みにくくなります。人間が追える粒度で 3〜5 個程度から始めるのが無難です。

### 2. task list は workflow の代わりではない

厳密な分岐や依存関係、再試行制御が必要なら workflow のほうが向いています。Task Lists は、人間に見せる計画と進捗の表現だと考えたほうがよいです。

### 3. 進捗表示の責務を分ける

Task Lists を入れたからといって、ユーザー向け説明文が不要になるわけではありません。

* task state: 構造化された進捗
* 通常の応答文: 人間向けの説明

の 2 層で考えると設計しやすいです。

### 4. instruction 設計はちゃんと書く

TaskSignalProvider を足しただけだと、モデルがいつ task を切るべきか曖昧な場合があります。最初に plan を出すのか、途中で差し替えてよいのか、完了前に確認するのかは、instructions へ明示したほうが安定します。

---

## まとめ

Task Lists は、見た目としては「エージェントの todo 表示」ですが、実態はもっと重要です。**長時間エージェントの計画と進捗を、Mastra の Signals / Memory モデルの中で durable に扱うための標準部品**です。

今回の発表で嬉しいのは、単に進捗が見やすくなることだけではありません。

1. エージェントの作業計画を最初に共有できる
2. 進捗更新を構造化データとして扱える
3. Memory / Signals と自然につながる
4. 人間が途中参加しやすくなる

Mastra を使っていて、「エージェントは動いているが、何をしているか見えにくい」と感じていたなら、今回の Task Lists はかなり効くはずです。特に research や coding のような長時間タスクでは、単なる補助機能ではなく、**プロダクト体験そのものを整える機能**として見ておく価値があります。

---

## 関連リンク
