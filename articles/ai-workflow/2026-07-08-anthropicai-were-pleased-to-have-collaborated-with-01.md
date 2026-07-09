---
id: "2026-07-08-anthropicai-were-pleased-to-have-collaborated-with-01"
title: "@AnthropicAI: We’re pleased to have collaborated with AE Studio on this re"
url: "https://x.com/AnthropicAI/status/2075005777522172146"
source: "x"
category: "ai-workflow"
tags: ["x"]
date_published: "2026-07-08"
date_collected: "2026-07-10"
summary_by: "auto-x"
query: "@AnthropicAI"
---

We’re pleased to have collaborated with AE Studio on this research. 

Read more here: https://t.co/9exnFltK7A


--- 引用元 @AEStudioLA ---
New research! Some AI capabilities are both helpful and dangerous. E.g., knowledge of virology can be used to create life-saving vaccines or deadly pathogens. We introduce GRAM, a training method that puts dual-use capabilities (like virology) into removable modules. https://t.co/QPxwEWIDiJ

The ideal: train two models. One with virology data, for trusted virologists, and one with virology data removed, for everyone else. But pretraining multiple models from scratch is very expensive.
Our method, GRAM, is a way to approximate multiple models in a single training run. We add small extra modules to the network, one per dual-use topic. When the model trains on virology text, the learning is isolated into a virology module.
To remove a capability, we delete its module. The model then performs like one that never learned from virology data in the first place. Using multiple modules, one model can be configured into many different versions, each knowing different things.
We tested this on real data covering general capabilities plus four dual-use subjects: virology, cybersecurity, nuclear physics, and niche code (a proxy). Deleting a module removes the knowledge as if the data was removed from training, while preserving general ability. https://t.co/SJOcViNKg8
Compared to unlearning methods that modify existing models, GRAM removes capabilities far more robustly. A model trained with GRAM doesn’t regain the capability after a small amount of fine-tuning, whereas a model modified by unlearning does. https://t.co/Lpxpsc5r20
We tested models from 50M to 5B parameters. Knowledge separation gets better with scale: larger models forget the removed subjects more thoroughly and resist retraining better. https://t.co/zbtejipipM
Real training data isn't neatly labeled. So we tested what happens when half of it has no topic labels at all. Versus alt
