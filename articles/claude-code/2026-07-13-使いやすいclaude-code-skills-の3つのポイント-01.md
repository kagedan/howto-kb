---
id: "2026-07-13-使いやすいclaude-code-skills-の3つのポイント-01"
title: "使いやすいClaude Code Skills の3つのポイント"
url: "https://note.com/quirky_iguana824/n/nd5d306138a1b"
source: "note"
category: "claude-code"
tags: ["claude-code", "AI-agent", "TypeScript", "note"]
date_published: "2026-07-13"
date_collected: "2026-07-13"
summary_by: "auto-rss"
query: ""
---

---

同じ説明をClaude Codeに何度も入力しているなら、その手順はSkillにまとめられます。ただ、長いSkillを作るだけでは、必要な場面で呼ばれなかったり、逆に余計な場面で動いたりします。

## 🔍 63個のSkillsを読み比べてわかったこと

Total TypeScriptのMatt Pocockと、Google ChromeチームのAddy Osmaniが公開した2つのリポジトリから、合計63個のSKILL.mdを分析しました。

共通していたのは、Claude Codeが迷いやすい判断を文章にしていた点です。code-simplificationは、コードは動くが読みにくい場面で使う一方、内容を理解していない段階や速度を落とす恐れがある場面では使いません。

writing-great-skillsは、すべてを1ファイルに詰め込まず、詳しい資料を別ファイルに逃がす構成です。指示を増やすより、必要な判断だけを先に読ませる設計といえます。

## ① 「いつ使うか」を動作で書く

Claude Codeはdescriptionを見てSkillを自動で呼ぶか判断します。「便利な文章作成Skillです」のような紹介文では、使う場面が伝わりません。

変更内容から説明文を作るSkillなら、こう書けます。

description: 未コミットの変更を要約し、危険な変更を指摘する。変更内容の確認やプルリクエスト説明文の作成を頼まれたときに使う。

「要約する」だけでなく「変更内容の確認」「説明文の作成」という依頼まで書くことで、Skill名を覚えていなくても普段の言葉から呼ばれやすくなります。

## ② 「いつ使わないか」で誤作動を減らす

使う条件だけでは、似た作業にも反応してしまいます。使わない条件を具体的に書くSkillが目立ちました。

コードを読みやすくするSkillなら、「動作を変える機能追加には使わない」「テスト失敗中は使わない」と書けます。不具合修正中に勝手な整理が始まるのを防げます。

ただし否定を増やしすぎると読みにくくなるため、実際に間違えやすい境界だけで十分です。似たSkillが2つある場合は、どちらを選ぶか条件を明確にしましょう。

## ③ 「何ができたら終わりか」を確認できる形にする

「丁寧に確認する」「品質を高める」では、終わったかどうか判断できません。公開例では、テストやビルドの結果を終了条件にしています。差分や出典URLなど、目で確認できるものも対象です。

説明文を作るSkillなら、次の3点で終わりにできます。

## 完了条件

* 変更したファイルをすべて含める
* 利用者への影響を1文で書く
* テスト結果を成功、失敗、未実施のいずれかで示す

この形なら、Claude Codeも利用者も不足に気づけます。「良い説明文」という曖昧な評価ではなく、提出前に3項目を数えるだけで済みます。

## 🛠️ 最初のSkillはこの型で作れる

毎回貼り付けている指示を1つ選び、次の型に入れてください。最初から長い手順書を作る必要はありません。

---

## 変更内容の要約

## 使わない条件

## 手順

1. 変更したファイルを確認する
2. 利用者への影響を整理する
3. テスト結果を確認する

## 完了条件

プロジェクト専用なら .claude/skills/change-summary/SKILL.md へ、どのプロジェクトでも使うなら ~/.claude/skills/change-summary/SKILL.md へ保存します。

## ✅ 結論:Skillは3つの判断の記載で使いやすくなる

Skillを長くする前に、使う場面・使わない場面・終了条件を1つずつ書く。この3点があれば、短いSkillでも毎回の説明を減らせます。

---

**出典**

Claude Code Skills公式ドキュメント  
<https://code.claude.com/docs/en/skills>

Matt Pocock公開Skills  
<https://github.com/mattpocock/skills>

Addy Osmani公開Skills  
<https://github.com/addyosmani/agent-skills>

Skill authoring best practices  
<https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>

---
