---
id: "2026-04-15-今日のclaude-code-v21109-リリース毎日changelog解説-01"
title: "今日のClaude Code v2.1.109 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/8d920b8bbc871098f906"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-15"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.109は変更点ひとつだけのコンパクトなリリースです。拡張思考(extended thinking)中のインジケータ表示が改善されました。

**今回の注目ポイント**

1. **拡張思考インジケータにローテーション式のプログレスヒントを追加** -- 思考中に「いま何やってるの?」が分かりやすくなりました

## 拡張思考のインジケータが進化した話

:::note info
Claude Codeで日常的にコーディングしていて、長い思考待ちが気になっていた方に嬉しい改善です。
:::

Claude Codeに少し複雑なタスクを投げると、裏側で拡張思考が走ります。コードベースの理解、設計判断、実装方針の検討......けっこう色々考えているわけですが、これまではその間のインジケータ表示がわりと素っ気なくて、「止まっ
