---
id: "2026-04-10-claude-managed-agentsのアーキテクチャと既存エージェント実行環境との技術比較-01"
title: "Claude Managed Agentsのアーキテクチャと既存エージェント実行環境との技術比較"
url: "https://qiita.com/tatematsu-k/items/dce3ce5252e24c4585bd"
source: "qiita"
category: "ai-workflow"
tags: ["API", "AI-agent", "qiita"]
date_published: "2026-04-10"
date_collected: "2026-04-10"
summary_by: "auto-rss"
query: ""
---

## TL;DR

- Claude Managed Agentsは2026年4月8日にパブリックベータとして公開された、エージェント実行基盤のマネージドサービス
- 既存のフレームワーク（LangGraph、CrewAI、Dify等）とは異なり、**モデル＋ハーネス（制御ループ）＋サンドボックス＋セッション永続化がAPI一つで提供される垂直統合アーキテクチャ**
- 内部アーキテクチャはSession / Harness / Sandboxの3コンポーネントに分離されており、エンジニアリングブログで設計が公開されている
- 課金モデルはアクティブ実行時間のみの従量課金（$0.08/時間、アイドル無料）

## はじめに

この記事では、AIエージェントの実行環境を5つのカテゴリに分類し、それぞれのアーキテクチャ・組み込み機能・課金モデルを技術的な観点で比較する。

対象読者はAIエージェントの本番運用を検討しているエンジニア。各実行環境の公式ドキュメントおよびエンジニアリングブログに基づく事実ベースの比較とする。

## エージェント実行環境の分類

AIエージェントの実行には、LL
