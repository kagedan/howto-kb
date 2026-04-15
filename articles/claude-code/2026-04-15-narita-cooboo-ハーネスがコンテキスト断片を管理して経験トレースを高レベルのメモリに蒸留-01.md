---
id: "2026-04-15-narita-cooboo-ハーネスがコンテキスト断片を管理して経験トレースを高レベルのメモリに蒸留-01"
title: "@narita_cooboo: ハーネスがコンテキスト断片を管理して、経験トレースを高レベルのメモリに蒸留する──この論点、skillsエコシステムを運"
url: "https://x.com/narita_cooboo/status/2044214393777598956"
source: "x"
category: "claude-code"
tags: ["AI-agent", "x"]
date_published: "2026-04-15"
date_collected: "2026-04-15"
summary_by: "auto-x"
---

ハーネスがコンテキスト断片を管理して、経験トレースを高レベルのメモリに蒸留する──この論点、skillsエコシステムを運用していると日々ぶつかる課題そのものでした。「断片の出し入れ」と「再帰動作のエラー率」、出してみて気付いたことをskill改良に戻す、を繰り返すと少しずつ精度が上がっていく感覚があります。#skills


--- 引用元 @Vtrivedy10 ---
Harness, Memory, Context Fragments, & the Bitter Lesson

this is a work in progress mental dump on interesting intersections between how we use and design a harness, implications for memory being accumulated over long timescales, and the search bitter lesson we can’t escape

this is v30+, HTML diagrams help me iteratively refine + chat to roughly “see” and alter the mental model

Harnesses & Context Fragments:
a very important job of the harness is to efficiently & correctly route data within its boundaries into the context window boundary for computation to happen

the context window is a precious artifact.  Harnesses make decisions on how to populate, manage, edit, and organize it so agents can do work.  Each loaded object can be thought of as a Context Fragment and represents an explicit decision by the user and harness designer of what needs a model needs to do work at any given time.

many ideas on externalizing objects + loading into the context window are pioneered and very well described by @a1zhang with RLMs

Experiential Memory:
we’re in the very early days of deploying agents and agents produce massive amounts of data in every interaction they have.  this is akin to humans doing things and remembering things they did.

however agent memory has a massive advantage as it can be accumulated across all agents which are easily forked and duplicated (unlike humans).  @dwarkesh_sp does a good talking about this massive benefit of artificial systems

memory can be treated as an externalized object.  the harness is tasked with doing good contextualized retrieval which means pulling in the right data from accumulated memories across all agent interactions

Search & The Bitter Lesson:
As we deploy agents in our world over year timescales, there is going to be a hyper-exponential in
