---
id: "2026-06-05-claude-code-の-review-と-code-review-は何が違うのか-対象動作種別で-01"
title: "Claude Code の `/review` と `/code-review` は何が違うのか ── 対象・動作・種別で使い分ける"
url: "https://zenn.dev/gudezou/articles/86b91bfb854da6"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-06-05"
date_collected: "2026-06-06"
summary_by: "auto-rss"
query: ""
---

![サムネイル](https://static.zenn.studio/user-upload/4587b8f6b5cc-20260605.png)

* `/review` はプルリクエストを読み取り専用で見るコマンド、`/code-review` はいま編集している差分を調べて `--fix` で直せるスキル。
* 見分ける軸は3つで、対象 (プルリクエストか差分か)、動作 (見るだけか直すか)、種別 (組み込みコマンドかスキルか)。
* `/security-review` はセキュリティ専用、`/simplify` は動作の誤りを探さず、`/verify` はアプリを実際に動かして確かめる。

---

## `/review` は PR を読み、`/code-review` は差分を直す

`/review` と `/code-review` は名前がそっくりです。  
でも、対象・動作・種別の3つの軸すべてで違います (Anthropic Docs > Commands)。

`/review` は、Claude Code に最初から入っている組み込みコマンドです。  
対象はプルリクエスト (PR) です。  
いまのセッションの中で、読み取り専用でレビューします。  
コードには手を入れず、読んで指摘するだけです。

`/code-review` は、バンドルされたスキルです。  
スキルとは Claude に渡されるプロンプトの一種で、関連する場面では Claude が自分で呼び出すこともあります。  
対象は、いま編集している差分です。  
動作の誤りと、再利用・単純化・効率といった整理できる箇所の両方を調べます。

`/code-review` には、付けられるオプションがあります。  
`--fix` を付けると、見つかった指摘を作業ツリーにそのまま反映します。  
`--comment` を付けると、GitHub のプルリクエストにインラインのコメントとして投稿します。  
さらに `/code-review ultra` を使うと、クラウド上で複数のエージェントによる深いレビューを走らせられます。  
この `/code-review ultra` は、`/ultrareview` という別名でも呼び出せます。  
ただし、いま推奨されている呼び出し方は `/code-review ultra` のほうです。  
`/ultrareview` は別名として残っているだけなので、新しく覚えるなら `/code-review ultra` で十分です。

対象も動作も種別も違うので、名前は似ていても別物だと覚えておいてください。

![/review と /code-review の対象・動作・種別の対比](https://static.zenn.studio/user-upload/c8d47015707d-20260605.png)

---

## `/security-review`・`/simplify`・`/verify` をいつ使い分けるか

レビュー系のコマンドは、やりたいことから逆引きすれば迷いが減ると思います。

`/security-review` は、セキュリティ専用のレビューです。  
いまのブランチにたまった変更を解析します。  
インジェクション・認証まわりの問題・データの漏れといったリスクを洗い出します。

`/simplify` も、バンドルされたスキルです。  
整理できる箇所だけをレビューして、修正を当てます。  
既存の部品を使い回せないか、もっと単純にできないか、といった切り口で見ます。  
ただし `/simplify` は、動作の誤りそのものは探しません。  
バグを見つけたいときは `/code-review` を使います。

`/verify` は、変更が本当に動くかを確かめるスキルです。  
テストや型チェックには頼りません。  
プロジェクトのアプリを実際にビルドして動かし、結果を見て意図どおりか確かめます。

コードの正しさを疑うなら `/code-review`。  
整理だけなら `/simplify` です。  
セキュリティなら `/security-review`。  
実際の動きを確かめるなら `/verify` です。  
プルリクエスト全体を読むなら `/review` を使います。  
これらの定義は Anthropic Docs > Commands ページに揃っています。

![レビュー系コマンドの使い分け早見表](https://static.zenn.studio/user-upload/83ffb71d5e6a-20260605.png)

---

## 参考文献

1. Anthropic. *Commands - Claude Docs*. Anthropic. <https://code.claude.com/docs/en/commands>
