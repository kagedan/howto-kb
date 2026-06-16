---
id: "2026-06-15-恐怖のclaude-dynamic-flowsでサブエージェントがすべてfable-5で立ち上がった-01"
title: "恐怖のClaude ～Dynamic FlowsでサブエージェントがすべてFable 5で立ち上がったら"
url: "https://zenn.dev/mdtechknowledge/articles/dynamic-workflows-fable5-runaway"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "zenn"]
date_published: "2026-06-15"
date_collected: "2026-06-16"
summary_by: "auto-rss"
query: ""
---

9.8時間の動画を解析させようと、Claude Code の **Dynamic Workflows** を起動した。メインモデルは、公開されたばかりの最上位クラス **Claude Fable 5**。

「36個のサブエージェントで並列に読ませれば速い」——そう思った、次の瞬間だった。

## その画面

![Dynamic Workflows の進捗画面。36個のサブエージェントがすべて Fable 5 で起動している](https://res.cloudinary.com/zenn/image/fetch/s--YJsZadBR--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://quintessence-lab.github.io/mdTechKnowledge/images/cwc-tokyo-fable5-subagents-swarm.png?_a=BACMTiAE)

36個のサブエージェント。その **すべての行に「Fable 5」**。

最上位モデルが36体、一斉に画像読み取りという重い処理を始めていた。画面には `failed: API Error ... (ECONNRESET)`、`idle`、そして延々と続く `queued` の文字。トークンは猛烈な勢いで溶け、**ほどなくしてセッションの利用上限に到達**。作業は強制的に止まった。

ずらりと並んだ「Fable 5」の列は、なかなかに"恐ろしい"光景だった。

## なぜこうなるのか

Dynamic Workflows のサブエージェントは、**明示的にモデルを指定しない限り、メインループのモデルを引き継ぐ**。

つまり、メインを Fable 5 にしていれば——子エージェントも、全員 Fable 5。

Fable 5 は最上位クラス＝高価なモデルだ。それが数十体、同時に動けば、コストも消費トークンも一気に跳ね上がる。上限到達は時間の問題だった。

## 回避策：サブエージェントのモデルを明示指定する

対策はシンプルで、**サブエージェントのモデルを明示的に指定する**だけ。

```
// Dynamic Workflows の agent() でモデルを明示
agent(prompt, { model: 'sonnet' })
```

視覚読み取り・転記・分類のような **大量かつ機械的な並列処理** は、Sonnet で十分なことが多い。一段下のモデルに逃がすだけで、コストと上限の両面で安全になる。実際、この動画解析も読み取りを **Sonnet** で再実行したところ、問題なく完走した。

## 教訓

* **メインを Fable 5 にしているときの Dynamic Workflows は要注意。** 子は黙っていると全員 Fable 5 になる。
* 起動前に「**子は何のモデルで動くのか**」を必ず確認する。
* **大量ファンアウトはモデルを一段下げる。** 速さの代わりに上限とコストを失っては本末転倒。

最強のモデルを、最強のまま36体並べると——速さの前に、財布とレート上限が悲鳴をあげる。便利な道具ほど、"何が走るのか"を握っておきたい。

---

> この一幕は、約9.8時間のアーカイブをスライド書き起こしした際の制作裏話です。完成物はこちら: [Code with Claude Tokyo 2026 全セッションまとめ](https://note.com/mdtechknowledge/n/nf921803c2112)
>
> 関連: [Claude Code Dynamic Workflows ガイド](https://note.com/mdtechknowledge/n/ndacb07ee23fa) ／ [Claude Fable 5 徹底解剖①概要編](https://note.com/mdtechknowledge/n/n5fdb0e2f02ad)

---
