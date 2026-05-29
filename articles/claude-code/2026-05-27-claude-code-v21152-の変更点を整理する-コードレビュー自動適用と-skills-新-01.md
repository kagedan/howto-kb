---
id: "2026-05-27-claude-code-v21152-の変更点を整理する-コードレビュー自動適用と-skills-新-01"
title: "Claude Code v2.1.152 の変更点を整理する — コードレビュー自動適用と Skills 新フロントマター"
url: "https://zenn.dev/goki602/articles/2026-05-27-claude-code-v2-1-152-what-changed"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-05-27"
date_collected: "2026-05-29"
summary_by: "auto-rss"
query: ""
---

2026年5月27日、Claude Code v2.1.152 がリリースされた。今回のアップデートは `/code-review` の大幅強化と、Skills フロントマターの拡張が中心だ。「レビューして終わり」から「レビューして直す」への一歩を踏んだリリースといえる。[公式リリースノート](https://github.com/anthropics/claude-code/releases)と[公式 changelog](https://code.claude.com/docs/en/changelog)をベースに、実際のワークフローへの影響を整理する。

## 主な変更点4つ

v2.1.152 の変更は次の4点にまとめられる。

* **`/code-review --fix`** — レビュー結果を working tree に直接適用
* **`/simplify` の変更** — `/code-review --fix` を呼び出すエイリアスに統合
* **Skills frontmatter の `disallowed-tools` 対応** — スキル実行中に無効化するツールを指定可能に
* **`/reload-skills` コマンド追加** — 再起動なしでスキルを再スキャン

## `/code-review --fix` — 指摘と修正を1コマンドに

これまでの `/code-review` は差分を解析して問題点や改善案を**列挙するだけ**だった。修正は手動で行う必要があり、指摘が多いと対応コストも高くなりがちだった。

v2.1.152 からは `--fix` フラグを付けることで、レビュー結果を working tree に**直接書き込む**ところまで自動化される。公式リリースノートによれば、正確性・再利用性・簡略化・効率改善の4軸でレビューを行い、その場で修正を適用する。

effort レベルと組み合わせることも可能だ。

```
# 公式 docs の記述に基づく。実行前に git 作業ツリーが clean な状態を推奨
/code-review --fix
/code-review high --fix
```

effort を `high` 以上にすると指摘の網羅性は上がるが、確度の低い提案も含まれてくる可能性がある。`medium`(デフォルト)で `--fix` を日常使いしつつ、重要な PR の前後に `high` で精査するといった使い分けが、公開情報を見る限り自然に見える。

なお `--comment` フラグ(GitHub PR のインラインコメント投稿)と `--fix` は排他でなく、組み合わせも可能だ。

## `/simplify` の変更 — エイリアスへ統合

`/simplify` はこれまで独立したコマンドとして機能していたが、v2.1.152 から **`/code-review --fix` を呼び出すエイリアス**に変更された。

「既存ユーザーへの影響」という観点で重要なのは、`/simplify` を打つと**提案の表示ではなく自動修正**が走るようになった点だ。意図せずファイルが変更される事故を防ぐため、実行前に `git status` で作業ツリーを確認する習慣をつけておきたい。チームで Claude Code を使っている場合は、この挙動変更をメンバー間で共有しておく価値がある。

Claude Code の Skills は `.claude/skills/` 以下のマークダウンファイルで定義するカスタムコマンドだ([公式スキルドキュメント](https://code.claude.com/docs/en/skills))。従来 frontmatter で指定できた `allowed-tools` は「使えるツールを明示的に絞る許可リスト」として機能していた。

v2.1.152 で追加された **`disallowed-tools`** は逆に**拒否リスト**として機能する。

```
---
name: audit-check
description: ファイルを読むだけの監査スキル
disallowed-tools:
  - Edit
  - Write
  - Bash
---

# スキルの本文...
```

`allowed-tools` と `disallowed-tools` の使い分けを整理する。

| フィールド | 動作 | 向いているケース |
| --- | --- | --- |
| `allowed-tools` | 指定ツールのみ使用可 | 使えるツールを厳密に絞りたいとき |
| `disallowed-tools` | 指定ツールのみ無効化 | ほぼ全ツールを使わせつつ、一部だけ禁止したいとき |

公開情報によれば、`allowed-tools` と `disallowed-tools` が両方指定された場合、`allowed-tools` が優先され `disallowed-tools` は無視される。`disallowed-tools` が効くのは `allowed-tools` が未指定の場合のみ、という点を押さえておきたい([Feature Request #6005](https://github.com/anthropics/claude-code/issues/6005) も参照)。

なお、`allowed-tools` の強制実施については過去に複数の GitHub Issues で「設定しても無視される」という報告があった([Issue #18837](https://github.com/anthropics/claude-code/issues/18837))。`disallowed-tools` が実運用でどの程度強制されるかは、今後のコミュニティレポートを追うのが確実だ。

## `/reload-skills` — 再起動なしで変更を反映

スキルを追加・編集した後、これまでは Claude Code のセッション再起動が必要だった。v2.1.152 で追加された `/reload-skills` コマンドを使うと、**セッションを維持したまま `.claude/skills/` を再スキャン**できる。

スキルを試行錯誤しながら開発する場面では、「編集 → 再起動 → 確認」サイクルを「編集 → `/reload-skills` → 確認」に短縮できる。小さな改善だが、スキルを頻繁に手直しする開発フェーズでは積み重なって効いてくる変更だ。

## まとめ

v2.1.152 の変更方向は明確だ — **コードレビューの「指摘止まり」を解消**し、**Skills の制御をより細かく・反復しやすく**整備する。

なかでも `/code-review --fix` は、「レビュー → 手動修正」のサイクルを1コマンドに縮める可能性を持つ。`/simplify` の挙動変更は既存ユーザーへの影響があるため注意が必要だ。`disallowed-tools` は「全ツール許可のまま一部だけ制限したい」という設定の簡潔さが魅力で、スキル設計の幅を広げてくれる。

詳細は[公式リリースノート](https://github.com/anthropics/claude-code/releases)と[スキルドキュメント](https://code.claude.com/docs/en/skills)で確認できる。
