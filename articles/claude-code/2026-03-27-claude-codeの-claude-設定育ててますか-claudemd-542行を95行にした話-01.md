---
id: "2026-03-27-claude-codeの-claude-設定育ててますか-claudemd-542行を95行にした話-01"
title: "Claude Codeの `.claude/` 設定、育ててますか？ — CLAUDE.md 542行を95行にした話と、自己診断スキルの作り方"
url: "https://qiita.com/kiyotaman/items/487f16cb54e018bf52eb"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "qiita"]
date_published: "2026-03-27"
date_collected: "2026-03-28"
summary_by: "auto-rss"
---

## はじめに

Claude Codeを本格的に使い込んでいくと、`.claude/` ディレクトリが育っていく。rules、commands、agents、hooks。気がつけば充実した開発環境が出来上がる。

先日、以下の記事を書いたが、

https://qiita.com/kiyotaman/items/30b14edf0b8a8cb5d01c

しかし、ある日ふと気づく。**CLAUDE.md が542行ある。そしてその大半が、`.claude/rules/` や `.claude/commands/` に書いたことの繰り返しだ。**

この記事では、開発時にClaude Code設定を全面的に見直した実体験をもとに、`.claude/` ディレクトリの「育て方」と「メンテナンスの仕組み化」について書く。

## CLAUDE.md が肥大化する構造的な理由

### 最初は便利だった

CLAUDE.mdは最初、プロジェクト固有の知識をClaude Codeに伝える唯一の場所だった。コーディング規約、テストの実行方法、ブランチ戦略、エラー時の対処法……。全部ここに書いた
