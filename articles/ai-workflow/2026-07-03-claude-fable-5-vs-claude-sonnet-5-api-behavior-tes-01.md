---
id: "2026-07-03-claude-fable-5-vs-claude-sonnet-5-api-behavior-tes-01"
title: "Claude Fable 5 vs Claude Sonnet 5: API Behavior Test"
url: "https://qiita.com/xujfcn/items/3d0d034fe92ea8222ae3"
source: "qiita"
category: "ai-workflow"
tags: ["API", "OpenAI", "qiita"]
date_published: "2026-07-03"
date_collected: "2026-07-04"
summary_by: "auto-rss"
query: ""
---

# Claude Fable 5 vs Claude Sonnet 5: API Behavior Test

On 2026-07-03, both `claude-fable-5` and `claude-sonnet-5` appeared in Crazyrouter `/v1/models` with OpenAI-compatible endpoint support.

Test base URL:

```text
https://cn.crazyrouter.com/v1
```

Simple exact-output test:

| Model | Response ID | Visible output |
|---|---|---|
| `claude-fable-5` | `msg_01MPuZqzZwj6ysEuzamkxdUC` | `Claude Fable 5 test OK` |
| `claude-sonnet-5` | `msg_0195uVQqkDHcxNFgnJYiPTNV` | `Claude Sonnet 5 test OK` |

Same JSON task:

| Model | Response ID | Result |
|---|---|---|
| `claude-fable-5` | `msg_018ht1NoiLUSdhnSAw7ScQ8g` | Returned visible compact JSON |
| `claude-sonnet-5` | `chatcompl_01VV1nUDJdqUwjgH2zBfVUp7` | HTTP 200, finish_reason stop, but empty visible content |

Production lesson: validate visible content and output shape. HTTP 200 is not enough.

Full article: https://crazyrouter.com/blog/claude-fable-5-vs-claude-sonnet-5-api-test-2026?utm_source=qiita&utm_medium=article&utm_campaign=claude_fable_vs_sonnet_20260703&utm_content=qiita_claude-fable-5-vs-sonnet-5_20260703__canonical&utm_term=Claude%20Fable%205%20vs%20Claude%20Sonnet%205
