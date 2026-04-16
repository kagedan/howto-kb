---
id: "2026-04-16-今日のclaude-code-v21110-リリース毎日changelog解説-01"
title: "今日のClaude Code v2.1.110 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/7a134becf6f3f3d1d298"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-16"
date_collected: "2026-04-16"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.110では、ターミナル体験を大きく変える `/tui` コマンドの追加と、IDE連携・プラグイン管理周りの改善が中心です。

**今回の注目ポイント**
1. **`/tui fullscreen` でフリッカーフリーなフルスクリーンモード** — ちらつきのない没入型UIが同一会話のまま利用可能に
2. **Write toolがIDE diff編集をモデルに通知** — ユーザーが提案内容を書き換えた事実をAIが認識できるように
3. **`--resume`/`--continue` がスケジュールタスクを復活** — セッション再開時にcron・loopの未完タスクが自動復帰

---

## `/tui fullscreen` でフルスクリーンモードが同一会話のまま切り替え可能に

:::note info
