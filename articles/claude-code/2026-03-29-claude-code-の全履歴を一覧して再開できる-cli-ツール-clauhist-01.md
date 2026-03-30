---
id: "2026-03-29-claude-code-の全履歴を一覧して再開できる-cli-ツール-clauhist-01"
title: "Claude Code の全履歴を一覧して再開できる CLI ツール clauhist"
url: "https://qiita.com/lef237/items/05a8ead41b3d558c58f2"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-29"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

Claude Code でも、作業ディレクトリに移動してから `/resume` を使えば、そのディレクトリの履歴をたどれます。

ただ、そこで見られるのは基本的にその作業ディレクトリの履歴です。複数のリポジトリや作業ディレクトリをまたいで、過去の作業をまとめて見たいときは少し不便です。

`clauhist` は、その不便さを埋めるための CLI ツールです。Claude Code の履歴を `fzf` で一覧し、作業ディレクトリをまたいで目的のセッションを探して、そのまま再開できます。

## インストール

```sh
cargo install clauhist
```

ソースから入れる場合は次のとおりです。

```sh
git clone https://github.com/lef237/clauhist.git
cd clauhist
cargo install --path .
```

実行時には `fzf` と Claude Code が必要です。

現在はcargoでのインストールのみに対応しています。

## できること

`clauhist` を起動する
