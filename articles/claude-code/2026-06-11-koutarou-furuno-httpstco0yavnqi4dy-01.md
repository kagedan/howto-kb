---
id: "2026-06-11-koutarou-furuno-httpstco0yavnqi4dy-01"
title: "@koutarou_furuno: https://t.co/0YaVnqI4dY"
url: "https://x.com/koutarou_furuno/status/2065034757789073762"
source: "x"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "OpenAI", "x"]
date_published: "2026-06-11"
date_collected: "2026-06-17"
summary_by: "auto-x"
query: "RT @kagedan_3"
---

https://t.co/0YaVnqI4dY


--- Article ---
**「プロンプトを書くな。ループを書け」**

Peter Steinberger（OpenClaw創設者、現OpenAI）と、Boris Cherny（Anthropic Claude Code責任者）が、独立して同じことを言い始めた。

偶然じゃない。

地球上で最も重要な2つのAIラボのトップエンジニアが、同時に同じパターンに収束している。「流行の話」じゃなくて、**AIの使い方そのものが変わるシグナル**だと思う。

この記事は、そのシフトを整理したRahul（[@sairahul1](https://x.com/sairahul1/status/2064277888216555684)）のスレッドを元に、僕なりに整理し直したもの。

## プロンプト時代に何が起きていたか

2年間、みんなこれをやってきた。

あなた → プロンプト → AI → 出力 → あなたが確認 → 修正 → また入力

気づいてる人は多いと思うけど、**「ループしてるのは人間」**だった。

AIに一回聞いて、確認して、また聞いて、また確認する。「AIを使ってる」というより「AIと一緒に作業してる」に近い状態。

限界は明確。スケールしない（人間の時間が上限）、品質が人間のレビュー精度に依存する、夜中に動かせない。

![](https://pbs.twimg.com/media/HKge5wWbUAAutC6.jpg)

## Boris Chernyがやっていること

Claude Codeのヘッドが言った言葉をそのまま引用する。

> "I don't prompt Claude anymore. I have loops running that prompt Claude and figure out what to do. My job is to write loops."

「僕はもうClaudeにプロンプトを送ってない。ループが走っていて、そのループがClaudeに何をすべきか考えさせてる。僕の仕事はループを書くこと」

Peter Steinbergerも同じことをこう言った。

> "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents."

ここで止まって読んでほしい。

「指示を改善する」から「指示を出す仕組みを設計する」へ。**レイヤーが一段上がった。**

![](https://pbs.twimg.com/media/HKge8_-bMAAf5JK.jpg)

## ループエンジニアリングとは何か

シンプルに言うと：

**「エージェントが自分で発見→計画→実行→検証→修正を繰り返す仕組みを設計すること」**

5つのフェーズに分解するとこうなる。

DISCOVER（発見）

    ↓

PLAN（計画）

    ↓

EXECUTE（実行）

    ↓

VERIFY（検証）

    ↓

ITERATE（修正）

    ↓

クリアしたら完了 / 失敗したらDISCOVERに戻る

人間はゴールだけ決める。あとはループが回る。

![](https://pbs.twimg.com/media/HKgfAb-akAAwR1q.jpg)

## 2つのスケール：1人 vs チーム

ループには規模が2つある。

**① シングルエージェントループ**

1つのエージェントが自分で全サイクルを回す。「自分の下書きを自分で何度も直す人」のイメージ。スコープが小さく、集中した作業向き。

**② フリートループ（艦隊型）**

オーケストレーターが大きなゴールを持ち、そのゴールをスペシャリストに分解。スペシャリストはさらにサブエージェントに細分化する。

オーケストレーター（ゴール全体を管理）

       ↓              ↓              ↓

調査担当       開発担当       QA担当

  ↓              ↓              ↓

Web調査   コード書き+デバッグ   テスト+バグ追跡

全エージェントが同じ5ステージのループを回している。チームで一つのプロジェクトを動かすイメージ。

余談なんだけど、これよく「AIが勝手に何でもやってくれる」みたいな文脈で語られるんだよね。
実態は**「誰が何を見るかの設計が全部」**で、そこは人間がやらないといけない。ループを書ける人が強い理由がここにある。
