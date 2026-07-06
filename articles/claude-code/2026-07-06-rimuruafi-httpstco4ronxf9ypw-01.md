---
id: "2026-07-06-rimuruafi-httpstco4ronxf9ypw-01"
title: "@rimuruafi: https://t.co/4ROnxf9Ypw"
url: "https://x.com/rimuruafi/status/2074220998275301483"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "OpenAI", "x"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/4ROnxf9Ypw


--- Article ---
皆さんCodex使ってて、Skillsって多すぎてどれから入れればいいか迷いますよね😱

大丈夫です。この記事で全部整理します。最後まで読んでいただければ、あなたのCodexが今日から別物になることをお約束します🔥

ところで、Codex普段使っててこんな悩みありませんか？

**・Codex CLIを使ってるけど、毎回同じ前提説明を繰り返してる
・Skillsという機能があるのは知ってるけど、何を入れればいいかわからない
・設計→開発→テスト→ドキュメントの流れをまとめて自動化したい
・Codexを「ただのコード生成器」以上に使いこなしたい**

2025年12月、OpenAIはCodex CLIとIDE拡張の両方でSkills機能を正式リリースしました。それまでのCustom Promptsは廃止され、すべてSkillsに統一されています。 

つまり今、Codex Skillsを整えてるかどうかが、生産性の差そのものになってます。

今回はその中身をわかりやすく整理して、副業・受託・プロダクト開発でそのまま使えるSkills 30選を紹介します👇

## ■ そもそもCodex Skillsとは何か

ほとんどの人はCodexを「その場で指示して、答えを受け取って終わり」で使っています。

でもCodexには「Skills」という仕組みがあります。これを使うと、Codexは設計者・レビュアー・デバッガー・ドキュメントライターを兼ねた「開発チーム」として機能します。

Skillは、SKILL.mdという必須ファイルと、scripts・references・assetsという任意フォルダで構成されます。SKILL.mdには「特定の作業をどう進めるか」がステップバイステップで書かれていて、実行スクリプトやテンプレートも同梱できます。 [Vibe Coding Gallery](https://vibecoding.gallery/en/tools/openai-codex-cli/)

一度Skillとして入れておけば、毎セッションで同じ指示を繰り返す必要がなくなります。

インストールと呼び出し

Codexにはあらかじめキュレーションされた基本Skill群があります。$skill-installer を実行すると、OpenAI公式のワークフローに沿ったSkillが一括で導入されます。 [Vibe Coding Gallery](https://vibecoding.gallery/en/tools/openai-codex-cli/)

呼び出し方は2通り。

- **明示的に：$skill-name と打てば、そのSkillが起動します**
- **自動選択：普通にプロンプトを投げると、タスクに合ったSkillをCodexが自分で選びます**
Codex Skillsは、Claude Skillsとほぼ同じ設計

これ、意外と知られてません。

Codex SkillsとClaude Skillsは、両方とも「開いたAgent Skills標準」に沿って作られています。だから多くのSkillは、Codex・Claude Code・GitHub Copilotで共通して使えます。

つまり、GitHubで公開されているClaude Skillsも、そのままCodexで動きます。

これが今回、Codex Skillsを一気に揃えられる最大の理由です。

## ■ Meta Skills ── まず最初に入れるべき「スキルを作るスキル」

他のすべてのSkillの土台になるのが、Meta Skillsです。

**①Skill Installer**

OpenAI公式がキュレーションしたSkill群を一括インストールする、公式のインストーラーSkill。最初にこれを打つだけで、Codexが「素のCLI」から「セットアップ済み開発環境」に変わります。 [Vibe Coding Gallery](https://vibecoding.gallery/en/tools/openai-codex-cli/)

呼び出し：$skill-installer

**②Skill Creator**

あなたのタスクからSKILL.md案を提案してくれるSkill。

使い方：やってるワークフローを箇条書きで説明 → SKILL.md案を提案させる → 3〜5回テストして失敗を分析 → 改善させる

一度これを回すと「毎回説明してた作業」が消えます。

**③Create Plan（experimental）**

Codexにexperimentalと
