---
id: "2026-04-14-use-figmaでlpワイヤーフレームを自動生成する-figmaformlova実践ガイド-01"
title: "use_figmaでLPワイヤーフレームを自動生成する -- Figma×FORMLOVA実践ガイド"
url: "https://qiita.com/lovanaut/items/407dd4bf1a651064ad82"
source: "qiita"
category: "claude-code"
tags: ["MCP", "API", "qiita"]
date_published: "2026-04-14"
date_collected: "2026-04-15"
summary_by: "auto-rss"
---

![Gemini_Generated_Image_tfgz5itfgz5itfgz.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/4385658/ffb8c4b5-0c7c-4df5-b8d2-adb717f4fbe0.png)
<!-- IMAGE: Hero / Eyecatch -- コード断片とFigmaフレームが1対1で対応している図 -->

この記事では、Figma Plugin API（`use_figma`）を使ってLPワイヤーフレームをプログラマティックに構築する方法を解説します。MCP経由でFigmaに接続し、ヒアリングフォームの回答データをワイヤーフレームとして出力する実装パターンです。

コードスニペットはそのまま`use_figma`のコマンドとして実行できる形式で書いています。

## 前提

- Figma MCP Server に接続済み（Claude Desktop、Cursor等のMCPクライアント経由）
- `use_figma`ツールでFigma Plugin
