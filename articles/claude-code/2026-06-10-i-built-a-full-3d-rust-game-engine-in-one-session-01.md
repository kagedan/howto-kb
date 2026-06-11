---
id: "2026-06-10-i-built-a-full-3d-rust-game-engine-in-one-session-01"
title: "I built a full 3D Rust game engine in one session with Claude Fable 5"
url: "https://zenn.dev/tonrakun/articles/f1d57df4c3e2e8"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "Python", "JavaScript", "TypeScript", "zenn"]
date_published: "2026-06-10"
date_collected: "2026-06-11"
summary_by: "auto-rss"
query: ""
---

Fable 5 dropped 2026 6/9 (jp time). I poked at it for a bit and then just went for it: asked it to build a 3D game engine in Rust from scratch. Physics engine, GUI editor, script editor — the whole thing. One session, no resets.

I'm on the $20/month Pro plan. No Max, no Max 2.

Here's how that worked.

---

## The token problem with Fable 5

Fable 5 is genuinely good at coding. The SWE-Bench Pro numbers aren't hype. But it's priced at $10/$50 per million input/output tokens — exactly 2× Opus 4.8.

In practice that means context fills up faster. You hit the ceiling, Claude resets, then has to re-read all your files from scratch, which fills the context again. With Fable 5, that loop comes at you twice as fast.

To get around that I've been using **T0K3N-MCP**, an MCP server I wrote myself.

---

## What T0K3N-MCP does

Short version: it cuts token consumption by up to 87% by never reading more of a file than it needs to.

Standard file reads dump the whole thing into context:

```
read_file("mod.rs")  →  4,997 tokens (95% of it irrelevant to what you asked)
```

T0K3N-MCP does it in two steps — get the structure first, then fetch only the part you actually need:

```
read_code_skeleton("mod.rs")       →  1,162 tokens (signatures only)
read_code_body(["function:54-67"]) →    150 tokens (just that function)
                                        ─────────────────────────────
Total                                   1,312 tokens  ← 74% saved
```

### The numbers

I measured this with Anthropic's token-counting API using `claude-haiku-4-5-20251001` — not Fable 5 itself. That model was just the measuring instrument. The reduction comes from reading less of the file, so the savings are the same regardless of which model is actually doing the coding.

I've now run this across four languages against real production codebases:

| Codebase | Language | Per-file savings | Project-level |
| --- | --- | --- | --- |
| T0K3N-MCP itself | Rust | **87.3%** | ~90% |
| vercel/commerce | TypeScript | **75.5%** | **86.0%** |
| pallets/flask | Python | **78.8%** | **90.5%** |
| gin-gonic/gin | Go | **70.4%** | **85.6%** |
| **Grand average** | — | **78.0%** | **88.0%** |

Go lands lowest at 70%, and there's a concrete reason for it. Idiomatic Go tends to have large interface surfaces — lots of small methods with explicit receiver types like `func (c *Context) GetString(key any) string`. That means the skeleton already retains a lot of information, so there's less body to discard. Still a 70% reduction. Python comes in at 78.8%, just behind Rust.

Effective context window: **4.5–8× larger** depending on the language.

---

## Supported languages

Code analysis (skeleton reads, dependency graphs, complexity maps, etc.) works across 13 languages:

| Language | Extensions |
| --- | --- |
| Rust | `.rs` |
| Python | `.py` |
| JavaScript | `.js`, `.jsx` |
| TypeScript | `.ts`, `.tsx` |
| Go | `.go` |
| C++ | `.cpp`, `.cc`, `.cxx`, `.hpp` |
| Java | `.java` |
| Kotlin | `.kt` |
| Swift | `.swift` |
| Ruby | `.rb` |
| C# | `.cs` |
| PHP | `.php` |
| Lua | `.lua` |

Parsers are statically linked into the binary via tree-sitter — no Node.js, no Python dependency. New language requests go in Issues.

---

## What I actually built

Right after Fable 5 launched I threw this at it: build a full 3D-capable game engine in Rust from scratch.

What came out:

* 3D rendering pipeline
* ECS (Entity-Component-System)
* Physics engine (full implementation, not a stub)
* GUI editor
* Script editor

All in one session.

When I say "one session" I don't mean I finished it in under some time limit. The point is the **token budget never ran out**. No context overflow, no reset-and-reload. T0K3N-MCP kept consumption low enough that the whole project fit inside the context window from start to finish.

---

Beyond T0K3N-MCP's tooling, I hit `/clear` pretty aggressively between phases. Conversation history piles up and eats tokens even when it's not useful anymore. Clearing it at natural breakpoints — once the architecture was locked, once a module was done — kept things lean.

The thing that makes this actually work is `session_snapshot` / `session_restore`. Save state before clearing, restore it after. You don't lose anything.

The rest T0K3N-MCP handles: `check_budget` picks the right read strategy automatically, `batch_read` collapses multiple file reads into one call, and `memory_save` / `memory_get` carries information across sessions.

---

## The math

Fable 5 at 2× Opus, then T0K3N-MCP knocks 87% off that:

```
Fable 5 cost           =  Opus 4.8 × 2.0
After T0K3N-MCP (−87%) =  Opus 4.8 × 2.0 × 0.13
                       =  Opus 4.8 × 0.26
```

Mythos-class model, less than a quarter of Opus token spend. The Pro plan is fine.

---

Repo:  
<https://github.com/tonrakun/t0k3n-mcp>  
Full benchmark methodology is in `.docs/benchmark_token_savings.md` and `.docs/benchmark_multilanguage_study3_4.md`
