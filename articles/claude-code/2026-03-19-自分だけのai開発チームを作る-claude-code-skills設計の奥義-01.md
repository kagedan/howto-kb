---
id: "2026-03-19-自分だけのai開発チームを作る-claude-code-skills設計の奥義-01"
title: "自分だけのAI開発チームを作る — Claude Code Skills設計の奥義"
url: "https://qiita.com/AI-SKILL-LAB/items/6f7247c805a8c16cfe9b"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-03-19"
date_collected: "2026-03-19"
summary_by: "auto-rss"
---

## 第1章: 7日間で100PR処理した男 — gstackの衝撃

ちょっと想像してみてください。

あなたが1週間で100本のプルリクエストを処理しなきゃいけないとしたら...無理ですよね。普通なら。

でも、Y CombinatorのCEO、Garry Tanさんが実際にやったんです。2026年3月のことでした。

「どうやって？」ってなりませんか。

秘密は、彼が公開した **gstack** っていうオープンソースの設定ファイルにありました。MITライセンスで公開されていて、誰でもワンクリックでインストールできる。

中身は、Claude Code用に設計された8つの「スキル」。

Planning、Code Review、QA... それぞれが独立した「AI担当者」のように振る舞うんです。

TechCrunchはこれを「愛と憎しみを呼んでいる」って書きました。賛否両論ってことですね。一部の人は「これはAI依存の極みだ」って批判的。でも、別の人は「これこそが開発の未来だ」って絶賛。

正直、どっちの意見も一理あるかなと思います。

AIに頼りすぎるのは危険だし、でも使わな
