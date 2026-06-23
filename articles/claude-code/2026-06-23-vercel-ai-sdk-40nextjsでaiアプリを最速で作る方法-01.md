---
id: "2026-06-23-vercel-ai-sdk-40nextjsでaiアプリを最速で作る方法-01"
title: "Vercel AI SDK 4.0──Next.jsでAIアプリを最速で作る方法"
url: "https://note.com/fragments_jp/n/n91ec73294a43"
source: "note"
category: "claude-code"
tags: ["API", "OpenAI", "Gemini", "GPT", "note"]
date_published: "2026-06-23"
date_collected: "2026-06-23"
summary_by: "auto-rss"
query: ""
---

AIチャットアプリを作ろうとして、最初に詰まるのはバックエンドとフロントエンドの繋ぎ目だ。

ストリーミングをどう実装するか。Claudeのレスポンスをリアルタイムで表示するにはSSEか、WebSocketか。モデルを切り替えるたびにAPIのインターフェースが違う。

これを全部自分で実装していた。100行書いて、エラーで止まって、また書き直した。

**Vercel AI SDK 4.0**を使ったら、そのコードが10行になった。手元で計測した。バックエンド7行、フロントエンド3行のuseChat一発でストリーミングチャットが動く。

---

## Vercel AI SDK とは

Next.jsなどのフロントエンドフレームワークからAIモデルを呼び出すためのライブラリだ。

**何が嬉しいか：**  
1. **プロバイダー統一**：ClaudeもGPTもGeminiも同じコードで呼び出せる  
2. **ストリーミング内蔵**：リアルタイムで文字が表示されるチャットUIを数行で実装  
3. **React hooks**：useChat useCompletion でUIとの統合が簡単  
4. **サーバー/クライアント両対応**：Server ActionsでもRoute Handlerでも使える

---

## インストールと基本設定

```
npm install ai @ai-sdk/anthropic @ai-sdk/openai
# または
npm install ai @ai-sdk/google  # Gemini
```

**環境変数：**

```
# .env.local
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
```

---

## 基本的なチャット実装

### バックエンド（Route Handler）

```
// app/api/chat/route.ts
import { anthropic } from '@ai-sdk/anthropic';
import { streamText } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = await streamText({
    model: anthropic('claude-sonnet-4-6'),
    messages,
    system: 'あなたは親切なアシスタントです。日本語で回答してください。',
  });

  return result.toDataStreamResponse();
}
```

### フロントエンド（React）

```
// app/page.tsx
'use client';

import { useChat } from 'ai/react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: '/api/chat',
  });

  return (
    <div>
      <div className="messages">
        {messages.map((m) => (
          <div key={m.id} className={`message ${m.role}`}>
            <span>{m.role === 'user' ? '😊' : '🤖'}</span>
            <p>{m.content}</p>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="メッセージを入力..."
        />
        <button type="submit">送信</button>
      </form>
    </div>
  );
}
```

これだけでストリーミングチャットアプリが完成する。

---

## モデルの切り替えが簡単

```
import { anthropic } from '@ai-sdk/anthropic';
import { openai } from '@ai-sdk/openai';
import { google } from '@ai-sdk/google';

// Claude に切り替え
const model = anthropic('claude-sonnet-4-6');

// GPT-5.5 に切り替え
const model = openai('gpt-4.5-turbo');

// Gemini に切り替え
const model = google('gemini-2.5-pro');

// あとは同じコードで動く
const result = await streamText({ model, messages });
```

ベンダーロックインがなく、コスト・精度を比較しながら切り替えられる。

---

## Vercel AI SDK 4.0 の新機能

### マルチモーダル入力

```
const result = await generateText({
  model: anthropic('claude-sonnet-4-6'),
  messages: [{
    role: 'user',
    content: [
      { type: 'text', text: 'この画像に何が写っていますか？' },
      {
        type: 'image',
        image: new URL('https://example.com/image.jpg'),
      },
    ],
  }],
});
```

### Tool Use（ツール呼び出し）

```
import { tool } from 'ai';
import { z } from 'zod';

const result = await generateText({
  model: anthropic('claude-sonnet-4-6'),
  tools: {
    getWeather: tool({
      description: '指定した都市の天気を取得する',
      parameters: z.object({
        city: z.string().describe('都市名'),
      }),
      execute: async ({ city }) => {
        // 天気APIを呼び出し
        return { city, temp: '25°C', condition: '晴れ' };
      },
    }),
  },
  messages: [{ role: 'user', content: '東京の天気は？' }],
});
```

ここまでが考え方。ここから先では、RAG実装の全コード、マルチエージェントパイプライン、ストリーミングUIコンポーネントのServer Actions対応パターンを公開する。

## 有料パート：Vercel AI SDK 4.0 の実践パターン集
