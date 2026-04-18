---
id: "2026-04-18-prologでllmの論理推論を強化するmcpサーバーを作ってみた-01"
title: "PrologでLLMの論理推論を強化するMCPサーバーを作ってみた"
url: "https://qiita.com/rikarazome/items/d78fcb4a810035493c23"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "LLM", "qiita"]
date_published: "2026-04-18"
date_collected: "2026-04-18"
summary_by: "auto-rss"
query: ""
---

## はじめに

LLMに論理パズルを出すと、簡単な三段論法は解けるのに、制約が絡む問題になると間違える。

たとえば覆面算（SEND + MORE = MONEY）。各文字に0-9の異なる数字を当てはめるだけの問題だが、Claude Sonnetでも間違える。組み合わせが多すぎて、推測では正解にたどり着けない。

一方Prologなら制約を書くだけで一瞬で解ける。LLMにPrologを書かせて、実行はPrologに任せればいい。そう考えて、SWI-PrologをMCPサーバーとして使えるようにする [prolog-reasoner](https://github.com/rikarazome/prolog-reasoner) を作った。

### この記事でわかること

- LLMがどういう論理問題で間違えるか
- prolog-reasonerの仕組みと使い方
- Prologに任せるとどれくらい精度が変わるか（ベンチマーク結果）

## LLMが間違える問題

LLM単体だとどこで躓くか、具体例を見る。

### 覆面算 SEND + MORE = MONEY

各文字に0-9
