---
id: "2026-04-08-今日のclaude-code-v2196-リリース毎日changelog解説-qiita-01"
title: "今日のClaude Code v2.1.96 リリース｜毎日Changelog解説 - Qiita"
url: "https://qiita.com/moha0918_/items/1d5d42f68720010a9d28"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-08"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

v2.1.94で混入したBedrock認証エラーのバグを修正した、単一バグフィックスのリリースです。

## 今回の注目ポイント

1. **Bedrock認証エラーの修正** -- v2.1.94から発生していた `403 "Authorization header is missing"` エラーを解消

---

## Bedrock認証が突然壊れた問題、修正されました

v2.1.94にアップデートしてからBedrockリクエストが失敗するようになった方は、今すぐv2.1.96へのアップデートを推奨します。

**何が変わったか**というと、v2.1.94で混入したリグレッション（デグレ）バグが修正されました。

具体的には、以下の環境変数を使ってBedrockの認証を制御しているケースで、リクエストが `403 "Authorization header is missing"` エラーで失敗する問題が発生していました。

```
AWS_BEARER_TOKEN_BEDROCK
CLAUDE_CODE_SKIP_BEDROCK_AUTH
```

**なぜ嬉しいか**は明快で、これらの環境変数はAWS Bedrock経由でClaude Codeを利用する際の認証フローをカスタマイズするためのものです。特に社内プロキシやカスタム認証基盤を経由してBedrockにアクセスしている環境では、これらの変数が必須となることがあります。v2.1.94へのアップデート後に突然Claude Codeが使えなくなった方にとっては、待ちわびた修正です。

`CLAUDE_CODE_SKIP_BEDROCK_AUTH` はBedrockの署名付きリクエストをスキップするための変数で、独自の認証レイヤーを持つ環境向けの設定です。v2.1.94以前のバージョンで正常に動作していた場合、v2.1.96で元の挙動に戻ります。

---

## まとめ

今回のv2.1.96は、v2.1.94で発生したBedrock認証まわりのリグレッションバグを修正する緊急パッチリリースです。**AWS Bedrock経由でClaude Codeを利用している方**、特に `AWS_BEARER_TOKEN_BEDROCK` や `CLAUDE_CODE_SKIP_BEDROCK_AUTH` を設定している環境では、すぐにアップデートすることをおすすめします。新機能の追加はありませんが、Bedrockユーザーにとっては実質的に「使えない状態から使える状態に戻る」重要な修正です。
