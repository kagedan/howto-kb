---
id: "2026-03-17-claude-codeを入れた3台のマシンを共通のclaudemd-skillsで管理する方法-01"
title: "Claude Codeを入れた3台のマシンを共通のCLAUDE.md, skillsで管理する方法"
url: "https://qiita.com/shunxneuro/items/8ed58f11c4e0e334bbba"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "cowork", "qiita"]
date_published: "2026-03-17"
date_collected: "2026-03-18"
summary_by: "auto-rss"
---

## Claude Codeを入れた3台のマシンを共通のCLAUDE.md, skillsで管理する方法 (私の活用事例)

こんにちは。Yamamotoです。初投稿です。

私はAIの研究に従事していてAIエージェントを最近よく触っています。

私の研究ではlaptop PC, GPU work station, Linux serverの三つのマシンを使いスマホもTailnet上で共有して、スマホからもターミナルを覗けるようにしています。

| マシン | OS | GPU | 主な用途 |
|---|---|---|---|
| PC1 Laptop | Windows + WSL | laptop RTX 4000 | 論文収集・解析・ **Claude Cowork** |
| PC2 Workstation | Windows + WSL | Ada 6000 (48GB) | GPUバウンドな処理・AI学習 |
| PC3 Server | Linux | RTX 4000  | デプロイ・Docker・Web |
| iPhone | iOS | - | Tailsca
