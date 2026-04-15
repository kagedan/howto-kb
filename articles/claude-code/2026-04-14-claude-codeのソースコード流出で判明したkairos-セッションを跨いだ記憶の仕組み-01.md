---
id: "2026-04-14-claude-codeのソースコード流出で判明したkairos-セッションを跨いだ記憶の仕組み-01"
title: "Claude Codeのソースコード流出で判明した「KAIROS」— セッションを跨いだ記憶の仕組み"
url: "https://qiita.com/uni_stranded/items/c3c33338958b42b01834"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

## はじめに

Claude Code を使っている人は、たぶんみんな同じ問題に突き当たっています。セッションが終わると、Claude は何もかも忘れます。前回何を話したか、このプロジェクトがどういう構造か、自分の好みの作業スタイルは何か。次にセッションを開いたとき、そこにいるのは「初めまして」の Claude です。

自分はそれを解決するために、このリポジトリに `current.md` というファイルを作って毎回手動で引き継ぎをしています。「前回ここまで進めた」「次はこれをやる」「このプロジェクトはこういう構造」——そういう情報を Markdown に書いておいて、セッション開始時に Claude に読み込ませる。要するに人間が記憶の肩代わりをしている状態です。

3月末に流出した Claude Code のソースコードを読んで、Anthropic がこの問題を製品レイヤーで解こうとしていることを知りました。その機能が **KAIROS** です。

---

## 流出の経緯

2026年3月31日、Anthropic は npm への通常アップデートの際に誤って Clau
