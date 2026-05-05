---
id: "2026-05-03-claude-code-hooks完全ガイドslack連携lint自動化push前チェックの実装レシ-01"
title: "Claude Code Hooks完全ガイド──Slack連携・Lint自動化・Push前チェックの実装レシピ"
url: "https://zenn.dev/kai_kou/articles/024-claude-code-hooks-slack-lint-push-guide"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-03"
date_collected: "2026-05-05"
summary_by: "auto-rss"
---

## はじめに

Claude Codeの**Hooks**は、特定のイベントに応じてスクリプトを自動実行する仕組みです。「タスクが完了したらSlackに通知」「ファイルを編集したらLintを自動実行」「git push前に未コミット変更を警告」といった自動化を、settings.jsonにスクリプトを登録するだけで実現できます。

Hooksを使いこなすと、Claude Codeとの協業で発生しがちな3つの問題が解消されます。

| 課題 | Hooksでの解決 |
| --- | --- |
| タスク完了に気づかずPCの前で待機 | Slack通知で完了を把握、スマホからリアクションで次指示 |
| 編集後のLint/構文エラーの見落とし | 編集直後に自動チェック、エラーは即座にフィードバック |
| git push前のチェック漏れ | push検出時に自動で未コミット変更・高リスクファイルを警告 |

この記事では、Hooksの基本概念から、**Slack連携**・**Lint自動チェック**・**Push前安全チェック**の3つの実装レシピまでを体系的に解説します。

### この記事で学べること

* Hooksのイベント駆動モデルとsettings.jsonの設定方法
* Slack連携通知の実装（Keychain安全管理込み）
* PostToolUseによるLint自動チェックの実装
* PreToolUseによるPush前安全チェックの実装
* 無限ループ防止・トークン管理などの注意点

### 前提環境

| 項目 | 要件 |
| --- | --- |
| OS | macOS 13.0+（Keychain使用。Linux/WSLは代替手段あり） |
| Claude Code | インストール済み・認証済み |
| jq | 1.6以上（`brew install jq`） |
| Slack | ワークスペースへのアクセス権（Slack連携の場合） |

## TL;DR

1. Hooksは`settings.json`の`hooks`フィールドに**イベント名 + スクリプトパス**を書くだけで設定できる
2. 最初に入れるべき3つ: **Slack通知（Stop）**、**Lint自動チェック（PostToolUse）**、**Push前チェック（PreToolUse）**
3. **exit codeで動作制御**: `0`=成功、`1`=エラー（コンテキストに追加）、`2`=ブロック（実行中断）

---

## 1. Hooksの基本概念

### イベント駆動モデル

Hooksは、Claude Codeの実行ライフサイクル中に発生する**イベント**をトリガーとしてスクリプトを実行します。

```
  ユーザー入力
      │
      ▼
  ┌──────────────────┐
  │ UserPromptSubmit │  ← プロンプト送信時
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐     ┌───────────────┐
  │  PreToolUse      │────▶│  ツール実行   │
  │ (検証・ブロック) │     │ (Read/Edit等) │
  └──────────────────┘     └───────┬───────┘
                                   │
                                   ▼
                           ┌──────────────────┐
                           │  PostToolUse     │  ← Lint・後処理
                           └───────┬──────────┘
                                   │
                     ┌─────────────┴────────────┐
                     ▼                          ▼
             ┌──────────────┐          ┌──────────────────┐
             │    Stop      │          │  Notification    │
             │ (Slack通知等)│          │ (macOS通知等)    │
             └──────────────┘          └──────────────────┘
```

### よく使う5つのイベント

| イベント | タイミング | 主な用途 |
| --- | --- | --- |
| **PreToolUse** | ツール実行前 | 検証・ブロック・事前チェック |
| **PostToolUse** | ツール実行後 | フォーマット・Lint・後処理 |
| **Stop** | 停止時 | 完了通知・Slack投稿 |
| **Notification** | 通知発生時 | macOS通知・外部連携 |
| **SessionStart** | セッション開始時 | コンテキスト初期化・再注入 |

上記以外にも、UserPromptSubmit、PermissionRequest、PostToolUseFailure、SubagentStart、SubagentStop、TeammateIdle、TaskCompleted、InstructionsLoaded、ConfigChange、WorktreeCreate、WorktreeRemove、PreCompact、SessionEndなど合計18のイベントが用意されています。最初から全部使う必要はなく、課題が出てきたタイミングで追加していく進め方が推奨されます。

### settings.jsonでの設定方法

Hooksは`~/.claude/settings.json`（グローバル）または`.claude/settings.json`（プロジェクト単位）で定義します。

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/slack-feedback.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/post-edit-lint.sh"
          }
        ]
      }
    ]
  }
}
```

**設定項目の説明**:

| 項目 | 説明 | 例 |
| --- | --- | --- |
| `type` | フック実行方式。`"command"`（bashスクリプト）、`"prompt"`（LLM判断）、`"agent"`（サブエージェント）、`"http"`（Webhookポスト）、`"mcp_tool"`（MCPツール呼び出し） | `"command"` |
| `command` | 実行するコマンド（`type: "command"` 時。絶対パス推奨） | `"bash ~/.claude/hooks/my-hook.sh"` |
| `matcher` | ツール名のフィルタ（正規表現対応） | `"Edit|Write"` |

### exit codeによる動作制御

Hookスクリプトのexit codeによって、Claude Codeの次の動作が変わります。

| exit code | 意味 | Claude Codeの動作 |
| --- | --- | --- |
| `0` | 正常 | 実行を続行。stdoutはClaude Codeのコンテキストに追加される |
| `2` | ブロック | 実行を中断。stderrの内容がClaude Codeへのフィードバックとして渡される |
| その他 | エラー | stderrをログ記録するが、Claudeのコンテキストには渡されない |

---

## 2. 実装レシピ①: Slack連携通知

タスク完了時にSlackへ自動投稿し、絵文字リアクションで次の指示を受け取る仕組みです。

### 動作フロー

```
Claude Code停止 → slack-feedback.sh起動
    → Keychainからトークン取得
    → Slack APIで完了通知を投稿
    → フィードバック待機（1分→3分→5分）
    → ユーザーがリアクション（👍など）
    → リアクションを指示に変換してClaude Codeに渡す
```

### settings.json設定

```
{
  "hooks": {
    "Stop": {
      "type": "command",
      "command": "bash ~/.claude/hooks/slack-feedback.sh"
    }
  }
}
```

### スクリプトの実装

```
#!/bin/bash
# ~/.claude/hooks/slack-feedback.sh

# 1. セッション情報を取得
PROJECT_NAME=$(basename $(pwd))
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# 2. Keychainからトークンを安全に取得
SLACK_TOKEN=$(security find-generic-password \
  -a "claude-code" \
  -s "slack-bot-token" \
  -w 2>/dev/null)

if [ -z "$SLACK_TOKEN" ]; then
  echo "Slack Token未設定。Keychainに登録してください。" >&2
  exit 1
fi

# 3. Slack投稿（jqでJSONを安全に構築。プロジェクト名に引用符等が含まれてもエスケープされる）
MESSAGE="[${PROJECT_NAME}] タスク完了 (${TIMESTAMP})\nフィードバックをお待ちしています..."
PAYLOAD=$(jq -n \
  --arg channel "#your-channel" \
  --arg text "$MESSAGE" \
  '{channel: $channel, text: $text}')
RESPONSE=$(curl -s -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer ${SLACK_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# 4. メッセージIDを取得してフィードバック待機
MESSAGE_ID=$(echo $RESPONSE | jq -r '.ts')
# ... フィードバック待機ロジック（省略）
```

### リアクション→指示の変換マッピング

Slack通知メッセージにリアクションを付けると、対応する指示がClaude Codeに自動送信されます。

| リアクション | 意味 | 変換後の指示 |
| --- | --- | --- |
| 👍 | LGTM | コミット&プッシュを実行 |
| 👀 | レビュー依頼 | コードレビューを開始 |
| 🔁 | やり直し | タスクをやり直す |
| ❌ | 破棄 | 変更を破棄 |
| 🚀 | テスト実行 | テストを実行 |

スレッド返信でも自然言語での指示が可能です。

### Slackトークンの安全な管理

macOS Keychainを使った安全な管理方法は以下の通りです。

**Step 1: Keychainにトークンを登録**

```
security add-generic-password \
  -a "claude-code" \
  -s "slack-bot-token" \
  -w "xoxb-your-token-here" \
  -T "" \
  ~/Library/Keychains/login.keychain-db
```

**Step 2: スクリプトからKeychainのトークンを取得**

```
SLACK_TOKEN=$(security find-generic-password \
  -a "claude-code" \
  -s "slack-bot-token" \
  -w 2>/dev/null)
```

**MCP経由の代替手段**:

MCP（Model Context Protocol）経由でSlack連携する場合はOAuth認証でトークン管理が自動化されるため、Keychain設定は不要です。

```
claude mcp add --transport http slack https://mcp.slack.com
```

---

## 3. 実装レシピ②: Lint自動チェック

ファイル編集後に構文チェックを自動実行し、エラーを即座に検出する仕組みです。

### settings.json設定

```
{
  "hooks": {
    "PostToolUse": {
      "type": "command",
      "command": "bash ~/.claude/hooks/post-edit-lint.sh",
      "matcher": "Edit|Write"
    }
  }
}
```

`matcher`に`"Edit|Write"`を指定することで、EditツールまたはWriteツールの実行後にのみLintが動作します。

### スクリプトの実装

```
#!/bin/bash
# ~/.claude/hooks/post-edit-lint.sh

# stdinからツール情報をJSON形式で受け取る
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# ファイル拡張子で処理を分岐
case "${FILE_PATH##*.}" in
  md)
    # YAMLフロントマターの閉じチェック
    if head -n 1 "$FILE_PATH" | grep -q "^---$"; then
      if ! sed -n '2,/^---$/p' "$FILE_PATH" | grep -q "^---$"; then
        echo "YAMLフロントマターが閉じられていません: $FILE_PATH"
        exit 1
      fi
    fi
    ;;
  sh|bash)
    # Shell構文チェック
    if ! bash -n "$FILE_PATH" 2>/dev/null; then
      echo "Shell構文エラー: $FILE_PATH"
      bash -n "$FILE_PATH"
      exit 1
    fi
    ;;
  json)
    # JSON構文チェック
    if ! jq empty "$FILE_PATH" 2>/dev/null; then
      echo "JSON構文エラー: $FILE_PATH"
      jq empty "$FILE_PATH"
      exit 1
    fi
    ;;
esac

echo "Lint OK: $FILE_PATH"
```

### エラー時の動作

構文エラーが検出されるとHookが`exit 1`を返し、エラー情報がClaude Codeのコンテキストに追加されます。Claude Codeはエラー内容を参照して自動的に修正を試みます。

---

## 4. 実装レシピ③: Push前安全チェック

`git push`コマンド実行前に、未コミット変更や高リスクファイルをチェックして警告する仕組みです。

### settings.json設定

```
{
  "hooks": {
    "PreToolUse": {
      "type": "command",
      "command": "bash ~/.claude/hooks/pre-push-check.sh",
      "matcher": "Bash"
    }
  }
}
```

### スクリプトの実装

```
#!/bin/bash
# ~/.claude/hooks/pre-push-check.sh

INPUT=$(cat)
BASH_COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# git pushコマンドのみ対象
if [[ ! "$BASH_COMMAND" =~ git.*push ]]; then
  exit 0
fi

# 未コミット変更チェック
UNCOMMITTED=$(git status --short)
if [ -n "$UNCOMMITTED" ]; then
  echo "未コミット変更があります:"
  echo "$UNCOMMITTED"
fi

# プッシュ対象コミット取得
CURRENT_BRANCH=$(git branch --show-current)
COMMITS=$(git log "origin/${CURRENT_BRANCH}..HEAD" --oneline 2>/dev/null)
if [ -n "$COMMITS" ]; then
  echo "プッシュ対象コミット:"
  echo "$COMMITS"
fi

# 高リスクファイル変更チェック
HIGH_RISK=$(git diff "origin/${CURRENT_BRANCH}..HEAD" --name-only 2>/dev/null \
  | grep -E '\.(env|secret|key|pem)$')
if [ -n "$HIGH_RISK" ]; then
  echo "高リスクファイルの変更を検出:"
  echo "$HIGH_RISK"
  exit 2  # ブロック: ユーザー確認を要求
fi

echo "Push前チェック完了"
```

**exit 2**を返すとClaude Codeの実行がブロックされ、ユーザー確認が求められます。`.env`や秘密鍵などの高リスクファイルが含まれている場合の安全弁として機能します。

---

## 5. 注意点

### 無限ループの防止

PostToolUseのHookがClaude Codeにエラーを返すと、Claude Codeが自動修正（Edit）を実行し、そのEditがまたHookをトリガーする...という無限ループが発生する場合があります。

**ロックファイルによる再帰防止**:

```
#!/bin/bash
# post-edit-lint-safe.sh

LOCK_FILE="/tmp/claude-hook-lint.lock"

# 再帰検出: ロックファイルが存在すればスキップ
if [ -f "$LOCK_FILE" ]; then
  exit 0
fi

# ロックファイルを作成（スクリプト終了時に自動削除）
touch "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT

# --- ここにLint処理を記述 ---
```

`/tmp/claude-hook-lint.lock`の存在で再帰を検出し、即座に`exit 0`でスキップする方式です。`trap`でスクリプト終了時にロックファイルを確実に削除します。

### command型とprompt型の使い分け

Hooksには**command型**（bashスクリプト実行）と**prompt型**（LLM判断）の2種類があります。

| 型 | 特徴 | 適したユースケース |
| --- | --- | --- |
| command型 | 高速、決定的な処理 | Lint、Slack投稿、ファイル検証 |
| prompt型 | 柔軟、文脈依存の判断 | 「認証コード変更時にレビューリマインダー追加」など |

prompt型はLLM呼び出しが入るため応答が遅くなります。定型処理にはcommand型を使い、prompt型は文脈に応じた判断が本当に必要な場面に限定することが推奨されます。

```
{
  "hooks": {
    "PreToolUse": {
      "type": "prompt",
      "prompt": "If this edit affects authentication code, add a security review reminder.",
      "matcher": "Edit"
    }
  }
}
```

### Hookのデバッグ

Hookが期待通りに動作しない場合のデバッグ方法です。

```
# 直接実行してテスト
echo '{"tool_input":{"file_path":"test.json"}}' | bash ~/.claude/hooks/post-edit-lint.sh

# デバッグ出力（stderrに出力するとClaude Codeのコンテキストに影響しない）
echo "Debug: FILE_PATH=$FILE_PATH" >&2
```

よくある問題と対処法は以下の通りです。

| 問題 | 原因 | 対処法 |
| --- | --- | --- |
| Hookが実行されない | 実行権限がない | `chmod +x`で権限付与 |
| パスが通らない | 相対パスを使用 | 絶対パス（`~/.claude/hooks/...`）を使用 |
| 環境変数が取れない | シェル環境が異なる | スクリプト内で`source ~/.zshrc` |
| 無限ループ | Hook→ツール呼出→Hook | ロックファイルで再帰防止 |

---

## 6. 推奨Hook構成

### 初心者向け: まず入れるべき3つ

最初から多くのHookを設定すると互いに干渉する可能性があるため、以下の3つから始めることを推奨します。

| Hook | イベント | 効果 |
| --- | --- | --- |
| post-edit-lint.sh | PostToolUse | 編集後の構文エラーを自動検出 |
| pre-push-check.sh | PreToolUse | Push前の安全チェック |
| slack-feedback.sh | Stop | タスク完了のSlack通知 |

### 完全な設定例

上記3つのHookに加え、機密ファイル保護とコンテキスト再注入を組み合わせた設定例です。

```
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/compact-reinject.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/pre-push-check.sh"
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/protect-sensitive-files.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/post-edit-lint.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/slack-feedback.sh"
          }
        ]
      }
    ]
  }
}
```

---

## まとめ

Claude Code Hooksは、settings.jsonにイベントとスクリプトを登録するだけで、開発ワークフローの自動化を実現する仕組みです。

導入のポイントを整理すると以下の通りです。

* **まず3つから始める**: Lint自動チェック、Push前チェック、Slack通知
* **exit codeを正しく使う**: `0`=成功（stdout→コンテキスト追加）、`2`=ブロック（stderr→Claude Codeにフィードバック）
* **安全対策を忘れない**: トークンはKeychain管理、再帰防止フラグ、高リスクファイルのブロック
* **段階的に拡張する**: 課題が出てきたタイミングで新しいHookを追加

Hooksの設計で特に重要なのは**冪等性**（同じHookが何度実行されても問題ない設計）と**最小権限**（必要なイベント・ツールにのみmatcherを設定）の2点です。

## 参考リンク
