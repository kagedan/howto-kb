---
id: "2026-06-04-claude-code-hooks-活用まとめ-安全性ログ作業時間を全自動化する-01"
title: "Claude Code hooks 活用まとめ — 安全性・ログ・作業時間を全自動化する"
url: "https://qiita.com/satoshi_061/items/c3a20d437a55e59068c4"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "Python", "qiita"]
date_published: "2026-06-04"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

## はじめに

前回の記事（[Claude Code hooks設定まとめ — 音声読み上げ＆macOS/Windows通知を自動化する](https://qiita.com/satoshi_061/items/b18cce9612f6f155e294)）では、作業完了や権限確認を音声通知するフックを紹介しました。

hooks の便利さに気づいてしまったので、今回はさらに実用的な3つのフックを設定しました。

- **PreToolUse（Bash）**：危険コマンドを自動ブロック
- **PreToolUse（全ツール）**：ツール実行ログを自動記録
- **Stop**：作業時間を自動計測・記録

おまけとして「hooks はトークンをほぼ消費しない」という話も最後にまとめています。

---

## TL;DR

- `PreToolUse` フックで `rm -rf` などの危険コマンドを Claude が実行する前にブロックできる
- 全ツール実行をタイムスタンプ付きでログファイルに記録できる
- `Stop` フックでタスクの所要時間を自動記録できる
- hooks は基本的にトークン・コンテキストを消費しない（`async: true` なら完全にゼロ）

---

## 設定ファイルの場所

```
~/.claude/settings.json（グローバル設定）
```

フックのスクリプトは `~/.claude/hooks/` ディレクトリにまとめて管理します。

```bash
mkdir -p ~/.claude/hooks
```

---

## 設定① PreToolUse（Bash）— 危険コマンドの自動ブロック

### 何をするか

Claude が `rm -rf` や `DROP TABLE` などの危険なコマンドを実行しようとした瞬間にブロックします。Claude 側にエラーが返り、実行されません。

### スクリプト（~/.claude/hooks/block_dangerous.py）

```python
#!/usr/bin/env python3
import sys
import json

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

cmd = data.get('tool_input', {}).get('command', '')

dangerous_patterns = [
    'rm -rf',
    'rm -r /',
    'DROP TABLE',
    'DROP DATABASE',
    'mkfs',
    'dd if=',
    ':(){:|:&};:',
    '> /dev/sda',
    'chmod -R 777 /',
]

for pattern in dangerous_patterns:
    if pattern.lower() in cmd.lower():
        print(f'⛔ 危険なコマンドをブロックしました\nパターン: {pattern}\nコマンド: {cmd[:200]}', file=sys.stderr)
        sys.exit(2)
```

### settings.json への追加

```json
"PreToolUse": [
  {
    "matcher": "Bash",
    "hooks": [
      {
        "type": "command",
        "command": "python3 ~/.claude/hooks/block_dangerous.py"
      }
    ]
  }
]
```

### ポイント

- **`matcher: "Bash"`**：Bash ツール実行時のみ発火
- **`async` なし（同期実行）**：ブロックのためには同期が必須。`async: true` だとブロックできない
- **exit code 2**：Claude Code の仕様で、exit 2 を返すとそのツール実行をブロックして Claude にエラーを返す

### 動作イメージ

Claude に危険な操作を依頼すると：

```
⛔ 危険なコマンドをブロックしました
パターン: rm -rf
コマンド: rm -rf /tmp/...
```

Claude はエラーを受け取り、別の手段を検討するか操作を中止します。

---

## 設定② PreToolUse（全ツール）— ツール実行ログの自動記録

### 何をするか

Claude が Bash・Read・Write・Edit・WebSearch などを実行するたびに、タイムスタンプ付きで `~/.claude/tool_log.txt` に記録します。「今日 Claude が何をやったか」を後から確認できます。

### スクリプト（~/.claude/hooks/log_tools.py）

```python
#!/usr/bin/env python3
import sys
import json
import datetime
import os

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

session_id = data.get('session_id', 'unknown')[:8]
tool = data.get('tool_name', 'unknown')
tool_input = data.get('tool_input', {})
ts = datetime.datetime.now()

# ツール種別ごとにログの要約を作成
if tool == 'Bash':
    detail = tool_input.get('command', '')[:120]
elif tool in ('Read', 'Write', 'Edit'):
    detail = tool_input.get('file_path', '')
elif tool == 'WebSearch':
    detail = tool_input.get('query', '')[:120]
else:
    detail = str(tool_input)[:120]

# セッション開始時刻を記録（初回ツール実行時）
session_file = f'/tmp/claude_session_{session_id}'
if not os.path.exists(session_file):
    with open(session_file, 'w') as f:
        f.write(ts.isoformat())

# ツールログに追記
log_file = os.path.expanduser('~/.claude/tool_log.txt')
with open(log_file, 'a') as f:
    f.write(f'{ts.strftime("%Y-%m-%d %H:%M:%S")} [{session_id}] [{tool}] {detail}\n')
```

### settings.json への追加

```json
"PreToolUse": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 ~/.claude/hooks/log_tools.py",
        "async": true
      }
    ]
  }
]
```

### ログの確認方法

```bash
# 通常確認
cat ~/.claude/tool_log.txt

# リアルタイムで流す
tail -f ~/.claude/tool_log.txt
```

```
2026-06-04 22:35:06 [1aca92a7] [Bash] ls -la
2026-06-04 22:35:10 [1aca92a7] [Read] /Users/.../.claude/settings.json
2026-06-04 22:35:12 [1aca92a7] [Edit] /Users/.../.claude/settings.json
2026-06-04 22:35:20 [1aca92a7] [WebSearch] Claude Code hooks Windows
```

---

## 設定③ Stop — 作業時間の自動計測・記録

### 何をするか

タスク完了時に所要時間を計算して `~/.claude/work_log.txt` に記録します。ログ記録スクリプト（設定②）がセッション開始時刻を `/tmp/claude_session_<id>` に保存しているので、それを参照して経過時間を算出します。

### スクリプト（~/.claude/hooks/record_work_time.py）

```python
#!/usr/bin/env python3
import sys
import json
import datetime
import os

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

session_id = data.get('session_id', 'unknown')[:8]
ts = datetime.datetime.now()

# セッション開始時刻から所要時間を計算
elapsed_str = ''
session_file = f'/tmp/claude_session_{session_id}'
if os.path.exists(session_file):
    try:
        with open(session_file) as f:
            start = datetime.datetime.fromisoformat(f.read().strip())
        elapsed_sec = int((ts - start).total_seconds())
        mins, secs = divmod(elapsed_sec, 60)
        elapsed_str = f' | 所要時間: {mins}分{secs}秒'
        os.remove(session_file)
    except Exception:
        pass

# 作業ログに追記
log_file = os.path.expanduser('~/.claude/work_log.txt')
with open(log_file, 'a') as f:
    f.write(f'{ts.strftime("%Y-%m-%d %H:%M:%S")} タスク完了{elapsed_str}\n')
```

### settings.json への追加（既存の Stop フックに追記）

```json
"Stop": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "既存の通知コマンド",
        "async": true
      }
    ]
  },
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 ~/.claude/hooks/record_work_time.py",
        "async": true
      }
    ]
  }
]
```

### ログの確認方法

```bash
cat ~/.claude/work_log.txt
```

```
2026-06-04 22:35:11 タスク完了 | 所要時間: 3分42秒
2026-06-04 22:58:30 タスク完了 | 所要時間: 12分7秒
```

---

## まとめ settings.json（hooks 部分）

3つをすべて設定した場合の `hooks` セクションです。

```json
"hooks": {
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python3 ~/.claude/hooks/record_work_time.py",
          "async": true
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
          "command": "python3 ~/.claude/hooks/block_dangerous.py"
        }
      ]
    },
    {
      "hooks": [
        {
          "type": "command",
          "command": "python3 ~/.claude/hooks/log_tools.py",
          "async": true
        }
      ]
    }
  ]
}
```

---

## おまけ：hooks はトークン・コンテキストをほぼ消費しない

hooks は Claude Code のハーネス（CLI の実行基盤）側で動く仕組みで、Claude API の呼び出しとは独立しています。

| フックの状態 | トークン消費 |
|---|---|
| `async: true` のフック全般 | **ゼロ**（出力が Claude に返らない） |
| `Stop` フック | **ゼロ**（Claude が応答を終えた後に実行） |
| `PreToolUse` 通過時（exit 0） | **ゼロ** |
| `PreToolUse` ブロック時（exit 2） | **数十〜100トークン程度**（エラーメッセージが Claude に返る） |

今回設定した3つのうち、トークンが発生するのは危険コマンドを実際にブロックしたときだけです。通常の使用ではほぼゼロです。

ガンガン追加しても API コストもコンテキストも圧迫しません。

---

## まとめ

| フック | タイミング | 効果 |
|---|---|---|
| `PreToolUse（Bash）` | Bash 実行前 | 危険コマンドを自動ブロック |
| `PreToolUse（全ツール）` | 全ツール実行前 | `~/.claude/tool_log.txt` に記録 |
| `Stop` | タスク完了後 | `~/.claude/work_log.txt` に所要時間を記録 |

hooks は「設定したら何もしなくていい」のが最大の強みです。Claude Code を安心して使うための基盤として、ぜひ取り入れてみてください。

---

## 参考

- [Claude Code 公式ドキュメント — Hooks](https://docs.anthropic.com/ja/docs/claude-code/hooks)
- [Claude Code 設定リファレンス](https://docs.anthropic.com/ja/docs/claude-code/settings)
- [前回記事：Claude Code フック設定まとめ — 音声読み上げ＆macOS/Windows通知を自動化する](https://qiita.com/satoshi_061/items/b18cce9612f6f155e294)
