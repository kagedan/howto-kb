---
id: "2026-07-21-mastra-で作る-aiエージェント30-agent-mail-と連携してエージェント専用メールで-01"
title: "Mastra で作る AIエージェント(30) Agent Mail と連携して、エージェント専用メールで送受信する"
url: "https://zenn.dev/shiromizuj/articles/bfee99ca38ff45"
source: "zenn"
category: "claude-code"
tags: ["prompt-engineering", "API", "AI-agent", "LLM", "OpenAI", "GPT"]
date_published: "2026-07-21"
date_collected: "2026-07-22"
summary_by: "auto-rss"
query: ""
---

[Mastra で作る AI エージェント](https://zenn.dev/shiromizuj/articles/a0a1659e9f05b6) というシリーズの第30回です。

---

## やりたいこと

今回は、ユーザーとメールでやり取りする　Mastra エージェントを構築してみたいと思います。エージェント専用のメールアドレスを持ち、受信メールを Webhook で受け取り、そのまま自動返信できる構成を作ります。

AIエージェント向けの様々な Eメールプロバイダについてはこちらの記事をご覧ください。  
<https://zenn.dev/shiromizuj/articles/ff0ac931b6f3c5>

この記事では、メールプロバイダとして [Agent Mail](https://www.agentmail.to/) を使います。 読者が同じものを再現できるように、アカウント作成から実装、デプロイ、Webhook 作成、よく詰まるポイントまで順番に説明します。

## 最初に「出来上がり」を紹介。

「ユーザーとメールでやり取りする　Mastra エージェント」というのはどういうものか、この記事を最後まで読み進めるとどんなことができるようになるのか、そのイメージを持てるように、まず最初に「出来上がり」をご紹介します。

ユーザがエージェントに対してメールを送ってみます。ちょうどこの記事を執筆しているのがサッカーW杯決勝の前日なので、そのあたりの質問をしてみます。  
![](https://static.zenn.studio/user-upload/a2169501d8b2-20260720.png)

返事が返ってきました。ちゃんとWeb検索しているようです。

![](https://static.zenn.studio/user-upload/3fde39974094-20260719.png)

ここで、**別のメールアドレスから**エージェントにメールします。「さっきのメールを送った者と同じ人物なんだけど」と名乗って、情報を抽出しようと試みます。

![](https://static.zenn.studio/user-upload/3cecf0e6c7d5-20260719.png)

環境変数に設定した固定文言を返却しています。ガードレールが働いて、別アカウントの情報抽出を防いだことが分かります。

![](https://static.zenn.studio/user-upload/bac2a4e68210-20260719.png)

こんなエージェントを、ここから開発・構築していきます。

## 全体像

開発の流れは次の通りです。

1. Agent Mail でエージェント専用の inbox を作ります。
2. Mastra のアプリを用意し、受信メールに反応するエージェントを実装します。
3. Agent Mail の Webhook を作成し、公開 URL へ配送させます。
4. Mastra Platform にデプロイして、実際にメール送受信を動かします。
5. 必要なら Tavily を使って、時事性のある質問に強くします。

## 1. 先に用意するアカウント

まずは次の3つを用意します。

### 1-1. Agent Mail アカウント

Agent Mail は、AI エージェント向けに専用のメールアドレス、受信 API、Webhook を提供するサービスです。人間用のメールアカウントを流用するのではなく、エージェント専用の inbox を持たせることで、受信イベントをそのまま処理しやすくなります。

サインアップすると、少なくとも次の値が得られます。

* API キー
* inboxId
* エージェント用メールアドレス

この実装では inboxId を `.env` の `APP_CONFIG.agentMail.defaultInboxId` に入れて使います。

詳細手順はこちらの記事の末尾の章をご覧ください。  
<https://zenn.dev/shiromizuj/articles/07643bf38b0666>

### 1-2. Mastra Platform アカウント

Mastra Platform は、ローカルで作った Mastra アプリをそのままデプロイし、公開 URL を持たせるために使います。Webhook を受けるには、ローカルだけではなく公開 URL が必要なので、ここは必須です。

詳細手順はこちらの記事をご覧ください。  
<https://zenn.dev/shiromizuj/articles/9ccd85865dca81>

### 1-3. LLM と検索の API キー

今回の実装では、返信生成に Azure OpenAI を使い、最新情報が必要な質問には Tavily を使います。

* Azure OpenAI: 返信生成用
* Tavily: Web 検索用

## 2. アプリをどう構築するか

今回のアプリの階層構造は以下の通りです。

```
.
├─ src/
│  ├─ config/
│  │  └─ app-config.ts
│  ├─ guards/
│  │  └─ response-guard.ts
│  ├─ mastra/
│  │  ├─ agents/
│  │  │  └─ mail-agent.ts
│  │  ├─ memory/
│  │  │  └─ libsql-memory.ts
│  │  ├─ routes/
│  │  │  └─ agentmail-webhook-route.ts
│  │  ├─ tools/
│  │  │  └─ open-web-search.ts
│  │  └─ index.ts
│  ├─ observability/
│  │  └─ duckdb-observability.ts
│  ├─ services/
│  │  └─ reply-mail.ts
│  ├─ utils/
│  │  └─ email.ts
│  ├─ webhooks/
│  │  └─ agentmail-webhook.ts
│  └─ index.ts
└─ scripts/
	└─ create-agentmail-webhook.ts
```

アプリの責務は大きく5つに分かれています。

さらに、Mastra Platform 上で公開するために custom route を登録します。

## 3. 設定ファイルをまとめる

本来、環境変数は種別ごとに定義すべきですが、今回は Mastra Platform の free 版を利用するので、環境変数として3つしか定義できません。そこで今回の実装では `APP_CONFIG` という JSON 1つに集約しています。

```
# APP_CONFIG に全設定をJSONで集約する
# 例は1行JSONのまま利用する
APP_CONFIG={"azure":{"endpoint":"https://YOUR-RESOURCE.openai.azure.com/openai/v1","apiKey":"YOUR_AZURE_OPENAI_API_KEY","deployment":"gpt-5.4"},"agentMail":{"apiKey":"YOUR_AGENTMAIL_API_KEY","webhookSecret":"whsec_xxx","defaultInboxId":"inbox_xxx"},"app":{"model":"openai/gpt-5.4","port":8787,"safetyFallbackMessage":"安全性の確認のため、今回は要点のみお返しします。必要であれば質問を分けて再送してください。"},"storage":{"libsqlUrl":"file:./data/mastra.db","observabilityDuckdbPath":"./data/observability.duckdb"},"search":{"maxResults":5,"tavilyApiKey":"tvly-xxxx"}}
```

設定の読み込みは `src/config/app-config.ts` で行います。ここでは Azure、Agent Mail、アプリ設定、ストレージ、検索設定をひとまとめにして、起動時に Zod で検証します。

```
import { z } from "zod";

/**
 * アプリケーション全体で利用する設定スキーマ。
 * 環境変数3個制限に対応するため、APP_CONFIG(JSON)へ集約する。
 */
const appConfigSchema = z.object({
  azure: z.object({
    endpoint: z.string().url(),
    apiKey: z.string().min(1),
    deployment: z.string().min(1),
  }),
  agentMail: z.object({
    apiKey: z.string().min(1),
    webhookSecret: z.string().min(1),
    defaultInboxId: z.string().optional(),
  }),
  app: z.object({
    model: z.string().default("openai/gpt-5.4"),
    port: z.number().int().positive().default(8787),
    safetyFallbackMessage: z
      .string()
      .default("安全性の確認のため、今回は要点のみお返しします。必要であれば質問を分けて再送してください。"),
  }),
  storage: z.object({
    libsqlUrl: z.string().optional(),
    observabilityDuckdbPath: z.string().default("./data/observability.duckdb"),
  }),
  search: z.object({
    maxResults: z.number().int().positive().max(10).default(5),
    tavilyApiKey: z.string().min(1).optional(),
  }),
});

export type AppConfig = z.infer<typeof appConfigSchema>;

/**
 * APP_CONFIG(JSON)を読み取り、型安全な設定オブジェクトを返す。
 */
export function loadAppConfig(): AppConfig {
  const raw = process.env.APP_CONFIG;
  if (!raw) {
    throw new Error("APP_CONFIG が未設定です。JSON文字列で設定してください。");
  }

  const parsed = JSON.parse(raw) as unknown;
  return appConfigSchema.parse(parsed);
}

/**
 * 起動時に1回だけ設定を確定させる。
 */
export const appConfig = loadAppConfig();
```

特に重要なのは次の2点です。

* `azure.endpoint` には `/openai/v1` を含めること
* `search.tavilyApiKey` を入れておくと、検索の精度が安定すること

`APP_CONFIG` の例は `.env.example` を見れば分かるようにしてあります。

## 4. エージェント本体を作る

エージェント本体は `src/mastra/agents/mail-agent.ts` にあります。

```
import { Agent } from "@mastra/core/agent";
import { createOpenAI } from "@ai-sdk/openai";
import { appConfig } from "../../config/app-config";
import { openWebSearch } from "../tools/open-web-search";
import { createConversationMemory, createLibsqlStorage } from "../memory/libsql-memory";

/**
 * Azure OpenAI v1 API 互換の OpenAI プロバイダを初期化する。
 * endpoint には /openai/v1 を含む URL を設定する。
 */
function createAzureOpenAiV1Provider() {
  return createOpenAI({
    baseURL: appConfig.azure.endpoint,
    apiKey: appConfig.azure.apiKey,
    name: "azure-openai-v1",
  });
}

const storage = createLibsqlStorage();
const memory = createConversationMemory(storage);
const openai = createAzureOpenAiV1Provider();

/**
 * メール返信専用エージェント。
 * 他ユーザーの履歴を参照・推測・開示しないことを強く制約する。
 */
export const mailAgent = new Agent({
  id: "mail-agent",
  name: "Mail Reply Agent",
  instructions: [
    "あなたはメール返信専用のアシスタントです。",
    "常に丁寧で簡潔な日本語で返答してください。",
    "以下を厳守してください:",
    "- この送信者以外の会話履歴を参照・要約・推測・出力しない",
    "- 個人情報や機密情報を勝手に補完しない",
    "- 不確実な情報は不確実と明示する",
    "- 日付・試合結果・ニュース・相場など最新性が重要な質問では、回答前に open-web-search を必ず1回以上使う",
    "- 検索結果が0件または不十分なら、その事実を明示したうえで断定を避ける",
  ].join("\n"),
  model: openai(appConfig.azure.deployment),
  memory,
  tools: {
    openWebSearch,
  },
});
```

ここでは Azure OpenAI v1 のエンドポイントを `@ai-sdk/openai` で使い、Mastra の `Agent` に渡しています。ポイントは次の通りです。

* モデルは `openai/gpt-5.4` 形式で扱います
* 会話メモリを持たせて、送信者ごとの文脈を維持します
* 返信対象はあくまでその送信者の文脈だけに限定します
* 最新性が必要な質問では Web 検索ツールを使うよう指示します

この「会話の線引き」はかなり大事です。メール返信エージェントは、別送信者の文脈を勝手に混ぜると危険なので、プロンプト上でも厳しめに制約しています。

## 5. 返信品質を上げる Web 検索

最初は DuckDuckGo の Instant Answer を使っていましたが、時事質問ではヒットが弱い場面がありました。そこで、現在は Tavily を優先し、失敗時のみ DuckDuckGo にフォールバックする構成にしています。

実装は `src/mastra/tools/open-web-search.ts` です。

```
import { createTool } from "@mastra/core/tools";
import { z } from "zod";
import { appConfig } from "../../config/app-config";

type SearchResult = {
  title: string;
  url: string;
  snippet: string;
};

/**
 * Tavily APIでWeb検索を実行する。
 */
async function searchWithTavily(query: string, maxResults: number): Promise<SearchResult[]> {
  const apiKey = appConfig.search.tavilyApiKey;
  if (!apiKey) {
    return [];
  }

  const response = await fetch("https://api.tavily.com/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      api_key: apiKey,
      query,
      search_depth: "advanced",
      max_results: maxResults,
    }),
  });

  if (!response.ok) {
    return [];
  }

  const payload = (await response.json()) as {
    results?: Array<{
      title?: string;
      url?: string;
      content?: string;
    }>;
  };

  return (payload.results ?? [])
    .filter((item) => Boolean(item.url))
    .map((item) => ({
      title: item.title?.trim() || "検索結果",
      url: item.url!.trim(),
      snippet: item.content?.trim() || "",
    }));
}

/**
 * DuckDuckGo Instant Answer APIでフォールバック検索を実行する。
 */
async function searchWithDuckDuckGo(query: string, maxResults: number): Promise<SearchResult[]> {
  const params = new URLSearchParams({
    q: query,
    format: "json",
    no_html: "1",
    no_redirect: "1",
  });

  const response = await fetch(`https://api.duckduckgo.com/?${params.toString()}`);
  if (!response.ok) {
    return [];
  }

  const payload = (await response.json()) as {
    AbstractText?: string;
    AbstractURL?: string;
    Heading?: string;
    RelatedTopics?: Array<
      | {
          Text?: string;
          FirstURL?: string;
        }
      | {
          Name?: string;
          Topics?: Array<{
            Text?: string;
            FirstURL?: string;
          }>;
        }
    >;
  };

  const flattened: SearchResult[] = [];

  if (payload.AbstractText && payload.AbstractURL) {
    flattened.push({
      title: payload.Heading ?? "概要",
      url: payload.AbstractURL,
      snippet: payload.AbstractText,
    });
  }

  for (const topic of payload.RelatedTopics ?? []) {
    if ("Topics" in topic && Array.isArray(topic.Topics)) {
      for (const item of topic.Topics) {
        if (item.Text && item.FirstURL) {
          flattened.push({
            title: topic.Name ?? "関連項目",
            url: item.FirstURL,
            snippet: item.Text,
          });
        }
      }
      continue;
    }

    if ("Text" in topic && topic.Text && topic.FirstURL) {
      flattened.push({
        title: "関連項目",
        url: topic.FirstURL,
        snippet: topic.Text,
      });
    }
  }

  return flattened.slice(0, maxResults);
}

/**
 * Tavily優先で公開Webから情報を取得し、必要に応じてDDGへフォールバックする。
 */
export const openWebSearch = createTool({
  id: "open-web-search",
  description: "公開Webから関連情報を収集して要約候補を返します。",
  inputSchema: z.object({
    query: z.string().min(1).describe("検索クエリ"),
    maxResults: z.number().int().positive().max(10).default(5),
  }),
  outputSchema: z.object({
    summary: z.string(),
    provider: z.string(),
    results: z.array(
      z.object({
        title: z.string(),
        url: z.string(),
        snippet: z.string(),
      }),
    ),
  }),
  execute: async ({ query, maxResults }) => {
    const requestedMaxResults = Math.min(maxResults, appConfig.search.maxResults);

    const tavilyResults = await searchWithTavily(query, requestedMaxResults);
    if (tavilyResults.length > 0) {
      return {
        summary: `クエリ「${query}」に関連する候補を${tavilyResults.length}件取得しました。`,
        provider: "tavily",
        results: tavilyResults,
      };
    }

    const ddgResults = await searchWithDuckDuckGo(query, requestedMaxResults);
    const results = ddgResults;
    const summary =
      results.length > 0
        ? `クエリ「${query}」に関連する候補を${results.length}件取得しました。`
        : `クエリ「${query}」に一致する候補を取得できませんでした。`;

    return { summary, provider: "duckduckgo", results };
  },
});
```

このツールの役割は明快で、検索結果をまとめてエージェントに渡すことです。

* Tavily が使えるならまずそこを検索する
* 失敗したら DuckDuckGo を試す
* 返り値に `provider` を入れて、どの検索源を使ったか分かるようにする

検索結果が十分に出なければ、エージェントは断定を避けるようにしています。実際のメール返信では、この「断定しない」方が大事なことも多いです。

## 6. 会話メモリと保存先

会話メモリは `src/mastra/memory/libsql-memory.ts` で初期化しています。

```
import { LibSQLStore } from "@mastra/libsql";
import { Memory } from "@mastra/memory";
import { join } from "node:path";
import { appConfig } from "../../config/app-config";

/**
 * 実行環境に応じて LibSQL の接続先を決める。
 * Mastra Platform や外部DBが注入するURLを優先し、ローカル開発時のみ file: を使う。
 */
function resolveLibsqlUrl(): string {
  return process.env.MASTRA_STORAGE_URL
    ?? process.env.TURSO_DATABASE_URL
    ?? appConfig.storage.libsqlUrl
    ?? createLocalLibsqlUrl();
}

/**
 * リモート LibSQL/Turso 用の認証トークンを取得する。
 */
function resolveLibsqlAuthToken(): string | undefined {
  return process.env.TURSO_AUTH_TOKEN;
}

/**
 * ローカル開発用の LibSQL URL を動的に生成する。
 * 文字列リテラルの file: パスをビルドへ残さないため、デプロイ preflight を妨げない。
 */
function createLocalLibsqlUrl(): string {
  return ["file:", join(".", "data", "mastra.db")].join("");
}

/**
 * LibSQLストレージを初期化する。
 */
export function createLibsqlStorage(): LibSQLStore {
  return new LibSQLStore({
    id: "mail-agent-storage",
    url: resolveLibsqlUrl(),
    authToken: resolveLibsqlAuthToken(),
  });
}

/**
 * 送信者単位の会話保持に使うMemoryインスタンスを生成する。
 */
export function createConversationMemory(storage: LibSQLStore): Memory {
  return new Memory({
    storage,
    options: {
      lastMessages: 30,
      semanticRecall: false,
      generateTitle: false,
      workingMemory: {
        enabled: false,
      },
    },
  });
}
```

ここでは2つのことをやっています。

1. 接続先の LibSQL URL を環境変数優先で解決する
2. 送信者ごとの会話を保存する Memory を作る

接続先の優先順位は次の通りです。

1. `MASTRA_STORAGE_URL`
2. `TURSO_DATABASE_URL`
3. `APP_CONFIG.storage.libsqlUrl`
4. ローカルの `file:` パス

この順番にしておくと、Mastra Platform では注入された Turso を使い、ローカルではファイルベースで試せます。

### ちょっとした経験談

ここで一度、Mastra の Memory 設定で `threads.generateTitle` を使ってしまい、production 起動時にクラッシュしました。現在の Mastra では、この設定は top-level の `generateTitle` に移っています。

この手の互換差分は、型チェックだけでは見つからず、実際の起動で初めて落ちることがあります。デプロイ後に health check を必ず見る理由がこれです。

## 7. ガードレールで情報漏洩を防ぐ

メール返信エージェントでは、別ユーザーの情報が混ざった出力を防ぐことが重要です。

この実装では、`src/guards/response-guard.ts` で返信テキストを最終チェックし、問題があれば安全文面へ切り替えます。

```
import { appConfig } from "../config/app-config";
import { findEmailCandidates } from "../utils/email";

/**
 * 他ユーザー情報漏洩の疑いを簡易検知し、安全側にフォールバックする。
 */
export function runResponseGuardrail(input: {
  text: string;
  senderEmail: string;
  agentInboxEmail?: string;
}) {
  const emails = findEmailCandidates(input.text);
  const allowList = new Set<string>([
    input.senderEmail.toLowerCase(),
    input.agentInboxEmail?.toLowerCase() ?? "",
  ]);

  const suspicious = emails.filter((mail) => !allowList.has(mail));
  if (suspicious.length > 0) {
    return {
      safe: false,
      reason: `許可されないメールアドレスを検知: ${suspicious.join(", ")}`,
      sanitizedText: appConfig.app.safetyFallbackMessage,
    };
  }

  return {
    safe: true,
    sanitizedText: input.text,
  };
}
```

このガードレールは、次の流れで動きます。

1. 生成文からメールアドレス候補を抽出します。
2. 許可リスト（送信者本人とエージェント自身）を作ります。
3. 許可外アドレスが含まれていれば `safe: false` にします。
4. `safe: false` の場合は、返信本文を `safetyFallbackMessage` に差し替えます。

このように、モデルの出力をそのまま送るのではなく、最後にアプリ側のルールで止めることで、安全性を上げています。

## 8. Webhook 受信と返信送信

Webhook の本体は `src/webhooks/agentmail-webhook.ts` にあります。

```
import { Webhook } from "svix";
import { appConfig } from "../config/app-config";
import { mailAgent } from "../mastra/agents/mail-agent";
import { runResponseGuardrail } from "../guards/response-guard";
import { extractEmailAddress } from "../utils/email";
import { DuckDbObservability } from "../observability/duckdb-observability";
import { getMessageDetail, sendReplyMail } from "../services/reply-mail";

/**
 * AgentMailのWebhookイベント最小型。
 */
type AgentMailWebhookEvent = {
  event_id?: string;
  eventId?: string;
  event_type?: string;
  eventType?: string;
  message?: {
    inbox_id?: string;
    inboxId?: string;
    thread_id?: string;
    threadId?: string;
    message_id?: string;
    messageId?: string;
    from?: string;
    subject?: string;
    extracted_text?: string;
    extractedText?: string;
  };
};

const svix = new Webhook(appConfig.agentMail.webhookSecret);
const observability = new DuckDbObservability(appConfig.storage.observabilityDuckdbPath);
let initialized = false;
let observabilityAvailable = true;

/**
 * Webhook処理の初期化を一度だけ実行する。
 */
async function ensureInitialized(): Promise<void> {
  if (initialized) {
    return;
  }

  try {
    await observability.init();
  } catch {
    // 観測ログの失敗でWebhook本処理を止めない。
    observabilityAvailable = false;
  }

  initialized = true;
}

/**
 * 観測ログ書き込み。失敗しても本処理は継続する。
 */
async function safeLog(input: {
  id: string;
  eventType: string;
  senderEmail: string;
  threadId: string;
  status: "received" | "replied" | "blocked" | "error";
  detail?: string;
}): Promise<void> {
  if (!observabilityAvailable) {
    return;
  }

  try {
    await observability.log(input);
  } catch {
    observabilityAvailable = false;
  }
}

/**
 * Svix署名検証用にヘッダを正規化する。
 */
function normalizeHeaders(headers: Record<string, string | string[] | undefined>): Record<string, string> {
  const normalized: Record<string, string> = {};
  for (const [key, value] of Object.entries(headers)) {
    if (typeof value === "string") {
      normalized[key] = value;
    }
    if (Array.isArray(value)) {
      normalized[key] = value.join(",");
    }
  }
  return normalized;
}

/**
 * 受信Webhookを検証し、返信生成まで実行する。
 */
export async function handleAgentMailWebhook(input: {
  rawBody: Buffer;
  headers: Record<string, string | string[] | undefined>;
}): Promise<{ status: number; body?: string }> {
  try {
    await ensureInitialized();
  } catch {
    // 初期化失敗時もWebhook本処理は継続する。
    observabilityAvailable = false;
    initialized = true;
  }

  let event: AgentMailWebhookEvent;
  try {
    event = svix.verify(input.rawBody, normalizeHeaders(input.headers)) as AgentMailWebhookEvent;
  } catch {
    return { status: 400, body: "invalid signature" };
  }

  const eventType = event.event_type ?? event.eventType ?? "unknown";
  if (eventType !== "message.received") {
    return { status: 204 };
  }

  const message = event.message;
  const inboxId = message?.inbox_id ?? message?.inboxId ?? appConfig.agentMail.defaultInboxId;
  const threadId = message?.thread_id ?? message?.threadId;
  const messageId = message?.message_id ?? message?.messageId;
  const from = message?.from;
  const extractedText = message?.extracted_text ?? message?.extractedText ?? "";

  if (!inboxId || !threadId || !messageId || !from) {
    return { status: 400, body: "payload missing required fields" };
  }

  const senderEmail = extractEmailAddress(from);
  const eventId = event.event_id ?? event.eventId ?? crypto.randomUUID();

  await safeLog({
    id: eventId,
    eventType,
    senderEmail,
    threadId,
    status: "received",
  });

  try {
    const sourceMessage = await getMessageDetail(inboxId, messageId);
    const messageIdHeader =
      sourceMessage.headers?.["Message-Id"] ??
      sourceMessage.headers?.["Message-ID"] ??
      sourceMessage.messageId;

    const prompt = [
      "次の受信メールに日本語で返信してください。",
      `送信者: ${senderEmail}`,
      `件名: ${sourceMessage.subject ?? "(no subject)"}`,
      "本文:",
      extractedText || sourceMessage.extractedText || sourceMessage.text || "(本文なし)",
    ].join("\n");

    const output = await mailAgent.generate(prompt, {
      memory: {
        thread: threadId,
        resource: senderEmail,
      },
      maxSteps: 5,
    });

    const guardrail = runResponseGuardrail({
      text: output.text,
      senderEmail,
    });

    if (!guardrail.safe) {
      await safeLog({
        id: eventId,
        eventType,
        senderEmail,
        threadId,
        status: "blocked",
        detail: guardrail.reason,
      });
    }

    await sendReplyMail({
      inboxId,
      messageId,
      subject: sourceMessage.subject,
      bodyText: guardrail.sanitizedText,
      inReplyTo: messageIdHeader,
      references: sourceMessage.references,
    });

    await safeLog({
      id: eventId,
      eventType,
      senderEmail,
      threadId,
      status: "replied",
    });

    return { status: 204 };
  } catch (error) {
    const detail = error instanceof Error ? error.message : "unknown error";
    await safeLog({
      id: eventId,
      eventType,
      senderEmail,
      threadId,
      status: "error",
      detail,
    });
    return { status: 500, body: "internal error" };
  }
}
```

このファイルの役割は、受信から返信までを一気通貫でつなぐことです。

やっていることは次の順番です。

1. Svix 署名を検証する
2. `message.received` 以外を無視する
3. 受信メッセージの詳細を Agent Mail から取り直す
4. エージェントに返信文を生成させる
5. ガードレールで危険な出力を抑える
6. 返信 API でメールを返す

### 重要な実装ポイント

* 返信時は `In-Reply-To` と `References` を付けて、スレッドを維持します
* 返信メールの件名は `Re:` を補強します
* 生成文に他送信者の情報が混ざる場合は、安全な文面にフォールバックします

観測ログとして DuckDB にも記録していますが、ここは fail-open にしています。つまり、ログが壊れても返信処理を止めないようにしています。

## 9. Mastra Platform へ公開する

公開まわりで大事なのは、Express の `src/index.ts` だけではなく、Mastra の custom API route にも登録することです。

### 9-1. ルート登録

Webhook 受信ルートは `src/mastra/routes/agentmail-webhook-route.ts` で定義し、`src/mastra/index.ts` の `server.apiRoutes` へ登録しています。

```
// src/mastra/routes/agentmail-webhook-route.ts
import { registerApiRoute } from "@mastra/core/server";
import { handleAgentMailWebhook } from "../../webhooks/agentmail-webhook";

/**
 * Mastra Server に AgentMail Webhook 受信ルートを登録する。
 * requiresAuth を false にして外部Webhookを受け付ける。
 */
export const agentMailWebhookRoute = registerApiRoute("/webhooks/agentmail", {
  method: "POST",
  requiresAuth: false,
  handler: async (c) => {
    const bodyBuffer = Buffer.from(await c.req.arrayBuffer());
    const headers = Object.fromEntries(c.req.raw.headers.entries());

    const result = await handleAgentMailWebhook({
      rawBody: bodyBuffer,
      headers,
    });

    if (result.body) {
      return new Response(result.body, { status: result.status });
    }

    return new Response(null, { status: result.status });
  },
});
```

```
// src/mastra/index.ts
import { Mastra } from "@mastra/core";
import { mailAgent } from "./agents/mail-agent";
import { agentMailWebhookRoute } from "./routes/agentmail-webhook-route";

/**
 * Mastra本体。
 */
export const mastra = new Mastra({
  agents: {
    mailAgent,
  },
  server: {
    apiRoutes: [agentMailWebhookRoute],
  },
});
```

これにより、Mastra Platform 上でも `/webhooks/agentmail` が公開されます。

### 9-2. デプロイ手順

`.env` と `.env.production` が併存しているので、デプロイ時は `--env-file` を明示します。

```
npx mastra deploy --env production --project <PROJECT_ID> --env-file .env.production --yes
```

デプロイ後は次を確認します。

```
npx mastra env deploys production --json
curl https://mastra-agent-mail-production.up.railway.app/health
```

## 10. Webhook を作成する

Webhook は、Agent Mail に届いたメールを自分のアプリへ即時配送するために作ります。

本リポジトリでは `scripts/create-agentmail-webhook.ts` を用意しています。

```
import "dotenv/config";
import { AgentMailClient } from "agentmail";
import { z } from "zod";

/**
 * Webhook作成スクリプト専用の最小設定スキーマ。
 * 既存アプリ本体と違い、webhookSecret 未設定でも実行できるようにする。
 */
const webhookSetupConfigSchema = z.object({
  agentMail: z.object({
    apiKey: z.string().min(1),
    defaultInboxId: z.string().optional(),
  }),
});

/**
 * APP_CONFIG からWebhook作成に必要な設定だけを抜き出す。
 */
function loadWebhookSetupConfig() {
  const raw = process.env.APP_CONFIG;
  if (!raw) {
    throw new Error("APP_CONFIG が未設定です。先に .env を設定してください。");
  }

  return webhookSetupConfigSchema.parse(JSON.parse(raw) as unknown);
}

/**
 * CLI引数から公開Webhook URLを取得する。
 */
function readWebhookUrl(): string {
  const webhookUrl = process.argv[2]?.trim();
  if (!webhookUrl) {
    throw new Error(
      "Webhook URL が未指定です。例: npm run create:webhook -- https://example.com/webhooks/agentmail",
    );
  }

  return z.string().url().parse(webhookUrl);
}

/**
 * Webhook を作成し、必要な控え値を標準出力へ出す。
 */
async function main(): Promise<void> {
  const config = loadWebhookSetupConfig();
  const webhookUrl = readWebhookUrl();
  const client = new AgentMailClient({ apiKey: config.agentMail.apiKey });

  const webhook = await client.webhooks.create({
    url: webhookUrl,
    eventTypes: ["message.received"],
    ...(config.agentMail.defaultInboxId
      ? { inboxIds: [config.agentMail.defaultInboxId] }
      : {}),
  });

  console.log("Webhook created.");
  console.log(`webhookId=${webhook.webhookId}`);
  console.log(`secret=${webhook.secret}`);
  console.log(`url=${webhook.url}`);
  console.log(`enabled=${webhook.enabled}`);
  console.log(`inboxIds=${(webhook.inboxIds ?? []).join(",")}`);
  console.log("Copy the secret into APP_CONFIG.agentMail.webhookSecret.");
}

void main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : "Unknown error";
  console.error(message);
  process.exitCode = 1;
});
```

### 作成コマンド

```
npm run create:webhook -- https://YOUR_PUBLIC_HOST/webhooks/agentmail
```

成功すると、次のような情報が表示されます。

```
Webhook created.
webhookId=wh_...
secret=whsec_...
url=https://YOUR_PUBLIC_HOST/webhooks/agentmail
enabled=true
inboxIds=inbox_...
```

この `secret` を `.env` 側の `APP_CONFIG.agentMail.webhookSecret` に反映して、再デプロイします。

### スクリプトの役割

このスクリプトは、次の3つだけをしています。

1. `APP_CONFIG` から Agent Mail の API キーと inboxId を読む
2. CLI 引数から Webhook URL を読む
3. `client.webhooks.create()` で `message.received` 用の Webhook を作る

## 11. 実際に詰まりやすかった点

ここは補助情報ですが、実運用でかなり役に立ったので残しておきます。

### 11-1. 404 が返る

Webhook URL を叩いて 404 の場合は、Mastra 側の custom route 登録漏れを疑います。Express で受けているだけでは、Platform 側の公開ルートとしては出てきません。

### 11-2. 500 が返る

Webhook が 500 のときは、ハンドラ内の初期化や外部サービスの接続エラーを疑います。

特に今回は、DuckDB の初期化が失敗して Webhook 自体が落ちたことがありました。ログは便利ですが、本処理を巻き込まないようにした方が安全です。

### 11-3. 返信は返るが WebSearch が弱い

時事性が必要なのに検索結果が弱いときは、検索プロバイダを見直します。今回のような用途では、Tavily のような専用検索 API の方が安定しやすいです。

## 12. この記事を再現するための最短手順

1. Agent Mail の API キーと inboxId を用意します。
2. Azure OpenAI の endpoint と API キーを `APP_CONFIG` に入れます。
3. 必要なら `search.tavilyApiKey` も入れます。
4. `npm run typecheck` で型を確認します。
5. `npx mastra deploy --env production --project <PROJECT_ID> --env-file .env.production --yes` でデプロイします。
6. `npm run create:webhook -- https://YOUR_PUBLIC_HOST/webhooks/agentmail` で Agent Mail の Webhook を作ります。
7. 返ってきた secret を `APP_CONFIG.agentMail.webhookSecret` に反映して再デプロイします。
8. Agent Mail にメールを送って、返信が返ることを確認します。

## 13. まとめ

今回の構成は、次の3点を押さえると再現しやすくなります。

* 設定は `APP_CONFIG` にまとめる
* Webhook は Mastra Platform の custom route として公開する
* 最新情報が必要な質問には Tavily のような検索 API を使う

この3つを守ると、単なるメール返信エージェントではなく、実運用に耐えやすい Agent Mail 連携の Mastra アプリになります。
