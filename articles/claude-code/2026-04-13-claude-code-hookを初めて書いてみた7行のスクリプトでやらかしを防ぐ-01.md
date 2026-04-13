---
id: "2026-04-13-claude-code-hookを初めて書いてみた7行のスクリプトでやらかしを防ぐ-01"
title: "Claude Code Hookを初めて書いてみた——7行のスクリプトで「やらかし」を防ぐ"
url: "https://qiita.com/yurukusa/items/e387a4bcfab4272dabdc"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-13"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

Claude Codeを使い始めて1週間で、作りかけのファイルをAIに消された。

リファクタリングを頼んだだけなのに、Claudeは「不要なファイルを整理しよう」と判断して、いくつかのファイルをまとめて削除した。Gitにcommitしていない変更も含めて。

GitHubにはもっと深刻な事例がある。[C:\Usersフォルダが全部消された](https://github.com/anthropics/claude-code/issues/36339)という報告。Claude Codeは便利だが、「何でもできる」ということは「何でも壊せる」ということでもある。

この事故の後、「hookを入れなきゃ」と思った。hookというのは、AIが何かをやろうとした瞬間に「ちょっと待て」と割り込んで止める仕組みだ。

## 最初のhookを書いてみる

hookは実はすごくシンプルだ。たった7行のスクリプトで書ける。

やることは1つ。AIが`rm -rf /`（ファイルを全部消すコマンド）を実行しようとしたら、ブロックする。

まず、`jq`（JSONを処理するコマンド）が必要。入っていなければ
