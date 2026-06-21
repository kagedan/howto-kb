---
id: "2026-06-20-mastra-announce-2026上期の集大成-mastra-harness-は長時間エージェ-01"
title: "[Mastra Announce] 2026上期の集大成！ Mastra Harness は「長時間エージェントの実行基盤」だ"
url: "https://zenn.dev/shiromizuj/articles/b2be08f68477ec"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "OpenAI", "GPT"]
date_published: "2026-06-20"
date_collected: "2026-06-21"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で発表された[Announcements](https://mastra.ai/blog/category/announcements)を速報ベースでお伝えします。ただの直訳ではなく、関連ドキュメントも参照したうえで手厚くしたり省略したりします。速報性重視でAIの力を多分に使っているので、私自身の考察は少なめです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

2026年6月18日、Mastra は **Announcing Mastra Harness** を公開しました。

今回の発表を短く言うと、**長時間動き、人間が途中で介入し、複数フェーズをまたいで協調するエージェントを、`Agent` 単体より一段高い抽象で組めるようにした**という話です。

これまでの Mastra でも同じことを実現するのは不可能ではなかったかもしれませんが、 エージェントを制御する様々な仕掛けを個別に実装して組み合わせる必要がありましたが、今回それらが `Harness` という 1 つの runtime API にまとまった、というものです。

実際の作りに着目すれば、Mastra が `Agent` という推論単位の API から一段上がって、**スレッド、モード、承認、途中介入、サブエージェント、表示状態、永続セッション**まで含めた「実行基盤」をフレームワークとして明示した、といえます。

---

## 改めて、ハーネスとは何か

**`Harness` は、Agent の外側に置く session controller です。**

Mastra の公式 docs は、Harness を「UI と agent loop の間にある runtime concerns をまとめて扱う層」と説明しています。つまり、エージェント自身が何を答えるかではなく、**そのエージェントを人間がどう使い、どう監視し、どう途中で方向修正し、どう長時間生かし続けるか**を扱うレイヤです。

そのため Harness が抽象化しているのは、たとえば次のような関心事です。

* 同じ会話を thread として永続化する
* Plan / Execute / Review のような mode を切り替える
* Web / TUI / Slack など複数クライアントから同じ会話を購読する
* ツール実行の承認を session 単位で覚える
* サブエージェントへ委譲する
* 実行中タスクへ follow-up を差し込む
* 低レベルイベントを UI 向け display state に畳み込む

ここが重要です。`Harness` は **Agent の代替ではありません**。`Agent` が LLM、ツール、メモリ、推論ループの基本単位だとすると、`Harness` はその Agent を「共同作業相手」として運用するための殻です。

---

## 背景: なぜいま Harness が必要だったのか

### 1. 2026 年のエージェントは、もう one-shot API では足りない

2024 年ごろのエージェント API は、`generate()` や `stream()` を呼んで結果を受け取るだけでも十分に価値がありました。ですが 2026 年に入ってからの実務では、もっと別の要件が目立つようになっています。

* 途中で人間が方針を変えたい
* 10 分以上かかる仕事を続けてほしい
* 別クライアントから進捗を見たい
* dangerous なツールだけ止めたい
* 計画用の人格と実行用の人格を分けたい
* サブエージェントへ一部タスクだけ振りたい

こうなると問題は「LLM が答えを返せるか」ではなく、**長時間動くエージェントをどう制御するか**へ移ります。

Mastra はこの数か月、まさにそこを埋める部品を一気に積み上げてきました。今回の Harness は、その部品群を「ひとまとまりの runtime」として見せる発表です。

### 2. Mastra Code で先に使っていたものを、汎用 API として切り出した

公式アナウンスでは、Mastra チームがほぼ 6 か月かけて TUI コーディングエージェント **Mastra Code** を作り、その中で有効だった仕組みを `Harness` に抽出したと説明しています。

つまりこれは「理論先行の設計」ではなく、**実際にコーディングエージェントを毎日運用していたときに必要だった機能を、一般化して取り出した API** です。

この流れはかなり納得感があります。コード生成エージェントのように長く動き、途中で割り込みが入り、危険操作もあり、サブタスク委譲も必要な領域では、`Harness` のような制御層が実際に必要だからです。

---

## Agent と Harness の違いを先に整理する

今回の発表は便利そうに見える一方で、「結局 Agent と何が違うのか」が曖昧なままだと理解しづらいです。先に整理してしまいます。

| レイヤ | 主な責務 | 典型 API |
| --- | --- | --- |
| `Agent` | 推論、ツール呼び出し、メモリ、ストリーミング | `generate()` / `stream()` |
| `Harness` | thread、session、mode、承認、subagent、display state、途中介入 | `sendMessage()` / `switchMode()` / `subscribe()` |

言い換えると、`Agent` は「どう考えて答えるか」の層で、`Harness` は「その考える存在をどう人間のアプリに埋め込むか」の層です。

docs にも、**単純な request/response や完全な自前制御が欲しいなら `Agent` を直接使い、共同作業型セッションを手早く作りたいなら `Harness` を使う**、という整理が書かれています。この切り分けはかなり妥当です。

---

## 最近の Mastra アナウンスの中での位置づけ

今回の Harness 発表は単独で見るより、6 月前半の一連の流れに置いたほうが分かりやすいです。

### 6月3日: Agent Signals

Signals は、実行中の thread に対して `sendMessage()`、`queueMessage()`、reactive signal、state signal、notification signal を送れる仕組みでした。  
これは **「動いているエージェントへ途中参加する primitive」** です。

### 6月9日: Code Mode

Code Mode は、複数ツールをまたぐ計算を、その場で生成した TypeScript 関数に閉じ込める仕組みでした。  
これは **「1 回の run の中での multi-tool orchestration」** を賢くする方向です。

### 6月15日: SDK Subagents

Claude Code / Cursor / Codex などを Mastra に取り込み、Mastra 自体を harness-agnostic に寄せる発表でした。  
これは **「外部ハーネスすら Mastra の runtime に統合する」** 方向です。

### 6月16日: Managed Databases

Mastra Platform から DB を即座に用意し、メモリやストレージの足回りを整えやすくする発表でした。  
これは **「長時間 runtime を支える永続層の導入コストを下げる」** 方向です。

### 6月18日: Harness

そして今回の Harness は、それらを受けて **「そもそも対話型の長時間エージェント runtime を 1 つのクラスとして持とう」** と言った発表です。

この 5 本を並べると、Mastra が目指しているのは単なる agent framework ではなく、

1. 推論する Agent を持ち、
2. それを取り巻く runtime を持ち、
3. さらに外部ハーネスや永続基盤まで包み込む

という、かなり上位のオーケストレーション層だと見えてきます。

---

## Harness が具体的に提供するもの

公式 announcement と docs を合わせると、Harness の価値は大きく 6 つあります。

### 1. Session と thread を中心にした長時間会話

Harness には Session という概念があり、そこに active mode、thread binding、permission grants、follow-up queue、usage などが乗ります。  
これにより「会話をまたいで同じ相手として振る舞う」前提が最初から入っています。

### 2. Mode 切り替え

Plan / Execute / Review のようなフェーズを、別 Agent を起動し直すのではなく、**同じ thread を保ったまま mode 切り替え**として扱えます。  
しかも `transitionsTo` で次の mode への handoff も宣言できます。

### 3. 承認つきツール実行

標準 Agent でもツール承認はできますが、Harness では **承認を session 全体で保持** できます。  
「この run の間、read 系は全部許可」「このツールは deny」など、より runtime 的な制御になります。

### 4. サブエージェント委譲

サブエージェントは built-in tool のように expose され、親エージェントが必要時に呼び出せます。  
このとき isolated subagent と forked subagent を使い分けられるのが面白いです。

* isolated: 親コンテキストを持たないので、雑音を減らした独立推論に向く
* forked: 親会話を引き継ぐので、同じ流れの延長で細かい探索をさせたいときに向く

### 5. Display State

Harness は多数の低レベルイベントを `HarnessDisplayState` に畳み込むため、UI 側は message delta や tool delta を全部自前で組み立てなくて済みます。  
これは Web UI や TUI を実装するときにかなり効きます。

### 6. Observational Memory

長時間エージェントでは、履歴の compaction が雑だと文脈を落としやすいです。Harness は Mastra の Observational Memory と組み合わせることで、長い thread を比較的壊しにくく扱えます。

---

## 具体的な使い方

ここからは、実際にどう使うのかを最小構成で見ます。例として、**計画を立ててから実装し、必要ならレビュー用サブエージェントへ振るコーディングエージェント**を作ります。

### 1. Harness を初期化する

```
import { Agent } from "@mastra/core/agent";
import { Harness } from "@mastra/core/harness";
import { LibSQLStore } from "@mastra/libsql";
import { Memory } from "@mastra/memory";

const planAgent = new Agent({
  id: "plan-agent",
  name: "Plan Agent",
  instructions: [
    "あなたは実装前の計画担当です。",
    "いきなりコードを書かず、目的、変更点、確認事項、リスクを先に整理してください。",
  ].join("\n"),
  model: "openai/gpt-5.5",
});

const executeAgent = new Agent({
  id: "execute-agent",
  name: "Execute Agent",
  instructions: [
    "あなたは実装担当です。",
    "承認済みの計画に従って変更し、必要ならテストまで進めてください。",
  ].join("\n"),
  model: "openai/gpt-5.5",
});

export const codingHarness = new Harness({
  id: "coding-harness",
  storage: new LibSQLStore({
    url: "file:./mastra.db",
  }),
  memory: new Memory({
    storage: new LibSQLStore({
      url: "file:./mastra-memory.db",
    }),
    options: {
      observationalMemory: true,
    },
  }),
  modes: [
    {
      id: "plan",
      name: "Plan",
      metadata: { default: true },
      agent: planAgent,
      transitionsTo: "execute",
    },
    {
      id: "execute",
      name: "Execute",
      agent: executeAgent,
    },
  ],
  subagents: [
    {
      id: "reviewer",
      name: "Reviewer",
      description: "差分を読んでバグや抜け漏れを探す",
      instructions: "変更差分を批判的に読み、危険な点を指摘してください。",
      defaultModelId: "anthropic/claude-opus-4-6",
    },
  ],
});
```

この段階で押さえておきたいのは、`Harness` に直接 1 つの `agent` を渡すこともできますが、今回のように **mode を複数持たせると価値が出やすい** という点です。

### 2. thread を作り、イベントを購読する

```
await codingHarness.init();
await codingHarness.selectOrCreateThread();

codingHarness.subscribe((event) => {
  if (event.type === "message_update") {
    console.log("メッセージ更新:", event.message);
  }

  if (event.type === "display_state_changed") {
    const state = codingHarness.getDisplayState();

    if (state.isRunning) {
      console.log("現在のタスク:", state.tasks);
      console.log("実行中ツール:", state.activeTools);
    }
  }
});

await codingHarness.sendMessage({
  content: "CSV 入力機能を追加する前に、変更計画を立ててください。",
});
```

ここでの感覚は `agent.stream()` とはかなり違います。  
1 回の返答を取るというより、**同じ thread を継続して見守る** イメージです。

### 3. 承認フローを入れる

コーディングエージェントでは、ファイル書き込みやシェル実行を人間承認にしたくなることが多いです。Harness ではそれを session レベルで扱えます。

```
codingHarness.subscribe((event) => {
  if (event.type !== "tool_approval_required") return;

  console.log("承認待ちツール:", event.toolName);

  codingHarness.respondToToolApproval({
    // ここでは例として、その都度承認する
    decision: "approve",
  });
});

// 読み取り系だけは事前に常時許可しておく
codingHarness.setPermissionForCategory({
  category: "read",
  policy: "allow",
});
```

この設計がよいのは、「承認が一度きりの UI 操作で終わらず、その後の runtime policy として効く」ことです。

### 4. 実行中に質問させる

不明点があるまま危険な推測をされるより、途中で人間に聞き返してくれたほうが安全です。Harness には `ask_user` が built-in で入っています。

```
codingHarness.subscribe((event) => {
  if (event.type !== "tool_suspended") return;
  if (event.toolName !== "ask_user") return;

  const { question } = event.suspendPayload;
  console.log("エージェントからの質問:", question);

  codingHarness.respondToToolSuspension({
    toolCallId: event.toolCallId,
    resumeData: "既存の CSV パーサーを流用してください。",
  });
});
```

ここは実務でかなり大事です。長時間エージェントほど、**分からないときに止まって聞けること**が品質に直結します。

### 5. モードを明示的に切り替える

承認ベースで自動遷移させるだけでなく、状況に応じて手動切り替えもできます。

```
await codingHarness.switchMode({
  modeId: "execute",
});

await codingHarness.sendMessage({
  content: "計画は承認します。実装に進んでください。",
});
```

これにより、「計画と実装で別人格・別モデル・別ツールセット」を自然に切り替えられます。

### 6. forked subagent を使う考え方

たとえば実装中に「既存コードベースの探索だけを別にやらせたい」ことがあります。そのとき、親会話を引き継いだ forked subagent を使うと、同じ文脈を保ったまま局所探索を任せられます。

逆に、レビューや別観点の検証のように、**親の思い込みを持ち込ませたくない** 場面では isolated subagent のほうが向いています。

この isolated / forked の切り分けは、Harness の中でもかなり実務的なポイントです。

---

## どんなケースで特に効くか

docs と announcement を踏まえると、Harness が特に向いているのは次のようなケースです。

### 1. コーディングエージェント

長く動き、途中で危険操作があり、プラン承認も必要で、レビュー用の別人格も欲しい。  
Harness が一番はまりやすい領域です。

### 2. 調査からドラフトまで進めるリサーチエージェント

Research mode で情報収集し、Draft mode で文章化するような構成です。  
同じ thread を維持したまま人格だけ切り替えられるので、UI 実装がかなり素直になります。

### 3. 人間が途中介入する長時間業務エージェント

サポート、オペレーション、バックグラウンド処理など、途中で別ユーザーや別 UI が関わるものです。  
Signals と組み合わせると、Harness の価値がさらに大きくなります。

---

## 逆に、まだ Harness を使わなくてもよいケース

公式 docs もかなり率直で、すべてのエージェントに Harness が必要だとは言っていません。次のようなケースでは、従来の `Agent` だけで十分です。

* 1 回の入力に 1 回答えるだけ
* thread や mode を持たない
* 承認や途中介入が不要
* 独自 runtime をかなり細かく作り込みたい

この線引きは大事です。Harness は便利ですが、そのぶん持ち込む抽象も増えます。**単純なチャットボットまで無理に Harness 化する必要はない** です。

---

## 注意点

### 1. alpha である

docs では Harness は alpha と明記されています。minor version の範囲でも破壊的変更がありえます。  
本番採用するなら、アプリ側に薄いラッパーを置いておくほうが安全です。

### 2. 永続化前提で考えたほうがよい

Harness の価値は session continuity にあります。逆に言うと、ストレージを適当に扱うと価値が落ちます。  
thread、memory、observability の保存先を最初から意識して設計したほうがよさそうです。

### 3. UI 実装もセットで考えるべき

Harness は TUI / Web UI / モバイル UI に display state を供給する発想が強いです。  
バックエンドだけ導入しても恩恵はありますが、真価が出るのは「状態を見せる画面」と組み合わせたときです。

---

## まとめ

今回の Harness 発表は、単なる `@mastra/core` のクラス追加ではありません。Mastra が 2026 年春から積み上げてきた

* Signals による途中介入
* Code Mode による multi-tool orchestration
* SDK subagents による harness-agnostic 化
* Managed Databases による永続基盤整備

といった流れを受けて、**長時間・対話型・マルチクライアントなエージェント runtime を、明示的にフレームワークの一級概念へ引き上げた**発表だと言えます。

`Agent` が推論の単位だとすれば、`Harness` は共同作業ランタイムの単位です。コーディングエージェント、長時間リサーチエージェント、人間承認つき業務エージェントを作ろうとしている人にとって、かなり重要な節目になる発表でした。

---

## 参考リンク
