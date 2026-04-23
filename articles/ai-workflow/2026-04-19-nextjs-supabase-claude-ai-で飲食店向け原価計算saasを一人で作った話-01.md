---
id: "2026-04-19-nextjs-supabase-claude-ai-で飲食店向け原価計算saasを一人で作った話-01"
title: "Next.js + Supabase + Claude AI で飲食店向け原価計算SaaSを一人で作った話"
url: "https://zenn.dev/saytooy_arch/articles/13-genka-nextjs-supabase-ai-cost"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

# Next.js + Supabase + Claude AI で飲食店向け原価計算SaaSを一人で作った話

## はじめに

個人事業主として食品をECで販売している方の多くは、原価計算を「感覚」でやっています。

「このお菓子、材料費いくらだっけ……たぶん300円くらい？」

この「たぶん」が、じわじわ利益を削っていきます。

この課題を解決するため、**Genka**（原価計算・食品表示ラベル統合SaaS）を一人で開発しました。本記事では技術的な実装ポイントを中心に紹介します。

---

## サービス概要

**Genka** は以下の機能を提供する SaaS です。

* **AI原価計算**: レシピのテキストを貼り付けるだけで、Claude AI（Haiku）が食材・分量を自動抽出して原価率を計算
* **食品表示ラベル生成**: アレルゲン・栄養成分を含む食品表示ラベルをPDF出力
* **価格提案**: 目標原価率から逆算した推奨販売価格を提示
* **月次振り返り**: 月ごとの理論原価・粗利のサマリー

**技術スタック:**

| レイヤー | 技術 |
| --- | --- |
| フロントエンド | Next.js 15 (App Router) + Tailwind CSS |
| バックエンド | Next.js API Route Handlers |
| DB | Supabase (PostgreSQL) + Drizzle ORM |
| 認証 | Supabase Auth |
| AI | Anthropic Claude Haiku 4.5 |
| 決済 | Stripe |
| デプロイ | Vercel |

---

## アーキテクチャ設計の要点

### レイヤー構成

```
src/
  app/
    (app)/          # 認証済みページ（ダッシュボード・メニュー・食材）
    (auth)/         # 認証ページ（ログイン・サインアップ）
    api/            # API Route Handlers
  services/         # ビジネスロジック層（serviceは直接DBを触る）
  db/
    schema.ts       # Drizzle ORM スキーマ定義
  lib/
    calc/           # 原価計算ロジック（純粋関数）
    supabase/       # Supabase クライアント
```

**設計方針**: API Route Handler は「認証 → バリデーション → service呼び出し → レスポンス成形」のみ。ビジネスロジックは全て `services/` に閉じ込めます。

### 認証パターン

```
// src/services/auth-service.ts
export async function authenticate(): Promise<AuthResult> {
  const supabase = await createServerSupabase();
  const { data: { user }, error } = await supabase.auth.getUser();

  if (error || !user) {
    return { ok: false, error: { code: "UNAUTHORIZED", status: 401, ... } };
  }

  const shop = await db
    .select({ id: shops.id })
    .from(shops)
    .where(eq(shops.userId, user.id))
    .limit(1);

  if (!shop.length) {
    return { ok: false, error: { code: "SHOP_NOT_FOUND", status: 404, ... } };
  }

  return { ok: true, context: { userId: user.id, shopId: shop[0].id } };
}
```

全API Route Handlerの冒頭でこの `authenticate()` を呼び、`shopId` でデータをフィルタします。テナント分離の基本です。

---

## Claude AI によるレシピ自動解析

最も差別化できているポイントが、Claude Haiku を使ったレシピ自動解析です。

### 実装フロー

```
レシピテキスト入力
       ↓
Claude Haiku API呼び出し（structured output）
       ↓
食材名・分量・単位の配列を取得
       ↓
食材マスタと照合（名前マッチング）
       ↓
原価率自動計算
```

### プロンプト設計のポイント

レシピテキストから食材を抽出する際、以下の点に気をつけました。

```
const systemPrompt = `
あなたは料理レシピから食材と分量を抽出する専門家です。
以下のルールに従って抽出してください：

1. 各食材を個別の項目として列挙する
2. 分量は数値と単位に分離する（例: "薄力粉 200g" → name:"薄力粉", quantity:200, unit:"g"）
3. "少々"・"適量"は quantity:0 として扱う
4. レシピに含まれない調味料は追加しない
5. 食材名は一般的な表記を使う（"薄力粉" OK、"ケーキ用小麦粉" NG）
`;
```

**JSONスキーマを使ったstructured output** により、後処理のパース失敗を防いでいます。

### エラーハンドリング

AI出力は不確実なため、以下のフォールバックを実装しています：

1. JSON パース失敗 → ユーザーにエラーを返す（手動入力を促す）
2. 食材マスタ未登録 → `ingredientId=null` のまま保存し、後から登録できる
3. AIタイムアウト（15秒） → タイムアウトエラーを返す

---

## Drizzle ORM × Supabase の実践的な使い方

### スキーマ定義

```
// src/db/schema.ts
export const menus = pgTable("menus", {
  id: uuid("id").primaryKey().defaultRandom(),
  shopId: uuid("shop_id")
    .notNull()
    .references(() => shops.id, { onDelete: "cascade" }),
  name: text("name").notNull(),
  sellingPrice: decimal("selling_price", { precision: 10, scale: 0 }).notNull(),
  rawRecipe: text("raw_recipe"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
});
```

Drizzle ORM は型安全なクエリが書けるため、プロダクションでも安心して使えます。

### トランザクション実装例

食材の自動追加（レシピ入力時に未登録食材を自動的に食材マスタへ追加）はトランザクションで実装しました。

```
return await db.transaction(async (tx) => {
  // Step 1: 未登録食材を自動追加
  for (const name of uniqueUnlinkedNames) {
    const existing = await tx
      .select({ id: ingredients.id })
      .from(ingredients)
      .where(and(eq(ingredients.shopId, shopId), eq(ingredients.name, name)))
      .limit(1);

    if (!existing.length) {
      const [inserted] = await tx
        .insert(ingredients)
        .values({ shopId, name, unitPrice: "0", unit: "g", ... })
        .returning({ id: ingredients.id });
      resolvedIds.set(name, inserted.id);
    }
  }

  // Step 2: メニュー本体をINSERT
  const [menu] = await tx
    .insert(menus)
    .values({ shopId, name: input.menuName, ... })
    .returning({ id: menus.id });

  // Step 3: menu_ingredients を一括INSERT
  await tx.insert(menuIngredients).values([...]);

  return { menuId: menu.id, autoAddedIngredients };
});
```

---

## Stripe サブスクリプション統合

### プラン設計

| プラン | 月額 | メニュー数 | ラベル生成 |
| --- | --- | --- | --- |
| 無料 | 0円 | 3件 | 1件/月 |
| スタンダード | 980円 | 無制限 | 10件/月 |
| プロ | 2,980円 | 無制限 | 無制限 |

### Webhook 処理の実装

Stripe のWebhookイベントを受け取り、サブスクリプション状態を更新します。

```
// POST /api/stripe/webhook
export async function POST(request: NextRequest) {
  const body = await request.text();
  const sig = request.headers.get("stripe-signature") ?? "";

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, sig, webhookSecret);
  } catch {
    return NextResponse.json({ error: "Webhook signature verification failed" }, { status: 400 });
  }

  switch (event.type) {
    case "customer.subscription.created":
    case "customer.subscription.updated":
      await handleSubscriptionUpdate(event.data.object as Stripe.Subscription);
      break;
    case "customer.subscription.deleted":
      await handleSubscriptionCanceled(event.data.object as Stripe.Subscription);
      break;
  }

  return NextResponse.json({ received: true });
}
```

**ポイント**: `webhooks.constructEvent` でシグネチャ検証を必ず行います。署名なしのWebhookリクエストを受け入れると、悪意あるリクエストでサブスクリプション状態を改ざんされる可能性があります。

---

## 食品表示ラベル自動生成

食品表示法の義務項目を自動生成する機能です。

### アレルゲン判定

日本の食品表示法では、8品目（義務表示）+ 20品目（推奨表示）のアレルゲン表示が求められます。

```
const MANDATORY_ALLERGENS = ["えび", "かに", "くるみ", "小麦", "そば", "卵", "乳", "落花生"];
const RECOMMENDED_ALLERGENS = ["アーモンド", "あわび", "いか", ...]; // 20品目
```

各食材の `allergen_flags` JSONBカラムにアレルゲン情報を保持し、メニュー内の全食材を集計して表示ラベルを生成します。

### 栄養成分計算

日本食品標準成分表（八訂）増補2023年のデータをDBに投入し、食材の重量から栄養成分を計算します。

```
栄養成分（1食分）= Σ（食材の使用量g ÷ 100 × 成分表100g当たりの値）
```

---

## 開発プロセスの工夫

### AI駆動開発

本プロジェクトはClaudeをエージェントとして活用した「AI駆動開発」で構築しました。

* **仕様策定 → 実装 → テスト → レビュー**の全工程をエージェントが担当
* 品質ゲート（工程移行チェックリスト）で手順の抜け漏れを防止
* hookスクリプトでコーディング規約の自動チェックを実施

### テスト戦略

* **単体テスト（Vitest）**: 原価計算ロジックなどの純粋関数
* **統合テスト（Playwright）**: E2Eのクリティカルパス（サインアップ→メニュー作成→原価確認）

---

## まとめ・今後

**作って気づいたこと:**

1. **AI抽出の精度**はユーザー体験に直結。Haiku は速度と精度のバランスが良い
2. **Drizzle ORM** は型安全で開発体験が良い。SQLに近い書き方で習得コストも低い
3. **Supabase Auth** + RLS の組み合わせはマルチテナントSaaSに向いている

**今後の予定:**

* クローズドβテスト（個人事業主10〜30名）
* 検証後に正式リリース
* 食品表示法の改正への追従（2026年対応）

---

もし「自分もこういうツールが欲しかった」という方がいれば、βテスターとして参加していただけると嬉しいです。

GitHubリポジトリ: （βテスト終了後に公開予定）

---

*本記事はGenkaの技術実装の一部を紹介したものです。詳細な実装については質問をお気軽にどうぞ。*
