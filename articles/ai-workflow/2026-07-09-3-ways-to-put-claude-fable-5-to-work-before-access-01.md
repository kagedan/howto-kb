---
id: "2026-07-09-3-ways-to-put-claude-fable-5-to-work-before-access-01"
title: "3 Ways to Put Claude Fable 5 to Work Before Access Runs Out"
url: "https://zenn.dev/neotechpark/articles/b94aaa1c8c24a5"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "zenn"]
date_published: "2026-07-09"
date_collected: "2026-07-10"
summary_by: "auto-rss"
query: ""
---

If you have access to frontier AI models right now, you already know that access does not stay open forever, and it does not stay cheap forever either. Claude Fable 5 is one of those models that rewards people who show up with a plan instead of people who just start typing prompts and hope for the best. This article walks through three tutorials you can actually run this week, each one built around something real engineers do on the job, whether that job is a freelance gig, a startup side project, or a full time engineering role.

We are not going to cover every possible use case here. Instead we picked three that map directly onto what hiring managers and clients actually look for from engineers today: the ability to rebuild something functional from scratch, the ability to catch problems in a codebase before they become expensive, and the ability to turn a vague idea into a shipped product using nothing but a written plan. If you can show a client or an interviewer that you did all three, you are already ahead of most applicants.

A quick note before we start. Claude Fable 5 and its sibling Claude Mythos 5 were released on June 9, 2026, and briefly had access suspended a few days later to comply with export control rules from the US Department of Commerce. Access was restored on July 1, 2026 after the Department of Commerce lifted those restrictions. Some of what you will see floating around online right now, including specific usage limits or claims about pricing changes, comes from individual creators testing the model rather than from Anthropic directly, so always double check current limits and pricing on Anthropic's own documentation before you build a workflow around a specific number.

## The Core Workflow: Plan With One Model, Execute With Another

Before touching any of the three tutorials, it helps to understand the workflow pattern that makes all of them work well. Frontier coding models are expensive to run for long stretches, so the trick is to separate planning from execution. You use a fast, cheaper reasoning model to do research and produce a clear brief, then you hand that brief to Fable 5 and let it run the long autonomous session.

This loop shows up in all three tutorials below. Skipping the planning step and going straight to Fable 5 with a vague request is the single fastest way to burn through your usage without getting anything useful back.

This is the fastest way to build a portfolio piece that shows real engineering judgment, not just copy paste code. Pick a small SaaS tool you or your team already pays for. It does not need to be complex. A voice transcription helper, a simple time tracker, or a lightweight note taking app are all good candidates because they have a clear, testable scope.

Here is the process step by step.

**Step one, research the target tool.** Ask your planning model to look into how the tool works at a functional level. What does it listen to, what does it store, what does it output. You are not trying to steal proprietary code, you are trying to understand the feature set well enough to recreate the core functionality on your own terms.

**Step two, decide what you are changing.** The whole point of rebuilding something is to make it better for your specific situation. Maybe the original tool sends your data to a cloud server and you want everything running locally on your machine instead. Maybe you want to strip out features you never use and keep only the essentials. Write this down clearly.

**Step three, turn the research into a brief.** Have your planning model condense everything into a single, structured prompt. This should describe the goal, the constraints, and what a finished version looks like. The clearer this document is, the less back and forth you will need with Fable 5 later.

**Step four, hand it to Fable 5 for a long running session.** This is where you use an autonomous or goal oriented mode rather than a single short prompt. You are asking the model to keep working toward the end state you described, not to produce one quick draft and stop.

**Step five, test against the original.** Once you have a working version, compare it side by side against the tool you started from. Note what is missing, note what works better, and be honest about both.

The result of this tutorial is something you can put directly into a portfolio. Most engineering teams value demonstrated ownership of a full build cycle, from problem definition to working software, more than they value a list of frameworks on a resume.

## Tutorial Two: Run a Full Codebase Review and Debugging Pass

This one is less about building something new and more about proving you can be trusted with an existing codebase, which is exactly the kind of trust a remote engineer needs to earn quickly with a new client or employer.

**Step one, pick a codebase with some real history.** A personal project that has grown messy over time works well, or a codebase from a past job if you have permission to use it. The point is to work with something that has accumulated genuine technical debt rather than a fresh toy project.

**Step two, ask for a full review, not a narrow one.** A simple request works fine here. Ask Fable 5 to review the codebase for both code quality issues and actual bugs, not just style problems. Longer sessions with larger codebases tend to surface findings across the whole system rather than just the files you point at directly.

**Step three, expect a layered output.** A thorough pass usually comes back with a large number of raw findings that then get grouped, deduplicated, and ranked by how serious they are. Read through the full list before acting on anything, since the highest severity item is not always the most urgent one to fix depending on your deadline.

**Step four, triage before you fix.** Do not blindly accept every suggested fix. Go through the list and decide what actually matters for your situation right now versus what can wait. This triage step is itself a skill worth demonstrating if you are documenting this process for a portfolio or a blog post.

**Step five, fix incrementally and re-test.** Work through the prioritized list in small batches, testing after each batch rather than applying every fix at once. This keeps you from introducing new problems while chasing old ones.

If you take on freelance or contract work, this entire process doubles as a service offering. A structured code health audit is something you can package and sell on its own, separate from any new feature work.

## Tutorial Three: Ship a Long Horizon Project From a Written Brief Alone

This tutorial is the most ambitious of the three, and it is the one that best demonstrates whether you can manage a genuinely long autonomous build rather than a short task. The core idea is simple even if the execution takes patience: you write one solid planning document, then let the model work against it across many sessions until the project is done.

**Step one, write the brief yourself, at least partially.** This is the part people skip and should not. The strongest results come from projects where a human wrote at least the first version of the planning document. It does not need to be long, but it needs to be specific about what you are building, why, and what a successful outcome looks like.

**Step two, include your non negotiables.** Spell out the constraints that matter to you. What technology stack are you committed to, what should the final experience feel like, what is explicitly out of scope. Vague briefs produce vague results no matter how capable the model is.

**Step three, let your planning model sharpen the draft.** Take your rough brief and have a reasoning focused model tighten it up, filling gaps and catching contradictions before you hand it off.

**Step four, run the build in goal oriented mode.** Rather than issuing individual instructions, use a mode that lets Fable 5 keep working toward your stated end state across an extended session, checking in only when it needs a decision from you.

**Step five, review milestones, not every commit.** For a project spanning many commits over hours or days, checking in at natural milestones is more sustainable than reviewing every single change. Save detailed review for points where the project direction could meaningfully shift.

A project built this way, documented from the original brief through to the finished product, is one of the strongest things you can show a potential employer or client. It proves you can define a problem, manage an extended build process, and land a working result, which is precisely the kind of independence that remote work requires when direct supervision is limited.

## A Few Honest Cautions

None of this works well if you skip the planning step and go straight to Fable 5 with an unstructured request. Long autonomous sessions on a rough prompt tend to wander, and wandering costs you usage you cannot get back easily.

It is also worth being skeptical of specific numbers you see quoted online, including weekly usage percentages or claims about pricing structures. Individual creators test these models in the days right after release and sometimes publish figures that are accurate only for a narrow window or under specific plan conditions. Anthropic's own documentation is the reliable source if a specific limit or price actually matters for how you plan your week.

Finally, remember that the planning document is doing most of the real thinking in each of these tutorials. Fable 5 executes well against a clear target, but it cannot read your mind about what a clear target should be. The time you spend writing a good brief is rarely wasted time.

## Common Pitfalls Across All Three Tutorials

A handful of mistakes show up again and again once people start experimenting with this workflow, and it is worth naming them directly so you can avoid repeating them.

**Treating the planning model as optional.** It is tempting to skip straight to Fable 5 because it feels like the more capable model, but that instinct works against you. The planning model is cheaper to run and better suited to research and structuring, while Fable 5 is better suited to sustained execution. Using the wrong tool for the wrong stage wastes both time and usage.

**Writing briefs that describe the process instead of the outcome.** A weak brief says something like build me a note taking app. A strong brief says what the app stores, how a user interacts with it, what happens when data conflicts, and what the interface should feel like when it is done. Outcome focused briefs give the model something concrete to aim for.

**Reviewing too often or not often enough.** Checking in after every single change during a long autonomous session defeats the purpose of running a long session in the first place. On the other hand, walking away for hours without any checkpoints means you might come back to a build that drifted far from what you actually wanted. Milestone based review, as described in tutorial three, tends to strike the right balance.

**Forgetting to test against something real.** Whether you are rebuilding a tool, auditing a codebase, or shipping a new project, the value only becomes visible once you compare the output against a real benchmark, whether that is the original tool you copied, the bug reports from before your audit, or the requirements you wrote in your original brief. Skipping this step means you cannot honestly say whether the exercise worked.

## Turning These Exercises Into Something You Can Show

Documentation is what separates a private experiment from something you can use professionally. For each of the three tutorials, keep a short record as you go rather than trying to reconstruct the story afterward.

For the rebuild exercise, save the original research notes, the brief you handed to Fable 5, and a short comparison against the original tool. This becomes a case study you can post on Zenn, LinkedIn, or wherever you are building a public presence, and it doubles as proof of your process, not just your output.

For the codebase audit, save the raw findings list alongside the triaged version and a short note explaining why you prioritized what you did. Hiring managers and clients care as much about your judgment in triage as they care about the fixes themselves, since triage is what they are actually paying you to do once you join a team.

For the long horizon build, save the original PRD, the refined version, and a short log of the milestones you hit along the way. If the project spans many commits, you do not need to document every one, but a summary of the major turning points shows that you can manage a project across time, not just produce a single burst of output.

This kind of documented process is exactly the material that turns into a strong blog post, a talk at a community event, or a portfolio piece attached to a job application. The three tutorials in this article are meant to be run once for practice and then run again, for real, on something that matters to your career.

## Why This Matters

Every one of these three tutorials produces something concrete you can show, not just something you can talk about. A rebuilt tool, a documented code audit, and a shipped project from a written brief are exactly the kind of evidence that turns an application from a resume into a portfolio. If you try even one of these this week, you will walk away with more than a finished build. You will walk away with a repeatable process you can apply the next time a client hands you an ambiguous problem and expects you to figure out the rest on your own.
