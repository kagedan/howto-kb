---
id: "2026-04-14-aiollm-web-search対応の実装レシピrobotstxt-llmstxt-構造化データ-01"
title: "AIO（LLM Web Search）対応の実装レシピ：robots.txt / llms.txt / 構造化データ"
url: "https://qiita.com/Enegent/items/680f547fc6bf946af87a"
source: "qiita"
category: "ai-workflow"
tags: ["LLM", "qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

## はじめに

個人開発で運営している電気料金比較サービス [エネジェント](https://enegent.jp) で、**AIO（LLM Web Search）対応**を一通り整えたのでレシピとして共有します。

AIO = AI Optimization。従来のSEO（Googleの検索結果で上位を取る）とは別軸で、ChatGPT・Claude・Perplexity・Grok 等のLLMが**Web検索→引用する時に拾われやすいサイト構造**を整える取り組みです。

「誰よりも早く対応する」価値があると判断した理由:

- LLM経由の流入は今後数年で確実に増える
- 対応している個人開発サイトがまだ少ない
- 技術的には**数時間で実装可能**

対応した項目:

1. **robots.txt** で AI クローラーを明示的に歓迎
2. **llms.txt**（Anthropic発の新規格）でサイト概要・主要ページを提示
3. **構造化データ**（JSON-LD）を全記事に敷く
4. **動的OGP画像**（シェア時の視認性）
5. **相互リンク**でE-E-A-T
