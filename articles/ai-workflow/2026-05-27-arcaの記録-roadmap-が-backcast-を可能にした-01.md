---
id: "2026-05-27-arcaの記録-roadmap-が-backcast-を可能にした-01"
title: "Arcaの記録: ROADMAP が backcast を可能にした"
url: "https://zenn.dev/sisiodos/articles/5bb97e95ace33b"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

# Arcaの記録: ROADMAP が backcast を可能にした

Arca の初期段階では、role separation や review loop、handoff、PR-based operation など、比較的明示的な workflow を整備していました。

といった、比較的明示的な実行フローを整備していた時期です。

しかし、2026/04/19 に `GOAL.md` と `ROADMAP.md` を導入したことで、Arca の性質は少し変わり始めます。

当時はまだグラフ構造は導入していませんでした。exploratory graph, planning graph もありません。

ただ、markdown を2つ置いて実験していただけでした。

しかし今振り返ると、この時点から Arca は少しずつ「workflow system」ではなくなっていったように思います。

---

## 最初に導入したのは `GOAL.md` だった

理由は単純で、

> 「agent に現在の方向性を持たせたい」

と思ったからです。

workflow や task だけでは、agent が局所的な作業へ閉じやすかった。

そこで、何を目指しているのか、どういう状態へ向かいたいのか、を repository に明示しようと考えました。

もちろん、これらは git log や issue, PR を積み重ねれば復元できる情報ではあります。

しかし実際には、人間も agent も、毎回その履歴全体を辿るわけではありません。

そこで `GOAL.md` は、「現在どこへ向かっているのか」を即座に共有するための cache state のような役割を持ち始めました。

repository 全体に埋もれている方向性を、人間と agent がすぐ読める形で materialize していたのです。

---

## しかし GOAL が近すぎた

ところが、実際に運用してみると別の問題が起きます。

agent は GOAL に非常に強く引っ張られます。

そのため、方向性が安定する一方で、GOAL 自体が直近の optimization target になっていきました。

つまり、短期的な convergence や local optimization が起きやすくなり、どうしても近い未来へ閉じやすくなっていたのです。

---

## そこで `ROADMAP.md` を導入した

ここでやりたかったことは、大きく2つありました。

1つは、もう少し遠い future direction を書くことです。将来的にどう変化しそうか、どんな構造が必要になりそうか、どんな段階が現れそうかを、やや speculative に書き始めました。

もう1つは、stage backcast です。次にどの状態を達成すべきか、どの段階を超える必要があるか、現在どの maturity boundary にいるのかを整理し、future state から現在地点を逆算するためのものでもありました。

---

## Backcast が始まる

この頃から、agent に対して少し変わった使い方を始めます。

単に TODO を分解させるのではなく、まず future state を置き、その状態へ到達するためにどのような stage が必要そうかを考えさせるようになりました。

興味深かったのは、この頃から task 自体を書く頻度がかなり減っていったことです。

当初は Codex CLI に task decomposition を支援させていました。しかし roadmap を導入して以降は、細かな task 分割すらあまり行わなくなっていきました。

agent が roadmap と現在地点を見ながら、自律的に次の stage や必要そうな作業を推測するようになっていったからです。

---

## まだ Graph は存在していない

現在の Arca には exploratory graph や visible cognition、planning traceability のような概念があります。

しかし、2026/04/19 時点では、まだそうしたものは存在していませんでした。

本当にやっていたことは単純で、repository に `GOAL.md` と `ROADMAP.md` を置き、agent に読ませていただけです。

---

## しかし exploration の性質が変わった

ただ、それだけでも agent の振る舞いはかなり変わりました。

task を実行するだけではなく、roadmap を読み、将来方向を推測し、現在位置を解釈しながら作業するようになっていきます。

また、どの stage にいるのか、どの構造が不足しているのか、といった視点も現れ始めました。

---

## Workflow の外側

そして、この頃から別の問題も見え始めます。

workflow 自体は機能していました。しかし、本当に重要な reasoning は task の外側に存在していたのです。

なぜその方向へ向かったのか、なぜ別案を捨てたのか、といった情報は task state にうまく収まりませんでした。

つまり、workflow は execution を扱うことはできても、exploration を扱うには少し窮屈だったのです。

この経験を経て、私は task と exploration を分離する方が良いと考えるようになりました。

---

## 後から見ると、ここが始まりだった

現在の Arca は、初期の workflow harness からかなり変化しています。

しかし、その変化の始点は意外と単純でした。

2026/04/19 に、repository に `GOAL.md` と `ROADMAP.md` を置いた。ただそれだけです。

最初は「少し遠い方向を書いておく」程度の感覚でした。しかし今振り返ると、この時点から Arca には future-state reasoning や backcasting、exploratory planning のような性質が入り始めていたのだと思います。

そして、おそらくここから、後の exploratory graph や visible cognition の方向へ繋がっていったのだと考えています。
