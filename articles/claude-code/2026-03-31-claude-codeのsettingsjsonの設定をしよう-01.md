---
id: "2026-03-31-claude-codeのsettingsjsonの設定をしよう-01"
title: "Claude Codeのsettings.jsonの設定をしよう"
url: "https://qiita.com/makoto-ogata@github/items/641a26f0d5d40aa1c0c4"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-04-01"
summary_by: "auto-rss"
---

## 前提
Claudeを今月から本格的に使いはじめ、仕事でもプライベートの両方でClaude使ってますが実際のところ「使いこなしている」とは到底言えません。
どの程度の知識レベルかというと、大体の設定は「CLAUDE.md」書いて追加で「SKILL.md」とか書いておけばいいんでしょ？というレベルです。



## settings.jsonの役割

settings.jsonの役割は「何ができるかを制御する（権限・動作）」がメインで、何かをお願いするファイルではないということです。
何をするのか「指示」するのはCLAUDE.mdに書いておきましょう。

## やれること

めちゃくちゃ多いので、公式見たほうが早いです。

https://code.claude.com/docs/ja/settings

設定の中には権限を付与できるのもあるので、権限設定も併せて見ておくと良いと思います。
最初は下の表の3つを抑えていればだいたいは大丈夫だと思っています。

|キー|説明|
|:--|:--|
|Allow|確認なしで自動実行してOK|
|Ask|実行前に確認を求める|
|Deny|
