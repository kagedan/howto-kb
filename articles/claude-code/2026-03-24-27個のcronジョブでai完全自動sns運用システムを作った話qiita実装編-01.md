---
id: "2026-03-24-27個のcronジョブでai完全自動sns運用システムを作った話qiita実装編-01"
title: "27個のcronジョブでAI完全自動SNS運用システムを作った話【Qiita実装編】"
url: "https://qiita.com/kenji_harada/items/f846eab18f9cafa63d8d"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "TypeScript", "qiita"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

この記事は自社ブログ([nands.tech](https://nands.tech/posts/ai-autonomous-sns-platform-full-architecture))の要約版です

## はじめに

「SNS更新、忘れがちなんですよね...」

そんな悩みを抱えるエンジニアは多いはず。自分も例外ではなく、技術的な知見はあるのに情報発信が継続できない日々が続いていました。

そこで思い切って**AIに全部任せる**システムを作ってみました。

1ヶ月間Claude Codeと向き合い、27個のcronジョブが24時間稼働する完全自動SNS運用基盤が完成。結果、**人間の作業時間は1日0分**になりました。

今回は実装のポイントとコード例を中心に紹介します。

## システム構成と技術スタック

まず全体像から。6層のアーキテクチャで構成されています：

```typescript
// メインの処理フロー
export async function executeAutoPostFlow() {
  // 1. ソース収集
  const sources = a
