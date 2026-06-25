---
id: "2026-06-25-claude-47s-tokenizer-is-probably-the-real-price-in-01"
title: "Claude 4.7’s tokenizer is probably the real price increase"
url: "https://note.com/modern_ferret431/n/n442f7b92f463"
source: "note"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "note"]
date_published: "2026-06-25"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

If you build on Claude Code, tokenizer changes are not a boring implementation detail. They hit your context window, your cache bill, and your rate limits, which makes this a very practical story rather than a theoretical one. What Abhishek Ray did here is useful because he measured the actual effect instead of repeating the docs.

## Key Points

* Anthropic’s migration guide says Claude Opus 4.7 uses roughly 1.0–1.35x as many tokens as 4.6, but Ray measured 1.47x on technical docs and 1.45x on a real [CLAUDE.md](http://claude.md/) file.
* Across seven real Claude Code-ish samples, the weighted ratio was 1.325x, or 8,254 tokens becoming 10,937.
* In a separate set of synthetic samples, English and code-heavy content landed near the top of Anthropic’s stated range, while CJK content barely moved at all, around 1.01x.
* The biggest increases showed up in English prose and code, which is exactly the kind of material Claude Code users keep stuffing into context.
* Ray also tested instruction-following with a small IFEval sample of 20 prompts. Claude 4.7 did a little better on strict instruction following: 90% vs 85% at the prompt level.
* That improvement was modest, not dramatic. On the looser metric, the models tied.
* The likely tradeoff is smaller or fewer subword merges for common English and code patterns, but that remains a hypothesis because token counts can’t reveal the exact vocabulary changes.
* The practical cost is higher per session, even though the per-token price did not change. Ray estimates roughly 20–30% more per long Claude Code session.
* Prompt caching still works, but the cached prefix is larger, so you pay more to write and read it.
* For Max-plan users, the same pattern likely means the 5-hour window ends sooner on English-heavy work.

## My Take

What strikes me is that this is one of those changes that sounds tiny until you run the numbers. A tokenizer swap does not feel as dramatic as a new model release, but if you live inside Claude Code all day, it can quietly change the economics of your workflow. I think that’s the most important part of the article: not that 4.7 is “worse,” but that it is measurably more expensive to use on the kind of text developers actually send.

The instruction-following bump is interesting, but I’d be careful not to oversell it. A +5 point swing on 20 sampled IFEval prompts is suggestive, not definitive. That said, it does line up with Anthropic’s claim that the model is more literal and precise. If I were choosing between 4.6 and 4.7 for a real coding session, I’d care less about benchmark vibes and more about whether it reduces annoying formatting mistakes, tool-call slips, and weird prompt drift. If that’s what the tokenizer helps with, I can see why Anthropic made the trade.

The cost side feels more concrete and, honestly, a little annoying. Claude Code users already think in terms of cache hits, context growth, and session length. A 1.3x-ish token inflation means your “same” workflow stops being the same in practice. I’d especially watch long refactors, chatty debugging sessions, and anything with a big [CLAUDE.md](http://claude.md/) plus lots of history. Those are exactly the situations where the hidden overhead compounds.

I’d be curious whether Anthropic will eventually explain the tokenizer change more directly, because right now the article’s evidence suggests the upper end of the documented range is not an edge case. For Claude Code users, that means plan for the worst reasonable ratio, not the midpoint.

The short version: 4.7 may buy you a bit more literalness, but you pay for it in tokens. If you build with Claude, that tradeoff is real enough to budget for.
