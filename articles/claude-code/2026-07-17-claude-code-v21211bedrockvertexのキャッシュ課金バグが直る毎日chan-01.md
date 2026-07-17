---
id: "2026-07-17-claude-code-v21211bedrockvertexのキャッシュ課金バグが直る毎日chan-01"
title: "Claude Code v2.1.211｜Bedrock/Vertexのキャッシュ課金バグが直る｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/c8b144e3ba36744b964b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "AI-agent", "qiita"]
date_published: "2026-07-17"
date_collected: "2026-07-18"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.211 で一番効くのは、Bedrock・Vertex・Mantle・Foundry でプロンプトキャッシュが効かず、システムコンテキストの末尾が毎リクエスト新規入力トークンとして課金されていた不具合の修正。ゲートウェイ経由で会話を重ねるほど、無駄な入力トークンが請求に積み上がっていました。新機能は `--forward-subagent-text` の1件のみで、目立つのは権限とキャッシュまわりの挙動修正。

## 今回の注目ポイント

1. **Bedrock/Vertex のキャッシュ課金リグレッションを修正** システムコンテキスト末尾を毎リクエスト新規トークンとして課金していた (v2.1.211)
2. **サブエージェントの本文と thinking を stream-json に出力** 新フラグ `--forward-subagent-text` と環境変数 `CLAUDE_CODE_FORWARD_SUBAGENT_TEXT` で有効化 (v2.1.211)
3. **PreToolUse hook の ask が auto mode に勝つように** 非サンドボックスの Bash で hook が返した `ask` が最低でも承認プロンプトを保証 (v2.1.211)
4. **「always allow」がリポジトリルート保存に** worktree で与えた許可がセッションと worktree を跨いで残る (v2.1.211)
5. **chat 転送時の権限プレビューが Unicode 偽装を無効化** 双方向上書き・ゼロ幅・類似引用符を使ってもツール入力から承認メッセージの見た目を書き換えられない (v2.1.211)
6. **整数系の環境変数が科学表記・桁区切りを受付** タイムアウトやトークン予算を `1e6` や `64_000` と書ける (v2.1.211)

## Bedrock/Vertex でキャッシュが効かず毎回課金されていた

Bedrock・Vertex・Mantle・Foundry でプロンプトキャッシュのリグレッションが起きていました。システムコンテキストの末尾ブロックが、本来キャッシュヒットすべき場面でも毎リクエスト新規入力トークンとして課金される不具合。リクエストのたびに、キャッシュされるべき末尾ブロックをまるごと入力として払い直す形になっていました。

影響を受けるのは Anthropic API 直叩きではなく、この4つのゲートウェイ/プラットフォーム経由の構成。長いシステムプロンプトや CLAUDE.md を積んでいるほど、末尾ブロックのトークン数がそのまま無駄な課金に乗っていました。v2.1.211 でこのブロックがキャッシュヒットするようになり、請求が本来の水準へ戻る。

:::note warn
Bedrock / Vertex / Mantle / Foundry でここ数バージョン動かしていたなら、キャッシュヒット率と入力トークン課金を一度見直す価値があります。v2.1.211 前後で入力トークンの請求が下がります。
:::

## サブエージェントの本文と thinking を stream-json に流す

```bash
claude -p "レビューして" --output-format stream-json --forward-subagent-text
```

`--forward-subagent-text` フラグ、または環境変数 `CLAUDE_CODE_FORWARD_SUBAGENT_TEXT` を設定すると、stream-json 出力にサブエージェントの本文と thinking が乗るようになりました。付けなければ、サブエージェントの内部は stream に出てきません。

サブエージェントを動かす headless 実行で、thinking や途中出力を丸ごとログに落とせるようになる。stream-json をパースして自前のツールに流している人向けの追加。

## hook の ask が auto mode に上書きされなくなった

:::note info
対象読者: PreToolUse hook で Bash 実行をゲートしつつ、auto (自動承認) モードも併用している人。
:::

auto mode が、非サンドボックスの Bash に対して PreToolUse hook の `ask` 判定を上書きしてしまう不具合がありました。hook 側が「これは人間に確認させたい」と `ask` を返しても、auto mode がそれを飲み込んで自動承認していた。

v2.1.211 では hook の `ask` が判定の下限になります。auto mode でも、hook が `ask` を返したコマンドは最低でも承認プロンプトが出る。危険なコマンドを hook でゲートしている構成なら、auto mode 中の自動承認による取りこぼしが無くなる。

## その他の変更

| バージョン | カテゴリ | 変更点 | 概要 |
|---|---|---|---|
| v2.1.211 | 改善 | バックグラウンドエージェントの結果報告 | 実行中エージェントの状態を報告し、結果を捏造せず実際の完了を待つように |
| v2.1.211 | 修正 | `/clear` のコストカウンタ | `/clear` 後に statusline のコストが $0 から再開 |
| v2.1.211 | 修正 | サブエージェントのモデル override | resume や follow-up で親モデルに戻っていたのを修正 |
| v2.1.211 | 修正 | 並列セッションの一斉ログアウト | 認証情報を共有する複数セッションが sleep 復帰後に同時ログアウト |
| v2.1.211 | 修正 | Vertex/Bedrock の起動時通知 | モデル明示時に既定 Opus を試し、誤った fallback 通知を出していた |
| v2.1.211 | 修正 | plugin MCP サーバの再接続 | idle な web セッション復帰後に再接続せず MCP 呼び出しが失敗 |
| v2.1.211 | 修正 | nested `.claude/rules/*.md` | project settings を除外していても読み込まれていた |
| v2.1.211 | 変更 | Vim mode `s` / `S` | NORMAL モードで substitute char/line が効くように |

## まとめ

v2.1.211 は新機能1件に対して修正・変更が30件超という、地固めのリリース。キャッシュ課金の修正はゲートウェイ利用者の請求に直接効き、hook の `ask` 尊重は権限設計の前提を1つ固める。Bedrock/Vertex 構成なら、アップデート後に入力トークンの請求を一度確認すると差分が見えます。
