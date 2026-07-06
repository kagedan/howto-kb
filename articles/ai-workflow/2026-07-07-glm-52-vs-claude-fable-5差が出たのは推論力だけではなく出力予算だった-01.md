---
id: "2026-07-07-glm-52-vs-claude-fable-5差が出たのは推論力だけではなく出力予算だった-01"
title: "GLM-5.2 vs Claude Fable 5：差が出たのは推論力だけではなく出力予算だった"
url: "https://qiita.com/xujfcn/items/5572380abf7da0e82f6a"
source: "qiita"
category: "ai-workflow"
tags: ["API", "OpenAI", "GPT", "JavaScript", "qiita"]
date_published: "2026-07-07"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

# GLM-5.2 vs Claude Fable 5：差が出たのは推論力だけではなく出力予算だった

この比較は「どちらが絶対に強いか」を決める記事ではありません。実際の API 呼び出しで、GLM-5.2 は出力予算を増やすと数学・物理の推論を正しく返しました。一方で Claude Fable 5 は低い予算でも短く安定し、長い HTML アニメーションではより確実に完走しました。

![GLM-5.2 vs Claude Fable 5 benchmark](https://gcore.jsdelivr.net/gh/xujfcn/images@main/blog/posts/model-compare-fable5-gpt55-round2-claude-fable5.png)

## このテストを見る理由

The test used the Crazyrouter OpenAI-compatible API rather than a chat UI. That matters because the result was not judged only by prose quality. Each response was checked with operational metadata:

```text
Base URL: https://cn.crazyrouter.com/v1
Endpoint: POST /v1/chat/completions
Models: glm-5.2, claude-fable-5
temperature: 0.2
Test date: 2026-07-06
```

The important fields were `max_tokens`, `completion_tokens`, `reasoning_tokens`, `finish_reason`, visible content length, whether the generated HTML was closed, and whether the animation actually moved in a browser.

## テストした課題

The benchmark deliberately mixed three task types:

| Task | Purpose | Reference result |
|---|---|---|
| `MATH-003` | State-based expectation reasoning | Expected flips until HH = `6` |
| `PHYS-003` | Momentum plus energy accounting | `V = 3.0 m/s`, `x ≈ 0.148 m` |
| `CODE-003-ANIM` | Long runnable artifact generation | Complete 800x500 Canvas animation HTML |

The first two tasks measured reasoning. The third task measured whether a model can produce a complete artifact, not merely a convincing partial code block.

## 観測結果

| Task | `glm-5.2` | `claude-fable-5` |
|---|---|---|
| Math, original budget | `finish_reason=length`, `completion_tokens=1601`, `reasoning_tokens=1600`, visible body empty | `finish_reason=stop`, complete and correct |
| Math, retest | Correct after `max_tokens=3200` | Retest not needed |
| Physics, original budget | `finish_reason=length`, visible body empty | Complete and correct |
| Physics, retest | Correct after `max_tokens=8000` | Retest not needed |
| Animation, original budget | Empty visible HTML at `max_tokens=3200` | Partial HTML, truncated |
| Animation, retest | Still truncated at `max_tokens=8000` | Complete HTML; browser validation passed |

The most important observation is that GLM-5.2 was not failing the reasoning itself. In the math and physics tasks, it produced correct answers after a larger output budget. The problem was visibility and completion: a request could return HTTP 200 while the user-facing content was empty or incomplete.

For the long Canvas animation, the difference was sharper. GLM-5.2 produced a visible HTML fragment at `max_tokens=8000`, but it stopped inside JavaScript and did not close the file. Claude Fable 5 completed the HTML at `max_tokens=8000`; browser validation showed no console errors, an 800x500 canvas, controls, a speed slider, and `changedPixels=55090` after 700 ms.

## 費用対効果の見方

執筆時点で Crazyrouter の pricing API は `glm-5.2` に `discount: 0.8` を返しています。つまり、`reasoning_tokens` と `max_tokens` をきちんと監視できる用途では、GLM-5.2 はかなり費用対効果の高い選択肢になります。

This is the practical tradeoff:

| Workload | Better fit from this test |
|---|---|
| Short reasoning with enough output budget | GLM-5.2 can be a cost-effective option |
| Low-budget reasoning responses | Claude Fable 5 was steadier |
| Long single-file code generation | Claude Fable 5 was stronger in this run |
| Batch evaluations where metadata is logged | GLM-5.2 becomes easier to operate safely |

Do not treat the `0.8` multiplier as a permanent universal price. It is a pricing-data snapshot from Crazyrouter at publication time and should be checked again before a large deployment.

## 実装時の注意

Minimal request:

```bash
curl https://cn.crazyrouter.com/v1/chat/completions \
  -H "Authorization: Bearer $CRAZYROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-5.2",
    "messages": [
      {
        "role": "user",
        "content": "Solve the HH expected-flips problem with state equations."
      }
    ],
    "temperature": 0.2,
    "max_tokens": 3200
  }'
```

To compare Claude Fable 5, keep the same payload and change only the model:

```json
{
  "model": "claude-fable-5"
}
```

For production-style evaluations, log this shape for every request:

```json
{
  "model": "glm-5.2",
  "max_tokens": 3200,
  "finish_reason": "length",
  "completion_tokens": 3200,
  "reasoning_tokens": 3178,
  "visible_content_chars": 0,
  "html_closed": false,
  "browser_validation": "not_run_incomplete_html"
}
```

API endpoints should stay clean. Do not add UTM parameters to `https://cn.crazyrouter.com/v1`. Use tracking only on human-facing article or registration links.

同じ OpenAI 互換リクエストを Crazyrouter で流し、自分のプロンプトで両モデルを比較できます。

https://crazyrouter.com/register?utm_source=external&utm_medium=article&utm_campaign=glm52_fable5_budget_cost_20260706&utm_content=external_glm-52-vs-claude-fable-5-output-budget-cost-ja_20260706__bottom&utm_term=glm-5.2+claude+fable+5+benchmark

## FAQ

### Did GLM-5.2 fail the reasoning tasks?

No. In this run, GLM-5.2 solved the math task after `max_tokens=3200` and the physics task after `max_tokens=8000`. The issue was that lower budgets were consumed mostly by reasoning tokens before visible content appeared.

### Why not score HTTP 200 as success?

Because HTTP 200 only means the API call returned. A benchmark answer can still be unusable if `finish_reason=length`, visible content is empty, or generated code is incomplete.

### Why was the animation task included?

Long code generation exposes a different failure mode. A model can write a convincing first half of a file and still fail if the HTML or JavaScript is cut off.

### Is GLM-5.2 still worth testing?

Yes. The current `0.8` discount multiplier makes it attractive for workloads where you can allocate enough output budget and monitor response metadata.

### What should be recorded in future comparisons?

At minimum: `max_tokens`, `completion_tokens`, `reasoning_tokens`, `finish_reason`, visible output length, artifact completeness, and runtime validation.

## Final verdict

結論は単純ではありません。GLM-5.2 はコスト面で魅力があり推論も可能ですが、出力予算の管理が必要です。Claude Fable 5 は短い回答と完成した単一 HTML 生成で安定していました。
