---
id: "2026-06-20-claude-code-の-hooks-で開発フローを自動化する-設定から実践まで-01"
title: "Claude Code の hooks で開発フローを自動化する — 設定から実践まで"
url: "https://zenn.dev/moha0918/articles/daily-cc-hooks-20260406"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-06-20"
date_collected: "2026-06-21"
summary_by: "auto-rss"
query: ""
---

## きっかけ

Claude Code を使いはじめた頃、ちょっと不満だったことがある。長いバッシュコマンドが終わっても音も通知も出ない。別のウィンドウで作業してると「あ、もう終わってた」という状況が何度も続いた。

調べてみると **hooks** という機能があることを知った。ツールの実行前後や、セッション開始時などに任意のシェルコマンドを差し込める仕組みだ。これがかなり便利で、今では自分のワークフローに欠かせなくなっている。

この記事では hooks の基本的な使い方から、実際に役立った設定例まで書いていく。

---

## hooks とは何か

Claude Code の hooks は、特定のイベントが発生したときに **任意のシェルコマンドを自動で実行する** 仕組み。設定は `~/.claude/settings.json` に書く。

対応しているイベントは次の6種類。

| イベント | タイミング |
| --- | --- |
| `PreToolUse` | Claude がツールを実行する直前 |
| `PostToolUse` | ツールの実行が完了した直後 |
| `Notification` | Claude から通知が来たとき |
| `Stop` | Claude の応答が終了したとき |
| `SubagentStop` | サブエージェントが終了したとき |
| `SessionStart` | セッションが開始されたとき |

イベントごとに実行するコマンドを登録しておくと、Claude が勝手にそのコマンドを呼んでくれる。

---

## 設定の書き方

`~/.claude/settings.json` の `hooks` キーに設定する。基本構造はこう。

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo '✅ Bash コマンド完了'"
          }
        ]
      }
    ]
  }
}
```

`matcher` でどのツールに反応するかを絞り込める。`Bash`、`Write`、`Edit`、`Read` など、Claude Code が使うツール名を指定する。省略するか空文字にすると全ツールに反応する。

hook の `type` は今のところ `command` のみ。`command` に実行したいシェルコマンドを書く。

---

## 実際に使っている設定例

### 1. Bash 完了時に通知を鳴らす

長時間かかる処理（ビルド、テスト、デプロイなど）が終わったら音を出したかった。macOS なら `say` コマンドが使える。

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "say '処理が完了しました' 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

Linux なら `notify-send` や `paplay` に置き換えればいい。`2>/dev/null || true` をつけておくと、コマンドが使えない環境でもエラーにならない。

### 2. 危険なコマンドを事前にチェックする

`PreToolUse` を使うと、Claude がツールを実行する前に介入できる。たとえば `rm -rf` が含まれているコマンドをログに記録しておく設定。

```
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"[$(date)] PRE: $CLAUDE_TOOL_INPUT\" >> ~/claude-bash-log.txt"
          }
        ]
      }
    ]
  }
}
```

`CLAUDE_TOOL_INPUT` という環境変数にツールへの入力内容が入ってくる。Bash ツールなら実行しようとしているコマンド文字列が取れる。

実際のプロジェクトでは、本番環境の設定ファイルを書き換えようとしたときのログが残っていて助かったことがある。「あのとき何が起きてたんだっけ」が追えるのは地味に便利。

### 3. セッション開始時に環境を整える

`SessionStart` は Claude Code のセッションが始まったときに1回だけ実行される。プロジェクトのセットアップを自動化するのに使える。

```
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cd /path/to/project && npm install --silent 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

チームで共有している設定なら、セッション開始のたびに依存関係が最新になるので「なんか動かない」が減る。

### 4. Claude の回答終了を検知する

`Stop` イベントは Claude が1つの回答を書き終えたときに発火する。長い作業を依頼しているときに、作業完了を検知して次のアクションを促すような使い方ができる。

```
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude が応答を完了しました\" with title \"Claude Code\"' 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

これで macOS の通知センターに通知が飛ぶ。別画面で作業していても気づけるようになった。

---

## hooks から渡される環境変数

hooks 実行時にはいくつかの環境変数が自動でセットされる。把握しておくと条件分岐などに使える。

| 変数名 | 内容 |
| --- | --- |
| `CLAUDE_TOOL_NAME` | 実行されたツール名（例: `Bash`, `Write`） |
| `CLAUDE_TOOL_INPUT` | ツールへの入力（JSON 文字列） |
| `CLAUDE_TOOL_OUTPUT` | ツールの出力（PostToolUse のみ） |
| `CLAUDE_SESSION_ID` | 現在のセッション ID |

`CLAUDE_TOOL_INPUT` は JSON 文字列なので、`jq` で特定のフィールドだけ取り出すことも可能。

```
# Bash ツールの実行コマンドだけ取り出す例
echo "$CLAUDE_TOOL_INPUT" | jq -r '.command // empty'
```

---

## ハマったポイント

### コマンドが失敗するとセッションが止まる

`PreToolUse` の hook でコマンドが失敗（exit code 非ゼロ）を返すと、Claude のツール実行がブロックされる。意図的に止めたいときは使えるが、単なる通知目的なら `|| true` を末尾につけておくのが無難。

### JSON のエスケープに注意

`settings.json` は JSON なのでダブルクォートのエスケープが必要になる場面がある。複雑なコマンドはシェルスクリプトに切り出して、hook からはそのスクリプトを呼ぶ形にすると管理しやすい。

```
{
  "type": "command",
  "command": "~/.claude/hooks/post-bash.sh"
}
```

スクリプトファイルに分けると、エスケープ問題からも解放されるし、後から変更もしやすい。

### matcher の大文字小文字

`matcher` は大文字小文字を区別する。`bash` ではなく `Bash`、`write` ではなく `Write` と書かないと反応しない。最初ここで詰まって30分溶かした。

---

## まとめ

hooks は「Claude Code に手を入れずに周辺の自動化をする」のに適した機能。通知・ログ・環境セットアップあたりから始めると効果を実感しやすい。

自分が今使っている最小限の設定はこれ。

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "say done 2>/dev/null || true"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"完了\" with title \"Claude Code\"' 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

シンプルだけど、これだけで Claude 作業中に他のことをしていても戻るタイミングがわかるようになった。興味があれば少しずつ育てていくといい。
