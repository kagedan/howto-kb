---
id: "2026-05-12-zenok-karpathy-just-gave-a-name-to-my-workflow-ive-01"
title: "@zenok__: Karpathy just gave a name to my workflow. I’ve been running"
url: "https://x.com/zenok__/status/2054346435832021461"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "LLM", "x"]
date_published: "2026-05-12"
date_collected: "2026-05-13"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

Karpathy just gave a name to my workflow.

I’ve been running Claude Code + Codex in parallel, asking each for HTML output. Open all the outputs in browser tabs. Side by side.

Not for speed. For something else.

Reason 1: Context consistency check. Same prompt, different models. If they all return wildly different HTML structures, my context wasn’t clear enough. That’s where most “AI bugs” actually start. Context bugs disguised as model bugs.

Reason 2: Decision making. When comparing architectures or approaches, text outputs blur together. HTML side-by-side, the trade-offs become visible in seconds.

Karpathy’s framing just put words on it: text is the bottleneck, not the model.


--- 引用元 @karpathy ---
This works really well btw, at the end of your query ask your LLM to "structure your response as HTML", then view the generated file in your browser. I've also had some success asking the LLM to present its output as slideshows, etc.

More generally, imo audio is the human-preferred input to AIs but vision (images/animations/video) is the preferred output from them. Around a ~third of our brains are a massively parallel processor dedicated to vision, it is the 10-lane superhighway of information into brain. As AI improves, I think we'll see a progression that takes advantage:

1) raw text (hard/effortful to read)
2) markdown (bold, italic, headings, tables, a bit easier on the eyes) <-- current default
3) HTML (still procedural with underlying code, but a lot more flexibility on the graphics, layout, even interactivity) <-- early but forming new good default
...4,5,6,...
n) interactive neural videos/simulations

Imo the extrapolation (though the technology doesn't exist just yet) ends in some kind of interactive videos generated directly by a diffusion neural net. Many open questions as to how exact/procedural "Software 1.0" artifacts (e.g. interactive simulations) may be woven together with neural artifacts (diffusion grids), but generally something in the direction
