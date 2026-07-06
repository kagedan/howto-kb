---
id: "2026-07-06-vercel-ai-sdkで試合ログからaiフィードバックをストリーミング生成する-01"
title: "Vercel AI SDKで試合ログからAIフィードバックをストリーミング生成する"
url: "https://zenn.dev/nadarakainc/articles/37711a3e0150f6"
source: "zenn"
category: "claude-code"
tags: ["prompt-engineering", "API", "LLM", "TypeScript", "construction", "zenn"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

## はじめに

サッカーチームの試合ログ（スタメン、交代、出場時間）は、そのままだと数字とテキストの羅列で、指導者が読んでもすぐには振り返りに使いにくいものです。

この記事では、Vercel AI SDKとClaudeを使い、試合ログを「良かった点・改善したい点・次へのアドバイス」という指導者向けのフィードバック文に変換する機能を実装します。以下の流れで進めます。

* 試合ログを、AIが読みやすいテキストに変換する
* 試合形式に応じたシステムプロンプトを設計する
* `streamText`でフィードバックをストリーミング生成する
* 生成結果をDBに保存し、クライアント側で逐次表示する

この機能はAPIキーをユーザー自身に登録してもらうBYOK（Bring Your Own Key）方式にしています。また、無料プランには月間の生成回数制限を設けています。この記事では、その設計もあわせて解説します。

## 前提

この記事では、以下の構成を想定します。

```
src/
├─ app/
│ └─ api/
│   └─ ai/
│     └─ feedback/
│       └─ route.ts
├─ actions/
│ └─ feedback.ts
├─ lib/
│ ├─ ai-prompts.ts
│ ├─ match-log.ts
│ └─ plan.ts
└─ components/
  └─ match-feedback-block.tsx
```

Next.js App Router、TypeScript、Drizzle ORMを前提にします。認証はBetter Authを使っていますが、セッション取得部分は他の認証ライブラリに置き換えても考え方は同じです。

## パッケージをインストールする

Vercel AI SDK本体と、Anthropicプロバイダーをインストールします。

```
npm install ai @ai-sdk/anthropic
```

## APIキーをBYOK方式で管理する

この機能では、Anthropicの利用料金をサービス側で肩代わりするのではなく、ユーザー自身のAPIキーを使う設計にしています。設定画面で登録してもらったキーを、DBの`user`テーブルに保存します。

```
// actions/api-key.ts
"use server";

export async function updateAnthropicApiKey(apiKey: string) {
  const session = await auth.api.getSession({ headers: await headers() });
  if (!session) return { error: "認証エラーです" };

  if (!apiKey.startsWith("sk-ant-")) {
    return { error: "Anthropic API キーは sk-ant- で始まる必要があります" };
  }

  await db
    .update(user)
    .set({ anthropicApiKey: apiKey })
    .where(eq(user.id, session.user.id));

  return { success: true };
}
```

`sk-ant-`で始まるかどうかだけの簡易チェックですが、明らかに違う値の混入は防げます。

なお、このキーは現状DBにそのまま平文で保存しています。個人開発の範囲では割り切っていますが、複数人が使うサービスとして本番運用する場合は、暗号化してから保存するか、シークレット管理サービス側に持たせる設計にすべきです。この記事では実装を単純化するために平文保存にしている、という点は正直に書いておきます。

## 試合ログをAI向けのテキストに変換する

DBから取得した試合データ（スタメン、交代イベント、出場時間）は構造化されたオブジェクトなので、そのままプロンプトに渡すと情報が読み取りにくくなります。まず、人間が読む記事のような自然な日本語テキストに変換します。

```
// lib/match-log.ts
export function buildMatchLogText(input: MatchLogInput): string {
  const { match, players, events, starters } = input;
  const lines: string[] = [];

  lines.push("【試合概要】");
  lines.push(`対戦相手: ${match.opponent ?? "（未設定）"}`);
  lines.push(`形式: ${formatLabel}`);
  lines.push("");

  lines.push("【スターティングメンバー】");
  // ... スタメン一覧を追加

  lines.push("【試合イベント】（試合経過時間）");
  // ... 交代などのイベントを時系列で追加

  lines.push("【出場時間集計】");
  // ... 出場時間の長い順に追加

  return lines.join("\n");
}
```

ポイントは、生データをそのまま渡すのではなく「見出し＋箇条書き」の形にテキスト整形してからLLMに渡すことです。モデル側の解釈のブレを減らせますし、人間がデバッグ時にログをそのまま読んでも内容を把握できます。

## システムプロンプトを設計する

出力フォーマットが安定しないと、毎回違う構成のフィードバックが返ってきて実運用に耐えません。見出し・文字数・トーンをシステムプロンプト側で明示的に指定します。

```
// lib/ai-prompts.ts
const FORMAT_LABELS: Record<string, string> = {
  "5v5": "フットサル（5人制）",
  "8v8": "少年サッカー（8人制）",
  "11v11": "サッカー（11人制）",
};

export function getSystemPrompt(format?: string | null): string {
  const formatLabel = FORMAT_LABELS[format ?? ""] ?? "サッカー";

  return `あなたは${formatLabel}の経験豊富なコーチです。
試合ログ（スタメン、交代、出場時間）を読み、指導者向けの簡潔なフィードバックを書いてください。

【出力のルール】
- 日本語で、250字以上500字程度にまとめる
- 以下の3つのセクションを含めること：
  1. ## 良かった点（チームまたは個人のポジティブな所見）
  2. ## 改善したい点（次の試合や練習に活かせる具体的なポイント）
  3. ## 次へのアドバイス（一言で締めくくる）
- 表現は温かく、建設的に
- スタメン・交代・出場時間などのログが少ない場合は、得られる情報の範囲で書くこと`;
}
```

最後の「ログが少ない場合は、得られる情報の範囲で書くこと」という一文は、実際に運用してみて追加したものです。試合開始直後などログがほとんどない状態で生成すると、情報がないのに断定的な内容を書いてしまうことがあったため、フォールバックの指示を明示しています。

## ストリーミングで生成するRoute Handlerを作る

フィードバック生成はレスポンスが長く数秒かかるため、`streamText`でストリーミング配信します。

```
// app/api/ai/feedback/route.ts
import { streamText } from "ai";
import { createAnthropic } from "@ai-sdk/anthropic";

export async function POST(req: Request) {
  const session = await auth.api.getSession({ headers: await headers() });
  if (!session) {
    return new Response("Unauthorized", { status: 401 });
  }

  const { matchId } = await req.json();
  if (!matchId || typeof matchId !== "string") {
    return new Response("matchId が必要です", { status: 400 });
  }

  // 先に利用制限をチェックする（モデル呼び出しの前に判定する）
  const isPro = await getIsPro(session.user.id);
  if (!isPro) {
    const remainingCount = await getRemainingFeedbackCount(session.user.id);
    if ((remainingCount ?? 0) <= 0) {
      return new Response(
        "無料プランの今月のAIフィードバック上限に達しました。",
        { status: 402 },
      );
    }
  }

  const userData = await db.query.user.findFirst({
    where: eq(userTable.id, session.user.id),
    columns: { anthropicApiKey: true },
  });

  if (!userData?.anthropicApiKey) {
    return new Response("Anthropic API キーが設定されていません。", {
      status: 400,
    });
  }

  // 権限チェック込みで試合データを取得する
  const data = await getMatchData(matchId);
  if (!data) {
    return new Response("試合が見つかりません", { status: 404 });
  }

  const matchLogText = buildMatchLogText(data);
  const anthropic = createAnthropic({ apiKey: userData.anthropicApiKey });

  const result = streamText({
    model: anthropic("claude-sonnet-4-6"),
    system: getSystemPrompt(data.match.format),
    prompt: getFeedbackUserPrompt(matchLogText),
    maxOutputTokens: 1024,
    onFinish: async ({ text }) => {
      // ストリーム完了後にDBへ保存（1試合1件、上書き）
      await upsertMatchFeedback(matchId, text);

      if (!isPro) {
        await db.insert(aiFeedbackUsage).values({
          id: randomUUID(),
          userId: session.user.id,
          matchId,
        });
      }
    },
  });

  return result.toTextStreamResponse();
}
```

ここで意識している点が2つあります。

1つ目は、利用制限のチェックをモデル呼び出しより前に行うことです。ユーザーはBYOKで自分のAPIキーを使っているとはいえ、無料プランの回数制限を超えているのに先にモデルを呼んでしまうと、無駄なAPI呼び出しと待ち時間が発生します。認証→プラン確認→APIキー確認→試合データ取得→生成、という順序を守ります。

2つ目は、`getMatchData(matchId)`の中で「このユーザーがこの試合にアクセスできるか」の権限チェックを行っていることです。`matchId`はクライアントから送られてくる値なので、そのまま信用せず、必ずサーバー側で所有者確認を行ってから処理を進めます。

## クライアント側でストリームを受け取る

Vercel AI SDKには`useChat`や`useCompletion`のようなReact hooksも用意されていますが、この機能では「ストリーム完了後にDB保存の完了を待ってから編集モードに切り替える」「無料プランの残り回数をUIに出す」といった独自の状態管理をしたかったため、`fetch`を直接叩いて`ReadableStream`を手動で読み取る方式にしています。

```
const res = await fetch("/api/ai/feedback", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ matchId }),
});

if (!res.ok) {
  const text = await res.text();
  throw new Error(text || "生成に失敗しました");
}

const reader = res.body?.getReader();
if (!reader) throw new Error("ストリームを取得できませんでした");

const decoder = new TextDecoder();
let fullText = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  fullText += decoder.decode(value, { stream: true });
  setStreamContent(fullText); // 逐次UIに反映
}

setSavedContent(fullText);
```

`reader.read()`をループで呼び、届いたチャンクを`TextDecoder`でデコードしながら`state`に反映していくだけのシンプルな実装です。カーソルの点滅アニメーションを添えるだけでも、体感の待ち時間はかなり短く感じられます。

## 生成後に編集して保存できるようにする

AIの生成結果は、そのまま公開・共有する前提ではなく「たたき台」として扱えるようにしています。生成後は通常のテキスト編集に切り替えられるようにし、保存はServer Actionで行います。

```
// actions/feedback.ts
"use server";

export async function updateFeedback(matchId: string, content: string) {
  const session = await auth.api.getSession({ headers: await headers() });
  if (!session) return { success: false, error: "ログインしてください" };

  const data = await getMatchData(matchId);
  if (!data) return { success: false, error: "試合が見つかりません" };

  await upsertMatchFeedback(matchId, content);

  return { success: true };
}
```

生成用のRoute Handlerと保存用のServer Actionの両方で、同じ「1試合1件、上書き保存」のロジックを使っています。AIが生成した内容も、手動で編集した内容も、扱いとしては同じ`matchFeedback`レコードです。

## よくあるミス

**`toDataStreamResponse()`と`toTextStreamResponse()`を混同する**

Vercel AI SDKの`streamText`には、レスポンスをストリームに変換する方法が複数あります。`useChat`など標準のhooksを使う前提なら`toDataStreamResponse()`が便利ですが、これは独自のデータストリーム形式（メタデータ付き）で返るため、この記事のようにクライアント側で`ReadableStream`を手動でテキストとして読み取る実装と組み合わせると、余計な制御文字が混じって表示が崩れます。クライアント側の受け取り方に合わせて、`toTextStreamResponse()`のようなプレーンテキスト形式を選びます。

**利用制限のチェックを生成の後に行ってしまう**

「生成してから、DB保存時にまとめて制限チェックする」実装にすると、上限を超えたユーザーのリクエストでも実際にはモデルへの呼び出しが発生してしまいます。BYOKであってもAPI利用料はユーザー負担なので実害は小さいですが、無駄なレイテンシと失敗時のUX悪化につながるため、モデル呼び出し前にチェックする順序にしています。

**`matchId`をそのまま信用してDBを操作する**

クライアントから受け取った`matchId`を使ってDBを直接更新するのではなく、必ず「そのユーザーがそのリソースにアクセスできるか」を確認する関数を経由させます。生成用のRoute Handlerと編集保存用のServer Actionの両方で、同じ権限チェック関数を呼ぶようにすると、チェック漏れを防ぎやすくなります。

## まとめ

Vercel AI SDKでストリーミング生成する機能を実装する場合、基本の流れは以下です。

* 構造化データはプロンプトに渡す前に、読みやすいテキストへ変換する
* システムプロンプトで出力フォーマット（見出し・文字数・トーン）を固定する
* 認証・利用制限・権限チェックは、モデル呼び出しより前に済ませる
* クライアントの受け取り方（hooksか手動fetchか）に応じて、`toDataStreamResponse()`と`toTextStreamResponse()`を使い分ける
* 生成結果はAIまかせにせず、人が編集して保存できる導線を用意する

LLMを機能に組み込むときは「モデルにどう喋らせるか」だけでなく、「どのデータをどう整形して渡すか」「生成前にどんなチェックを済ませておくか」の設計が、体験の安定性を大きく左右します。
