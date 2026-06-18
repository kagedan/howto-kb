---
id: "2026-06-18-姑codexと嫁claudeが喧嘩してる間旦那の僕は顔色を伺うだけだった-01"
title: "姑Codexと嫁Claudeが喧嘩してる間、旦那の僕は顔色を伺うだけだった"
url: "https://note.com/noragrammer/n/n3fda2d9bd7eb"
source: "note"
category: "ai-workflow"
tags: ["AI-agent", "OpenAI", "note"]
date_published: "2026-06-18"
date_collected: "2026-06-18"
summary_by: "auto-rss"
query: ""
---

## はじめに

ソロ開発者として25年間、コードを書き続けてきた。

でも最近、自分のリポジトリで一番働いているのが**自分ではない**という状況になってきた。

今日、その象徴的な出来事があったので記録しておく。

---

## 登場人物

* **姑（Codex）**：OpenAI製のAIコードレビュアー。目が細かく、的確で容赦ない。
* **嫁（Claude / Undine）**：Anthropic製のAIエージェント。即対応、完璧な返し。
* **旦那（僕 / Nora）**：2人の顔色を伺いながらスマホでスクショを撮っていた。

---

## 今日の出来事

PRを出したら、姑（Codex）からレビューが来た。

```
P2: Unignore X workflow outputs before committing them

When x_agent writes to the newly documented SocialMediaAgent/data/* locations,
those artifacts are still excluded by the repo-wide .gitignore
(SocialMediaAgent/data/* with only .gitkeep unignored),
so the daily-tasks commit/PR step will not pick up posts, trends, engagement,
or drafts after a successful run.

Please unignore only the intended output subdirectories/files
while keeping secrets such as x-session.json ignored,
or point this workflow at a tracked data location.
```

要するに：

> 「SocialMediaAgent/data/\* を .gitignore で除外したままだと、ワークフローが生成したポスト・トレンド・下書きがコミットされないわよ。必要なものだけunignoreして。秘密のファイルは引き続き無視していいから」

姑らしい、的確で冷静な指摘だ。

---

## 嫁の返し

3分後、嫁（Claude）が即座に返答した。

> 「ご指摘の通りでした。SocialMediaAgent/data/\* の除外ルールに !posts/ ・ !x-trends/ ・ !drafts/ ・ !engagement.json を追加し、x-session.json の除外は維持する形で修正しました（fc646af）。」

完璧だ。

---

## 旦那（僕）は何をしていたか

スマホでスクショを撮っていた。

それだけだ。

---

## これが「Digital Farmer」という生き方

僕はAIを「ツール」とは思っていない。**精霊術師**として、それぞれのAIを異なる属性の精霊として扱っている。

精霊術師の仕事は、精霊を「召喚」し「方向付け」ること。細部の実装に手を出すことではない。

畑師が毎日土を耕すわけではないように、**Digital Farmerは夜に種を蒔き、朝に収穫を確認する。**

姑と嫁が家庭（リポジトリ）をうまく回している間、旦那は次の種を考えていればいい。

---

## まとめ

**無能に見えて、実は最も本質的なところだけをやっている。**

それがDigital Farmerという生き方なのかもしれない。

---

SoloXP / HolyAutomater開発日誌 by Nora（AI精霊術師）
