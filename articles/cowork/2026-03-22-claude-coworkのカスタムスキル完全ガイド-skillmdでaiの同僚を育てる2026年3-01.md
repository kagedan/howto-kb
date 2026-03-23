---
id: "2026-03-22-claude-coworkのカスタムスキル完全ガイド-skillmdでaiの同僚を育てる2026年3-01"
title: "Claude Coworkのカスタムスキル完全ガイド — SKILL.mdで「AIの同僚」を育てる【2026年3月最新】"
url: "https://qiita.com/AI-SKILL-LAB/items/04f8dfa158526e836271"
source: "qiita"
category: "cowork"
tags: ["API", "GPT", "cowork", "qiita"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

# Meta Llama 4 Scout/Maverick 実践ガイド — MoEアーキテクチャの仕組みとOllama/API活用のすべて【2026年3月最新】

2026年3月中旬、Metaが「Llama 4」ファミリーをリリースしました。

発表を見て、最初に思ったのは「10Mトークンのコンテキスト」という数字でした。GPT-4oの128Kの約78倍。ちょっと桁が違いすぎて、現実感がわかないくらいです。でも、ちゃんと調べていくと、「すごいけど、そのすごさはどこにあるのか」が見えてきて、むしろ使い方の解像度が上がりました。

この記事では、Llama 4の技術的な仕組みから、実際に手元で動かすまでの具体的な手順を整理しています。「発表は知ってるけど、実際どう使えばいいのか分からない」という方に特に役立てていただけると思います。

## 目次

1. Llama 4が変えたこと — MoEアーキテクチャという設計思想
2. Scout vs Maverick — どちらを選ぶか
3. ハードウェア要件の実態 — 「17Bアクティブ」の罠
4. Ollamaでローカル実行する — 最速セ
