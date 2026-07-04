---
id: "2026-07-03-trq212-httpstcohpizr1kg7r-01"
title: "@trq212: https://t.co/hPiZr1kG7r"
url: "https://x.com/trq212/status/2073100352921215386"
source: "x"
category: "ai-workflow"
tags: ["prompt-engineering", "AI-agent", "x"]
date_published: "2026-07-03"
date_collected: "2026-07-05"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/hPiZr1kG7r


--- Article ---
Working with Claude Fable 5 keeps re-teaching me an old lesson: the map is not the territory.

The map, a representation of the work to be done, is my prompts and skills and context, it’s what I give Claude. The territory is where the work needs to happen, the codebase, the real world, its actual constraints.

![](https://pbs.twimg.com/media/HMUY0Dpa4AA__qj.jpg)

The difference between the map and the territory is what I call *unknowns*. When Claude runs into an unknown, it needs to make a decision based on its best guess of what I want. The more work being done, the more unknowns Claude might run into

Fable is the first model where I find the quality of the work is bottlenecked by my ability to clarify its unknowns.

Importantly, just planning ahead isn’t always enough. You can find unknowns deep in implementation, or your unknowns may point you to the fact that you should actually be solving the problem in a different way altogether.

I’ve found that working with Fable is an iterative process of discovering my unknowns before, during, and after implementation.

I've made some [**example artifacts for finding unknowns her](https://thariqs.github.io/html-effectiveness/unknowns/)e**, but be sure to come back to build the intuition for when to use them.

## Knowing your unknowns

What are your unknowns? When I come to Claude with a problem I tend to break it down in 4 ways:

- **Known Knowns:** This is essentially what is in my prompt. What do I tell the agent that I want?
- **Known Unknowns:** What haven't I figured out yet, but I’m aware that I haven’t?
- **Unknown Knowns:** What's so obvious I’d never write it down, but would recognize it if I saw it?
- **Unknown Unknowns:** What haven't I considered at all? What knowledge am I not aware of? Do I know how good something can be?
![](https://pbs.twimg.com/media/HMUa_3jbcAAJeRy.jpg)

The best agentic coders are good have relatively few unknowns. Watching someone like [Boris](
