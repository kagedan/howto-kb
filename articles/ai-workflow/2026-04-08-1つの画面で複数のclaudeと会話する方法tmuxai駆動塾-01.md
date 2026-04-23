---
id: "2026-04-08-1つの画面で複数のclaudeと会話する方法tmuxai駆動塾-01"
title: "1つの画面で複数のClaudeと会話する方法【tmux】｜AI駆動塾"
url: "https://note.com/l_mrk/n/n7a3aebdf91eb"
source: "note"
category: "ai-workflow"
tags: ["note"]
date_published: "2026-04-08"
date_collected: "2026-04-08"
summary_by: "auto-rss"
query: ""
---

お世話になっております。AI駆動塾です。

走り書きの記事になりますが、tmuxとClaudeCodeの体験がかなりよかったのでシェアします。

これまで私は基本的に私はX運用をする際に下記のようにそれぞれ「長文作成用」、「短文作成用」というふうにターミナルを画面分割してClaudeCodeを運用していました。

![](https://assets.st-note.com/img/1775606859-3yBh9ZpzFbMm1LGvxVfQOeSq.png?width=1200)

**しかし、とにかく見ずらい触りずらい。**

少し各ターミナルの位置をずらすと、「あれ？これ何用のターミナルだっけ？」と各画面の会話そ遡って時間を無駄にしてしまったり、普通にブラウザを見てる時、邪魔だからと手癖で誤ってウィンドウを消してしまったり。

ここで私に**「1画面で複数のClaudeと会話したい！」**という目標ができました。

まず通常のターミナルで先述の目的を達成しようとしたところ、1画面で複数のターミナルを起動して管理することはできました。

しかし、**下記画像のように横に分割することしかできません。**

![](https://assets.st-note.com/img/1775609051-C4KgRSMecfDmAaUWtzxEGXTy.png?width=1200)

みなさんご存知のように、Claudeの出力は上から下に出力されるので、横分割のままだと会話が非常に見ずらい。なので可能ならば縦分割できるようにしたい。
