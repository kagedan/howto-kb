---
id: "2026-05-21-chat-sdk-anthropic-managed-agents-で作る-slack-ai-エージ-01"
title: "Chat SDK × Anthropic Managed Agents で作る Slack AI エージェント"
url: "https://zenn.dev/titabash/articles/fafa0c3b676625"
source: "zenn"
category: "claude-code"
tags: ["API", "AI-agent", "LLM", "TypeScript", "zenn"]
date_published: "2026-05-21"
date_collected: "2026-05-22"
summary_by: "auto-rss"
query: ""
---

## はじめに

この記事では、**Vercel が公開している Chat SDK** と **Anthropic Managed Agents** を組み合わせて、Slack 上で動作する AI エージェントを構築する方法を解説します。

「Slack に AI エージェントを乗せる」だけなら `@slack/bolt` + LLM SDK 直叩きでも作れます。ただしその構成は、

* Discord や Teams への横展開で**全部書き直し**になる
* Agent 側の skill 管理や session 永続化を**自前**で実装する必要がある
* 進捗表示・並列実行・人間承認 (HITL) を**毎回スクラッチ**になる

という辛さがあります。Chat SDK は前者、Managed Agents は後者を吸収してくれる組み合わせなので、業務でちゃんと使うエージェントを作るときに有力な選択肢です。

**この記事でわかること：**

* Chat SDK と Managed Agents それぞれの役割
* Slack webhook を Chat SDK で受けてエージェントへ橋渡しする方法
* Managed Agents の応答を Slack に流し戻す方法
* Slack の `assistant.threads.setStatus` を進捗インジケータとして転用するテクニック

**前提知識：** TypeScript / Slack Bot 開発の基礎 / Anthropic API を触ったことがある

---

## アーキテクチャ全体像

最初に全体像を示します。

ポイントは **責務分離** です。

| レイヤー | 担当 |
| --- | --- |
| Chat SDK | プラットフォーム差分の吸収（Slack / Discord / Teams） |
| Managed Agents | session 永続化、skill 管理、stream 配信 |
| dispatcher | 両者を繋ぐ薄いグルー |

---

## Chat SDK とは

[Chat SDK](https://chat.vercel.ai/) は **チャットプラットフォーム横断のアダプタ層** を提供する npm パッケージです。Slack / Discord / Teams などのプラットフォーム固有の webhook ペイロードを共通の `Thread` / `Channel` / `Message` インターフェースに正規化してくれます。

```
import { createChatInstance } from "chat";
import { slackAdapter } from "@chat-adapter/slack";

const bot = createChatInstance({
  adapters: [
    slackAdapter({
      signingSecret: process.env.SLACK_SIGNING_SECRET!,
      clientId: process.env.SLACK_CLIENT_ID!,
      clientSecret: process.env.SLACK_CLIENT_SECRET!,
    }),
  ],
});

// プラットフォーム横断の event handler
bot.onNewMessage(/<@/, async ({ thread, message, ctx }) => {
  await thread.post(`Hello, <@${message.userId}>`);
});
```

`onNewMessage` / `onMention` / `onDirectMessage` などのハンドラを登録するだけで、Slack でも Discord でも同じコードで動きます。

---

## Anthropic Managed Agents とは

[Anthropic Managed Agents](https://docs.claude.com/en/api/agent-sdk/overview) は **エージェントのセッション・スキル・実行履歴を Anthropic 側でホストしてくれる API** です。`create_agent` で作った agent に対して `sessions` を作り、`messages` を流し込むと、agent が考えてツールを叩いてストリームを返してくれます。

```
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

// エージェントを作成
const agent = await client.beta.agents.create({
  model: "claude-opus-4-5",
  system: "あなたは Slack 上で動作する有能なアシスタントです。",
  skills: ["my-skill-id"],
});

// セッションを開始
const session = await client.beta.agents.sessions.create({
  agent_id: agent.id,
});

// メッセージを送る（ストリーム応答）
const stream = await client.beta.agents.sessions.messages.create({
  agent_id: agent.id,
  session_id: session.id,
  content: "今日のタスクを整理して",
  stream: true,
});

for await (const event of stream) {
  // event.type: "agent.message" / "session.status_idle" / etc.
}
```

ローカルで session を永続化したり、skill ファイルを bundle してデプロイしたりする必要がありません。複雑なエージェントを **stateless なクライアント側コード** から扱える点が強みです。

---

## Slack App セットアップ

### 必須スコープ

OAuth & Permissions で以下を追加：

* `app_mentions:read`
* `chat:write`
* `im:history`
* `im:read`
* `assistant:write` ← `setStatus` 転用に必須
* `channels:history`（必要に応じて）

### 必須イベント

Event Subscriptions で以下を購読：

### URL の登録（3 箇所）

Slack App ダッシュボードの以下 3 箇所はそれぞれ **別の Request URL フィールド**を持っています。同じ webhook URL でよいので、全部に `https://your-app.example.com/api/webhooks/slack` を入れます。

| 設定画面 | フィールド名 | 必要性 |
| --- | --- | --- |
| Event Subscriptions | Request URL | 必須（メンション・DM 受信） |
| Interactivity & Shortcuts | Request URL | Block Kit のボタンを使うなら必須 |
| Slash Commands | Request URL | スラッシュコマンドを使うなら必須 |

---

## Webhook receiver の実装

Chat SDK は webhook ペイロードのパースと署名検証を肩代わりしてくれます。

```
// /api/webhooks/slack/route.ts
import { bot } from "@/lib/bot";

export async function POST(request: Request) {
  const response = await bot.handleWebhook(request, { platform: "slack" });
  return response;
}
```

リクエストを Chat SDK に丸投げするだけで、内部で adapter が「これは event\_callback だ」「これは interactive payload だ」と判別してくれます。

Content-Type の区別

Slack は event 通知を JSON で、Block Kit 操作を `application/x-www-form-urlencoded` で送ってきます。Chat SDK が両方ハンドルしてくれるので自前で `Content-Type` を見る必要はありません。

---

## メンションを受けて Managed Agents に橋渡しする

ここが記事の本題です。

### イベントハンドラ

```
// /lib/bot.ts
import { createChatInstance, type Thread } from "chat";
import { slackAdapter } from "@chat-adapter/slack";
import { dispatchToAgent } from "./dispatcher";

export const bot = createChatInstance({
  adapters: [slackAdapter({ /* config */ })],
});

bot.onNewMessage(/<@/, async ({ thread, message, ctx }) => {
  // 自分宛のメンションだけ反応
  if (!message.text.includes(`<@${ctx.botUserId}>`)) return;

  await dispatchToAgent({
    thread,
    userMessage: message.text,
    userId: message.userId,
  });
});

bot.onDirectMessage(async ({ thread, message }) => {
  await dispatchToAgent({
    thread,
    userMessage: message.text,
    userId: message.userId,
  });
});
```

### ディスパッチャ：Slack ↔ Agents session を紐付ける

ディスパッチャの責務は3つ。

1. Slack スレッドに対応する agent session を解決（無ければ作る）
2. ユーザーメッセージを agent に送ってストリームを開く
3. ストリームイベントを Slack に橋渡しする

```
// /lib/dispatcher.ts
import Anthropic from "@anthropic-ai/sdk";
import type { Thread } from "chat";
import { getOrCreateSession } from "./session-store";
import { translateAgentEvent } from "./notifier";

const client = new Anthropic();
const AGENT_ID = process.env.ANTHROPIC_AGENT_ID!;

export async function dispatchToAgent(input: {
  thread: Thread;
  userMessage: string;
  userId: string;
}) {
  const { thread, userMessage, userId } = input;

  // ① スレッドに紐づく session を取得（無ければ作成）
  const sessionId = await getOrCreateSession({
    threadId: thread.id,
    userId,
  });

  // ② "考え中..." を表示
  await thread.setStatus("考え中…");

  try {
    // ③ Managed Agents にメッセージ送信
    const stream = await client.beta.agents.sessions.messages.create({
      agent_id: AGENT_ID,
      session_id: sessionId,
      content: userMessage,
      stream: true,
    });

    // ④ stream event を Slack に翻訳
    for await (const event of stream) {
      await translateAgentEvent({ event, thread });
    }
  } finally {
    // ⑤ 必ずステータスをクリア
    await thread.setStatus("");
  }
}
```

### session の永続化

agent session ID は **Slack の thread ごとに永続化する** 必要があります。最小実装は KV ストアでよいですが、要件次第で DB に保存します。

```
// /lib/session-store.ts
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();
const sessionMap = new Map<string, string>(); // 実装では永続ストアに置き換え

export async function getOrCreateSession(input: {
  threadId: string;
  userId: string;
}): Promise<string> {
  const existing = sessionMap.get(input.threadId);
  if (existing) return existing;

  const session = await client.beta.agents.sessions.create({
    agent_id: process.env.ANTHROPIC_AGENT_ID!,
    metadata: { thread_id: input.threadId, user_id: input.userId },
  });

  sessionMap.set(input.threadId, session.id);
  return session.id;
}
```

---

## ストリームイベントを Slack に翻訳する

Managed Agents は以下のような event を流してきます。

| event.type | 意味 |
| --- | --- |
| `agent.message` | エージェントの応答テキスト（部分） |
| `agent.tool_use` | ツール呼び出し開始 |
| `agent.tool_result` | ツール呼び出し結果 |
| `session.thread_message_created` | サブエージェントが動き始めた |
| `session.status_idle` | このターン完了 |

これらを Slack の `thread.post()` と `setStatus()` に翻訳します。

```
// /lib/notifier.ts
import type { Thread } from "chat";

export async function translateAgentEvent(input: {
  event: any; // Anthropic SDK の event 型
  thread: Thread;
}) {
  const { event, thread } = input;

  switch (event.type) {
    case "agent.message": {
      // 最終応答を Slack に投稿
      if (event.content) {
        await thread.post(event.content);
      }
      break;
    }
    case "agent.tool_use": {
      // ツール呼び出し中は status に表示（thread には post しない）
      await thread.setStatus(`${event.tool_name} を実行中…`);
      break;
    }
    case "session.thread_message_created": {
      // サブエージェント稼働中
      await thread.setStatus("詳細を調査中…");
      break;
    }
    case "session.status_idle": {
      // 完了
      await thread.setStatus("");
      break;
    }
  }
}
```

---

## `setStatus` の実体

`Thread.setStatus()` は Slack adapter 経由で **`assistant.threads.setStatus`** API を呼びます。これは元々 Slack の Assistant Threads 機能向けに用意された API ですが、通常の Bot スレッドでも呼べます。

Slack 上では thread の入力欄下に `Bot が "考え中…" と表示` と灰色テキストが表示されます。ユーザーから見ると「AI アシスタントが動いている」という UX になり、待ち時間の体感が大きく改善します。

```
// 例：ツール実行ごとに status を更新
await thread.setStatus("コードを生成中…");
await thread.setStatus("テストを実行中…");
await thread.setStatus("結果をまとめています…");
// 応答投稿前に空文字でクリア
await thread.setStatus("");
```

### メンションから応答までのタイムライン

実際にユーザーがメンションしてから応答が返るまで、内部で何が起きているかをシーケンスで示します。

このフローによって、**ユーザーは「待たされている」のではなく「動いているのが見える」** 体験を得られます。

---

## 動作確認

### ローカルでの起動

webhook を Slack から受けるには公開 URL が必要です。開発時は ngrok / Cloudflare Tunnel を使います。

```
cloudflared tunnel --url http://localhost:3000
```

吐き出された URL を Slack App の Event / Interactivity / Slash Command の **3 つの Request URL 欄すべて** に登録します。

![](https://static.zenn.studio/user-upload/370102ac6b14-20260521.png)

![](https://static.zenn.studio/user-upload/a983a30f6836-20260521.png)

### 動作チェックリスト

---

## 本番運用時に詰まりやすいポイント

実装が動いた後、運用フェーズで踏みやすい落とし穴を3つ挙げます。

### 1. ストリーム中断時の status クリア漏れ

LLM のストリーム途中で例外が出ると、`setStatus("")` を呼ばずに終わって **「考え中…」が永遠に残る** ことがあります。必ず `try / finally` で囲んでください。

### 2. 同じスレッドへの並列メッセージ

ユーザーが Bot の応答前に追加メッセージを送ると、同じ session に対して並列に message create が走り、agent 側で race condition になります。Chat SDK の concurrency lock や、ディスパッチャ側で **thread 単位のキュー** を持つことを検討してください。

### 3. session\_idle ≠ 「全部終わった」

`session.status_idle` は **このターン** が終わった signal です。マルチエージェント構成だと別の `thread_*` event がまだ流れていることがあるので、「完了」文言を `setStatus` に出すのは `session.status_idle` のみに限定するのが安全です。

---

## まとめ

この記事では以下を解説しました：

* ✅ Chat SDK で Slack webhook を抽象化して受ける
* ✅ Managed Agents の session を Slack スレッドと 1:1 で紐付ける
* ✅ stream event を `thread.post()` と `setStatus()` に翻訳する
* ✅ Slack の `assistant.threads.setStatus` を「AI アシスタント感」の演出に転用する

この構成は、後から **Discord や Teams への展開** が比較的低コストで済みます。Chat SDK の adapter を足して、event handler の差分だけ書けば横展開できるためです。

「単一プラットフォームかつ単機能エージェント」なら過剰な構成ですが、**プラットフォーム横断 × マルチエージェント × 長期運用** を見据えるなら検討する価値があります。

## 参考

<https://chat.vercel.ai/>

<https://docs.claude.com/en/api/agent-sdk/overview>

<https://api.slack.com/methods/assistant.threads.setStatus>
