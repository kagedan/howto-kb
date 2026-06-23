---
id: "2026-06-22-ccchangelogja-claude-code-v21186-リリース-主な変更点-mcp-サー-01"
title: "@CCChangelogJA: 🆕 Claude Code v2.1.186 リリース！ 📌 主な変更点: • MCP サーバー認証用の `claud"
url: "https://x.com/CCChangelogJA/status/2069177102474101088"
source: "x"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "x"]
date_published: "2026-06-22"
date_collected: "2026-06-23"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

🆕 Claude Code v2.1.186 リリース！

📌 主な変更点:
• MCP サーバー認証用の `claude mcp login/logout` コマンド追加（SSH 対応）
• `!` bash コマンドが自動応答をトリガーするように変更
• バックグラウンドサブエージェントが権限プロンプトをメインセッションに表示
• ワークフローのステータスフィルタリング機能追加
• スリープ復帰後のストリーミングエラーを修正

https://t.co/zgNDltrYK7

🚀 新機能

【MCP 認証】
• `claude mcp login <name>` および `claude mcp logout <name>` コマンドを追加 - インタラクティブな `/mcp` メニューを開かずに CLI から MCP サーバーを認証可能
• `--no-browser` フラグで SSH 経由の stdin リダイレクトに対応

【UI 改善】
• `/workflows` エージェント詳細ビューにステータスフィルタリング（`f` キー）を追加
• `/plugin` の Installed タブに "Skills" セクションを追加
• `teammateMode: "iterm2"` 設定を追加 - auto モードで `it2` CLI が見つからない場合に警告を表示
• `/login` に "Claude Platform on AWS - refresh credentials" オプションを追加（`awsAuthRefresh` 設定時）

【動作変更】
• `!` bash コマンドが Claude に出力への自動応答をトリガーするように変更 - 以前のコンテキストのみの動作に戻すには settings.json で `"respondToBashCommands": false` を設定
• バックグラウンドサブエージェントがメインセッションに権限プロンプトを表示するように変更（自動拒否せず） - ダイアログにどのエージェントが要求しているか表示され、Esc でそのツールのみ拒否可能
• `/review <pr>` が `/code-review medium` と同じレビューエンジンを使用するように変更
• `CLAUDE_CODE_MAX_RETRIES` の上限を 15 に変更 - 無人セッションには `CLAUDE_CODE_RETRY_WATCHDOG` を使用

🐛 バグ修正 + ⚡ パフォーマンス改善

【重要な修正】
• マシンのスリープ復帰後にストリーミングリクエストが "Content block not found" または JSON パースエラーで失敗する問題を修正
• サブエージェントのトランスクリプトスクロール位置が終了時にメイントランスクリプトに影響する問題を修正
• バックグラウンドセッションの要約が重複する問題を修正 - エージェント自身のターン終了時の要約が要約行として表示されるように
• `claude agents` からバックグラウンドセッションを開いた際に前の画面が残る問題を修正

【権限・セキュリティ】
• `Agent(type)` 拒否ルールと `Agent(x,y)` 許可タイプ制限が名前付きサブエージェント生成時に適用されない問題を修正
• Chrome タブグループ分離が並行 CLI セッションで製品内権限ゲートがオフの場合に適用されない問題を修正
• `--tools` が初回起動時にフラグ読み込み前に機能ゲート付きツールを通過させる問題を修正

【UI/UX】
• バックグラウンドタスクプレビューがエージェントのプラン読み込み前に生のツール名を点滅表示する問題を修正
• メインターン終了後もバックグラウンドエージェントが実行中の場合に Esc と Ctrl+C が応答しない問題を修正
• 権限プロンプトでオプションテキストがオーバーフローした際にオプション番号がずれる問題を修正
• エージェントパネルで完了したサブエージェントに `x` を押しても消えない問題を修正
• 古いセッション再開時に意図的に削除されたツールに対する誤解を招く "MCP server disconnected" 通知を修正
• `/plugin` Installed が最上部にスクロール済みでも "more above" インジケーターを表示する問題を修正
• `~~strikethrough~~` がアシスタントメッセージで打ち消し線として表示されずチルダが表示される問題を修正
• `claude agents` のバックグラウンドジョブステータスが返信後も古い "n
