---
id: "2026-04-03-ai-ergonomics-is-garbage-collector-a-liability-for-01"
title: "AI Ergonomics: Is Garbage Collector a Liability for AI Agents?"
url: "https://zenn.dev/flp/articles/ai-ergonomics"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

![GC](https://res.cloudinary.com/zenn/image/fetch/s--fOGfhXIT--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/ai-ergonomics/gc.png?_a=BACAGSGT)

Lately, as we’ve been using AI agents to write more code, the obvious results have happened:

* The amount of code written per time period goes way up.
* The bottleneck shifts from writing to verification.
* A “fast feedback” mechanism is becoming more valuable.

That made me wonder: if we rely more on AI agents to write code, what's the possible impact on the trends in programming languages?

And this led me to a specific question I want to share as **food for thought**:

> “We built garbage collectors to reduce human cognitive load. What happens when the primary coder isn’t human anymore?”

## Human-First Design

To understand why this shift might be happening, we have to look at why the Garbage Collector was designed for "Human Era".

In the early era, hardware efficiency was the priority. Engineers had to manually control memory allocation and they owned the burden of memory safety. But humans often made mistakes, which led to crashes and corrupted state. Manual memory management was high-performance, but it was mentally exhausting.

Once the hardware became fast enough, GC (Java, Python, Go) began gaining traction to prioritize "Human Velocity", trading hardware efficiency for lowering cognitive load on managing lifecycles. We chose "Human Ergonomics" over "Hardware Efficiency".

We also accepted opaqueness as trade-off. The burden of memory safety was shifted to runtime. Memory management became dependent on runtime profiling to find and understand an issue. For humans, this trade-off was a great deal. But this opaqueness becomes interesting once the author changes.

## An Emerging Alternative: The Promise of Performance & Safety

Before agentic coding became mainstream, we saw a rise in "strict" languages like Rust. It was built as a way to guarantee memory safety by moving the burden from engineers to compile-time constraints.

For humans, this is often a steep learning curve. In this case, we sacrifice initial velocity for "Zero-Cost Safety"—strong memory safety with high performance.

But here is my observation: By building these strict, deterministic referee to save ourselves from our own mistakes, we may have accidentally built **an ideal environment for an AI feedback loop**.

## And The Agent Came: A Flip in “Ergonomic”

In an agentic workflow, the definition of "ergonomic" is flipping upside down.

### The Cognitive Load Flip

Humans find strict rules like ownership and lifetimes to be friction. While agent see it as fast, structured signals to iterate toward correctness. An agent can also absorb the cognitive burden of writing complex memory safe code.

### Feedback Loops Comparison

Compare the two ways an AI agent "learns" to fix a performance bug:

> The GC Model: Write → Run → Observe → Profile → Tweak.

This is slow and noisy. The agent has to trace how an opaque GC process behaves at runtime.

> The Compiler Model: Write → Compile → Get Precise Error → Fix.

This is fast, deterministic, and text-rich feedback loop. A compiler error tells the agent exactly what is wrong and why, right in the source code.

In an agentic world, "Opaqueness" becomes a liability. If an AI agent can’t see lifetimes or resource constraints clearly in the code, it has to predict runtime behavior. So what used to be a small trade-off for human convenience might become a bigger cost in an agentic workflow where verification is the bottleneck.

## The Possible Implication

If this thesis holds, a couple of implications could follow.

1. Building a modern Garbage Collector is an enormous engineering investment. We paid that cost to unlock human productivity. But why keep this investment if the author of the code is capable of following the strict set of rules flawlessly?
2. This investment could shift toward something else that can give earlier feedback and verification (compilers, analyzers).
3. Zero-cost safety: We might be able to reclaim the hardware efficiency without sacrificing memory safety and reducing development velocity.

## Beyond Memory Management

I suspect this isn't just about memory management. We might be seeing a broader trend from **opaque runtime feedback** toward **transparent compile-time feedback loop**? Systems that validate correctness earlier are becoming more "ergonomic" for the AI agents writing our code.

What do you think? Are we heading toward a post-GC world?

Where else do you think AI is "flipping" our preference within software engineering?

Curious to hear your perspectives and counter-arguments below! 👇

### PS:

Follow FLP on [GitHub](https://github.com/flpstudio) and [LinkedIn](https://www.linkedin.com/company/fujitsu-launchpad/) to stay updated on new products and technologies from our team.

---

---

---

# 🇯🇵 日本語版

![GC](https://res.cloudinary.com/zenn/image/fetch/s--fOGfhXIT--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/v1/ai-ergonomics/gc.png?_a=BACAGSGT)

最近、AIエージェントにコードを書いてもらう場面が増えてきて、わかりやすい変化がいくつか起きています。

* 一定時間あたりに書かれるコード量が大きく増える
* ボトルネックが「書くこと」から「検証すること」へ移る
* 「速いフィードバック」を返せる仕組みの価値がどんどん上がる

そこで気になったんです。コードを書く主体をAIエージェントにより強く依存するようになると、プログラミング言語のトレンドにはどんな影響が出るんだろう、と。

その流れで、ひとつ考えるきっかけとして共有したい問いがあります。**ちょっとした思考材料**として読んでもらえるとうれしいです。

> “人間の認知負荷を下げるために Garbage Collector を作ってきました。では、コードを書く主役がもう人間ではないとしたら、何が起きるでしょうか？”

## 人間中心の設計

なぜこんな変化が起こりうるのかを考えるには、まず Garbage Collector が「人間の時代」に向けて設計された理由を見る必要があります。

初期の時代は、とにかくハードウェア効率が最優先でした。エンジニアはメモリ確保を手動で制御する必要があり、メモリ安全性の責任も自分たちで負っていました。でも、人間はどうしてもミスをします。その結果、クラッシュしたり、状態が壊れたりしがちでした。手動メモリ管理は高性能ではあるものの、かなり神経を使う作業だったんですよね。

その後、ハードウェアが十分に速くなると、GC（Java、Python、Go）が広まり始めます。ライフサイクル管理の認知負荷を下げるために、ハードウェア効率を少し犠牲にしてでも「Human Velocity」を優先するようになったわけです。つまり、私たちは「Hardware Efficiency」より「Human Ergonomics」を選んできました。

そのトレードオフとして、不透明さも受け入れてきました。メモリ安全性の負担は runtime 側に移り、メモリ管理の問題を見つけて理解するには、runtime の profiling に頼ることになります。人間にとっては、これはかなりお得な交換条件でした。ただ、コードの書き手が変わると、この不透明さはちょっと面白い論点になってきます。

## 新しく浮上している代替案: Performance と Safety の約束

agentic coding が当たり前になる前から、Rust のような「strict」な言語が伸びてきていました。これは、メモリ安全性の負担をエンジニアから compile-time の制約へ移すことで、安全性を保証しようとするアプローチです。

人間にとっては、これはしばしば学習コストが高いです。この場合、初速は多少犠牲にする代わりに、「Zero-Cost Safety」――高い性能を保ちながら強いメモリ安全性を得ます。

ただ、ここでひとつ思っていることがあります。自分たちのミスを防ぐために、こうした strict で deterministic なレフェリーを作ってきた結果、**AIのフィードバックループにとって理想的な環境**を、意図せず用意してしまったのかもしれません。

## そしてエージェントがやってきた: 「Ergonomic」の反転

agentic workflow では、「ergonomic」の意味そのものがひっくり返りつつあります。

### Cognitive Load の反転

ownership や lifetime のような strict なルールは、人間にとっては摩擦になりがちです。一方でエージェントにとっては、正しさに向けて反復するための、速くて構造化されたシグナルに見えます。しかも、複雑でメモリ安全なコードを書くときの認知的な負担も、エージェント側が吸収できます。

### フィードバックループの比較

AIエージェントがパフォーマンスバグを直そうとするとき、「学び方」は大きく2つあります。

> GC モデル: Write → Run → Observe → Profile → Tweak.

これは遅くてノイジーです。エージェントは、opaque な GC の処理が runtime でどう振る舞うかを追いかけなければいけません。

> Compiler モデル: Write → Compile → Get Precise Error → Fix.

こちらは速くて deterministic で、しかもテキスト情報が豊富なフィードバックループです。compiler error は、何が悪いのか、なぜ悪いのかを、source code のその場でかなり正確に教えてくれます。

agentic な世界では、「Opaqueness」は弱点になってきます。AIエージェントが code の中で lifetime や resource constraints を明確に見通せないなら、runtime の挙動を予測しないといけません。そうなると、人間の利便性のためには小さなトレードオフだったものが、検証がボトルネックになる agentic workflow では、もっと大きなコストになるかもしれません。

## 考えられる示唆

この仮説が成り立つなら、いくつかの示唆がありそうです。

1. モダンな Garbage Collector を作るのは、とてつもなく大きなエンジニアリング投資です。私たちは人間の生産性を上げるためにそのコストを払ってきました。でも、コードの書き手が strict なルールを正確に守れるなら、その投資を今後も維持する理由はどこまであるでしょうか。
2. その投資先は、より早いフィードバックや検証を返せるもの（compiler、analyzer）へ移っていくかもしれません。
3. Zero-cost safety: メモリ安全性を犠牲にせず、開発速度も落とさずに、ハードウェア効率を取り戻せる可能性があります。

## メモリ管理だけの話ではない

これはメモリ管理に限った話ではない気がしています。もっと広く見ると、**opaque な runtime feedback** から **transparent な compile-time feedback loop** への流れが起きているのかもしれません。より早い段階で正しさを検証できるシステムのほうが、コードを書くAIエージェントにとっては、より「ergonomic」になりつつあるのではないでしょうか。

みなさんはどう思いますか？ 私たちは post-GC な世界に向かっているんでしょうか。

他に、software engineering の中で、AI が私たちの好みを「反転」させている領域ってどこにあると思いますか？

ぜひ、みなさんの視点や反論も聞いてみたいです！👇

### PS:

FLP の最新プロダクトやテクノロジー情報は、[GitHub](https://github.com/flpstudio) と [LinkedIn](https://www.linkedin.com/company/fujitsu-launchpad/) で確認できます。ぜひフォローしてください
