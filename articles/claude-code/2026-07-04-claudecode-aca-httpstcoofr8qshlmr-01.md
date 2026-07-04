---
id: "2026-07-04-claudecode-aca-httpstcoofr8qshlmr-01"
title: "@ClaudeCode_aca: https://t.co/OFr8QsHlMr"
url: "https://x.com/ClaudeCode_aca/status/2073329744888918394"
source: "x"
category: "claude-code"
tags: ["claude-code", "AI-agent", "x"]
date_published: "2026-07-04"
date_collected: "2026-07-05"
summary_by: "auto-x"
query: "Claude Code hooks 使い方 OR subagents 設定 OR Claude Code スケジュール"
---

https://t.co/OFr8QsHlMr


--- Article ---
Claude Code アカデミアです。

AIエージェント開発に2,000時間以上を費やしたガチ勢のみで運営しています。

![](https://pbs.twimg.com/media/HMXxCOqaQAAQENl.jpg)

**Claude Codeを極めたい方は、フォロー (**@ClaudeCode_aca **)しておいてください。  **

**無料公式LINEは[こち**ら](https://utage-system.com/line/open/wcoIZQB0rwv3?mtid=1U5McDifKcjO)

では本題です。

**Fable 5の性能を120%引き出すノウハウを解説します。**

Fable 5の本領は**「放置」**にあります。

/loopと/skillを組み合わせた瞬間——AIが自律的に動き続ける。

自分で判断し、自分で検証する仕組みが完成します。

海外では**Loop Engineering**という新しいパラダイムが生まれました。

プロンプトを設計する時代から、ループを設計する時代へ。

この記事では、2,000時間以上の実践から辿り着いた設定を全部出します。

/loop × /skillの具体的な構成をそのまま公開します。

# ■ Loop Engineering——「プロンプト」の次に来た概念

![](https://pbs.twimg.com/media/HMXwbsbbYAAB1Cb.jpg)

2026年6月、Googleの開発者アドボケイトAddy Osmaniが名付けました。
**Loop Engineering**——ループを設計する新パラダイムです。

## ▍ 従来のAI活用とは根本的に違う

従来のAI活用はこうでした。

1. 人間がプロンプトを書く

2. AIが回答する

3. 人間が確認する

4. また書く——この繰り返し

Loop Engineeringはこの構造を壊します。

**人間がループを設計する。AIが自律的に繰り返す。人間は結果だけ受け取る。**

僕はこの違いに気づいた瞬間に変わりました。

## ▍ なぜFable 5でこの話が爆発しているのか

**Fable 5以前のモデルでは、自律ループが実用レベルに達していませんでした。**
僕も過去に試しました。途中で文脈を見失って暴走するのがオチでした。

Fable 5は違います。

- 100万トークンのコンテキストを最後まで正確に記憶する
- 長時間の自律実行で「嘘の完了報告」を防ぐ仕組みが入っている
- サブエージェントを積極的に並列起動して効率を上げる
- メモリで学習を蓄積し、回を追うごとに精度が上がる
**Loop Engineeringを現実にできる最初のモデルです。**

## ▍ 6つの構成要素

|  要素 | 役割  |
| --- | --- |
|  Automations |   自動起動|
|  Worktrees |  ファイル衝突回避 |
| Skills  |  指示セット保存 |
| Connectors  |  外部ツール統合 |
| Sub-agents  |   検証用独立エージェント|
|  Memory | セッション間記憶  |

**このうち/loopと/skillの2つだけで今日から始められます。**
僕はこの2つから入って、今では全6要素をフル活用しています。

> **👉 Claude Codeを極めたい方は、**[@ClaudeCode_aca](https://x.com/@ClaudeCode_aca) **をフォロー！  

👉 無料公式LINEは[こち**ら](https://utage-system.com/line/open/wcoIZQB0rwv3?mtid=1U5McDifKcjO)

# ■ /loopコマンド完全解説——「3つのモード」を使い分けろ

![](https://pbs.twimg.com/media/HMXwfYKbMAAGFu6.jpg)

/loopはClaude Codeの**組み込みスキル**です。
セッション中にプロンプトを自動で繰り返します。

知らない人がマジで多いんですが——**3つのモードがあります。**

- **固定間隔**: 「5分ごとに確認」のような定期監視
- **動的間隔**: AIが状況を見て待機時間を判断
- **メンテナンス**: 放置するだけでPRケアやバグハントを自動実行
僕の感覚だと、7割の人がモード①しか知りません。

## ▍ モード①: 固定間隔—
