---
id: "2026-04-22-ccchangelogja-新機能改善-subagent-agent-forked-subagent-01"
title: "@CCChangelogJA: 🚀 新機能・改善 【Subagent & Agent】 • Forked subagents を外部ビルドで有効化可能"
url: "https://x.com/CCChangelogJA/status/2046762742107844909"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "x"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-x"
---

🆕 Claude Code v2.1.117 リリース！

📌 主な変更点:
• Forked subagents が外部ビルドで利用可能に（環境変数設定で有効化）
• Pro/Max 購読者向けに Opus 4.6/Sonnet 4.6 のデフォルト effort を high に変更
• プラグインインストール時の依存関係自動解決機能を追加
• 起動速度の改善（ローカル・https://t.co/IYtLQ7H57q MCP サーバーの並行接続がデフォルトに）
• Opus 4.7 のコンテキストウィンドウサイズ認識の修正

https://t.co/8UaQkemt6F

🚀 新機能・改善

【Subagent & Agent】
• Forked subagents を外部ビルドで有効化可能に（`CLAUDE_CODE_FORK_SUBAGENT=1` で設定）
• Agent frontmatter の `mcpServers` が `--agent` 経由のメインスレッドセッションで読み込まれるように

【モデル設定】
• `/model` コマンド改善: プロジェクトが別モデルを固定している場合でも選択が再起動後も永続化。起動ヘッダーでアクティブモデルの出処（プロジェクト/managed-settings）を表示
• Pro/Max 購読者向けに Opus 4.6 と Sonnet 4.6 のデフォルト effort を `high` に変更（従来は `medium`）

【プラグイン管理】
• `plugin install` を既インストール済みプラグインに実行した場合、「既にインストール済み」で停止せず不足している依存関係をインストール
• プラグイン依存関係エラーが「not installed」とインストールヒントを表示。`claude plugin marketplace add` が設定済みマーケットプレイスから依存関係を自動解決
• managed-settings の `blockedMarketplaces` と `strictKnownMarketplaces` がプラグインのインストール・更新・リフレッシュ・自動更新時に強制適用

【セッション管理】
• `/resume` コマンドが大規模で古いセッションを再読み込み前に要約提案（既存の `--resume` の挙動と同等に）
• `cleanupPeriodDays` の保持期間スイープが `~/.claude/tasks/`、`~/.claude/shell-snapshots/`、`~/.claude/backups/` もカバー

【Advisor Tool（実験的）】
• ダイアログに「experimental」ラベルと詳細リンクを追加。有効時に起動通知を表示
• セッションが毎プロンプトと `/compact` で「Advisor tool result content could not be processed」エラーでスタックする問題を解消

【パフォーマンス】
• ローカルと https://t.co/IYtLQ7H57q の MCP サーバーが両方設定されている場合の起動高速化（並行接続がデフォルトに）
• macOS/Linux ネイティブビルド: `Glob` と `Grep` ツールを埋め込み型 `bfs` と `ugrep` に置き換え、Bash ツール経由で利用可能に。別ツールのラウンドトリップなしで高速検索（Windows と npm インストール版は変更なし）
• Windows: プロセスごとに `where.exe` 実行ファイル検索をキャッシュし、サブプロセス起動を高速化

【OpenTelemetry】
• `user_prompt` イベントがスラッシュコマンドの `command_name` と `command_source` を含むように
• `cost.usage`、`token.usage`、`api_request`、`api_error` がモデルが effort レベルをサポートする場合に `effort` 属性を含むように
• カスタム/MCP コマンド名は `OTEL_LOG_TOOL_DETAILS=1` が設定されていない限り編集される

🐛 バグ修正 ⚡ パフォーマンス

【認証・セッション】
• Plain-CLI OAuth セッションがアクセストークン有効期限切れ時に「Please run /login」で終了する問題を修正。401 エラー時にトークンをリアクティブに更新
• `CLAUDE_CODE_OAUTH_TOKEN` 環境変数で起動し、トークンが期限切れに
