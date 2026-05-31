---
id: "2026-05-30-openclaw-2026410入門-active-memorycodex統合mlx-voice完全-01"
title: "OpenClaw 2026.4.10入門 — Active Memory・Codex統合・MLX Voice完全ガイド"
url: "https://zenn.dev/kai_kou/articles/223-openclaw-2026-4-10-active-memory-codex-guide"
source: "zenn"
category: "claude-code"
tags: ["prompt-engineering", "API", "AI-agent", "OpenAI", "GPT", "zenn"]
date_published: "2026-05-30"
date_collected: "2026-05-31"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年4月11日、AIエージェントプラットフォーム OpenClaw がバージョン **2026.4.10** をリリースしました。多数の新機能とバグ修正を含む大型リリースで、今回の目玉は次の3つです。

* **Active Memory Plugin** — 会話前に自動でメモリを検索し関連コンテキストをプリロードする新プラグイン
* **Native Codex Integration** — `codex/gpt-*` を独立プロバイダーとして統合し、認証・スレッド管理・コンパクション対応
* **Local MLX Voice（実験的）** — macOS 上でローカル音声処理を実現するTalk Mode拡張

本記事では、公式ドキュメントとリリースノートをもとに、これら3つの主要機能の仕組みと設定方法を解説します。

### この記事で学べること

* OpenClaw 2026.4.10 の変更点全体像
* Active Memory Plugin の設定・動作原理・Context Modeの選び方
* Native Codex統合への移行手順
* Local MLX Voice の有効化方法
* SSRF 対策を含むセキュリティ強化の内容

### 対象読者

* OpenClaw を業務・個人プロジェクトで活用しているエンジニア
* AIエージェントのメモリアーキテクチャに興味がある方
* v2026.3.x 以前のバージョンからのアップグレードを検討している方

---

## TL;DR

* **Active Memory**: 会話前に自動でメモリサブエージェントを起動し、ユーザーが明示的に「検索して」と言わなくても関連コンテキストを取得
* **Native Codex**: `codex/gpt-*` プロバイダーが独立した認証・スレッド管理を持ち、`openai/gpt-*` との混用が可能に
* **MLX Voice**: macOS 限定、ローカルで音声処理を完結（実験的機能、デフォルト無効）
* **SSRF Hardening**: ブラウザ・サンドボックス・Docker CDP を対象に大幅なセキュリティ強化

---

## OpenClaw 2026.4.10 の主な変更点

| カテゴリ | 変更内容 |
| --- | --- |
| Memory | Active Memory Plugin（新規） |
| Model Integration | Codex プロバイダーのネイティブ化 |
| Voice | Local MLX Speech Provider（実験的） |
| Security | SSRF ハードニング、ツール実行検証強化 |
| Channels | Microsoft Teams ピン/リアクション操作、Matrix MSC4357 対応 |

---

## Active Memory Plugin の仕組み

### 従来のメモリとの違い

OpenClaw の既存メモリシステムは **リアクティブ型** でした。つまり、ユーザーや別のエージェントが明示的に `memory_search` を呼び出さない限り、過去の情報は参照されません。

Active Memory は **プロアクティブ型** を採用しています。

```
[従来] ユーザー入力 → メインエージェント返答
[2026.4.10以降] ユーザー入力 → ブロッキングメモリサブエージェント起動 → メインエージェント返答
```

公式ドキュメントの定義では、Active Memory は「eligible な会話セッションでメイン返答前に実行される、plugin が所有するブロッキングメモリサブエージェント」です。

### 動作条件

Active Memory が起動するには、次の4条件をすべて満たす必要があります。

1. プラグインが有効（`enabled: true`）
2. 対象エージェントID が設定に含まれる
3. チャットタイプが `allowedChatTypes` に含まれる
4. インタラクティブな永続セッションである

以下のケースでは **スキップ** されます。

* ヘッドレス実行
* バックグラウンドタスク
* サブエージェント内での実行
* ワンショットAPI呼び出し

---

## Active Memory の設定

`openclaw.json` の `plugins.entries` に以下を追加します。

```
{
  plugins: {
    entries: {
      "active-memory": {
        enabled: true,
        config: {
          agents: ["main"],
          allowedChatTypes: ["direct"],
          queryMode: "recent",
          promptStyle: "balanced",
          timeoutMs: 15000,
          maxSummaryChars: 220
        }
      }
    }
  }
}
```

### 主要パラメータ解説

| パラメータ | 型 | 説明 |
| --- | --- | --- |
| `agents` | `string[]` | Active Memory を有効にするエージェントID のリスト |
| `allowedChatTypes` | `string[]` | 対象チャットタイプ（`"direct"` / `"group"` / `"channel"`） |
| `queryMode` | `string` | コンテキストスコープ（後述） |
| `promptStyle` | `string` | 想起の積極度を制御（後述） |
| `timeoutMs` | `number` | メモリ検索のタイムアウト（ミリ秒） |
| `maxSummaryChars` | `number` | 取得するサマリーの最大文字数 |

### Context Mode の選び方

| Mode | 送信スコープ | 推奨 `timeoutMs` | 用途 |
| --- | --- | --- | --- |
| `message` | 最新ユーザー入力のみ | 3,000〜5,000ms | 速度最優先。好みや設定の想起に適する |
| `recent` | 最新メッセージ + 直近の履歴 | 15,000ms | バランス重視。フォローアップ質問に有効 |
| `full` | 会話全体 | 15,000ms以上 | 高品質想起が必要な長期会話 |

長期会話では `full` モードが最も精度が高い一方、処理時間が増加します。通常は `recent` から始めるのが推奨されています。

### Prompt Style の選び方

`promptStyle` は6種類あり、メモリ想起の積極度を調整します。

| スタイル | 説明 |
| --- | --- |
| `balanced` | 汎用デフォルト |
| `strict` | 隣接コンテキストへのブリードを最小化 |
| `contextual` | 会話履歴を考慮した継続性重視 |
| `recall-heavy` | 緩いマッチングで広く想起 |
| `precision-heavy` | 積極的に「結果なし」を選好 |
| `preference-only` | 習慣・好みの最適化 |

---

## ランタイム検査とデバッグ

Active Memory の動作はセッション中にリアルタイムで確認できます。

```
# ステータス確認（"Active Memory: ok 842ms recent 34 chars" のように表示）
/verbose on

# デバッグサマリー表示（想起されたコンテキストを確認）
/trace on

# プラグイン状態の切り替え
/active-memory status
/active-memory on
/active-memory off
```

セッション内での変更は一時的です。永続化する場合は `--global` フラグを使用します。

### トランスクリプトの永続化

デフォルトではメモリサブエージェントの実行ログは揮発性です。デバッグ目的で永続化するには次の設定を追加します。

```
{
  plugins: {
    entries: {
      "active-memory": {
        config: {
          persistTranscripts: true,
          transcriptDir: "active-memory"
        }
      }
    }
  }
}
```

保存先: `agents/<agent>/sessions/active-memory/session.jsonl`

`full` クエリモードでは急速にファイルが蓄積するため、定期的なクリーンアップが必要です。

---

## Native Codex Integration

### 変更の背景

これまで OpenClaw における Codex は、OpenAI 互換レイヤーの上に薄く重ねた「アドオン統合」でした。この方式では認証のずれや予期しない失敗が発生しやすく、長期スレッドでのコンテキスト管理にも課題がありました。

2026.4.10 では Codex を **ファーストクラスプロバイダー** として独立させ、専用のパスで管理するようになりました。

### モデルパスの変更

| 種別 | モデルパス |
| --- | --- |
| Codex（新） | `codex/gpt-*` |
| OpenAI 互換 | `openai/gpt-*` |

既存の `openai/gpt-*` パスは引き続き有効です。Codex 特有の機能（ネイティブスレッド、コンパクション、Codex認証）を使用する場合のみ `codex/gpt-*` に切り替えます。

### 移行ガイド

以前 Codex を使用していた設定は、モデルパスを変更するだけで移行できます。

```
// Before（旧設定）
{
  model: "openai-codex/gpt-5.4"
}

// After（新設定）
{
  model: "codex/gpt-*"
}
```

`codex/gpt-*` プロバイダーが提供する主な機能:

* **Codex管理認証**: OpenAI 認証とは独立したCodex専用の認証フロー
* **ネイティブスレッド**: Codex のスレッドAPIをそのまま利用
* **モデル自動検出**: `model_discovery` によって利用可能なモデルを動的に確認
* **コンパクション**: 長期会話でのコンテキスト圧縮

公式ブログでは「チャット・コーディング・長期実行を組み合わせるワークフローで発生していたドリフトや予期しない失敗が解消される」と説明されています。

---

## Local MLX Voice（実験的機能）

### 概要

OpenClaw の Talk Mode に、macOS 向けのローカル音声処理プロバイダー（MLX Speech Provider）が追加されました。これにより、音声処理をクラウドに送信せずに macOS 上でローカル完結させることが可能になります。

### 主な特徴

* **ローカル発話再生**: 音声をクラウドに送らずデバイス上で処理
* **プロバイダー選択**: セッション内で明示的にMLXプロバイダーを指定可能
* **割り込み処理**: 話し中に別の発話で割り込める
* **システムボイスへのフォールバック**: MLX処理が失敗した場合、自動でシステム音声に切り替え

### 注意事項

* **macOS 専用**（Windows・Linuxでは利用不可）
* **実験的機能**（デフォルト無効）
* MLX フレームワークの事前インストールが必要（Apple Silicon 推奨）

有効化はセッション内から:

またはグローバル設定:

```
{
  voice: {
    provider: "mlx"
  }
}
```

---

## セキュリティ強化（SSRF 対策）

2026.4.10 では、SSRF（Server-Side Request Forgery）に対する広範なハードニングが行われています。

### 主な対策内容

| 対象 | 変更内容 |
| --- | --- |
| ブラウザナビゲーション | リダイレクト先ホストの許可リスト適用 |
| サンドボックス | 外部リクエスト時のホスト名検証強化 |
| Docker CDP | コンテナ内の Chrome DevTools Protocol 通信を制限 |
| ツール実行 | `preflight` バリデーションの強化 |
| Exec Policy | 新しい `openclaw exec-policy` CLIで権限の監査・制御が可能に |

信頼済みのプライベートエンドポイントには `allowPrivateNetwork` 設定でオプトイン対応しています。

### exec-policy コマンド

```
# ツール実行権限の現在の状態を確認
openclaw exec-policy status

# 許可されているツールを一覧表示
openclaw exec-policy list
```

ブラウザ自動化ワークフローを運用している場合は、アップグレード後にリダイレクト設定を見直すことが推奨されています。

---

## チャンネル機能の更新

### Microsoft Teams

Teams チャンネルにピン・リアクション関連のアクションが追加されました。

| アクション | 説明 |
| --- | --- |
| ピン/アンピン | メッセージをチャンネル内でピン留め・解除 |
| リアクション | 絵文字リアクションの追加・一覧取得 |
| 既読マーク | メッセージを既読としてマーク |

### Matrix

Matrix チャンネルで MSC4357（ライブマーカー）に対応し、タイプライターアニメーションがより滑らかに動作するようになりました。

---

## まとめ

OpenClaw 2026.4.10 の主要な変更点をまとめます。

* **Active Memory Plugin**: 会話前に自動でメモリサブエージェントを起動し、関連コンテキストをプリロードする機能。`queryMode`（message/recent/full）と `promptStyle` で挙動を細かく調整可能
* **Native Codex Integration**: `codex/gpt-*` を独立プロバイダーとして統合。既存の `openai/gpt-*` パスはそのまま維持
* **Local MLX Voice（実験的）**: macOS 上でローカル音声処理を実現。プライバシー重視の環境で有効
* **SSRF Hardening**: ブラウザ・サンドボックス・Docker CDP にわたる広範なセキュリティ強化

Active Memory は長期会話を持つエージェントワークフローで即座に価値を発揮します。まず `recent` モード・`balanced` スタイルで試し、ユースケースに応じて調整していくのが推奨されます。

---

## 参考リンク
