---
id: "2026-04-20-suica-versa-aiに渡すコンテキストも複雑になりがちだからdbと権限は別レイヤーで管理した-01"
title: "@suica_versa: AIに渡すコンテキストも複雑になりがちだからDBと権限は別レイヤーで管理した方がAIの開発スピードもでる気がしている"
url: "https://x.com/suica_versa/status/2046368755794805215"
source: "x"
category: "claude-code"
tags: ["API", "x"]
date_published: "2026-04-20"
date_collected: "2026-04-21"
summary_by: "auto-x"
query: "Claude Code CLAUDE.md 書き方 OR コンテキスト管理 OR Handover"
---

AIに渡すコンテキストも複雑になりがちだからDBと権限は別レイヤーで管理した方がAIの開発スピードもでる気がしている


--- 引用元 @kenn ---
ほら、ワイだけじゃない、RLSが諸悪の根源だってSentryの創業者も言ってるぞ

FirebaseもSupabaseも、とにかくクライアント側だけでなんとかしようというのは無理筋だという大原則をまず知ろう

DBクエリー、普通にサーバー側で書くだけで超シンプルになる
複雑性はセキュリティの最大の敵

このへんとか

https://t.co/siYhb1tGCO
Netlifyの創業者も言ってるぞ。

ちなみにReact RouterではAPIといっても何も特別なことはなく、loader/actionモデルで通常ルートのそばに置いてクッキー認証するだけなのでミスりようがないです。
Gista.jsでログイン認証を扱っているのはこの章です。BetterAuthやClerkに逃げてた人も必見。重厚なツールに頼らなくてもこんな短いコードで安全に実装できるんだ…という新鮮な気づきがあるはず。

https://t.co/tN9fCws7Lh
