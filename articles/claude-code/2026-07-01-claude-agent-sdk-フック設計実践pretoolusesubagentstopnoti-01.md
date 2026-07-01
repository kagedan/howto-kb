---
id: "2026-07-01-claude-agent-sdk-フック設計実践pretoolusesubagentstopnoti-01"
title: "Claude Agent SDK フック設計実践：PreToolUse・SubagentStop・Notification を使い分ける"
url: "https://zenn.dev/yushiyamamoto/articles/claude-agent-sdk-hooks-design-2026-06"
source: "zenn"
category: "claude-code"
tags: ["prompt-engineering", "AI-agent", "Python", "TypeScript", "zenn"]
date_published: "2026-07-01"
date_collected: "2026-07-02"
summary_by: "auto-rss"
query: ""
---

Claude Agent SDK（Python / TypeScript）には、エージェントの実行ライフサイクルに割り込む **フック（Hooks）** が用意されている。ツール呼び出しのブロック・変換から、並列サブエージェントの完了集約、Slack 通知まで、単一のコールバック関数で賄える設計だ。

しかし「とりあえずフックを書いた」だけではまず何かが動かない。マッチャーの誤解、`updatedInput` に必須の付帯フィールド忘れ、サブエージェント再帰ループ——公式ドキュメント（platform.claude.com/docs/en/agent-sdk/hooks）を読み込んで踏んだ落とし穴を、よく使う3つのイベントに絞ってまとめる。

---

## フックイベントの全体像

SDK には現在 18 種類のフックイベントがある。カテゴリで整理する。

| カテゴリ | 主なイベント | 典型用途 |
| --- | --- | --- |
| ツール制御 | `PreToolUse` / `PostToolUse` / `PostToolUseFailure` | ブロック・変換・監査ログ |
| ユーザー入力 | `UserPromptSubmit` | プロンプトへのコンテキスト注入 |
| サブエージェント | `SubagentStart` / `SubagentStop` | 並列タスク追跡・結果集約 |
| 通知 | `Notification` | Slack / PagerDuty 転送 |
| セッション | `SessionStart` / `SessionEnd` | 初期化・クリーンアップ（TS のみ） |
| コンパクション | `PreCompact` | 会話圧縮前のアーカイブ |
| Git | `WorktreeCreate` / `WorktreeRemove` | ワークスペース追跡（TS のみ） |

Python SDK は `SessionStart` / `SessionEnd` を SDK コールバックとしてサポートしていない。初期化ロジックが必要なら `receive_response()` の最初のメッセージをトリガー代わりにする。

---

`.env` ファイルへの書き込みをブロックする最小例（Python）：

```
async def protect_env_files(input_data, tool_use_id, context):
    file_path = input_data["tool_input"].get("file_path", "")
    if file_path.split("/")[-1] == ".env":
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "deny",
                "permissionDecisionReason": "Cannot modify .env files",
            }
        }
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[protect_env_files])]
    }
)
```

**変換**（書き込み先をサンドボックスにリダイレクト）は `updatedInput` で行う。この場合 `permissionDecision: "allow"` の明示が必須で、省略すると変換が無視される。

**自動承認**は読み取り専用ツール（Read / Glob / Grep）の権限ダイアログを抑制したいときに使う：

```
READ_ONLY = ["Read", "Glob", "Grep"]

async def auto_approve_read_only(input_data, tool_use_id, context):
    if input_data["tool_name"] in READ_ONLY:
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "allow",
                "permissionDecisionReason": "Read-only tool auto-approved",
            }
        }
    return {}
```

### マッチャーの誤解

マッチャーは正規表現でツール名にのみ適用される。ファイルパスや引数で絞り込みたい場合はコールバック内で `tool_input["file_path"]` を確認する。マッチャーなしで登録すると全ツール呼び出しに発火するので意図的でない場合は危険だ。

複数フックをチェーンする場合は配列の先頭から順に評価され、いずれかが `deny` を返した時点でブロック確定になる：

```
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(hooks=[rate_limiter]),
            HookMatcher(hooks=[authorization_check]),
            HookMatcher(matcher="Write|Edit|Delete", hooks=[audit_logger]),
        ]
    }
)
```

---

## 2. SubagentStop：並列タスク完了の集約

動的ワークフローで並列サブエージェントを実行すると、完了イベントを拾って集約したくなる。`SubagentStop` は `agent_id`・`agent_type`・`agent_transcript_path` を渡してくる：

```
async def subagent_tracker(input_data, tool_use_id, context):
    print(f"[DONE] {input_data['agent_id']} ({input_data['agent_type']})")
    print(f"  transcript: {input_data['agent_transcript_path']}")
    # ログ送信だけなら非同期で返してエージェントを待たせない
    return {"async_": True, "asyncTimeout": 30000}
```

ログ送信のためにエージェントを待機させたくない場合は `async_: True` を返す（Python は予約語衝突で `async_`）。結果を親エージェントに注入したい場合は `systemMessage` フィールドを使う。

サブエージェントが持つ権限は親から自動継承されない。並列サブエージェントごとに権限ダイアログが出て詰まる場合は、`PreToolUse` フックで対象ツールを自動承認するのが最も確実だ。

---

## 3. Notification：Slack への転送

`Notification` フックは次の4種類のイベントで発火する：

| イベント種別 | 内容 |
| --- | --- |
| `permission_prompt` | 権限確認待ち |
| `idle_prompt` | ユーザー入力待ち |
| `auth_success` | 認証完了 |
| `elicitation_dialog` | ユーザーへの問いかけ |

長時間バックグラウンド実行するエージェントの状態を Slack に流す例：

```
async def to_slack(input_data, tool_use_id, context):
    msg = input_data.get("message", "")
    try:
        await asyncio.to_thread(_post_to_slack, msg)  # ブロッキングをスレッドに逃がす
    except Exception as e:
        print(f"slack error: {e}")  # 失敗してもエージェントを止めない
    return {}

options = ClaudeAgentOptions(
    hooks={"Notification": [HookMatcher(hooks=[to_slack])]}
)
```

HTTP リクエストは必ず `asyncio.to_thread` でラップし、例外をキャッチする。フックの未処理例外はエージェント実行を中断する。

---

## 失敗パターン

| パターン | 症状 | 対策 |
| --- | --- | --- |
| イベント名タイポ | フックが一切発火しない | `PreToolUse`（大文字小文字は厳密）。`preToolUse` は無効 |
| マッチャー過剰適用 | 全ツールに発火する | マッチャーなし登録は意図的な場合のみ |
| `updatedInput` が無視される | 変換が適用されない | `permissionDecision: "allow"` の明示が必須 |
| `UserPromptSubmit` 無限ループ | サブエージェントが同じフックを踏む | `agent_id` が非空なら早期リターンで回避 |
| `max_turns` 到達後にフック未発火 | 終了処理が走らない | ターン上限前に処理を終わらせるか別の監視を用意 |
| Python で `SessionStart` 未対応 | コールバック登録が動かない | shell command hooks を `.claude/settings.json` に書き、`setting_sources` で読み込む |

---

## 実装チェックリスト

---

## 参考リンク
