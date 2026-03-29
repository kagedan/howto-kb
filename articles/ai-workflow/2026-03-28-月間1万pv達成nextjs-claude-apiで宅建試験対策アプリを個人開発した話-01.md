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

解説の品質がアプリの
