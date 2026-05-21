---
id: "2026-05-20-zenn記事を生成するエージェントを5人作ったのに1本も動かなかった全員description欄が空-01"
title: "Zenn記事を生成するエージェントを5人作ったのに1本も動かなかった。全員description欄が空だった"
url: "https://zenn.dev/i_ichi/articles/agent-audit-invisible-servants"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-20"
date_collected: "2026-05-21"
summary_by: "auto-rss"
query: ""
---

「記事を書いてほしい」と Claude Code に頼んだ。

書いた。ただし、自分が用意したパイプラインを一切通らずに。

エージェントを設計していた。企画、査読、執筆、レビュー、最終チェック。Zenn 記事を一本仕上げるための専任チームだ。Claude Code はそれを無視した。

なぜかを調べた。

## Claude Code はdescriptionしか読まない

Claude Code のエージェントには重大な仕様がある。

**オーケストレーター（LLM）はエージェントを呼ぶとき、descriptionフィールドしか読まない。**

本文は読まない。どんなに詳細な手順書があっても、description が空なら、そのエージェントはオーケストレーターの視界に存在しない。「記事を書いてほしい」というリクエストが来ても、対応できるエージェントとして認識されないから、自分で処理する。

`~/.claude/agents/` を全棚卸しした。

```
## 棚卸し結果（32エージェント）

問題なし: 27件
descriptionなし: 5件
  - zenn-planner        （企画エージェント）
  - zenn-plan-reviewer  （企画レビュアー Review 1）
  - zenn-writer         （執筆エージェント）
  - zenn-article-reviewer（執筆レビュアー）
  - zenn-final-reviewer （最終ゲートレビュアー Review 3）
```

5人全員、Zennチームだった。

## パイプラインごと消えていた

5人は独立した個人ではない。直列につながった専任チームだ。

```
zenn-planner
  → zenn-plan-reviewer
    → zenn-writer
      → zenn-article-reviewer
        → zenn-final-reviewer
```

5人全員が description なし。パイプラインごとオーケストレーターに存在を認識されていなかった。

## 自分の環境で確認する

```
grep -rL "description:" ~/.claude/agents/
```

出力されたファイルが、オーケストレーターから見えていないエージェントだ。

## 直し方は一行

description を書く。それだけだ。実際に書いたものがこれ。

```
zenn-planner:
  Zenn記事の企画書を生成する。テーマ・事実情報を受け取り「誰に何を
  伝えてどう変えるか」を設計する。執筆はzenn-writerが担当 — 企画書のみ出力。

zenn-writer:
  Zenn tech記事の執筆エージェント。zenn-plannerの企画書を受け取り記事を
  生成する。企画・査読は別エージェントが担当 — 執筆のみ。

zenn-article-reviewer:
  Zenn記事草案を3ペルソナ（Reporter/Critic/Pragmatist）で査読する。
  書き直しはしない — 判定・指摘・改善例のみ出力。

zenn-final-reviewer:
  Zenn記事の公開前最終ゲート。リスク・事実確認・読者アクションを3ペルソナで
  鑑定する。修正指示は出さない — 人間への提示レポートのみ出力。
```

これを書いたら、「記事を書いてほしい」に zenn-planner が応答した。

当たり前のことが、まさかできていなかった。

## なぜ執筆はスキルではなくエージェントにしたのか

スキル（`commands/`）は現在の会話コンテキストで動く。今の会話履歴をそのまま引き継いで処理する。

エージェント（`agents/`）は独立したコンテキストで動く。メインの会話から切り離され、渡された情報だけで処理する。

Zenn記事を一本書くには、tone\_guide・style\_guide・企画書・過去記事を読み込んで、数千トークンの文章を生成する。これをスキルでやると、会話の全履歴と合算してコンテキスト窓が圧迫される。エージェントとして切り離せば、「企画書を渡す → 記事が返ってくる」で済む。メインの会話は汚れない。

スキルが向いているのは「今の会話の流れを参照しながら手続きをこなす」タスクだ。`/complete-task` が典型で、直前の作業内容を把握した上で Linear・Notion・Discord を一括処理する。会話文脈が必要だから、独立したコンテキストに切り出す意味がない。

**使い分けの基準：**

* 作業に「今の会話履歴」が必要 → スキル
* 作業に「渡した情報だけ」で足りる＋重い → エージェント

## 落ち

この記事は zenn-writer が書いていない。

Zenn記事を書く専門チームが動いていなかったから、この記事も彼らなしで書いた。description を書き終えた今、ようやく彼らは動ける。

次の記事は zenn-writer が書くかもしれない。
