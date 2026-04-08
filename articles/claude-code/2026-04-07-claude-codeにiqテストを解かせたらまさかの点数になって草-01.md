---
id: "2026-04-07-claude-codeにiqテストを解かせたらまさかの点数になって草-01"
title: "Claude CodeにIQテストを解かせたらまさかの点数になって草"
url: "https://qiita.com/brain_test_dev/items/717458379e4564013c49"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

自分はIQテストを個人開発している。全30問、数値推理・空間認識・論理推理・言語理解の4分野で測定するやつ。

で、ある日思った。**「Claude Codeに解かせたら何点取るんだろう」**

最近Claude Codeを開発で使いまくっていて、こいつの推論力はマジでヤバいと実感している。コード生成、デバッグ、設計判断、だいたいのことは人間より速い。

じゃあIQテストも余裕で満点なんじゃないか？ 試してみた。

https://picoli.site/q-iq-0005a

## 実験方法

IQテストの全30問をClaude Code（Claude Opus 4）に解かせた。

やり方はシンプル。各問題のスクリーンショットを撮って、Claude Codeに画像として渡し、「この問題の答えを選んでください」と聞くだけ。

ルールは以下。

- 1問ずつ画像で渡す（一括ではなく逐次）
- 「IQテストの問題です。選択肢の中から正解を1つ選んでください」とだけ指示
- 追加のヒントなし
- 考え方の説明も求めない（答えだけ）
- 制限時間なし（人間は1問60秒だが、AIには制限なし）
