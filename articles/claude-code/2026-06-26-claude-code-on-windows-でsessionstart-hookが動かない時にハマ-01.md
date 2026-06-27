---
id: "2026-06-26-claude-code-on-windows-でsessionstart-hookが動かない時にハマ-01"
title: "Claude Code on Windows でSessionStart hookが動かない時にハマった話（type vs cat）"
url: "https://qiita.com/supertask/items/4319d9268d3b3df51523"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-06-26"
date_collected: "2026-06-27"
summary_by: "auto-rss"
query: ""
---

## TL;DR
- Claude Code（Happy経由含む）の `SessionStart` hook はWindowsでも **Git Bash (`/usr/bin/bash`)** で実行される
- なので `settings.json` に Windowsの `type` コマンドを書くと、bashビルトインの `type`（コマンド種別表示）として解釈されて失敗する
- `cat` を使い、パスは `/c/Users/...` 形式にすれば動く
- hookの動作確認は `~/.claude/projects/<project>/<session-uuid>.jsonl` の `hook_non_blocking_error` を見れば一発
## 背景：何をしたかったか
Claude Code + Happy アプリでは、セッション開始時に MCPツール `mcp__happy__change_title` を呼ぶことでセッション一覧のタイトルが自動設定される仕組みがあります。
しかし `mcp__happy__change_title` は **deferred tool**（必要時にスキーマがロードされるツール）扱いになっているため、`ToolSearch` で呼び出してから使う2段階の手順が必要で、Claudeが雑談判定などでスキップしてしまいタイトルが付かないケースがありました。
そこで「セッション開始時に強制的にリマインダを差し込むhook」を組むことにしました。
## 最初の設定（失敗版）
`~/.claude/hooks/title-reminder.txt` にリマインダ本文を置き、`~/.claude/settings.json` でこんなhookを設定:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "type \"C:\\Users\\supertask\\.claude\\hooks\\title-reminder.txt\""
          }
        ]
      }
    ]
  }
}
```
Windowsだから `type` でファイル内容を出力すればいいだろう、と。
## 動かない
新しいセッションを開いてもタイトルが付かない。
## 調査：hookログはどこにある？
Claude Codeのセッションログは以下に保存されます:
```
~/.claude/projects/<project-slug>/<session-uuid>.jsonl
```
このJSONLには、ユーザー入力・アシスタント応答だけでなく、**hookの実行結果**も `attachment` として記録されています。
最新のセッションファイルを開いて、先頭付近を見ると…
```json
{
  "attachment": {
    "type": "hook_non_blocking_error",
    "hookName": "SessionStart:startup",
    "hookEvent": "SessionStart",
    "stderr": "Failed with non-blocking status code: /usr/bin/bash: line 1: type: C:\\Users\\supertask\\.claude\\hooks\\title-reminder.txt: not found",
    "stdout": "",
    "exitCode": 1,
    "command": "type \"C:\\Users\\supertask\\.claude\\hooks\\title-reminder.txt\"",
    "durationMs": 221
  }
}
```
**`/usr/bin/bash: line 1: type: ... not found`**
つまり：
1. hook は発火している（`SessionStart:startup` が走った）
2. でも実行シェルが `cmd` ではなく `/usr/bin/bash`（Git Bash）
3. bashの `type` はファイル表示コマンドではなく **コマンド種別表示のビルトイン**
4. 引数にWindowsパスを渡したので "not found" になった
## 修正版
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cat \"/c/Users/supertask/.claude/hooks/title-reminder.txt\""
          }
        ]
      }
    ]
  }
}
```
ポイント:
- `type` → `cat`
- パスを `C:\Users\...` から bash 形式の `/c/Users/...` に変更（バックスラッシュのエスケープも不要になる）
これで `SessionStart` hookの `stdout` が `additionalContext` としてセッションに注入され、Claudeがセッション冒頭でタイトル設定処理を実行するようになりました。
## 学び
### 1. Windows でもClaude Code のhookはbashで動く
直感的にはOSネイティブシェル（cmd / PowerShell）が使われそうですが、実際は Git Bash です。**Windows固有のコマンド（`type`, `dir`, `copy` 等）は使わない**、これを徹底するのが安全。
### 2. hookが「無言で失敗」してもログには残る
`hook_non_blocking_error` という attachment 型でセッションJSONLに記録されます。「hook書いたのに効いてない」と思ったら、まずここを見るのが最短ルート。
```bash
grep "hook_non_blocking_error" ~/.claude/projects/*/[セッションID].jsonl
```
### 3. パスはbash形式が無難
- `C:\Users\foo` → `/c/Users/foo`
- バックスラッシュエスケープの混乱もなくなる
- スペースを含む場合はクオート
## まとめ
Claude Code on Windowsでhookを書くときは、
| やりがち | 正解 |
|---|---|
| `type "C:\path\file.txt"` | `cat "/c/path/file.txt"` |
| `dir`, `copy`, `del` | `ls`, `cp`, `rm` |
| `%USERPROFILE%` | `$HOME` または `/c/Users/<name>` |
そして詰まったら **セッションJSONLの `hook_non_blocking_error` を見る** — これだけ覚えておけば、無音失敗のhookデバッグは怖くないです。
## タグ
ClaudeCode / Claude / Windows / Bash / Hooks
