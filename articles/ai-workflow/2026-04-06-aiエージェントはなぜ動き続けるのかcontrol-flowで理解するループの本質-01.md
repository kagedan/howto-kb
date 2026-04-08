---
id: "2026-04-06-aiエージェントはなぜ動き続けるのかcontrol-flowで理解するループの本質-01"
title: "AIエージェントはなぜ動き続けるのか｜Control Flowで理解するループの本質"
url: "https://zenn.dev/startspace/articles/15e9e68d8346a7"
source: "zenn"
category: "ai-workflow"
tags: ["LLM", "zenn"]
date_published: "2026-04-06"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

導入｜なぜAIエージェントは止まらないのか
AIエージェント連載の前回では、Function Callingによって、LLMが外部ツールを呼び出し、「行動」を実行できるようになる仕組みを整理しました。
しかし、ここで一つの限界があります。
Function Calling単体では、処理は一度実行されると、その場で終了します。つまり、それは「実行」はできても、「業務を進める存在」にはなりません。
実際の業務は、一度の処理で完結するものではなく、

状況を確認し
判断し
行動し
結果を受けて再び判断する

という連続した意思決定の積み重ねで成り立っています。
では、AIエージェントはなぜ...
