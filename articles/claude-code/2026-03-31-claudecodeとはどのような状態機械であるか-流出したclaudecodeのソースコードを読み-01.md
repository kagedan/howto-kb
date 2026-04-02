---
id: "2026-03-31-claudecodeとはどのような状態機械であるか-流出したclaudecodeのソースコードを読み-01"
title: "ClaudeCodeとは、どのような状態機械であるか? ~ 流出したClaudeCodeのソースコードを読み解いてみた ~"
url: "https://zenn.dev/jintarotanba/articles/a5018cbed152ed"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "LLM", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

LLM APIをどう実行するか という観点から Claude Code を読むと、このコードベースは「高機能なAIエージェントの魔法の塊」ではありません。
むしろ、かなり明確に次の3層へ分解できます。


request compiler
会話状態を、毎ターン API に送れる payload へ再コンパイルする層

runtime harness
その payload を実際に API へ流し、ストリームを解釈し、ツール実行や権限処理を仲介する層

recursive state machine
assistant -&gt; tool_use -&gt; tool_result -&...
