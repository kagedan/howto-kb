---
id: "2026-07-06-claude-codeでworktree作成時にmise-trustを自動実行する-01"
title: "Claude Codeでworktree作成時にmise trustを自動実行する"
url: "https://qiita.com/yuta0709dev/items/74a77195e37e50bda29c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

最近はClaudeデスクトップアプリのCodeタブを使って、PRごとにWorktreeを作成して実装させています。

miseを使っているプロジェクトだと、Worktree作成直後は`mise.toml`がtrustされていない状態のため、Claudeの作業が途中で止まってしまうことがあり地味に面倒でした。そこで、Worktreeで作業を始めるタイミングで自動的に`mise trust`が実行されるようにしたので、その設定を共有します。

## 実現方法

Claude CodeのHooksを使います。

https://code.claude.com/docs/ja/hooks

Hooksは、Claude Codeのライフサイクルの特定のタイミングで、任意のシェルコマンドを自動実行できる機能です。

ClaudeデスクトップでWorktreeのセッションを開始したタイミングで`mise trust`を実行するには、`~/.claude/settings.json`の`hooks`に次のように設定します。

```json:~/.claude/settings.json
{
    "hooks": {
        "SessionStart": [
          {
            "hooks": [
              {
                "type": "command",
                "command": "mise trust"
              }
            ]
          }
        ]
    }
}
```

:::note info
この例ではグローバルな設定を書き換えていますが、プロジェクトごとに設定したい場合は、

https://code.claude.com/docs/ja/settings#what-uses-scopes

に書かれているプロジェクト単位の`settings.json`を使いましょう。Git管理せず自分だけに適用したい場合は`settings.local.json`が使えます。
:::

ちなみにドキュメントを見ると、それらしいフックイベントとして「WorktreeCreate」があります。ただ、これはClaude CodeがWorktree作成時に行うgit操作などを丸ごと置き換えるためのものです。今回のように「Worktreeの作成自体はClaude Codeのデフォルトに任せて、作成後にコマンドを実行したい」というケースでは、「SessionStart」を使うのが良さそうです。

## 最後に

Worktreeを使った開発を快適にするための設定を紹介しました。

もっと良い方法があるかもしれないので、ご存知の方はぜひコメントで教えてください!
