---
id: "2026-07-05-ai-masaou-httpstcolejjil89v4-01"
title: "@AI_masaou: https://t.co/lEjJIL89V4"
url: "https://x.com/AI_masaou/status/2073718435725689018"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "x"]
date_published: "2026-07-05"
date_collected: "2026-07-06"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/lEjJIL89V4

いつも通り、動画でも解説しているのでこちらもご覧ください✔︎

https://t.co/QR06ViCplU


--- Article ---
Claude Code に大きめの仕事を任せて、結果に「そうじゃない」と返した経験はないだろうか。その原因はモデルの能力ではなく、自分が言語化できていない「未知」にある — Anthropic の Thariq 氏はそう説く。本ページは 2026-07-04 公開の長文記事 [「A Field Guide to Fable: Finding Your Unknowns」](https://x.com/trq212/status/2073100352921215386) (86 万 views) を日本語で網羅解説する。

## 結論:

1. 仕事の質のボトルネックは、モデルではなく「自分の未知を明確にする力」に移った。
1. 未知は 4 象限で棚卸しする。危険なのは「無自覚の既知」と「無自覚の未知」。
1. 実装の前・最中・後に未知を潰す 8 つの技法がある。すべてプロンプト例付き。
# 地図は現場ではない — すべての出発点

prompt は「地図」、codebase は「現場」。その差分が未知になる。

![](https://pbs.twimg.com/media/HMdRrvcbEAAgr5r.jpg)

> **「Fable は、仕事の質が『自分の未知を明確にする力』でボトルネックになる最初のモデルだ」** — これが記事の中心的な主張だ。モデルの実行力が十分に高くなった結果、詰まる場所が人間側に移った。

ただし、事前の計画だけでは足りない。未知は実装の奥深くで見つかることがある。さらに「そもそも別の解き方をすべきだ」と、未知の方から教えてくれることさえある。

だから著者は、Fable との仕事をこう定義する。実装の「前・最中・後」に、自分の未知を発見し続ける反復プロセスだ。著者が公開している [未知発見用のサンプル集](https://thariqs.github.io/html-effectiveness/unknowns/) も本記事とあわせて参照できる。

# 未知の 4 象限 — 「何を知らないか」を知る

#  問題を Claude に持ち込む前に、自分の知識を 4 つに分けて棚卸しする。

問題を Claude に持ち込む前に、自分の知識を 4 つに分けて棚卸しする。

![](https://pbs.twimg.com/media/HMdSoVKaAAEd9Y7.jpg)

- **既知の既知** — prompt に書けていること。「何をしてほしいか」を伝えられている部分。
- **既知の未知** — まだ決めていない、と自覚できていること。
- **無自覚の既知** — 当たり前すぎて書き出さないが、見せられれば「それだ」と分かること。
- **無自覚の未知** — 考えたことすらないこと。「どこまで良くできるか」の上限を知らないことも、ここに含まれる。
**上手い人ほど、未知が少ない。**著者は [Boris](https://www.linkedin.com/in/bcherny) (Claude Code 作者の Boris Cherny 氏) や [Jarred](https://www.linkedin.com/in/jarred-sumner-a8772425) (Bun 作者の Jarred Sumner 氏) のプロンプトを見て、こう述べる。「欲しいものを細部まで知っているのが明らかだ」。彼らは codebase ともモデルの挙動とも、深く同期している。

それでも彼らは「未知は必ず残る」前提で動く。未知を減らし、未知に備える — それ自体が agentic coding (AI にコードを書かせて進める開発) の技能だ。そしてこの技能は、Claude と働くうちに上達していく。

# さじ加減の罠 — 具体的すぎても、曖昧すぎても失敗する

未知を考慮しない指示は、正反対の 2 方向に同時に失敗する。

![](https://pbs.twimg.com/media/HMdSwZEbUAAtsbi.jpg)

未知を放置すると、この 2 つの失敗を同時に引く。道が塞がっているのか、開けているのか。それを自分でも知らないまま、要所では Claude の側から進路を変えてほしいと期待する。この期待には無理がある。

**救いは、Claude 自身が未知の発見を速めてくれること**だ。

- codebase もインターネットも、人間よりはるかに速く探索できる
- たいていの話題なら
