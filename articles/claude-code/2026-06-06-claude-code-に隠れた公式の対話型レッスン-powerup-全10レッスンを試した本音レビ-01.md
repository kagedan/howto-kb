---
id: "2026-06-06-claude-code-に隠れた公式の対話型レッスン-powerup-全10レッスンを試した本音レビ-01"
title: "Claude Code に隠れた公式の対話型レッスン /powerup ── 全10レッスンを試した本音レビュー"
url: "https://zenn.dev/gudezou/articles/d5c136ba2b52dc"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-06-06"
date_collected: "2026-06-07"
summary_by: "auto-rss"
query: ""
---

![サムネイル](https://static.zenn.studio/user-upload/01f3c2274d0a-20260606.png)

* Claude Code には `/powerup` という公式の対話型レッスンがあるのに、初回起動時の案内が無く、ほとんどの人が存在に気付いていません
* Claude Code 2.1.90 で追加された機能で、2.1.165時点のレッスンは10個、全部やっても体感10~15分で終わります
* 10個を均等に学ぶ必要はなく、初心者がまず知るべきものと、後回しでいいものが混ざっている印象を受けました

---

## 公式の対話型レッスン /powerup に、ほとんどの人が気付いていない

Claude Code には `/powerup` という公式の対話型レッスンがあります。  
アニメーション付きの短い対話レッスンで機能を学べる仕組みで、公式の Claude Code Docs > Commands ページにもそう書かれています。  
追加されたのは Claude Code 2.1.90 です。  
その記録は anthropics/claude-code リポジトリの `CHANGELOG.md` に残っています。

ところが初回起動時に `/powerup` の案内は出ません。  
その存在を知るには、自分で / メニューを開いてコマンドを眺めるか、ドキュメントを読んで偶然見かけるしかないのが実状です。  
その証拠に、追加の翌日には anthropics/claude-code リポジトリに Issue #42305 が立ちました。  
『ドキュメントに `/powerup` の説明が無い』という指摘です。  
長く使っている人でも気付いていないことが多く、私の周りでも自分から探して見つけたよという人はいません。  
良い学習の入り口なのに、見つけてもらうための導線がほとんど用意されていない、というのが正直な印象です。

![/ メニューに並ぶコマンドの中に /powerup が埋もれている様子](https://static.zenn.studio/user-upload/c9819154ddc3-20260606.png)

---

## 全10レッスンを試してわかった「これだけやれ」

私が試した Claude Code 2.1.165 では、レッスンは全部で10個でした。  
ネット上の記事には18個と書くものもありますが、版によって数が違うようで、私が使っているバージョンでは10個です。  
じっくり読んでも10~15分、読み飛ばせば5分ほどで終わります。

10個のうち、初心者がまず知っておきたいのは次の5個です。

* Talk to your codebase
  + @ でファイルや行を指す方法で、メンション機能なので必須操作です。
* Steer with modes
  + shift+tab でモード切り替えができます。
  + 頻繁に使うので必須操作です。
* Undo anything
  + `/rewind` と Esc-Esc での実行取り消しについて。
  + 特に Esc-Esc を知っておけば何かあった時にすぐに中止できます。
* Teach Claude your rules
  + `CLAUDE.md` とは何かを教えてくれます。
  + 書き方や構成に関する最低限の作法を知れます。
* Dial the model
  + `/model` と `/effort` の切り替えについて。
  + model と effort 費用対効果に直結するので知っておくべき内容です。

残りは、初心者のうちは後回しで大丈夫です。

* Run in the background
* Code from anywhere
  + リモート操作について。
  + こちらも中級者向けの話です。
* Extend with tools
* Multiply yourself
  + サブエージェントについて。
  + Claude Code 自体もよくわからないのに深入りし過ぎな印象。
* Automate your workflow
  + スキルとフックについて。
  + スキルは理解しておくと効率が段違いに良くなりますが、フックまで急いで理解する必要はない印象。

![各レッスンで何を学べるかと、まず知っておきたい/後回しでいいの優先度をまとめた早見表](https://static.zenn.studio/user-upload/525184355275-20260606.png)

`/powerup` を実際にやってみて感じたのは、どれも Claude Code を使いながら覚えていく内容だということです。  
最初に通しでレッスンをやったとしても、覚えていられるかどうかは正直あやしいです。  
知っておいて損は無い、くらいの軽い気持ちで、頭の片隅に置いとければいいや程度に眺めるのがちょうどいいと思います。

---

## 参考文献

1. Anthropic. *Commands - Claude Docs*. Claude Code Documentation. <https://code.claude.com/docs/en/commands>
2. anthropics/claude-code. *claude-code/CHANGELOG.md at v2.1.90 · anthropics/claude-code*. GitHub. <https://github.com/anthropics/claude-code/blob/v2.1.90/CHANGELOG.md>
3. anthropics/claude-code. *[DOCS] /powerup slash command missing documentation · Issue #42305 · anthropics/claude-code*. GitHub. <https://github.com/anthropics/claude-code/issues/42305>
