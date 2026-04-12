---
id: "2026-04-12-claude-codeのhookどれを入れればいい5つの質問で最適な安全設定が分かるツールを作った-01"
title: "Claude Codeのhook、どれを入れればいい？——5つの質問で最適な安全設定が分かるツールを作った"
url: "https://qiita.com/yurukusa/items/6fa3ebbb45406547d2ff"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "qiita"]
date_published: "2026-04-12"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

Claude Codeにhookを入れたいけど、650個以上もあるとどれを選べばいいかわからない。

そこで[Hook Selector](https://yurukusa.github.io/cc-safe-setup/hook-selector.html)を作った。5つの質問に答えるだけで、自分の使い方に合ったhookセットが出てくる。

## 使い方

1. [Hook Selector](https://yurukusa.github.io/cc-safe-setup/hook-selector.html)を開く
2. 5つの質問に答える（30秒）
3. 推薦されたhookのインストールコマンドをコピペ

質問の内容:
- Claude Codeの使い方（対話型/半自律/完全自律）
- 一番心配なこと（ファイル削除/トークン消費/秘密漏洩/コード品質）
- 技術レベル
- サブエージェント/MCPの使用有無
- 過去の事故経験

## なぜ作ったか

cc-safe-setupに650以上のexample hookがあるが、「全部入れる」のは無意味だし、「1つずつ読んで選ぶ」の
