---
id: "2026-04-20-claude-code-の記憶を育てる-osskiokuを作った-01"
title: "Claude Code の記憶を育てる OSS「KIOKU」を作った"
url: "https://qiita.com/megaphone-tokyo/items/fdd8d91e1134e15fc5d7"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-rss"
query: ""
---

![Generated Image April 16, 2026 - 10_20PM.jpg](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4412014/6e9ada1a-a55d-4a23-af43-45cbe7e22037.jpeg)


> ※この記事は [Zenn での投稿](https://zenn.dev/megaphone/articles/af2b2a05531912) の転載です。

## はじめに

Claude Code を毎日使っていて、一つ大きな不満がありました。

**「前のセッションで話した内容、次のセッションでは全部忘れられている」**

プロジェクトの前提、使っている技術スタック、設計判断の理由。毎回一から説明し直す日々。「これ昨日も言ったんだけどな...」を何度繰り返したか分かりません。

この問題を解決するために、Claude Code のセッション記憶を自動で蓄積するツールを作りました。

**KIOKU — Memory for Claude Code**

http
