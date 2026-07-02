---
id: "2026-07-02-mastra-announce-durable-agents-で切れても続くエージェント実行が標準機-01"
title: "[Mastra Announce] Durable Agents で「切れても続く」エージェント実行が標準機能に"
url: "https://zenn.dev/shiromizuj/articles/2ec8b9dcf4f8d3"
source: "zenn"
category: "claude-code"
tags: ["API", "AI-agent", "OpenAI", "GPT", "zenn"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の [公式Blog](https://mastra.ai/blog) で公開された announcement をもとに、関連 docs と reference を合わせて整理します。今回の Durable Agents は単なる stream の小改善ではなく、**長時間エージェントを現実のネットワークや process restart に耐えさせるための実行モデル**が、Mastra の標準 API として見えてきたアップデートです。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## 今回の発表をひとことで言うと

**Mastra の通常 `Agent` を、「接続が切れても再接続できる」「run が request より長生きできる」実行形へ包むための標準 API が入った** という発表です。

公式 docs の説明を短くまとめると、Durable Agent は次の 3 つを同時に満たそうとしています。

1. stream 中に client が落ちても reconnect できる
2. run state が保持され、process restart をまたいで継続できる
3. event を PubSub 経由で流し、observe / reconnect しやすくする

従来の「1 回の request の中で agent が最後まで走り切る」前提から一歩進んで、**長く動く agent runtime を first-class に扱う**方向がはっきり見えた、と読むのが自然です。

---

## 背景: なぜ Durable Agents が必要だったのか

短いチャット応答だけなら、普通の `.generate()` や `.stream()` で十分です。しかし最近の Mastra は、Task Lists、Signals、Notification Inbox、built-in event system、SDK subagents など、**数十秒から数分、場合によってはそれ以上動く agent runtime** をかなり前提にし始めています。

そうなると、次の問題が現実的になります。

* ブラウザをリロードしたら stream が見えなくなる
* モバイル回線や spotty network で途中切断が起きる
* background research のように、run が 1 回の HTTP request では収まらない
* 同じ run を別 client から引き継いで見たい
* worker や process の再起動で、その場の実行状態を失いたくない

ここで重要なのは、これは単なる UX の不満ではないことです。**長時間 agent は、接続と実行寿命を切り離さないと設計が苦しくなる**。Durable Agents は、そのための基礎 API です。

---

## 何が追加されたのか

### 1. `createDurableAgent()` が入った

いちばん中心になるのは `createDurableAgent()` です。通常の `Agent` をそのまま包み、durable execution と resumable streams を付与します。

```
import { Mastra } from "@mastra/core";
import { Agent } from "@mastra/core/agent";
import { createDurableAgent } from "@mastra/core/agent/durable";

const agent = new Agent({
  id: "my-agent",
  name: "My Agent",
  instructions: "あなたは役に立つアシスタントです。",
  model: "openai/gpt-5.5",
});

// 通常の Agent を durable execution 対応に包む
const durableAgent = createDurableAgent({ agent });

export const mastra = new Mastra({
  agents: {
    myAgent: durableAgent,
  },
});
```

reference を見ると、この durable wrapper は event を PubSub に流し、stream event を cache に保持できます。つまり、**stream の配信路と replay 用の保存先を明示的に持てる**のがポイントです。

### 2. `createEventedAgent()` も用意された

`createEventedAgent()` は、built-in workflow engine 上で fire-and-forget に近い durable execution を行う API です。通常の durable agent と同じく stream 可能ですが、underlying workflow は non-blocking に進みます。

ここで見えてくるのは、Mastra が durable execution を単一の実装に閉じず、\*\*「同じ agent surface のまま、下の実行エンジンだけ差し替えられる」\*\*方向を取っていることです。

### 3. `createInngestAgent()` で分散実行にも寄せられる

Inngest 版の durable agent も並行して用意されています。`createInngestAgent()` は PubSub と resumable streams の面では Durable Agent と似ていますが、**agentic loop 自体は Inngest の execution engine 上で走る**のが違いです。

これにより、in-process の durable execution から、より distributed な durable execution まで、同じ発想で広げられます。

---

## 何がうれしいのか

### 1. client と run の寿命を分離できる

これがいちばん大きいです。普通の stream は、どうしても「接続中の client が見ている間だけ成立する」色が強くなります。Durable Agents では、**run そのものを先に立て、その様子を client が後から追いかける**発想に寄せられます。

この違いは、長時間の coding agent や research agent ではかなり効きます。

### 2. reconnect 前提の UI を作りやすい

docs では、disconnect / reconnect、process restart、second client が途中から観測するケースが明確に挙げられています。これは逆に言うと、Mastra 側が「長時間 run の UI では reconnect は普通に起きる」と認めた、ということでもあります。

つまり今後の UI は、

* runId を保持する
* 切断後に再購読する
* 履歴や chunk の replay を前提に画面を復元する

という設計にしやすくなります。

### 3. background research のような用途に素直に合う

公式 docs でも、background research や multi-step tool use のような、request をまたぐ作業が Durable Agents の想定として挙げられています。これは Mastra の最近の流れとも一致しています。

* Signals で途中介入する
* Task Lists で計画と進捗を見せる
* Event system で cross-process に event を流す
* Durable Agents で run を長生きさせる

こうして並べると、Mastra は単発の chat completion ではなく、**継続実行される agent runtime** を徐々に部品化していると分かります。

### 4. process restart 耐性を agent 側にも持ち込める

Workflow の世界では durable execution は珍しくありませんでした。Mastra 自身も Workflow runner として Inngest や Temporal 方向を出してきています。ただ、agent 側はこれまで request/response 的に捉えられがちでした。

今回の Durable Agents は、その durable execution の考え方を **workflow ではなく agent loop 側へ持ち込んだ** ところに意味があります。

---

## 既存手法・関連機能との位置づけ

### 普通の `Agent` との違い

通常の `Agent` は、open-ended な仕事をその場で考えながら進める Mastra の基本単位です。ただし、run の寿命や reconnect を特別に意識しないなら、それで十分です。

Durable Agent はその上に、**長生きする run と resumable stream** を足したものと考えると分かりやすいです。

### Workflow との違い

Workflow は、手順がある程度決まっている処理に向いています。分岐、並列、再試行、suspend / resume のような制御を、開発者が明示的に設計できます。

一方 Durable Agents は、**手順は agent に任せたいが、実行寿命だけは durable にしたい**場面に向いています。

整理すると、こんな住み分けです。

* 手順を厳密に定義したい: Workflow
* 手順は open-ended だが長く動かしたい: Durable Agent

### Inngest / Temporal との関係

Mastra はすでに Workflow 側で durable execution との接続を強めてきました。今回の Durable Agents は、その発想を agent runtime にも広げたものです。

特に `createInngestAgent()` が同時に reference に並んでいるのは象徴的です。Mastra は durable execution を単に「workflow の話」に閉じず、**agent でも execution engine を差し替えられる世界観**を作ろうとしているように見えます。

---

## 導入時に気をつけたい点

### 1. beta である

docs にも warning があり、Durable Agents は現時点で beta です。API が今後変わる可能性は普通にあります。production で全面採用するなら、バージョン固定はかなり大事です。

### 2. cache を切ると resumable ではなくなる

reference では `cache` を `false` にすると stream は non-resumable になると説明されています。つまり、**Durable Agent を名乗っていても、どこまで durable かは cache / PubSub の構成次第**です。

### 3. PubSub 設計も一緒に考える必要がある

event は PubSub で流れるので、単に wrapper だけ追加して終わりではありません。特に複数 process や複数 host に広がるなら、event system 側の backend 選定まで含めて考える必要があります。

### 4. cleanup の扱いを忘れない

reference の usage では、stream 後に `cleanup()` で PubSub の購読解除を行います。実装時には、この lifecycle を UI や server handler 側できちんと回収する必要があります。

---

## まとめ

Durable Agents は、Mastra の agent を「もっと長く、もっと壊れにくく、もっと reconnect しやすく」するための標準 API です。

今回の発表で嬉しいのは、単に stream が再開できることではありません。

1. run が request より長生きできる
2. client disconnect を前提に UI を設計しやすい
3. process restart や distributed execution の方向へ広げやすい
4. workflow だけでなく agent loop 側にも durable execution の考え方が入ってきた

Mastra の最近の announcement を追っていると、Task Lists、Signals、Notification Inbox、Event System、SDK subagents と、全部が少しずつ同じ方向を向いています。今回の Durable Agents は、その流れの中でもかなり中心に近い部品です。**「単発の AI 応答」ではなく、「現実の不安定な接続や長時間作業に耐える agent runtime」を Mastra が本気で整え始めた** と見ると、この発表の意味がよく分かります。
