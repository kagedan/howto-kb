---
id: "2026-05-27-anthropic公式プラグインsecurity-guidanceでclaude-codeのセキュリ-01"
title: "Anthropic公式プラグイン「security-guidance」でClaude Codeのセキュリティレビューを自動化する"
url: "https://zenn.dev/shirochan/articles/95c5c286beb5a3"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "Python", "zenn"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude Code でコードを書いているとき、セキュリティの観点でのレビューは後回しになりがちです。`pickle.load` の危険性を知っていても、実装に集中しているうちに書いてしまうことはあります。

`security-guidance` はそれを防ぐプラグインです。インストールするだけで、**コマンドを実行しなくても自動でセキュリティレビューが走る**という設計で、3つの層が連携して Claude が生成したコードを監視します。

<https://x.com/ClaudeDevs/status/2059385239781384341>

## security-guidance とは

`security-guidance` は [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) で公開されているAnthropicの公式プラグインです。

コマンドを持たず、**フックのみで動作**します。インストール後は意識せずとも以下の3層が自動で機能します。

| 層 | タイミング | 方式 | 概要 |
| --- | --- | --- | --- |
| Layer 1 | Edit/Write のたびに | 正規表現 | 約25種類の危険パターンを即時検出 |
| Layer 2 | ターン終了時 | LLM（Opus 4.7） | 差分全体をLLMがレビューし高リスクの指摘を返す |
| Layer 3 | git commit/push 時 | エージェント | コードベース横断でデータフローを追跡 |

<https://code.claude.com/docs/en/security-guidance>

<https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance>

## インストール

```
/plugin install security-guidance@claude-plugins-official
/reload-plugins
```

**前提条件:**

* Claude Code CLI ≥ v2.1.144
* Python 3.8+（`python3` / `python` / `py -3` のいずれかが PATH 上にあること）

## 3層の詳細

### Layer 1: パターン警告（正規表現）

`Edit` / `Write` / `MultiEdit` / `NotebookEdit` のたびに、変更内容を約25種類のルールと照合します。一致した場合は即座に警告メッセージを表示します。LLM呼び出しはなく、正規表現のみで動作するため遅延はありません。同じパターンはセッション中1ファイルにつき1回のみ警告するため、同じファイルへの繰り返し編集で警告が氾濫することはありません。

検出対象のパターン例:

| カテゴリ | 対象 |
| --- | --- |
| 安全でないデシリアライズ | `pickle.load`、`yaml.load()`、`torch.load(weights_only=False)`、`marshal.loads`、`shelve.open` など |
| XSS | `innerHTML`、`outerHTML`、`insertAdjacentHTML`、`document.write`、`dangerouslySetInnerHTML` |
| コマンドインジェクション | `child_process.exec`、`os.system()`、`subprocess` の `shell=True`、Go の `exec.Command("sh", "-c", ...)` |
| 暗号の誤用 | AES-ECB モード、IVなし暗号化（`createCipher`）、TLS 検証無効 |
| XML | 安全でないパーサー設定（XXE） |
| GitHub Actions | ワークフローへのユーザー入力の直接埋め込み |

### Layer 2: LLM差分レビュー（Stop フック）

Claude がターンを終了しようとしたとき（`Stop` イベント）、バックグラウンドで差分全体を Opus 4.7 に送ってレビューします。

動作の特徴:

* **バックグラウンド実行（asyncRewake）**: バックグラウンドで動作し、指摘が見つかった場合（exit code 2）のみ Claude に通知が届きます。通知内容はシステムリマインダーとして Claude に渡され、Claude が内容を受け取って対処します。指摘がなければ何も起きません
* 1ターンで変更されたファイルを最大30件まで対象とし、連続して最大3回まで実行されます
* `claude-security-guidance.md`（後述）の内容がプロンプトに付加され、プロジェクト固有のルールも反映されます

### Layer 3: エージェントコミットレビュー（git commit/push）

**Claude が Bash ツール経由で** `git commit` または `git push` を実行したとき、SDK 駆動のエージェントが起動します。ユーザーが自分のシェルから直接打ったコミットや、セッション内の `!` シェルエスケープ経由のコミットは対象外です。

このエージェントが Layer 1・2 と異なる点:

* `Read` / `Grep` / `Glob` ツールを使ってコードベースを横断的に調査
* 単一ファイルでは検出できない **複数ファイルにまたがる脆弱性**を検出（IDOR・認証バイパス・クロスファイル SSRF など）
* こちらも**バックグラウンド実行（asyncRewake）** で動作し、問題があった場合のみ報告

## カスタマイズ

### プロジェクト固有のルール（claude-security-guidance.md）

以下のいずれかのパスに `claude-security-guidance.md` を置くと、LLM差分レビューのプロンプトに追記されます:

| パス | スコープ |
| --- | --- |
| `~/.claude/claude-security-guidance.md` | ユーザー全体 |
| `<project>/.claude/claude-security-guidance.md` | プロジェクト（コミット推奨） |
| `<project>/.claude/claude-security-guidance.local.md` | プロジェクトローカル（`.gitignore` 推奨） |

3つすべてが読み込まれ、「ユーザー → プロジェクト → ローカル」の順に連結されます。合計が 8 KB を超えた場合はローカルから順に切り捨てられます。

記述例:

```
# Acme セキュリティルール

- `customers` / `orders` テーブルへの SELECT は `db.replica` 経由のみ。`db.primary` は書き込み専用
- バックグラウンドジョブはユーザーコンテキストの認証トークンを使わない。サービスアカウント認証は `jobs.get_service_account()` で取得する
- `requests.get(url)` に外部ユーザー制御の `url` を渡す場合は `acme.net.safe_request` の SSRFアローリストラッパーを必ず使う
```

> **注意**: このファイルはLLMプロンプトに埋め込まれるため、シークレット情報は記載しないでください。

### カスタムパターンルール（security-patterns.yaml）

`<project>/.claude/security-patterns.yaml`（または `.json`）を置くことで、独自の正規表現ルールを追加できます。ユーザー・プロジェクト・ローカルの3段階で最大50ルールまで定義可能です。なおビルトインのパターンは無効化できず、カスタムルールは追加のみです。

### 環境変数による制御

| 変数 | デフォルト | 説明 |
| --- | --- | --- |
| `SECURITY_GUIDANCE_DISABLE=1` | 未設定 | プラグイン全体を無効化 |
| `ENABLE_PATTERN_RULES=0` | 有効 | Layer 1（正規表現警告）を無効化 |
| `ENABLE_CODE_SECURITY_REVIEW=0` | 有効 | Layer 2・3（LLMレビュー全体）を無効化 |
| `ENABLE_STOP_REVIEW=0` | 有効 | Layer 2（Stopフック）のみ無効化 |
| `ENABLE_COMMIT_REVIEW=0` | 有効 | Layer 3（コミットレビュー）を無効化 |
| `SECURITY_REVIEW_MODEL` | `claude-opus-4-7` | Layer 2 に使うモデル |
| `SG_AGENTIC_MODEL` | 同上と同じ | Layer 3 に使うモデル |
| `SG_DUAL_OR=on` | 未設定 | Layer 2 を2並列で実行し結果をマージ（高再現率モード） |

## モデルの指定

デフォルトは `claude-opus-4-7` です。Bedrock / Vertex / LLM ゲートウェイを使う場合はプロバイダー固有の形式で指定します:

```
# 1P / API キー
SECURITY_REVIEW_MODEL=claude-opus-4-7

# Bedrock（推論プロファイル ID）
SECURITY_REVIEW_MODEL=us.anthropic.claude-opus-4-7

# Vertex（日付タグ形式）
SECURITY_REVIEW_MODEL=claude-opus-4-7@20260218
```

## プライバシーと送信データ

Layer 2・3 は外部のモデルエンドポイントにデータを送信します。送信内容:

* **Layer 2**: 変更されたファイルパス、差分ハンク、差分内のファイル内容
* **Layer 3**: Layer 2 の内容 + エージェントが `Read`/`Grep`/`Glob` で取得した関連ファイル

送信先は Claude Code の設定に依存します（Anthropic API / Bedrock / Vertex / LLM ゲートウェイなど）。

デバッグログは `~/.claude/security/log.txt` に記録されます（フルのファイル内容やプロンプトは含まれない。1 MB でローテート）。

## 注意点

* Layer 2・3 は git リポジトリ外ではスキップされます。Layer 1 のパターンチェックはリポジトリ外でも動作します。
* Layer 3（エージェントコミットレビュー）は現在 `claude-security-guidance.md` を読み込みません。プロジェクト固有のルールが反映されるのは Layer 2 のみです。
* 特定の指摘を抑制したい場合は、その行に「なぜ安全か」のコメントを書くとLLMレビューが除外対象として扱います。恒常的な除外は `claude-security-guidance.md` に記載します。
* このプラグインはあくまでベストエフォートの補助ツールです。SAST/DAST・依存関係スキャン・ペネトレーションテストの代替にはなりません。

## まとめ

`security-guidance` は「インストールして忘れる」設計のセキュリティレビュープラグインです。コマンドを覚える必要はなく、コーディング中に自動で3層のチェックが走ります。

Layer 1 が即時フィードバックを担い、Layer 2 がターン完了後に差分全体を精査し、Layer 3 がコミット時にコードベース横断の視点で見直すという役割分担により、単一の手法では見落とす脆弱性をカバーします。

---

**参考リンク**
