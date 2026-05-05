---
id: "2026-05-03-kgsi-httpstcoo5mnqxhocn-01"
title: "@kgsi: https://t.co/o5mNqxHocn"
url: "https://x.com/kgsi/status/2050820587107631362"
source: "x"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "AI-agent", "Gemini"]
date_published: "2026-05-03"
date_collected: "2026-05-05"
summary_by: "auto-x"
---

https://t.co/o5mNqxHocn


--- Article ---
最近、開発の半分くらいをCodex Appに移しています。理由は単純で、4月の段階でClaudeの性能がナーフされた？と思えるぐらい、知性が下がっているな..と思ったことと、**Codexのアプリ版のCodex Appがかなり使いやすくなったからです。**

ただ、Claude Codeに慣れている人ほど、そのまま移るのは面倒だと思います。設定ファイルやスキル、コマンド、外部ツールの連携、補助エージェント、自動実行トリガー。置き場所も考え方も、少しずつ違います。

この記事、**Claude CodeからCodex Appへの移行（マイグレーション）を考えている人向けのガイドです。**スムーズにCodexへ移行できるよう解説していきます。

# 自動インポートから始める

現在、Codex Appには**「Import other agent setup」**機能があり、Claude Codeの設定を自動で読み込めます。Settings > Generalから「Import」を選ぶと、以下が自動移行されます。

基本的な移行はこのインポートフローで済みます。

手動で書き換えるのは、カスタム認証や環境変数を使ったMCP設定、ツールの権限制限、フックの挙動差分など、インポート後にレビューが必要な部分に絞られます。

# 主要機能の対応マップ

同じことをするにも、置き場所と書式が変わるものがあります。仕組みそのものが違って、機械的に変換できないものもあれば、どちらかにしかない機能もあります。
機能ごとの対応状況をまとめると、以下のようになります。

![](https://pbs.twimg.com/media/HHXvGRPaEAAs9Ph.jpg)

機械変換で済むのは、**設定ファイルとスキル、コマンド、外部ツール連携の4つです。**手で直さないといけないのは、補助エージェントと自動実行トリガー、承認設定の3つです。

# CLAUDE.mdからAGENTS.mdへ

## **自動で移行する場合**

Codex Appの「Import other agent setup」で`CLAUDE.md`は自動的に`AGENTS.md`として読み込まれます。まずはこのインポートフローを試してみてください。

## 手動で移行する場合

自動インポートを使わない場合、Claude Codeが`CLAUDE.md`（グローバルは`~/.claude/CLAUDE.md`、プロジェクトは直下）を読むのに対し、Codexが読むのはAGENTS.mdです。配置先は`~/.codex/AGENTS.md`と、リポジトリ直下になります。

フォーマットはほぼ同じMarkdownで、CodexとCursorで同様のAGENTS.mdが使えます。

`cp [CLAUDE.md](http://claude.md/) AGENTS.md`で済むケースがほとんどで、あとは「Claude Code」「Skills」「Plugins」といったツール固有の固有名を機械的に置換すれば足ります。

# スキルとコマンドの移植

## 自動で移行する場合

Codex Appのインポートフローで、SkillsとSlash commandsは自動的にCodexのskillsとして読み込まれます。まずは自動インポートを試してください。

## 手動で移行する場合

**Skills：
**スキル（[SKILL.md](http://skill.md/)）は2025年末頃から、フロントマターに`name`と`description`を書いた似たようなフォーマットがClaude Code、Codex、Cursor、Gemini CLIで使われるようになりました。

Claude Codeでは`~/.claude/skills/`、Codexでは`~/.codex/skills/`に置けば、本文の書き換えはほぼ不要です。フロントマターの一部にはツール固有のフィールドがあるので、最初の1ファイルだけ読み比べて確認しておくと安心です。

**Command：
**スラッシュコマンドは、置き場所が`~/.claude/commands/`から`~/.codex/prompts/`に変わるだけで、Markdownの中身はそのまま動きます。

**補助エージェント：
**Codex AppのインポートフローでSubagentsも自動移行されます。ただし、Claude Codeの`.claude/agents/<name>.md`はCodex側では設定ファイルの`[agents]`セクションに役割を
