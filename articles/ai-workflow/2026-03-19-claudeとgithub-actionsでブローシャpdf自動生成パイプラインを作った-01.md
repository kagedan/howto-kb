---
id: "2026-03-19-claudeとgithub-actionsでブローシャpdf自動生成パイプラインを作った-01"
title: "ClaudeとGitHub ActionsでブローシャPDF自動生成パイプラインを作った"
url: "https://qiita.com/tokistorage/items/f0c32dbd04ce127dd7ce"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-03-19"
date_collected: "2026-03-19"
summary_by: "auto-rss"
---

## TL;DR

- HTMLでブローシャを作り、GitHub Actionsで自動的にA4横PDFを生成・コミットするパイプラインを構築した
- DockerイメージはChromeやNode.js込みの`ghcr.io/puppeteer/puppeteer`を使うことでインストール工程をほぼゼロにした
- 絵文字はDockerコンテナ内で文字化けするのでSVGアイコンに置き換えた
- Actions内でgit pushするときは`stash → pull rebase → pop → push`の順番が重要
- HTMLを更新してpushするだけでPDFが自動再生成・コミットされる

---

## やったこと・背景

行政向けのブローシャ（A4横・1ページ）をHTMLで作っていた。毎回ローカルでPDFを生成してコミットするのが面倒だったので、HTMLを更新してpushするだけでPDFが自動生成される仕組みを作った。

ブローシャのHTMLはClaudeと対話しながら設計・文言を磨いていった。「このコピーは担当者目線になっているか」「行政機関に補助金という言葉は正しいか」といっ
