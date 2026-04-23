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

```
---
name: commit
description: git に変更をコミットする。メッセージの自動生成、pre-commit フック対応、Conventional Commits 準拠の整形まで行う。
---

# Commit Skill

## 手順
1. `git status` で変更を確認
2. `git diff --staged` で差分内容を把握
...
```

必須は `name` と `description` の2つ。`description` は1〜2文で「何ができるか」「いつ使うか」を具体的に書く。抽象的な説明（「git を操作する」）では起動しない。

## ディレクトリ構成

```
~/.claude/skills/
├── commit/
│   └── SKILL.md
├── review-pr/
│   └── SKILL.md
└── deploy/
    └── SKILL.md
```

1スキル1ディレクトリが推奨。スキル内で参照する補助ファイル（テンプレート、スクリプト）を同じディレクトリに同梱できる。

## 実例1: commit Skill

```
---
name: commit
description: ステージ済みの変更を Conventional Commits 形式でコミットする。差分から type (feat/fix/refactor/docs/test/chore) を自動判定し、Scope とメッセージを生成。pre-commit hook 失敗時は修正して再コミット。
---

# Commit Skill

## 前提チェック
- 未ステージの変更がある場合は中断してユーザーに確認
- `.env` など秘密情報を含むファイルが staged にあれば即中断

## 実行手順
1. `git status --short` と `git diff --staged` を取得
2. 差分から type を判定:
   - 新機能追加 → feat
   - バグ修正 → fix
   - リファクタ → refactor
   - ドキュメント → docs
   - テスト → test
   - その他 → chore
3. 最も変更の多いディレクトリを scope に設定
4. `{type}({scope}): {要約}` 形式でコミット
5. pre-commit hook が失敗したらエラー内容を読んで修正 → 再ステージ → 再コミット

## 禁止事項
- `--no-verify` の使用
- `git add .` / `git add -A`
- force push
```

`description` に具体的な挙動（Conventional Commits、type 判定、hook 対応）まで書き込むのがポイント。「コミットする」だけだと類似 Skill と区別できず起動が不安定になる。

## 実例2: review-pr Skill

```
---
name: review-pr
description: GitHub Pull Request を徹底レビューする。引数で PR 番号を受け取り、gh pr view でメタ情報、gh pr diff で差分を取得、セキュリティ・パフォーマンス・設計・テスト観点で指摘コメントを生成する。
---

# Review PR Skill

## 入力
- 引数: PR 番号（例: 123）

## 手順
1. `gh pr view {番号} --json title,body,author,files`
2. `gh pr diff {番号}` で全差分取得
3. 以下の観点でレビュー:
   - セキュリティ (SQLi, XSS, 秘密情報ハードコード)
   - パフォーマンス (N+1, 不要な再レンダリング)
   - 設計 (責務分離, 命名, 抽象化レベル)
   - テスト (カバレッジ, エッジケース)
4. 各指摘を severity (critical/major/minor) 付きで出力
5. ユーザー承認後、`gh pr review --comment` でまとめて投稿
```

「引数で PR 番号を受け取り」と書いておくと、Claude が自動で引数を抽出してくれる。

## 実例3: deploy Skill

```
---
name: deploy
description: main ブランチを本番環境にデプロイする。CI の状態確認、マイグレーションの有無チェック、承認プロンプト、デプロイ実行、Slack 通知までを自動化。ロールバック手順も含む。
---

# Deploy Skill

## 事前チェック
1. `git branch --show-current` が main か確認
2. `gh run list --branch main --limit 1` で最新 CI が success か確認
3. `git log origin/main..HEAD` で未 push がないか確認
4. マイグレーションファイルの差分を検出して警告

## デプロイ
1. ユーザーに「本番反映していいか」を必ず聞く
2. `npm run deploy:prod`
3. `curl https://api.example.com/health` でヘルスチェック
4. 失敗時は即 `npm run rollback`
5. 成功時は Slack に結果を通知

## 禁止
- 金曜夕方以降のデプロイは警告を出す
- 事前チェックをスキップしない
```

デプロイのように事故が許されない作業こそ Skill 化する価値がある。人間は疲れて手順を飛ばすが、Skill は飛ばさない。

## description を書くときの5つのコツ

1. **具体的な動詞から始める** (「コミットする」「レビューする」「デプロイする」)
2. **対象を明示する** (「ステージ済みの変更を」「GitHub PR を」「main ブランチを」)
3. **副次効果を書く** (「自動判定」「Slack 通知」「ロールバック含む」)
4. **トリガー条件が曖昧な語を避ける** (「コードを改善」はNG。「ESLint エラーを修正」はOK)
5. **1〜2文で収める** (長すぎると description マッチングの精度が落ちる)

## 要点

Skill は単なるスニペット置き場ではなく、**起動条件まで含めた再利用可能な手順書**だ。`description` を具体的に書き、1スキル1責務で切り、事故の許されない作業から優先的に Skill 化する。この3原則を守れば、日々のコーディング体験は別物になる。
