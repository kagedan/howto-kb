---
id: "2026-05-20-claude-code-最新機能ガイド-vertex-ai連携とチームオンボーディングを解説-01"
title: "Claude Code 最新機能ガイド — Vertex AI連携とチームオンボーディングを解説"
url: "https://zenn.dev/kai_kou/articles/217-claude-code-vertex-ai-onboarding-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "API", "TypeScript", "zenn"]
date_published: "2026-05-20"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code v2.1.98〜v2.1.101（2026年4月リリース）では、エンタープライズチームの導入を大幅に簡略化する新機能が複数追加されました。[公式 Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) に掲載された主なアップデートは次の通りです。

* **Vertex AI セットアップウィザード** — `/setup-vertex` で GCP 認証から Claude Code 接続まで対話的に設定
* **`/team-onboarding` コマンド** — 新規メンバーのランプアップガイドを自動生成
* **Monitor ツール** — バックグラウンドスクリプトのイベントをリアルタイムストリーミング
* **サブプロセスサンドボックス** — Linux でのPID名前空間分離によるセキュリティ強化

この記事では、上記の各機能を実際のコマンドと設定例とともに解説します。

### この記事で学べること

* GCP Vertex AI 経由での Claude Code 接続方法
* `/team-onboarding` で新規メンバーのセットアップを自動化する手順
* Monitor ツールで長時間バックグラウンド処理を監視する方法
* サブプロセスサンドボックスの有効化と制御方法

### 対象読者

* Claude Code をチーム・組織に展開したい方
* GCP / Vertex AI 環境で Claude Code を利用したい方
* Claude Code のセキュリティ設定を強化したい方

### 前提条件

* Claude Code v2.1.101 以降（`claude --version` で確認）
* GCP アカウント（Vertex AI セクションのみ）

## TL;DR

* `/setup-vertex` で Vertex AI セットアップが対話ウィザード化 — 手動設定不要
* `/team-onboarding` で現在のプロジェクトに合ったランプアップドキュメントを自動生成
* `Monitor` ツールはバックグラウンドBashコマンドの stdout を逐次通知として受け取れる
* `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` でサブプロセスをPID名前空間分離（Linux限定）

---

## 機能1: Vertex AI セットアップウィザード

### 概要

Claude Code v2.1.98 以降、GCP の Vertex AI 経由で Claude モデルを利用する際の設定が対話型ウィザードに統一されました（[Claude Code on Google Vertex AI](https://code.claude.com/docs/en/google-vertex-ai)）。

これまでは環境変数の手動設定が必要でしたが、ウィザードがGCP認証・プロジェクト選択・リージョン設定・モデルピン留めを順に案内します。

### ウィザードの起動方法

**初回セットアップ:**

1. Claude Code 起動後、ログイン画面で「3rd-party platform」を選択
2. 「Google Vertex AI」を選択するとウィザードが自動起動

**設定変更（既存ユーザー向け）:**

セッション内でいつでも実行でき、GCP認証情報・プロジェクト・リージョン・モデルピンを変更可能です。

### ウィザードの設定ステップ

ウィザードは以下のステップを対話的に処理します。

```
[1] GCP Authentication
    → Application Default Credentials を使用するか、Service Account JSON を指定するか選択

[2] Project Configuration
    → GCP プロジェクトID を入力
    → プロジェクト内の Vertex AI が有効になっているか自動検証

[3] Region Selection
    → モデルが利用可能なリージョンを一覧表示して選択
    → 例: us-central1, europe-west4, asia-northeast1

[4] Credential Verification
    → 設定した認証情報と API 接続を自動テスト

[5] Model Pinning（任意）
    → claude-sonnet-4-6, claude-haiku-4-5 等の特定モデルに固定するかどうかを設定
```

### 環境変数による手動設定との比較

ウィザードを使わない場合の従来の手動設定:

```
# 手動設定（旧来の方法）
export CLAUDE_CODE_USE_VERTEX=1
export ANTHROPIC_VERTEX_PROJECT_ID="my-project-id"
export CLOUD_ML_REGION="us-central1"
export ANTHROPIC_MODEL="claude-sonnet-4-6"
```

ウィザードはこれらの設定を Claude Code の設定ファイル（`~/.claude/settings.json`）に自動で書き込むため、セッションをまたいで設定が保持されます。

---

## 機能2: `/team-onboarding` コマンド

### 概要

`/team-onboarding` は、現在のリポジトリ・プロジェクトでの Claude Code 利用状況を分析し、新規チームメンバー向けの「ランプアップガイド」を自動生成するコマンドです。

チームで Claude Code を本格導入した際、「どのようなプロンプトや設定を使っているか」「プロジェクト固有のワークフローは何か」を新規メンバーに伝えるドキュメント作成が省力化されます。

### 使い方

Claude Code はローカルの以下の情報を参照してガイドを生成します。

* `CLAUDE.md` / `.claude/` 内の設定・Skill定義
* `.clauderc`、`settings.json` の設定
* 直近の会話履歴・コマンド使用パターン
* MCP サーバー設定

### 生成されるガイドの内容例

```
# チームオンボーディングガイド — [プロジェクト名]

## Claude Code セットアップ
1. `npm install` でプロジェクト依存関係をインストール
2. `.env` ファイルを設定（テンプレート: `.env.example` を参照）
3. Claude Code の起動: `claude`

## このプロジェクトで利用しているカスタムコマンド
- `/review` — PRレビュー用のチェックリストを実行
- `/deploy-check` — デプロイ前の確認項目をすべてチェック
- `/db-schema` — データベーススキーマのサマリーを取得

## MCP サーバー設定
- **GitHub MCP**: PRの作成・レビューに利用
- **Slack MCP**: レビュー通知の自動投稿

## よく使うワークフロー
...（プロジェクトに応じた内容が自動生成）
```

### 活用シナリオ

| シナリオ | 効果 |
| --- | --- |
| 新規エンジニアの参画 | プロジェクト固有の Claude Code ワークフローを即座に把握 |
| チームメンバーへの横展開 | 属人的な利用ノウハウをドキュメント化 |
| オンコール引き継ぎ | 緊急対応時の Claude Code 操作手順を共有 |

---

## 機能3: Monitor ツール

### 概要

`Monitor` は、シェルコマンドを起動してその stdout をイベントストリームとして Claude Code のセッションに届ける新ツールです（v2.1.98 追加）。長時間スクリプトや `run_in_background` で起動したバックグラウンドプロセスの進行状況を逐次確認でき、自律エージェントが途中経過を観察しながら次のアクションを判断できます。

### ユースケース

```
長時間テストの監視
  └─ npm test をバックグラウンド実行 → Monitor でログを観察 → テスト失敗を自動検知・修正

ビルドパイプラインの追跡
  └─ docker build をバックグラウンド実行 → Monitor でビルドログを確認

外部API処理の待機
  └─ データ処理スクリプトをバックグラウンド実行 → Monitor で完了を待機
```

### 使用例

Claude Code へのプロンプト例:

```
テストスイートをバックグラウンドで実行して、
失敗したテストがあれば修正してください。
Monitor ツールで進行状況を追いながら対応してください。
```

この指示により Claude Code は:

1. `npm test` をバックグラウンド実行
2. Monitor ツールで stdout をストリーミング受信
3. テスト失敗を検知した場合、即座に該当コードの修正へ移行

### Monitor ツールの仕様

| 項目 | 内容 |
| --- | --- |
| 対応OS | すべてのプラットフォーム |
| 入力 | バックグラウンドプロセスのID |
| 出力 | stdout 行ごとの通知イベント |
| タイムアウト | プロセス終了まで待機（または手動キャンセル） |

---

## 機能4: サブプロセスサンドボックス（Linux）

### 概要

Claude Code v2.1.98 では、Linux環境でのサブプロセス実行に **環境変数スクラブ**と **PID 名前空間分離** が追加されました（[環境変数リファレンス](https://code.claude.com/docs/en/env-vars)）。環境変数スクラブがメイン機能であり、サブプロセスから認証情報などの機密環境変数を除去します。Linux ではさらに PID 名前空間分離も適用され、プロセスリストへのアクセスも制限されます。

### 有効化方法

```
export CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1
```

この環境変数を設定すると、Claude Code が起動するすべてのサブプロセスで機密環境変数がスクラブ（除去）されます。Linux 環境ではさらに PID 名前空間分離も適用されます。

### スクリプト実行回数の制限

```
# スクリプトごとにセッション中の実行上限を設定（JSON オブジェクト形式）
export CLAUDE_CODE_SCRIPT_CAPS='{"./scripts/deploy.sh": 2, "./scripts/test.sh": 50}'
```

`CLAUDE_CODE_SCRIPT_CAPS` にスクリプトパスをキー、実行上限回数を値とする JSON オブジェクトを設定できます。指定したスクリプトが上限回数を超えて実行されるのを防止するガードとして機能します。

### セキュリティ上の効果

| 保護対象 | 効果 |
| --- | --- |
| プロセスリスト | サブプロセスから他プロセスのPIDが不可視 |
| 環境変数 | スクラブにより親プロセスの機密環境変数を隔離 |
| スクリプト実行数 | 上限設定によりループ・大量実行を抑制 |

---

## 機能5: その他の主要アップデート

### OS CA 証明書ストアのデフォルト信頼（v2.1.101）

企業内の TLS インターセプトプロキシ（例: Zscaler, Netskope）使用時に、追加設定なしで Claude Code が通信できるようになりました。

```
# 以前: 企業証明書を手動で追加が必要
export NODE_EXTRA_CA_CERTS=/path/to/corp-cert.pem

# 現在: OS の証明書ストアを自動参照（デフォルト）
# 設定不要

# バンドル証明書のみに戻す場合
export CLAUDE_CODE_CERT_STORE=bundled
```

### デフォルト Effort レベルの変更（v2.1.94）

API キーユーザー・Bedrock/Vertex ユーザー・Team/Enterprise ユーザーのデフォルト effort が `medium` から `high` に変更されました。

```
# 現在のセッションの effort を変更
/effort low    # 速度優先
/effort medium # バランス
/effort high   # 品質優先（デフォルト）
```

### MCP ツール結果サイズの拡張（v2.1.91 追加、v2.1.98 でバグ修正）

MCP ツールが返す結果の最大サイズを500Kまで拡張できるようになりました。データベーススキーマや大規模ファイルツリーの取得に有効です。

MCP サーバー側での設定例（TypeScript SDK）:

```
// MCPレスポンスのメタデータに maxResultSizeChars を付与
return {
  content: [{ type: "text", text: largeSchema }],
  _meta: {
    "anthropic/maxResultSizeChars": 500000,
  },
};
```

---

## アップデート概要まとめ

| バージョン | 主な新機能 | リリース日 |
| --- | --- | --- |
| v2.1.92 | Bedrock セットアップウィザード・`/cost` 強化 | 2026年4月上旬 |
| v2.1.94 | デフォルト effort High 変更・Amazon Bedrock Mantle対応 | 2026年4月8日 |
| v2.1.98 | Vertex AI セットアップウィザード・Monitor ツール・サブプロセスサンドボックス | 2026年4月9日 |
| v2.1.101 | `/team-onboarding`・OS CA証明書ストア信頼 | 2026年4月11日 |

---

## まとめ

* **Vertex AI セットアップウィザード** (`/setup-vertex`) により、GCP環境への Claude Code 接続が手動設定不要の対話フローで完結するようになった
* **`/team-onboarding`** コマンドで、プロジェクト固有の Claude Code ワークフローをドキュメント化・共有する手間が大幅に削減された
* **Monitor ツール** でバックグラウンド処理のリアルタイム監視が可能になり、長時間タスクの自律実行精度が向上した
* **サブプロセスサンドボックス** により、Linux 環境でのセキュリティが PID 名前空間レベルで強化された

いずれも組織・チーム単位での Claude Code 展開を加速する機能であり、エンタープライズ利用での採用障壁を下げるアップデートといえます。

## 参考リンク
