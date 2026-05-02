---
id: "2026-05-01-claudecode-lab-anthropicとopenaiが同時に公式プロンプトガイドを公開し海-01"
title: "@claudecode_lab: AnthropicとOpenAIが同時に公式プロンプトガイドを公開し、海外で話題に 両者ともに「古いプロンプトの書き方"
url: "https://x.com/claudecode_lab/status/2050182870065639683"
source: "x"
category: "ai-workflow"
tags: ["prompt-engineering", "OpenAI", "GPT", "x"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-x"
query: "Claude プロンプト 書き方 OR Claude 業務効率化 実例"
---

AnthropicとOpenAIが同時に公式プロンプトガイドを公開し、海外で話題に

両者ともに「古いプロンプトの書き方はもう通用しない」
でも理由は真逆。

🚩Claude Opus 4.7 → 推測しなくなった。書いた通りにしか動かない
🚩GPT-5.5 →自分で判断するようになった。細かく書きすぎると逆効果

↓でClaudeのプロンプトの書き方を解説します！

今すぐできるClaudeプロンプト見直しリスト

❌やめること
・「いい感じに」「よろしく」系のふんわり指示
・長い背景説明だけして結論を言わない
・NG例だけ並べて「これをやるな」と書く

✅やること
・最初の一文で「何を出してほしいか」を明言する
・フォーマット・分量・観点を最初に書く
・NG例より「こういうのがいい」と例を見せる

公式プロンプトガイドはこちら
Anthropic
https://t.co/7IwrIK1vd6

OpenAI
https://t.co/K9ulWKStyJ


--- 引用元 @alex_prompter ---
Both OpenAI and Anthropic just released official prompting guides.

Both say the same thing.

Your old prompts don’t work anymore.
But for opposite reasons.

Claude Opus 4.7 stopped guessing what you meant. It does exactly what you type. Nothing more, nothing less. 

Vague instructions that worked on 4.6? They now produce narrow, literal, sometimes worse results. 

Not because the model got dumber. Because it stopped compensating for sloppy thinking.

GPT-5.5 went the other direction. OpenAI’s guide literally says: “Don’t carry over instructions from older prompt stacks.” 

Legacy prompts over-specify the process because older models needed hand-holding. GPT-5.5 doesn’t. That extra detail now creates noise and produces mechanical output.
Claude got more literal. 

GPT got more autonomous. Both now punish the same thing: prompts written without clear thinking behind them.

One developer on Reddit captured it perfectly after analyzing hundreds of community posts. The complaints tracked almost perfectly with prompt specificity. 

Precise prompts got better results on 4.7. Vague prompts got worse. The model didn’t regress. The prompts did.

OpenAI’s new framework is “outcome-first prompting.” Describe what good looks like. Define success criteria. Set constraints. Then get out of the way. The model picks the path. 

Anthropic’s framework is the inverse: be surgically specific about what you want, because the model won’t fill in your blanks anymore.

Two different architectures. Two different philosophies. 

One i
