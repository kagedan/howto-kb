---
id: "2026-06-09-oikon48-anthropicのclaude-codeチームのthariqがclaude-fab-01"
title: "@oikon48: AnthropicのClaude CodeチームのThariqが、「Claude Fable 5が出てから、仕事の進め方"
url: "https://x.com/oikon48/status/2064402696124453157"
source: "x"
category: "claude-code"
tags: ["claude-code", "LLM", "x"]
date_published: "2026-06-09"
date_collected: "2026-06-10"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

AnthropicのClaude CodeチームのThariqが、「Claude Fable 5が出てから、仕事の進め方が根本的に変わった」ことを紹介。

昔は『Claudeが仕事を正しくこなしているか』を検証していたが、今は『Claudeが正しい仕事をしているか』を検証するようになった。」

具体的な3つの変化:

① Claudeを「思考のパートナー」として扱う

- 早い段階でClaudeに相談する（実装前にインタビューさせる） 
- 単なる制約ではなく「背景・文脈」をしっかり伝える 
- 例：「シンプルに作って」「過剰に作るな」ではなく 「これは実験的な機能で、1ヶ月後に削除する可能性が高い。だから後で捨てやすい設計にして」

② 目標と検証方法を明確に与える

Claude Codeの新機能**/goal** と Workflows を積極的に使う：
- /goal → 「この仕様を完全に実装し終わるまで動き続けろ」と指示 
- Workflows → Claude自身が作業を並列化・検証し、レポートを作成
- プロンプト例 「Set a goal to implement the spec fully, then use a workflow to verify each part of the plan, and prepare a report on what was implemented and if anything differed.」

③ もっと大胆に

- 今まで「LLMには無理だろ」と思っていたことも挑戦させる 
- たとえばこの動画の編集もClaude Fable 5にやらせている

https://t.co/vN8njVyWNL
