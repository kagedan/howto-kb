---
id: "2026-06-22-loop-engineering入門ai-agentを完了まで自律走行させるoss-01"
title: "Loop Engineering入門：AI Agentを完了まで自律走行させるOSS"
url: "https://zenn.dev/tackeyy/articles/e72211a1a49609"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "zenn"]
date_published: "2026-06-22"
date_collected: "2026-06-23"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/a6ca61998b1d-20260621.png)

## TL;DR

Prompt engineeringが「AIに何を頼むか」だとすれば、loop engineeringは「AIが完了まで進み続ける仕組みをどう設計するか」です。  
`mission`は、そのためのClaude Code / Codex向けOSSです。計画、実行、レビュー、採点をloopし、品質ゲートを通るまでAIが「終わったふり」で止まらないようにします。

Claude Codeにはすでに`/goal`があります。`/goal`は「この条件を満たすまで続ける」ための軽量なcompletion conditionとして便利です。一方で`mission`は、より重い複数ステップ作業向けに、`.mission-state`、レビュー、採点、score history、threshold gateを持つcompletion layerとして作っています。  
つまり、短い作業なら`/goal`で十分です。調査、実装、レビュー、修正、リリース準備のように「なぜ止まってよいのか」を後から説明したい作業では、`mission`のようなstatefulな品質ゲートが効きます。  
また、単に「loopさせる」だけならpromptを再投入したり、while的にagentを回したりすることでも実現できます。ただし、それだけでは各iterationの状態、レビュー結果、採点根拠、停止条件が曖昧になりがちです。`mission`はloopそのものではなく、loopを安全に止めるための状態管理と品質ゲートを提供します。

GitHub: <https://github.com/tackeyy/mission>

## 想定読者

* Claude Code / Codexを使っているが、毎回promptで頑張っている人
* AIに調査、実装、リリース、ドキュメント更新などの複数ステップ作業を任せたい人
* AI Agentが途中で満足して止まる、検証せず完了報告する、という問題に不満がある人

## 導入

AIに仕事を任せる時、難しいのは「最初のprompt」だけではありません。  
むしろ実務で困るのは、その後です。AIは途中まで進めて、もっともらしい完了報告を出します。しかし、テストが未実行だったり、レビュー指摘が残っていたり、ドキュメント更新が抜けていたりします。  
この問題に対する次の設計単位が **loop engineering** だと考えています。  
Prompt engineeringが「AIに何を頼むか」だとすれば、loop engineeringは「AIが完了まで進み続ける仕組みをどう設計するか」です。

## 何が問題か

単発promptは、複数ステップの仕事に弱いです。

* 計画がない
* 途中の状態が残らない
* レビューが自己申告になる
* 採点基準が曖昧
* いつ止まってよいかが曖昧

結果として、AIは「終わったように見えるところ」で止まります。  
でも、実務で必要なのは「終わった感じ」ではなく「止まってよい根拠」です。

## missionとは

`mission`はClaude Code / Codex向けのOSS loop engineering pluginです。  
やることはシンプルです。

```
plan -> execute -> review -> score -> iterate
```

計画し、実行し、レビューし、採点し、品質ゲートを通らなければ次のiterationに進みます。  
`mission`は、agentが止まる前に以下を要求します。

* stateが残っていること
* reviewer / scorer phaseを通っていること
* score historyが記録されていること
* thresholdを超えていること

## `/goal`や単純なprompt loopと何が違うか

`/goal`は軽量なcompletion conditionとして便利です。単一セッションで「この条件を満たすまで続けて」という用途に向いています。  
一方で`mission`は、もう少し構造化されたcompletion layerです。`.mission-state`、review loop、score history、threshold gateを持ち、複数ステップの仕事で「なぜ止まってよいのか」を説明できるようにします。  
単純なprompt replay loopは、同じpromptを再投入できます。ただし、計画、レビュー、採点、状態管理がなければ、結局「何をもって完了とするか」が曖昧なままです。

## 使いどころ

`mission`が向いているのは、早く止まりすぎることが主なリスクの作業です。

* issue修正からテスト、PR準備まで任せる
* 調査、要約、ドキュメント化まで任せる
* リリース前チェックを漏れなく回す
* 長い作業をcompaction / resumeをまたいで継続する

逆に、1問1答の短い作業には過剰です。

## なぜOSSにしたか

Loop engineeringは、個人のprompt技術というより、共有できるworkflowの設計に近いです。  
どのphaseを入れるべきか。レビューは何人がよいか。採点はどう記録するか。どこで止めるか。これらはrepoとして改善できる対象です。  
`mission`は、その実験場として作っています。

## 試してほしいこと

Claude CodeまたはCodexで、いつもなら途中で止まりがちな複数ステップの仕事を`mission`に渡してみてください。

例:

```
/mission READMEの導入を改善し、テストとリンク確認まで行って
```

もしloop engineering、agent workflows、skills、plugins、sub-agentsに関心があれば、GitHubでstarしてフィードバックをもらえるとうれしいです。

GitHub: <https://github.com/tackeyy/mission>
