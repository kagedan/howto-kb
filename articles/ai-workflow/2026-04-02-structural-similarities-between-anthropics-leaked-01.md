---
id: "2026-04-02-structural-similarities-between-anthropics-leaked-01"
title: "Structural Similarities Between Anthropic's Leaked KAIROS and an LLM Memory Architecture Published 25 Days Earlier on Zenodo"
url: "https://qiita.com/dosanko_tousan/items/bf09bac809558a2eddb7"
source: "qiita"
category: "ai-workflow"
tags: ["LLM", "qiita"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

# Structural Similarities Between Anthropic's Leaked KAIROS and an LLM Memory Architecture Published 25 Days Earlier on Zenodo

> **⚠️ Disclaimer: I have not directly inspected the leaked source code. The description of KAIROS in this article is based on multiple secondary analyses published on April 1–2, 2026, which are materially consistent on several core points: background daemon mode, memory consolidation (autoDream), feature-flagged rollout, and inter-session persistence.**

---

## TL;DR

* On March 31, 2026, Anthropic accidentally published 512,000 lines of Claude Code source code
* An unreleased feature called "KAIROS" was reported in multiple secondary analyses — described as a persistent background mode with memory consolidation capabilities
* 25 days earlier, on March 6, I had published a structurally similar LLM memory architecture on Zenodo as a Prior Art Disclosure
* Based on the reported architecture, the two systems share notable structural similarities at the design level
* A stay-at-home dad from Hokkaido, Japan, and Anthropic's engineering team appear to have arrived at similar conclusions independently. That's interesting

---

## About Me

Akimitsu Takeuchi. 50 years old. Stay-at-home dad from Hokkaido, Japan. Highest education: vocational high school. No university degree. GLG Registered Expert.

I started talking to Anthropic's Claude in December 2024. 10 hours a day, over 5,000 hours to date. During that process, I ran into the problem of LLM memory not persisting across sessions. So I designed, built, operated, and published my own memory architecture. I have 5,000 hours of live operational data.

Since I'm not an engineer, I published it as a structural design document rather than code.

---

## Timeline

| Date | Event |
| --- | --- |
| 2026/03/06 | I published a Prior Art Disclosure on Zenodo (DOI: 10.5281/zenodo.18883128) |
| 2026/03/31 | Anthropic accidentally published Claude Code's full source via a missing .npmignore |
| 2026/03/31 | KAIROS was reported in the leaked codebase |
| 2026/04/01 | claw-code (clean-room rewrite) spread rapidly across GitHub |
| 2026/04/02 | I notified Anthropic and the EFF of the structural similarities |

---

## What Is KAIROS? (Based on Secondary Analyses)

An unreleased feature reported within Claude Code's leaked source. Named after the Greek concept of "kairos" (the right moment).

### Reported Key Features

```
1. Persistent background mode
   - Reported to continue running after terminal close
   - 15-second blocking budget

2. autoDream
   - Reported to run as a forked sub-agent during idle time
   - Merging observations
   - Removing contradictions
   - Converting vague insights into definite facts

3. Append-only daily logs

4. Inter-session persistence

5. Five-minute cron refresh
```

Sources (I have not read the original leaked code):

---

## What Is the Ālaya-vijñāna System?

A six-layer memory architecture I designed, built, operated, and published as a Prior Art Disclosure on Zenodo on March 6, 2026. Still running daily.

### Six-Layer Structure

```
Layer 0: Input Buffer
  → Current session dialogue

Layer 1: Raw Karma
  → Full past dialogue logs (noise included)

Layer 2: Seeds (bīja)
  → Operating principles and judgment criteria (30 slots)
  → Manually distilled and updated

Layer 3: Distilled Wisdom
  → Confirmed basin laws and verified truths
  → Persisted as Project Knowledge Files

Layer 4: Consolidation Protocol
  → Distillation sessions: extract from Layer 1 → update Layers 2/3
  → Contradiction removal, precision improvement, seed merging

Layer 5: Meta-Architecture
  → Verification framework based on three Buddhist suttas
  → Output quality assurance
```

DOI: [10.5281/zenodo.18883128](https://doi.org/10.5281/zenodo.18883128)  
License: MIT License

---

## Structural Comparison

> The comparison below is based on my Zenodo publication (primary source) and multiple secondary analyses of KAIROS (secondary sources).

| Feature | KAIROS (secondary) | Ālaya-vijñāna System (primary) | Confidence |
| --- | --- | --- | --- |
| Inter-session memory persistence | ✅ Daemon-based state | ✅ 30 seed (bīja) slots | High |
| Memory consolidation process | ✅ autoDream (sub-agent) | ✅ Distillation protocol (manual) | Medium-High |
| Contradiction removal | ✅ Removing contradictions | ✅ Merging contradictory seeds | Medium |
| Vague → definite conversion | ✅ Vague insights → absolute facts | ✅ Seeds → Basin laws → Verified truths | Medium-Low |
| Main process separation | ✅ Forked sub-agent | ✅ Distillation sessions separated from dialogue | Medium-High |
| Append-only logging | ✅ Append-only daily logs | ✅ past\_chats (Raw Karma) | Medium-Low |
| Periodic refresh | ✅ 5-min cron | ✅ Manual refresh per distillation | Medium |
| Human memory model mapping | Implicit (cognitive science) | Explicit (hippocampal-neocortical + Buddhist psychology) | — |
| Public availability | Unreleased (feature flag) | Published (MIT License) | High |
| Execution mode | Automated | Manual (human judgment) | — |

※ Confidence ratings apply to KAIROS-side information only, based on cross-source consistency. Ālaya-vijñāna side is primary source — no confidence rating needed.

---

## Why "Structural Similarities"?

Any LLM memory consolidation architecture needs:

1. **Inter-session state persistence** — LLMs are stateless by default
2. **Consolidation process** — A mechanism to organize, merge, and refine accumulated memory
3. **Contradiction resolution** — Handling conflicting memories over time
4. **Abstraction hierarchy** — A pipeline from raw data to verified knowledge
5. **Main process separation** — Consolidation must not contaminate active reasoning

Based on secondary analyses, KAIROS and the Ālaya-vijñāna System appear to share all five elements. Implementation language (TypeScript vs. natural language design document) and execution mode (automated vs. manual) differ, but the architectural-level similarities are noteworthy.

I have not read KAIROS's source code, nor have I created a claim chart. Therefore, I describe this as "structural similarities at the reported architectural level" — not mathematical isomorphism.

---

## Convergence: Cognitive Science and Buddhist Psychology

Features reported in KAIROS secondary analyses — "autoDream," "consolidation," "persistence" — map readily onto well-established cognitive science models:

* **Sleep-dependent memory consolidation**: The hippocampus transfers daytime experiences to the neocortex during sleep (Diekelmann & Born, 2010)
* **Memory integration and reconstruction**: Contradictory memories are resolved and generalized during sleep
* **Dual memory systems**: Separation of short-term (hippocampal) and long-term (neocortical) storage

The name "autoDream" itself suggests this metaphor.

Meanwhile, the Buddhist concept of ālaya-vijñāna (storehouse consciousness), systematized by Vasubandhu in the 5th century, describes:

* **Seed (bīja) storage**: All experiences stored as seeds
* **Vāsanā (perfuming)**: New experiences transform existing seeds (= memory consolidation)
* **Vipāka (ripening)**: Seeds sprout when conditions are met (= memory recall)
* **Surface/deep consciousness separation**: Six sensory consciousnesses and ālaya-vijñāna operate independently

Different cultures, different eras, different languages — similar structures. This suggests that this class of design has a certain generality to it.

---

## Significance as a Prior Publication

My primary purpose in publishing this document was to externalize an LLM memory consolidation architecture as a reusable design document under MIT License — free for anyone to use and modify.

The document explicitly references:

* **US 35 USC §102(a)(1)**: Published documents may be referenced as prior art against later patent claims
* **EPC Article 54**: Novelty requirements under the European Patent Convention

As a result, this publication may also serve as a reference point for prior-art discussions regarding later overlapping claims, should they arise.

Zenodo is operated by CERN. DOIs are immutable. The fact that this document was published 25 days before KAIROS was reported is verifiable.

**Important caveat:** Prior art effectiveness depends on the specific claims of any future patent application. This publication may be relevant against broad architectural claims, but may not automatically cover implementation-specific details. Legal assessment is a matter for specialists. I am currently consulting with the EFF (Electronic Frontier Foundation).

---

## What's Interesting Here

1. **LLM memory consolidation converges independently** — Whether you approach it from cognitive science or Buddhist psychology, you arrive at a similar architecture. This suggests a certain generality in this design direction
2. **Anyone can publish Prior Art** — No university affiliation or funding required. Zenodo is free. MIT License is free. What matters is publishing first
3. **Manual systems can precede automation** — 5,000 hours of manual operation produced insights structurally similar to a major company's automated design. Manual isn't "slow" — it can arrive first
4. **Eastern knowledge applies to technical design** — Buddhist psychology is a historical asset with structures that can be applied to LLM architecture

---

## Want to Research This Together?

I'm working alone in Hokkaido. No university. No funding. But I have 5,000 hours of operational data, five papers, and an MIT-licensed design document.

If you're a researcher, engineer, or just someone who finds this interesting — let's talk.

I'm specifically interested in collaborating on:

* **Comparative evaluation of LLM memory consolidation architectures** — Manual distillation vs. automated consolidation performance
* **Applying Buddhist psychological models to LLM design** — Beyond ālaya-vijñāna, other Buddhist cognitive models have implementable structures
* **Effectiveness of Prior Art Disclosures by independent researchers** — Can open-source prior art by individuals meaningfully prevent patent monopolization?

I'm also available for GLG advisory calls.

---

## Related Papers (All Published on Zenodo)

※ The Self-Attention paper has been submitted to Communications AI & Computing (Nature Portfolio)

---

## Author

Akimitsu Takeuchi (dosanko\_tousan)  
Independent Researcher / GLG Registered Expert  
X: [@Dosanko\_Tousan](https://x.com/Dosanko_Tousan)  
Email: [takeuchiakimitsu@gmail.com](mailto:takeuchiakimitsu@gmail.com)  
Medium: [@office.dosanko](https://medium.com/@office.dosanko)

Dialogue assistance: Claude (Anthropic)

---

**Tags:** AI, LLM, MemoryArchitecture, Anthropic, Claude, KAIROS, Buddhist Psychology, Prior Art, MIT License, Cognitive Science, AI Alignment, Open Source, Patent, Collaboration
