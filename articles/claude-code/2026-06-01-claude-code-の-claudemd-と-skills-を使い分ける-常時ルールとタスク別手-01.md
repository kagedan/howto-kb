---
id: "2026-06-01-claude-code-の-claudemd-と-skills-を使い分ける-常時ルールとタスク別手-01"
title: "Claude Code の CLAUDE.md と Skills を使い分ける ― 常時ルールとタスク別手順の設計"
url: "https://qiita.com/goki602/items/8af4792b8e8794173e7c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "AI-agent", "qiita"]
date_published: "2026-06-01"
date_collected: "2026-06-01"
summary_by: "auto-rss"
query: ""
---

> 本記事は Claude Code(Anthropic)を活用して執筆しています。
> 検証可能な範囲で公開情報を整理したものですが、
> コード例等は実環境での動作確認をおすすめします。

CLAUDE.md に何でも書き込んでいたら 500 行を超えて制御できなくなった ― そんな状況を避けるために、公式ドキュメントは「**常に守るルールは CLAUDE.md、特定タスクの手順は Skills**」という役割分担を明確に推奨している。この記事では両者の設計思想と設定方法を公開情報から整理する。読み終えた後に「どちらに書くか」の迷いを減らすことが目的だ。

## CLAUDE.md の役割と構造

[CLAUDE.md](https://code.claude.com/docs/en/claude-md) は、Claude Code がセッション開始時に毎回自動で読み込む設定ファイルだ。リポジトリルートに置けばそのプロジェクト全体に適用され、`~/.claude/CLAUDE.md` に置けばすべてのプロジェクトに跨るグローバル設定になる。

公式ドキュメントが推奨する記載内容は以下の3つだ：

- **ビルド・テストコマンド**: `npm run build`、`pytest -x` など、チームで毎回使うコマンド
- **コーディング規約**: 型定義の書き方、命名規則、インポート順序
- **プロジェクト固有のアーキテクチャ概要**: ディレクトリ構造の意味、外部サービスへの接続方法

初期ファイルは `/init` コマンドで生成できる。Claude Code がコードベースを解析してビルドシステムやテストフレームワークを自動検出し、骨格を生成してくれる。これを雛形に削りながら育てていくのが [Best practices](https://code.claude.com/docs/en/best-practices) での推奨手順だ。

サイズの目安は **500 行以下**。これを超えると毎セッションのコンテキスト消費が増え、モデルの注意が分散しやすくなる。「この指示、毎回必要か?」を自問しながら定期的に整理するのがベストだ。

## Skills の役割と frontmatter

[Skills](https://code.claude.com/docs/en/skills) は `.claude/skills/` 以下に置く `SKILL.md` ファイル群だ。CLAUDE.md と異なり、**description が合致したときにのみ読み込まれる**条件付き設定モジュールとして機能する。

各 SKILL.md の冒頭に YAML フロントマターを記述する。

```yaml
---
name: "code-review"
description: "Pull Request のコードレビューを実施する。指摘項目の優先度付け・コメント文体・自動修正の可否を定義している。コードレビューを依頼されたとき、またはレビューコメントを整理したいときに使う。"
---
```

`description` が最重要フィールドで、Claude はこの内容を見てスキルを自動発動するか判断する。**250 文字を超えると切り詰められる**ため、「何をするスキルか」と「いつ使うべきか」のトリガー条件を前半に凝縮する必要がある。

v2.1.152 から `disallowed-tools` フィールドも利用できる。スキル実行中に禁止するツールを指定でき、意図しないファイル操作や外部リクエストをスキル単位で制御できるようになった（[リリースノート](https://github.com/anthropics/claude-code/releases)）。`disallowed-tools: ["Bash", "WebFetch"]` のように書けば、そのスキルが有効な間はシェル実行や外部フェッチが無効化される。

## 使い分けの判断基準

| 観点 | CLAUDE.md | Skills |
|---|---|---|
| 読み込みタイミング | 毎セッション自動 | description が合致したとき |
| 向いている内容 | 常時適用のルール・コマンド | 特定タスクの手順（レビュー・テスト・デプロイ等）|
| サイズ感の目安 | 500 行以下 | 1 ファイル = 1 タスク完結 |
| 配置場所 | `CLAUDE.md`（ルート）または `~/.claude/CLAUDE.md` | `.claude/skills/` または `~/.claude/skills/` |

判断のシンプルな基準はこうだ：

- **すべての作業で必要なルール** → CLAUDE.md に書く
- **特定のコマンドや場面でしか使わない手順** → Skills に切り出す

CLAUDE.md が肥大化し始めたら「このルールは特定のタスクにしか関係しないか?」を自問する。Yes なら Skills に移動するのが公式ドキュメントの推奨だ（[スキルで Claude を拡張する](https://code.claude.com/docs/en/skills)）。

## 運用上の注意点

**スキルの再読み込み**: v2.1.152 から `/reload-skills` コマンドが使えるようになった。SKILL.md を編集した後に実行すると、再起動なしに変更を反映できる。開発中はこれを活用すると試行錯誤が速くなる。

**グローバル vs プロジェクト**: `~/.claude/skills/` に置いたスキルはすべてのプロジェクトで有効になる。個人的な汎用手順はグローバルに、チーム固有の手順はリポジトリの `.claude/skills/` に置く運用が整理しやすい（[スキルオーサリングのベストプラクティス](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)）。

**description の品質が全体を左右する**: スキルが自動発動しない場合、まず description を見直す。「何をするか」だけでなく「いつ使うべきか」のトリガー条件を書くと発動精度が上がる。250 文字という制限を意識して、重要な情報を前半に詰める。

## まとめ

CLAUDE.md は「毎セッション読まれる設計書」、Skills は「呼ばれたときだけ展開される手順書」だ。CLAUDE.md を 500 行以内に抑えてタスク別の手順を Skills に切り出すことで、コンテキストの無駄遣いを防ぎつつ Claude の挙動を安定させられる。

`/init` で土台を作り、`/reload-skills` で素早く反復し、description を磨いていくサイクルが現実的な育て方になる。公式ドキュメントは [code.claude.com/docs](https://code.claude.com/docs/en/overview) にまとまっているので、実際に設定を組む前に目を通しておくと設計の迷いが減る。
