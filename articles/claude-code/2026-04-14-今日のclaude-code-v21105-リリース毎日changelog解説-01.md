---
id: "2026-04-14-今日のclaude-code-v21105-リリース毎日changelog解説-01"
title: "今日のClaude Code v2.1.105 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/adfe2a43357decb68ff7"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

プラグイン向けの新機能2つと、体感に効く安定性改善、そしてバグ修正が24件。地味ながら着実に磨かれたリリースです。

**今回の注目ポイント**

1. **PreCompact フックでコンテキスト圧縮を制御可能に** --- 長いセッションの自動圧縮をフックで止められるようになりました
2. **プラグインにバックグラウンドモニター機能が追加** --- セッション裏で監視処理を自動起動するプラグインが作れます
3. **ストリーム・ネットワーク周りの安定性向上** --- 無限ハングや無言スピナーがようやく解消されました

---

## PreCompact フックでコンテキスト圧縮を制御できるようになった

:::note info
対象: 長いセッションを日常的に使うユーザー、フックを活用しているパワーユーザー
::
