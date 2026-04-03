---
id: "2026-04-02-github-copilotのskillmd育成rpg-lv0の村人がlv7の伝説の勇者になるまで鍛-01"
title: "GitHub Copilotの『SKILL.md育成RPG』— Lv.0の村人がLv.7の伝説の勇者になるまで鍛えたらコードレビューはどう変わるのか"
url: "https://qiita.com/yukurash/items/d8971bdf08f8416ad7dd"
source: "qiita"
category: "ai-workflow"
tags: ["AI-agent", "qiita"]
date_published: "2026-04-02"
date_collected: "2026-04-03"
summary_by: "auto-rss"
---

## 本記事について
AI Agent の Skill の必要性や重要性を学ぶため検証した内容になります。
検証した内容を AI が RPG 風にまとめてくれたので温かい目でお楽しみください。

## TL;DR
- バグ10個入りのコードを AI Agentにレビューさせた
- スキル（SKILL.md）を Lv.0 → Lv.7 まで段階的に強化して精度を比較
- Lv.0 でも 9/10 検出できるが、出力がバラバラで実用しづらい
- **Lv.5（出力テンプレート追加）で全件検出＋構造化レポートを達成**  ← 最大の転換点
- Skill vs Instructions の比較もまとめたので、使い分けに迷っている人もぜひ

おまけとして Skill vs Instructions の比較表 も載せています。


---

## はじめに 

最近は「AI Agentすごい！」と「いや意外と微妙…」の声が同時に飛び交ってますよね。同じAIなのに、なぜ人によって評価が割れるのか？

答えはシンプルでした。**勇者（エージェント）に渡す装備（スキル）の育て方が違う**。

前回の記
