---
id: "2026-05-31-claude-code-v21158-リリース毎日changelog解説-01"
title: "Claude Code v2.1.158 リリース｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/eb81e3eaf92809d5aa82"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-05-31"
date_collected: "2026-05-31"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.158 の変更は Auto mode のクラウド対応1点。Bedrock・Vertex・Foundry でも Opus 4.7 / 4.8 の自動切り替えが使えるようになりました。

### 今回の注目ポイント

1. **Auto mode が Bedrock / Vertex / Foundry に対応** - エンタープライズのクラウドバックエンド経由でも Opus 4.7・4.8 の自動切り替えがオプトインで使える

## Auto mode がエンタープライズのクラウドで解禁

:::note info
対象読者: Bedrock / Vertex / Foundry 経由で Claude Code を運用しているチーム
:::

Auto mode は、タスクに応じて Claude Code が使うモデルを自動で切り替える機能。これまで対象外だった3つのクラウドバックエンドが、v2.1.158 で加わりました。

- Bedrock (AWS)
- Vertex (Google Cloud)
- Foundry (Azure)

対象は Opus 4.7 と Opus 4.8。デフォルト無効なので、環境変数で明示的にオプトインします。

```bash
# 例: Bedrock 経由で Auto mode を有効化
export CLAUDE_CODE_USE_BEDROCK=1
export CLAUDE_CODE_ENABLE_AUTO_MODE=1
claude
```

何が変わるか。社内ポリシーで Bedrock や Vertex を必須にしている組織では、Auto mode に乗れず、モデル選択を手動で握り続ける必要がありました。v2.1.158 でクラウド経由でも自動切り替えが効きます。

`CLAUDE_CODE_ENABLE_AUTO_MODE=1` を入れない限り挙動は変わりません。既存の運用を崩さないオプトイン式。

## まとめ

v2.1.158 は Auto mode のクラウド対応のみ。Bedrock・Vertex・Foundry で Opus 4.7 / 4.8 を使うチームは、環境変数1つで自動切り替えに乗れます。クラウドバックエンドが必須の組織は、`CLAUDE_CODE_ENABLE_AUTO_MODE=1` を足すだけで切り替わります。
