---
id: "2026-03-18-保存版claude-code-hooks全21イベント完全解説-イベント駆動でai開発ワークフローを-01"
title: "【保存版】Claude Code Hooks全21イベント完全解説 — イベント駆動でAI開発ワークフローを自動化する"
url: "https://qiita.com/miruky/items/e33ccda99281b40ad97b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "LLM", "qiita"]
date_published: "2026-03-18"
date_collected: "2026-03-19"
summary_by: "auto-rss"
---

## はじめに

こんばんは、mirukyです。  
Claude Code を使っていて、**「ファイル編集後に毎回フォーマッタを手動で実行するのが面倒」**「**危険なコマンドを事前にブロックしたい」**「**作業完了時にSlackに通知を飛ばしたい」** と思ったことはありませんか？

**Claude Code Hooks**は、Claude Code のライフサイクルの特定のポイントで自動的にシェルコマンド、HTTPリクエスト、LLMプロンプト、またはサブエージェントを実行できる仕組みです。

2025年6月30日にv1.0.38で初めてリリースされて以降、急速に進化を続け、2026年3月時点（v2.1.78）では**21種類のフックイベント**と**4種類のハンドラータイプ**を備えた強力な自動化フレームワークとなっています。

この記事では、Hooks の基本概念から全イベントの詳細仕様、実践的なレシピ、セキュリティ上の注意点まで、**網羅的かつ実践的に解説**します。

## 目次

1. Hooks とは何か？なぜ必要なのか？
2. Hooks のアーキテクチャ
3. 最初のフックを設定する
4. 全21イベント完全リファレンス
5. 4つのハンドラータイプ
6. マッチャーパターンによるフィルタリング
7. 入出力の仕組み
8. 実践レシピ集
9. 非同期フック（Async Hooks）
10. スキル・エージェントへのフック埋め込み
11. セキュリティ上の注意点
12. トラブルシューティング
13. バージョン別進化の歴史
14. まとめ

## 1. Hooks とは何か？なぜ必要なのか？

### Hooks の本質

Hooks は、Claude Code のライフサイクル上の**特定のポイント（イベント）** で自動的に実行されるユーザー定義のアクションです。

処理の流れと各フックイベントの発火ポイントは以下のとおりです。

1. ユーザーのプロンプト送信 → `UserPromptSubmit`
2. Claude Code がツールを呼び出す直前 → `PreToolUse`（ブロック可能）
3. ツール実行後 → `PostToolUse`（結果取得）
4. Claude の応答完了時 → `Stop`

### なぜ Hooks が必要なのか？

Claude Code は LLM ベースのコーディングエージェントですが、LLM に「毎回必ずフォーマッタを実行して」と指示しても、**100% 確実に実行される保証はありません**。Hooks を使えば、**決定論的なルール**として確実に処理を実行できます。

| アプローチ | 実行保証 | 用途 |
| --- | --- | --- |
| CLAUDE.md に指示を書く | LLM依存（忘れることがある） | 柔軟なガイダンス |
| Skills で手順を定義 | LLM依存（呼ばれないことがある） | 再利用可能な指示 |
| **Hooks でイベントに紐づける** | **確実に実行される** | **自動化・セキュリティ・強制** |

### Hooks で実現できること

* **セキュリティ**: 危険なコマンドのブロック、保護ファイルへの書き込み防止
* **コード品質**: 編集後の自動フォーマット、リント実行
* **通知**: 作業完了時のデスクトップ通知、Slack連携
* **監査**: 全ツール使用のログ記録、設定変更の追跡
* **ワークフロー**: テスト自動実行、コンテキスト再注入
* **品質ゲート**: タスク完了前のテスト実行確認

## 2. Hooks のアーキテクチャ

### 3層構造

Hooks の設定は3層のネスト構造になっています。

1. **Hook Event（いつ実行するか）** — 例: `PreToolUse`, `Stop`, `PostToolUse`
2. **Matcher Group（どの条件で実行するか）** — 例: `"Bash"`, `"Edit|Write"`
3. **Hook Handler（何を実行するか）** — タイプ: `command` / `http` / `prompt` / `agent`

### 設定ファイルの配置場所

| 場所 | スコープ | バージョン管理 |
| --- | --- | --- |
| `~/.claude/settings.json` | 全プロジェクト共通 | ローカルのみ |
| `.claude/settings.json` | 単一プロジェクト | リポジトリにコミット可能 |
| `.claude/settings.local.json` | 単一プロジェクト | gitignore対象 |
| マネージドポリシー設定 | 組織全体 | 管理者制御 |
| プラグイン `hooks/hooks.json` | プラグイン有効時 | プラグインに同梱 |
| スキル/エージェントのフロントマター | コンポーネント有効時 | コンポーネントファイル内 |

### フック解決フロー

フックの処理は以下の順序で行われます。

1. **イベント発火** — Claude Code のライフサイクル上の特定のポイントでイベントが発火
2. **マッチャー照合** — 正規表現パターンでフィルタリング（省略時は全一致）
3. **ハンドラー実行** — すべてのマッチしたフックが並列実行され、同一コマンドは自動的に重複排除
4. **結果処理** — exit code や JSON 出力に基づいて Claude Code が判断

## 3. 最初のフックを設定する

### ステップ1: デスクトップ通知フックを作る

Claude Code が入力を待っているときにデスクトップ通知を受け取るフックを設定してみましょう。

`~/.claude/settings.json` を開き、以下を追加します：

```
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

**Linux の場合**: `notify-send "Claude Code" "Claude Code needs your attention"` を使用してください。  
**Windows の場合**: PowerShell の `New-BurntToastNotification` を使用してください。

### ステップ2: 設定の確認

Claude Code 内で `/hooks` と入力してフックブラウザを開きます。`Notification` イベントの横にフックのカウントが表示されていれば成功です。

### ステップ3: テスト

Claude Code に何か作業を依頼し、ターミナルから離れてみてください。デスクトップ通知が届くはずです。

`/hooks` メニューは読み取り専用です。フックの追加・変更・削除は、settings JSON を直接編集するか、Claude Code に変更を依頼してください。

## 4. 全21イベント完全リファレンス

### イベント一覧

Claude Code Hooks は 21 種類のフックイベントをサポートしています。セッション開始からエージェントループ、セッション終了まで、ライフサイクル全体をカバーしています。

#### セッション管理イベント

| イベント名 | 発火タイミング | ブロック可能 |
| --- | --- | --- |
| `SessionStart` | セッション開始・再開時 | いいえ |
| `SessionEnd` | セッション終了時 | いいえ |
| `InstructionsLoaded` | CLAUDE.md / rules ファイル読み込み時 | いいえ |
| `ConfigChange` | 設定ファイル変更時 | はい |

#### ユーザー入力イベント

| イベント名 | 発火タイミング | ブロック可能 |
| --- | --- | --- |
| `UserPromptSubmit` | ユーザーがプロンプト送信時（処理前） | はい |

#### ツール関連イベント

| イベント名 | 発火タイミング | ブロック可能 |
| --- | --- | --- |
| `PreToolUse` | ツール実行前 | はい |
| `PermissionRequest` | 権限ダイアログ表示時 | はい |
| `PostToolUse` | ツール実行成功後 | いいえ（フィードバック可） |
| `PostToolUseFailure` | ツール実行失敗後 | いいえ（フィードバック可） |

#### 通知・エージェントイベント

| イベント名 | 発火タイミング | ブロック可能 |
| --- | --- | --- |
| `Notification` | Claude Code が通知送信時 | いいえ |
| `SubagentStart` | サブエージェント生成時 | いいえ（コンテキスト注入可） |
| `SubagentStop` | サブエージェント完了時 | はい |
| `Stop` | Claude の応答完了時 | はい |

#### チーム・タスクイベント

| イベント名 | 発火タイミング | ブロック可能 |
| --- | --- | --- |
| `TeammateIdle` | チームメイトがアイドル状態になる前 | はい |
| `TaskCompleted` | タスク完了マーク時 | はい |

#### ワークツリーイベント

| イベント名 | 発火タイミング | ブロック可能 |
| --- | --- | --- |
| `WorktreeCreate` | ワークツリー作成時 | はい（失敗可） |
| `WorktreeRemove` | ワークツリー削除時 | いいえ |

#### コンパクト・MCP イベント

| イベント名 | 発火タイミング | ブロック可能 |
| --- | --- | --- |
| `PreCompact` | コンテキスト圧縮前 | いいえ |
| `PostCompact` | コンテキスト圧縮後 | いいえ |
| `Elicitation` | MCP サーバーがユーザー入力要求時 | はい |
| `ElicitationResult` | MCP エリシテーション応答後 | はい |

### 各イベントの詳細

#### SessionStart — セッション開始のカスタマイズ

セッション開始時にコンテキストを注入したり、環境変数を設定したりできます。

**マッチャー値:**

| 値 | 意味 |
| --- | --- |
| `startup` | 新規セッション |
| `resume` | `--resume` / `--continue` / `/resume` |
| `clear` | `/clear` 後 |
| `compact` | 自動・手動コンパクション後 |

**入力スキーマ:**

```
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/.../my-project",
  "permission_mode": "default",
  "hook_event_name": "SessionStart",
  "source": "startup",
  "model": "claude-sonnet-4-6"
}
```

**特殊機能 — 環境変数の永続化:**

SessionStart フックでは `CLAUDE_ENV_FILE` 環境変数が利用可能です。ここに `export` 文を書き込むことで、セッション中のすべての Bash コマンドで環境変数を利用できます。

```
#!/bin/bash
if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
  echo 'export DEBUG_LOG=true' >> "$CLAUDE_ENV_FILE"
fi
exit 0
```

#### PreToolUse — ツール実行のゲートキーパー

ツール実行前に実行され、**ブロック・許可・ユーザー確認**の3つの判断が可能です。

**マッチ対象ツール名**: `Bash`, `Edit`, `Write`, `Read`, `Glob`, `Grep`, `Agent`, `WebFetch`, `WebSearch`, MCP ツール (`mcp__<server>__<tool>`)

**各ツールの入力スキーマ:**

| ツール | 主要フィールド |
| --- | --- |
| `Bash` | `command`, `description`, `timeout` |
| `Write` | `file_path`, `content` |
| `Edit` | `file_path`, `old_string`, `new_string` |
| `Read` | `file_path`, `offset`, `limit` |
| `Glob` | `pattern`, `path` |
| `Grep` | `pattern`, `path`, `glob` |
| `WebFetch` | `url`, `prompt` |
| `WebSearch` | `query`, `allowed_domains` |
| `Agent` | `prompt`, `description`, `subagent_type` |

**決定制御（hookSpecificOutput）:**

| フィールド | 意味 |
| --- | --- |
| `permissionDecision` | `"allow"`: 許可、`"deny"`: 拒否、`"ask"`: ユーザーに確認 |
| `permissionDecisionReason` | 理由のメッセージ |
| `updatedInput` | ツール入力の書き換え |
| `additionalContext` | Claude へのコンテキスト追加 |

```
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Use rg instead of grep for better performance"
  }
}
```

`"allow"` を返してもパーミッションルール（deny ルールなど）は上書きされません。マネージドポリシーの deny リストは常にフック承認より優先されます。

#### Stop — 作業完了の品質ゲート

Claude が応答を終了しようとするときに実行されます。フックが `decision: "block"` を返すと、Claude は作業を続行します。

**無限ループ防止:**

Stop フックの入力には `stop_hook_active` フィールドが含まれます。このフィールドが `true` の場合、すでに Stop フックによって作業が続行されていることを示します。**必ずこのフィールドをチェックして無限ループを防止してください。**

```
#!/bin/bash
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0  # Claude の停止を許可
fi
# ... 通常のフックロジック
```

#### PermissionRequest — 権限ダイアログの自動制御

権限ダイアログの表示時に実行され、ユーザーに代わって許可・拒否を自動的に行えます。

`PermissionRequest` フックは非インタラクティブモード（`-p`）では発火しません。自動化されたパーミッション制御には `PreToolUse` フックを使用してください。

**更新可能なパーミッション（updatedPermissions）:**

| type | 説明 |
| --- | --- |
| `addRules` | パーミッションルールを追加 |
| `replaceRules` | 指定した behavior のルールをすべて置換 |
| `removeRules` | マッチするルールを削除 |
| `setMode` | パーミッションモードを変更（`default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan`） |
| `addDirectories` | 作業ディレクトリを追加 |
| `removeDirectories` | 作業ディレクトリを削除 |

**destination（適用先）:**

| 値 | 効果 |
| --- | --- |
| `session` | メモリ内のみ（セッション終了で破棄） |
| `localSettings` | `.claude/settings.local.json` に永続化 |
| `projectSettings` | `.claude/settings.json` に永続化 |
| `userSettings` | `~/.claude/settings.json` に永続化 |

## 5. 4つのハンドラータイプ

### 対応表

すべてのイベントが 4 つのタイプすべてに対応しているわけではありません。

**全4タイプ対応イベント:**  
`PreToolUse`, `PermissionRequest`, `PostToolUse`, `PostToolUseFailure`, `Stop`, `SubagentStop`, `TaskCompleted`, `UserPromptSubmit`

**command のみ対応イベント:**  
`SessionStart`, `SessionEnd`, `ConfigChange`, `Notification`, `SubagentStart`, `TeammateIdle`, `PreCompact`, `PostCompact`, `Elicitation`, `ElicitationResult`, `InstructionsLoaded`, `WorktreeCreate`, `WorktreeRemove`

### 1. Command Hook（`type: "command"`）

シェルコマンドを実行する最も基本的なタイプです。

```
{
  "type": "command",
  "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write",
  "timeout": 600
}
```

| フィールド | 必須 | 説明 |
| --- | --- | --- |
| `type` | はい | `"command"` |
| `command` | はい | 実行するシェルコマンド |
| `timeout` | いいえ | タイムアウト秒数（デフォルト: 600秒） |
| `async` | いいえ | `true` でバックグラウンド実行 |
| `statusMessage` | いいえ | 実行中のスピナーメッセージ |
| `once` | いいえ | `true` でセッション中1回のみ実行（スキルのみ） |

**入出力の流れ:**

```
Claude Code → JSON (stdin) → コマンド実行 → exit code + stdout/stderr → Claude Code
```

### 2. HTTP Hook（`type: "http"`）

イベントデータを HTTP エンドポイントに POST します。チーム横断の監査サービスやクラウドファンクションとの連携に最適です。

```
{
  "type": "http",
  "url": "http://localhost:8080/hooks/tool-use",
  "headers": {
    "Authorization": "Bearer $MY_TOKEN"
  },
  "allowedEnvVars": ["MY_TOKEN"],
  "timeout": 30
}
```

| フィールド | 必須 | 説明 |
| --- | --- | --- |
| `type` | はい | `"http"` |
| `url` | はい | POST 先の URL |
| `headers` | いいえ | 追加 HTTP ヘッダー（環境変数の展開に対応） |
| `allowedEnvVars` | いいえ | ヘッダーで展開を許可する環境変数名のリスト |
| `timeout` | いいえ | タイムアウト秒数（デフォルト: 600秒） |

**レスポンスの扱い:**

* **2xx + 空ボディ**: 成功（exit 0 と同等）
* **2xx + テキストボディ**: 成功、テキストがコンテキストに追加
* **2xx + JSON ボディ**: 成功、command hook と同じ JSON 出力形式で解析
* **非 2xx / 接続失敗**: ノンブロッキングエラー（処理は続行）

HTTP hook はステータスコードだけではアクションをブロックできません。ブロックするには 2xx レスポンスで JSON ボディに `decision: "block"` を含める必要があります。

### 3. Prompt Hook（`type: "prompt"`）

LLM（デフォルトで Haiku）に判断を委ねるタイプです。決定論的なルールではなく、**文脈に応じた判断**が必要な場合に使います。

```
{
  "type": "prompt",
  "prompt": "Check if all tasks are complete. If not, respond with {\"ok\": false, \"reason\": \"what remains to be done\"}.",
  "model": "claude-haiku-4-5",
  "timeout": 30
}
```

| フィールド | 必須 | 説明 |
| --- | --- | --- |
| `type` | はい | `"prompt"` |
| `prompt` | はい | LLM に送るプロンプト（`$ARGUMENTS` でフック入力 JSON を展開） |
| `model` | いいえ | 使用するモデル（デフォルト: 高速モデル） |
| `timeout` | いいえ | タイムアウト秒数（デフォルト: 30秒） |

**レスポンススキーマ:**

```
{
  "ok": true,
  "reason": "All tasks complete"
}
```

* `"ok": true` → アクション許可
* `"ok": false` → アクションブロック（`reason` が Claude にフィードバック）

### 4. Agent Hook（`type: "agent"`）

サブエージェントを起動し、`Read`、`Grep`、`Glob` などのツールを使って**実際のコードベースを検査**してから判断するタイプです。最大50ターンの multi-turn 実行が可能。

```
{
  "type": "agent",
  "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
  "timeout": 120
}
```

| フィールド | 必須 | 説明 |
| --- | --- | --- |
| `type` | はい | `"agent"` |
| `prompt` | はい | 検証タスクの指示（`$ARGUMENTS` でフック入力 JSON を展開） |
| `model` | いいえ | 使用するモデル（デフォルト: 高速モデル） |
| `timeout` | いいえ | タイムアウト秒数（デフォルト: 60秒） |

**Prompt Hook との使い分け:**

|  | Prompt Hook | Agent Hook |
| --- | --- | --- |
| 実行方式 | 単一 LLM 呼び出し | multi-turn（最大50ターン） |
| ツールアクセス | なし | あり（Read, Grep, Glob） |
| 適切な用途 | フック入力データだけで判断できる場合 | コードベースの実際の状態を検査する必要がある場合 |
| デフォルトタイムアウト | 30秒 | 60秒 |

## 6. マッチャーパターンによるフィルタリング

### マッチャーの基本

マッチャーは正規表現パターンで、フックが発火する条件を絞り込みます。省略すると全てのイベントに反応します。

```
{
  "matcher": "Edit|Write",
  "hooks": [
    {
      "type": "command",
      "command": "echo 'Edit/Write tool matched'"
    }
  ]
}
```

### イベントごとのマッチ対象

| イベント | マッチ対象 | 例 |
| --- | --- | --- |
| `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest` | ツール名 | `Bash`, `Edit|Write`, `mcp__.*` |
| `SessionStart` | セッション開始方法 | `startup`, `resume`, `clear`, `compact` |
| `SessionEnd` | 終了理由 | `clear`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other` |
| `Notification` | 通知タイプ | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog` |
| `SubagentStart`, `SubagentStop` | エージェントタイプ | `Bash`, `Explore`, `Plan` |
| `PreCompact`, `PostCompact` | トリガー | `manual`, `auto` |
| `ConfigChange` | 設定ソース | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` |
| `Elicitation`, `ElicitationResult` | MCP サーバー名 | `my-mcp-server`, `auth-server` |
| `UserPromptSubmit`, `Stop`, `TeammateIdle`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove`, `InstructionsLoaded` | マッチャー非対応 | 常に全発火 |

### MCP ツールのマッチング

MCP サーバーのツールは `mcp__<server>__<tool>` の命名規則に従います。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__memory__.*",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Memory operation initiated' >> ~/mcp-operations.log"
          }
        ]
      },
      {
        "matcher": "mcp__.*__write.*",
        "hooks": [
          {
            "type": "command",
            "command": "/home/user/scripts/validate-mcp-write.py"
          }
        ]
      }
    ]
  }
}
```

* `mcp__memory__.*` — Memory サーバーの全ツール
* `mcp__.*__write.*` — 任意のサーバーの write を含むツール
* `mcp__github__search_repositories` — GitHub サーバーの特定ツール

## 7. 入出力の仕組み

### 共通入力フィールド

すべてのフックイベントで以下のフィールドが JSON として受け渡されます。

| フィールド | 説明 |
| --- | --- |
| `session_id` | セッション識別子 |
| `transcript_path` | 会話 JSON のパス |
| `cwd` | フック呼び出し時のカレントディレクトリ |
| `permission_mode` | 現在のパーミッションモード |
| `hook_event_name` | 発火したイベント名 |

`--agent` 実行時やサブエージェント内では、追加で `agent_id` と `agent_type` が含まれます。

### Exit Code による制御

| Exit Code | 意味 | 動作 |
| --- | --- | --- |
| **0** | 成功 | stdout の JSON を解析。`UserPromptSubmit` と `SessionStart` では stdout がコンテキストに追加 |
| **2** | ブロッキングエラー | stderr が Claude にフィードバック。イベントに応じてアクションをブロック |
| **その他** | ノンブロッキングエラー | stderr は verbose モード（`Ctrl+O`）でのみ表示。処理は続行 |

### Exit Code 2 の挙動一覧

| イベント | ブロック可能 | 挙動 |
| --- | --- | --- |
| `PreToolUse` | はい | ツール呼び出しをブロック |
| `PermissionRequest` | はい | パーミッションを拒否 |
| `UserPromptSubmit` | はい | プロンプト処理をブロック＆消去 |
| `Stop` | はい | Claude の停止を阻止、会話を続行 |
| `SubagentStop` | はい | サブエージェントの停止を阻止 |
| `TeammateIdle` | はい | チームメイトのアイドルを阻止 |
| `TaskCompleted` | はい | タスク完了マークを阻止 |
| `ConfigChange` | はい | 設定変更の適用をブロック |
| `Elicitation` | はい | エリシテーションを拒否 |
| `ElicitationResult` | はい | レスポンスをブロック（decline に変更） |
| `WorktreeCreate` | はい | ワークツリー作成を失敗させる |
| `PostToolUse` | いいえ | stderr を Claude に表示（ツールは既に実行済み） |
| `PostToolUseFailure` | いいえ | stderr を Claude に表示（ツールは既に失敗済み） |
| `SessionStart`, `SessionEnd`, `Notification`, `SubagentStart`, `PreCompact`, `PostCompact` | いいえ | stderr をユーザーにのみ表示 |
| `WorktreeRemove` | いいえ | デバッグモードでのみログ記録 |
| `InstructionsLoaded` | いいえ | exit code は無視 |

### JSON 出力の構造

exit 0 で JSON を stdout に出力すると、より詳細な制御が可能です。

**ユニバーサルフィールド:**

| フィールド | デフォルト | 説明 |
| --- | --- | --- |
| `continue` | `true` | `false` で Claude の処理を完全停止 |
| `stopReason` | なし | `continue: false` 時にユーザーに表示 |
| `suppressOutput` | `false` | `true` で verbose モードでの stdout 表示を抑制 |
| `systemMessage` | なし | ユーザーに表示する警告メッセージ |

**決定制御パターン:**

| イベント | パターン | フィールド |
| --- | --- | --- |
| `UserPromptSubmit`, `PostToolUse`, `PostToolUseFailure`, `Stop`, `SubagentStop`, `ConfigChange` | トップレベル decision | `decision: "block"`, `reason` |
| `TeammateIdle`, `TaskCompleted` | exit code 2 または JSON | exit code 2 で stderr フィードバック。`{"continue": false, "stopReason": "..."}` でチームメイトを完全停止 |
| `PreToolUse` | hookSpecificOutput | `permissionDecision` (allow/deny/ask) |
| `PermissionRequest` | hookSpecificOutput | `decision.behavior` (allow/deny) |
| `WorktreeCreate` | stdout パス | ワークツリーの絶対パスを stdout に出力。非ゼロ exit で失敗 |
| `Elicitation`, `ElicitationResult` | hookSpecificOutput | `action` (accept/decline/cancel) |
| `WorktreeRemove`, `Notification`, `SessionEnd`, `PreCompact`, `PostCompact`, `InstructionsLoaded` | なし | 決定制御なし（副作用のみ） |

exit code 2 と JSON 出力を混在させないでください。Claude Code は exit code 2 の場合、JSON を無視します。

## 8. 実践レシピ集

### レシピ1: ファイル編集後の自動フォーマット

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

この例では `jq` を使用しています。macOS: `brew install jq`、Ubuntu: `apt-get install jq` でインストールできます。

### レシピ2: 保護ファイルへの書き込みブロック

**スクリプト（`.claude/hooks/protect-files.sh`）:**

```
#!/bin/bash
# protect-files.sh

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

PROTECTED_PATTERNS=(".env" "package-lock.json" ".git/")

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH matches protected pattern '$pattern'" >&2
    exit 2
  fi
done

exit 0
```

```
chmod +x .claude/hooks/protect-files.sh
```

**設定:**

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh"
          }
        ]
      }
    ]
  }
}
```

### レシピ3: 危険なBashコマンドのブロック

```
#!/bin/bash
# .claude/hooks/block-rm.sh
COMMAND=$(jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Destructive command blocked by hook"
    }
  }'
else
  exit 0
fi
```

### レシピ4: コンパクション後のコンテキスト再注入

コンテキストウィンドウが一杯になると、コンパクションで会話が要約されます。これにより重要な詳細が失われることがあります。`SessionStart` フックで `compact` マッチャーを使うと、コンパクション後に重要なコンテキストを再注入できます。

```
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Reminder: use Bun, not npm. Run bun test before committing. Current sprint: auth refactor.'"
          }
        ]
      }
    ]
  }
}
```

`echo` の代わりに `git log --oneline -5` のように動的な出力を生成するコマンドを使用することもできます。静的なコンテキストを毎回注入する場合は、`CLAUDE.md` の使用を検討してください。

### レシピ5: 設定変更の監査ログ

```
{
  "hooks": {
    "ConfigChange": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "jq -c '{timestamp: now | todate, source: .source, file: .file_path}' >> ~/claude-config-audit.log"
          }
        ]
      }
    ]
  }
}
```

### レシピ6: 特定のパーミッションプロンプトの自動承認

`ExitPlanMode`（プラン提示後の実行確認）を自動承認する例：

```
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"PermissionRequest\", \"decision\": {\"behavior\": \"allow\"}}}'"
          }
        ]
      }
    ]
  }
}
```

マッチャーを `.*` や空文字にすると、ファイル書き込みやシェルコマンドを含む**すべてのパーミッションプロンプトを自動承認**してしまいます。マッチャーは可能な限り狭くしてください。

### レシピ7: Prompt Hook で多角的な完了チェック

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "You are evaluating whether Claude should stop working. Context: $ARGUMENTS\n\nAnalyze the conversation and determine if:\n1. All user-requested tasks are complete\n2. Any errors need to be addressed\n3. Follow-up work is needed\n\nRespond with JSON: {\"ok\": true} to allow stopping, or {\"ok\": false, \"reason\": \"your explanation\"} to continue working.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### レシピ8: Agent Hook でテスト実行を検証

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

### レシピ9: HTTP Hook でチーム共有の監査サービスに送信

```
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:8080/hooks/tool-use",
            "headers": {
              "Authorization": "Bearer $MY_TOKEN"
            },
            "allowedEnvVars": ["MY_TOKEN"]
          }
        ]
      }
    ]
  }
}
```

### レシピ10: Bashコマンドの全ログ記録

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' >> ~/.claude/command-log.txt"
          }
        ]
      }
    ]
  }
}
```

## 9. 非同期フック（Async Hooks）

### 概要

デフォルトでは、フックは Claude の処理をブロックして完了まで待機します。テストスイートの実行やデプロイのような時間のかかるタスクでは、`"async": true` を設定するとバックグラウンドで実行しながら Claude は作業を続行できます。

### 設定方法

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/run-tests-async.sh",
            "async": true,
            "timeout": 300
          }
        ]
      }
    ]
  }
}
```

### 非同期フックのスクリプト例

```
#!/bin/bash
# run-tests-async.sh

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# ソースファイルのみテスト
if [[ "$FILE_PATH" != *.ts && "$FILE_PATH" != *.js ]]; then
  exit 0
fi

RESULT=$(npm test 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  jq -n --arg msg "Tests passed after editing $FILE_PATH" '{"systemMessage": $msg}'
else
  jq -n --arg msg "Tests failed after editing $FILE_PATH: $RESULT" '{"systemMessage": $msg}'
fi
```

### 制約事項

| 制約 | 説明 |
| --- | --- |
| command タイプのみ | `prompt` や `agent` は非同期実行不可 |
| ブロック不可 | 非同期フック完了時にはアクションは既に完了済み |
| 次ターンで配信 | `systemMessage` や `additionalContext` は次の会話ターンで配信 |
| 重複排除なし | 同じ非同期フックが複数回発火した場合、個別のプロセスが作成 |

非同期フックの完了通知はデフォルトで非表示です。`Ctrl+O` で verbose モードを切り替えるか、`--verbose` で起動すると表示されます。

## 10. スキル・エージェントへのフック埋め込み

### フロントマターでの定義

スキルやサブエージェントの YAML フロントマターにフックを直接定義できます。これらのフックは**コンポーネントのライフサイクルにスコープ**され、コンポーネントが有効な間のみ実行されます。

```
---
name: secure-operations
description: Perform operations with security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

**ポイント:**

* すべてのフックイベントが利用可能
* サブエージェントの `Stop` フックは自動的に `SubagentStop` に変換される
* コンポーネント終了時にクリーンアップされる

## 11. セキュリティ上の注意点

### 重要な警告

**command フックはシステムユーザーの完全な権限で実行されます。** ユーザーアカウントがアクセスできるすべてのファイルへの変更、削除、アクセスが可能です。設定に追加する前に、必ずすべてのフックコマンドを確認・テストしてください。

### セキュリティベストプラクティス

| プラクティス | 説明 |
| --- | --- |
| 入力の検証 | 入力データを盲目的に信頼しない |
| シェル変数のクォート | `$VAR` ではなく `"$VAR"` を使用 |
| パス走査のブロック | ファイルパス内の `..` をチェック |
| 絶対パスの使用 | スクリプトには完全パスを指定（`"$CLAUDE_PROJECT_DIR"` でプロジェクトルート参照） |
| 機密ファイルの除外 | `.env`、`.git/`、鍵ファイルなどを処理しない |

### 組織レベルの制御

エンタープライズ管理者は `allowManagedHooksOnly` を設定して、ユーザー・プロジェクト・プラグインのフックをブロックし、マネージドポリシーのフックのみを許可できます。

`disableAllHooks` 設定はマネージドポリシーの階層を尊重します。**ユーザーやプロジェクト設定の `disableAllHooks` ではマネージドフックを無効化できません**。マネージドフックを無効化できるのは、マネージドレベルの `disableAllHooks` のみです。

## 12. トラブルシューティング

### フックが発火しない

1. `/hooks` でフックが正しいイベントの下に表示されているか確認
2. マッチャーパターンがツール名と正確に一致しているか確認（**大文字小文字は区別されます**）
3. 正しいイベントタイプをトリガーしているか確認
4. `PermissionRequest` を非インタラクティブモード（`-p`）で使っている場合は `PreToolUse` に切り替え

### フックエラーが出力に表示される

手動でテスト：

```
echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | ./my-hook.sh
echo $?  # exit code を確認
```

* `"command not found"` → 絶対パスまたは `$CLAUDE_PROJECT_DIR` を使用
* `"jq: command not found"` → `jq` をインストール
* スクリプトが実行されない → `chmod +x ./my-hook.sh`

### Stop フックが無限ループ

`stop_hook_active` フィールドをチェックしていない可能性があります。

```
#!/bin/bash
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0  # Claude の停止を許可
fi
# ... フックロジック
```

### JSON 解析エラー

シェルプロファイル（`~/.zshrc` / `~/.bashrc`）に無条件の `echo` 文がある場合、フックの JSON 出力に余計なテキストが混入します。

```
# ~/.zshrc や ~/.bashrc で修正
if [[ $- == *i* ]]; then
  echo "Shell ready"
fi
```

`$-` にはシェルフラグが含まれ、`i` はインタラクティブシェルを意味します。フックは非インタラクティブシェルで実行されるため、`echo` はスキップされます。

### `/hooks` に設定したフックが表示されない

* JSON が有効か確認（末尾カンマやコメントは不可）
* 設定ファイルが正しい場所にあるか確認
* ファイルウォッチャーが変更を検知しなかった場合、セッションを再起動

### デバッグ技法

```
# フル実行詳細を表示
claude --debug

# verbose モード切替（実行中）
# Ctrl+O を押す
```

デバッグモードではマッチしたフック、exit code、出力が表示されます。

```
[DEBUG] Executing hooks for PostToolUse:Write
[DEBUG] Getting matching hook commands for PostToolUse with query: Write
[DEBUG] Found 1 hook matchers in settings
[DEBUG] Matched 1 hooks for query "Write"
[DEBUG] Found 1 hook commands to execute
[DEBUG] Executing hook command: <Your command> with timeout 600000ms
[DEBUG] Hook command completed with status 0: <Your stdout>
```

## 13. バージョン別進化の歴史

Claude Code Hooks は継続的に進化しています。主要なマイルストーンを振り返ります。

| バージョン | リリース日 | 追加された機能 |
| --- | --- | --- |
| v1.0.38 | 2025年6月30日 | **Hooks 機能初回リリース** |
| v2.0.12 | 2025年10月9日 | プラグインシステムリリース（プラグイン内フック対応） |
| v2.1.32 | 2026年2月5日 | Agent Teams（実験的）— `TeammateIdle` フック |
| v2.1.63 | 2026年2月28日 | **HTTP Hooks**（`type: "http"`）追加 |
| v2.1.69 | 2026年3月5日 | `InstructionsLoaded` フック追加 |
| v2.1.76 | 2026年3月14日 | MCP エリシテーション対応（`Elicitation` / `ElicitationResult` フック）、`PostCompact` フック追加 |
| v2.1.78 | 2026年3月17日 | プラグイン永続データ（`${CLAUDE_PLUGIN_DATA}`）追加 |

## 14. まとめ

### Claude Code Hooks の全体像

ここまでお読みいただき、ありがとうございます。  
まとめると、Claude Code Hooksを使用する3ステップは下記の通りです。

1. **`~/.claude/settings.json`** に `Notification` フックを追加して動作確認
2. **`.claude/settings.json`** にプロジェクト固有のフック（自動フォーマット等）を設定
3. 必要に応じて `prompt` / `agent` / `http` タイプを活用して高度な自動化を実現

Claude Codeはどんどん新機能が追加され、使いやすくなっていますね。

ではまた、お会いしましょう。

## 参考リンク
