---
id: "2026-05-31-claude-codeユーザーがclojure開発でcodexreplを試してみた-01"
title: "Claude CodeユーザーがClojure開発でCodex+REPLを試してみた"
url: "https://zenn.dev/shinseitaro/articles/claude-code-user-tries-codex-repl-for-clojure"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-05-31"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

## 1. なぜ試すのか

私は普段

で開発しています。

最近 Clojurians Slack を眺めていると

> Codex + REPL

を推す人が増えた気がします。特にvlaaadさん（2026/05/26 20:32:45）この発言が気になりました。

> [Basically what I do in the REPL myself codex can too.](https://clojurians.slack.com/archives/C068E9L5M2Q/p1779795165724429?thread_ts=1779793020.541479&cid=C068E9L5M2Q)

Clojurian = REPL 屋 なので、この発言が刺さった人は多いハズ (思い込み)。私も試してみることにしました。

## 2. 環境準備

私のマシンとEditor環境

* Linux Mint
* VSCode + Calva
* Clojure CLI

Node確認

```
node --version
npm --version
# v22.14.0
# 11.4.2
```

Codex導入

```
npm install -g @openai/codex
```

確認

```
codex --versionc
# codex-cli 0.135.0
```

## 3. サンプルプロジェクト作成

```
mkdir codex-clojure-demo
cd codex-clojure-demo
```

deps.edn

```
{:paths ["src"]}
```

src/demo/core.clj

```
(ns demo.core)

(defn average
  [xs]
  (/ (reduce + xs)
     (count xs)))
```

起動確認

```
(require '[demo.core :as d])

(d/average [1 2 3])
```

## 4. Codex起動

初めてだったんでこんなのでました

```
  Welcome to Codex, OpenAI's command-line coding agent

  Sign in with ChatGPT to use Codex as part of your paid plan
  or connect an API key for usage-based billing

  1. Sign in with ChatGPT
     Usage included with Plus, Pro, Business, and Enterprise plans

  2. Sign in with Device Code
     Sign in from another device with a one-time code

> 3. Provide your own API key
     Pay for what you use
```

とりあえずお試しなので、新しいAPI Key を作成して渡します。この実験が終わったらAPI Key を消せばそれ以上課金されないのでお掃除も楽ちんです。

初めてのプロンプトを渡します。

```
This is a Clojure project.
Always use REPL-driven development.
Start a REPL first.
Never assume functions exist.
Verify everything in the REPL.
Do not stop after writing code.
Run it and confirm it works.
```

ちょっと脱線しますが、"**Never assume functions exist.**" は案外キモです。2026/05/26 19:57:00 に始まった[スレッド](https://clojurians.slack.com/archives/C068E9L5M2Q/p1779793020541479) で、

> ... I've tried chatgpt and gemini via their web interfaces to ask for some simple functions working on tablecloth, XMLs, basic data structures but the results were pretty underwhelming.. eg **regularly giving me code that includes non-existing functions** and stuff like that. ...

ほんとそれ！現象で、LLMはClojureの存在しない関数を平気で呼びます。

たとえば、

```
(require [tablecloth.api :as tc])
(tc/average [1 2 3]) ;; ないよ！ tc/mean はあるけど
```

とか日常茶飯事です。他の言語のLibraryにあるならClojureにもあるんじゃない？ってことみたいです。

なのでプロンプトで強く「関数が既存だと思うなよ！」というのは大切です。

## 5. 最初のタスク

Prompt

```
Add median function.
Use REPL-driven development.
```

こちらが返事

```
• I’ll inspect the namespace and current project shape, then verify the loaded namespace in the running REPL before editing. After the change I’ll reload and exercise the function from the REPL.

• Explored
  └ Read core.clj

• Ran git status --short
  └ fatal: not a git repository (or any of the parent directories): .git

• Explored
  └ Read deps.edn

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• The namespace currently only defines average, and this directory is not a git repo. I’m checking that directly in the REPL now before adding median.

↳ Interacted with background terminal · clojure
  └ (require 'demo.core :reload)
    (ns-publics 'demo.core)
    (resolve 'demo.core/average)
    (resolve 'demo.core/median)

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• demo.core/median is absent in the REPL, so I’m adding it now. I’ll keep the implementation small: sort
  the collection, choose the middle value for odd counts, average the two middle values for even counts,
  and reject an empty collection explicitly.

↳ Interacted with background terminal · clojure
  └ (mapv resolve '[sort count nth inc quot zero?])

• Edited src/demo/core.clj (+10 -0)
     6
     7 +(defn median [xs]
     8 +  (let [sorted-xs (vec (sort xs))
     9 +        n (count sorted-xs)]
    10 +    (if (zero? n)
    11 +      (throw (IllegalArgumentException. "Cannot calculate median of an empty collection"))
    12 +      (let [middle (quot n 2)]
    13 +        (if (odd? n)
    14 +          (nth sorted-xs middle)
    15 +          (average [(nth sorted-xs (dec middle))
    16 +                    (nth sorted-xs middle)])))))))

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• The function is in place. I’m reloading the namespace in the same REPL and checking odd, even,
  unsorted, singleton, ratio, and empty-input behavior.

↳ Interacted with background terminal · clojure
  └ (require 'demo.core :reload)
    (resolve 'demo.core/median)
    (demo.core/median [3 1 2])
    (demo.core/median [4 1 2 3])
    (demo.core/median [10])
    (demo.core/median [1 2])
    (try (demo.core/median []) (catch IllegalArgumentException e (.getMessage e)))

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• The REPL surfaced a reader error on reload, even though the var was still present afterward from the
  attempted load. I’m inspecting the file structure and fixing the delimiter issue before treating the
  result as valid.

• Explored
  └ Read core.clj

• Edited src/demo/core.clj (+1 -1)
    15            (average [(nth sorted-xs (dec middle))
    16 -                    (nth sorted-xs middle)])))))))
    16 +                    (nth sorted-xs middle)]))))))

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• The extra closing paren is fixed. I’m doing a clean REPL reload now and will only count the examples
  after reload succeeds.

↳ Interacted with background terminal · clojure
  └ (require 'demo.core :reload)
    (ns-publics 'demo.core)
    (resolve 'demo.core/median)
    [(demo.core/median [3 1 2])
     (demo.core/median [4 1 2 3])
     (demo.core/median [10])
     (demo.core/median [1 2])]
    (try (demo.core/median []) (catch IllegalArgumentException e (.getMessage e)))

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• The reload succeeded and the REPL examples returned the expected values. I’m closing the REPL session now since the verification for this change is complete.

↳ Interacted with background terminal · clojure
  └ (System/exit 0)

• Ran clojure
  └ Clojure 1.12.4
    user=> (require 'demo.core :reload)
    … +36 lines (ctrl + t to view transcript)
    user=> "Cannot calculate median of an empty collection"
    user=> (System/exit 0)

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• Added median in src/demo/core.clj:7.

  Behavior verified in the REPL after reloading demo.core:

  - [3 1 2] -> 2
  - [4 1 2 3] -> 5/2
  - [10] -> 10
  - [1 2] -> 3/2
  - [] throws IllegalArgumentException with Cannot calculate median of an empty collection

  The REPL reload succeeded before those checks.
```

REPL できちんと評価してますね。しかし作ってきた `median` 関数は全くClojureらしくないですね。むむむ・・・。

ちなみにこの一発で **0.23 USD** 消費してました。

## 6. ベンチマークさせる

次にREPLで実行速度を測ってベンチマークをだすかどうか？確認してみます。

```
Create a faster version of average.
Benchmark it.
```

長いのでアコーディオンしておきます。

返事

```
• I’ll start a fresh REPL first, then inspect what the namespace currently exposes from inside it before changing anything. For benchmarking I’ll stick to local REPL measurements unless the project already
  has a benchmark dependency.

• Explored
  └ Read deps.edn, core.clj

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• The project has no benchmark library configured, and demo.core currently contains average and median.  I’m loading that namespace in the REPL and checking the publics before deciding the fastest compatible
  implementation shape.

↳ Interacted with background terminal · clojure
  └ (require 'demo.core :reload)
    (ns-publics 'demo.core)
    (mapv resolve '[demo.core/average demo.core/median demo.core/fast-average])

• fast-average is absent, so I’m going to prototype the implementation in the REPL first. The likely tradeoff is speed via double arithmetic, so I’ll verify both behavior and timing before saving it.

↳ Interacted with background terminal · clojure
  └ (mapv resolve '[double-array reduce aset-double aget double zero?])
    (defn average-fast-prototype [xs]
      (let [state (reduce (fn [^doubles state x]
                            (aset-double state 0 (+ (aget state 0) (double x)))
                            (aset-double state 1 (+ (aget state 1) 1.0))
                            state)
                          (double-array 2)
                          xs)
            n (aget ^doubles state 1)]
        (if (zero? n)
          (throw (ArithmeticException. "Divide by zero"))
          (/ (aget ^doubles state 0) n))))
    [(average-fast-prototype [1 2 3])
     (average-fast-prototype [1 2])
     (average-fast-prototype [10])]
    (try (average-fast-prototype []) (catch ArithmeticException e (.getMessage e)))

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• The prototype works and intentionally returns double values. I’m benchmarking it against the current exact-ratio average on the same numeric vector now, with a small warmup and a sink to keep calls evaluated.

↳ Interacted with background terminal · clojure
  └ (def bench-data (vec (range 100000)))
    (def sink (volatile! nil))
    (defn run-bench [label f n]
      (println label)
      (time (dotimes [_ n]
              (vreset! sink (f bench-data))))
      @sink)
    (dotimes [_ 20] (demo.core/average bench-data) (average-fast-prototype bench-data))
    (run-bench "average x200" demo.core/average 200)
    (run-bench "average-fast-prototype x200" average-fast-prototype 200)
    (run-bench "average x1000" demo.core/average 1000)
    (run-bench "average-fast-prototype x1000" average-fast-prototype 1000)

• Waited for background terminal · clojure

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• The first prototype was slower on a vector because the mutable accumulator plus function-call overhead loses to Clojure’s optimized reduce +. I’m testing a less invasive double-returning variant next, then I’ll save the version that actually benchmarks faster.

↳ Interacted with background terminal · clojure
  └ (defn average-fast-prototype-2 [xs]
      (/ (double (reduce + xs))
         (count xs)))
    [(average-fast-prototype-2 [1 2 3])
     (average-fast-prototype-2 [1 2])]
    (dotimes [_ 20] (average-fast-prototype-2 bench-data))
    (run-bench "average x1000 repeat" demo.core/average 1000)

↳ Interacted with background terminal · clojure
  └ (mapv resolve '[unchecked-add unchecked-add-int unchecked-long])
    (defn average-fast-prototype-3 [xs]
      (/ (double (reduce unchecked-add 0 xs))
         (count xs)))
    [(average-fast-prototype-3 [1 2 3])
     (average-fast-prototype-3 [1 2])]
    (dotimes [_ 20] (average-fast-prototype-3 bench-data))
    (run-bench "average-fast-prototype-3 x1000" average-fast-prototype-3 1000)
    (run-bench "average x1000 repeat2" demo.core/average 1000)

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• The simple variants still aren’t faster for ordinary vectors. The useful speedup is for primitive numeric arrays, where we can avoid boxed sequence reduction entirely, so I’m verifying Clojure’s array primitives and benchmarking that path against the existing average.

↳ Interacted with background terminal · clojure
  └ (mapv resolve '[areduce alength instance? Class/forName])
    (def double-array-class (Class/forName "[D"))
    (defn average-fast-prototype-4 [xs]
      (if (instance? double-array-class xs)
        (let [^doubles a xs
              n (alength a)]
          (if (zero? n)
            (throw (ArithmeticException. "Divide by zero"))
            (/ (areduce a i sum 0.0 (+ sum (aget a i))) n)))
        (/ (double (reduce + xs)) (count xs))))
    (def bench-doubles (double-array (range 100000)))
    [(average-fast-prototype-4 bench-doubles)
     (demo.core/average bench-doubles)]
    (dotimes [_ 20] (demo.core/average bench-doubles) (average-fast-prototype-4 bench-doubles))
    (defn run-bench-on [label f data n]
      (println label)
      (time (dotimes [_ n]
              (vreset! sink (f data))))
      @sink)
    (run-bench-on "average double-array x1000" demo.core/average bench-doubles 1000)
    (run-bench-on "average-fast double-array x1000" average-fast-prototype-4 bench-doubles 1000)

• Waited for background terminal · clojure

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• The primitive-array path is clearly faster in the REPL: about 1202 ms for the existing average versus 74 ms for the prototype over 1000 runs of a 100k-element double-array. I’m adding that as average-fast, with a documented double-returning contract and a normal collection fallback.
• Edited src/demo/core.clj (+18 -0)
     6
     7 +(def ^:private double-array-class (class (double-array 0)))
     8 +
     9 +(defn average-fast
    10 +  "Returns a double average. Optimized for primitive double arrays."
    11 +  [xs]
    12 +  (if (instance? double-array-class xs)
    13 +    (let [^doubles a xs
    14 +          n (alength a)]
    15 +      (if (zero? n)
    16 +        (throw (ArithmeticException. "Divide by zero"))
    17 +        (/ (areduce a i sum 0.0 (+ sum (aget a i)))
    18 +           n)))
    19 +    (let [n (count xs)]
    20 +      (if (zero? n)
    21 +        (throw (ArithmeticException. "Divide by zero"))
    22 +        (/ (double (reduce + xs))
    23 +           n)))))
    24 +
    25  (defn median [xs]

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• average-fast is written. I’m reloading the namespace and checking the saved var, behavior on collections and arrays, empty input, then running the benchmark again against the saved function.

↳ Interacted with background terminal · clojure
  └ (set! *warn-on-reflection* true)
    (require 'demo.core :reload)
    (ns-publics 'demo.core)
    (resolve 'demo.core/average-fast)
    [(demo.core/average-fast [1 2 3])
     (demo.core/average-fast [1 2])
     (demo.core/average-fast (double-array [1 2 3]))
     (demo.core/average [1 2 3])]
    [(try (demo.core/average-fast []) (catch ArithmeticException e (.getMessage e)))
     (try (demo.core/average-fast (double-array 0)) (catch ArithmeticException e (.getMessage e)))]
    (dotimes [_ 20] (demo.core/average bench-doubles) (demo.core/average-fast bench-doubles))
    (run-bench-on "saved average double-array x1000" demo.core/average bench-doubles 1000)
    (run-bench-on "saved average-fast double-array x1000" demo.core/average-fast bench-doubles 1000)

• Waited for background terminal · clojure

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• The saved function reloads cleanly with reflection warnings enabled, and the benchmark still shows the optimized path returning the same result with roughly a 15x improvement for double-array input. I’m closing the REPL now.

↳ Interacted with background terminal · clojure
  └ (System/exit 0)

• Ran clojure
  └ Clojure 1.12.4
    user=> (require 'demo.core :reload)
    … +148 lines (ctrl + t to view transcript)
    49999.5
    user=> (System/exit 0)

─────────────────────────────────────────────────────────────────────────────────────────────────────────

• Added average-fast in src/demo/core.clj:7. It returns a double, uses an optimized areduce path for primitive double-array input, and falls back for normal collections.

  REPL verification after reload:

  - (demo.core/average-fast [1 2 3]) -> 2.0
  - (demo.core/average-fast [1 2]) -> 1.5
  - (demo.core/average-fast (double-array [1 2 3])) -> 2.0
  - empty inputs throw ArithmeticException

  Benchmark in the REPL on a 100,000-element double-array, 1000 runs:

  - average: 1182.602574 msecs
  - average-fast: 75.270898 msecs

  That is about 15.7x faster for the optimized primitive-array case.
```

Fasterバージョンを作って、REPLで評価しています。評価関数 `run-bench-on` を作成してメモリ上で使っていますね。最初に「関数が存在すると思うなよ？！」が効いているようです。

今ので、**USD 0.45** くらい消費されていました。

## 7. 感想

使い心地はClaude Codeと変わらないのですね。  
書いてきたコードもClaude Codeのときに感じる「冗長だわ・・・」という気持ちと変わらない。  
もっとガンガンコードを書かせるProjectをしないとわからないですね。

ただ、

* Codex Proは16,800円/月
* Claude Max 20x が USD 200.00/月 (31,879円,2026/05/31現在)

倍だよねー。

## 最後に掃除

先程作った API KEY を Web から操作して削除しました。これで思わぬ課金も無いハズ。
