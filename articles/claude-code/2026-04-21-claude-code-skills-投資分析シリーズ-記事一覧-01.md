---
id: "2026-04-21-claude-code-skills-投資分析シリーズ-記事一覧-01"
title: "Claude Code Skills × 投資分析シリーズ — 記事一覧"
url: "https://zenn.dev/okikusan/articles/23041c3800a927"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "zenn"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-rss"
---

Claude Code Skills を使って投資分析システムを構築・進化させてきたシリーズです。自然言語で話しかけるだけで、銘柄探索・分析・ポートフォリオ管理・リスク評価が自動実行されます。

## シリーズの流れ

スクリプトによる **自動化** から始まり、GraphRAG による **学習**、高度な分析機能の追加を経て、最終的に6つの AI エージェントが自律的に連鎖する **マルチエージェントオーケストレーション** に到達しました。

## 記事一覧

### Vol.1: 株スクリーニングを自動化した話

**テーマ**: スクリプトで **自動化**

Python × yfinance × Claude Code Skills で、株式スクリーニングからポートフォリオ管理まで投資分析を自動化。4つのスクリーナーエンジンとヘルスチェック機能を実装。

<https://zenn.dev/okikusan/articles/eacc59ca26e566>

---

### Vol.2: 使うほど賢くなる投資分析AI

**テーマ**: GraphRAG で **学習**

Neo4j ナレッジグラフを導入し、過去の分析・売買・投資メモを蓄積。使うほど文脈を踏まえた判断ができるようになる仕組み。

<https://zenn.dev/okikusan/articles/37dfaec84afec2>

---

### Vol.3: 処方箋エンジン・逆張り検出・銘柄クラスタリング

**テーマ**: 分析機能を **高度化**

PF処方箋エンジン、逆張りシグナル検出、コミュニティベースの銘柄クラスタリングなど7つの新機能を追加。

<https://zenn.dev/okikusan/articles/655df6dd36dfd4>

---

### Vol.4: ゼロから再設計。マルチAIエージェントが自律的に動く投資アシスタントに【最新】

**テーマ**: Agentic AI Pattern で **自律化**

Vol.1〜3 の構造を全て捨て、6つの AI エージェント（Screener / Analyst / Health Checker / Researcher / Strategist / Reviewer）が連鎖して自律的に動くマルチエージェントオーケストレーションに完全リニューアル。マルチLLM（GPT / Gemini / Grok / Claude）によるレビュー、自律修正ループ、DeepThink（Evaluator-Optimizer パターン）、GraphRAG による文脈注入を実装。

<https://zenn.dev/okikusan/articles/2a3ec2999d6581>

## リポジトリ

### Vol.4（現行）

Vol.4 で完全リニューアルしたため、新しいリポジトリとして公開しています。

<https://github.com/okikusan-public/stock_skills_2>

```
.claude/
  skills/stock-skills/   — SKILL.md（オーケストレーター）+ routing.yaml + orchestration.yaml
  skills/deepthink/      — DeepThink（Evaluator-Optimizer 自律深掘り）
  agents/                — 6エージェント（agent.md + examples.yaml）
tools/                   — 8ツール（Yahoo Finance / Grok / GraphRAG / LLM / notes / portfolio_io / watchlist / cash_balance）
src/data/                — 内部実装（yahoo_client / grok_client / graph_query / graph_store）
config/                  — 設定（llm_capabilities.yaml / exchanges.yaml / themes.yaml）
```

### Vol.1〜3（旧リポジトリ）

<https://github.com/okikusan-public/stock_skills>

## 技術スタック

* **ランタイム**: Claude Code（Claude Opus 4.6）
* **外部LLM**: GPT-5.4（OpenAI）、Gemini 2.5 Flash（Google）、Grok 4（xAI）
* **データ取得**: yfinance（Yahoo Finance API）
* **リアルタイム情報**: Grok API — X センチメント・ニュース、Gemini Grounding — Google検索
* **ナレッジグラフ**: Neo4j（GraphRAG）
* **言語**: Python 3.10+

---
