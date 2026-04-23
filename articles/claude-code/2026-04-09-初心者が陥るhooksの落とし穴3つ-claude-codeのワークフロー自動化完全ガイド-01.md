---
id: "2026-04-09-初心者が陥るhooksの落とし穴3つ-claude-codeのワークフロー自動化完全ガイド-01"
title: "初心者が陥るHooksの落とし穴3つ — Claude Codeのワークフロー自動化完全ガイド"
url: "https://qiita.com/moha0918_/items/7dae0551edf85c051a48"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

Claude CodeのHooksを設定してみたら、思ったより簡単に動いた。でも2つ目のHookを書いたあたりから「なんか想定と違う挙動をする」という経験をした方は多いのではないでしょうか。

Hooksは設定自体はシンプルなのですが、**「なぜ動かないのか」が分かりにくい**という落とし穴が3つほどあります。この記事では、入門者がハマりやすいその3つのポイントを解説しながら、Hooksの全体像と実用的な使い方を紹介します。

対象読者: Claude Codeを使い始めて間もない方、Hooksを設定してみたが思い通りに動かない方  
前提: Claude Codeがインストール済みであること。JSONファイルの編集ができること

## まずHooksとは何か

Claude CodeのHooksは、**特定のタイミングで自動的にシェルコマンドを実行する仕組み**です。

たとえばこんなことができます。

* Claudeがファイルを編集するたびに、自動でPrettierを走らせる
* 危険なコマンドが実行される前にブロックする
* Claudeが待ち状態になったらデスクトップ通知を送る
* コンテキストが圧縮されたとき、重要な情報を再注入する

LLMに「毎回フォーマットして」と頼むと、たまにサボります。でもHooksに設定すれば**必ず実行される**のが最大のメリットです。

### ライフサイクルのどこで動くか

イベントの種類は非常に多いですが、よく使う主要なものを整理します。

| イベント | 発火タイミング | 主なユースケース |
| --- | --- | --- |
| `PreToolUse` | ツール実行前 | コマンドのブロック、検証 |
| `PostToolUse` | ツール実行後 | フォーマット、ログ記録 |
| `Notification` | Claudeが入力待ちになったとき | デスクトップ通知 |
| `SessionStart` | セッション開始・再開時 | コンテキストの注入 |
| `Stop` | Claudeが応答を終えたとき | タスク完了チェック |
| `PermissionRequest` | 許可ダイアログが出る前 | 特定操作の自動承認 |
| `CwdChanged` | 作業ディレクトリが変わったとき | 環境変数の再読み込み |

## 最初のHookを動かしてみる

百聞は一見に如かず。まずデスクトップ通知Hookを設定してみましょう。

`~/.claude/settings.json` を開いて、以下を追加します。

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

Linux の場合は `notify-send 'Claude Code' 'Claude Code needs your attention'` に、Windows の場合は PowerShell のコマンドに置き換えてください。

設定後に `/hooks` コマンドを実行すると、設定したHookの一覧が確認できます。`Notification` の横に件数が表示されていれば成功です。

macOSで通知が表示されない場合、Script Editorに通知権限がない可能性があります。ターミナルで `osascript -e 'display notification "test"'` を一度実行し、「システム設定 > 通知」でScript Editorの通知を許可してください。

## 落とし穴その1: matcherの大文字小文字を間違える

最初のハマりポイントです。`matcher` は**正規表現で、大文字小文字を区別します**。

たとえば `PostToolUse` で「ファイル編集後にフォーマットする」Hookを書くとき、こう書いてしまいがちです。

```
{
  "matcher": "edit|write"
}
```

これは動きません。Claude Codeのツール名は `Edit`、`Write` と先頭が大文字です。

正しくはこうです。

```
{
  "matcher": "Edit|Write"
}
```

実際にPrettierを自動実行する設定はこちらです。プロジェクトルートの `.claude/settings.json` に追加します。

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

`jq` でstdinから編集されたファイルのパスを取り出し、Prettierに渡しています。`jq` がない場合は `brew install jq`（macOS）または `apt-get install jq`（Ubuntu）でインストールしてください。

`/hooks` でHookが表示されているのに動かない場合は、ツール名の大文字小文字を真っ先に確認しましょう。

## 落とし穴その2: exit codeの意味を理解していない

Hooksは**exit code（終了コード）で動作を制御します**。ここを誤解すると、ブロックしたつもりのコマンドが素通りしたり、意図せずエラーになったりします。

exit codeの意味は3パターンです。

| exit code | 意味 |
| --- | --- |
| `0` | 正常終了。アクションはそのまま進む |
| `2` | アクションをブロックする。stderrの内容がClaudeへのフィードバックになる |
| それ以外 | アクションは進む。エラーとして記録される（ブロックにはならない！） |

特にハマりやすいのが「exit 1でブロックできると思っていた」ケースです。**exit 1はブロックではありません。**

`.env` や `package-lock.json` などの保護ファイルへの書き込みをブロックするスクリプトを例に見てみましょう。

まず `.claude/hooks/protect-files.sh` を作成します。

```
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

PROTECTED_PATTERNS=(".env" "package-lock.json" ".git/")

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH は保護されたファイルです ('$pattern' に一致)" >&2
    exit 2  # これがブロックのexit code
  fi
done

exit 0
```

実行権限を付与します。

```
chmod +x .claude/hooks/protect-files.sh
```

`.claude/settings.json` に登録します。

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

stderrに書いたメッセージはClaudeへのフィードバックとして届くので、Claudeは「なぜブロックされたか」を理解して別のアプローチを試みます。これが地味に便利です。

### 動作確認の方法

スクリプトが正しく動くか手動でテストできます。

```
echo '{"tool_name":"Write","tool_input":{"file_path":"/project/.env"}}' | ./protect-files.sh
echo $?  # exit codeを確認
```

期待値は `2` です。

## 落とし穴その3: シェルプロファイルのechoがJSONを壊す

これが一番気づきにくい落とし穴です。**`~/.zshrc` や `~/.bashrc` に `echo` 文を書いている場合、Hookが正常に動かないことがあります。**

Claude Codeはhookスクリプトを実行するとき、シェルのプロファイル（`~/.zshrc` など）を読み込みます。もしそこに無条件の `echo` が書いてあると、hookのstdout（JSON）の前にその出力が混じります。

```
Shell ready on arm64
{"decision": "block", "reason": "Not allowed"}
```

Claude CodeはこれをJSONとしてパースしようとして失敗します。エラーメッセージは「JSON validation failed」系のものです。

修正方法はシンプルで、`~/.zshrc` や `~/.bashrc` の `echo` をインタラクティブシェルのときだけ実行するように条件分岐します。

```
# ~/.zshrc または ~/.bashrc
if [[ $- == *i* ]]; then
  echo "Shell ready"
fi
```

`$-` にシェルのフラグが入っており、`i` がインタラクティブモードを意味します。Hookは非インタラクティブなシェルで実行されるため、この条件下では `echo` がスキップされます。

## 設定ファイルはどこに置くべきか

Hookの設定場所によって**スコープが変わります**。

| 設定ファイルの場所 | 適用範囲 | リポジトリで共有できるか |
| --- | --- | --- |
| `~/.claude/settings.json` | 自分の全プロジェクト | できない（ローカル限定） |
| `.claude/settings.json` | そのプロジェクトのみ | できる（コミット可能） |
| `.claude/settings.local.json` | そのプロジェクトのみ | できない（.gitignore推奨） |

通知やデスクトップ連携など**個人の好みに関するもの**はグローバル設定（`~/.claude/settings.json`）へ。コードフォーマットや保護ファイルルールなど**プロジェクト全体で統一したいもの**はプロジェクト設定（`.claude/settings.json`）へ、というのが基本的な考え方です。

## より高度な使い方

### コンテキスト圧縮後に重要情報を再注入する

長いセッションではコンテキストが圧縮され、大事な情報が失われることがあります。`SessionStart` の `compact` マッチャーを使えば圧縮後に自動で情報を再注入できます。

```
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Reminder: パッケージマネージャーはnpmではなくBunを使う。コミット前に bun test を実行する。現スプリント: 認証リファクタリング'"
          }
        ]
      }
    ]
  }
}
```

stdoutに書いた内容がClaudeのコンテキストに追加されます。`echo` をスクリプトに置き換えて動的な情報（直近のgitログなど）を渡すこともできます。

### 特定の許可ダイアログを自動承認する

毎回同じ許可ダイアログが出て煩わしいなら、`PermissionRequest` Hookで自動承認できます。`ExitPlanMode`（プランを提示した後の「進めますか？」確認）を自動承認する例です。

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

`matcher` を `.*` や空文字にして全ての許可ダイアログを自動承認するのは危険です。ファイル書き込みやシェルコマンドも自動承認されてしまいます。matcherは必ず絞り込んで使いましょう。

### AIに判断させるPrompt-based Hooks

「動かしていいかどうかをルールでなくAIに判断させたい」という場面では `type: "prompt"` が使えます。`Stop` Hookに設定すると、Claudeが止まろうとするたびにハイクモデル（デフォルトはHaiku）が「タスクが完了しているか」を確認します。

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "依頼されたタスクが全て完了しているか確認してください。未完了があれば {\"ok\": false, \"reason\": \"残っているタスクの内容\"} で返してください。"
          }
        ]
      }
    ]
  }
}
```

`ok: false` が返るとClaudeは作業を続け、`reason` が次の指示になります。

## デバッグ方法

Hookが意図通りに動かないときのチェックリストです。

**まず `/hooks` コマンドで確認する**  
設定したHookが一覧に表示されているか確認します。表示されていなければ、JSONの文法エラーか、設定ファイルの場所が間違っています。

**ログを有効にする**  
起動時に `claude --debug-file /tmp/claude.log` を付けると詳細ログが書き出されます。別ターミナルで `tail -f /tmp/claude.log` しながら作業すると、どのHookが何のexit codeで終わったかが分かります。

**スクリプトを手動テストする**  
Hookスクリプトはシェルから直接テストできます。

```
echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | ./my-hook.sh
echo $?
```

これで問題が切り分けられます。Claude Codeから呼ばれたときだけ動かないなら、シェルプロファイルの問題（落とし穴その3）を疑いましょう。

**`Ctrl+O` でトランスクリプトを確認する**  
セッション中に `Ctrl+O` を押すとトランスクリプトビューが開き、Hookの実行結果のサマリーが確認できます。

## まとめ

Hooksは「LLMに毎回お願いする」のではなく「Claude Codeの動作を確定的にコントロールする」仕組みです。設定自体は数行のJSONで済みますが、落とし穴を知らないと原因不明の不動作にはまります。

今回紹介した3つの落とし穴を再整理します。

1. **matcherは大文字小文字を区別する** → ツール名は `Edit`、`Bash` のように先頭大文字
2. **ブロックはexit 2。exit 1ではブロックにならない** → exit codeの意味を覚える
3. **シェルプロファイルの無条件echoがJSONを壊す** → `if [[ $- == *i* ]]` で条件分岐

まず試すなら**デスクトップ通知Hook**がおすすめです。設定が一番シンプルで、動作確認もしやすいです。動いたら次に**自動フォーマットHook**を追加すると、すぐに実務での恩恵を感じられます。
