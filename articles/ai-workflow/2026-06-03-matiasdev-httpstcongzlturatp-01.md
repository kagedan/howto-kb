---
id: "2026-06-03-matiasdev-httpstcongzlturatp-01"
title: "@matiasdev_: https://t.co/NgzltuRaTp"
url: "https://x.com/matiasdev_/status/2062037189345595612"
source: "x"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "x"]
date_published: "2026-06-03"
date_collected: "2026-06-04"
summary_by: "auto-x"
query: ""Model Context Protocol" tutorial OR "Claude MCP" integration"
---

https://t.co/NgzltuRaTp


--- Article ---
## TL;DR

- Your agent has the perfect tool wired up and still answers from memory, calls the wrong one, or quotes your refund policy and then **promises the refund** — because the model never saw your code, only the description string, and the string didn't tell it any better.
- The model programs against three strings: the tool **name**, the **description**, and each **parameter description**. Those strings are the API. The `execute` body is invisible to it.
- The move that makes it work: write the description for a new hire, not a compiler — encode *what it returns*, *when to reach for it*, and *the one thing it must NOT conclude from the result* (a `found: false` means "ask the customer," not "invent a status").
- A precise description is worth more than a smarter model: Anthropic got SOTA on SWE-bench by refining tool descriptions alone, and a tight contract cut my agent's wrong-tool and hallucinated-state errors to near zero — at zero extra tokens per call.
- This is the tool-design layer of the same harness I've been building out in [the processors deep-dive](https://matiaslapolla.com/blog/mastra-processors-and-guardrails); MCP is just the wire that carries those strings to other agents — and, if you're not careful, carries an injection straight into yours.
## Why "good code, weak description" isn't enough

Here's the default. You need your support agent to look up order status, so you write a tool: a clean Zod input schema, a real `execute` that hits the OMS, a tidy output shape. Then you reach the `description` field and type the thing every tutorial types:

> description: 'Looks up an order.'

Compiles. Passes review. Ships. And then production does what production does:

- A customer asks "where's my stuff?" and the agent answers from memory — never calls the tool, because "looks up an order" didn't say *this is how you answer "where is my order" questions.*
- A customer gives a typo'd order id, the lookup returns
