---
id: "2026-04-11-claude-46-web-search-dynamic-filtering入門-精度11向上トーク-01"
title: "Claude 4.6 Web Search Dynamic Filtering入門 — 精度11%向上・トークン24%削減の実装"
url: "https://qiita.com/kai_kou/items/f224054baeab92dc2ad6"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-04-11"
date_collected: "2026-04-12"
summary_by: "auto-rss"
---

## はじめに

Claude 4.6（Opus 4.6 / Sonnet 4.6）のリリースに合わせて、AnthropicはWeb Searchツールに**Dynamic Filtering**機能を追加しました。

これまでのWeb Searchは、検索結果のHTMLをそのままコンテキストウィンドウに読み込んでいました。Dynamic Filteringでは、Claudeがその場でフィルタリングコードを生成・実行し、関連するコンテンツだけを抽出してからコンテキストに読み込みます。

[Anthropicの公式ブログ](https://claude.com/blog/improved-web-search-with-dynamic-filtering)によると、この機能により2つのベンチマーク（BrowseComp・DeepsearchQA）の平均で**精度が11%向上し、入力トークンが24%削減**されています。

### この記事で学べること

- Dynamic Filteringの仕組みと従来の方式との違い
- `web_search_20260209`ツールバージョンの実
