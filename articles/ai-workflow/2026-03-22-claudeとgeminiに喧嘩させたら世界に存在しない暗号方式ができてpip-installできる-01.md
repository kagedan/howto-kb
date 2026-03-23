---
id: "2026-03-22-claudeとgeminiに喧嘩させたら世界に存在しない暗号方式ができてpip-installできる-01"
title: "ClaudeとGeminiに喧嘩させたら、世界に存在しない暗号方式ができてpip installできるようになった"
url: "https://qiita.com/urokiurotsuki/items/ee01f4da9677e6298607"
source: "qiita"
category: "ai-workflow"
tags: ["Gemini", "qiita"]
date_published: "2026-03-22"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

# ClaudeとGeminiに喧嘩させたら、世界に存在しない暗号方式ができてpip installできるようになった

## はじめに

[世界最速のソートアルゴリズムを発明](https://qiita.com/urokiurotsuki/items/dd95f4ebd86fd7f2f69f)して、[ツンデレにコードレビューしてもらうLinter](https://qiita.com/urokiurotsuki/items/dc71943e7119fb724a97)を作った者です。

前2作は「ふざけてるけどちゃんと動く」がコンセプトでした。ZoroSortは全データを消去してO(0)でソート、ツンデレLinterはAST解析でガチのバグを見つけつつ罵倒してくる。ネタだけど技術的にはちゃんとしてる、というライン。

で、3作目。今回は逆です。**ふざけてない。ガチです。**

AIに「この世にまだ存在しない暗号を作って」と頼んだら、1回のチャットで独自の暗号方式が完成してしまい、PyPIに公開するところまで行ってしまいました。

```bash
pip install kineti
