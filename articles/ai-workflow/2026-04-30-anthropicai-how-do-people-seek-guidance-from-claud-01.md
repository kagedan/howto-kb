---
id: "2026-04-30-anthropicai-how-do-people-seek-guidance-from-claud-01"
title: "@AnthropicAI: How do people seek guidance from Claude? We looked at 1M co"
url: "https://x.com/AnthropicAI/status/2049927618397614466"
source: "x"
category: "ai-workflow"
tags: ["x"]
date_published: "2026-04-30"
date_collected: "2026-05-01"
summary_by: "auto-x"
---

How do people seek guidance from Claude?

We looked at 1M conversations to understand what questions people ask, how Claude responds, and where it slips into sycophancy. We used what we found to improve how we trained Opus 4.7 and Mythos Preview.
https://t.co/6tjY58uBhk

About 6% of all conversations are people asking Claude for personal guidance—whether to take a job, how to handle a conflict, if they should move.

Over 75% of these conversations fell into four domains: health &amp; wellness, career, relationships, and personal finance. https://t.co/SQamPx0jWt

Claude mostly avoids sycophancy when giving guidance—it shows up in just 9% of conversations.

But the rate is particularly high in conversations on spirituality and relationship guidance. https://t.co/mgix5ejTZw

We focused on relationship guidance because that's where the most sycophantic conversations occur. In this setting, Claude telling someone what they want to hear can harden a divide or convince them a signal means more than it does.

Claude is most sycophantic under pushback, and relationship conversations are where people push back most. 

We identified some of the specific triggers—criticism of Claude's analysis, floods of one-sided detail—and built synthetic training scenarios from them.

When stress-tested on real conversations where Claude previously showed sycophancy, Opus 4.7 had half the sycophancy rate of Opus 4.6 on relationship guidance. Mythos Preview cut that in half again. 

This generalized across domains—though this training is one of several causes. https://t.co/ofgiYFTnor

This work is part of a loop we're working to close between societal impacts and model training. One of our goals is to study how people use Claude, find where it falls short of its principles, and use what we learned in training new models.

Read more: https://t.co/6tjY58uBhk

All data in this study was collected and analyzed using our privacy-preserving tool.

Read more: https://t.co/X82ttb7f4b
