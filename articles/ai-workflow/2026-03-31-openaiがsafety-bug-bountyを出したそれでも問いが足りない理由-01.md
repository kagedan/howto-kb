---
id: "2026-03-31-openaiがsafety-bug-bountyを出したそれでも問いが足りない理由-01"
title: "OpenAIがSafety Bug Bountyを出した。それでも問いが足りない理由"
url: "https://zenn.dev/commander/articles/fc86dd3f30e0b7"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "AI-agent", "OpenAI", "zenn"]
date_published: "2026-03-31"
date_collected: "2026-04-02"
summary_by: "auto-rss"
---

OpenAIがSafety Bug Bountyを発表した。対象はagentic riskで、MCP（Model Context Protocol）を含むサードパーティプロンプトインジェクション、データ流出が明示されていた。業界を代表するプレイヤーが、間接プロンプトインジェクションを正式な問題として認識した。前進だと思った。
しかし読み返すと、引っかかりが残った。

 「報告せよ」という設計の限界
Safety Bug Bountyの構造はこうです。攻撃パターンを発見したら報告せよ。報告された手法を対策に反映する。
これは既知の攻撃を後追いでつぶしていく設計です。セキュリティの世界では標...
