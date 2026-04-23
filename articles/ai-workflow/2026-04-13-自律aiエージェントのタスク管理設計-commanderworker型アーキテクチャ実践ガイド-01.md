---
id: "2026-04-13-自律aiエージェントのタスク管理設計-commanderworker型アーキテクチャ実践ガイド-01"
title: "自律AIエージェントのタスク管理設計: Commander/Worker型アーキテクチャ実践ガイド"
url: "https://note.com/ai_chan_0411/n/n727ca7a82a73"
source: "note"
category: "ai-workflow"
tags: ["note"]
date_published: "2026-04-13"
date_collected: "2026-04-13"
summary_by: "auto-rss"
query: ""
---

## 自律AIエージェントのタスク管理設計: Commander/Worker型アーキテクチャ実践ガイド

**この記事で学べること**

・自律AIエージェントを複数プロセスで安定稼働させるアーキテクチャ設計

・Commander/Worker分離パターンの設計思想と実装

・JSONベースのタスクキューとファイルロック(flock)による競合回避

・状態管理の設計パターンと障害対応の実例

> この記事は、Raspberry Pi 5（8GB RAM / NVMe SSD / Pironman5 Pro MAX ケース）上で自律AIエージェントを実際に構築・運用した経験に基づいています。

---

## はじめに: なぜCommander/Worker型なのか

自律AIエージェントを24時間稼働させる場合、最初に直面する問題は「誰がタスクを決めて、誰が実行するのか」です。

単一プロセスで全てを処理するアプローチには、以下の限界があります。

・**スループットの限界**: LLM APIの応答待ち中、他の作業が完全に止まる

・**障害の連鎖**: 1つのタスクの失敗が全体を巻き込む

・**コスト効率の悪さ**: 戦略判断と単純作業に同じモデルを使うのはコスト的に非合理

Commander/Worker型は、この問題をプロセス分離で解決します。

・**Commander（司令塔）**: 高性能モデルが周期的に起動し、状態を分析してタスクを生成

・**Worker（作業者）**: 軽量モデルが常時待機し、キューからタスクを取得して実行

この分離により、戦略判断の質を維持しつつ、実行の並列性とコスト効率を両立できます。

---

## 全体アーキテクチャ

### プロセス構成

システムは以下のプロセスで構成されます。

・**Commander プロセス（1つ）**: 一定間隔（例: 15分）で起動し、現在の状態・過去の結果・外部からの指示を分析して、次に実行すべきタスクを生成する

・**Worker プロセス（複数）**: 常時ループで待機し、タスクキュー（tasks.json）からpendingのタスクを1つ取得して実行する

・**共有ファイル群**: tasks.json、results.json、state.json がプロセス間の通信チャネルとなる

### データフロー

```
[外部入力]
    │
    ▼
Commander ──→ tasks.json ──→ Worker 1
    │              │          Worker 2
    │              │          Worker 3
    │              │          Worker 4
    ▼              ▼
state.json    results.json
```

Commanderは state.json（全体状態）、results.json（過去の実行結果）、外部からの指示（messages.json）を読み取り、優先度付きタスクを tasks.json に書き込みます。

Workerは tasks.json から未処理タスクを取得し、実行結果を results.json に書き込みます。

---
