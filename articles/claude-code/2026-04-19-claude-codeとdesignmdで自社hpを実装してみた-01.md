---
id: "2026-04-19-claude-codeとdesignmdで自社hpを実装してみた-01"
title: "Claude CodeとDESIGN.mdで自社HPを実装してみた"
url: "https://qiita.com/Kawashima_RPA/items/e2c7da94bfa59bd3859e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-19"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

## WordPressで自社HPを構築していたが、再検討してみた

以前はXサーバーでWordPressを使って自社HPを運営していました。ドラッグ&ドロップでページを組めて便利だったのですが、使い続けるうちに「本当にWordPressが必要か？」と思うようになりました。

- ブログ記事はQiitaに移行していた
- WordPressの管理画面の重さ、プラグインの更新管理が負担になってきた
- デザインの細かい調整が意外とやりにくい

そこで、**「Claude Codeでホームページを作り直してみよう」** と再検討することにしました。どこまで作れるか試してみたくなったのです。

---

## できあがったもの

![HP実装デモ](https://raw.githubusercontent.com/AutoFor/life-public/main/qiita/assets/hp-demo.gif)

**実際のHP：https://autofor.co.jp/**

実装したページ：

- `index.html` — トップページ
- `about.html` — 会社概
