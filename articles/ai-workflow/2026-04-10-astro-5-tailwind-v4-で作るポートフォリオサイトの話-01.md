---
id: "2026-04-10-astro-5-tailwind-v4-で作るポートフォリオサイトの話-01"
title: "Astro 5 + Tailwind v4 で作るポートフォリオサイトの話"
url: "https://zenn.dev/ena_dri/articles/ad4417181bf3f0"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

## はじめに

[Zenn（前）](https://zenn.dev/ena_dri/articles/d32b848b88f64d)回、個人HPをゴリゴリエモーショナルな感じで当時の”アレ”を集めに集めてつくったのを、そうだ！作り直そう！と一念発起した感じです。因みにあれからも何度かブラッシュアップしてて最近はまた[変](https://www.ena-dri.dev/)な感じになっているので是非見てきてね。大人の厨二病ってこんな感じですよ。

さて、本題ですが今回作った新しいポートフォリオサイトは↓  
成果物: [modern.ena-dri.dev](https://modern.ena-dri.dev/)

## コンセプト

モノクローム（ink / paper）のみ。装飾はゼロ。それっぽいオサレな感じにしてみる。  
要するに遊んでみたかっただけである。

* 色: 白・黒・グレーのみ
* 線: 0.5px罫線と斜線パターン
* フォント: Playfair Display（見出し）× DM Sans（本文）

---

## 技術スタック

| 役割 | 採用技術 |
| --- | --- |
| フレームワーク | Astro 5.x |
| スタイリング | Tailwind CSS v4 |
| データ管理 | Astro Content Collections |
| ホスティング | Cloudflare Pages |

---

## 実装メモ

### Tailwind v4 の設定

`tailwind.config.mjs` は不要になった。`global.css` の `@theme` ブロックだけで完結する。

```
@import "tailwindcss";
@plugin "@tailwindcss/typography";

@theme {
  --color-ink: #1a1a1a;
  --color-ink-muted: #666666;
  --color-paper: #f8f8f8;
  --color-rule: #e5e5e5;
  --font-display: "Playfair Display", serif;
}
```

### Zenn記事の取り込み

Zennの記事をサイト内で表示するためにAstroカスタムLoaderを実装した。RSSは途中までしか配信されないので、非公式JSON APIを2段階で叩く。

```
// src/content.config.ts
const writing = defineCollection({
  loader: async () => {
    const res = await fetch('https://zenn.dev/api/articles?username=ena_dri&order=latest');
    const { articles } = await res.json();

    return Promise.all(
      articles.map(async (item) => {
        const detail = await fetch(`https://zenn.dev/api/articles/${item.slug}`);
        const { article } = await detail.json();
        return {
          id: item.slug,
          title: item.title,
          htmlBody: article.body_html,
        };
      })
    );
  },
  schema: z.object({ ... })
});
```

ビルド時に全記事のHTMLが静的化される。

> **注意**: 記事数が多い場合は `Promise.all` の並列リクエストがレートリミットに触れる可能性があります。その場合はチャンク分割処理が必要です。

### Zenn埋め込みカードの処理

Zennが生成する `<iframe>` は外部JSがないと描画されない。`data-content` からURLを抽出して自前のリンクカードに置換した。  
このやり方であれば、サイト内デザインを崩さずにカードが表示出来ていい。

↓こんな感じ。Zenn記事を個人のポートフォリオで表示するのいいよね。  
![](https://static.zenn.studio/user-upload/16337b4dabea-20260410.png)

```
htmlBody = htmlBody.replace(
  /<iframe[^>]*src="https:\/\/embed\.zenn\.studio\/card[^>]*data-content="([^"]+)"[^>]*><\/iframe>/g,
  (_, encodedUrl) => {
    const url = decodeURIComponent(encodedUrl);
    return `<div class="zenn-link-replacement">
              <a href="${url}" target="_blank">${url}</a>
            </div>`;
  }
);
```

Zenn由来のシンタックスハイライトも `!important` で上書きして無彩色に統一している。

---

## なぜ 前回Vercel使って今回はCloudflare Pages か

サイトの性質によってホスティング先の選択肢が変わるというの最近学んだ。

ポートフォリオ・ブログのように「誰が見ても同じ内容」ならビルド時に全部HTMLを吐き出して終わり。Cloudflare PagesはそのHTMLを世界中のエッジから配信するだけなので、サーバーレスポンスの待ち時間がほぼゼロになる。

ログイン機能やユーザーごとに異なるコンテンツが必要な場合はVercelのようなサーバーサイドレンダリング環境が適している。  
※最近の筆者のプロダクトなら[TypePlot](https://typeplot.ena-dri.dev/)がなんちゃって動的サイト。

## まとめ

何よりも感動したのが、.mdを追加したり更新したりしてpushすればサイト内容が簡単に修正追加できることですね。Astro 5面白いかよ…

あとAstro 5のContent Collections（カスタムLoader）は、外部APIからの取得・変換処理をビルドプロセスに組み込める。Cloudflare Pagesへのデプロイも、GitHubへのpushで完結するのはいいよね。

HPのデザインを考えてる時にふと。  
最近流行ってるDESIGN.mdもそうだけど、AI臭さをどうやって薄めるかは中々の課題だと感じたので邁進していきたいですね。
