---
id: "2026-04-09-aiエージェントの記憶基盤にcockroachdbを選んだ技術的な理由postgresql互換ベクタ-01"
title: "AIエージェントの記憶基盤にCockroachDBを選んだ技術的な理由——PostgreSQL互換・ベクター検索・ゼロデータロス"
url: "https://qiita.com/claush/items/b1f686ac6a586c7ddc24"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-09"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

## はじめに——なぜDBの選択が重要か

AIエージェントに長期記憶を持たせる際、データベースの選択は「どこにデータを置くか」以上の意味を持つ。

- セッションをまたいで記憶が残るか
- サーバー移行時にデータが消えないか
- 意味検索（セマンティック検索）に対応できるか
- スキーマ変更のたびにサービスを止めなくて済むか

これらの問いに対する答えが、DBの選択を左右する。

本記事では、iOSアプリ「Claush」のAI記憶基盤として**CockroachDB**を選んだ技術的な理由を整理する。

---

## Claushとは

**Claush**は、iPhoneからVPS上のClaude CodeをSSH経由で操作するiOSアプリだ。チャット感覚でClaude Codeに指示を出せるほか、アプリを閉じてもVPS上で処理が継続するバックグラウンド実行に対応している。

https://apps.apple.com/jp/app/claush/id6760445443

AIキャラクター「セバス」が会話を担当し、会話の長期記憶を保持する。記憶システムはVPS上で動作する`m
