---
id: "2026-04-07-claudebasics-why-claudemd-and-not-just-prompting-e-01"
title: "@claudebasics: Why CLAUDE.md and not just prompting each time? CLAUDE.md p"
url: "https://x.com/claudebasics/status/2041629621746114924"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "x"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-x"
---

Claude Code keeps leaving placeholder comments. "// add logic here". "// rest of implementation". "// TODO".

This is fixable with a one-time system prompt patch. Here's how ｧｵ

The root cause: Claude's RLHF training rewards concise responses. Over time it learned that brief and sketchy often scores better than complete.

But in a coding context, partial implementations are worse than useless 窶? they break your build and waste review time.

The fix 窶? add these rules to your CLAUDE.md:

Write complete implementations. Never use placeholder comments.
Do not summarize what you're about to do. Just do it.
Never write "rest of code unchanged". Rewrite the full function.

Why CLAUDE.md and not just prompting each time?

CLAUDE.md persists. Claude Code reads it at the start of every session automatically. You set the rule once and forget it.

One-time 10-minute setup vs. reminding Claude every session.

The other piece: break tasks down further.

Laziness appears most often on big, vague requests. Claude doesn't know where to draw the scope boundary so it draws it too narrow.

Smaller, concrete tasks = complete implementations more reliably.

Quick test: ask Claude Code to implement one function. Check if it writes the full body or punts with a comment.

If you see a comment, your project needs anti-laziness rules.

Write the rules once. Add them to CLAUDE.md. Never fight this problem again.

Follow @claudebasics for daily Claude Code tips.
