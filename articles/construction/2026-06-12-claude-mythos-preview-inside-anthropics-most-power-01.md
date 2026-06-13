---
id: "2026-06-12-claude-mythos-preview-inside-anthropics-most-power-01"
title: "Claude Mythos Preview: Inside Anthropic's Most Powerful AI Model"
url: "https://zenn.dev/neotechpark/articles/54899972128158"
source: "zenn"
category: "construction"
tags: ["OpenAI", "GPT", "zenn"]
date_published: "2026-06-12"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

If you have been following AI security news lately, you have probably seen the name "Claude Mythos" pop up. It is not a normal product launch. In fact, you cannot buy it, subscribe to it, or even sign up for a waitlist. Anthropic built a model so capable at finding software vulnerabilities that it decided the safest move was to not release it publicly at all.

Let's break down what Mythos actually is, why it matters, and what it tells us about where AI security is heading.

## What Is Claude Mythos Preview

Claude Mythos Preview is a large language model from Anthropic that specializes in one thing: hunting for zero day vulnerabilities in software, and even building working exploits for them. It was introduced in April 2026 as a model that can autonomously find zero day vulnerabilities and create exploits for them.

Anthropic has been blunt about how capable this model is. The company called it its most powerful model yet, one that is able to identify thousands of zero day vulnerabilities over the course of several weeks.

That is a big claim. Normally, finding a single zero day can take a skilled human researcher weeks or months. Mythos is reportedly doing this at scale.

## Project Glasswing: The Coalition Behind It

Instead of releasing Mythos to the public, Anthropic created something called Project Glasswing. Think of it as a closed club where trusted organizations get access to Mythos under strict conditions.

The name itself has a nice story behind it. Project Glasswing is inspired by the glasswing butterfly, which has transparent wings that help it hide in plain sight, and the project is described as a defensive cybersecurity coalition.

The first wave of partners was small but extremely high profile. Anthropic gave access to twelve launch partners, including Amazon Web Services, Apple, Google, Microsoft, CrowdStrike, NVIDIA, and Palo Alto Networks.

These are not small startups. These are companies whose software runs a huge chunk of the internet.

## The Numbers So Far

So what has actually happened since launch? The results are honestly pretty wild.

In the first weeks of Project Glasswing, the roughly 50 initial partners used Claude Mythos Preview to find more than ten thousand high or critical severity vulnerabilities across some of the most important software in the world.

That number alone explains why this story keeps making headlines. Ten thousand serious bugs is not a small batch test, it is a massive sweep across critical infrastructure.

Here is a simple timeline of how the program has grown:

## From 50 Partners to 200

The program did not stay small for long. Anthropic decided the results were strong enough to justify a major expansion.

Following weeks of collaboration with Glasswing partners, the security industry, open source maintainers, and the US government, Anthropic extended the partnership to approximately 150 new organizations based in more than 15 countries.

What is interesting here is who got added. This was not just more tech giants. The new group includes infrastructure operators in sectors that were not represented before, such as power, water, healthcare, and telecommunications, along with hardware vendors and critical software maintainers including nonprofit groups.

One of the more recent additions is Cloud Software Group. With Mythos, Cloud Software Group expects to build on its existing security program by finding vulnerabilities faster, improving triage and remediation planning, detecting complex attack paths that traditional testing can miss, and responding more quickly to open source threats.

A simple breakdown of the growth looks like this:

## Why Not Just Release It

This is the part people argue about the most. Why would a company build something this powerful and then lock it away?

Anthropic's own explanation is about timing and risk. The company says cheap, fast AI models with powerful cyber capabilities are coming soon, and within 6 to 12 months it expects other AI companies to have Mythos class models that could be released without safeguards against misuse, which could make cyberattacks far more frequent and unpredictable.

In other words, the goal of Glasswing is not just to use Mythos quietly. It is meant to push the entire industry toward better norms before more of these models show up, including ones built by less careful companies.

There is also a more skeptical take floating around. Some commentary frames this as either genuine caution or a clever marketing move, since keeping the model exclusive means it gets enormous attention precisely because the public cannot access it.

## Is Mythos Actually That Special

Here is where things get a bit more nuanced. Not everyone agrees Mythos is dramatically ahead of other models.

Cloudflare reportedly noted that other models found a lot of the same bugs as Mythos, and a security company called Aisle tested several small open source models and was able to find the same vulnerabilities that Anthropic had highlighted, some of which had gone unnoticed by humans for decades.

This led some experts to push back on the whole approach. Some cybersecurity experts told the New York Times that keeping the model restricted does not actually fix the underlying problem of widespread vulnerabilities, it just gives a small group of organizations a head start.

So depending on who you ask, Mythos is either a genuinely unprecedented leap, or it is one of the first models to clearly demonstrate a capability that was already quietly emerging across the industry.

## The Competitive Angle

Anthropic is not the only lab working on this kind of capability. Since Mythos was released, OpenAI reportedly launched its own cybersecurity focused model called GPT-5.5-Cyber, which it has rolled out to a large group of partners for testing.

This is a pretty clear signal. Cyber focused AI models are becoming their own category, and multiple major labs are now racing in this direction at the same time.

Glasswing is not just "here is a model, good luck." Anthropic has also been rolling out supporting tools. Anthropic released Claude Security in public beta for Claude Enterprise customers, along with a Cyber Verification Program that lets approved security professionals use its models for legitimate cybersecurity work with fewer restrictions, plus custom skills, an automated scanning and reporting framework, and a threat modeling tool for identifying and prioritizing attack targets.

This matters because finding ten thousand vulnerabilities is only half the problem. Someone still has to verify them, prioritize them, and actually patch them, which is its own massive workload.

## The Bigger Picture

What makes this story worth writing about is not just one model. It is what it represents.

For years, people talked about AI eventually being able to find software bugs automatically. Mythos is one of the first public, large scale, real world demonstrations that this is no longer theoretical. Ten thousand high or critical flaws is not a lab demo number, it is an industry scale number.

At the same time, the debate around it shows how messy this transition is going to be. Is restricting access the right move, or does it just delay an inevitable spread of similar capabilities to less careful actors? Anthropic clearly believes the former, at least as a starting point, while expanding the circle of trusted partners step by step.

Either way, if you work in software, security, or infrastructure, this is one to keep watching. The line between "AI that helps defenders" and "AI that helps attackers" is getting thinner, and Mythos is sitting right at that line.
