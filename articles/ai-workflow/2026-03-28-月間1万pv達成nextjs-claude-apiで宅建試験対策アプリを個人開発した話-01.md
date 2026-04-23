---
id: "2026-03-28-月間1万pv達成nextjs-claude-apiで宅建試験対策アプリを個人開発した話-01"
title: "月間1万PV達成：Next.js + Claude APIで宅建試験対策アプリを個人開発した話"
url: "https://qiita.com/takkenai/items/2218577e522cb8355eef"
source: "qiita"
category: "ai-workflow"
tags: ["API", "TypeScript", "qiita"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

# 月間1万PV達成：Next.js + Claude APIで宅建試験対策アプリを個人開発した話

副業として個人開発を続けて3年。今年ついに月間1万PVを超えるアプリをリリースできました。それが宅建（宅地建物取引士）試験対策アプリ **[takkenai.jp](https://takkenai.jp)** です。

## なぜ宅建アプリを作ったのか

自分も宅建を受験して、既存アプリの**解説の薄さ**に不満を感じていました。○×だけ表示して終わり、解説があっても条文を貼るだけ。「なぜそうなるのか」が全然わからない。

2024年にClaude APIを使い始め、「これで宅建解説を自動生成したら面白いのでは」と思いつき、開発をスタートしました。

## 技術スタック

```
Next.js 14（App Router）+ TypeScript
Tailwind CSS v3
Prisma + Vercel Postgres
Claude API（anthropic SDK）
Vercel（デプロイ）
```

## AI解説の実装：「結論→根拠→覚え方」

解説の品質がアプリの核心です。試行錯誤の末、このシステムプロンプトに落ち着きました。

```
const SYSTEM_PROMPT = `
あなたは宅建試験の専門講師です。以下の3段階フォーマットで解説してください。

【結論】1〜2文で正誤と要点を明示
【根拠】法令条文・判例・原則と「なぜそうなるのか」の理由
【覚え方】試験本番で使えるキーワードや類似問題との違い
`.trim();
```

ストリーミングで解説を表示することで、待ち時間なく読み始められます。

```
// app/api/explain/route.ts
export async function POST(req: NextRequest) {
  const { questionId } = await req.json();
  
  const stream = await anthropic.messages.stream({
    model: 'claude-3-5-sonnet-20241022',
    max_tokens: 800,
    system: SYSTEM_PROMPT,
    messages: [{ role: 'user', content: buildPrompt(question) }],
  });

  return new Response(
    new ReadableStream({
      async start(controller) {
        for await (const chunk of stream) {
          if (chunk.type === 'content_block_delta') {
            controller.enqueue(new TextEncoder().encode(chunk.delta.text));
          }
        }
        controller.close();
      },
    })
  );
}
```

## 通勤モードの実装

「電車の中でサクサク解ける」をコンセプトにした通勤モード。スワイプで次の問題へ、オフライン対応でNetworkなしでも動きます。

```
// IndexedDBで問題をキャッシュ
export async function cacheQuestionsForOffline(questions: Question[]) {
  const db = await openDB('takkenai-cache', 1, {
    upgrade(db) { db.createObjectStore('questions', { keyPath: 'id' }); },
  });
  const tx = db.transaction('questions', 'readwrite');
  await Promise.all([...questions.map(q => tx.store.put(q)), tx.done]);
}
```

## リリースから月間1万PV達成まで

| 時期 | 施策 | 月間PV |
| --- | --- | --- |
| 2024年10月 | ベータリリース | ~200 |
| 2024年11月 | Qiita記事投稿 | ~800 |
| 2024年12月 | X（Twitter）で拡散 | ~2,500 |
| 2025年5月 | **月間1万PV達成** | 10,200 |

**効いた施策：**

1. Qiitaへの技術記事投稿（開発時のつまずきを記事化）
2. 試験カレンダーに合わせたコンテンツ更新
3. カテゴリ別・年度別のSSGページ生成でロングテールSEO

## おわりに

「自分が本当に欲しかったものを作る」という動機の強さと、Next.js + Claude APIという技術スタックが、少ない工数でも高品質なプロダクトを可能にしてくれました。

宅建試験を受験予定の方は **[takkenai.jp](https://takkenai.jp)** をぜひ試してみてください。1250問以上の過去問、AI解説付き、基本無料です。
