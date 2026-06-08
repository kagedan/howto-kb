---
id: "2026-06-07-claude-apiで自律型aiエージェントを作る-tool-use-fetch-apiで実装する実-01"
title: "Claude APIで「自律型AIエージェント」を作る — Tool Use × Fetch APIで実装する実践ガイド"
url: "https://zenn.dev/kasaharareo/articles/73f54ca3a623ab"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "OpenAI", "Gemini", "zenn"]
date_published: "2026-06-07"
date_collected: "2026-06-08"
summary_by: "auto-rss"
query: ""
---

## はじめに

前回の記事では、Claude / OpenAI / Gemini の3社APIをSDKに頼らずFetch API + SSEで統一する設計について書きました。

<https://zenn.dev/kasaharareo/articles/b9e89b27b51534>

今回はその続編として、**Claude APIのTool Use（Function Calling）機能**を使い、AIが自律的にツールを選んでタスクを実行する「**AIエージェント**」を実装します。

### AIエージェントとは？

普通のチャットボットは「質問→回答」の1往復で終わります。

一方、AIエージェントは違います。

1. ユーザーの質問を受け取る
2. 「この質問に答えるには何が必要か？」をAI自身が判断する
3. 必要なツール（API、DB検索、計算など）を**自分で選んで実行する**
4. 結果を見て、さらに別のツールが必要なら**再度実行する**
5. 十分な情報が揃ったら、最終回答を返す

つまり、AIが**自分で考えて、自分で動く**。これがエージェントの本質です。

### この記事で作るもの

Claude APIのTool Use機能を使って、以下を実装します。

* ツール定義（AIに「使える道具」を教える）
* 基本的なTool Useフロー（1往復）
* **自律型エージェントループ**（AIが自分で複数ツールを連続実行）
* エラーハンドリングと実運用のポイント

前回と同じく**SDKは使いません**。Fetch APIだけで実装します。

---

Tool Useのフローは、意外とシンプルです。

```
User: 「神戸の天気を教えて」
  ↓
Claude: 「天気を調べるために get_weather ツールを使います」
  ↓ ← stop_reason: "tool_use"
開発者: get_weather("神戸") を実行 → 結果を取得
  ↓
開発者: ツールの結果を Claude に返す
  ↓
Claude: 「神戸は27℃で晴れ時々曇りです」
  ↓ ← stop_reason: "end_turn"
```

ポイントは、**Claude自身がAPIを叩くわけではない**ということ。

Claudeは「このツールを、この引数で呼んでほしい」とリクエストするだけ。実際のツール実行は開発者側が行い、結果をClaudeに返します。この\*\*「AIが判断、人間（コード）が実行」\*\*という分業が、Tool Useの設計思想です。

### stop\_reason が鍵

Claude APIのレスポンスには `stop_reason` が含まれます。

| stop\_reason | 意味 |
| --- | --- |
| `"end_turn"` | 回答完了。ツール不要 |
| `"tool_use"` | ツールを使いたい。実行して結果を返してほしい |

この `stop_reason` を見て処理を分岐するだけで、エージェントが作れます。

---

## Step 1: ツールを定義する

まず、Claudeに「こんな道具が使えるよ」と教えます。

```
const tools = [
  {
    name: "get_weather",
    description: "指定された都市の現在の天気情報を取得します",
    input_schema: {
      type: "object",
      properties: {
        city: {
          type: "string",
          description: "天気を取得したい都市名（例: 東京、大阪、神戸）",
        },
      },
      required: ["city"],
    },
  },
  {
    name: "get_calendar",
    description: "指定された日付のスケジュールを取得します",
    input_schema: {
      type: "object",
      properties: {
        date: {
          type: "string",
          description: "日付（YYYY-MM-DD形式）",
        },
      },
      required: ["date"],
    },
  },
];
```

`description` は**Claudeがツールを選ぶ判断材料**になります。ここを曖昧に書くと、意図しないツールが呼ばれたり、逆に必要な時に呼ばれなかったりします。「何ができるか」「どんな入力が必要か」を具体的に書くのがコツです。

---

## Step 2: Claude API にリクエストを送る

前回の記事と同じく、Fetch APIでリクエストします。違いは `tools` パラメータが追加されるだけ。

```
async function callClaude(
  messages: Message[],
  tools: Tool[]
): Promise<ApiResponse> {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": process.env.ANTHROPIC_API_KEY!,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      tools,    // ← ここにツール定義を渡す
      messages,
    }),
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}
```

SSEは使わず、通常のJSONレスポンスで受け取ります。エージェントは「考える→ツール実行→また考える」のループなので、ストリーミングよりも同期的な処理の方がシンプルに書けます。

---

## Step 3: ツールを実行する

Claudeが「get\_weather を使いたい」と言ってきたら、実際にそのツールを実行します。

ここでは理解しやすいようにダミーデータを返していますが、本番では外部APIやデータベースへの問い合わせに置き換えます。

```
function executeTool(
  name: string,
  input: Record<string, unknown>
): string {
  switch (name) {
    case "get_weather": {
      // 本番: OpenWeatherMap API 等を呼ぶ
      const city = input.city as string;
      const weatherData: Record<string, { temp: number; condition: string }> = {
        "東京": { temp: 28, condition: "晴れ" },
        "大阪": { temp: 30, condition: "曇り" },
        "神戸": { temp: 27, condition: "晴れ時々曇り" },
      };
      const data = weatherData[city] || { temp: 25, condition: "不明" };
      return JSON.stringify({
        city,
        temperature: data.temp,
        condition: data.condition,
        humidity: 65,
      });
    }

    case "get_calendar": {
      // 本番: Google Calendar API 等を呼ぶ
      return JSON.stringify({
        date: input.date,
        events: [
          { time: "10:00", title: "チームMTG" },
          { time: "14:00", title: "コードレビュー" },
          { time: "18:00", title: "フリー" },
        ],
      });
    }

    default:
      return JSON.stringify({ error: `Unknown tool: ${name}` });
  }
}
```

**返り値は必ず文字列（JSON文字列）にする**のがポイントです。Claudeはこの文字列を読んで次の判断をします。

---

ここまでのパーツを組み合わせて、1往復のTool Useを実装します。

```
async function basicToolUse() {
  const userMessage = "神戸の天気を教えて";
  const messages: Message[] = [{ role: "user", content: userMessage }];

  // 1. Claude に聞く（ツール定義付き）
  const firstResponse = await callClaude(messages, tools);

  if (firstResponse.stop_reason === "tool_use") {
    // 2. Claude が使いたいツールを取り出す
    const toolUseBlock = firstResponse.content.find(
      (block) => block.type === "tool_use"
    );

    // 3. ツールを実行
    const toolResult = executeTool(toolUseBlock.name, toolUseBlock.input);

    // 4. 結果を Claude に返す
    messages.push({ role: "assistant", content: firstResponse.content });
    messages.push({
      role: "user",
      content: [{
        type: "tool_result",
        tool_use_id: toolUseBlock.id,
        content: toolResult,
      }],
    });

    // 5. Claude が最終回答を生成
    const finalResponse = await callClaude(messages, tools);
    const textBlock = finalResponse.content.find(
      (block) => block.type === "text"
    );
    console.log(textBlock.text);
  }
}
```

ここで注意すべきは **messages の組み立て方**です。

ツール結果を返す時、`role: "user"` で `type: "tool_result"` を送ります。直感的には「ツールの結果だから assistant では？」と思いがちですが、**ツール結果は user ロールで送る**のがClaude APIの仕様です。

会話の流れとしては：

```
messages[0]: { role: "user",      content: "神戸の天気を教えて" }
messages[1]: { role: "assistant", content: [tool_use block] }     ← Claudeの応答をそのまま
messages[2]: { role: "user",      content: [tool_result block] }  ← 結果は user で返す
```

---

## Step 5: 自律型エージェントループ

ここが**この記事の核心**です。

Step 4 は「ツール1回呼んで終わり」でしたが、実際のエージェントは**何回ツールを呼ぶか事前にわからない**。Claudeが「もう十分」と判断するまでループを回す必要があります。

```
async function agentLoop(userMessage: string): Promise<string> {
  const messages: Message[] = [{ role: "user", content: userMessage }];
  const MAX_ITERATIONS = 10; // 無限ループ防止

  for (let i = 0; i < MAX_ITERATIONS; i++) {
    const response = await callClaude(messages, tools);

    // end_turn → 最終回答
    if (response.stop_reason === "end_turn") {
      const textBlock = response.content.find(
        (block) => block.type === "text"
      );
      return textBlock?.text || "";
    }

    // tool_use → ツール実行して続行
    if (response.stop_reason === "tool_use") {
      messages.push({ role: "assistant", content: response.content });

      // 複数ツール同時呼び出し（parallel tool use）に対応
      const toolUseBlocks = response.content.filter(
        (block) => block.type === "tool_use"
      );

      const toolResults = toolUseBlocks.map((toolBlock) => {
        const result = executeTool(toolBlock.name, toolBlock.input);
        return {
          type: "tool_result" as const,
          tool_use_id: toolBlock.id,
          content: result,
        };
      });

      messages.push({ role: "user", content: toolResults });
    }
  }

  return "最大実行回数に達しました";
}
```

**たったこれだけ**で、AIエージェントが動きます。

重要なのは `for` ループの中身がとてもシンプルだということ。やっていることは：

1. Claudeに聞く
2. `stop_reason` を見る
3. `"end_turn"` なら終了、`"tool_use"` ならツール実行して次のループへ

この\*\*「判断はAIに任せ、実行は人間（コード）が行う」\*\*というパターンが、AIエージェントの設計原則です。

Claudeは1回のレスポンスで**複数のツールを同時に呼ぶ**ことがあります。

例えば「神戸の天気と明日の予定を教えて」と聞くと、`get_weather` と `get_calendar` が1回のレスポンスに含まれることがあります。

```
{
  "content": [
    { "type": "text", "text": "天気と予定を調べますね。" },
    { "type": "tool_use", "name": "get_weather", "input": { "city": "神戸" } },
    { "type": "tool_use", "name": "get_calendar", "input": { "date": "2026-06-08" } }
  ],
  "stop_reason": "tool_use"
}
```

だから `find` ではなく `filter` で全ての `tool_use` ブロックを取り出し、それぞれ実行して結果を返すのがポイントです。

---

## Step 6: 実行してみる

```
// シンプルな質問（ツール1回で完結）
await agentLoop("神戸の天気を教えて");
// → 「神戸は27℃で晴れ時々曇りです。湿度は65%で...」

// 複合的な質問（複数ツールを自律的に実行）
await agentLoop(
  "明日の神戸の天気と、明日のスケジュールを確認して、" +
  "外出に適した時間帯を提案して"
);
// → Claude が天気とカレンダーを両方取得し、
//   「18:00のフリー枠は天気も良いので外出に最適です」
//   のような回答を自動で生成する
```

2つ目の質問が面白いポイントです。

ユーザーは「外出に適した時間帯を提案して」と言っただけ。「天気APIを呼べ」「カレンダーAPIを呼べ」とは一言も言っていません。Claudeが**自分で「天気とスケジュールの両方が必要だ」と判断**して、必要なツールを選んで実行します。

これが「エージェント」と「チャットボット」の決定的な違いです。

---

## Step 7: エラーハンドリング

実運用では、ツールの実行が失敗することがあります。外部APIのタイムアウト、認証エラー、不正なパラメータなど。

**重要: ツールが失敗しても、エラーをClaudeに返す**。

```
function executeToolSafely(
  name: string,
  input: Record<string, unknown>
): string {
  try {
    return executeTool(name, input);
  } catch (error) {
    // エラーをClaudeに伝える → Claudeが対処法を考える
    return JSON.stringify({
      error: true,
      message: error instanceof Error ? error.message : "Unknown error",
      tool: name,
      input,
    });
  }
}
```

エラーが起きた時に例外を投げてループを止めるのではなく、**エラー情報をClaudeに返す**のが正解です。Claudeは「このツールがエラーになったから、別のアプローチを試そう」「ユーザーにエラーの状況を説明しよう」と自分で判断できます。

### その他の実運用ポイント

**タイムアウト設定**

```
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 30000); // 30秒

const response = await fetch(url, {
  ...options,
  signal: controller.signal,
});
clearTimeout(timeout);
```

**コスト管理**

```
// レスポンスの usage からトークン数を取得
console.log(`Input: ${response.usage.input_tokens} tokens`);
console.log(`Output: ${response.usage.output_tokens} tokens`);

// ループ内でトークン合計を監視
let totalTokens = 0;
const TOKEN_LIMIT = 10000;

// ループ内で
totalTokens += response.usage.input_tokens + response.usage.output_tokens;
if (totalTokens > TOKEN_LIMIT) {
  console.warn("Token limit reached");
  break;
}
```

**MAX\_ITERATIONS は必ず設定する**

無限ループ防止のために `MAX_ITERATIONS` は必須です。Claudeが「ツールAの結果を見てツールBを呼び、Bの結果を見てまたAを呼ぶ」という無限ループに入る可能性はゼロではありません。10回もあれば十分で、通常のエージェントは2〜3回で完了します。

---

## まとめ

実装を振り返ると、AIエージェントの核心は驚くほどシンプルです。

1. ツールを定義して Claude に教える
2. `stop_reason` を見てループを回す
3. `"tool_use"` ならツール実行、`"end_turn"` なら終了

**コードにして50行程度**で、自律型AIエージェントが動きます。

前回の記事で「SDKに頼らない設計」にこだわったのと同じで、今回もFetch APIだけで実装しました。仕組みを理解していれば、どんなフレームワークでも応用が効きます。

### 発展のアイデア

この基本構造をベースに、ツールを追加するだけで様々なエージェントが作れます。

* **業務自動化エージェント**: Google Sheets API + Gmail API を追加して、データ集計→レポート作成→メール送信を自動化
* **カスタマーサポートエージェント**: FAQ検索 + チケット作成 + エスカレーション判断を自律実行
* **コンテンツ作成エージェント**: Web検索 + 画像生成 + CMS投稿を連続実行

エージェントの能力は「どんなツールを与えるか」で決まります。ループの仕組みは同じで、ツールを差し替えるだけ。この拡張性がTool Useの最大の強みです。

---

前回の記事と合わせて読んでいただくと、Claude APIの全体像が見えてくると思います。

質問やフィードバックがあれば、ぜひコメントください。

<https://zenn.dev/kasaharareo/articles/b9e89b27b51534>
