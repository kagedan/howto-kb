---
id: "2026-04-09-zettelkastenに基づくllmエージェントのメモリ設計a-mem論文解説-01"
title: "Zettelkastenに基づくLLMエージェントのメモリ設計：A-Mem論文解説"
url: "https://zenn.dev/tsurubee/articles/amem-llm-agent-memory-design"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "LLM", "zenn"]
date_published: "2026-04-09"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

はじめに：LLMエージェントはどう記憶するか
Claude CodeのようなAIコーディングエージェントは、過去のことをどのように記憶しているのだろうか。まず基本となるのはコンテキストウィンドウである。ユーザーとの対話履歴やコードの内容は、コンテキストとしてモデルに渡される。モデルはこのコンテキストの範囲内であれば、過去のやり取りを参照して一貫した応答を返すことができる。しかし、コンテキストウィンドウには上限がある。対話が長くなれば古い情報は押し出されていくし、そもそもセッションが終われば対話履歴はリセットされる。コンテキストだけでは、長期的な記憶を維持することはできない。
そこで、...
