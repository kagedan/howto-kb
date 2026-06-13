---
id: "2026-06-12-claude-code-hooks-使ってみたネコ通知ᐞᐞ-01"
title: "Claude Code hooks 使ってみた【ネコ通知】₍ᐞ•༝•ᐞ₎"
url: "https://zenn.dev/michan74/articles/8906dc0e93eddc"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "LLM", "zenn"]
date_published: "2026-06-12"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

Claude Codeのhooksの噂は聞いたことありましたが、実際に設定したら何が変わるのかを試してみました。

# Claude Code hooksとは？？？

公式ドキュメントを参照します。

> フックは、Claude Code のライフサイクル内の特定のポイントで自動的に実行されるユーザー定義のシェル コマンド、HTTP エンドポイント、または LLM プロンプトです。  
> 引用: [Hooks リファレンス - Claude Code Docs](https://code.claude.com/docs/ja/hooks)

噛み砕くと、セッション開始やツール(MCP)の利用やサブエージェントの開始など特定のポイントをフックに、好きなコマンドやプロンプトを実行できる機能です！  
例えば毎回セッション開始時に、「くま！」と挨拶させたり、AIによるコード修正後にテストを自動で実行させられたりすることができます。

フックにできるポイントは、[Hooks フック ライフサイクル - Claude Code Docs](https://code.claude.com/docs/ja/hooks#hook-lifecycle)に一覧になっています。

# 試してみる！

[hooks でアクションを自動化する - Claude Code Docs](https://code.claude.com/docs/ja/hooks-guide) に従って、試してみました。

`.claude/settings.json`に以下の記述を書くだけです！

settings.json

```
"hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"くまったな〜\" with title \"´•ᴥ•` Claude Code\"'"
          }
        ]
      },
    ],
  }
```

Claude Codeに指示を出し、別のアプリに切り替えて待っていると、Claude Codeの応答が終わったタイミングで通知センターに「くまったな〜」が届きました！

![](https://static.zenn.studio/user-upload/01aff2544e7c-20260611.png)

今回は実際にhooksを使って、通知とテストの自動実行を設定してみました。

# hooksで通知を変更してみる

試したのが通知のhookだったので、通知を変更して見ようかなと思います。  
やりたいことはこうです。

* **作業が終わったとき** → Claudeが終わったことを知れる通知音
* **許可を求めているとき** → 違う通知音で「確認が必要」と分かる
* **ファイルを変更するとき** → さらに別の音で「ファイル変更の確認」と知れる

## matcherでの判定

`Notification` hookのmatcherには通知の種類を指定できます。空文字 `""` にするとすべての通知で発火しますが、種類を指定することで特定のタイミングだけに絞り込めます。  
以下が一覧です。↓↓ (このあたりの情報は公式ドキュメントに記載があります。)

| matcher | タイミング |
| --- | --- |
| `idle_prompt` | Claudeが応答を終えて入力待ちになったとき |
| `permission_prompt` | ツール実行の許可ダイアログが出るとき |
| `auth_success` | 認証完了時 |
| `elicitation_dialog` | MCPサーバーがフォームを開くとき |
| `elicitation_complete` | MCPフォームが閉じられたとき |
| `elicitation_response` | MCPフォームの応答がサーバーに返されるとき |
| `""` (空文字) | 上記すべて |

今回は、`permission_prompt: ツール実行の許可ダイアログが出るとき`で別の通知音にしたいので、以下のように設定します。

```
{
  "matcher": "permission_prompt",
  "hooks": [
    {
      "type": "command",
      "command": "osascript -e 'display notification \"よろくま〜〜\" with title \"´•ᴥ•` Claude Code\"' && afplay /Users/dorayaki/Downloads/cat.mp3"
    }
  ]
}
```

## 最終的な通知系hooks

許可を求めているときにネコの鳴き声(甘え声)を出すようにしました。ネコと作業している気分になり、癒されます。

* **作業が終わったとき** → 普通の通知音
* **許可を求めているとき** → ネコの鳴き声
* **ファイルを変更するとき** → ネコの鳴き声×2

「作業が終わったとき」 と 「許可を求めているとき」 の判別は`Notification`hookのmatcherで実現できましたが、、「ファイルを変更するとき」 の判別が`Notification`hookのmatcherでは不可能だったので、`PreToolUse`hookを使いました。`PreToolUse` ではstdinで `tool_name` や `tool_input` が直接渡ってくるので、matcherでツール名を絞り込むことができます。

settings.json

```
"hooks": {
  "Notification": [
    {
      "matcher": "idle_prompt",
      "hooks": [
        {
          "type": "command",
          "command": "osascript -e 'display notification \"くまったな〜\" with title \"´•ᴥ•` Claude Code\"' && afplay /System/Library/Sounds/Tink.aiff"
        }
      ]
    },
    {
      "matcher": "permission_prompt",
      "hooks": [
        {
          "type": "command",
          "command": "osascript -e 'display notification \"確認してください！\" with title \"´•ᴥ•` Claude Code\"' && afplay ~/Downloads/cat.mp3"
        }
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "Edit|Write|MultiEdit",
      "hooks": [
        {
          "type": "command",
          "command": "afplay -t 0.3 ~/.claude/.dorayaki/sounds/cat.mp3 && afplay -t 0.3 ~/.claude/.dorayaki/sounds/cat.mp3"
        }
      ]
    }
  ]
}
```

# hooksで自動でミニテストを動かしてみる

単純にテスト作成や修正したタイミングでミニテストが動くと楽だなと思ったので追加してみました。

## 複雑な条件での判定

通知の設定の際は、matcherでの判定をしましたが、今回は「テストファイルを編集した時」というさらに複雑な条件での判定が必要となります。その場合、コマンド側で制御します。

hookコマンドにはstdinでJSON形式のデータが渡ってくるので、`jq` で値を取り出し、中身によって処理を分岐させることができます。

例えば、`PostToolUse` hookで「`backend-application` 配下の `_test.rb` ファイルを編集したときだけテストを実行する」という条件はこう書けます。

```
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

BACKEND_DIR="/path/to/main-application/backend-application"

# backend-application 内の _test.rb ファイルのみ対象
if [[ "$FILE_PATH" != "$BACKEND_DIR"*"_test.rb" ]]; then
  exit 0
fi

bundle exec rails test "${FILE_PATH#$BACKEND_DIR/}"
```

## 最終的なテストのhooks

hooksでスクリプトを呼ぶように設定しておきます。

settings.json

```
"hooks": {
  "PostToolUse": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "type": "command",
          "command": "/path/to/main-application/.claude/hooks/run_minitest_on_test_change.sh"
        },
        {
          "type": "command",
          "command": "/path/to/main-application/.claude/hooks/run_rubocop_on_edit.sh"
        }
      ]
    }
  ]
}
```

実行する用のスクリプトです。↓↓

ファイルのディレクトリと名前を確認して、テストを実行します。  
main-application  
|- frontend-application  
|- backend-application <- このディレクトリ内の`*_test.rb`のファイル変更のみテストを実行する

また、デフォルトだとログがどこにも出ていないようだったので、デバッグ用にtmpファイルにログをたくさん出すようにしました。  
結果の通知もエラーでスクリプト自体失敗する時以外はどこから確認するかわからなかったので、通知音を仕込むようにしました。これはなんだか正しいのかよくわかりません。hooksは裏で勝手に動いている想定で、結果を確認するものではないのかもしれません。結果を確認するのであれば、コマンド実行して待っておけばいいのかもしれません。。。  
一旦、今回は不便だったので通知を仕込みました。

run\_minitest\_on\_test\_change.sh

```
#!/bin/bash
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "Write" ]]; then
  exit 0
fi

BACKEND_DIR="/path/to/main-application/backend-application"
if [[ "$FILE_PATH" != "$BACKEND_DIR"*"_test.rb" ]]; then
  exit 0
fi

RELATIVE_PATH="${FILE_PATH#$BACKEND_DIR/}"

bundle exec rails test "$RELATIVE_PATH" 2>&1 | tee /tmp/minitest_result.log
EXIT=${PIPESTATUS[0]}

if [ "$EXIT" -eq 0 ]; then
  osascript -e 'display notification "✅ テスト通過！" with title "Claude Code"'
else
  osascript -e 'display notification "❌ テスト失敗" with title "Claude Code"'
fi
```

# 今後

hooksの使い方がわかったので、最強のhooks編成を考えていきます。  
通知に関しては今回は通知音のみの実装となりましたが、今後ディスプレイ全体をチカチカさせたり、光る外部デバイスを光らせるなど、自分専用にカスタマイズしていきたいですね。
