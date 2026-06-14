---
id: "2026-06-13-ai-depression-fable-5を触ってからopus-48の使い方まで変わった-モデル性能-01"
title: "@ai_depression: Fable 5を触ってから、Opus 4.8の使い方まで変わった。 モデル性能が上がったというより、自分の指示精度が上"
url: "https://x.com/ai_depression/status/2065627944945606798"
source: "x"
category: "ai-workflow"
tags: ["x"]
date_published: "2026-06-13"
date_collected: "2026-06-14"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

Fable 5を触ってから、Opus 4.8の使い方まで変わった。

モデル性能が上がったというより、自分の指示精度が上がっている状態だけど、これ、けっこう大きいな

以前は開発系の作業をAIに投げるときも、なんとなく「この機能作って」「このエラー直して」「この処理をいい感じに整理して」みたいな渡し方をしていたんですが、それだとAI側からすると情報が足りない。

どこまで作るのか。
既存コードのどこを触っていいのか。
入力と出力は何か。
失敗時はどう振る舞うのか。
テストはどこまで見るのか。
人間が最後に確認すべき観点は何か。

この辺が曖昧なままだと、AIは動きはするけど安定しない何かを作るけど、実務で使うにはまあまあ惜しい。あと一歩でツールなのに。

Fableを触って一番変わったのは、ここでしたね

「AIに作業を任せる」ではなく、作業を小さな責任単位に分けて、エージェントに渡せる形に整える感覚が身についた。

たとえば、いきなり「投稿生成ツールを作って」と渡すんじゃなくて、

◽️入力は元ネタ文章
◽️出力は切り口候補、フック、本文
◽️最初は本文を書かず切り口だけ出す
◽️ユーザーが番号を選んだら本文に進む
◽️文体は既存ガイドを最優先にする
◽️失敗パターンは、説明文っぽくなることと、抽象論で終わること
◽️レビュー時は、冒頭の強さ、具体例、語尾の単調さを見る

みたいに渡す。
コンテキスト→ワークフロー→ハーネス

ここまで分けると、Fableほどではないにしても、Opus 4.8でもかなり使えるものが出るようになった

つまり、性能差をモデルの中だけで見ていたけど、実際は「人間側のタスク設計」がボトルネックだっただけで高いモデルを触る価値は、出力の強さだけじゃないってこと

良いモデルに触ることで、雑な指示がどれだけ雑だったかが見える。
作業の分け方、前提の渡し方、レビュー観点の置き方が変わる。
その結果、普段使いのモデルに戻しても成果物の品質が底上げされる。

ゲームでいうと、最強装備を一回触ったことで、自分の立ち回りの下手さに気づく感じ。

装備を外してもエイムは残る。

だから今の自分の中では、Fable 5は常用するというより、設計レビューと最終確認に使うのがかなり現実的だと思ってます。

普段の実装や叩き台づくりはOpus 4.8で進めて、最後にFable 5で「構造として破綻してないか」「エージェントに任せる粒度として粗くないか」「見落としている例外処理はないか」を見てもらう。

全部を高いモデルで殴らない。

高いモデルで基準値を上げて、普段のモデルで量を回して、最後だけレビューに戻す。

この運用ができると、コストも下がるし、開発周りの速度も精度もかなり上がる。

最先端に早く触る意味って、たぶんここにある。

新しいモデルを知識として追うだけだと「性能上がったんだな」で終わるけど、実際に触ると、自分の仕事の渡し方そのものが更新される。

コンフォートゾーンを抜ける一番確実な方法は、最先端を眺めることじゃなくて、一回触って自分の基準を壊されることだと実感した、これがブレイクスルーってやつか


--- 引用元 @AnthropicAI ---
The US government, citing national security authorities, has issued an export control directive to suspend all access to Fable 5 and Mythos 5 by any foreign national, whether inside or outside the United States, including foreign national Anthropic employees.

The net effect of this order is that we must abruptly disable Fable 5 and Mythos 5 for all our customers to ensure compliance.

Access to all other Claude models is not affected.

We apologize for this disruption to our customers. We believe this is a misunderstanding and are working to restore access as soon as possible.

Read our full statement: https://t.co/bwn0sximKZ
