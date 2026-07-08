---
id: "2026-07-08-claudedevs-httpstcodxoi9nna86-01"
title: "@ClaudeDevs: https://t.co/dxoI9Nna86"
url: "https://x.com/ClaudeDevs/status/2074900291062034618"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "API", "x"]
date_published: "2026-07-08"
date_collected: "2026-07-09"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/dxoI9Nna86


--- Article ---
Claude Code gives you two settings that both seem to "make the answer better": the model, and the effort level. But what do these actually do to the output? And how do you know whether to reach for a different model or just change the effort level?

It's easy to assume that choosing a larger model like Fable gives you a smarter output than Sonnet, and that a higher effort level just means Claude thinks longer before it answers.

The first assumption is true. Our largest models are **more capable**, according to industry-standard benchmarks.

But effort means more than "thinking time." Effort controls **how much work Claude does on your request overall**. That includes how long it thinks, but also:

- how many files it reads;
- how much it verifies; and
- how far it pushes through a multi-step task before checking in with you.
At higher effort, Claude takes more of those actions (read files, run tests, double-check) before it comes back to you. At lower effort, it would rather ask you for more context than spend tokens figuring something out on its own.

---

## **How model selection works**

To understand what the model setting actually controls, it helps to start at the very beginning, from the moment you press enter.

Claude Code assembles your message together with the system prompt, tool definitions, your CLAUDE.md, the conversation history, and any files in context. All of this is sent as one request to the API.

![](https://pbs.twimg.com/media/HMp7c2RbkAAVN7X.jpg)

The model never sees any of that as plain text, though. The first thing that happens on the server is tokenization: the text gets split into pieces, and each piece is mapped to an integer from a fixed vocabulary the model was trained with. `const` might map to 1978, `await` might map to 4293. From here on, **your prompt is an array of integers**.

![](https://pbs.twimg.com/media/HMp7pYKbAAA_X1F.jpg)

The model's job is to take that array and predict which to
