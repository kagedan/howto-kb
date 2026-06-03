---
id: "2026-06-02-claude-code-の-hooks-で入力構造がわからない問題を解決するヘルパーフックパターン-01"
title: "Claude Code の Hooks で「入力構造がわからない」問題を解決するヘルパーフックパターン"
url: "https://qiita.com/takahashi-ry/items/a7e2d68b2402502ada8f"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "qiita"]
date_published: "2026-06-02"
date_collected: "2026-06-03"
summary_by: "auto-rss"
query: ""
---

## はじめに

Anthropic Academy の Claude Code のコースで特に「ヘルパーフックパターン」が面白かったのでまとめようかと思います。

:::note info
Anthropic Academy とはAnthropicが無料で公開している学習教材です。

Get in the know with Anthropic resources. From API development guides to enterprise deployment best practices, the academy has you covered.
訳 : Anthropicのリソースを活用して、知識を深めましょう。API開発ガイドからエンタープライズ展開のベストプラクティスまで、アカデミーがあらゆるニーズに対応します。
:::

Claude Code の Hooks 機能は便利なのですが、**フックタイプによって stdin に入力される JSON の構造が異なる**という仕様があります。事前に構造がわからない状態でフックを書くのは困難です。

## 背景：Claude Code の Hooks

Hooks は Claude Code のライフサイクルの特定のタイミングで外部コマンドを実行する仕組みです。

よく使われるのは `PreToolUse`（ツール使用前）と `PostToolUse`（ツール使用後）ですが、実は他にも多くのフックタイプが存在します。

| フック名 | 実行タイミング |
| --- | --- |
| `PreToolUse` | ツールが使用される直前 |
| `PostToolUse` | ツールが使用された直後 |
| `Notification` | ツール使用許可が必要時、または 60 秒アイドル後 |
| `Stop` | Claude Code が応答を終了したとき |
| `SubagentStop` | サブエージェント（Task）が完了したとき |
| `PreCompact` | コンパクト処理実行直前 |
| `UserPromptSubmit` | ユーザーがプロンプトを送信した後、処理前 |
| `SessionStart` | セッション開始・再開時 |
| `SessionEnd` | セッション終了時 |

利用イメージの例を挙げるとすると、プログラムの編集を終えた後に必ず型チェックを走らせるといったようなことです。あとは `.env` を読ませないようにするとかですね。

## 問題：二段構えの複雑さ

ここが本題の入り口です。

フックタイプによって stdin に入力される JSON の構造が異なる**うえに**、`PreToolUse` や `PostToolUse` の場合は**呼び出されたツールによって `tool_input` の中身も変わる**という、二段構えの複雑さがあります。

### 具体例で見る違い

`PostToolUse` フックで `TodoWrite` ツールの使用を監視している場合、以下のような入力が stdin に渡されます。

```json
{
  "session_id": "9ecf22fa-edf8-4332-ae85-b6d5456eda64",
  "transcript_path": "<path_to_transcript>",
  "hook_event_name": "PostToolUse",
  "tool_name": "TodoWrite",
  "tool_input": {
    "todos": [
      { "content": "write a readme", "status": "pending", "id": "1" }
    ]
  },
  "tool_response": {
    "oldTodos": [],
    "newTodos": [
      { "content": "write a readme", "status": "pending", "id": "1" }
    ]
  }
}

```

一方、`Stop` フックの入力は全く異なる構造になります。

```json
{
  "session_id": "af9f50b6-f042-4773-b3e2-c3a4814765ce",
  "transcript_path": "<path_to_transcript>",
  "hook_event_name": "Stop",
  "stop_hook_active": false
}

```

`tool_name` も `tool_input` も `tool_response` も存在しません。フックタイプが変わるとフィールド構成がガラッと変わるのです。

さらに `PostToolUse` 内で `tool_name` が `Write` なら `tool_input` は `{ "content": "...", "filePath": "..." }` になり、`Bash` なら `{ "command": "..." }` になります。ツールが変わるたびに中身が変わる。

**つまり：フックタイプ × ツール名の 2 次元で入力構造が変わる。**


## 解決：ヘルパーフックパターン

入力構造が事前にわからない状態で本番のフックを書くのは困難です。公式レッスンでは以下のようなヘルパーフックを最初に作成して、実際の入力を観察するアプローチを推奨しています。

```json
{
  "PostToolUse": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "jq . > post-log.json"
        }
      ]
    }
  ]
}

```

### このパターンの仕組み

1. **`matcher: "*"`** — 全てのツール呼び出しをキャッチ
2. **`jq .`** — stdin の JSON を整形して出力
3. **`> post-log.json`** — ファイルに保存

これで実際にどの構造の入力が来るかを確認できるので、本番のフックを書く際の参考になります。

### 実践的な使い方

```json
{
  "PreToolUse": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "jq . > pre-log.json"
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "jq . > post-log.json"
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "jq . > stop-log.json"
        }
      ]
    }
  ]
}

```

複数のフックタイプに同時にヘルパーフックを設定して、一度に全構造を観察することもできます。


実はフックの基本構造は公式の [Hooks Reference](https://code.claude.com/docs/en/hooks) に記載されています。しかし、tool_input の中身は「呼び出されるツール（組み込みツールやMCPで追加した独自ツールなど）」によって動的に変わるため、ドキュメントだけでは完全に網羅できません。


## まとめ

まだまだHooksを使いこなせていませんが、これを機になにか設定してみようと思いました。もし、こういう使い方できるよ、便利だよといったおすすめの方法があれば教えてください。

---

*本記事は Anthropic Academy のレッスンを元に独自に要約・再構成したものです。詳細は [Anthropic Academy](https://anthropic.skilljar.com/) 公式ページをご参照ください。*
