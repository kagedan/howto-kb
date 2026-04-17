---
id: "2026-04-16-第1回claude-code流出に学ぶチャットボットをエージェントに変えるreactループの正体-01"
title: "第1回：【Claude Code流出に学ぶ】チャットボットを「エージェント」に変えるReActループの正体"
url: "https://zenn.dev/guba98/articles/0e98bf54b43960"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-16"
date_collected: "2026-04-17"
summary_by: "auto-rss"
query: ""
---

「プロンプトエンジニアリングの終焉と、AIソフトウェアエンジニアリングの幕開け」
これが、2026年3月に起きたAnthropicの公式CLIツール「Claude Code」の約51万行に及ぶソースコード流出事件が我々に突きつけた現実です。
AIを「単なるチャットボット」から「自律的に仕事をするエージェント」へと昇華させるための魔法は、複雑なプロンプトの奥底にはありませんでした。それは、我々ソフトウェアエンジニアが日常的に書いている、泥臭くも堅牢な「ループ構造」の中にあったのです。
今回は、流出コードから読み解くエージェントの心臓部、「ReAct（推論と行動）ループ」の正体に迫ります。...
