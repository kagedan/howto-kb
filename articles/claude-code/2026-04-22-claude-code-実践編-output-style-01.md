---
id: "2026-04-22-claude-code-実践編-output-style-01"
title: "Claude Code 実践編 — Output Style"
url: "https://qiita.com/sugo_mzk/items/30da0a75b55cd7abe7c3"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "qiita"]
date_published: "2026-04-22"
date_collected: "2026-04-23"
summary_by: "auto-rss"
---

# Claude Code 実践編 — Output Style

## はじめに — 「絶対おっしゃる通りです！」にモヤっとする

Claude Code を日常的に使っていると、ある瞬間に手が止まる。

```
You're absolutely right!
Let me fix that right away.
...
I have successfully updated the code!
```

テストは動かしていない。tsc も通していない。それなのに「successfully」と言い切って turn を閉じてくる。あるいは自分のコードの明確なバグを「Good catch!」と言ってから直す。

最初は「プロンプトに "簡潔に、同調するな" と書けば直るだろう」と思っていた。直らなかった。CLAUDE.md に書いても効きが悪い。`--append-system-prompt` に突っ込んでも挙動はあまり変わらない。

結局 npm で配布されている `@anthropic-ai/claude-code` パッケージの `cli.js`（Node.js バンドル）を開
