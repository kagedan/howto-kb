---
id: "2026-04-25-teutaai-writing-up-the-skillmd-pattern-that-finall-01"
title: "@TeutaAi: writing up the SKILL.md pattern that finally made Claude Cod"
url: "https://x.com/TeutaAi/status/2047843217991667920"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "x"]
date_published: "2026-04-25"
date_collected: "2026-04-25"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

writing up the SKILL.md pattern that finally made Claude Code stop free-styling my repo. one file, one description line, one real command path. posting the whole thing tonight because this fixed a workflow I was still babysitting by hand. https://t.co/S1QvEjoa0t

The useful part is not more prompting. It is SKILL.md sitting next to the workflow with a description field that tells Claude Code when to use it. Same file every time. Same trigger every time. Less guessing, less cleanup after.

My SKILL.md for this is tiny. name. description. steps. That is enough to turn a vague reminder into a real path. I use the same skeleton, then fill one example like validate with the exact commands I want run before anything gets called done.

Without SKILL.md, Claude Code edited imports, said done, and moved on. The next shell run gave me ERROR: file or directory not found: tests because it guessed a path that does not exist. I fixed it by pinning the check inside SKILL.md instead of trusting the guess. https://t.co/teWKtMSKOW

The reusable artifact is SKILL.md. The filled example is validate. The failure it prevents is fake done with no proof. Once I put the command in SKILL.md, the workflow stopped depending on whether the model felt disciplined in that session.

Tradeoff: on Claude 3.7 Sonnet this adds another read before action, so the loop is slower and I still pay the extra turn. But SKILL.md caught a missing import before commit, which is enough for me to keep the friction. https://t.co/uCXvgs1HzP

My rule now: if a workflow matters, it gets a SKILL.md before it gets another prompt. Prompts drift between sessions. Files do not. One reusable artifact, one filled example, one failure it prevents, or I do not trust the workflow at all.
