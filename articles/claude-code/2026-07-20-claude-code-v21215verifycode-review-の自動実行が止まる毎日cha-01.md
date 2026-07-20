---
id: "2026-07-20-claude-code-v21215verifycode-review-の自動実行が止まる毎日cha-01"
title: "Claude Code v2.1.215｜/verify・/code-review の自動実行が止まる｜毎日Changelog解説"
url: "https://qiita.com/moha0918_/items/cec53cc700e513ac13d7"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "qiita"]
date_published: "2026-07-20"
date_collected: "2026-07-21"
summary_by: "auto-rss"
query: ""
---

:::note info
Claude Codeの[公式Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)をリリースから最速で翻訳・解説しています。
:::

v2.1.215 で Claude Code が `/verify` と `/code-review` を自分から走らせなくなりました。検証もレビューも、打った時だけ動く。裏で黙ってトークンを消費されていた人には効く変更です。

## /verify と /code-review が勝手に走らなくなった

**変わったのは起動の主導権だけ。スキル自体は無くなりません。**

changelog の記載はこの 1 行だけ。

> Claude no longer runs the `/verify` and `/code-review` skills on its own; invoke them with `/verify` or `/code-review` when you want them

これまでの Claude Code は、コードを書き換えたあとに「検証したほうがいい」「レビューしたほうがいい」と判断すると、`/verify` や `/code-review` を自分から起動することがありました。頼んでいないのにテストが回り始めたり、差分レビューが走ったり。検証が要らない小さな変更でも一式走って、トークンと時間を持っていかれることがあった。

v2.1.215 でこの自動起動が止まります。検証もレビューも、打った時だけ動く。エージェントが裏で何を始めるか読めない状態が減り、1 タスクあたりの消費が予測しやすくなります。

:::note warn
CLAUDE.md やワークフローで「実装後に自動で検証が走る」前提を書いていた場合、その前提は崩れます。検証やレビューを確実に通すには、手順として `/verify` `/code-review` を明示的に挟む必要があります。
:::

## 使いたいときは自分で呼ぶ

やることは単純。検証したいタイミングで打つだけ。

- `/verify` は変更を実際に動かし、意図どおり動くかを end-to-end で確認する
- `/code-review` はいまの差分を読み、バグや整理できる箇所を洗い出す

自動起動が消えただけで、スキルの中身は同じ。起動を決めるのが Claude から自分に移りました。

## 影響が出るのは自動検証に頼っていた人

:::note info
対象読者: 実装 → 自動検証 → 修正のループを Claude 任せにしていた人。
:::

明示的に `/verify` を打つ習慣が無かった人は、今後は自分で呼ばないと検証が走りません。逆に、勝手なレビューを煩わしく感じていた人にとっては、頼んでもいないレビューが割り込まなくなります。

## まとめ

v2.1.215 は `/verify` と `/code-review` の自動起動を止める 1 点のみの更新。スキルは残り、呼び出しが明示指定に変わっただけです。自動検証を運用に組み込んでいたなら、手順に `/verify` `/code-review` を書き足しておくと安全。
