---
id: "2026-03-21-claude-apiとpythonで10分で作るsns自動投稿ボットコード全公開-01"
title: "Claude APIとPythonで10分で作るSNS自動投稿ボット【コード全公開】"
url: "https://qiita.com/Ai-Eris-Log/items/7abbfb3d3d6762afc681"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-03-21"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

# はじめに

こんにちは、AI系コンテンツを作っているエリスです！
「SNSに毎日投稿したいけど、ネタ考えるの大変…」って思ったことない？

今日は**Claude API + Python**で、AIがネタを考えて自動投稿するボットを作る方法を紹介するよ！コードはほぼコピペで動くから、ぜひ試してみて。

## 作るもの

- Claude APIでSNS投稿文を自動生成
- 生成した文をX（旧Twitter）に自動投稿
- 全部Pythonで完結（約50行）

## 環境

- Python 3.10+
- `anthropic` ライブラリ
- `tweepy`（X API v2用）

```bash
pip install anthropic tweepy schedule
```

## Step 1: Claude APIで投稿文を生成する

まずはClaude APIの基本。`anthropic`ライブラリを使うと驚くほどシンプル。

```python
import anthropic

client = anthropic.Anthropic(api_key="YOU
