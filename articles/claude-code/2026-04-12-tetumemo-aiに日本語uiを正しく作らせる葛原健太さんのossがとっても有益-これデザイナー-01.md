---
id: "2026-04-12-tetumemo-aiに日本語uiを正しく作らせる葛原健太さんのossがとっても有益-これデザイナー-01"
title: "@tetumemo: 📝 AIに日本語UIを「正しく」作らせる葛原健太さんのOSSがとっても有益、 これデザイナーもエンジニアもVibe Co"
url: "https://x.com/tetumemo/status/2043181131085054337"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-04-12"
date_collected: "2026-06-20"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

📝 AIに日本語UIを「正しく」作らせる葛原健太さんのOSSがとっても有益、
これデザイナーもエンジニアもVibe Codingするなら全員知った方がいいレベル。

「awesome-design-md-jp」っていう
日本語対応のDESIGNmd集。
Apple・MUJI・LINE・Mercari・noteなど
日本の有名サービス24社分のデザインルールを収録。

これ何かというと、DESIGNmdをプロジェクトに置くだけでAIが「そのサービスらしいデザイン」を再現してくれる仕組み。

でも今まで欧米サービスしかなくて、日本語UIを作らせるとフォントがおかしい・行間が詰まってる・句読点が崩れるみたいなことが普通に起きてた。

それを解決したのがこのリポジトリです↓🧵

そもそも「DESIGNmd」って何かというと、
Google Stitchが提唱したフォーマットで「AIエージェント向けのデザイン仕様書」のこと。

AGENTSmd（どう作るか）と並べて
DESIGNmd（どう見せるか）をプロジェクトに置く。

これだけでAIが毎回ゼロから考えなくてもそのサービスのデザインを再現できるようになる。

で、日本語版が必要な理由が面白くて、

◆ 和文フォント指定がない
→ AIが勝手にHelveticaとかで組んでしまう

◆ 行間（line-height）の違い
→ 欧文は1.4〜1.5が標準
→ 日本語は1.7〜2.0が標準
→ そのまま使うと読みにくい詰まった文章になる

◆ 字間（letter-spacing）の違い
→ 日本語は0.04〜0.1emが読みやすい
→ 欧文仕様のままだと窮屈な見た目に

◆ 禁則処理
→ 句読点や括弧の行頭・行末ルール
→ これがないと「、」が行頭に来たりする

こういう細かい積み重ねで
「なんか日本語っぽくない」UIができあがってた。

個人的に面白いと思ったのが
Claude（AI）と一緒に作ったって点で、

コミットログに「claude」が共同作者として入ってる。

収録されてるサービスも
Apple Japan・MUJI・Mercari・LINE・note・Zenn・Qiita・楽天・食べログ・pixiv...

日本のWebを代表するサービスが24社分。

「AIに日本語のUIを作らせたら微妙だった」
って経験がある人、
このリポジトリのDESIGNmdをプロジェクトに入れるだけで
かなり変わると思います。

テンプレートも公開されてるので
自社サービスのDESIGNmdを作るのにも使えます。

https://t.co/AFDN0sApcO

葛原健太さんのポストはこちら　↓

https://t.co/ObBAB99Dxk

Awesome Design MD JP

https://t.co/vu4SGuo9K9 https://t.co/LYz7SOI3DD

📝毎週火曜日にAIに特化した実体験型ニュースレターを発行しています

無料で読めます　↓

https://t.co/ciBcp7XVmv

今週の記事

📝Google AI Proの無料でもらえる$10クレジット、毎月消えていませんか？Claude Code × Nano Banana 2で有効活用して使い切る方法

https://t.co/nKDGAwTtmg
