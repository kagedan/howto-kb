---
id: "2026-04-12-masahitoyasuda-自分でデータを蓄積するllmwikiがどの程度役に立つのかとりあえずo-01"
title: "@MasahitoYASUDA: 自分でデータを蓄積するLLMwikiがどの程度役に立つのか、とりあえずObsidianとCoworkで構築してみました。"
url: "https://x.com/MasahitoYASUDA/status/2043144575074853080"
source: "x"
category: "cowork"
tags: ["AI-agent", "LLM", "cowork", "x"]
date_published: "2026-04-12"
date_collected: "2026-04-13"
summary_by: "auto-x"
query: "Cowork スケジュール OR Cowork スキル作成 OR Cowork 自動化"
---

自分でデータを蓄積するLLMwikiがどの程度役に立つのか、とりあえずObsidianとCoworkで構築してみました。まずはやってみないと、その有用性は分からないと思うので。その日に読んだ論文やwebページをrawフォルダに全て投げておいて、深夜にCoworkのスケジュール化したタスクで解析、分類させてます


--- 引用元 @karpathy ---
LLM Knowledge Bases

Something I'm finding very useful recently: using LLMs to build personal knowledge bases for various topics of research interest. In this way, a large fraction of my recent token throughput is going less into manipulating code, and more into manipulating knowledge (stored as markdown and images). The latest LLMs are quite good at it. So:

Data ingest:
I index source documents (articles, papers, repos, datasets, images, etc.) into a raw/ directory, then I use an LLM to incrementally "compile" a wiki, which is just a collection of .md files in a directory structure. The wiki includes summaries of all the data in raw/, backlinks, and then it categorizes data into concepts, writes articles for them, and links them all. To convert web articles into .md files I like to use the Obsidian Web Clipper extension, and then I also use a hotkey to download all the related images to local so that my LLM can easily reference them.

IDE:
I use Obsidian as the IDE "frontend" where I can view the raw data, the the compiled wiki, and the derived visualizations. Important to note that the LLM writes and maintains all of the data of the wiki, I rarely touch it directly. I've played with a few Obsidian plugins to render and view data in other ways (e.g. Marp for slides).

Q&A:
Where things get interesting is that once your wiki is big enough (e.g. mine on some recent research is ~100 articles and ~400K words), you can ask your LLM agent all kinds of complex questions against the wiki, and it will go off, research the answers, etc. I thought I had to reach for fancy RAG, but the LLM has been pretty good about auto-maintaining index files and brief summaries of all the documents and it reads all the important related data fairly easily at this ~small scale.

Output:
Instead of getting answers
