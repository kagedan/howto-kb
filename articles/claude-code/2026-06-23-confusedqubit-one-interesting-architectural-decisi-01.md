---
id: "2026-06-23-confusedqubit-one-interesting-architectural-decisi-01"
title: "@confusedqubit: One interesting architectural decision we made with Substrat"
url: "https://x.com/confusedqubit/status/2069560721848041548"
source: "x"
category: "claude-code"
tags: ["AI-agent", "x"]
date_published: "2026-06-23"
date_collected: "2026-06-24"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

One interesting architectural decision we made with Substrate was to do deterministic simulation testing and write formal proofs for every performance, security, or correctness sensitive part. 

Ultimately this meant we couldn’t use a lot of rust-vmm because the necessary seams and traits didn’t exist for us to do things like simulate virtio devices. 

It was a lot more work, but ultimately it paid massive dividends because the performance characteristics became an emergent property of how the entire system works together as a whole, not something we had to patch in later.


--- 引用元 @confusedqubit ---
I may be a bit late to the “time to interactive” agent sandbox party, but I wanted to make sure our hypervisor absolutely MOGGED everyone else.

10x faster than Firecracker and 425x faster than Cloud Hypervisor.

https://t.co/8x3eklASGk is the best agent infra platform, period.

FYI: both Firecracker and Cloud Hypervisor are also warm restores. Our cold restores (snapshot not already on the host) still beat FC’s warm restores. 

Because we can, and frankly because we should. 

Follow our live per-commit benchmarks here: https://t.co/Gm73GgaxSU
