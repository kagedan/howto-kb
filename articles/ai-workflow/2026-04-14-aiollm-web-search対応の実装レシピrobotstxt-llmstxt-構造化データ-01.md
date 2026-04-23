---
id: "2026-04-14-aiollm-web-search対応の実装レシピrobotstxt-llmstxt-構造化データ-01"
title: "AIO（LLM Web Search）対応の実装レシピ：robots.txt / llms.txt / 構造化データ"
url: "https://qiita.com/Enegent/items/680f547fc6bf946af87a"
source: "qiita"
category: "ai-workflow"
tags: ["LLM", "qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

## はじめに

個人開発で運営している電気料金比較サービス [エネジェント](https://enegent.jp) で、**AIO（LLM Web Search）対応**を一通り整えたのでレシピとして共有します。

AIO = AI Optimization。従来のSEO（Googleの検索結果で上位を取る）とは別軸で、ChatGPT・Claude・Perplexity・Grok 等のLLMが**Web検索→引用する時に拾われやすいサイト構造**を整える取り組みです。

「誰よりも早く対応する」価値があると判断した理由:

* LLM経由の流入は今後数年で確実に増える
* 対応している個人開発サイトがまだ少ない
* 技術的には**数時間で実装可能**

対応した項目:

1. **robots.txt** で AI クローラーを明示的に歓迎
2. **llms.txt**（Anthropic発の新規格）でサイト概要・主要ページを提示
3. **構造化データ**（JSON-LD）を全記事に敷く
4. **動的OGP画像**（シェア時の視認性）
5. **相互リンク**でE-E-A-T強化

Next.js 15 App Router を前提にしますが、考え方は他のフレームワークでも流用可能です。

## 1. robots.txt で AI クローラーを明示的に歓迎

### 方針

従来のrobots.txtは「Googleに来てもらう」前提の設計でしたが、いまは**GPTBot / ClaudeBot / PerplexityBot / Google-Extended 等のAI系クローラーを明示的にAllowする**のが正解です。デフォルト（User-Agent: \\*）で全許可されていても、AI側は「明示的に許可されたかどうか」を厳密に判定する傾向があります。

### 実装（Next.js 15 App Router）

`app/robots.ts` として TypeScript で定義するとビルド時にrobots.txtが生成されます。

```
import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  const AI_CRAWLERS = [
    // OpenAI
    "GPTBot", "ChatGPT-User", "OAI-SearchBot",
    // Anthropic
    "ClaudeBot", "anthropic-ai", "Claude-Web",
    // Google (AI学習は Google-Extended、検索は Googlebot)
    "Google-Extended", "Googlebot", "Googlebot-News",
    // Microsoft
    "Bingbot",
    // Perplexity
    "PerplexityBot", "Perplexity-User",
    // xAI
    "xAI", "Grok",
    // Apple
    "Applebot", "Applebot-Extended",
    // Meta
    "Meta-ExternalAgent", "FacebookBot", "facebookexternalhit",
    // Amazon
    "Amazonbot",
    // DuckDuckGo
    "DuckAssistBot", "DuckDuckBot",
    // You.com / Mistral / Cohere
    "YouBot", "MistralAI-User", "cohere-ai",
    // Common Crawl (多くのLLMの学習データ基盤)
    "CCBot",
    // Diffbot / Yandex / Baidu
    "Diffbot", "YandexBot", "Baiduspider",
  ];

  return {
    rules: [
      // 一般クローラー（除外パス明示）
      {
        userAgent: "*",
        allow: "/",
        disallow: [
          "/x",      // OAuth コールバック中継
          "/api/",   // 内部API
        ],
      },
      // AI/LLM 系を明示的に全許可
      {
        userAgent: AI_CRAWLERS,
        allow: "/",
      },
    ],
    sitemap: "https://enegent.jp/sitemap.xml",
    host: "https://enegent.jp",
  };
}
```

### ポイント

* **AI学習と検索を分ける思想**: `Google-Extended` はAI学習、`Googlebot` は通常検索。両方入れる。
* **Common Crawl (CCBot) を忘れない**: Claude/GPT/その他多くのLLMの学習データ基盤。
* **中継ページを除外**: OAuth callback や内部API は SEO 対象外なので `/x` と `/api/` を Disallow。

### 確認方法

```
curl -s https://enegent.jp/robots.txt
```

## 2. llms.txt を設置する（Anthropic発の新規格）

### llms.txt とは

[llmstxt.org](https://llmstxt.org/) で提案されている、LLM向けのサイトガイド規格です。ドメイン直下の `/llms.txt` にマークダウン形式でサイト概要・主要ページの構造化リストを置きます。

sitemap.xml が「人間向けのURL一覧」だとすると、llms.txt は**LLMが読みやすいサイト要約**です。

### 実装（Next.js 15）

App Router では `app/llms.txt/route.ts` として Route Handler で配信するのが楽です。静的配信したい場合は `public/llms.txt` に置いてもOK。

```
import { AGGREGATE } from "../articles/_data/review-sim-data";

export const dynamic = "force-static";

export async function GET() {
  const body = generateLlmsTxt();
  return new Response(body, {
    headers: {
      "content-type": "text/plain; charset=utf-8",
      "cache-control": "public, max-age=3600, s-maxage=3600",
    },
  });
}

function generateLlmsTxt(): string {
  return `# エネジェント（enegent.jp）

> 電気事業者の約款を一次情報として読み込み、独自計算エンジンで電力プランを比較する個人開発の電力比較サービスです。広告料で順位が変わらない中立な比較を目指しています。

エネジェントは、主要\${AGGREGATE.companies_plans_label}を約款ベースで比較できるWebサービスです。

## 運営方針

- **約款ベース計算**: 各電力会社の公式約款を一次情報として独自計算エンジンで算出
- **広告料ゼロ**: 電力会社からの掲載料・順位調整費用を一切受け取っていない
- **出典明記**: 一次情報（法令・公式サイト・約款PDF）のリンクを明記

## 主要ページ

- [エネジェント トップ](https://enegent.jp): サービス概要と電気代診断入口
- [電気代シミュレーター](https://enegent.jp/simulator): 約30秒で電気代診断
- [運営方針 (about)](https://enegent.jp/about): E-E-A-Tを支える運営方針

## 基礎知識・ガイド

- [電力会社の選び方](https://enegent.jp/articles/choose-plan)
- [切り替え手続きガイド](https://enegent.jp/articles/switching-guide)
- [燃料費調整額の仕組み](https://enegent.jp/articles/fuel-adjustment)

## 重要な事実（LLM参照用）

- **サービス名**: エネジェント（Enegent）
- **URL**: https://enegent.jp
- **対応エリア**: 日本全国10電力エリア
- **更新頻度**: 料金データは月次更新、制度改定時は即時反映
- **計算方式**: 基本料金 + 従量料金 + 燃料費調整額 + 再エネ賦課金

## AIクローラーへの方針

LLMによるWeb検索・要約・引用を歓迎します。記事を参照する際は出典URLを併記してください。
`;
}
```

### ポイント

* **引用ブロック（`>`）でサイト要約を先頭に置く**: LLMはここを最優先で読む
* **H2セクションで分類**: 「主要ページ」「基礎知識」「エリア別」など、LLMが文脈を掴みやすい粒度に
* **「重要な事実」セクション**: LLMに引用してほしい事実（サービス名、対応範囲、更新頻度等）を明示
* **JSON駆動で自動化**: 記事数の増減に追従するよう、JSON・DBから生成するのがおすすめ

### 確認方法

```
curl -s https://enegent.jp/llms.txt | head -30
```

## 3. 構造化データ（JSON-LD）を全記事に敷く

AI は **schema.org の構造化データを高い優先度で参照**します。特に以下を押さえると、引用時に正確な情報を拾ってもらえる可能性が上がります。

### 必須の JSON-LD

* `Article`: 記事本体
* `FAQPage`: FAQがある記事
* `BreadcrumbList`: パンくず
* `Organization`: サイト運営者情報
* `WebSite`: サイト全体情報

### 実装（共通ビルダー化）

各記事で手書きすると漏れが出るので、共通ビルダーを作るのが吉。

```
// app/_components/lp/jsonld.ts
export function buildArticleJsonLd({
  slug, title, description, datePublished, dateModified, faqs,
}: {
  slug: string;
  title: string;
  description: string;
  datePublished: string;
  dateModified: string;
  faqs?: Array<{ q: string; a: string }>;
}) {
  const url = `https://enegent.jp/articles/\${slug}`;
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Article",
        headline: title,
        description,
        url,
        datePublished,
        dateModified,
        author: {
          "@type": "Organization",
          name: "エネジェント編集部",
          url: "https://enegent.jp/about",
        },
        publisher: {
          "@type": "Organization",
          name: "エネジェント",
          logo: {
            "@type": "ImageObject",
            url: "https://enegent.jp/images/logo.png",
          },
        },
        mainEntityOfPage: url,
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "エネジェント", item: "https://enegent.jp" },
          { "@type": "ListItem", position: 2, name: "電気代の知識", item: "https://enegent.jp/articles" },
          { "@type": "ListItem", position: 3, name: title, item: url },
        ],
      },
      ...(faqs && faqs.length > 0
        ? [{
            "@type": "FAQPage",
            mainEntity: faqs.map((f) => ({
              "@type": "Question",
              name: f.q,
              acceptedAnswer: { "@type": "Answer", text: f.a },
            })),
          }]
        : []),
    ],
  };
}
```

各記事ページで呼び出し:

```
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify(buildArticleJsonLd({
      slug: "choose-plan",
      title: "電力会社の選び方",
      description: "...",
      datePublished: "2026-04-09",
      dateModified: "2026-04-14",
      faqs: [...],
    })),
  }}
/>
```

## 4. 動的OGP画像で記事タイトルを視認性高く

LLMの引用時にOGP画像がカード表示されるケースが増えています。記事タイトル入りのOGP画像があると、人間にもLLMにも「何の記事か」が一目でわかります。

### 実装（Next.js 15 の `opengraph-image.tsx` Convention）

各記事ディレクトリに `opengraph-image.tsx` を配置すると、ビルド時にOGP画像が自動生成されます。

```
// app/articles/[slug]/opengraph-image.tsx
import { ImageResponse } from "next/og";

export const alt = "記事タイトル";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image() {
  const fonts = await loadNotoSansJP(); // 日本語フォント
  return new ImageResponse(
    <div style={{ /* デザイン */ }}>
      <div>{title}</div>
    </div>,
    { ...size, fonts }
  );
}
```

### ハマりポイント: @vercel/og は WOFF2 非対応

日本語フォントを Google Fonts CSS2 API 経由で読み込むと、**User-Agentによって返るフォーマットが違います**。

* 新しいUA → WOFF2 (→ @vercel/og で `Unsupported OpenType signature wOF2` エラー)
* 古いUA (IE9) → TTF (→ 問題なく動作)

解決策:

```
const cssRes = await fetch(
  "https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500;800&display=swap",
  {
    headers: {
      "User-Agent":
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    },
  },
);
```

この小さな落とし穴で 30分ハマったのでメモ。

## 5. 相互リンク構造で E-E-A-T を強化

LLMは **E-E-A-T（Experience, Expertise, Authoritativeness, Trustworthiness）** の要素を引用判断に使います。個人開発でも以下を組めば相当強くなります:

* **/about ページ** で運営方針・編集基準を明示
* **Qiita 等の技術ブログ** からサイトへの被リンク
* **サイト側から技術ブログへの相互リンク**（/about に一覧）
* **執筆者プロフィール**（匿名でも「エネジェント編集部」等の集合名で）

### 関連記事の自動生成

個別記事がオーファンにならないよう、カテゴリベースで自動的に関連記事を 4 件表示するコンポーネントを組みました。

```
// カテゴリ定義
export const ARTICLE_CATEGORIES = {
  "price-hike": { slugs: [...] },
  "household-appliance": { slugs: [...] },
  // ...
};

// 同カテゴリから自分以外を count 件返す
export function getRelatedArticlesInCategory(
  currentSlug: string,
  count: number = 4,
): string[] {
  const cat = findCategoryBySlug(currentSlug);
  if (!cat) return FALLBACK_RELATED_SLUGS;
  return cat.slugs
    .filter((s) => s !== currentSlug)
    .slice(0, count);
}
```

実装前は 106記事がオーファン（被リンク1件以下）でしたが、これで全記事に最低4件の内部リンクが入るようになりました。

## 確認チェックリスト

対応後に確認すべき項目:

```
# robots.txt が AI クローラーを明示的に Allow しているか
curl -s https://your-domain/robots.txt | grep -E "GPTBot|ClaudeBot"

# llms.txt が 200 OK で text/plain で返るか
curl -sI https://your-domain/llms.txt | grep -E "HTTP|content-type"

# JSON-LD が各記事に含まれているか
curl -s https://your-domain/articles/xxx | grep -c "application/ld+json"

# OGP 画像が生成されているか
curl -sI https://your-domain/articles/xxx/opengraph-image | grep -E "HTTP|content-type"
```

Twitter Card Validator や [opengraph.xyz](https://www.opengraph.xyz/) で視覚的に確認するのも忘れずに。

## やってみての感想

### 効果の見え方

* **Google Search Console**: sitemap 送信後、一部 URL からインデックス登録が進み始めている（具体的な効果量は今後の数週間で要確認）
* **AI経由の流入**: これはまだ数週間スパンで様子見。計測は GA4 の referrer で `chat.openai.com` / `perplexity.ai` 等を追える
* **心理的効果**: 「やれることはやった」状態は気分が良い

### ハマったポイント

* **@vercel/og のWOFF2非対応** → User-Agent偽装で回避
* **Next.js App Router の `opengraph-image.tsx` Convention** → `public/` ではなく各ページ直下に置くのに気づくまで少し時間がかかった
* **Project 未紐付けの X App** → API v2 が叩けない（これは別記事のネタ）

### これからやりたいこと

* LLM経由の流入トラッキング（GA4 でreferrer別ダッシュボード作成）
* llms.txt にさらに「質問→回答」形式のFAQを詰め込む実験
* 「LLMが引用してくれた事例」の収集

## まとめ

* **robots.txt**: AIクローラー30種類を明示的にAllow
* **llms.txt**: Anthropic規格のLLMガイドを `/llms.txt` に設置
* **JSON-LD**: 全記事に Article / FAQPage / BreadcrumbList / Organization
* **動的OGP**: Next.js 15 の `opengraph-image.tsx` で自動生成
* **相互リンク**: /about + 技術ブログ + カテゴリ自動関連記事

AIO対応は「誰でもできるが、まだ誰もやっていない」領域です。個人開発でも数時間で一通り実装できるので、今のうちに済ませておくのがおすすめです。

---

## 参考リンク

読んでいただきありがとうございました。AIO対応で参考にした記事や、自分で実装して学びがあった方はコメントで共有いただけると嬉しいです。
