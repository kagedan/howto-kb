---
id: "2026-06-16-claudeでヘッドレスclaude-pとapiキーを使い分けてる方への注意事項-01"
title: "Claudeでヘッドレス（claude -p）とAPIキーを使い分けてる方への注意事項"
url: "https://note.com/it_work_labo/n/n2e4b86552661"
source: "note"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "note"]
date_published: "2026-06-16"
date_collected: "2026-06-16"
summary_by: "auto-rss"
query: ""
---

ご存じかもしれませんが、6/15 に課金まわりの仕様が変わっています。自前のツールから Claude Codeなどをヘッドレス（claude -p）で呼んでいる人向けの注意喚起です。

## 注意事項

対話モードなら API キーを使うか聞かれるみたいですが、非対話（ヘッドレス）の -p では確認が出ません。よって、自作ツールで.env や config 経由で ANTHROPIC\_API\_KEY が環境に残っていて、それを claude -p の subprocess が引き継いでいる場合、「**サブスクではなくAPIが優先され、課金が走ります**」

※[公式ヘルプ](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan)でも明言されています。

## 対策案

## ついでに：2026/6/15 の変更

キーが無くサブスク認証で動いていても、6/15 以降は claude -p / Agent SDK の利用が対話枠とは別枠の **Agent SDK クレジット**（標準 API レート）から引かれます。「CLI ＝定額」ではなくなりました。

急に高額な課金が発生しないように、ご自身の環境を確認してください！  
この辺りは修正が入ると思いますが、まずは注意喚起として告知しておきます。

最後までお読み頂き、ありがとうございました。
