---
id: "2026-06-19-wenchangyue-sync-all-your-claude-code-skills-acros-01"
title: "@WenchangYue: Sync all your Claude Code skills across machines with one gi"
url: "https://x.com/WenchangYue/status/2067768598547095702"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "x"]
date_published: "2026-06-19"
date_collected: "2026-06-19"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Sync all your Claude Code skills across machines with one git repo and one symlink.

Setup:
1. Make ~/.claude/skills a git repo and push it to GitHub.
2. Move your global ~/.claude/CLAUDE.md into that repo, then symlink it back. https://t.co/zUhr9PQCmJ

Now your rules and skills version together. Claude still reads the standard path; git just tracks the real file behind the symlink. Clone on a second machine, recreate the symlink, and you are done.

The trap nobody warns you about: edit the same skill on two machines and your push gets rejected, your pull throws conflicts. The two histories diverged, and git will not guess which side should win.

The fix: pick one machine as the source of truth. On it, run:

git merge -s ours origin/main
git push

That keeps its content, folds the other machine's history in (nothing is lost), and the remote now matches it.

One catch: -s ours drops the other machine's conflicting edits from the result. They stay in history, just superseded. Use it only when you really mean this machine wins.

How do you keep your AI tooling config in sync across machines?

#ClaudeCode #DevTools #Dotfiles #Git
