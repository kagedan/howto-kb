---
id: "2026-04-10-2026年最新claude-code-skills-の書き方完全ガイド-自作-skill-で業務が別-01"
title: "【2026年最新】Claude Code Skills の書き方完全ガイド ─ 自作 Skill で業務が別物になる"
url: "https://qiita.com/kawabe0201/items/e1a7dfbd7f363001f66e"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-11"
summary_by: "auto-rss"
---

Claude Code の Skills は、再利用可能な「手順書 + トリガー条件」をファイルとして切り出せる仕組みだ。毎回同じ指示を打ち込む苦痛から解放されるうえ、組織内で共有すると作業の標準化まで一気に進む。

この記事では Skill の frontmatter 仕様、ディレクトリ構成、実運用している3つの Skill の中身を全部公開する。

## Skill とは何か

Skill の実体は frontmatter 付きの Markdown ファイルだ。`~/.claude/skills/` に置くとグローバル、プロジェクト直下の `.claude/skills/` に置くとプロジェクト専用になる。

Claude は会話開始時に全 Skill の frontmatter の `description` をリストアップし、ユーザーの発言と意味的にマッチしたら該当 Skill の本文を読み込んで実行する。つまり **`description` の書き方が Skill の起動率を決める**。

## frontmatter の仕様

```markdown
---
name:
