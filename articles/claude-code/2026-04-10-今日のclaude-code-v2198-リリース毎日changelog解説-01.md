---
id: "2026-04-10-今日のclaude-code-v2198-リリース毎日changelog解説-01"
title: "今日のClaude Code v2.1.98 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/0695a5e0a5b2ade1cf85"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

Bedrock設定ウィザードに続き、今回はVertex AI対応の設定ウィザード追加、Perforceサポート、セキュリティ強化、そして40件超のバグ修正と幅広い改善が入ったリリースです。

## 今回の注目ポイント

1. **Google Vertex AI 対話式セットアップウィザード** -- ログイン画面から GCP 認証・プロジェクト設定・モデル固定まで一気通貫で設定可能に
2. **Perforce 連携モード (`CLAUDE_CODE_PERFORCE_MODE`)** -- 読み取り専用ファイルへの誤上書きを防止し、`p4 edit` へのヒントを表示
3. **Bash ツールのセキュリティ修正多数** -- バックスラッシュエスケープや複合コマンドによる権限バイパスなど複数の脆弱性を修正

---

##
