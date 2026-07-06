---
id: "2026-07-06-claudedevs-httpstcov694m8eaj6-01"
title: "@ClaudeDevs: https://t.co/v694m8Eaj6"
url: "https://x.com/ClaudeDevs/status/2074208949205881033"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/v694m8Eaj6


--- Article ---
There’s a lot of talk right now about "designing loops" instead of prompting your coding agent. If you spend some time on X trying to pin down what a loop actually is, you'll come across multiple different answers.

On the Claude Code team, we define **loops as agents repeating cycles of work until a stop condition is met**. We categorize a few different types of loops based on:

- How they are triggered
- How they are stopped
- What Claude Code primitive is used
- What type of task is most appropriate for each.
We’ll cover the main loop types, when to use each, and how to maintain code quality while managing token usage. Not all tasks require complex loops; start with the simplest solution and use these patterns selectively.

---

## **Turn-based loops**

![](https://pbs.twimg.com/media/HMkOVNybEAAncbL.jpg)

- **Triggered by**: A user prompt.
- **Stop criteria**: Claude judges it has completed the task or needs additional context.
- **Best used for: **Shorter tasks that are not part of a regular process or schedule.
- **Managed usage by: **Write specific prompts and improve verification using skills to reduce the number of turns.**‍**
Every prompt you send starts a manual loop with you directing each turn. Claude gathers context, takes action, checks its work, repeats if needed, and responds. We call this the agentic loop.

For example, ask Claude to create a like button. It reads your code, makes the edit, runs the tests, and hands back something it *believes* works. You then manually check the work, and write the next prompt.

You can improve the verification step by encoding your manual steps as a SKILL.md so Claude can check more of its own work, end-to-end. This should include tools or connectors to allow Claude to *see*, *measure* or *interact* with the result. The more quantitative the checks are, the easier it is for Claude to self-verify.

For example, in your SKILL.md file you may specify:

```markdown
--- 
name:
