---
id: "2026-04-13-github検索アプリにclaude-aiを組み込んで分かった使いどころの設計判断-01"
title: "🔍GitHub検索アプリにClaude AIを組み込んで分かった、使いどころの設計判断"
url: "https://zenn.dev/yumazd/articles/4324440fc3c7ec"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

## はじめに

とある用事でGitHub リポジトリを検索・閲覧できる Web アプリを Next.js 16（App Router）で作りました。その中で Claude AI を3箇所に組み込んだのですが、**「どこに・いつ・どう入れるか」の設計判断**が一番難しく、学びも多かったので共有します。

<https://github.com/yumazd/search-github>

![](https://static.zenn.studio/user-upload/f3868823517c-20260413.jpg)

### 技術スタック

| カテゴリ | 技術 |
| --- | --- |
| フレームワーク | Next.js 16 (App Router) / React 19 / TypeScript |
| スタイリング | Tailwind CSS 4 / shadcn/ui |
| AI | Anthropic Claude Haiku 4.5（`@anthropic-ai/sdk`） |
| 外部API | GitHub REST API v2022-11-28 |
| テスト | Vitest + React Testing Library / Playwright |

### アプリの構成

3画面のシンプルな構成です。

1. **ホーム** — キーワード入力 + フィルタ（スター数・更新日）
2. **検索結果一覧** — 無限スクロールで最大1,000件表示
3. **リポジトリ詳細** — AI要約・README（翻訳機能付き）・コミットグラフ・言語比率

## AI を組み込んだ3つのポイント

全部に AI を突っ込むのではなく、**コスト・レイテンシ・UX のバランス**で「自動 / 遅延 / オンデマンド」を使い分けました。

| 機能 | タイミング | max\_tokens | なぜここに入れたか |
| --- | --- | --- | --- |
| 検索クエリの日英翻訳 | 検索実行時（サーバー） | 100 | GitHub API は英語の方がヒット精度が高い |
| 一覧のAI要約 | ページ描画後（クライアント非同期） | 2,000 | 英語 description を日本語1行に。初期描画をブロックしない |
| READMEの日本語翻訳 | ボタンクリック時 | 4,000 | 長文＝トークンコスト大。ユーザーが必要な時だけ |

### なぜ Claude Haiku 4.5 か

今回の用途は「翻訳」と「要約」が中心です。高度な推論は不要で、レスポンス速度とコストが重要でした。Haiku 4.5 はこの用途に十分な品質で、レイテンシも小さく、コストも抑えられます。

## AI組み込みで工夫したこと

### 1. バッチ処理 + 100ms デバウンス（一覧AI要約）

検索結果のカード10枚がそれぞれ AI 要約をリクエストすると、10回の API コールが走ります。いわゆる N+1 問題です。

これを**クライアント側のキューで収集 → 100ms debounce → 1回のバッチ API コール**に集約しました。

```
// ai-description.tsx — バッチキューの仕組み

let batchQueue: {
  full_name: string;
  description: string | null;
  topics: string[];
  resolve: (summary: string) => void;
}[] = [];
let batchTimer: ReturnType<typeof setTimeout> | null = null;

function requestSummary(
  fullName: string,
  description: string | null,
  topics: string[],
): Promise<string> {
  // キャッシュヒットならすぐ返す
  const cache = getCache();
  if (cache[fullName]) return Promise.resolve(cache[fullName]);

  return new Promise((resolve) => {
    batchQueue.push({ full_name: fullName, description, topics, resolve });

    if (!batchTimer) {
      batchTimer = setTimeout(async () => {
        const queue = [...batchQueue];
        batchQueue = [];
        batchTimer = null;

        const cached = getCache();
        const uncached = queue.filter((q) => !cached[q.full_name]);

        let summaries: Record<string, string> = {};
        if (uncached.length > 0) {
          try {
            summaries = await Promise.race([
              summarizeDescriptionsAction(
                uncached.map((q) => ({
                  full_name: q.full_name,
                  description: q.description,
                  topics: q.topics,
                })),
              ),
              // 10秒タイムアウト
              new Promise<Record<string, string>>((_, reject) =>
                setTimeout(() => reject(new Error("timeout")), 10000),
              ),
            ]);
            setCache(summaries);
          } catch {
            // タイムアウトやAPIエラー → スケルトンを非表示にする
          }
        }

        const all = { ...cached, ...summaries };
        queue.forEach((q) => q.resolve(all[q.full_name] || ""));
      }, 100); // ← 100ms debounce
    }
  });
}
```

ポイントをまとめると：

* **100ms デバウンス**で複数カードのリクエストを1回に集約
* **sessionStorage キャッシュ**でセッション中の再表示は API を叩かない
* **10秒タイムアウト**で AI が遅い場合も UI がハングしない
* **`Promise.race`** でタイムアウトと API コールを競合させるシンプルな実装

AI 側では1回のプロンプトで複数リポジトリの要約を JSON で返してもらいます。

```
// server/ai.ts — バッチ要約のプロンプト

const response = await getClient().messages.create({
  model: "claude-haiku-4-5-20251001",
  max_tokens: 2000,
  messages: [
    {
      role: "user",
      content: `以下のGitHubリポジトリの説明を、それぞれ日本語で1〜2行に要約してください。
各リポジトリごとに以下のJSON形式で返してください（他のテキストは不要）:
{"リポジトリのfull_name": "日本語の要約", ...}

${repoList}`,
    },
  ],
});
```

### 2. 日本語検出による条件付き翻訳

英語で検索しているのに翻訳 API を呼ぶのは無駄です。正規表現で日本語を含む場合のみ翻訳します。

```
// server/search.ts

export function containsJapanese(text: string): boolean {
  return /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]/.test(text);
}

export async function executeSearch(filters: SearchFilters, page: number = 1) {
  // 日本語を含む場合のみ翻訳
  const needsTranslation = aiEnabled && containsJapanese(filters.q);
  const translatedQ = needsTranslation
    ? await translateSearchQuery(filters.q)
    : filters.q;

  const query = buildSearchQuery(filters, translatedQ);
  const result = await searchRepositories({ ...query, page, per_page: RESULTS_PER_PAGE });

  return {
    total_count: result.total_count,
    items: result.items,
    translatedQ: needsTranslation ? translatedQ : undefined,
  };
}
```

翻訳プロンプトも工夫しています。「意味を膨らませない」「入力と同じ語数で返す」と指示することで、余計な類義語の追加を防いでいます。

```
content: `以下の検索クエリを英語に翻訳してください。
入力の語数と同じ語数で返してください（1語なら1語、2語なら2語）。
意味を膨らませたり類義語を追加しないでください。
キーワードのみを返してください。

クエリ: ${query}`,
```

### 3. AI\_ENABLED フラグで完全フォールバック

環境変数1つで AI 機能をまるごと OFF にできます。

```
const aiEnabled = process.env.AI_ENABLED === "true";
```

これにより：

* **AI の障害時**もアプリは 100% 動作する
* **開発時**は AI を OFF にしてレートリミットを気にせずテスト可能
* **AI はあくまで付加価値レイヤー**という設計思想を強制できる

すべての AI 関数は try-catch で囲み、失敗時は元のテキストをそのまま返します。

```
// translateSearchQuery — 失敗したら元のクエリをそのまま使う
} catch {
  return query;
}

// summarizeDescriptions — 失敗したら空オブジェクト
} catch {
  return {};
}
```

### 4. Zod バリデーションで入力を制限

Server Actions はクライアントから直接呼ばれるため、入力を必ずバリデーションします。

```
// server/actions.ts

// README翻訳：最大50KB
const readmeSchema = z.string().max(50000);

// バッチ要約：最大30リポジトリ、各フィールドにも上限
const repoSummarySchema = z
  .array(
    z.object({
      full_name: z.string().max(200),
      description: z.string().max(1000).nullable(),
      topics: z.array(z.string().max(100)).max(30),
    }),
  )
  .max(30);

// リポジトリ識別子：正規表現でインジェクション防止
const repoIdentifierSchema = z.object({
  owner: z.string().regex(/^[a-zA-Z0-9_.-]+$/).max(39),
  repo: z.string().regex(/^[a-zA-Z0-9_.-]+$/).max(100),
});
```

巨大な README を投げつけてトークンを浪費させたり、バッチサイズを爆発させるような攻撃を防ぎます。

## API読み込みの件数設計

### 段階的なデータ取得

| フェーズ | 件数 | 方式 |
| --- | --- | --- |
| 初期表示 | **10件** | Server Component で SSR |
| 追加読み込み | **10件ずつ** | Intersection Observer で無限スクロール |
| 上限 | **1,000件** | GitHub API の検索上限に合わせてストップ |

初期表示を10件に抑えた理由は2つあります。

1. **SSR のレスポンス速度を確保する** — 30件だと GitHub API + AI バッチ処理の合計レイテンシが大きくなる
2. **AI バッチ要約のトークン量を抑える** — 10件分の description なら1回の API コールで十分収まる

### キャッシュ戦略の使い分け

エンドポイントごとにデータの鮮度と更新頻度を考慮して `revalidate` を設定しています。

```
// server/github.ts

// 検索結果：60秒キャッシュ（鮮度重要だがレートリミット対策）
const res = await fetch(url.toString(), {
  headers: headers(),
  next: { revalidate: 60 },
});

// リポジトリ詳細：1時間キャッシュ（メタデータは頻繁に変わらない）
const res = await fetch(`${GITHUB_API_BASE}/repos/${owner}/${repo}`, {
  headers: headers(),
  next: { revalidate: 3600 },
});

// コミット統計：キャッシュなし（GitHub側が非同期計算するため）
const res = await fetch(
  `${GITHUB_API_BASE}/repos/${owner}/${repo}/stats/commit_activity`,
  { headers: headers(), cache: "no-store" },
);
```

### GitHub API の 202 問題とリトライ

GitHub のコミット統計 API は、初回アクセス時に `202 Accepted` を返して「いま計算中です」と言ってきます。これに対応するため、**サーバーとクライアントの2段構えのリトライ**を実装しました。

```
// server/github.ts — サーバー側リトライ（最大2回、1.5秒間隔）

export async function getCommitActivity(owner: string, repo: string): Promise<number[]> {
  for (let i = 0; i < 2; i++) {
    const res = await fetch(/* ... */, { cache: "no-store" });
    if (res.status === 202) {
      await new Promise((r) => setTimeout(r, 1500));
      continue;
    }
    if (!res.ok) return [];
    const data = await res.json();
    return data.map((week: { total: number }) => week.total);
  }
  return [];
}
```

```
// commit-chart-client.tsx — クライアント側リトライ（最大3回、1.7秒間隔）

useEffect(() => {
  if (initialData !== null || !owner || !repo) return;
  let cancelled = false;

  async function retryFetch() {
    for (let i = 0; i < 3; i++) {
      const result = await fetchCommitActivityAction(owner!, repo!);
      if (cancelled) return;
      if (result.length > 0) {
        setData(result);
        return;
      }
      await new Promise((r) => setTimeout(r, 1700));
    }
    if (!cancelled) setError(true);
  }

  retryFetch();
  return () => { cancelled = true; };
}, [initialData, owner, repo]);
```

サーバーで取得できなかった場合のみクライアントが引き継ぐので、多くのケースではサーバー側で解決します。

## スケルトンローディングの設計

一覧の概要表示 AI と README 翻訳 AI はクライアント側で動くため、初期表示をブロックしません。その代わり、**AI が裏で何かを読み込んでいることをユーザーにわかりやすく伝える**必要があります。何も表示しないと「壊れている？」と思われるし、雑なスピナーだと画面がガタつく。そこで場面ごとに最適なスケルトンを用意しました。

### 3種類のスケルトンを使い分ける

場面ごとに最適なスケルトンを用意しました。

#### 1. 初期ロード用（6枚のカード）

ページ遷移直後に表示される `loading.tsx` です。Next.js の規約ファイルなので、`<Suspense>` を手書きする必要がありません。

```
// app/result/loading.tsx

function SkeletonCard() {
  return (
    <div className="rounded-xl border border-white/30 bg-white/5 p-5
                    backdrop-blur-3xl animate-pulse">
      <div className="flex items-center gap-2.5">
        <div className="h-7 w-7 rounded-full bg-white/10" />   {/* アバター */}
        <div className="h-4 w-48 rounded bg-white/10" />        {/* リポジトリ名 */}
      </div>
      <div className="mt-3 space-y-2">
        <div className="h-3 w-full rounded bg-white/10" />      {/* 説明1行目 */}
        <div className="h-3 w-3/4 rounded bg-white/10" />       {/* 説明2行目 */}
      </div>
      <div className="mt-3 flex gap-3">
        <div className="h-3 w-16 rounded bg-white/10" />        {/* スター */}
        <div className="h-3 w-12 rounded bg-white/10" />        {/* 言語 */}
        <div className="h-3 w-12 rounded bg-white/10" />        {/* 更新日 */}
      </div>
    </div>
  );
}

export default function ResultLoading() {
  return (
    /* ...レイアウト省略... */
    {Array.from({ length: 6 }).map((_, i) => (
      <SkeletonCard key={i} />
    ))}
  );
}
```

ポイントは**実際のカードと同じ構造・サイズにすること**です。`h-7 w-7 rounded-full` はアバター画像と同じサイズ、`w-48` はリポジトリ名の平均的な幅に合わせています。これにより、実データに切り替わった時のレイアウトシフト（CLS）を最小化できます。

#### 2. 無限スクロール用（3枚 + スピナー）

追加読み込み中はスピナーとスケルトン3枚を表示します。初期ロードより少ない枚数にして「追加で読んでますよ」という印象を与えます。

```
// load-more.tsx

{hasMore && (
  <div ref={ref}>  {/* ← Intersection Observer の監視対象 */}
    {loading && (
      <div role="status" aria-label="結果を読み込み中">
        <div className="flex justify-center py-4">
          <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
        </div>
        {Array.from({ length: 3 }).map((_, i) => (
          <SkeletonCard key={`more-${i}`} />
        ))}
      </div>
    )}
  </div>
)}
```

#### 3. 詳細ページ用（Suspense 境界ごとに独立）

![](https://static.zenn.studio/user-upload/76f72c4ca621-20260413.jpg)

![](https://static.zenn.studio/user-upload/0a613c960a7e-20260413.jpg)

詳細ページでは AI 要約・コミットグラフ・README をそれぞれ **独立した Suspense 境界**で包んでいます。

```
// app/repositories/[owner]/[repo]/page.tsx

{/* AI要約 — 準備できたら差し込まれる */}
<Suspense fallback={<SummarySkeleton />}>
  <AiSummary fullName={repoData.full_name}
             description={repoData.description}
             topics={repoData.topics || []} />
</Suspense>

{/* コミットグラフ — GitHub API の 202 があるので遅い可能性 */}
<Suspense fallback={<CommitChartSkeleton />}>
  <CommitChart owner={owner} repo={repo} />
</Suspense>

{/* README — サイズが大きいと取得に時間がかかる */}
<Suspense fallback={<ReadmeSkeleton />}>
  <ReadmeViewer owner={owner} repo={repo} />
</Suspense>
```

これにより **準備できたコンポーネントから順次表示**されます。例えば README の取得に時間がかかっても、AI 要約やコミットグラフは先に表示されます。Next.js の Streaming SSR との相性が良く、ユーザーの体感待ち時間を大幅に短縮できます。

### AI 要約のインラインスケルトン

![](https://static.zenn.studio/user-upload/410af49c752e-20260413.jpg)

![](https://static.zenn.studio/user-upload/bfc381ff3076-20260413.jpg)

一覧ページの AI 要約は `useLayoutEffect` でキャッシュを先読みし、キャッシュがある場合はスケルトンを一切表示しません。

```
// ai-description.tsx

// paint前にキャッシュを読んでフラッシュを防ぐ
useLayoutEffect(() => {
  const cache = getCache();
  if (cache[fullName]) {
    setSummary(cache[fullName]);
  }
}, [fullName]);

// キャッシュがない場合のスケルトン
if (summary === null) {
  return (
    <div className="flex items-center gap-1.5 animate-pulse">
      <Languages className="h-3 w-3 text-violet-400" />
      <div className="h-3 w-3/4 rounded bg-white/10" />
    </div>
  );
}
```

`useEffect` ではなく `useLayoutEffect` を使う理由は、**描画前にキャッシュを確認して、不要なスケルトンの一瞬のチラつきを防ぐ**ためです。

## その他の設計判断

### Server / Client Component の境界

Next.js App Router では「どこで分割するか」が重要です。このアプリでは以下のように分けました。

* **Server Component**：初回データ取得（検索結果、リポジトリ詳細、README）
* **Client Component**：ユーザーインタラクション（無限スクロール、フィルタ変更、README翻訳）

初回レンダリングは Server Component で完結させ、JavaScript バンドルに AI SDK のコードが含まれないようにしています。

### URL ベースの状態管理

フィルタの状態を `searchParams` に持たせています。

* ブラウザの戻る/進むでフィルタが復元される
* URL をコピーするだけでフィルタ付きの検索結果を共有できる
* 状態管理ライブラリ（Redux / Zustand）が不要

### ドメイン層の分離

GitHub API のクエリ組み立てロジックを `domain/query-builder.ts` に切り出し、純粋関数として実装しました。

```
// domain/query-builder.ts

export function buildSearchQuery(filters: SearchFilters, translatedQ?: string) {
  const parts: string[] = [];
  const query = translatedQ || filters.q;
  if (query) parts.push(query);

  if (filters.stars !== "any") parts.push(`stars:>=${filters.stars}`);
  if (filters.pushed !== "any" && PUSHED_MAP[filters.pushed]) {
    const date = new Date();
    date.setDate(date.getDate() - PUSHED_MAP[filters.pushed]);
    parts.push(`pushed:>${date.toISOString().split("T")[0]}`);
  }

  parts.push("archived:false");
  parts.push("fork:false");
  return { q: parts.join(" "), /* sort, order */ };
}
```

外部依存がゼロなのでテストが書きやすく、フィルタ条件の追加もこの関数だけで完結します。

## まとめ

AI を組み込む際に一番大事だと感じたのは、**「ここは AI でやるべきか？」を機能ごとに問い直すこと**です。

| 判断軸 | 自動実行 | 遅延実行 | オンデマンド |
| --- | --- | --- | --- |
| レイテンシ許容度 | 低い（検索のクリティカルパスに入る） | 中（描画後でOK） | 高い（ユーザーが待つ覚悟） |
| トークンコスト | 小さい（100 tokens） | 中（2,000 tokens） | 大きい（4,000 tokens） |
| 失敗時の影響 | 低い（元のクエリで検索） | 低い（表示しないだけ） | 低い（元の README を表示） |

この3軸でマッピングすると、おのずと「自動 / 遅延 / オンデマンド」のどれが適切か決まります。

あとは **AI が壊れてもアプリは壊れない**設計を徹底すること。`AI_ENABLED` フラグ、すべての try-catch フォールバック、Zod バリデーションの3つのガードレールが、安心して AI を組み込める土台になりました。
