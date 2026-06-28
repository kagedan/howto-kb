---
id: "2026-06-28-whydeso-httpstcohtjy11z9qd-01"
title: "@whydeso: https://t.co/hTJY11Z9qd"
url: "https://x.com/whydeso/status/2071338115969560824"
source: "x"
category: "claude-code"
tags: ["claude-code", "LLM", "OpenAI", "x"]
date_published: "2026-06-28"
date_collected: "2026-06-29"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

https://t.co/hTJY11Z9qd


--- Article ---
Early in 2026, Andrej Karpathy, a co-founder of OpenAI, posted a GitHub gist called "LLM Knowledge Base." It got fourteen thousand stars in a single week. The idea was almost insultingly simple: stop dumping your knowledge into apps that lock it away, store it as plain text files, point an AI at the folder, and let it read, link, and build on everything you know.

That's it. No database, no vector store, no fancy infrastructure. Just a folder of markdown files and Claude sitting on top of it.

I built it. And it does something I genuinely didn't expect: it gets smarter the more you feed it. Not in a marketing way. In a literal way. The tenth thing you add is more useful than the first, because the system connects it to everything already there. This is the full setup, every command, every file, the exact structure. By the end you'll have a knowledge base that reads your notes, answers questions from them, and never makes you start from a blank chat again.

Fair warning: this lives in the terminal, not a pretty app. If that scares you, it's genuinely easier than it looks, and I'll walk every step.

---

![](https://pbs.twimg.com/media/HL7VZz2XQAAooZN.jpg)

# Why this works at all (the boring insight that matters)

Most "second brain" setups fail for one reason: they're write-only. You dump notes into Notion or Apple Notes and never open them again. The knowledge is there, but it just sits. It doesn't connect to anything, and it definitely doesn't get smarter.

The fix is two pieces working together. Obsidian, which is just a folder of plain markdown (.md) files on your computer with wiki-style [[links]] between them. And Claude Code, the terminal version of Claude, which can read, write, and edit every file in a folder you point it at.

Here's the key part people miss: Claude doesn't store your context in some hidden AI memory. Your context lives in your files, as plain text you control. If Claude ever gets something about yo
