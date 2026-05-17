---
id: "2026-05-16-line-messaging-api-を-typescript-で実装して-claude-に自動返信-01"
title: "LINE Messaging API を TypeScript で実装して Claude に自動返信させる"
url: "https://qiita.com/LemonCake/items/af3e77c6445a19788faf"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "TypeScript", "qiita"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

:::note
この記事で紹介する LINE Messaging API は、MCP サーバー **pay-per-call-mcp** から Claude 経由でも利用できます。
- **npm**: https://www.npmjs.com/package/pay-per-call-mcp
- **Glama**: https://glama.ai/mcp/servers/@evid-ai/pay-per-call-mcp
:::

## はじめに

LINE は日本国内で月間 9,500 万人以上が利用するメッセージングプラットフォームです。LINE Messaging API を使えば、顧客サポート・社内通知・予約確認といったビジネスユースケースを自動化できます。

本記事では以下を実装します。

- LINE Developers でのチャンネル設定と Channel Access Token 取得
- Express + TypeScript での Webhook サーバー
- 受信メッセージの型定義（署名検証付き）
- テキスト / 画像 / スタンプのハンドリング
- Claude API との連携（受信内容を Claude に渡して返信を生成）
- Reply Message と Push Message の使い分け
- リッチメニューの設定
- ngrok でのローカル開発
- エラーハンドリング（署名検証失敗、レート制限）

---

## LINE Messaging API の基本

| 項目 | 内容 |
|---|---|
| ベース URL | `https://api.line.me/v2/bot` |
| 認証方式 | Channel Access Token (Bearer) |
| API リファレンス | https://developers.line.biz/ja/reference/messaging-api/ |
| レート制限 | Push: 500 req/秒、Reply: 制限なし（replyToken は 1 回限り） |
| Webhook 署名 | `X-Line-Signature` ヘッダー（HMAC-SHA256） |

---

## セットアップ

### 1. LINE Developers でチャンネル作成

1. https://developers.line.biz/console/ にアクセス
2. 「Messaging API」チャンネルを作成
3. 「Channel secret」と「Channel access token (long-lived)」を取得
4. Webhook URL を設定（後で ngrok の URL を貼る）

### 2. 依存パッケージのインストール

```bash
npm init -y
npm install express @line/bot-sdk typescript ts-node @types/express dotenv
npm install @anthropic-ai/sdk
npx tsc --init
```

### 3. 環境変数

```bash
# .env
LINE_CHANNEL_SECRET=your_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
ANTHROPIC_API_KEY=your_anthropic_api_key
PORT=3000
```

---

## 型定義

LINE Messaging API のレスポンスに TypeScript の型を付けておくと実装が安全になります。

```typescript
// src/types/line.ts

export type LineMessageType = "text" | "image" | "sticker" | "video" | "audio" | "location" | "file";

export interface LineTextMessage {
  type: "text";
  id: string;
  text: string;
}

export interface LineImageMessage {
  type: "image";
  id: string;
  contentProvider: {
    type: "line" | "external";
    originalContentUrl?: string;
    previewImageUrl?: string;
  };
}

export interface LineStickerMessage {
  type: "sticker";
  id: string;
  packageId: string;
  stickerId: string;
  stickerResourceType: "STATIC" | "ANIMATION" | "SOUND" | "ANIMATION_SOUND" | "POPUP" | "POPUP_SOUND" | "NAME_TEXT" | "PER_STICKER_TEXT";
}

export type LineMessage = LineTextMessage | LineImageMessage | LineStickerMessage;

export interface LineSource {
  type: "user" | "group" | "room";
  userId?: string;
  groupId?: string;
  roomId?: string;
}

export interface LineMessageEvent {
  type: "message";
  message: LineMessage;
  webhookEventId: string;
  deliveryContext: { isRedelivery: boolean };
  timestamp: number;
  source: LineSource;
  replyToken: string;
  mode: "active" | "standby";
}

export interface LineFollowEvent {
  type: "follow";
  webhookEventId: string;
  deliveryContext: { isRedelivery: boolean };
  timestamp: number;
  source: LineSource;
  replyToken: string;
  mode: "active" | "standby";
}

export interface LineUnfollowEvent {
  type: "unfollow";
  webhookEventId: string;
  deliveryContext: { isRedelivery: boolean };
  timestamp: number;
  source: LineSource;
  mode: "active" | "standby";
}

export type LineWebhookEvent = LineMessageEvent | LineFollowEvent | LineUnfollowEvent;

export interface LineWebhookBody {
  destination: string;
  events: LineWebhookEvent[];
}

// Reply API のペイロード
export interface LineReplyRequest {
  replyToken: string;
  messages: LineReplyMessage[];
  notificationDisabled?: boolean;
}

export interface LineTextReplyMessage {
  type: "text";
  text: string;
  quickReply?: LineQuickReply;
}

export interface LineStickerReplyMessage {
  type: "sticker";
  packageId: string;
  stickerId: string;
}

export type LineReplyMessage = LineTextReplyMessage | LineStickerReplyMessage;

export interface LineQuickReply {
  items: LineQuickReplyItem[];
}

export interface LineQuickReplyItem {
  type: "action";
  action: LineQuickReplyAction;
}

export interface LineQuickReplyAction {
  type: "message" | "postback" | "uri";
  label: string;
  text?: string;
  data?: string;
  uri?: string;
}
```

---

## LINE クライアントの実装

```typescript
// src/line-client.ts
import * as crypto from "crypto";
import type {
  LineReplyRequest,
  LineReplyMessage,
  LineWebhookBody,
} from "./types/line.js";

export class LineClient {
  private readonly baseUrl = "https://api.line.me/v2/bot";
  private readonly token: string;
  private readonly secret: string;

  constructor(token: string, secret: string) {
    this.token = token;
    this.secret = secret;
  }

  // 署名検証（Webhook の真正性を確認）
  verifySignature(body: string, signature: string): boolean {
    const hmac = crypto.createHmac("sha256", this.secret);
    hmac.update(body);
    const expected = hmac.digest("base64");
    return crypto.timingSafeEqual(
      Buffer.from(expected),
      Buffer.from(signature)
    );
  }

  // Reply Message（replyToken は 1 回限り・30 秒以内に使う）
  async reply(replyToken: string, messages: LineReplyMessage[]): Promise<void> {
    const payload: LineReplyRequest = { replyToken, messages };
    const res = await fetch(`${this.baseUrl}/message/reply`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new LineApiError(res.status, JSON.stringify(err));
    }
  }

  // Push Message（任意のタイミングでユーザーに送信）
  async push(to: string, messages: LineReplyMessage[]): Promise<void> {
    const res = await fetch(`${this.baseUrl}/message/push`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify({ to, messages }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new LineApiError(res.status, JSON.stringify(err));
    }
  }

  // Broadcast（全フォロワーに送信）
  async broadcast(messages: LineReplyMessage[]): Promise<void> {
    const res = await fetch(`${this.baseUrl}/message/broadcast`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify({ messages }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new LineApiError(res.status, JSON.stringify(err));
    }
  }

  // 画像コンテンツ取得（LINE ホスト画像）
  async getMessageContent(messageId: string): Promise<ArrayBuffer> {
    const res = await fetch(
      `https://api-data.line.me/v2/bot/message/${messageId}/content`,
      {
        headers: { Authorization: `Bearer ${this.token}` },
      }
    );

    if (!res.ok) {
      throw new LineApiError(res.status, "Failed to fetch message content");
    }
    return res.arrayBuffer();
  }
}

export class LineApiError extends Error {
  constructor(
    public readonly statusCode: number,
    message: string
  ) {
    super(`LINE API Error ${statusCode}: ${message}`);
    this.name = "LineApiError";
  }
}
```

---

## Claude との連携

```typescript
// src/claude-client.ts
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// ユーザーメッセージをシステムプロンプト付きで Claude に渡す
export async function generateReply(
  userMessage: string,
  systemPrompt?: string
): Promise<string> {
  const system =
    systemPrompt ??
    "あなたは丁寧で親切なカスタマーサポート担当者です。簡潔に、200文字以内で回答してください。";

  const message = await client.messages.create({
    model: "claude-sonnet-4-6",
    max_tokens: 300,
    system,
    messages: [{ role: "user", content: userMessage }],
  });

  const block = message.content[0];
  if (block.type !== "text") {
    return "申し訳ありません。回答を生成できませんでした。";
  }
  return block.text;
}
```

---

## Webhook サーバー（メインロジック）

```typescript
// src/index.ts
import express, { Request, Response } from "express";
import "dotenv/config";
import { LineClient } from "./line-client.js";
import { generateReply } from "./claude-client.js";
import type {
  LineWebhookBody,
  LineMessageEvent,
  LineFollowEvent,
} from "./types/line.js";

const app = express();

// 署名検証のために生の body が必要
app.use(express.json({ verify: (req: any, _res, buf) => { req.rawBody = buf; } }));

const line = new LineClient(
  process.env.LINE_CHANNEL_ACCESS_TOKEN!,
  process.env.LINE_CHANNEL_SECRET!
);

// Webhook エンドポイント
app.post("/webhook", async (req: Request & { rawBody?: Buffer }, res: Response) => {
  // 1. 署名検証
  const signature = req.headers["x-line-signature"] as string;
  if (!signature || !req.rawBody) {
    res.status(400).json({ error: "Missing signature" });
    return;
  }

  if (!line.verifySignature(req.rawBody.toString(), signature)) {
    console.warn("Invalid signature — possible spoofed request");
    res.status(401).json({ error: "Invalid signature" });
    return;
  }

  // 2. 200 を先に返す（LINE は 1 秒以内のレスポンスを要求）
  res.status(200).json({ status: "ok" });

  // 3. イベント処理（非同期）
  const body = req.body as LineWebhookBody;
  await Promise.allSettled(body.events.map(handleEvent));
});

async function handleEvent(event: LineWebhookBody["events"][number]): Promise<void> {
  switch (event.type) {
    case "message":
      await handleMessageEvent(event as LineMessageEvent);
      break;
    case "follow":
      await handleFollowEvent(event as LineFollowEvent);
      break;
    case "unfollow":
      console.log(`User unfollowed: ${event.source.userId}`);
      break;
    default:
      console.log(`Unhandled event type: ${(event as any).type}`);
  }
}

async function handleMessageEvent(event: LineMessageEvent): Promise<void> {
  const { message, replyToken } = event;

  switch (message.type) {
    case "text": {
      console.log(`Text from ${event.source.userId}: ${message.text}`);

      try {
        const reply = await generateReply(message.text);
        await line.reply(replyToken, [{ type: "text", text: reply }]);
      } catch (err) {
        console.error("Failed to generate/send reply:", err);
        // replyToken が使えない場合は Push にフォールバック
        if (event.source.userId) {
          await line.push(event.source.userId, [
            { type: "text", text: "現在サービスが混み合っています。しばらくしてからお試しください。" },
          ]).catch(console.error);
        }
      }
      break;
    }

    case "image": {
      console.log(`Image from ${event.source.userId}: id=${message.id}`);
      await line.reply(replyToken, [
        { type: "text", text: "画像を受け取りました。テキストでお問い合わせいただくとより的確にご対応できます。" },
      ]);
      break;
    }

    case "sticker": {
      // スタンプには定番の返し方
      await line.reply(replyToken, [
        { type: "sticker", packageId: "446", stickerId: "1988" },
      ]);
      break;
    }

    default:
      console.log(`Unsupported message type: ${(message as any).type}`);
  }
}

async function handleFollowEvent(event: LineFollowEvent): Promise<void> {
  if (!event.replyToken) return;
  await line.reply(event.replyToken, [
    {
      type: "text",
      text: "友だち追加ありがとうございます！\n何かご不明な点があればお気軽にメッセージをどうぞ。",
      quickReply: {
        items: [
          {
            type: "action",
            action: { type: "message", label: "サービス案内", text: "サービスについて教えて" },
          },
          {
            type: "action",
            action: { type: "message", label: "料金確認", text: "料金を確認したい" },
          },
          {
            type: "action",
            action: { type: "message", label: "お問い合わせ", text: "担当者に問い合わせたい" },
          },
        ],
      },
    },
  ]);
}

const port = Number(process.env.PORT ?? 3000);
app.listen(port, () => console.log(`LINE Webhook listening on :${port}`));
```

---

## Push Message の一括送信（通知配信）

Reply Message はユーザーの発話に対する応答にしか使えません。システムからプロアクティブに通知を送る場合は Push Message を使います。

```typescript
// src/notifier.ts — Push Message を使ったバッチ通知の例
import "dotenv/config";
import { LineClient } from "./line-client.js";

const line = new LineClient(
  process.env.LINE_CHANNEL_ACCESS_TOKEN!,
  process.env.LINE_CHANNEL_SECRET!
);

interface OrderStatus {
  userId: string;
  orderId: string;
  status: "shipped" | "delivered" | "cancelled";
}

// 注文ステータス変更を顧客に通知
async function notifyOrderStatus(orders: OrderStatus[]): Promise<void> {
  const statusLabel: Record<OrderStatus["status"], string> = {
    shipped: "発送しました",
    delivered: "お届けしました",
    cancelled: "キャンセルされました",
  };

  // 1 秒に 500 件以内という制限を考慮して並行数を制御
  const CONCURRENCY = 50;
  for (let i = 0; i < orders.length; i += CONCURRENCY) {
    const batch = orders.slice(i, i + CONCURRENCY);
    await Promise.allSettled(
      batch.map(async (order) => {
        const label = statusLabel[order.status];
        await line.push(order.userId, [
          {
            type: "text",
            text: `ご注文 #${order.orderId} が${label}。\nご利用ありがとうございました。`,
          },
        ]);
      })
    );
    // バースト防止
    await new Promise((r) => setTimeout(r, 20));
  }
}

// 実行例
await notifyOrderStatus([
  { userId: "Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", orderId: "12345", status: "shipped" },
]);
```

---

## リッチメニューの設定

リッチメニューはチャット画面下部に表示される常設メニューです。ユーザーの操作を誘導するのに効果的です。

```typescript
// src/rich-menu.ts
import "dotenv/config";

const BASE_URL = "https://api.line.me/v2/bot";
const HEADERS = {
  "Content-Type": "application/json",
  Authorization: `Bearer ${process.env.LINE_CHANNEL_ACCESS_TOKEN}`,
};

async function createRichMenu(): Promise<string> {
  const res = await fetch(`${BASE_URL}/richmenu`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({
      size: { width: 2500, height: 843 },
      selected: true,
      name: "メインメニュー",
      chatBarText: "メニューを開く",
      areas: [
        {
          bounds: { x: 0, y: 0, width: 833, height: 843 },
          action: { type: "message", label: "サービス案内", text: "サービスを教えて" },
        },
        {
          bounds: { x: 833, y: 0, width: 834, height: 843 },
          action: { type: "message", label: "料金", text: "料金を確認したい" },
        },
        {
          bounds: { x: 1667, y: 0, width: 833, height: 843 },
          action: { type: "uri", label: "公式サイト", uri: "https://example.com" },
        },
      ],
    }),
  });

  if (!res.ok) throw new Error(`Failed to create rich menu: ${res.status}`);
  const { richMenuId } = await res.json();
  return richMenuId as string;
}

// リッチメニュー画像をアップロード（PNG 必須）
async function uploadRichMenuImage(richMenuId: string, imagePath: string): Promise<void> {
  const { readFile } = await import("fs/promises");
  const image = await readFile(imagePath);

  const res = await fetch(`https://api-data.line.me/v2/bot/richmenu/${richMenuId}/content`, {
    method: "POST",
    headers: {
      "Content-Type": "image/png",
      Authorization: `Bearer ${process.env.LINE_CHANNEL_ACCESS_TOKEN}`,
    },
    body: image,
  });

  if (!res.ok) throw new Error(`Failed to upload image: ${res.status}`);
}

// デフォルトリッチメニューとして設定
async function setDefaultRichMenu(richMenuId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/user/all/richmenu/${richMenuId}`, {
    method: "POST",
    headers: HEADERS,
  });
  if (!res.ok) throw new Error(`Failed to set default rich menu: ${res.status}`);
}

// まとめて実行
const richMenuId = await createRichMenu();
await uploadRichMenuImage(richMenuId, "./assets/rich-menu.png");
await setDefaultRichMenu(richMenuId);
console.log(`Rich menu set: ${richMenuId}`);
```

---

## ngrok でローカル開発

LINE の Webhook は HTTPS エンドポイントが必要です。ローカル開発では ngrok を使います。

```bash
# ngrok インストール（Homebrew）
brew install ngrok

# トンネル起動
ngrok http 3000

# 出力例:
# Forwarding  https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:3000
```

取得した URL に `/webhook` を加えて LINE Developers の Webhook URL に設定します。

```typescript
// ts-node で起動
npx ts-node --esm src/index.ts
```

---

## エラーハンドリングのまとめ

```typescript
// src/error-handler.ts
import { LineApiError } from "./line-client.js";

export async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3
): Promise<T> {
  let lastError: unknown;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;

      if (err instanceof LineApiError) {
        if (err.statusCode === 429) {
          // レート制限: 指数バックオフ
          const delay = Math.pow(2, attempt) * 500;
          console.warn(`Rate limited. Retrying in ${delay}ms (attempt ${attempt}/${maxRetries})`);
          await new Promise((r) => setTimeout(r, delay));
          continue;
        }

        if (err.statusCode === 400) {
          // replyToken 期限切れや不正 — リトライ不要
          console.error("Bad request (replyToken expired?):", err.message);
          throw err;
        }

        if (err.statusCode === 401) {
          // Channel Access Token が無効
          console.error("Unauthorized — check LINE_CHANNEL_ACCESS_TOKEN");
          throw err;
        }

        if (err.statusCode >= 500) {
          // LINE サーバー側エラー — リトライ
          console.warn(`Server error ${err.statusCode}. Retrying...`);
          await new Promise((r) => setTimeout(r, 1000 * attempt));
          continue;
        }
      }

      throw err;
    }
  }

  throw lastError;
}
```

### レート制限の考慮点

| メッセージ種別 | 制限 |
|---|---|
| Reply Message | 事実上なし（replyToken は 30 秒・1 回限り） |
| Push Message | 500 req/秒 |
| Broadcast | 1 req/秒 |
| Narrowcast | 1 req/秒 |

Push/Broadcast を大量に送る場合は上記に注意し、`withRetry` を活用してください。

---

## おわりに

本記事では LINE Messaging API と Claude を TypeScript で組み合わせ、以下を実装しました。

- HMAC-SHA256 による Webhook 署名検証
- テキスト・画像・スタンプのイベントハンドリング
- Claude による自動返信生成
- Push Message による能動的通知
- リッチメニューの設定
- レート制限対応の指数バックオフリトライ

このような **API 呼び出しを Claude が自律的に行う仕組み** は、MCP サーバー [pay-per-call-mcp](https://www.npmjs.com/package/pay-per-call-mcp) でさらに発展させられます。

- **npm**: https://www.npmjs.com/package/pay-per-call-mcp
- **Glama**: https://glama.ai/mcp/servers/@evid-ai/pay-per-call-mcp
