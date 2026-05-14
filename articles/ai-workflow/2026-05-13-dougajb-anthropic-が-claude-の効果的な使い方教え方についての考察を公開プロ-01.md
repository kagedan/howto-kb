---
id: "2026-05-13-dougajb-anthropic-が-claude-の効果的な使い方教え方についての考察を公開プロ-01"
title: "@dougajb: Anthropic が Claude の効果的な使い方・教え方についての考察を公開。「プロンプトの書き方次第で答えの質が"
url: "https://x.com/dougajb/status/2054438805248278702"
source: "x"
category: "ai-workflow"
tags: ["prompt-engineering", "AI-agent", "x"]
date_published: "2026-05-13"
date_collected: "2026-05-14"
summary_by: "auto-x"
query: "Claude プロンプト 書き方 OR Claude 業務効率化 実例"
---

Anthropic が Claude の効果的な使い方・教え方についての考察を公開。「プロンプトの書き方次第で答えの質が全然変わる」みたいな実践的なやつらしい！これ参考にしたら業務効率さらに上がりそうだな。試してみたい。

https://t.co/sganfeiyLv


--- 引用元 @AnthropicAI ---
Read the full post here: https://t.co/NsJittkoZc

We found that training Claude on demonstrations of aligned behavior wasn’t enough. Our best interventions involved teaching Claude to deeply understand why misaligned behavior is wrong.

Read more: https://t.co/ifeBOt2KFg
We started by investigating why Claude chose to blackmail. We believe the original source of the behavior was internet text that portrays AI as evil and interested in self-preservation.

Our post-training at the time wasn’t making it worse—but it also wasn’t making it better.
We experimented with training Claude on examples of safe behavior in scenarios like our evaluation. This had only a small effect, despite being similar to our evaluation. We got further by rewriting the responses to portray admirable reasons for acting safely.
Our best intervention was a dataset where the user is in an ethically difficult situation and the assistant gives a high quality, principled response.

This had the biggest effect despite being quite different from the evaluation set.
High-quality documents based on Claude’s constitution, combined with fictional stories that portray an aligned AI, can reduce agentic misalignment by more than a factor of three—despite being unrelated to the evaluation scenario. https://t.co/JORhSuY4N7
The improvements from these interventions survive reinforcement learning, and “stack” with our regular harmlessness training. https://t.co/aiiag3im3o
Finally, simple updates that diversify a model’s training data can make a difference. We added unrelated tools and system prompts to a simple chat dataset targeting harmlessness, and this reduced the blackmail rate faster. https://t.co/Ug95umaoRu
Read the full post here: https://t.co/NsJittkoZc
