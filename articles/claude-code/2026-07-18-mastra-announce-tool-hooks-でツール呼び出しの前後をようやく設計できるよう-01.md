---
id: "2026-07-18-mastra-announce-tool-hooks-でツール呼び出しの前後をようやく設計できるよう-01"
title: "[Mastra Announce] Tool Hooks で「ツール呼び出しの前後」をようやく設計できるようになった"
url: "https://zenn.dev/shiromizuj/articles/8dc4bd05087706"
source: "zenn"
category: "claude-code"
tags: ["API", "AI-agent", "OpenAI", "GPT", "zenn"]
date_published: "2026-07-18"
date_collected: "2026-07-19"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で公開された [Features](https://mastra.ai/blog/category/features) 記事をもとに、今回の発表が何を解決するのかを整理します。今回は新しいモデル機能というより、**エージェントの運用を本番品質へ引き上げるための実装面アップデート**です。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

2026年7月14日、Mastra は **Introducing Tool Hooks for Mastra Agents** を公開しました。

ひとことで言うと、今回の追加は **「ツール実行を、実行そのものと運用ロジックに分離する仕組み」** です。

これまでの Mastra でもツールは強力でしたが、

* 実行前のポリシー判定
* 実行中の引数ストリーム観測
* 実行後の監査ログ
* 危険呼び出しの短絡（ブロック）

といった処理は、ほぼ `execute` に埋め込むしかありませんでした。今回の `tool hooks` で、これを Agent / Tool / Workspace の各レイヤーに分けて実装できます。

---

## 先に結論

今回うれしいのは、Mastra の tools が「呼べる機能」から **「制御できる実行面」** に進んだことです。

特に大きいのは次の 4 点です。

1. `beforeToolCall` で事前ポリシーを一括適用できる
2. `beforeToolCall` で `{ proceed: false, output }` を返し、実行せずに結果を返せる
3. `onInputStart` / `onInputDelta` / `onInputAvailable` / `onOutput` で、ツール呼び出しを段階的に観測できる
4. Agent hooks と Workspace hooks を重ねて、監査・統制の責務分離ができる

結果として、**「ツールの中身を汚さずに、運用要件を後付けできる」** ようになります。

---

## 背景: これまで何が課題だったのか

### 1. ログやポリシーが `execute` に混ざりやすかった

従来は、たとえば「危険なコマンドを止める」「特定データをマスクして記録する」といった処理を `execute` に書くことが多く、ツール本来の責務（外部API呼び出しなど）と運用責務（監査・統制）が混ざりがちでした。

その結果、次の問題が出ます。

* 同じポリシーを複数ツールに重複実装する
* ツール再利用時に運用ロジックまで一緒に持ち出される
* ロジック変更時の影響範囲が読みにくい

### 2. ツール本体を編集できないと統制しにくかった

チーム運用では、ツールが別パッケージ由来だったり、共通ライブラリとして凍結されていたりします。こういう場合、`execute` に手を入れないと制御できない設計だと、アプリ側で柔軟に統制できません。

今回の hooks はこの痛点に直接効きます。**エージェント側の設定だけで、前後処理やブロック判定を足せる**からです。

### 3. ストリーミング時の「途中状態」を観測しづらかった

`.stream()` でツール引数が逐次生成されるとき、UI や監視で本当に見たいのは「最終引数」だけではありません。

* モデルがどんな意図で引数を組み立てているか
* 途中で危険な兆候が出ていないか
* 最終確定前に何を表示できるか

Tool-level hooks の 4 段階は、この観測ニーズをかなり素直に満たします。

---

## 今回の対応で何が入ったのか

## 1. Agent-level hooks

Agent の `hooks` に次を定義できます。

* `beforeToolCall`
* `afterToolCall`

`beforeToolCall` は、`{ proceed: false, output }` を返すことでツール実行をスキップできます。ここで返す `output` は、そのツールの結果としてモデル側へ渡されます。

これは「止める」だけでなく「安全な代替応答を返す」実装ができるという意味で重要です。

## 2. Per-call hooks

`.generate()` / `.stream()` 呼び出し時に `hooks` を渡すと、その1回だけフックを差し替えられます。

* 常時運用のログは Agent-level
* 一時デバッグの詳細ログは Per-call

のように使い分けられます。ドキュメント上も、Per-call は対応する Agent-level のキーを上書きし、指定しないキーはマージされます。

`createTool()` 側で、以下のライフサイクルフックを定義できます。

1. `onInputStart`
2. `onInputDelta`
3. `onInputAvailable`
4. `onOutput`

順序は上記のとおりです。`onOutput` は成功時に呼ばれ、実行エラー時は呼ばれません（エラー時は Agent-level の `afterToolCall` で `error` を受けられます）。

## 4. Workspace hooks

Workspace の `tools.hooks` でも `beforeToolCall` / `afterToolCall` を定義できます。ここでは `workspaceToolName` が追加で得られるため、リマップ後の表示名と元ツール名を対応付けて監査できます。

さらに docs には、Agent と Workspace の両方に hooks がある場合の順序が明示されています。

1. Agent `beforeToolCall`
2. Workspace `beforeToolCall`
3. tool 実行
4. Workspace `afterToolCall`
5. Agent `afterToolCall`

この順序が明示されたことで、ガードレールと監査の責務分離が設計しやすくなりました。

---

## 実装イメージ 1: ポリシー違反を「ブロックして代替結果を返す」

次は、公式サンプルの趣旨を保ちつつ、日本語でコメント・指示文を付けた例です。

```
import { Agent } from "@mastra/core/agent";
import { weatherTool } from "../tools/weather-tool";

const ブロック対象地域 = ["london", "paris"];

export const weatherAgent = new Agent({
  id: "weather-agent",
  name: "Weather Agent",
  instructions:
    "あなたは天気アシスタントです。ツール結果を簡潔に説明し、ポリシー違反時は安全な代替回答を返してください。",
  model: "openai/gpt-5.5",
  tools: { weatherTool },
  hooks: {
    beforeToolCall: ({ toolName, input }) => {
      if (toolName !== "weatherTool") return;

      const { location } = input as { location: string };
      const isBlocked = ブロック対象地域.some((地域名) =>
        location.toLowerCase().includes(地域名),
      );

      // ポリシー違反時はツールを実行せず、定義済みの安全な結果を返す
      if (isBlocked) {
        return {
          proceed: false,
          output: {
            temperature: null,
            feelsLike: null,
            humidity: null,
            windSpeed: null,
            windGust: null,
            conditions: `地域ポリシーにより「${location}」の取得は許可されていません。`,
            location,
          },
        };
      }
    },
    afterToolCall: ({ toolName, output, error }) => {
      if (error) {
        console.error(`[監査] ${toolName} でエラー`, error);
      } else {
        console.log(`[監査] ${toolName} の結果`, output);
      }
    },
  },
});
```

### ここで嬉しい点

* ツール本体を触らずにポリシーを差し込める
* ブロック時もアプリ挙動を壊さず、整形済み結果を返せる
* ログ責務を `execute` から分離できる

---

## 実装イメージ 2: ツール入力のストリームを段階的に監視する

```
import { createTool } from "@mastra/core/tools";
import { z } from "zod";

export const weatherTool = createTool({
  id: "weather-tool",
  description: "指定された都市の天気を取得します。",
  inputSchema: z.object({
    city: z.string(),
  }),
  outputSchema: z.object({
    temperature: z.number(),
    conditions: z.string(),
  }),

  // 引数ストリーミング開始
  onInputStart: ({ toolCallId }) => {
    console.log(`[入力開始] call=${toolCallId}`);
  },

  // 引数の差分を逐次観測
  onInputDelta: ({ inputTextDelta }) => {
    console.log(`[入力差分] ${inputTextDelta}`);
  },

  // 最終引数の確定点
  onInputAvailable: ({ input, toolCallId }) => {
    console.log(`[入力確定] call=${toolCallId} city=${input.city}`);
  },

  execute: async ({ city }) => {
    // 本来は外部API呼び出し
    return { temperature: 31, conditions: `${city} は晴れ` };
  },

  // 成功時の出力監査
  onOutput: ({ output, toolName }) => {
    console.log(`[出力] ${toolName}`, output);
  },
});
```

### ここで嬉しい点

* 「最終JSONだけ」ではなく、生成途中の挙動を観測できる
* UI で引数プレビューを先出ししやすい
* 監査ログを段階別に持てる

---

## 実運用で効く使い分け

### Agent hooks に寄せるべきもの

* プロダクト全体共通の監査ログ
* 危険操作ブロック
* 利用規約ベースの一律バリデーション

* そのツール特有の計測
* 入力組み立ての段階観測
* 出力品質メトリクスの採取

### Workspace hooks に寄せるべきもの

* ファイル操作やコマンド実行の横断監査
* リマップ名と実体名の対応記録
* 開発環境ポリシーの統制

この分離ができると、変更時の影響範囲が読みやすくなります。

---

## これで何が嬉しくなったのか（課題との対応表）

1. 課題: `execute` が肥大化しやすい

   * 改善: hooks へ責務分離し、ツール本体を薄く保てる
2. 課題: ツール本体を触れないと統制不能

   * 改善: Agent / Workspace 側で前後処理とブロックを適用できる
3. 課題: ストリーミング中の挙動が見えにくい

   * 改善: Tool-level の4段階フックで観測可能
4. 課題: ガードレールと監査を同じ場所に書いて混線する

   * 改善: Agent→Workspace→Tool の順序と責務を分けて設計できる

---

## 注意点

### 1. ブロック時の `output` は schema に合わせる

`beforeToolCall` で `proceed: false` を返す場合、返却する `output` はそのツールが期待する出力構造に合わせるのが安全です。型と実運用がずれると、後段処理で破綻しやすくなります。

### 2. hooks は増やしすぎると追跡しづらい

便利だからといって全レイヤーに重複ログを入れると、運用ノイズが増えます。

* Agent: 監査の骨格
* Workspace: 実行基盤の統制
* Tool: 個別計測

のように、目的を明確に分けるのがおすすめです。

### 3. `.stream()` と `.generate()` の観測粒度は違う

両者で hooks 自体は同順序で動作しますが、リアルタイム性の価値が大きいのは `.stream()` です。UI 要件がある場合はこの差を前提に設計した方がよいです。

---

## まとめ

今回の Tool Hooks は、見た目以上に重要なアップデートです。Mastra の tool 実行を「呼び出す」だけでなく、**いつ・どこで・何を制御するか** まで設計できるようになりました。

特に、今までの課題だった

* ポリシー実装の散在
* `execute` の肥大化
* ストリーミング中の不可視性

をまとめて改善できるのが大きいです。

一言でいえば、**ツール実行をアプリ機能から運用機能へ昇格させる基盤が入った**、という発表でした。
