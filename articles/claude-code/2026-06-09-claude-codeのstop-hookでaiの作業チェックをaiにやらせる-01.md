---
id: "2026-06-09-claude-codeのstop-hookでaiの作業チェックをaiにやらせる-01"
title: "Claude CodeのStop hookでAIの作業チェックをAIにやらせる"
url: "https://qiita.com/ohakutsu/items/1006542f6aff348a707c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "qiita"]
date_published: "2026-06-09"
date_collected: "2026-06-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

Claude CodeにはAgent-based hookがあります。
[Agent-based hooks | Automate actions with hooks - Claude Code Docs](https://code.claude.com/docs/en/hooks-guide#agent-based-hooks)

Agent-based hookでは、サブエージェントがツール（Read, Grepなど）を使って検証ができます。
そのため、command hookでは検証しづらいようなことをエージェントに検証させることができるため、メインエージェントによる対応漏れや検証漏れを確認できます。

## 使い方

Agent-based hookの定義は`"type": "agent"`とするだけでできます。

以下は、公式ドキュメントから引っ張ってきたユニットテストが通ることを検証してから停止を許可するStop hookの例です。
サブエージェントがチェックし、NGだった場合は修正をさせることができます。

```json:settings.json
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

Agent-based hookの制約としては、サブエージェントは最大で50回のターンまでという点です。
基本は収まるような気はしますが、一応ターン数の上限があるのは覚えておくと良さそうです。

## さいごに

Agent-based hookを使うと、「AIの作業チェックをAIにやらせる」ことができて便利です。
なお、Stop hookで作業を継続させると無限ループが気になると思いますが、それについても記事を書いているので読んでいただけると嬉しいです。

https://qiita.com/ohakutsu/items/bc97ebfdc87877b94561

## 参考

- [Agent-based hooks | Automate actions with hooks - Claude Code Docs](https://code.claude.com/docs/en/hooks-guide#agent-based-hooks)
