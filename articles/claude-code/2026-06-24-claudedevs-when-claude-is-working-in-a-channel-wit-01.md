---
id: "2026-06-24-claudedevs-when-claude-is-working-in-a-channel-wit-01"
title: "@ClaudeDevs: When Claude is working in a channel with four people, whose"
url: "https://x.com/ClaudeDevs/status/2069895377080443271"
source: "x"
category: "claude-code"
tags: ["AI-agent", "x"]
date_published: "2026-06-24"
date_collected: "2026-06-30"
summary_by: "auto-x"
---

When Claude is working in a channel with four people, whose credentials does it use?

The answer: its own. When tagging Claude, Claude gets provisioned like any other teammate, with its own credentials.

We call this access model "agent identity". Here's how it works: 🧵 https://t.co/UveJWgOQEx

Acting as the user works fine for a single personal assistant, but Claude Tag can be multiplayer. When three people are in one thread, there's no "right" set of permissions to borrow.

So in channels, Claude acts as itself. In DMs, where it's just you, Claude acts as you.

DMs are the simple case: Claude runs on your own connectors, with your name. That's where personal email and your calendar belong.

Channels are where agent identity kicks in. Claude gets its own Linear account, its own GitHub account, its own service account on your warehouse.

Admins provision it once and scope what it can reach per channel: broad read access in shared spaces, sensitive tools only where a few people are cleared.

Noah walks you through the setup in this video: https://t.co/HqymlIj7ki

You get one identity to audit. Every action shows up in each connected system's own logs under Claude's account. 

Revoke once, and access ends everywhere. Shared channels never expose anyone's private files.

Claude gets enough access to be useful in shared work, and admins control exactly where that stops.

More on the blog: https://t.co/CP6rCs8FNX
