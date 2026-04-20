---
id: "2026-04-19-cmux-上で-vim-から-claude-code-にファイル参照を渡すプラグイン-cmuxvim-01"
title: "cmux 上で Vim から Claude Code にファイル参照を渡すプラグイン cmux.vim を作った"
url: "https://zenn.dev/tanabee/articles/e9652e4dd2a11b"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "antigravity", "zenn"]
date_published: "2026-04-19"
date_collected: "2026-04-20"
summary_by: "auto-rss"
query: ""
---

背景
最近は Antigravity（IDE）と cmux（Vim + Claude Code）を使い分けて開発しています。IDE 側では当たり前にできる「エディタからファイル参照を渡す」操作が、cmux 上の Vim からだと手間でした。これがネックで、ファイル参照を渡したい場面では IDE に切り替えていました。
&gt; @src/components/UserProfile.tsx:L42-55 この部分のリファクタリングをお願い
このように @filepath でファイルや行範囲を明示的に指定するのは、AI に無駄なコンテキストを読ませず必要な箇所だけを渡せるという点で重要...
