---
id: "2026-06-24-therobertta-anthropics-thariq-shihipar-showed-spec-01"
title: "@therobertta_: Anthropic's Thariq Shihipar showed spec-as-HTML on Claire Vo"
url: "https://x.com/therobertta_/status/2069571216294490294"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-06-24"
date_collected: "2026-06-24"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Anthropic's Thariq Shihipar showed spec-as-HTML on Claire Vo's ChatPRD podcast. Architecture diagrams, UI drafts, state machines - one HTML file that both human and agent read.

Everyone talks about AI-powered design. Nobody mentions why your design system should live in code, not in Figma. Think about what that means for your team's quarterly planning and resource allocation.

1. THE HIDDEN COST OF FIGMA:

$15/seat/month for dev seats.
2. That is the visible cost.
3. The invisible cost is handoff friction.
4. Every time design passes to code, context gets lost.
5. The agent reads markdown but cannot see the design.
6. It guesses at layout, spacing, and hierarchy.
7. Think of it like translating a novel through 3 languages.
8. The meaning survives.
9. The nuance does not.

What I call "the handcraft gap" closed this year. Figma stock down 85% over 5 years.

Down 50% year-to-date. One HTML spec file eliminates the entire handoff workflow.

The human sees rendered components. The agent sees rendered components.

Same file. Same context.

No translation. Think about what that means for your team's quarterly planning and resource allocation.

The compounding trick most teams miss:

Every codebase I work on has a design-system.html.

Consider what happens after 100 PRs:

Each PR that touches UI also updates design-system.html. After 100 updates, the system contains more institutional design knowledge than any Figma board. Git-versioned. Zero sync overhead. Ask yourself how much of your design context currently lives outside version control. Think about what that means for your team's quarterly planning and resource allocation.

Here is what my production workflow looks like:

After a prospect call I need materials in 15 minutes. Granola transcript into Claude Code. It checks design-system.html first. Generates 95% of the proposal matching my exact brand. 5 minutes of polish.

That speed only works because the design system is in code. No login. No export. No sync step. C
