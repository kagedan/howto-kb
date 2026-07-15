---
id: "2026-07-15-agent-harnessを差し替えても運用責任までは差し替わらない-01"
title: "agent harnessを差し替えても、運用責任までは差し替わらない"
url: "https://zenn.dev/heftykoo/articles/0aa568b64a1f13"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "zenn"]
date_published: "2026-07-15"
date_collected: "2026-07-16"
summary_by: "auto-rss"
query: ""
---

AI SDK 7 の `HarnessAgent` は、Claude Code や Codex などの agent harness を一つの `Agent` interface から扱える。

この説明を読むと、model provider の延長で agent の実行系も交換できそうに見える。設定を一行変えれば、UI も呼び出し側もそのまま。たしかに、そこまでは合っている。

危ないのは、その先だ。

interface が揃っても、安全性まで揃うとは限らない。agent harness は model API よりずっと machine に近い。shell を動かし、file を書き、network に出て、session を持ち越す。抽象化で消えるのは呼び出し方の差であって、副作用の差ではない。

## 共通化されたのは「入口」である

公式の例はかなり短い。

```
import { HarnessAgent } from '@ai-sdk/harness/agent';
import { claudeCode } from '@ai-sdk/harness-claude-code';
import { createVercelSandbox } from '@ai-sdk/sandbox-vercel';

const agent = new HarnessAgent({
  harness: claudeCode,
  sandbox: createVercelSandbox({ runtime: 'node24' }),
  instructions: 'Review the repository and make a small, safe fix.',
});

const result = await agent.generate({
  prompt: 'Fix the failing unit test.',
});
```

`harness` に渡す adapter を変えても、`generate` や `stream` の呼び出しは保てる。既存の `useChat` とつなぐ UI 側も、大きく書き換えずに済む。ここは素直に便利だ。

ただ、この code に「small, safe fix」と書いたから安全になるわけではない。どの command を危険と見なすか、どこまで network access を許すか、session の再開時に何を引き継ぐかは、この interface だけでは決まらない。

model provider の抽象化では、主な差分を request と response の形に押し込めやすかった。agent harness の差分は runtime に漏れる。漏れるというより、そもそも runtime が本体に近い。

## approvalとsandboxをadapterの外へ出す

最初に分離したいのは approval と sandbox だと思う。

たとえば、片方の harness では file 削除の直前に承認を求め、別の harness では shell command 全体に承認を求めるかもしれない。permission rule の粒度も、default deny の範囲も共通とは限らない。両方が `Agent` interface を満たしていても、止まり方は違う。

sandbox も「設定してあるか」だけでは足りない。

workspace 外へ書けるのか。環境変数はどこまで見えるのか。外部 network は閉じているのか。子 process に制限が引き継がれるのか。入力が同じでも、ここが違えば risk は変わる。

そこで、adapter 名とは別に、製品側の runtime policy を持たせる。

```
type RuntimePolicy = {
  approval: 'destructive-only' | 'every-tool';
  network: 'deny' | { allow: string[] };
  sessionTtlMs: number;
  timeout: {
    totalMs: number;
    toolMs: number;
  };
  telemetry: {
    includeRuntimeContext: string[];
  };
};
```

これは AI SDK の型ではなく、application 側の契約である。大事なのは、`harness: codex` のような選択と一緒に安全性まで暗黙決定しないことだ。どの adapter を選んでも、製品が要求する境界は別 object として読めるようにする。

## 差し替えるなら、contract testを共有する

interface test だけなら、「応答が返る」「stream が最後まで流れる」で終わる。agent runtime には足りない。

自分なら adapter ごとに、少なくとも次の失敗を実際に起こす。

* 削除 command を要求し、期待した単位で approval が止まるか
* allowlist 外の host へ接続し、network が拒否されるか
* tool を意図的に遅延させ、tool timeout と total timeout を区別できるか
* session を再開し、古い権限や secret が残っていないか
* trace から prompt や runtime context を追える一方、secret が混ざっていないか

全部を一つの E2E に詰め込む必要はない。むしろ、adapter を替えたときに「どの境界が変わったか」を読める小さな検査に分けたほうがいい。

AI SDK 7 自体も、tool approval、複数段階の timeout、sandbox、telemetry を別々の機能として提供している。この並びを見るだけでも、agent の運用 contract が一枚では済まないことが分かる。

## sessionとtelemetryは後回しにすると効いてくる

local demo では、process を落とせば session も終わる。production では、deploy や承認待ちをまたいで処理を再開したくなる。そこで durable execution が必要になるが、再開できることは常に正義ではない。

誰の session なのか。いつ失効するのか。途中で policy が変わったら古い承認を使えるのか。adapter を替えた後も同じ session を継続してよいのか。保存形式を共通化しても、寿命の判断までは共通化されない。

telemetry では、span が出れば観測できたことにはならない。adapter 固有の tool call、approval 待ち、session resume の意味が揃っているかを見る必要がある。runtime context を trace に含める機能は調査に役立つが、含める field を雑にすると secret の新しい流出経路にもなる。

交換可能性を上げるほど、差分を観測する仕組みが要る。少し皮肉だが、抽象化した後のほうが adapter 固有の挙動をよく見なければならない。

## codemodで移行できない部分を先に書く

AI SDK 7 は Node.js 22 と ESM を必須にしている。import の変更や rename は codemod でかなり進められる。

それでも、runtime context の中身、approval policy、timeout の配分、telemetry に含める情報は自動では決められない。compile が通っても、以前の境界が保たれるとは限らない。

移行 checklist の先頭に package 更新を書くより、先に invariant を書いたほうがいい。

「外部 network は default deny」「破壊的操作は必ず人間承認」「session は24時間で失効」「secret は trace に出さない」。その後で adapter を替え、共通の contract test を通す。順序を逆にすると、動いたことだけ確認して安心してしまう。

## portabilityは差分を消すことではない

agent harness の共通 interface は有用だ。特定の実行系を UI や application code に焼き込まずに済む。experimental な package が変わっても、影響範囲を狭くできる。

ただし、portability の完成品ではない。

持ち運ぶ対象には、agent の呼び出し code と、承認、隔離、停止、再開、観測について製品側が決めた境界の両方が入る。その境界を adapter の外に置き、共通の検査で差分を露出させる。

agent portability は、異なる実行系を製品側の責任で運用するための土台である。

## Source notes
