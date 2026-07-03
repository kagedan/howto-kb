---
id: "2026-07-03-hyde-ai3-claude-code-power-setup-fable-5-opus-sonn-01"
title: "@Hyde_ai3: Claude Code Power Setup: Fable 5 + Opus + Sonnet + Codex Us"
url: "https://x.com/Hyde_ai3/status/2073151028237922659"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "OpenAI", "x"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Claude Code Power Setup: Fable 5 + Opus + Sonnet + Codex

Use Fable 5 as the orchestrator while offloading heavy reasoning and execution to specialized agents to save context and maximize performance.

🧠 Model Roles
Model
Role
Fable 5 (Max Reasoning)
🎯 Orchestrator
Opus
🧠 Deep reasoning subagent
Sonnet
⚡ Mechanical work subagent
Codex
👨‍💻 Peer senior engineer (independent perspective)
1️⃣ Set Fable 5 as the Main Model
In Claude Code:
/model
Select:
Fable 5
Reasoning: Max
Effort: Max
2️⃣ Create Two Subagents
Open:
/agents
🧠 deep-reasoner
Model: Opus
Use for reasoning-heavy phases,
architecture,
debugging complex issues,
algorithm design.

Think thoroughly and return a concise conclusion the orchestrator can act on.
⚡ fast-worker
Model: Sonnet
Use for mechanical tasks,
boilerplate,
tests,
formatting,
simple edits.

Execute efficiently.
3️⃣ Install OpenAI's Official Codex Plugin
Install the Codex CLI first.
Then run:
/plugin marketplace add openai/codex-plugin-cc

/plugin install codex@openai-codex

/codex:setup
4️⃣ Add This to CLAUDE.  Me
## Orchestration Workflow

You (Fable) are the orchestrator.

Plan.
Decompose.
Delegate.
Synthesize.

Reasoning-heavy phases
→ deep-reasoner (Opus)

Mechanical work
→ fast-worker (Sonnet)

Codex (/codex:rescue --background)
is a peer senior engineer with an independent perspective.

Treat Codex as a collaborator, not a reviewer.

For high-stakes decisions:

• Ask Opus and Codex to solve the problem independently.
• Do not reveal either solution to the other.
• Synthesize the strongest ideas yourself.
• Keep your own context lean.
5️⃣ Prompt Fable Like a Tech Lead
Goal:
[What you want to accomplish]

Context:
[Files, constraints, requirements]

You're the tech lead.

Delegate:
• Deep reasoning → deep-reasoner
• Mechanical work → fast-worker
• Fresh-perspective problems → Codex

Show me your execution plan first.

Then execute.
💡 Recommended Workflow
                Fable 5
            (Orchestrator)
                  │
      ┌────────
