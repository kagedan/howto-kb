---
id: "2026-06-09-rlancemartin-httpstcoes0jqm4ms9-01"
title: "@RLanceMartin: https://t.co/es0JQM4MS9"
url: "https://x.com/RLanceMartin/status/2064397389189071163"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "OpenAI", "GPT", "x"]
date_published: "2026-06-09"
date_collected: "2026-06-10"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/es0JQM4MS9


--- Article ---
Mythos-class models like Claude Fable 5 have changed the way many of us work at Anthropic. I want to share two tips for getting the most out of this class of models.

**Self-correction loops**

There’s been a lot of interest in loops recently. @bcherny [has mentioned](https://x.com/sairahul1/status/2064279904989147577?s=20) that “(his) job is to write loops.” Letting models hillclimb on an evaluation is a common recipe for improving task performance: [/goal](https://code.claude.com/docs/en/goal) in Claude Code and [Outcomes](https://platform.claude.com/docs/en/managed-agents/define-outcomes) in Claude Managed Agent are primitives that let you apply this general recipe for your specific task.

As mentioned in our [prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5), Fable 5 is good at self-correcting in a loop. A well designed goal or rubric adds feedback to the environment that Claude is running in. This let’s Claude run, collect feedback via the goal or rubric, self-correct, and proceed until the goal or rubric is satisfied.

![](https://pbs.twimg.com/media/HKYoS3maMAoXYHR.jpg)

I’ll share one toy example that I used to test Fable: [Parameter Golf](https://github.com/openai/parameter-golf) is an open source ML engineering challenge to train the best model that fits in a 16MB artifact in < 10 minutes on 8xH100s.

It’s a bit like @karpathy's [autoresearch](https://github.com/karpathy/autoresearch) project: it tests the ability of an agent to edit basic training code (a single train_gpt.py file), launch training, poll the log, read the score, and decide what experiment to run next.

I compared Fable 5 to Opus 4.7 on this challenge using [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) (CMA). CMA provides [the agent harness as well as a hosted sandbox](https://www.anthropic.com/engineering/managed-agents), so it’s well-suited for
