---
id: "2026-03-29-pythonでmcpサーバーを自作する-fastmcpで始めるaiツール開発の実践入門-01"
title: "PythonでMCPサーバーを自作する — FastMCPで始めるAIツール開発の実践入門"
url: "https://qiita.com/AI-SKILL-LAB/items/3ec7ef3dc124399fabea"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "Python", "qiita"]
date_published: "2026-03-29"
date_collected: "2026-03-30"
summary_by: "auto-rss"
---

# PythonでMCPサーバーを自作する — FastMCPで始めるAIツール開発の実践入門

## はじめに — stdioサーバーで `print()` したら壊れた話

正直に言うと、最初にMCPサーバーを作ったとき、stdioサーバーで普通に `print()` してデバッグしようとして、盛大に壊しました。

Claude Desktopで接続を試みると、ツールが認識されない。エラーログを見ても原因がわからない。「あれ、コード自体は正しいはずなのに...」という状態が30分くらい続いて、ようやく気づいたんです。stdioってJSON（リクエスト/レスポンスをJSONフォーマットでやり取りする仕組み）のメッセージを標準入出力でやり取りしてるんですよね。そこに `print()` でデバッグ文字列を混ぜたら、当然ながらパーサーが壊れる。

でも、その30分後に自分のツールが初めてClaude Desktopで呼ばれたとき...なんか「自分が作ったものをAIが使っている」という不思議な感覚があって、わりとこれは体験する価値があるなと思いました。

この記事は、そういう実際のハマりポ
