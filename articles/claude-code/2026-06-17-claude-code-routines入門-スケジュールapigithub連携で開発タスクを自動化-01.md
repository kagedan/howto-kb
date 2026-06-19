---
id: "2026-06-17-claude-code-routines入門-スケジュールapigithub連携で開発タスクを自動化-01"
title: "Claude Code Routines入門 — スケジュール・API・GitHub連携で開発タスクを自動化する"
url: "https://zenn.dev/kai_kou/articles/236-claude-code-routines-desktop-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "zenn"]
date_published: "2026-06-17"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年4月14〜15日、Anthropic は Claude Code に2つの大きなアップデートを投入しました。

1. **Routines（ルーティン）**: スケジュール・API・GitHubイベントで Claude Code タスクを自動実行する仕組み
2. **デスクトップアプリの刷新**: 並列セッション管理を軸にした全面リデザイン

本記事では、これらの機能の概要・設定方法・ユースケースを公式ドキュメントをもとに解説します。

### この記事で学べること

* Claude Code Routines の仕組みと3種類のトリガー
* スケジュール・GitHub・API 各トリガーの設定手順
* プラン別の利用制限
* デスクトップアプリ刷新の主要な新機能

### 対象読者

* Claude Code を日常的に使っているエンジニア
* CI/CD パイプラインや定期タスクの自動化に興味がある方
* 複数リポジトリを並行開発している方

## TL;DR

* **Routines** = プロンプト + リポジトリ + コネクタを1セットにした Claude Code 自動化機能
* スケジュール（毎時〜週次）、GitHub イベント、API の3トリガーに対応
* クラウド実行のためラップトップを開いたままにする必要なし
* 利用制限: Pro 5回/日、Max 15回/日、Team/Enterprise 25回/日
* デスクトップアプリは並列セッション・統合ターミナル・ドラッグ&ドロップレイアウトに対応

---

## Claude Code デスクトップアプリ刷新

Routines の理解の前に、同時にリリースされたデスクトップアプリの刷新を押さえておきます。

### 並列セッション管理サイドバー

新しいサイドバーでは、アクティブなセッションと最近のセッションを一覧管理できます。

* **フィルタ機能**: ステータス・プロジェクト・環境で絞り込み可能
* **グループ化**: プロジェクト別にグループ化して整理
* **即時移動**: 複数リポジトリの作業中に結果を確認しながら素早く切り替え可能

### ドラッグ&ドロップレイアウト

すべてのペイン（ターミナル・プレビュー・Diffビューア・チャット）がドラッグ&ドロップで自由配置できます。作業スタイルに合わせたグリッドレイアウトを組めます。

### 統合ターミナル・ファイルエディタ・Diffビューア

| ツール | 機能 |
| --- | --- |
| 統合ターミナル | テスト・ビルドをセッションと並行実行 |
| インアプリファイルエディタ | スポット編集を IDE を切り替えずに実施 |
| 高速 Diff ビューア | 大規模変更セットでもパフォーマンス低下なし |
| 拡張プレビュー | HTML ファイル・PDF をアプリ内で開ける |

---

## Routines とは

[公式ブログ](https://claude.com/blog/introducing-routines-in-claude-code)によると、Routines は次のように定義されています。

> A routine is a Claude Code automation you configure once — including a prompt, a repo, and any relevant connectors — and then run on a schedule, fire from an API call, or trigger off a GitHub event.

一度設定すれば、スケジュール・API・GitHub イベントで繰り返し実行できる Claude Code 自動化の単位です。

### 重要な特徴: クラウド実行

Routines は **Claude Code のウェブインフラ上で動作** します。ローカルの Mac やラップトップを開いたままにしておく必要はありません。夜間バッチ処理や CI 連携に適しています。

### 構成要素

| 構成要素 | 内容 |
| --- | --- |
| プロンプト | Claude に指示する自然言語の指示文 |
| リポジトリ | 対象とする GitHub リポジトリ |
| コネクタ | Slack・GitHub 等の外部サービス連携 |
| トリガー | 実行タイミングの定義（後述） |

---

## 3種類のトリガー

### 1. Schedule トリガー

定期実行スケジュールを設定します。[公式ドキュメント](https://code.claude.com/docs/en/routines)によると、プリセットとして次の頻度が選べます。

| 頻度 | 説明 |
| --- | --- |
| hourly | 毎時実行 |
| daily | 毎日1回実行 |
| weekdays | 平日（月〜金）毎日実行 |
| weekly | 週1回実行 |

**ユースケース例**: 毎晩の Issue トリアージ、週次ドキュメントチェック、毎朝のビルド確認

```
# 例: 週次ドキュメントドリフトチェックのプロンプト
merged PR を過去1週間分スキャンして、変更された API を参照している
ドキュメントを特定し、更新 PR をドキュメントリポジトリに作成してください。
```

### 2. GitHub トリガー

GitHub リポジトリのイベントに反応して実行されます。

**設定項目**:

* 対象リポジトリ
* 反応するイベント（PR 作成、Issue オープン 等）
* フィルタ条件（ラベル・ブランチ名等）

マッチする条件ごとに新しいセッションが作成され、ルーティンが実行されます。

**ユースケース例**:

* 新しい PR が作成されたら自動コードレビューを実行
* Issue にラベルが付与されたらトリアージコメントを投稿
* マージ後に関連ドキュメントの更新 PR を自動作成

### 3. API トリガー

ルーティンに専用の HTTP エンドポイントが割り当てられます。外部の CI/CD パイプラインや Webhook から呼び出せます。

[公式 API ドキュメント](https://platform.claude.com/docs/en/api/claude-code/routines-fire)によると、エンドポイントへの POST リクエストでルーティンを起動します。

```
curl -X POST "https://api.anthropic.com/v1/claude_code/routines/{routine_id}/fire" \
  -H "Authorization: Bearer {routine_token}" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -H "Content-Type: application/json" \
  -d '{"text": "deploy completed on staging"}'
```

レスポンスにはセッション ID と URL が含まれ、実行状況を追跡できます。

**ユースケース例**:

* CD パイプラインのデプロイ完了後にスモークテストを実行
* 外部監視サービスのアラートを受信して自動調査
* Slack コマンドから定型の調査タスクを起動

---

## プラン別利用制限

Routines の1日あたりの実行回数はプランによって異なります。[公式ドキュメント](https://code.claude.com/docs/en/routines)より:

| プラン | 1日の実行上限 |
| --- | --- |
| Pro | 5回 |
| Max | 15回 |
| Team | 25回 |
| Enterprise | 25回 |

!

**注意点**:

* Routines の実行は、通常のインタラクティブセッションと同様にサブスクリプションの使用量を消費します
* 上限超過分は追加料金（従量課金）が発生する場合があります（追加使用が有効な場合）
* 利用には **Claude Code on the web** が有効であることが必要です

---

## 実践ユースケース

公式ドキュメントに記載されている代表的な活用パターンを紹介します。

### バックログ管理の自動化

```
# プロンプト例
新しく作成された Issue を毎晩スキャンし、以下を実施してください:
1. カテゴリに応じたラベルを付与
2. 担当チームにアサイン
3. 翌朝の Slack チャンネルに優先度付きサマリーを投稿
```

* **トリガー**: Schedule（daily）
* **コネクタ**: GitHub, Slack

### ドキュメントドリフトの検知

```
# プロンプト例
先週マージされた PR をスキャンし、変更されたコードの API を参照している
ドキュメントを特定して、更新が必要なファイルにコメント付きの Update PR を作成してください。
```

* **トリガー**: Schedule（weekly）
* **コネクタ**: GitHub

### デプロイ後の自動検証

```
# プロンプト例
ステージング環境への最新デプロイに対してスモークテストを実行し、
異常を検出した場合は担当エンジニアに Slack で通知してください。
```

* **トリガー**: API（CD パイプラインから POST）
* **コネクタ**: GitHub, Slack

---

## Routines の設定手順

1. [code.claude.com](https://code.claude.com) にアクセスしてサインイン
2. 左サイドバーの **Routines** を選択
3. **New Routine** をクリック
4. プロンプト・リポジトリ・コネクタを設定
5. **Select a trigger** でトリガー種別を選択（複数選択可）
6. スケジュール / GitHub イベント / API のいずれかを設定
7. **Save** で保存 → API トリガーの場合は保存後に URL とトークンが生成される

---

## まとめ

Claude Code の Routines と デスクトップアプリ刷新のポイントをまとめます。

### Routines

* プロンプト + リポジトリ + コネクタをセットにした自動化の単位
* スケジュール・GitHub イベント・API の3種類のトリガーに対応
* クラウド実行のため、ローカル環境への依存なし
* Pro 5回/日 〜 Enterprise 25回/日の利用制限

### デスクトップアプリ刷新

* 並列セッションのサイドバー管理
* ドラッグ&ドロップによる自由なペイン配置
* 統合ターミナル・ファイルエディタ・高速 Diffビューア・HTML/PDF プレビュー

複数リポジトリを並行開発している場合や、Issue トリアージ・ドキュメント更新・デプロイ後検証などの定型タスクを自動化したい場合に、Routines は特に有効です。

## 参考リンク
