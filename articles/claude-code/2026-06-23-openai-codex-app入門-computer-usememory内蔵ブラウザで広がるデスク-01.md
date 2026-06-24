---
id: "2026-06-23-openai-codex-app入門-computer-usememory内蔵ブラウザで広がるデスク-01"
title: "OpenAI Codex App入門 — Computer Use・Memory・内蔵ブラウザで広がるデスクトップAIの全貌"
url: "https://zenn.dev/kai_kou/articles/239-codex-mac-computer-use-memory-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "OpenAI", "GPT", "zenn"]
date_published: "2026-06-23"
date_collected: "2026-06-24"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年4月16日、OpenAI は Codex App の大型アップデート（v26.415）をリリースしました。コーディングエージェントとして知られていた Codex App が、今回の更新で **デスクトップ全体を操作できる汎用AIエージェント** へと進化しています。

### この記事で学べること

* Codex App v26.415 の3大新機能（Computer Use・Memory・内蔵ブラウザ）の仕組み
* 複数エージェントをバックグラウンドで並列実行する方法
* 111個の新 Plugins と Thread Automations の活用法
* 前日リリースの CLI v0.121.0 の注目追加機能

### 対象読者

* OpenAI Codex を使って開発ワークフローを自動化したいエンジニア
* Claude Code など競合ツールと機能比較をしたい方
* AIエージェントによるデスクトップ操作（Computer Use）を実装したい方

### 前提環境

* macOS（Apple Silicon または Intel）
* ChatGPT Plus / Pro / Business / Edu / Enterprise プランのいずれか
* Codex App の最新版（v26.415 以降）

---

## TL;DR

* **Computer Use**: Codex が macOS のアプリを独自カーソルで操作。バックグラウンドで複数エージェントが並列実行でき、ユーザーの作業を妨げない
* **Memory（プレビュー）**: 過去のセッションから技術スタック・好み・ワークフローを記憶し、次回以降に自動活用
* **内蔵ブラウザ**: Atlas 技術基盤。localhost / 認証不要パブリックページをアプリ内で開き、レンダリング済みページにコメントして正確な指示を渡せる
* **111個の新 Plugins** を追加（CodeRabbit・GitLab Issues など）
* **Thread Automations**: 数日〜数週間の長期タスクを自律スケジューリング
* 週間アクティブユーザー 300万人を突破

---

## Codex App v26.415 の概要

Codex App はこれまで、コードの生成・リファクタリング・ドキュメント作成を中心とした「コーディング特化エージェント」として位置づけられてきました。v26.415 では、その枠を大きく超え **デスクトップ全体の操作・記憶・ブラウザアクセス** を統合した汎用エージェントプラットフォームへと変貌しています。

OpenAI は今回の更新を「Codex が Claude Code に対して競争優位を取り戻すための大型投資」と位置づけており、TechCrunch は「[OpenAI takes aim at Anthropic with beefed-up Codex](https://techcrunch.com/2026/04/16/openai-takes-aim-at-anthropic-with-beefed-up-codex-that-gives-it-more-power-over-your-desktop/)」と報じています。

### 主な変更サマリー

| カテゴリ | 内容 |
| --- | --- |
| Computer Use | macOS アプリの自律操作（カーソル・クリック・タイピング） |
| Memory | セッション横断の文脈記憶（プレビュー） |
| 内蔵ブラウザ | Atlas 基盤、ページへのコメント指示 |
| Image Generation | gpt-image-1.5 統合 |
| Plugins | 111個追加 |
| Thread Automations | 長期タスクの自律スケジューリング |
| PR Reviews | GitHub PR のサイドバー統合 |
| SSH（アルファ） | リモート devbox への接続 |
| Intel Mac 対応 | Apple Silicon に加えて Intel Mac をサポート |

---

## Computer Use — macOS アプリを自律操作

### 仕組み

Computer Use は Codex が「独自のカーソル」を持ち、macOS 上の任意のアプリを視覚認識・クリック・入力操作できる機能です。公式ドキュメントには次のように説明されています。

> Let Codex use macOS apps for GUI tasks, browser flows, and native app testing.  
> — [Codex App — OpenAI Developers](https://developers.openai.com/codex/app)

重要な点は、Codex エージェントがバックグラウンドで実行されるため、**ユーザー自身が他のアプリで作業しながら並列実行できる** ことです。

### 複数エージェントの並列実行

v26.415 の大きな強化点のひとつが、**複数エージェントを同時に走らせられる** マルチスレッドワークフローです。

* 異なるプロジェクトのタスクをエージェントごとに分離
* ワークツリー（worktrees）サポートにより、同一リポジトリで複数エージェントが衝突せずに作業
* 各エージェントは独立したコードのコピーで動作

### 活用例

```
# Codex に Slack と Google Calendar を解析させて
# 本日のタスクリストを自動生成させる例（概念）

"Codex、今日のSlackチャンネルとGoogleCalendarを確認して、
優先度順のタスクリストをNotionに作成してください"
```

TechCrunch の報道によれば、Codex は Slack チャンネルの解析と Google Calendar の確認を組み合わせて、日次タスクリストを自動生成できるとされています。

### 留意事項

* Computer Use 機能はプレビュー段階のため、すべての macOS アプリで動作する保証はない
* **macOS 限定**（EU・UK は現時点で未対応）。Windows・Linux は今後対応予定

---

## Memory — セッションを超えた文脈記憶

### 概要

Memory 機能（プレビュー）は、Codex が過去のセッションから以下の情報を記憶し、次回以降のタスクに自動活用する仕組みです。

* 個人の技術スタック（使用言語・フレームワーク・ライブラリ）
* コーディングの好みやスタイルガイド
* 過去に収集した情報や確認事項
* 繰り返し実行するワークフローの手順

ChatGPT の Memory 機能と同一の仕組みを Codex に適用したものであり、[9to5Mac の記事](https://9to5mac.com/2026/04/16/openais-codex-app-adds-three-key-features-for-expanding-beyond-agentic-coding/) によれば「以前のセッションから有用なコンテキストを記憶し、個人の好みや修正、収集に時間がかかった情報を保持できる」と説明されています。

### Thread Automations との連携

Memory と組み合わせることで、Thread Automations（後述）が強力になります。

* 過去の文脈を引き継いでタスクを数日後に再開
* 週次定例のコードレビューを Codex がスケジュール管理
* 長期プロジェクトの進捗を自律追跡

### Memory の管理

CLI v0.121.0 では Memory の削除コントロールが追加されています。

v0.121.0 のリリースノートでは「Memory の削除コントロール」機能の追加が明記されています。正確なコマンド構文は[公式 CLI リファレンス](https://developers.openai.com/codex/cli/reference)で確認してください。

---

## 内蔵ブラウザ — Atlas 技術基盤

### 機能概要

内蔵ブラウザは OpenAI の Atlas 技術をベースに構築されています。現時点では以下のページをアプリ内で開けます。

* **localhost ウェブアプリ**（開発中のフロントエンドなど）
* **サインイン不要のパブリックページ**

最大の特徴は、**レンダリング済みのページにコメントを書き込み、そのコメントを Codex への指示として直接渡せる** 点です。

```
# 開発中のダッシュボードを開き、
# グラフの配色が仕様と違う箇所にコメントを付けて
# Codex に修正させる例（概念）

1. ブラウザで http://localhost:3000 を開く
2. 問題箇所に「このグラフのバーカラーを #3B82F6 に変更」とコメント
3. Codex が自動的に該当コードを修正・プルリクエストを作成
```

### 今後の拡張予定

TechCrunch の取材によれば、現在は localhost アプリに限定されていますが、「ブラウザ自動化はプレビュー段階であり、今後特定アプリケーション外にも拡張予定」とされています。

---

## Image Generation — gpt-image-1.5 統合

Codex App 内に gpt-image-1.5 による画像生成機能が統合されました。これにより、プロダクト開発の以下のシーンでアプリ切替不要になります。

* **モックアップ**: UI/UX デザインのラフスケッチ生成
* **プロダクトコンセプト**: アイデアの視覚化
* **ドキュメント用図解**: アーキテクチャ・フロー図の自動生成

---

## 111個の新 Plugins — エコシステムの拡張

v26.415 で 111個の Plugins が新たに追加されました。

### 注目 Plugins

| Plugin | カテゴリ | 用途 |
| --- | --- | --- |
| CodeRabbit | コードレビュー | AI駆動のPRレビュー自動化 |
| GitLab Issues | タスク管理 | GitLab Issue からの自動タスク生成 |
| MCP サーバー連携 | 拡張性 | 任意のMCPサーバーをCodexから操作 |

### Plugins の構成

Codex Plugins は **Skills・アプリ統合・MCP サーバー** の3つを組み合わせてバンドルできます。[公式ドキュメント](https://developers.openai.com/codex/app)には「Connect apps, skills, and MCP servers to extend what Codex can do」と説明されています。

### Marketplace からのインストール

CLI v0.121.0 では Marketplace からの Plugin インストールが複数ソースから可能になりました。

```
# CLI から Marketplace Plugin をインストール（v0.121.0以降）
codex marketplace add <github-url-or-local-path>

# TUI 内でインストール済み Plugin 一覧を確認
# codex 起動後に /plugins を入力
```

---

## Thread Automations — 長期タスクの自律スケジューリング

Thread Automations を使うと、Codex が **数日〜数週間にわたる長期タスクを自律的にスケジュール管理** できます。

### 主な機能

* **スケジュール実行**: 指定時刻に自動起動してタスクを再開
* **コンテキスト保持**: 既存の会話スレッドを引き継いで実行
* **進捗追跡**: 長期プロセスのチェックインを自動実施

### 活用例

```
# 週次リグレッションテスト自動化（概念）
"毎週月曜 9:00 に main ブランチのリグレッションテストを実行し、
失敗があれば GitHub Issue を自動作成してください"
```

---

## その他の注目機能

### Pull Request Reviews

GitHub のプルリクエストを Codex のサイドバーで確認し、レビューコメントに対応するコード修正を Codex に依頼できます。TUI では `/review` スラッシュコマンドで PR レビューを起動できます。

### SSH リモート接続（アルファ）

リモートの devbox に SSH 接続し、ローカルと同様に Codex を利用できます。クラウド上の開発環境への対応が広がります。

### Artifact Viewer

PDF・スプレッドシートなどの生成ファイルをサイドバーでプレビューしてからシェアできます。

---

## Codex CLI v0.121.0 の注目追加

前日（2026-04-15）にリリースされた CLI v0.121.0 の主要追加機能です。

| 機能 | 概要 |
| --- | --- |
| Marketplace Plugin インストール | 複数ソースから Plugin を取得 |
| TUI ヒストリー（逆引き検索） | セッション履歴を Ctrl+R で検索 |
| Memory モード管理 | Memory の確認・削除操作 |
| bubblewrap セキュアコンテナ | Linux サンドボックスの強化 |
| 並列 MCP ツール呼び出し | MCP/Plugin の並列実行サポート |

---

## 料金・プラン

Codex App は以下のプランに含まれます。

| プラン | 月額 | Codex 利用枠 |
| --- | --- | --- |
| ChatGPT Plus | $20 | 標準枠 |
| ChatGPT Pro | $100 | Plus の 5倍（期間限定プロモーション中 10倍、〜2026/5/31） |
| Business / Edu / Enterprise | 要問合せ | 組織単位 |

---

## まとめ

Codex App v26.415 は、コーディングエージェントとしての枠を超え、**macOS 全体を自律操作できるデスクトップ AI エージェント** への転換点です。

* **Computer Use**: Codex が独自カーソルで macOS アプリを並列操作
* **Memory**: 過去セッションの文脈を引き継いだ長期エージェント実行
* **内蔵ブラウザ**: ページコメントによる精密な指示伝達
* **111 Plugins 追加**: Skills + MCP + アプリ統合の自由な組み合わせ

Anthropic の Claude Code や Cursor との競合が激化する中、OpenAI の Codex は「コード生成ツール」から「デスクトップ全体の自律エージェント」へと明確なポジション変更を打ち出しています。

### 次のステップ

---

## 参考リンク
