---
id: "2026-04-20-claude-codeが突然存在しないファイルを編集しましたと言い出したcompact後の幻覚を防ぐ-01"
title: "Claude Codeが突然「存在しないファイルを編集しました」と言い出した——compact後の幻覚を防ぐhook"
url: "https://qiita.com/yurukusa/items/a4a79ee057de1e532ff3"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

3時間のセッション中に突然、Claudeが「先ほど作成したutils/helper.tsを更新しました」と言い出した。そんなファイルは作っていない。

これはcontext compaction後に発生する「幻覚」で、GitHub Issue [#46602](https://github.com/anthropics/claude-code/issues/46602) で報告された（現在はクローズ済み、ただしcompactionの仕組み上、類似の現象は依然として発生しうる）。compactionで会話履歴が要約される際に、要約が不正確になり、Claudeが「やっていないこと」を「やった」と認識してしまう現象だ。

## 何が起きるのか

context compactionは、コンテキストウィンドウが一杯になると自動で実行される。古い会話を圧縮して容量を空ける処理だ。問題は、この圧縮で情報が失われること。

具体的には:
- 「ファイルAを編集した」という記録が「ファイルA,B,Cを編集した」に要約される
- 実際には存在しないファイルへの言及が生まれる
- Claudeがその幻覚に
