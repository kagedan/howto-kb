---
id: "2026-07-11-s1r1u5-there-are-many-components-in-our-security-o-01"
title: "@S1r1u5_: there are many components in our security orchestration, but"
url: "https://x.com/S1r1u5_/status/2076041885236465941"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "VSCode", "x"]
date_published: "2026-07-11"
date_collected: "2026-07-12"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

there are many components in our security orchestration, but one of the core primitive is obviously an agent that needs to support structured outputs, cost, loop, and context budgeting, custom tools, and a bunch of workflow-specific behavior.

using provider harnesses like codex or claude code, or third-party ones like opencode and pi, doesn’t work that well when you want the harness to be opinionated and deeply customized around your workflows.

so we built our own agent harness. the problem with custom agents is that they get stale. unlike traditional software, you can’t just write a few unit tests and know everything is still working. you deploy the agent and have no idea whether it’s quietly getting worse, making tool call errors, or behaving worse than first-party harnesses.

you can inspect traces, analyze logs and errors, but going through every trace is a massive pita.

one interesting solution for us was to use the agent in our own coding workflows and dogfood it every day. when the harness sucks, you notice immediately.

but then you run into another problem, writing a good tui for an internal agent is annoying. after using polished coding agents, you don’t want to use your own because the ui/ux sucks. eventually, you stop dogfooding it.

enter opencode, i first saw this kind of architecture in windsurf, the agent harness runs as a separate backend over http and protobuf, while vscode is just the ui. it’s a much better architecture because the same harness can power a vscode extension, web app, tui, or anything else. unlike cursor, where a lot of the harness seems buried inside a big-ass vscode workbench.js.

opencode works similarly. the tui talks to a web server running the agent loop and streams the events back to the ui. so i built a protocol translation layer between opencode’s core tools and our own agent harness.

now we get opencode’s tui and ui/ux, while still running our own agent loop, tools, budgeting, structured outputs, and orchestration unde
