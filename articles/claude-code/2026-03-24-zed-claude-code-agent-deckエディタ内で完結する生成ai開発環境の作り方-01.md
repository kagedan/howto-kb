---
id: "2026-03-24-zed-claude-code-agent-deckエディタ内で完結する生成ai開発環境の作り方-01"
title: "Zed × Claude Code × agent-deck：エディタ内で完結する生成AI開発環境の作り方"
url: "https://zenn.dev/milmed/articles/745aa734fcfdcc"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "zenn"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

なぜZed上でClaude Codeを動かすのか
生成AIツール（Claude Codeなど）をターミナルで使うとき、多くの方は別ウィンドウや専用ターミナルアプリを開き、その中でコマンドを実行します。
しかし、その方法には次のような課題があります。

ウィンドウやタブの切り替えが頻繁に発生する
ターミナルとエディタで操作体系が異なり、コンテキストスイッチが大きい
ファイルパスや行番号をコピーしてAIに渡す操作が手間になりがち

そこで私は、Zedのエディタ領域そのものをターミナルとして使うことで、
「普段のプログラミング操作の延長」でClaude Codeを扱えるようにしています。
...
