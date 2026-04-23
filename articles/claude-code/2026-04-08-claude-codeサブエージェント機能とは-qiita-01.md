---
id: "2026-04-08-claude-codeサブエージェント機能とは-qiita-01"
title: "【Claude Code】サブエージェント機能とは - Qiita"
url: "https://qiita.com/pro-tein/items/29b6ac8331f77f3ad1b6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "LLM", "qiita"]
date_published: "2026-04-08"
date_collected: "2026-04-09"
summary_by: "auto-rss"
query: ""
---

# はじめに

今回はClaude Codeをより使いこなすうえで欠かせない、**サブエージェント**機能について簡単にまとめてみました。

# サブエージェントとは

サブエージェントとは、**1つのLLM（メイン）だけで処理せず、内部で複数の小さなエージェントに分割して処理する仕組み**のことです。

* メインエージェントがサブエージェントにタスクを依頼し、サブエージェントがそのタスクを処理する
* 処理後に**必要な情報（結果）のみ**をメインエージェントにわたす
* 主に**並列処理**や**専門分担**（例：実装担当・レビュー担当など）に使われる
* **（重要） 明示的に見える機能ではなく、内部的な実行モデルとして存在する**  
  →使い心地としてはskillsに近いです

### こんなときに使いたい

* タスクが重く、終わる前にコンテキストウィンドウが上限に達してauto-compactが入ってしまう（勝手に必要な情報が捨てられてしまう）
* コードの実装とテストとレビューを同じセッションでやろうとすると、あっという間にコンテキストウィンドウが埋まってしまう
* mcpサーバーたくさん使いたいけど、context負荷重い！

## 使用するメリット

サブエージェントは**メインエージェントから独立した、まっさらのコンテキストを使用することができる**ため、  
・余計な情報が少ない分アウトプットの精度が高くなる  
・メインエージェントのコンテキストを汚さない（コンテキストを節約できる）  
・1回の同じセッション内でタスクを完遂できる  
というメリットがあります。

## エージェントチームとの違い

似たように作業を並列化できる機能として**エージェントチーム**がありますが、サブエージェントとの違いは以下のようになっています。（公式ドキュメントより抜粋）

[![subagents-vs-agent-teams-light.avif](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F794f2a13-8bce-4928-8551-21c072697e6d.avif?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=03352f1ca541203a1d895d9b40b1a7d5)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F794f2a13-8bce-4928-8551-21c072697e6d.avif?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=03352f1ca541203a1d895d9b40b1a7d5)

一番大きな違いは、サブエージェントが結果をメインエージェントに報告するだけで、互いに通信することはないのに対し、エージェントチームでは、チームメンバーがタスクリストを共有し、作業を要求し合い、互いに直接通信します。（まさにチームワーク）

[![SCR-20260331-tozp.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F88cc8dfe-b99a-47e9-bfd4-cad9ff9fe3ce.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c049b8e3627e29c4f77d9eeacfa50627)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F4345180%2F88cc8dfe-b99a-47e9-bfd4-cad9ff9fe3ce.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c049b8e3627e29c4f77d9eeacfa50627)

より詳しくは公式ドキュメントのこちらの章をご参照ください。

# サブエージェントを使ってみた

サブエージェントもskills同様、とても簡単に作成してすぐに使い始められます。  
詳しくはこちらの記事をご参考ください。

# 使用するうえでの注意点

さいごに、サブエージェント機能を使用するうえで注意すべきことがあります。  
それは、**タスクの処理内容が競合しないようにする**ことです。  
複数のサブエージェントを**並列化**した場合になりますが、  
・同じファイルの操作  
・同じ実装範囲のコード編集  
など、競合は意図しない結果を招くため注意が必要です。  
**「どのような条件」** で **「どの範囲」** を操作するサブエージェントが登録されているのか、注意しておく必要があります。

そのため、基本的にはユーザースコープ（ホームディレクトリ）ではなく、プロジェクト単位で必要なサブエージェントを作成して管理するのがおすすめです。

コードの実装に関しては、**git-worktree**を活用すれば並列化が可能になりますので、気になる方はぜひ調べてみてください。
