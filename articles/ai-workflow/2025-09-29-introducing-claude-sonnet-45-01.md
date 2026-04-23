---
id: "2025-09-29-introducing-claude-sonnet-45-01"
title: "Introducing Claude Sonnet 4.5"
url: "https://www.anthropic.com/news/claude-sonnet-4-5"
source: "anthropic"
category: "ai-workflow"
tags: ["anthropic"]
date_published: "2025-09-29"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

Claude Sonnet 4.5 is the best coding model in the world. It's the strongest model for building complex agents. It’s the best model at using computers. And it shows substantial gains in reasoning and math.

Code is everywhere. It runs every application, spreadsheet, and software tool you use. Being able to use those tools and reason through hard problems is how modern work gets done.

Claude Sonnet 4.5 makes this possible. We're releasing it along with a set of major upgrades to our products. In [Claude Code](https://anthropic.com/news/enabling-claude-code-to-work-more-autonomously), we've added checkpoints—one of our most requested features—that save your progress and allow you to roll back instantly to a previous state. We've refreshed the terminal interface and shipped a [native VS Code extension](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code). We've added a new [context editing feature and memory tool](https://anthropic.com/news/context-management) to the Claude API that lets agents run even longer and handle even greater complexity. In the Claude [apps](https://claude.ai/redirect/website.v1.7dfbee6c-de48-457e-ab7e-a34c9478faa9/download), we've brought code execution and [file creation](https://www.anthropic.com/news/create-files) (spreadsheets, slides, and documents) directly into the conversation. And we've made the [Claude for Chrome](https://www.anthropic.com/news/claude-for-chrome) extension available to Max users who joined the waitlist last month.

We're also giving developers the building blocks we use ourselves to make Claude Code. We're calling this the [Claude Agent SDK](https://anthropic.com/engineering/building-agents-with-the-claude-agent-sdk). The infrastructure that powers our frontier products—and allows them to reach their full potential—is now yours to build with.

This is the [most aligned frontier model](https://www.anthropic.com/claude-sonnet-4-5-system-card) we’ve ever released, showing large improvements across several areas of alignment compared to previous Claude models.

Claude Sonnet 4.5 is available everywhere today. If you’re a developer, simply use `claude-sonnet-4-5` via [the Claude API](https://docs.claude.com/en/docs/about-claude/models/overview). Pricing remains the same as Claude Sonnet 4, at $3/$15 per million tokens.

## Frontier intelligence

Claude Sonnet 4.5 is state-of-the-art on the SWE-bench Verified evaluation, which measures real-world software coding abilities. Practically speaking, we’ve observed it maintaining focus for more than 30 hours on complex, multi-step tasks.

Claude Sonnet 4.5 represents a significant leap forward on computer use. On OSWorld, a benchmark that tests AI models on real-world computer tasks, Sonnet 4.5 now leads at 61.4%. Just four months ago, Sonnet 4 held the lead at 42.2%. Our [Claude for Chrome](https://www.anthropic.com/news/claude-for-chrome) extension puts these upgraded capabilities to use. In the demo below, we show Claude working directly in a browser, navigating sites, filling spreadsheets, and completing tasks.

The model also shows improved capabilities on a broad range of evaluations including reasoning and math:

![Benchmark table comparing frontier models across popular public evals](/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F67081be1ea2752e2a554e49a6aab2731b265d11b-2600x2288.png&w=3840&q=75)

Claude Sonnet 4.5 is our most powerful model to date. See footnotes for methodology.

Experts in finance, law, medicine, and STEM found Sonnet 4.5 shows dramatically better domain-specific knowledge and reasoning compared to older models, including Opus 4.1.

The model’s capabilities are also reflected in the experiences of early customers:

> **We're seeing state-of-the-art coding performance from Claude Sonnet 4.5**, with significant improvements on longer horizon tasks. It reinforces why many developers using Cursor choose Claude for solving their most complex problems.

> **Claude Sonnet 4.5 amplifies GitHub Copilot's core strengths**. Our initial evals show significant improvements in multi-step reasoning and code comprehension—enabling Copilot's agentic experiences to handle complex, codebase-spanning tasks better.

> **Claude Sonnet 4.5 is excellent at software development tasks**, learning our codebase patterns to deliver precise implementations. It handles everything from debugging to architecture with deep contextual understanding, transforming our development velocity.

> Claude Sonnet 4.5 **reduced average vulnerability intake time for our Hai security agents by 44% while improving accuracy by 25%**, helping us reduce risk for businesses with confidence.

> **Claude Sonnet 4.5 is state of the art on the most complex litigation tasks.** For example, analyzing full briefing cycles and conducting research to synthesize excellent first drafts of an opinion for judges, or interrogating entire litigation records to create detailed summary judgment analysis.

> Claude Sonnet 4.5's edit capabilities are exceptional — **we went from 9% error rate on Sonnet 4 to 0% on our internal code editing benchmark**. Higher tool success at lower cost is a major leap for agentic coding. Claude Sonnet 4.5 balances creativity and control perfectly.

> Claude Sonnet 4.5 delivers impressive gains on our most complex, long-context tasks—from engineering in our codebase to in-product features and research. **It's noticeably more intelligent and a big leap forward**, helping us push what 240M+ users can design with Canva.

> **Claude Sonnet 4.5 has noticeably improved Figma Make in early testing**, making it easier to prompt and iterate. Teams can explore and validate their ideas with more functional prototypes and smoother interactions, while still getting the design quality Figma is known for.

> **Sonnet 4.5 represents a new generation of coding models**. It's surprisingly efficient at maximizing actions per context window through parallel tool execution, for example running multiple bash commands at once.

> For Devin, Claude Sonnet 4.5 increased planning performance by 18% and end-to-end eval scores by 12%—**the biggest jump we've seen since the release of Claude Sonnet 3.6**. It excels at testing its own code, enabling Devin to run longer, handle harder tasks, and deliver production-ready code.

> **Claude Sonnet 4.5 shows strong promise for red teaming**, generating creative attack scenarios that accelerate how we study attacker tradecraft. These insights strengthen our defenses across endpoints, identity, cloud, data, SaaS, and AI workloads.

> Claude Sonnet 4.5 resets our expectations—**it handles 30+ hours of autonomous coding**, freeing our engineers to tackle months of complex architectural work in dramatically less time while maintaining coherence across massive codebases.

> For complex financial analysis—risk, structured products, portfolio screening—Claude Sonnet 4.5 with thinking **delivers investment-grade insights that require less human review**. When depth matters more than speed, it's a meaningful step forward for institutional finance.

## Our most aligned model yet

As well as being our most capable model, Claude Sonnet 4.5 is our most aligned frontier model yet. Claude’s improved capabilities and our extensive safety training have allowed us to substantially improve the model’s behavior, reducing concerning behaviors like sycophancy, deception, power-seeking, and the tendency to encourage delusional thinking. For the model’s agentic and computer use capabilities, we’ve also made considerable progress on defending against prompt injection attacks, one of the most serious risks for users of these capabilities.

You can read a detailed set of safety and alignment evaluations, which for the first time includes tests using techniques from mechanistic interpretability, in the Claude Sonnet 4.5 [system card](https://www.anthropic.com/claude-sonnet-4-5-system-card).

![](/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F33efc283321feeff94dd80973dbcd38409806cf5-3840x2160.png&w=3840&q=75)

Overall misaligned behavior scores from an automated behavioral auditor (lower is better). Misaligned behaviors include (but are not limited to) deception, sycophancy, power-seeking, encouragement of delusions, and compliance with harmful system prompts. More details can be found in the Claude Sonnet 4.5 [system card](https://www.anthropic.com/claude-sonnet-4-5-system-card).

Claude Sonnet 4.5 is being released under our AI Safety Level 3 (ASL-3) protections, as per [our framework](https://www.anthropic.com/news/announcing-our-updated-responsible-scaling-policy) that matches model capabilities with appropriate safeguards. These safeguards include filters called classifiers that aim to detect potentially dangerous inputs and outputs—in particular those related to chemical, biological, radiological, and nuclear (CBRN) weapons.

These classifiers might sometimes inadvertently flag normal content. We’ve made it easy for users to continue any interrupted conversations with Sonnet 4, a model that poses a lower CBRN risk. We've already made significant progress in reducing these false positives, reducing them by a factor of ten since [we originally described them](https://www.anthropic.com/news/constitutional-classifiers), and a factor of two since Claude Opus 4 was released in May. We’re continuing to make progress in making the classifiers more discerning1.

## The Claude Agent SDK

We've spent more than six months shipping updates to Claude Code, so we know what it takes to [build](https://www.youtube.com/watch?v=DAQJvGjlgVM) and [design](https://www.youtube.com/watch?v=vLIDHi-1PVU) AI agents. We've solved hard problems: how agents should manage memory across long-running tasks, how to handle permission systems that balance autonomy with user control, and how to coordinate subagents working toward a shared goal.

Now we’re making all of this available to you. The [Claude Agent SDK](https://anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) is the same infrastructure that powers Claude Code, but it shows impressive benefits for a very wide variety of tasks, not just coding. As of today, you can use it to build your own agents.

We built Claude Code because the tool we wanted didn’t exist yet. The Agent SDK gives you the same foundation to build something just as capable for whatever problem you're solving.

## Bonus research preview

We’re releasing a temporary research preview alongside Claude Sonnet 4.5, called "[Imagine with Claude](https://claude.ai/redirect/website.v1.7dfbee6c-de48-457e-ab7e-a34c9478faa9/imagine)".

In this experiment, Claude generates software on the fly. No functionality is predetermined; no code is prewritten. What you see is Claude creating in real time, responding and adapting to your requests as you interact.

It's a fun demonstration showing what Claude Sonnet 4.5 can do—a way to see what's possible when you combine a capable model with the right infrastructure.

"Imagine with Claude" is available to Max subscribers for the next five days. We encourage you to try it out on [claude.ai/imagine](https://claude.ai/redirect/website.v1.7dfbee6c-de48-457e-ab7e-a34c9478faa9/imagine).

## Further information

We recommend upgrading to Claude Sonnet 4.5 for all uses. Whether you’re using Claude through our apps, our API, or Claude Code, Sonnet 4.5 is a drop-in replacement that provides much improved performance for the same price. Claude Code updates are available to all users. [Claude Developer Platform](https://claude.com/platform/api) updates, including the Claude Agent SDK, are available to all developers. Code execution and file creation are available on all paid plans in the Claude apps.

For complete technical details and evaluation results, see our [system card](https://www.anthropic.com/claude-sonnet-4-5-system-card), [model page](https://www.anthropic.com/claude/sonnet), and [documentation](https://docs.claude.com/en/docs/about-claude/models/overview). For more information, explore our [engineering](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) [posts](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) and research post on [cybersecurity](https://red.anthropic.com/2025/ai-for-cyber-defenders).
