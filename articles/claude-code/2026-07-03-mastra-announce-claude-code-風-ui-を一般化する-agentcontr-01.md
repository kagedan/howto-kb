---
id: "2026-07-03-mastra-announce-claude-code-風-ui-を一般化する-agentcontr-01"
title: "[Mastra Announce] Claude Code 風 UI を一般化する AgentController が見せる次の実装レイヤ"
url: "https://zenn.dev/shiromizuj/articles/4f5b4b80b8baec"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "OpenAI", "GPT"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で公開された[Features](https://mastra.ai/blog/category/features)記事をもとに、今回の発表が何を意味するのかを整理します。今回は単なる API 追加というより、Mastra が **長時間動く対話型エージェントの UI/制御層** をどう捉えているかがよく見える発表です。公式アナウンスは短めですが、埋め込まれていた YouTube デモもあわせて見ると、何が新しく、どこが実務に効くのかがかなりはっきりします。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

## Claude Code そのものではなく、Claude Code 的な体験を作るための制御層

2026年6月30日、Mastra の Alex Booker は [Build Claude Code for X with Agent Controller](https://mastra.ai/blog/build-claude-code-for-x-with-agentcontroller) を公開しました。記事の主題はシンプルで、**Claude Code のような「会話しながら進行し、途中でモードを変え、必要なら承認を挟み、状態を持続する」体験を、任意ドメイン向けに作れるようにする** というものです。

ここで重要なのは、Mastra が Claude Code 互換ツールを出したと言っているわけではないことです。そうではなく、**Claude Code 的な使い心地を支えるランタイム要素を、アプリケーションとして再利用できる形に切り出した**、という理解が正確です。

記事の冒頭でも、AgentController は次のような状況で使うものだと整理されています。

* 単発応答ではなく、ユーザーと継続的に協調する
* planning と execution のようにモードを切り替える
* ツール実行前に承認フローを入れる
* サブエージェントへ一部タスクを委譲する
* スレッドや状態を再開する
* 実行状況を UI にイベントとして流す

つまり今回の発表は、モデルの能力を増やす話ではなく、**エージェントを「使い続けられる製品」にするための制御面を整える話**です。

---

## 背景: 以前の Harness から、より役割の明確な AgentController へ

今回の API は、少し前に発表された [Mastra Harness](https://mastra.ai/blog/announcing-agent-harness) の延長線上にあります。

<https://zenn.dev/shiromizuj/articles/b2be08f68477ec>

名称変更の理由はかなり納得感があります。Mastra 自体が広い意味ではエージェントのハーネスであり、そのうえでさらに `Harness` という名前の API を置くと、責務の境界が見えにくかったからです。

ここで注意したいのは、**今回の 6 月 30 日発表そのものは、機能の大規模追加というより rename が中心**だという点です。sessions、modes、threads、permissions、subagents、event system といった中核機能は、すでに Harness 時代から備わっていました。したがって実態としては「別物になった」というより、**既存機能の責務をより正確に言い表す名前へ寄せた** と見るのが適切です。つまり、単なるラベル変更ではないものの、主眼は新機能の投入ではなく、Mastra 本体とこの API の境界を明瞭にするための概念整理にあります。

公式説明を噛み砕くと、責務の分担はこうなります。

* Mastra 本体: モデル、ツール、メモリ、ワークフロー、ストレージ、人間参加型制御など、エージェント実行の基礎インフラ
* AgentController: その上に載る対話的な体験の制御層。Session、Mode、Thread、Permission、Subagent、Model switching、UI event をまとめて扱う

この分け方はかなり実務的です。Agent 単体だけでアプリを作ろうとすると、どうしても次の処理を自前で配線することになります。

* どの会話が今アクティブか
* どのモードで動いているか
* 危険なツールは承認待ちにするか
* 実行中にユーザーが別メッセージを差し込めるか
* プロセスが落ちたあとに続きから復元できるか
* UI にいま何が起きているかをどう見せるか

AgentController は、この「UI と agent loop の間に必ず生えるコード」を抽象化したものです。Mastra の docs が `The AgentController sits between your application layer and the underlying agent loop` と書いているのは、まさにそこを指しています。

---

## 何が作れるのか: コーディングエージェントに限らない

アナウンスは Claude Code 的なコーディング体験を入り口にしていますが、同時に「それだけではない」とかなり強く主張しています。ドキュメントでも、次のような領域が想定されています。

* オーケストレータ
* エンジニアリングツール
* 金融ワークフロー
* リサーチアシスタント
* 法務レビューシステム
* セキュリティエージェント

この広がりを理解するには、AgentController が提供する機能を「コーディング専用機能」としてではなく、**長時間協調のための状態機械**として見ると分かりやすいです。

### 1. Session と Threads

セッションは、現在どの thread を見ているか、どの mode か、どの model か、どんな approval grant が付いているか、といった実行文脈を持ちます。スレッドを再開できるので、ユーザーは「昨日の続き」からそのまま始められます。

### 2. Modes

同じ会話コンテキストを保ったまま、plan から build、research から draft のように役割を切り替えられます。単なる system prompt の差し替えではなく、モードごとに instructions、tools、model を束ねて定義できるのがポイントです。

ファイル書き込みや本番デプロイのような危険操作だけ承認制にし、読み取り系は自動許可する、といった運用ができます。これは人間参加型制御の要です。

### 4. Subagents

親エージェントから、ツール制約を持つ子エージェントへ仕事を切り出せます。親スレッドを汚さずに調査だけ任せる、といった分業がしやすくなります。

### 5. Event system

UI 側は typed event を購読し、メッセージ更新、モード変更、承認待ち、利用量変化などをリアルタイム描画できます。ターミナル UI でも Web UI でも同じイベントに乗れるので、実装の軸が揃います。

この組み合わせは、Claude Code のような coding agent にぴったりですが、同時に「長時間動く社内エージェント全般」にもそのまま効きます。

---

## YouTube デモで見える本質: ブログ執筆ハーネスでも成立する

公式アナウンス中に埋め込まれていた短いデモ動画は約4分で、実質的には「AgentController で何が嬉しいか」を最短で示す内容になっています。面白いのは、ここで作っているのが coding harness ではなく **blog writing harness** だという点です。

デモでは次の流れが見えます。

1. `plan` モードで構成案を作る
2. モデル一覧を見て、その場で切り替える
3. セッションを「プロジェクト」として作る
4. その中に post1/post2 のような thread を切る
5. `write` モードへ移って本文を書く
6. research subagent が裏で複数の検索を走らせる
7. ファイル書き込み前に permission approval を要求する
8. YOLO mode をオンにすると承認をスキップできる
9. UI 上のグレー文字はすべて event から描画されている

このデモで見せているのは、「Claude Code クローンを作る」ことではなく、**Claude Code 的 UX の構成要素を一般化して見せている** ところです。ブログ執筆ですら、planning、mode switch、subagent research、approval gating、event-driven UI が必要になる。ならばコーディングに限らず、多くの agent product に同じ層が要るわけです。

動画内の説明で特に印象的なのは、mode を「profile や persona のようなもの」と説明している点です。同じベースエージェントでも、モードごとに違う顔と違う権限を持てる。この考え方は非常に実装しやすいです。

---

## 実装イメージ: UI と Agent の間に Controller を置く

公式 Quickstart はかなり短いですが、実際にどんな責務を載せるのかはよく分かります。最小構成はこんなイメージです。

```
import { Agent } from "@mastra/core/agent";
import { AgentController } from "@mastra/core/agent-controller";
import { LibSQLStore } from "@mastra/libsql";

const blogAgent = new Agent({
  id: "blog-agent",
  name: "blog-agent",
  instructions: "ユーザーの依頼を整理し、記事制作を前に進めてください。",
  model: "openai/gpt-5.5",
});

const controller = new AgentController({
  id: "blog-harness",
  agent: blogAgent,
  storage: new LibSQLStore({ url: "file:./data.db" }),
  modes: [
    {
      id: "plan",
      name: "Plan",
      metadata: { default: true },
      instructions: "最初は構成案を作り、いきなり本文を書かないでください。",
    },
    {
      id: "write",
      name: "Write",
      instructions: "承認された構成に沿って本文を書いてください。",
    },
  ],
});

controller.subscribe((event) => {
  if (event.type === "message_update") {
    console.log(event.message);
  }

  if (event.type === "tool_approval_required") {
    // 危険な操作だけ人間に確認させる
    console.log(`承認待ち: ${event.toolName}`);
  }
});

await controller.init();
await controller.selectOrCreateThread();
await controller.sendMessage({ content: "評価設計の記事シリーズを始めたい" });
```

このコード例だけでも、Mastra が AgentController を「単なる helper」ではなく **永続化・モード・イベント・権限を束ねるホスト** と見ていることが伝わります。

---

## どこが実務に効くのか

### 1. 単発チャットから「継続プロジェクト」へ上げやすい

セッションとスレッドが標準であるため、チャット体験をそのまま project/workspace 単位の作業体験へ育てやすいです。動画でも、session がプロジェクト、thread が個別記事という説明になっていました。これはブログ執筆だけでなく、issue 対応、設計レビュー、調査タスクでも自然です。

### 2. Plan と Execute を分けやすい

AI 製品では、いきなり実行させるより、まず計画させたいケースが多いです。AgentController は mode を正式機能として持つので、plan-only、execute-only、review-only といった責務分離がしやすいです。

### 3. Approval が「都度確認」から「運用ポリシー」になる

Mastra Harness 時代からの特徴ですが、承認は単発の yes/no ではなく、session をまたぐ権限管理に近い形で扱えます。たとえば read は常時許可、write は都度承認、deploy は常時拒否、といった設計にしやすいです。ここは coding agent を本番投入するならかなり重要です。

### 4. Web UI と TUI の両方を作りやすい

動画ではグレー文字が event だと説明されていました。これが示しているのは、表示が端末寄りかブラウザ寄りかは二次的で、**実体は event-driven state machine** だということです。Mastra Code のような TUI を作ることもできるし、同じイベントで Web アプリを動かすこともできます。

### 5. サブエージェントの責務を UI 体験に自然に埋め込める

単に agent が subagent を呼べるだけでなく、Controller がその進行や状態を UI イベントとして表に出せるのが効きます。ユーザーから見ると「裏で別の調査役が動いている」ことが分かるので、長時間処理の安心感が増します。

---

## 既存手法との位置づけ: Agent 単体より一段上の抽象化

Mastra にはもともと `Agent` クラスがあります。なので「全部 Agent で作ればいいのでは」とも思えます。docs でもそこは率直に書かれていて、単純な request-response やフルカスタム制御なら `Agent` を直接使えばよい、としています。

そのうえで AgentController が必要になるのは、次のような場合です。

* 1回の応答では終わらない
* 実行中に人間が割り込みたくなる
* モードやモデルを対話中に変えたい
* 危険ツールの承認フローを入れたい
* UI 側で「今何が起きているか」を常時出したい
* 再起動後に中断地点から再開したい

この意味では、AgentController は Agent の代替というより、**Agent を製品として見せるための上位レイヤ**です。旧名 Harness の思想を受け継ぎつつ、役割をより明確にした名前にしたのは正しい判断だと思います。

---

## まとめ

今回の発表は、見た目以上に重要です。新しい foundation model が増えたわけでも、派手な推論手法が追加されたわけでもありません。しかし、実際にユーザーが使い続ける agent product を作ろうとすると、必要になるのはむしろこうした制御層です。

Mastra はすでに Agent、Workflow、Workspace、Signals、Observational Memory などを揃えてきました。その流れの中で AgentController は、**「優秀な agent を作る」から「使い続けられる agent application を組み立てる」へ重心を移す API** だと読めます。

Claude Code 風の coding experience を作る入口として分かりやすい一方、本質はそこに留まりません。セッション、モード、承認、サブエージェント、イベント、状態永続化という部品は、今後の業務アプリ型 agent にかなり広く再利用されるはずです。短い発表ですが、Mastra が次にどのレイヤを取りにいこうとしているかを示す記事でした。

---

## 関連リンク
