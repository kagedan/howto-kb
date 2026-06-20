---
id: "2026-06-19-gemini-cliが6月18日でサービス終了antigravity-cliagyへの45分移行ガイ-01"
title: "Gemini CLIが6月18日でサービス終了：Antigravity CLI（agy）への45分移行ガイドとサイレント障害3つ"
url: "https://zenn.dev/yushiyamamoto/articles/antigravity-cli-gemini-cli-migration-2026-06"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "Gemini", "GPT"]
date_published: "2026-06-19"
date_collected: "2026-06-20"
summary_by: "auto-rss"
query: ""
---

2026-06-19 / 昨日（6月18日）、Google の Gemini CLI が個人向けサービスを終了した。後継は Antigravity CLI（バイナリ名：`agy`）――Go で書き直されたクローズドソースの新ツールだ。本稿は終了翌日時点で確認できる事実を整理し、**まだ移行が済んでいない場合の対処手順**と、予告なく壊れる3つのトラップをまとめる。

## 結論

| 論点 | 内容 |
| --- | --- |
| 誰が影響を受けるか | Google AI Pro・Ultra・個人向け無償 Code Assist ユーザー |
| エンタープライズは？ | Standard/Enterprise ライセンスまたは有償 API キー利用者は**対象外** |
| 移行時間の目安 | 対話利用のみなら約45分。CI/CD 含む場合は事前監査が必要 |
| 最大リスク | MCP `url` → `serverUrl` のサイレント障害・CI/CD パイプライン未更新 |
| クォータの変化 | 1,000リクエスト/日 → 週次コンピュートキャップ（リセット7日間） |

---

## 何が起きたか

Google は2026年5月19日（Google I/O）に、Gemini CLI の個人向けサービス終了を発表した。終了日は2026年**6月18日**。後継の Antigravity CLI は TypeScript 製だった旧ツールを Go で書き直したもので、バイナリ名は `agy`、現行バージョンは v1.0.1。

旧 Gemini CLI は Apache 2.0 のオープンソースで、104,000+ の GitHub スターと 6,000+ のコミュニティPRを集めていた。リポジトリは Linux Foundation に寄贈済みだが、Google のプロプライエタリバックエンドなしには動作しないため、オープン性は形骸化している。Antigravity CLI の公開リポジトリにはチェンジログと README と GIF のみ――アプリケーションコードは非公開だ。

---

## 影響範囲

**移行必須（6月18日でアクセス停止）:**

* Google AI Pro / Ultra ユーザー
* 個人向け無償 Gemini Code Assist ユーザー
* Gemini Code Assist for GitHub（新規組織インストール不可。既存リクエストも数週以内に停止）

**影響なし（移行不要）:**

* Gemini Code Assist Standard/Enterprise ライセンス保有者
* 有償 Gemini API キー・Gemini Enterprise Agent Platform 利用者

---

## 移行手順（5ステップ、約45分）

### Step 1: `agy` バイナリをインストール

```
# macOS / Linux
curl -fsSL https://antigravity.google/cli/install.sh | bash

# Homebrew
brew install --cask antigravity-cli

# Windows PowerShell
irm https://antigravity.google/cli/install.ps1 | iex
```

インストール直後に `agy doctor` を実行して環境を検証する。

### Step 2: 初回認証

`agy` 起動後に OAuth フローが走る。設定は `~/.gemini/antigravity-cli/settings.json` に自動保存される。

### Step 3: プラグインに変換

旧 "Extensions" が新 "Plugins" に改称。このコマンドで一括変換できる。

### Step 4: スキルフォルダを移動

```
# ワークスペーススキル
git mv .gemini/skills .agents/skills

# グローバルスキル
mv ~/.gemini/skills ~/.gemini/antigravity-cli/skills
```

コンテキストファイル `GEMINI.md` は `.antigravity.md` に変わるが、両方共存可能なため急ぎの改名は不要。

### Step 5: MCP 設定を書き直す

MCP 設定が `settings.json` インライン記述から独立ファイルに移動した。

```
移行前: ~/.gemini/settings.json 内にインライン記述
移行後: ~/.gemini/antigravity-cli/mcp_config.json
```

Step 5 後に `agy inspect` で MCP サーバーが正しく読み込まれているか確認する。

---

## サイレント障害3つ（ここが本番）

### 障害1: MCP `url` → `serverUrl` の改名（エラーが出ない）

リモート MCP サーバーの設定フィールドが `url` から `serverUrl` に変わった。**旧フィールド名のまま放置してもエラーは出ない**。起動時は正常に見え、実際にツールを呼び出した瞬間だけ失敗する。

```
// 旧（Gemini CLI）― 放置するとツール呼び出し時にサイレント失敗
{ "type": "remote", "url": "https://your-mcp.example.com" }

// 新（Antigravity CLI）― 正しい記述
{ "type": "remote", "serverUrl": "https://your-mcp.example.com" }
```

### 障害2: CI/CD パイプラインが自動更新されない

移行ツールはローカル設定のみを変換する。CI/CD・cron・Makefile から `gemini` バイナリを呼び出しているジョブは6月18日以降サイレントに動作停止する。

```
# org 全体で今すぐ grep して agy に置換する
grep -r "gemini " .github/workflows/
grep -r "gemini " .circleci/
grep -r "gemini " Makefile
grep -rn "gemini " scripts/
```

### 障害3: ACP stdio モードが未実装

`gemini --acp`（JSON-RPC インターフェース）は Discord・Slack・Teams のオーケストレーションブリッジで広く使われていたが、Antigravity CLI v1.0.1 時点で**未実装**（GitHub Issue #31 でトラック中）。

これはドロップイン移行ではなく、機能ロスだ。Issue #31 が解決するまで、該当ブリッジを使っている場合は Claude Code または OpenCode への切り替えを検討する。

---

## クォータの変化

旧 Gemini CLI の「1,000リクエスト/日（24時間リセット）」から、\*\*週次コンピュートキャップ（7日間サイクル）\*\*に変わった。

コミュニティ報告では、Pro ユーザーが約2,000行の生成後にキャップに達し、最大168時間（=1週間）クールダウンになる事例がある。軽度のインタラクティブ利用なら影響は軽微だが、毎日重量生成を行うユーザーには実質的なダウングレードだ。

対策は2つ: 重量タスクを1日に集中させず分散させること、週次キャップのない代替ツール（Claude Code・OpenCode 等）をバックアップに用意すること。

---

## 移行で得られるもの

* **非同期サブエージェント**: `/agent [task]` で最大5つの並列エージェントをバックグラウンド実行
* **マルチモデル**: `/model` で Gemini Family に加えて Claude Sonnet/Opus・GPT-OSS 120B を選択可能
* **Antigravity 2.0 デスクトップアプリとの共通ハーネス**: CLI 改善がデスクトップに即時反映

---

## 実装チェックリスト

---

## 失敗パターン

| パターン | 症状 | 原因 |
| --- | --- | --- |
| MCP サーバーが「見えるのにツールが動かない」 | ツール呼び出し時のみエラー | `url` → `serverUrl` 未修正 |
| CI/CD が6月18日以降に壊れた | `gemini: command not found` | パイプライン更新漏れ |
| API ブリッジが接続できない | 接続拒否 / undefined error | ACP stdio モード未実装 |
| 週の途中でクォータ切れ | 応答なし | 重量タスク集中によるキャップ到達 |

---

## 参考リンク
