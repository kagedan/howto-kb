---
id: "2026-05-29-ren-aivest-httpstco3wcnpbuhzt-01"
title: "@ren_aivest: https://t.co/3WcnpbUHzT"
url: "https://x.com/ren_aivest/status/2060180177918062994"
source: "x"
category: "claude-code"
tags: ["claude-code", "x"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/3WcnpbUHzT


--- Article ---
# 合計21エージェントが同時起動して12分で終わった

Claude Codeのworkflow機能がやばい、、、
**Opus 4.8時代の1番やばいアップデートかも**
解説します。

![](https://pbs.twimg.com/media/HJcnB3ibIAAzJUS.jpg)

## 「3ヶ月かけて計画するような大仕事が数日で完了する」という主張

## 実例の裏付け

誇張ではない証拠として、、、

JarredSumner氏がBunをZigからRustへ移植し、既存テストの99.8%が通過、約75万行のRust、初コミットからマージまで11日という事例が出ています。

75万行・11日というのは、従来なら確かに数ヶ月かかる規模です。

Anthropic公式に掲載あり

## 何が起きたか

![](https://pbs.twimg.com/media/HJcnPnKbsAAu-9-.png)

サイバーエージェントでも実際に活用した事例と内容が記載されていました。

「Dynamic workflowsは、**サブエージェントを1つ単発で投げる**のと、**本格的なエージェントチームを丸ごと構築する**との間にある"ギャップ"を埋めてくれる。

計画から実装までがそのまま流れるように進むので、可視性（何が起きているかの見通し）を失わずに、長時間の実行を安心して任せられる。」

ポイントを補足すると、

**「2つの極の間を埋める」という評価**これまでClaude Codeで複雑な作業をしようとすると、選択肢が両極端。

片方は「サブエージェント1個に単発でタスクを投げる」手軽だけど大規模作業には非力な方法。

もう片方は「複数エージェントを自分で組織化してチームを構築する」強力だけど設計・管理が重い方法。

Dynamic workflowsはその中間を埋め、軽い設定で大規模並列処理の恩恵を受けられる、という意味。

**「visibility（可視性）を失わない」が肝**長時間・大量エージェントの実行で一番怖いのは「中で何が起きているか分からないまま暴走する」こと。

記事の仕組み説明にもあったように、結果は折り込む前に検証され、進捗も随時保存されるので、だからこそ「longer runs（長時間の実行）を信頼できる」と評価している。

任せきりにしても見通しが効く、という安心感を指している

## 競合アプリのUIパターン調査、2026年最新デザイントレンド、テック系UI動向。
このリサーチを投げたところこうなった。

**Opus 4.7が同時に8体起動。その後さらに12体を追加起動し、最終的に1体に収束してメインセッションに戻ってきた**

Claude Codeに新しく追加された「Dynamic Workflows」機能。 workflowと入力するだけで発動する。

![](https://pbs.twimg.com/media/HJclTptacAAmDz5.jpg)

![](https://pbs.twimg.com/media/HJdJQbTa8AAsNz1.jpg)

合計21エージェント。
938kトークン消費。
所要時間12.6分。

アウトプットは**187k文字**。
構造を切り出してspecとして保存された。

## これまでとの違い

これまでのClaude Codeでも並列サブエージェントは動いていた。
ただし同時起動はせいぜい4〜7体程度。

それが今回は同時にかつ、多段階的に動く。
しかも1体1体がOpus 4.7。

もはやニューラルネットワークのような構造だが、、、
ノードの一つ一つがOpus 4.7もあるいうことが恐ろしい。

そしてすべてが収束してメインセッションに戻ってきたとき迎えるのはOpus 4.8。

**この安心感がworkflowの本質かもしれない**

## もう1つの実行結果

![](https://pbs.twimg.com/media/HJcl1G8bcAA00Hk.png)

別のワークフローも走らせた。

・5段階のフェーズ構成
・合計16エージェント起動
・768kトークン消費
・所要時間22分25秒

数百万トークン規模のリサーチが20分前後で完了する世界。

![](https://pbs.twimg.com/media/HJclfY1bUAAFXTT.jpg)

![](https://pbs.twimg.com/media/HJdJdtIacAE0GRb.jpg)

![](https://pbs.twimg.com/media/H
