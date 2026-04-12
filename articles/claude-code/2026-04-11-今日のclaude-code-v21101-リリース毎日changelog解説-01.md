---
id: "2026-04-11-今日のclaude-code-v21101-リリース毎日changelog解説-01"
title: "今日のClaude Code v2.1.101 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/abdb27e2cbdb6cbcf8ea"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

Claude Code v2.1.101は、セキュリティ修正・セッション管理の改善・バグ修正を中心に、エンタープライズ環境対応や開発者体験の向上に注力した大規模リリースです。

## 今回の注目ポイント

1. **`/team-onboarding` コマンドの追加** -- ローカルの使用状況からチームメンバー向けのオンボーディングガイドを自動生成
2. **OS の CA 証明書ストアをデフォルト信頼** -- エンタープライズの TLS プロキシ環境でも追加設定なしで動作するように
3. **`permissions.deny` が PreToolUse フックに確実に優先されるよう修正** -- セキュリティポリシーの抜け道をふさぐ重要な修正

---

## チームのオンボーディングを自動化する `/team-onb
