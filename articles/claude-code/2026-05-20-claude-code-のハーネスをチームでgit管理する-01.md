---
id: "2026-05-20-claude-code-のハーネスをチームでgit管理する-01"
title: "Claude Code のハーネスをチームでGit管理する"
url: "https://zenn.dev/forward/articles/be82a1bc3e2948"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "AI-agent", "zenn"]
date_published: "2026-05-20"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

# ▍結論

Claude Code 用のハーネス（agents・skills・hooks・commandsなど）を**個人の設定を壊さずに**配布するためのリポジトリ【 [share-harness](https://github.com/mimo-3/share-harness) 】を公開しました。  
<https://github.com/mimo-3/share-harness>

#### ○ 使い方

使い方はとても簡単で、各種agentsやskills、hooksのファイル名またはディレクトリ名に`-shared`のpostfixをつけるだけです。

実例をお見せするためにrepositoryにしましたが、.gitignoreだけコピーして使ってくれれば、各チームの.claudeディレクトリも共有できるようになります。

# ▍個人設定と衝突しないハーネスをプロジェクト横断で使いたかった

プロジェクト横断で使うagentsやskillsをチームで共有したいと思ったことはありませんか？  
プロジェクトごとにコードレビューやデザインのskills・agentsを作るのは非効率ですし、管理も複雑になります。

プロジェクト横断設定である`~/.claude`ディレクトリの共有をしたくなるのですが、そこには個人の agentsやskillsも同居しています。

配布リポジトリと個人環境を共存させることが難点で、チームでGit管理することが難しいことが課題になっていました。

# ▍.gitignoreをホワイトリスト的に使うことで衝突を避けた

`.gitignore`をホワイトリスト的に使うことで、上記の課題を解決しました。まずは`.gitignore`ですべてのファイルをignoreします。

その上で、`-shared`というpostfixが付くファイルだけをホワイトリスト方式でgit管理するようにしてみました。

下記が`.gitignore`の抜粋です。

```
# --- 全部 ignore -----------------------------------------------------------
*

# --- ハーネス本体（-shared 命名のみ）--------------------------------------
!agents/
!agents/*-shared.md
!skills/
!skills/*-shared/
!skills/*-shared/**

!commands/
!commands/*-shared.md

!hooks/
!hooks/*-shared.py
!hooks/hooks-shared.json
!hooks/lib_shared/
!hooks/lib_shared/**
```

# ▍おわりに

みなさんも同じ課題で悩んでいるのではないかと思い、公開してみました。  
また、ハーネスというのはagentsやskillsだけを指すのではないため、MCPやtools、contextといったローカルのコーディング用ハーネスを構成するその他要素についても別の方法で共有する仕組みを作ろうとしています。それについても、ゆくゆくは公開できたらと思っています。

「うちはこうやっているぞ」などの共有があったら、ぜひ教えてください！
