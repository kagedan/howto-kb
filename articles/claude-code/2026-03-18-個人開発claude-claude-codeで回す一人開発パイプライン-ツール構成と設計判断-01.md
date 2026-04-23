---
id: "2026-03-18-個人開発claude-claude-codeで回す一人開発パイプライン-ツール構成と設計判断-01"
title: "【個人開発】Claude + Claude Codeで回す一人開発パイプライン — ツール構成と設計判断"
url: "https://qiita.com/imyshKR/items/c2de1c0e24f0245bff91"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-18"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

一人で企画から運営まで回すために、Claude.ai、Claude Code、[Claude Forge](https://github.com/sangrokjung/claude-forge)を組み合わせたプロセスシステムを構築しています。この記事はシステム全体の構成と各ツールの役割をまとめたものです。  
[![forge-pipeline-diagram.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4380119%2F5924eb46-667b-4938-be34-998366126aba.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=00c4b24261273f072463fb7fa22b4cdf)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4380119%2F5924eb46-667b-4938-be34-998366126aba.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=00c4b24261273f072463fb7fa22b4cdf)

> ※ 各ツールの詳細記事は順次公開予定です。公開後にリンクを追加していきます。

## システム全体像

[![process-flow-diagram.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4380119%2F70d062a5-2273-4c41-bea7-70869c313613.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5c6094ffa500925a0f0e18bf5e0a6594)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4380119%2F70d062a5-2273-4c41-bea7-70869c313613.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=5c6094ffa500925a0f0e18bf5e0a6594)

```
1. アイデアメモ          → Claude.ai
2. プロジェクト企画       → Claude.ai + spec.md / prompt_plan.md
3. 実装                 → Claude Code + Claude Forge
4. 整理・理解            → Claude.ai + prompt_plan.md / progress_log.md
5. MVP運営              → Claude.ai + GA4
6. 保守・アップデート     → 2〜4を機能単位で繰り返し
```

この6段階の構成は、複数のプロジェクトを経験しながら自分で組み立てたものです。6の保守・アップデートでは、機能単位で以下を繰り返します。

```
機能企画（なぜ必要か）→ Claude Forgeで実装 → 整理（なぜ・どうやって）
```

## ツール構成マップ

| ツール | 種類 | 役割 | 適用段階 |
| --- | --- | --- | --- |
| 会話ネーミングCI | User Preferences | 会話の段階管理 | 全段階 |
| dev-logスキル | Claudeスキル | 一行ログ + 現状確認 | 全段階 |
| /plan-sync | Claude Codeスキル | Web企画→Code自動マージ | 実装 |
| Telegram Bot（実装中） | Node.js Bot | モバイルからパイプライン実行 | 実装 |
| Claude Forge | OSSパイプライン | /plan→/tdd→/review→/commit | 実装 |

## 各ツールの概要と詳細記事

### 会話ネーミングCI

User Preferencesに入れるルール。会話開始時にClaudeが「段階 | プロジェクト 作業内容」形式の名前を提案。

```
企画 | kigaru プレミアム機能
実装 | kigaru 相性機能
完了 | kigaru 今日の運勢
```

3段階（企画/実装/完了）の区分と切り替え基準は自分で定義。ハンドオフプロンプト作成＝実装開始。

→ [詳細記事](https://qiita.com/imyshKR/items/495bb9e910bea3c682b6)

### dev-logスキル

会話で作業が始まるとClaudeが一行ログを自動生成。8分類体系、ログフォーマット、memory edit + mdファイルの二重構造は自分で設計。

```
[kigaru] 📍プロモーション | [改善] AI応答速度 — 3秒→1.5秒 (03-14) | [デプロイ] ドメイン接続 (03-16)
```

8分類：企画/デザイン/開発/エラー/改善/リファクタリング/デプロイ/プロモーション

→ 詳細記事（近日公開）

### /plan-sync

Claude Webの企画マークダウンをClaude Codeに貼り付けると、既存文書と競合チェック後に自動マージ。オリジナルのForgeになかったものを独自に追加した機能で、4段階の競合チェックレポートも自分で設計しました。

```
/plan-sync [企画マークダウン]
→ 🔴競合 / 🟡注意 / 🟢新規 / 🔵実装済み でレポート
→ 承認後にspec.md + prompt_plan.md更新
```

→ 詳細記事（近日公開）

### Telegram Bot（実装中）

Claude Code headlessモード（`claude -p`）をTelegram Botで呼び出し。ノートPC＝サーバー、Cloudflare Tunnel経由。

`current_plan.md`でセッション間コンテキスト維持。この仕組みは自分で設計。auto/requiredのレベル分離。

→ 詳細記事（近日公開）

### Claude Forge パイプライン詳細

核心フロー：

```
/plan-sync → /next-task → /plan → /tdd → /code-review → /handoff-verify → /commit-push-pr
```

各ステップで人間が判断するポイントと、生成・消費されるファイルを整理します。

| ステップ | 内容 | 人間の判断 | ファイル操作 |
| --- | --- | --- | --- |
| /plan-sync | 企画mdをプロジェクト文書にマージ | 競合レポート確認 | `mymd/todo/`にplan md入力 → `prompt_plan.md`更新 |
| /next-task | 次タスク推薦 | タスク選択 | — |
| /plan | 実装計画策定 | **計画を承認または修正** | `current_plan.md`作成 |
| /tdd | テスト駆動実装 | — | — |
| /code-review | コード品質レビュー | — | — |
| /handoff-verify | ビルド/テスト/リント検証 | **変更点・エラー・注意事項を確認** | — |
| /commit-push-pr | コミット・PR作成 | — | 完了タスクを`prompt_plan.archived.md`に移動、`current_plan.md`削除 |

3〜7のステップは`progress_log.md`に記録されます。実装完了後の「4. 整理・理解」フェーズで、`prompt_plan.md`と`progress_log.md`を基に実装期間と過程を振り返ります。

Telegram Botはこのうち2〜7（`/plan-sync`から`/commit-push-pr`まで）をモバイルから実行可能にしたものです。

### ファイルライフサイクル

```
企画md（mymd/todo/）
  ↓ /plan-sync
prompt_plan.md（タスク追加）
  ↓ /plan
current_plan.md（実装計画 — 承認後に実装開始）
  ↓ /tdd ~ /commit-push-pr
prompt_plan.archived.md（完了タスク移動）
current_plan.md 削除
progress_log.md（3〜7の実行記録を蓄積）
```

## 設計原則

| 原則 | 内容 |
| --- | --- |
| 方向は人間、実行はAI | AIが次を決めない。選択肢の提示のみ |
| 軽さ | ログが重いとトークンの無駄遣い。一行ログ、リネーム一回、承認一回 |
| 段階的追加 | 問題が生じた時に必要な分だけ追加 |

---

*この記事の構成および執筆にClaudeを活用しています。*!
