---
id: "2026-07-16-claude-code-hooksでセッション監視ツールを作って学んだ設計の勘所-01"
title: "Claude Code hooksでセッション監視ツールを作って学んだ設計の勘所"
url: "https://qiita.com/hatoyab/items/6d9ccdc32db4f035d109"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "JavaScript", "qiita"]
date_published: "2026-07-16"
date_collected: "2026-07-17"
summary_by: "auto-rss"
query: ""
---

Claude Codeには、セッションの節目で任意のコマンドを実行できる **hooks** という仕組みがあります。本記事ではその基本と、外部アプリからセッション状態を観測する実装パターンを、実際に動いているOSS（[ccglance](https://github.com/hatoya/ccglance)）の実装を一次情報源として解説します。

## 1. Claude Code hooksとは

`~/.claude/settings.json` に登録したコマンドを、ライフサイクルイベントの発生時にClaude Codeが実行してくれる仕組みです。主なイベントは次の7つです。

| イベント | 発火タイミング |
| --- | --- |
| `SessionStart` | セッション開始時 |
| `UserPromptSubmit` | プロンプト送信時 |
| `PreToolUse` | ツール（Bash、Edit等）の実行直前 |
| `PostToolUse` | ツールの実行直後 |
| `Notification` | 許可待ち・入力待ちの通知時 |
| `Stop` | 応答（ターン）の完了時 |
| `SessionEnd` | セッション終了時 |

重要なのは、**hookコマンドのstdinにイベント情報のJSONが流れてくる**点です。`hook_event_name`、`session_id`、`cwd`、ツール系イベントなら `tool_name` などが含まれます（詳細は[公式ドキュメント](https://code.claude.com/docs/ja/hooks)）。

## 2. 最小のhookを書いてみる

流れてくるJSONをそのままファイルに追記して、中身を覗いてみます。

```json
{
  "hooks": {
    "PreToolUse": [
      { "hooks": [{ "type": "command", "command": "cat >> /tmp/claude-events.jsonl" }] }
    ]
  }
}
```

セッション再起動後、ツール実行のたびに次のようなJSONが記録されます。

```json
{"hook_event_name":"PreToolUse","session_id":"abc-123","cwd":"/Users/you/proj","tool_name":"Bash","tool_input":{"command":"ls"}}
```

Node.jsで書いたhookのテストも、サンプルJSONをstdinに流すだけです。本体を起動せずに動作確認できます。

```bash
node --check my-hook.js   # 構文チェック
echo '{"hook_event_name":"PreToolUse","session_id":"test-123","cwd":"/tmp","tool_name":"Bash"}' | node my-hook.js
```

## 3. 実例: hooksでセッション監視を実現する

ccglanceは、Claude Codeの全セッションの状態を常時最前面のパネルに表示するmacOSアプリです。

```
Claude Code → hooks（Node.jsスクリプト）
            → ~/.claude/ccglance/sessions/<session_id>.json に状態を書き込み
            → アプリが0.5秒ごとにディレクトリをポーリングして描画
```

サーバーもIPCも不要です。hookは毎回起動して即終了する独立プロセスなので常駐先がなく、「hookが書き、アプリが読む」ファイル経由の疎結合が最も堅牢で、どちらかが落ちても相手に影響しません。hookの中核はイベント名から状態への変換です。

```javascript
switch (input.hook_event_name) {
  case "UserPromptSubmit":
    base.status = "thinking";
    break;
  case "PreToolUse":
    base.status = "tool";
    base.tool = TOOL_LABELS[input.tool_name] || "Using tool";  // Bash → "Running command" 等
    break;
  case "PostToolUse":
    base.status = "thinking";  // ツールを抜けたら再び考え中
    break;
  case "Notification":
    base.status = "permission";  // 許可待ち・入力待ち
    break;
  case "Stop":
    base.status = "idle";
    break;
  case "SessionEnd":
    fs.unlinkSync(stateFile(sessionId));  // 状態ファイルを削除
    break;
}
```

書き込みは一時ファイル + `fs.renameSync` の原子的更新にして、ポーリング側が書きかけのJSONを読む事故を防ぎます。

## 4. ハマりどころ・設計上の注意

**settings.jsonには「マージ」で登録する。** このファイルには他ツールのhooksも同居するため、丸ごと上書きは厳禁です。ccglanceのインストーラは、自分のコマンドが未登録のイベントにだけ追記し（`command.includes("ccglance-hook.js")` で判定）、書き込み前にバックアップを作成します。アンインストール時も同じ判定で自分のエントリだけを削除します。

**古い状態ファイルは自動掃除する。** クラッシュしたセッションでは `SessionEnd` が発火せずファイルが残るため、12時間更新のないものは自動削除します。

**hookは絶対に本体を止めない。** hookの遅延やハングはセッション体験に直撃します。ccglanceでは、stdinが閉じない場合の3秒タイムアウト、ネットワーク処理（`gh pr view` でのPR状態取得）のdetachedな子プロセスへの分離、失敗時は握りつぶして `exit 0`、を徹底しています。

なお `PreToolUse`/`PostToolUse` はサブエージェントでも親と同じ `session_id` で発火し、hookはイベントごとに並行プロセスで走るため、同一ファイルのload-modify-saveは競合します。ccglanceではセッションごとのロックファイルで書き込みを直列化して対処しています。

## 5. まとめ

- hooksは「イベント発生時にstdinへJSONを渡してコマンドを実行する」だけのシンプルで強力な仕組み
- ファイル書き込み + ポーリングだけで、サーバーレスにセッション監視ツールが作れる
- 勘所は、settings.jsonのマージ・残留ファイルの掃除・本体をブロックしない設計の3点

実装の全体はリポジトリで公開しています。アプリとしてのccglance自体の紹介はZennに書いたので、興味があればそちらもどうぞ。

- GitHub: https://github.com/hatoya/ccglance
- Zenn記事（アプリ紹介編）: https://zenn.dev/hatoya/articles/62255987ec50e7
