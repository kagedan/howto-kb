---
id: "2026-04-15-今日のclaude-code-v21108-リリース毎日changelog解説-01"
title: "今日のClaude Code v2.1.108 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/2733a8fbd2c7c3861b47"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-15"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.108は、セッション管理まわりの使い勝手を底上げしたリリースです。新機能2つ・改善5つ・バグ修正14件とボリューム多め。

**今回の注目ポイント**

1. **Recap機能の追加** -- セッションに戻ったとき、何をやっていたか自動で要約してくれる
2. **プロンプトキャッシュTTLの環境変数制御** -- 1時間/5分のTTLを環境変数で明示的に切り替え可能に
3. **スラッシュコマンドのモデル自動発見** -- `/init` や `/review` をモデルが自律的に呼び出せるように

## Recap: 「あれ、どこまでやったっけ?」がなくなる

:::note info
長時間セッションやマルチタスクで何度もClaude Codeを行き来する人向けの機能です。
:::

仕事中にSlack対応やミ
