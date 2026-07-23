---
id: "2026-07-24-aiエージェント設計完全ガイド①-graph-engineering入門-01"
title: "AIエージェント設計完全ガイド①-Graph Engineering入門"
url: "https://qiita.com/miyaguchi_kioku/items/9ae9d000049641beacbe"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "AI-agent", "OpenAI", "GPT", "qiita"]
date_published: "2026-07-24"
date_collected: "2026-07-24"
summary_by: "auto-rss"
query: ""
---

## Prompt EngineeringからAgent Engineeringへ ― AI開発は新しい時代に入った

> 「AIに良いプロンプトを書けば十分」
>
> 半年前までは、それでも十分でした。
>
> しかし2026年現在、AI開発の中心は**AIエージェント**へ移りつつあります。

この記事では、AIエージェント開発の全体像を体系的に解説します。

本シリーズでは以下の流れで解説していきます。

1. Prompt Engineering
2. Loop Engineering
3. Agent Engineering
4. Graph Engineering
5. Claude Code Dynamic Workflows

この記事はその第1回です。

---

# AI開発は4つの時代に分けられる

私は現在のAI開発を次の4つの世代に分類しています。

```text
Prompt Engineering
        │
        ▼
Loop Engineering
        │
        ▼
Agent Engineering
        │
        ▼
Graph Engineering
```

それぞれ何が違うのでしょうか。

---

# 第1世代 Prompt Engineering

ChatGPTが登場した頃は、

**AIにどう指示を書くか**

がすべてでした。

例えば

```text
英語を日本語へ翻訳してください。

専門用語は残してください。

Markdownで出力してください。
```

このようなプロンプトを書くだけで、

AIの性能は大きく変わりました。

そのため

Prompt Engineering

という言葉が生まれました。

---

## Prompt Engineeringの限界

しかし、

次のような仕事はどうでしょう。

- Web検索
- PDF解析
- ソースコード解析
- レビュー
- 修正
- テスト
- ドキュメント作成

これらを

**一回のプロンプト**

だけで行うのは困難です。

例えば

```
調査して
↓
考察して
↓
コードを書いて
↓
レビューして
↓
修正して
```

というように、

複数の工程があります。

ここでPromptだけでは限界が見えてきました。

---

# 第2世代 Loop Engineering

そこで登場したのが

Loop Engineering

です。

つまり

AIが

「考える」

ことを繰り返します。

```text
考える

↓

回答する

↓

自己評価

↓

改善する

↓

再回答
```

これを何度も繰り返します。

---

## Reflection

代表例が

Reflection

です。

例えば

```
このコードを書いてください。
```

ではなく

```
コードを書いてください。

そのあと

問題点を自分で探してください。

改善してください。
```

という流れです。

つまり

AI自身がレビューします。

---

## Retry

一度失敗したら

もう一度挑戦します。

```
回答

↓

失敗

↓

改善

↓

再実行
```

単純ですが、

精度は大きく向上します。

---

## Memory

さらに

前回の失敗

前回の成功

を覚えておきます。

すると

同じ失敗を繰り返しません。

---

# 第3世代 Agent Engineering

Loopだけでも

かなり賢くなります。

しかし

まだ問題があります。

一人で全部やっています。

例えば

```
調査

↓

コード作成

↓

レビュー

↓

資料作成
```

全部

一人で担当しています。

人間ならどうでしょう。

会社では

営業

経理

設計

品質保証

それぞれ担当者がいます。

AIも同じです。

---

# AIエージェントとは

AIエージェントとは

**役割を持ったAI**

です。

例えば

```
Planner
```

仕事を分解します。

---

```
Researcher
```

情報を集めます。

---

```
Coder
```

プログラムを書きます。

---

```
Reviewer
```

コードをレビューします。

---

```
Writer
```

文章を書きます。

---

これらを組み合わせることで、

一つのAIより

高品質な成果が得られます。

---

# マルチエージェント

さらに

複数のAIを

協力させます。

```
        Planner
           │
    ┌──────┴──────┐
    ▼             ▼
Researcher    Researcher
    │             │
    └──────┬──────┘
           ▼
        Reviewer
           │
           ▼
        Reporter
```

これは

会社の組織

とよく似ています。

---

# なぜAgentが必要なのか

理由は単純です。

専門家は

専門家の仕事だけした方が

強いからです。

例えば

税理士に

デザインを頼みません。

デザイナーに

決算書を書いてもらいません。

AIも同じです。

役割を分けることで

品質が向上します。

---

# しかしAgentにも限界がある

ここまでで

かなり賢くなりました。

しかし

まだ問題があります。

例えば

```
Planner

↓

Research

↓

Review

↓

Report
```

これは

一本道です。

Researchが終わるまで

Reviewは待っています。

本当に待つ必要があるのでしょうか。

実は

待たなくてもよい仕事が

たくさんあります。

ここで登場するのが

**Graph Engineering**

です。

次回は

AIエージェントを

一直線ではなく

グラフとして設計する

Graph Engineering

について解説します。

---

# まとめ

AI開発は

```
Prompt

↓

Loop

↓

Agent

↓

Graph
```

という進化を続けています。

これからは

**プロンプトを書く技術**

だけではなく

**AIエージェントを設計する技術**

が重要になります。

さらにその先では

複数のAIエージェントを組み合わせる

**Graph Engineering**

が中心になっていくでしょう。

---

## 次回予告

次回は

**Graph Engineering入門**

として、

- Node
- Edge
- Parallel
- Fan-out
- Fan-in
- Pipeline

などを図を使ってわかりやすく解説します。

---

シリーズ

- **第1回：Prompt EngineeringからAgent Engineeringへ（この記事）**
- 第2回：Graph Engineering入門
- 第3回：Graph Engineering実践
- 第4回：Claude Codeで実践するDynamic Workflows
- 第5回：OpenAI Agents SDK・LangGraph・Google ADK比較
- 第6回：Monadoで作るAgent Operating System
- 第7回：AIエージェント実践事例
