---
id: "2026-07-12-claude-codeのrulesが全部常時ロードされてコンテキストを圧迫していた話-01"
title: "Claude Codeのrulesが全部常時ロードされてコンテキストを圧迫していた話"
url: "https://zenn.dev/o2wsu9/articles/aba0c9445f750d"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "zenn"]
date_published: "2026-07-12"
date_collected: "2026-07-13"
summary_by: "auto-rss"
query: ""
---

Claude Code の `~/.claude/rules/` に言語別のコーディング規約を置いていたら、Go も React も触っていないセッションでそれらが全文ロードされ、ベースラインのコンテキストを浪費していました。原因は frontmatter のフィールド名。Cursor の流儀で書いていました。発見から修正、実機での検証までの記録です。

## 事象

Claude Code はセッション開始時に `~/.claude/rules/` 配下の Markdown ファイルを読み込みます（サブディレクトリも再帰的に検出されます）。ここに `go-style.md` や `frontend-style.md` といった言語別ルールを置き、「Go ファイルを編集するときだけ Go の規約をロードしたい」という意図で frontmatter にファイルパターンを書いていました。

```
---
description: Go言語のコーディング規約
globs: "**/*.go"
---
```

ところが設定を棚卸ししてみると、ドキュメントだけを扱うセッションのコンテキストに `go-style.md` が全文入っていました。条件付けが効かず、すべてのルールが毎セッション無条件にロードされていたのです。常時消費されるベースラインは 30,000 トークン超。長時間セッションの劣化を早める要因になっていました。

## 環境

Claude Code v2.1.195 で確認しました。

## 原因

条件ロードのフィールド名が違っていました。`globs` は Cursor の `.cursor/rules` の仕様で、Claude Code はこれを解釈しません。Claude Code が条件ロードに使うのは `paths` です。

公式ドキュメントには次のように書かれています。

> Rules can be scoped to specific files using YAML frontmatter with the `paths` field. These conditional rules only apply when Claude is working with files matching the specified patterns.
>
> Rules without a `paths` field are loaded unconditionally and apply to all files.

`paths` を持たないルール、つまり `globs` しか書いていないルールは「無条件ロード」として扱われます。Cursor の流儀で frontmatter を書くと、条件付けが丸ごと無効化され、全ルールが常時ロードされるわけです。

参考: [How Claude remembers your project](https://code.claude.com/docs/en/memory)

## なぜ globs と書いていたのか

dotfiles の git 履歴を遡ると、rules ディレクトリを作った最初のコミットの時点で `description` と `globs` の組み合わせで書いていました。この 2 つを並べる書き方は、Cursor の `.cursor/rules/*.mdc` が使うスキーマ（`description` / `globs` / `alwaysApply`）そのものです。

[Cursor - Rules](https://cursor.com/docs/rules)

厄介なのは、Cursor を使っていなくてもこの罠に落ちることです。AI にルールファイルの雛形を生成させると、学習データや解説記事で最も普及している Cursor 流の frontmatter が出力されがちです。私の rules ファイルも初回コミットから `description` + `globs` の完成形で置かれており、Claude Code 向けのつもりで用意した設定に Cursor のスキーマが紛れ込んでいました。AI が生成した frontmatter はもっともらしい顔で置かれます。対象ツールの公式ドキュメントと突き合わせないと気づけません。

## 解決方法

`globs` を `paths` に置き換えます。`paths` は YAML のリスト形式で、複数パターンや brace 展開にも対応します。

```
---
description: Go言語のコーディング規約
paths:
  - "**/*.go"
---
```

複数の拡張子をまとめて指定する場合は次のように書けます。

```
---
description: フロントエンドのコーディング規約
paths:
  - "**/*.{ts,tsx,jsx}"
---
```

判断原則のように全セッションで効かせたいルールは、あえて `paths` を付けずに無条件ロードのまま残します。言語別・ファイル種別に依存するルールだけ `paths` でスコープするのが正しい使い分けです。

## 検証方法

「`paths` を付けたら本当に条件ロードされるのか」は `/memory` コマンドで確認できます。セッション中に実行すると、いまロードされている CLAUDE.md とルールファイルの一覧が表示されます。Go を触っていないセッションの一覧に `go-style.md` が無ければ、条件ロードは効いています。

ロードの理由まで見たい場合は `InstructionsLoaded` フックを使います。どのファイルが、どんな理由（`load_reason`）でロードされたかを記録できます。このフックでログを取りながら、Go ファイルを読むセッションと読まないセッションを 1 つずつ起動して比較しました。

[Claude Code hooks reference](https://code.claude.com/docs/en/hooks)

| ルール | Go を読むセッション | 読まないセッション | load\_reason |
| --- | --- | --- | --- |
| go-style.md | ロード | ロードされない | `path_glob_match` |
| coding-style.md | ロード | ロードされない | `path_glob_match` |
| security.md | ロード | ロードされない | `path_glob_match` |
| 判断原則（paths なし） | ロード | ロード | `session_start` |

Go を読んだセッションだけ言語別ルールがロードされ、`paths` を持たない判断原則はどちらのセッションでもロードされています。フィールド名を `globs` から `paths` に変えただけで、意図した条件ロードが動きました。

## 効果

言語別・設定別のルール 10 本を `paths` でスコープした結果、常時ロードされるベースラインは 30,420 トークンから 24,127 トークンに下がりました。条件ロードに回った約 6,300 トークンは、該当ファイルに触れないセッションでは消費されません。毎セッション黙って払っていた固定費が減ったことになります。
