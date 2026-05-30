---
id: "2026-05-29-claude-code個人用-claudelocalmd-を-gitignore-なしでチームに共有-01"
title: "【Claude Code】個人用 CLAUDE.local.md を .gitignore なしでチームに共有せずに持つ方法"
url: "https://qiita.com/satoshi_061/items/e571850a2a0aff191d86"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "qiita"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

# はじめに

Claude Code はプロジェクトルートに `CLAUDE.md` を置くことで、AI へのコンテキスト・ルールを定義できます。

ただし `CLAUDE.md` は git にコミットされるため、チーム全員に共有されます。「自分だけのメモや好みの指示を書きたいけど、チームには見せたくない」というケースに対応するのが `CLAUDE.local.md` です。

この記事では：

1. `CLAUDE.local.md` で個人用設定を持つ方法
2. `.gitignore` を使わずにチームと共有しない方法

を紹介します。

---

# CLAUDE.md の種類

Claude Code が読み込む設定ファイルには、大きく3種類あります。

| ファイル | 場所 | 共有 |
|---|---|---|
| `CLAUDE.md` | プロジェクトルート | git にコミット → チーム全員に共有 |
| `CLAUDE.local.md` | プロジェクトルート | git 管理外にすれば自分だけ |
| `~/.claude/CLAUDE.md` | ホームディレクトリ | ローカルのみ・全プロジェクト共通 |

今回使うのは `CLAUDE.local.md` です。プロジェクトルートに置くと Claude Code が自動で読み込みます。

---

# CLAUDE.local.md を作る

```bash
touch CLAUDE.local.md
```

あとは自由に書くだけです。たとえば：

```markdown
# 個人用メモ

## 外部ファイルの読み込み
@/Users/yourname/Documents/my-rules.md

## このリポジトリでの作業メモ
- main ブランチには直接プッシュしない
- PR は必ずレビュー依頼してからマージ
```

`@ファイルパス` の記法で別ファイルをインクルードすることもできます。

---

# .gitignore を使わずに git から除外する方法

`CLAUDE.local.md` を git 管理外にするには `.gitignore` に追記するのが一般的ですが、「プロジェクトの `.gitignore` は触りたくない」という場面もあります。

そんなときに使える2つの方法を紹介します。

## 方法1: `.git/info/exclude`（このリポジトリ限定）

`.git` ディレクトリ内にあるファイルで、git にコミットされません。`.gitignore` と同じ書式で書けます。

```bash
echo "CLAUDE.local.md" >> .git/info/exclude
```

- プロジェクトの `.gitignore` を変更しない
- このリポジトリだけに適用される
- `.git` ディレクトリはコミットされないので、チームには伝わらない

## 方法2: グローバル `.gitignore`（全リポジトリに適用）

```bash
# グローバル gitignore に追記
echo "CLAUDE.local.md" >> ~/.gitignore_global

# まだ設定していない場合は Git に登録
git config --global core.excludesfile ~/.gitignore_global
```

- すべてのリポジトリで自動的に無視される
- 一度設定すれば以後どのプロジェクトでも使える
- `CLAUDE.local.md` は Claude Code の慣習的なファイル名なので、グローバル設定に向いている

---

# どれを選ぶか

| 状況 | おすすめ |
|---|---|
| このリポジトリだけに個人メモを置きたい | `.git/info/exclude` |
| どのリポジトリでも `CLAUDE.local.md` を使いたい | グローバル `.gitignore` |
| チーム全員で共通の除外ルールにしたい | `.gitignore`（コミットする） |

---

# まとめ

- `CLAUDE.local.md` をプロジェクトルートに置くと Claude Code が自動で読み込む
- `.gitignore` を変更せずに git から除外するには `.git/info/exclude` またはグローバル `.gitignore` が使える
- 「このリポジトリだけ」なら `.git/info/exclude`、「全リポジトリで使いたい」ならグローバル設定がおすすめ

チームの `CLAUDE.md` はそのままに、自分だけの作業メモやルールを気軽に書けるようになります。
