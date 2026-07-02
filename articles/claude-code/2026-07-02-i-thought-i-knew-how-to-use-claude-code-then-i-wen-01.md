---
id: "2026-07-02-i-thought-i-knew-how-to-use-claude-code-then-i-wen-01"
title: "I Thought I Knew How to Use Claude Code. Then I Went to Code w/ Claude"
url: "https://zenn.dev/noahlogy/articles/7e223ba013b642"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "LLM", "zenn"]
date_published: "2026-07-02"
date_collected: "2026-07-03"
summary_by: "auto-rss"
query: ""
---

Hi, I'm Yuto (yutoii.vercel.app). I'm a first-year Honours Mathematics student at the University of Waterloo, currently working as an AI engineer intern at Noahlogy, an AI startup modernizing Japan's maritime industry: we turn the expertise of veteran engineers in shipbuilding, marine equipment, and shipping into AI agents, tackling the industry's twin challenges of technical succession and labor shortage. Claude is woven into daily life at the company. Everyone uses it for development work, our pull requests get reviewed by the Claude GitHub integration, and I've been working with Claude Code myself for about a month now, mostly handling GitHub PRs and issues. My current project is evaluating whether locally hosted LLMs can power Claude Code-style agents for clients whose data can never leave their own environment, so the question of where these tools are heading is very much my day job.

That's why, when DEEPCORE, the AI-focused incubator and VC under the SoftBank Group, invited Noahlogy to Code w/ Claude Tokyo and the team handed the seat to me. The event ran for two days this week, and it was the first time Anthropic has hosted it in Tokyo. The timing couldn't have been better: Claude Mythos 5 and Fable 5 had both launched on the same day, just one day before the event, and you could feel that energy in every session. Claude is already woven into major Japanese companies like Rakuten, and the room was full of people who already assumed AI would change how they work. The real question on everyone's mind was how fast they could keep up with it.

That last part is really what this post is about. I went in expecting to learn about new features. I left realizing something more uncomfortable: the tools had been evolving faster than my habits. I've been living in the terminal and VS Code, doing things the way I learned to do them months ago, while the product quietly grew past my routines. Out of the dozens of talks across the two days, four stuck with me. Each one announced something new, and each one also forced me to notice something about how I think and work. And if you've never written a line of code in your life, stay with me, because the most important thing I heard across the two days had surprisingly little to do with code.

![](https://static.zenn.studio/user-upload/323786b580a8-20260702.png)

## Talk 1: What's New with Claude Code

The opening talk was, on the surface, a feature tour. But the theme underneath it was autonomy. Claude Code is steadily shifting from a tool you operate to an agent you direct.

Some of the highlights that landed for me:

**Remote control.** Pick up a running session from your phone or the web, connected straight to your terminal CLI, so you no longer need to keep the laptop open while Claude works.

**Voice mode and quality-of-life upgrades.** A new `/voice` command brings voice to the terminal, alongside `/fullscreen`, flicker-free rendering, auto memory, and auto mode settings.

**Automatic Git worktrees.** Multiple agents can now work on the same task in parallel without stepping on each other.

**Routines.** Hand Claude a repeatable job, like checking the issues on a GitHub repo, with instructions and control over how often it runs.

**Agent views.** Every running agent sorted into three buckets: needs input, working, and completed. One glance shows where you're actually needed.

**Dynamic workflows.** Keyword: "ultracode." Claude runs many parallel sub-agents, has them verify each other's work, and returns a result. It's already being used for large-scale migrations, like adding new languages to an entire website in a single action.

Sitting there, I realized almost none of this was in my workflow. The features weren't hidden. I had simply stopped looking. Once a tool works "well enough," we stop re-learning it, and in a field where the ground shifts this drastically day by day, that's how you fall behind without noticing. The people who thrive here treat their own workflow as something to audit and update, the same way they'd update a dependency. Raw technical skill matters less than that habit.

## Talk 2: Stop Babysitting Your Agents

This was the talk that called me out personally. I've lost real hours to going back and forth with an agent: checking its work, nudging it, approving the next step. I always framed that as "waiting for Claude." The talk flipped it: most of that time, Claude was waiting for *me*.

The fix is verification loops. Think about how humans verify their own work: write the code, build it, run it, check for side effects, run the unit tests, deploy to staging. We don't ask a colleague to confirm every step is fine; the loop itself tells us. The argument was that we should get Claude into that exact loop: let it run the app, click the button, see it fail, read the logs, fix the code, and go around again until it can screenshot success and open a PR.

The mantra from the talk: **Run it, Drive it, Prove it, Unblock it.** Give Claude the ability to run its own work, drive the interface, prove the result (screenshots matter here, since Claude should be able to *see* the change it made), and unblock itself when it gets stuck. A pro tip I wrote down immediately: add a stop hook that asks Claude to run verification if it hasn't already, so self-checking becomes the default.

And then the talk stacked it: **verify → parallelize → background.** Once verification means you stop reading every diff, you can run ten agents instead of one. Once you can run ten, you can push real work into the background. And the background work goes well beyond coding: PR babysitting, updating docs, triaging issues, monitoring feedback, keeping CI green. The new `/loop` command runs a prompt on an interval in your session; the example given was `/loop 10m babysit my open PRs - fix CI, address comments, rebase`. That's an entire category of busywork, automated in one line.

What this talk really taught me is that trust in an AI agent has to be engineered. Every verification step you build is a unit of trust you no longer have to supply manually with your own attention. The bottleneck in my workflow was never the model's capability. It was my unwillingness to design a system where I didn't need to watch. And honestly, that lesson reaches well beyond software. Anyone who has handed work to someone and then hovered over their shoulder knows this pattern: the hovering feels responsible, and it's actually the thing keeping both of you slow.

![](https://static.zenn.studio/user-upload/b0d632ed52ce-20260702.jpg)

## Talk 3: The Capability Curve

If the first two talks were about tools, this one was about assumptions, and it might have been the most important talk of the event.

The framing fact: Sonnet 4 was published only a year ago, in May 2025. Twelve months later, Opus 4.8 is three times as accurate. The behavior changes are just as dramatic as the benchmarks. Models that used to act first and think later now read everything before taking action and catch their own mistakes mid-plan. Where a failed tool call used to send an agent into a loop of retrying the exact same call until the run stalled, it now reads the error, adjusts its approach, and keeps executing through failures that used to end the run entirely.

The core insight: **every time the model gets meaningfully better, your scaffolding should get meaningfully smaller, and most people don't update.** All those carefully engineered prompts, the chunked-up tasks, the elaborate workarounds? They're fossils. Each one encodes an assumption about a weakness that an older model had. If you never go back and delete them, you end up constraining a stronger model with rules written for a weaker one.

The practical advice that followed:

* **Shrink your scaffolding.** Describe what you want, rather than how to work around last year's model. Audit your prompts and systems regularly.
* **Refresh your evals.** Build evals that match your real traffic, update saturated ones (if the new model aces a test, that test is no longer measuring anything), and benchmark against new models as they arrive.
* **Give the model room to work.** Use adaptive thinking and let Claude decide when to think, dialing effort up or down to control cost. Grant more access in a controlled way; auto mode in Claude Code is the obvious example. Stop chunking work just to babysit the context window.
* **Close the agent loop.** Design your system so Claude can inspect its own outputs and iterate on them.

This talk reframed adaptation for me. Learning new features turns out to be the easy half of keeping up with AI. The harder half is *unlearning* compensations. The skill of the next few years might come down to what you have the discipline to delete from your workflow, more than what you add to it. And this applies even if you've never written a prompt longer than a sentence. If you tried AI a year ago, decided it couldn't do something, and walked away, that conclusion has expired too. The model you tested no longer exists.

## Talk 4: Same Model, Three Different Worlds: Japan, India, Australia

One of the most unexpected sessions was a live interview with Claude ambassadors from Japan, India, and Australia, comparing how their communities have grown around the same tools.

The contrasts were striking. Japan has been hosting events since March 2025; the latest drew over 200 people with full attendance, an even split of startups and big tech, and a distinctly Japanese love of physical robots (the Doraemon-shaped dream of AI you can actually hold). India operates at a completely different scale: 3,000 to 4,000 registrations competing for 100 spots, a crowd that's roughly 60:40 technical to non-technical, and stories like an ambassador from a very non-techy environment who built his own building platform with Claude Code. Australia has run 20 events since December, spread across the whole country and full of solo builders and founders: non-technical people prompting entire apps into existence, sometimes getting stuck only at the very last step, like figuring out how to get localhost into production.

Same model. Three completely different relationships with it. And that's what stayed with me: the technology doesn't flatten everyone into one way of working. Instead, it gets absorbed into whatever a community already cares about. Japan builds companions you can grow attached to. India builds at scale and pulls in people who were never "supposed" to be builders. Australia turns lone tinkerers into founders. The model is the constant; the culture is the variable.

The shared trend underneath it all, though, points somewhere bigger. Every ambassador said their audiences are becoming less technical as the models get smarter, and the gap between a six- or seven-figure product and something built for $300 to $400 is closing fast. When the cost of *making* collapses like that, the scarce skill stops being the ability to code and becomes the ability to think: knowing what's worth building, what questions to ask, and when to step back and let the AI lead. That skill sits closer to self-awareness than to engineering, and it travels across every border in that room. So if you've assumed building isn't for you because you never learned to code, this is the part of the post written for you. The people in those stories didn't become more technical. The technology became more human, and the gate is already open.  
![](https://static.zenn.studio/user-upload/3312d74e946d-20260702.jpg)

## General Thoughts on the Event

Beyond the content, the event itself was impressively run. Every talk started and ended on time, without a single delay across two days. Translator earpieces were available for live interpretation between English and Japanese, which made the whole event far more accessible than tech conferences usually are.

That accessibility meant something personal to me. As a Japanese speaker who also speaks English, I found myself moving between both audiences all day: chatting with local developers in Japanese, then turning around and talking with international attendees and speakers in English. Being able to bridge those two rooms made the event feel twice as big. There were conversations and perspectives I would have completely missed if I'd been limited to one language, and it made me appreciate how much of an event like this happens in the hallway conversations, away from the stage.

Networking, honestly, was a first for me. Day 1 went better than I expected: I pushed myself to talk to as many people as I could, especially early on, and the crowd was broad and welcoming. Day 2 had a different rhythm. It was a separate day just for independent developers and founders, so the crowd was smaller and the conversations went deeper, with people sharing real experience from their own projects rather than reacting to feature announcements. I found myself listening more than talking, and in hindsight that was exactly the right move; some of the most valuable insights of the whole event came from those quieter, more substantive exchanges.

One more thing I noticed: the talks weren't isolated. They referenced and reinforced each other, so every session I attended gave me more context for the next one. The new features from the opening talk kept reappearing as the practical answers to problems raised in later talks. By the end, the whole event read like one coherent argument rather than a schedule of presentations.

## Conclusion

If I compress two days into one sentence, it's a line from one of the Day 2 sessions: **the work is no longer writing the code. The work is setting up the conditions in which the code gets written well.**

The four talks were really four angles on that same idea. Keep re-learning your tools, because they're outgrowing your habits. Engineer verification so trust doesn't depend on your attention. Audit your own assumptions as aggressively as you audit your code, because the model you're compensating for no longer exists. And remember that this shift is happening everywhere at once, in Japan, India, and Australia, with each community making it their own.

As for me, I'm starting small. This week I'm setting up the two features I was most embarrassed to have ignored: remote control, so a session keeps working after I close my laptop, and routines, so the repetitive checks run without me. It's a modest commitment, and that's the point. Keeping up doesn't require heroics; it requires actually trying the thing you just learned about before the next thing arrives.

The balance is shifting: as the AI gets smarter, the job moves from giving strict instructions to knowing when to let it lead. The cost of making things is collapsing, and the skill that holds its value is the thinking that surrounds the building: knowing what's worth making, what to ask, and when to step back. That requires a kind of self-awareness about your habits, your bottlenecks, and your outdated assumptions that no model update can supply for you. The capability curve is climbing either way. The only real question is whether your way of working, coder or otherwise, climbs with it.  
![](https://static.zenn.studio/user-upload/de3d2c82738f-20260702.jpg)
