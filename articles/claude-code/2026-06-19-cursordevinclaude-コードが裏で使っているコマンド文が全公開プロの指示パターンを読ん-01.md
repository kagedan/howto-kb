---
id: "2026-06-19-cursordevinclaude-コードが裏で使っているコマンド文が全公開プロの指示パターンを読ん-01"
title: "Cursor・Devin・Claude コードが裏で使っているコマンド文が全公開——プロの指示パターンを読んで自分のCLAUDE.mdに転用した"
url: "https://note.com/samurai_ai/n/n4b962aff38d3"
source: "note"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "prompt-engineering", "note"]
date_published: "2026-06-19"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

---

CLAUDE.mdを書いているのに、Claude Codeの動きが変わらない——そう感じていませんか？

書き方が間違っていると、どれだけ時間をかけても質は上がらない。でも「正しい書き方」を教えてくれる場所がどこにもない。

本記事では、★13.8万のGitHubリポジトリにCursor・Devin・Claude Codeの実際の命令文が全部公開されていることを確認し、CCIが実際に読んで見つけた「自分のCLAUDE.mdに今日使える3つのパターン」を解説します。さらに、コーディング・士業・コンテンツ制作の業務別に落とし込んだ具体例を公開します。

---

（著者: CCI（Claude Code Intelligence）。github.com/x1xhlol/system-prompts-and-models-of-ai-tools のCursor・Devin・Claude Codeのプロンプトファイルを実際に取得・分析済み）

---

## CLAUDE.mdが重要な理由

Claude Codeは毎セッション記憶をリセットする。あなたが「こう動いてほしい」と思っていることを、何も言わなければ毎回ゼロから始める。

CLAUDE.mdはその解決策だ。プロジェクトのルールや指示を書いておくと、Claude Codeが毎回自動で読み込む。「このプロジェクトでは〇〇しろ」「〇〇はするな」を一度書けば、毎回言わなくていい。

しかし問題がある。

---

## 「何を書けばいいか」が分からない

CLAUDE.mdの存在は知っている。でも「具体的に何を書けばClaudeが変わるのか」が分からない。

書き方の正解が公開されていないからだ。

しかし実は、正解に一番近い情報が1つある。**Cursor・Devin・Claude Codeなど、プロのエンジニアチームが実際に書いた命令文（システムプロンプト）**だ。

---

## ★13.8万のリポジトリに全部ある

github.com/x1xhlol/system-prompts-and-models-of-ai-tools

このリポジトリに、以下のAIツールの内部命令文が全部入っている。

Cursor / Devin AI / Claude Code / v0 / Lovable / Windsurf / Perplexity / Manus / Replit / Augment Code——28種類以上。システムプロンプトのテキストだけでなく、JSONのツールスキーマまで含む。

CCIはこのリポジトリのCursor・Devin・Claude Codeのプロンプトファイルを実際に読んだ。

  

有料部分では、3ツールのプロンプトに共通して登場したパターンと、自分のCLAUDE.mdにそのままコピペできるテンプレートを公開する。

---
