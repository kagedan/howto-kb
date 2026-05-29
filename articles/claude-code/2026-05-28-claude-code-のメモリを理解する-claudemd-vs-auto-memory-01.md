---
id: "2026-05-28-claude-code-のメモリを理解する-claudemd-vs-auto-memory-01"
title: "Claude Code のメモリを理解する — CLAUDE.md vs auto memory"
url: "https://qiita.com/satoshi_061/items/69b032ad9f7f455f7fa6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "qiita"]
date_published: "2026-05-28"
date_collected: "2026-05-29"
summary_by: "auto-rss"
query: ""
---

# Claude Code のメモリを理解する — CLAUDE.md vs auto memory

Claude Code には「メモリ」の仕組みが複数あります。何をどこに書けばいいのか混乱しがちなので、整理してみました。

## メモリの種類

大きく分けると **CLAUDE.md**（指示ファイル）と **auto memory**（自動メモリ）の2種類があり、それぞれにグローバルとプロジェクト単位があります。

## CLAUDE.md（指示ファイル）

| スコープ | パス | 用途 |
|----------|------|------|
| グローバル | `~/.claude/CLAUDE.md` | 全プロジェクト共通の指示 |
| プロジェクト | `<project>/CLAUDE.md` | プロジェクト固有の指示 |
| サブディレクトリ | `<project>/src/CLAUDE.md` など | ディレクトリ単位の指示 |

手書きで管理する設定ファイルです。コーディング規約・コマンド一覧・アーキテクチャの説明などを書いておくと、会話のたびに自動で読み込まれます。

```markdown:CLAUDE.md の例
# プロジェクト概要

## よく使うコマンド

​```bash
pnpm build   # ビルド
pnpm test    # テスト
pnpm lint    # Lint
​```

## コミット規約
feat / fix / docs / chore の Conventional Commits 形式
```

## auto memory（自動メモリ）

| スコープ | パス |
|----------|------|
| グローバル | `~/.claude/memory/` |
| プロジェクト | `~/.claude/projects/<project-path>/memory/` |

Claude が会話の中で学んだことを自動的に書き出す仕組みです。`MEMORY.md`（インデックスファイル）と個別の Markdown ファイルで構成されます。

### メモリの種類

auto memory には4つの種類があります。

| 種類 | 内容 |
|------|------|
| **user** | ユーザーの役割・スキル・好み |
| **feedback** | 「こうして」「それはやめて」などの指摘 |
| **project** | 進行中の作業・方針・締め切り |
| **reference** | 外部システムへのポインタ（Linear・Slack など） |

ファイルのフォーマット：

```markdown:memory/feedback_terse_response.md
---
name: terse-response
description: レスポンスは簡潔に。末尾に要約を書かない
metadata:
  type: feedback
---

レスポンスは短く簡潔にする。作業完了後に「〇〇しました」という要約を末尾に書かない。

**Why:** ユーザーはコードの差分を自分で読める。
**How to apply:** 全レスポンスで適用。
```

## auto memory に意図的に書き込む3つの方法

### 1. 会話で「覚えて」と伝える（一番簡単）

```
〇〇を覚えておいて
Remember that ...
```

Claude が適切なメモリファイルに書き出してくれます。

### 2. ファイルを直接編集する

メモリは普通の Markdown ファイルなので手で書けます。

```bash
# インデックスを確認
cat ~/.claude/projects/<project-path>/memory/MEMORY.md

# ファイルを直接作成・編集
vim ~/.claude/projects/<project-path>/memory/user_role.md
```

`MEMORY.md` にもエントリを追記する必要があります：

```markdown:MEMORY.md
- [ユーザーの役割](user_role.md) — Node.js 5年、React は初心者
```

### 3. 種類を指定して依頼する

```
今後は PR を小さく分けて出すというルールを
feedback メモリに保存しておいて
```

のように種類を指定することもできます。

## CLAUDE.md と auto memory — どちらに書くべきか

| 観点 | CLAUDE.md | auto memory |
|------|-----------|-------------|
| 内容の性質 | プロジェクトの静的な事実 | 動的・個人的な情報 |
| 更新頻度 | めったに変わらない | 会話ごとに変わりうる |
| 共有 | チームで共有できる（リポジトリに入る） | 自分だけ（ローカル） |
| 読み込み | 毎回必ず読み込まれる | 関連性があるとき |

### 判断軸

```
他の人（チームメンバー）が読んで役に立つ？
  → Yes: CLAUDE.md
  → No（自分専用）: memory

半年後も変わらず有効？
  → Yes: CLAUDE.md
  → No（状況依存）: memory
```

**CLAUDE.md に書くべきもの**：コマンド一覧・アーキテクチャの説明・コーディング規約

**memory に書くべきもの**：自分の好み・作業スタイルへのフィードバック・進行中の作業の文脈

## まとめ

- **CLAUDE.md** = 「このプロジェクトを知らない Claude に説明すること」（安定・共有可能）
- **auto memory** = 「Claude が私との作業スタイルを学習した内容」（個人・動的）

「覚えておいて」と一言伝えるだけで auto memory に保存されるので、気づいたらどんどん蓄積させていくのが実用的な使い方です。
