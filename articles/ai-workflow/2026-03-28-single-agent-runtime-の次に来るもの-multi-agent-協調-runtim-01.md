---
id: "2026-03-28-single-agent-runtime-の次に来るもの-multi-agent-協調-runtim-01"
title: "single-agent runtime の次に来るもの: multi-agent 協調 runtime をどう考えるか"
url: "https://zenn.dev/nhigashi/articles/4f1f8790745bd8"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "zenn"]
date_published: "2026-03-28"
date_collected: "2026-03-29"
summary_by: "auto-rss"
---

LLM agent の実行基盤を作っていると、ある時点で気づくことがあります。

単一の runtime を賢くする問題と、複数の agent/runtime を協調させる問題は、かなり別物だということです。

ここしばらく見ていたのは、1 回の実行をどう成立させるか、という種類の問題でした。  
具体的には、必要な context を与え、tool を呼び、結果を返す、という流れをどううまく作るかです。

そこから見えてきたのは、単一 runtime の設計と multi-agent 協調の設計は、連続しているようでいて実は別レイヤーだ、ということでした。

そして multi-agent 協調を考えるときに必要なのは、単なる subagent 呼び出しではなく、

* durable な **context**
* reactive な **event / trigger**
* 誰をいつ起こすかを決める **scheduler**
* 1 回の実行を担う **runtime**

という分離だと考えています。

なお、この記事の背景にある実装や設計メモは GitHub で公開しています。

<https://github.com/nhigashi29/termy>

この記事自体は一般化して書いていますが、実際にはその試行錯誤の中で見えてきた整理です。

---

## 単一 runtime はかなり解けている

まず前提として、単一 agent の runtime はかなり強くなっている。

たとえば Pi 的な runtime を考えると、基本はこうです。

<https://github.com/badlogic/pi-mono>

1. task を受ける
2. 必要な context を読む
3. tool を叩く
4. 結果を返す

これはかなり強力です。  
要するに **「Single Agent 実行」** の問題としては、すでに多くのことができる段階に来ています。

もちろんプロンプトや tool-call の設計、memory の扱い、projection の工夫にはまだ検討の余地があります。  
ただ、それでも問題の中心は比較的はっきりしています。

* 何を見せるか
* どう推論させるか
* どう tool を呼ばせるか
* どう結果を返すか

ここでは runtime は、かなり self-contained に扱えます。

---

## 難しいのは multi-agent 協調

問題はその先です。

複数の agent がいると、単に runtime を増やせば終わりではない。  
必要になるのはむしろ **runtime 間の交通整理** です。

たとえばこんな問いが出てくる。

* いつ誰を起こすのか
* 何を渡すのか
* 誰が ownership を持つのか
* 終了条件は何か
* 途中結果をどう共有するのか
* notify は hint なのか obligation なのか
* 途中で止まったものをどう再開するのか

これはもう「賢い 1 回の実行」の問題ではなく、**協調 runtime** の問題になります。

---

## AutoGen 的な teams への違和感

AutoGen の `teams` のような仕組みはとても参考になります。  
ただ、使いながら感じるのは、あれは本質的には **会話 orchestration** だということです。

* 共通の会話履歴がある
* 次に誰が話すかを selector が決める
* termination condition で止める

これは便利ですし、デモや探索にはとても向いています。

ただ、私が欲しかったものは少し違っていました。  
欲しかったのは、agent 同士が自然言語で会話する仕組みというより、

* task が durable に記録される
* task の進行が observable である
* 誰が今 busy か分かる
* ある event に反応して runtime が起動する
* 必要なら time-driven / dependency-driven にも拡張できる

という、もっと systems-oriented な協調基盤でした。

---

## context と event は両方必要

ここで大事なのが、**context と event は別物ですが両方必要** だということです。

### context

context は、永続化される事実・状態・履歴です。

たとえば:

* task が作られた
* task が進行中になった
* result が出た
* review request が作られた
* agent が running / idle になった

こういうものは、後から参照できる source of truth として残したい。

### event / trigger

event は、「何かが変わったので runtime を起こせる / 起こすべき」という signal です。

たとえば:

* task created
* task completed
* dependency resolved
* timeout reached
* human reply received

context だけだと durable ですが reactive になれません。  
event だけだと reactive ですが履歴や説明可能性が弱くなります。

だから必要なのは、

* **task / context が主**
* **event / trigger は起動条件**
* **runtime は実行器**

という整理が適切だと考えています。

---

## spawn と run は分けるべき

multi-agent を考え始めると、`spawn` をどう考えるかが重要になります。

よくあるモデルはこうです。

1. main agent が subagent を spawn する
2. その場で run する
3. 結果を返す

これは分かりやすいのですが、協調系ではすぐ窮屈になります。

私は今、spawn を **「新しい責務単位・作業単位・文脈単位を生成すること」** と考える方が良いと思っています。

たとえば:

* task context を作る
* review request を作る
* meeting thread を作る
* dependency を記録する

この時点では、まだ runtime は起動しなくてもかまいません。  
大事なのは、

* 誰が owner か
* どういう input があるか
* 何が completion condition か
* visibility はどうなっているか

が durable に記録されることです。

その後で trigger が来て、scheduler が run を決めます。

つまり:

1. **Spawn / Context creation**
2. **Trigger**
3. **Run**

の 3 段階に分ける。

これはかなり大きな整理でした。

---

## 「誰が起こすか」から自由になる

この整理の良いところは、run の起点を main agent に固定しなくてよくなることです。

起動は少なくとも次の 4 種類があってよいと考えています。

1. **human-originated**
2. **agent-originated**
3. **system-originated**
   * retry, timeout, cron, scheduler の判断
4. **world-originated**
   * webhook, file change, inbox 更新

これらを全部同じ trigger abstraction に落とせると、かなりきれいになります。

---

## notification は万能ではない

設計していてかなり大事だと感じたのが、**notification を一枚岩にしないこと** でした。

「通知」を 1 種類の万能概念として持つと、すぐに曖昧になります。  
少なくとも次のように分けた方がよいと思います。

### 1. hint

「見た方がいいかも」  
起動するかどうかは scheduler が決めます。

### 2. request

「これを処理してほしい」  
ownership 候補が発生します。

### 3. assignment / obligation

「あなたが担当」  
明示的な lifecycle を持ちます。

この区別をしないと、

* 単なる signal
* 実際の work unit
* ownership を伴う責務

が混ざって壊れやすくなります。

だから私は、**task を主役にして、notification は実行を起こす trigger として扱う** のが安定すると感じています。

---

## agent は常時考え続ける存在ではない

multi-agent を考えるとき、agent を「ずっと裏で考え続ける知性」と見ると設計が散らかりやすくなります。

むしろ agent は、

> **条件が満たされたら起動される stateful worker**

として扱う方がよいと感じています。

起動条件は最低でもこの 4 類型を考えたい。

1. **event-driven**
   * 新しい task / result / message が来た
2. **time-driven**
   * deadline, retry, debounce, periodic check
3. **dependency-driven**
4. **human-driven**

こうすると「途中で runtime を起こす」「止まっているものを再開する」という問題が自然に見えてきます。

---

## 自分の今の設計: Observable Store と Agent Lifecycle

ここで考えているのは、次のような方向です。

### 1. Agent lifecycle を context として記録する

たとえば:

* `AgentStatus { status: "running", taskId, threadId }`
* `AgentStatus { status: "idle" }`

を append-only に記録します。

これにより:

* manager が worker の状態を見られる
* busy な agent を避ける routing ができる
* journal に lifecycle が残る
* 後から replay / trace ができる

### 2. ContextStore を observable にする

`store.append(task)` したら、それを `subscribe` で検知できるようにします。

```
interface ContextStore {
  subscribe(listener: (context: AnyContext) => void): () => void;
}
```

### 3. ExecutionEngine を reactive scheduler にする

これまで `tick()` を外から呼んでいましたが、それをやめます。

```
store.append(task)
  -> subscribe が発火
  -> ExecutionEngine が enqueue
  -> agent を dispatch
```

この形にすると、task を作る側は scheduler を意識しなくてよくなります。

* 書き込み = 事実の記録
* dispatch = engine の責務

という分離に戻せます。

### 4. `waitForTask(taskId)` で同期的な待機を支える

CLI や tool の一部は同期的に結果を待ちたい場面があります。  
そのため、engine 側に `waitForTask(taskId)` を持たせます。

これで上位は

だけを知っていればよくなります。

---

## 重要なのは single-agent runtime と coordination runtime の分離

ここまで考えて、私の中でかなりはっきりしてきたことがあります。

それは、

* **single-agent runtime**
* **multi-agent coordination runtime**

は分けて設計した方がよい、ということです。

### single-agent runtime

責務は比較的シンプルです。

* context を受ける
* projection する
* model を回す
* tool を叩く
* output を返す

### coordination runtime

こちらはもっと OS / scheduler に近いものです。

* task / result / lifecycle を durable に持つ
* event を受ける
* dispatch 条件を判定する
* ownership を管理する
* retry / timeout / debounce を扱う
* pause / resume を支える

---

## 今ほしい core abstraction

今のところ、最小の coordination runtime に必要なのはこのあたりだと考えています。

### Context record

永続化される事実です。

* task created
* task assigned
* task blocked
* result submitted
* agent running / idle

### Event / Trigger

状態変化や時刻条件から発生する signal です。

* on task\_created
* on dependency\_resolved
* on timer\_elapsed
* on human\_reply\_received

### Task

ownership を伴う work unit です。

### Subscription / Trigger rule

どの event でどの agent を起こすかを表すものです。

### Scheduler

起こすか、後回しにするか、まとめるかを決めるものです。

### Run

Pi 上で走る 1 回の execution です。

### Wake / Resume token

途中停止中のものを再開するための識別子です。

この切り方だと、かなり全体が安定します。

---

## 「everything is context」だけでは足りない

context は source of truth として中心に置くべきです。  
ただし coordination を動かすには、そこに

* trigger
* scheduling policy
* activation / resume

が必要になります。

だから優先順位としては、

1. **task / context が主**
2. **event / notify は起動トリガー**
3. **runtime は実行器**

この順番が安定すると考えています。

---

## まとめ

* 単一 agent runtime はかなり解けている
* 難しいのは複数 runtime の協調である
* 協調の本体は chat ではなく、context / event / scheduling にある
* spawn は「今すぐ実行」ではなく「責務・文脈の生成」と考えるべき
* task が本体で、notification は trigger として扱うのが安定する

<https://github.com/nhigashi29/termy>
