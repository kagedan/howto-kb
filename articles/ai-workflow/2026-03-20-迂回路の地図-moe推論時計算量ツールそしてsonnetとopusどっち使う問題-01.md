---
id: "2026-03-20-迂回路の地図-moe推論時計算量ツールそしてsonnetとopusどっち使う問題-01"
title: "迂回路の地図 — MoE、推論時計算量、ツール、そして「SonnetとOpusどっち使う？」問題"
url: "https://qiita.com/sugo_mzk/items/dcbd4196c7b21cb1148a"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-03-20"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

# 迂回路の地図 — MoE、推論時計算量、ツール、そして「SonnetとOpusどっち使う？」問題

## はじめに

[Part 1](/transformer-ceiling-part1) では事前学習スケーリングの燃料切れとデータ枯渇を、[Part 2](/transformer-ceiling-part2) ではTransformerの理論的限界と「考えているフリ」問題を見ました。

状況をまとめると：モデルをデカくしても改善しにくくなった。データも尽きかけている。アーキテクチャ自体に数学的な壁がある。CoTは推論モデルにはほぼ無意味で、思考トレースは75%不誠実。

でもAIの進歩は止まっていない。FrontierMathは16ヶ月で2%から50%になった。ARC-AGI-2で84.6%が出ている。何が起きているのか。

答えは：**業界はコアモデルを賢くするのを諦めて、周辺技術で迂回している**。この記事では、その迂回路の中身と、実務で使う側が知っておくべきことを整理します。

---

## 迂回路 1: MoE — 計算しないパラメータを大量に持つ

Mixture
