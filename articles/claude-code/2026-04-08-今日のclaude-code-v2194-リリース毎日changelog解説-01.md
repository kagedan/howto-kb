---
id: "2026-04-08-今日のclaude-code-v2194-リリース毎日changelog解説-01"
title: "今日のClaude Code v2.1.94 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/1d5e804cd3bd172b398a"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "qiita"]
date_published: "2026-04-08"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

Bedrock/Vertex/Foundry・チーム・エンタープライズユーザーのデフォルト `effort` レベルが **high** に引き上げられ、Bedrock Mantle対応やセッションタイトルのフック設定など実用的な改善が加わったリリースです。

## 今回の注目ポイント

1. **デフォルト `effort` が high に格上げ** -- API・Bedrock・Vertex・Foundry・Team・Enterpriseユーザーは設定なしで高品質な応答が得られるように
2. **Amazon Bedrock powered by Mantle 対応** -- 環境変数1つで Mantle 経由の Bedrock 呼び出しが可能に
3. **`hookSpecificOutput.sessionTitle`
