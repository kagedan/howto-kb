---
id: "2026-04-16-第2回claude-code流出に学ぶreduxは不要aiエージェントを支える34行-01"
title: "第2回：【Claude Code流出に学ぶ】Reduxは不要？AIエージェントを支える「34行」"
url: "https://zenn.dev/guba98/articles/889d141406e46d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "LLM", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

フロントエンドエンジニアの皆様、深呼吸して聞いてください。
50万行規模の商用AIエージェントOSである「Claude Code」は、ReduxもZustandも、その他の巨大な状態管理ライブラリも使っていませんでした。
彼らがAIの「記憶（コンテキスト）」と「UI状態」を管理するために書いていたのは、依存関係ゼロのわずか34行の自作Storeだったのです。今回は、この極小Storeの設計思想から、AI時代のシステムアーキテクチャを紐解きます。
巨大ライブラリを捨てたAnthropicの決断
AIエージェントは、ユーザーの入力、LLMの思考状態、ツールの実行結果など、膨大で非同期な状態...
