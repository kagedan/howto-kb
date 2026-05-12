---
id: "2026-05-11-microsoftwaza-01"
title: "microsoft/waza"
url: "https://zenn.dev/nobmake/articles/c38486b9c250c0"
source: "zenn"
category: "ai-workflow"
tags: ["prompt-engineering", "LLM", "zenn"]
date_published: "2026-05-11"
date_collected: "2026-05-12"
summary_by: "auto-rss"
query: ""
---

## 🥋 何者か？

**Waza**（技）は Microsoft が開発した **AIエージェント「スキル」の評価・ベンチマーク専用の Go 製 CLI** です。

> *"The way of technique — measure, refine, master"*

2026年2月に公開されたばかりのプロジェクト（スター約578）で、GitHub Copilot のような AI エージェントに組み込む  
「スキル（特定タスクを実行する専門モジュール）」の品質を体系的に計測・改善するためのフレームワークです。

---

## 🎯 主な機能

| コマンド | 説明 |
| --- | --- |
| `waza init` | プロジェクトワークスペースを初期化。`skills/` と `evals/` を分離管理 |
| `waza new skill` | スキルの雛形（SKILL.md + eval スイート）を自動生成 |
| `waza new eval` | 既存の SKILL.md から評価スイートを自動スキャフォールド |
| `waza new task from-prompt` | プロンプトを実際に流してその挙動からテスト YAML を自動生成 |
| `waza run` | YAML 定義の評価ベンチマークを実行（並列・キャッシュ・複数モデル対応） |
| `waza compare` | 異なるモデル間の結果を横断比較 |
| `waza grade` | 実行済みの結果を後からグレーディング |
| `waza check` | スキルが提出基準を満たしているか検証 |
| `waza coverage` | eval カバレッジグリッドを生成 |
| `waza tokens` | スキルのトークン消費量を分析・最適化提案 |

### バリデータ（11種類）

コード検証・正規表現・JSON スキーマ・LLM-as-Judge・スナップショット差分 など、  
柔軟な合否判定ルールを組み合わせ可能。

### CI/CD 統合

`waza init` 実行時に `.github/workflows/eval.yml` が自動生成され、  
**PR ごとに eval が自動実行**される。

---

## 🆚 従来手法との比較・メリット

従来：  
手動でプロンプトを送って目視確認  
→ 再現性なし・属人的・モデル切り替えのたびに一から確認

Waza：  
YAML で評価を定義 → CI が自動実行 → 結果を数値で比較  
→ 再現可能・バージョン管理可能・モデル間差異が定量的にわかる

| 課題（従来） | Waza の解決策 |
| --- | --- |
| スキルの品質が属人的・目視頼み | YAML ベースのテストスイートで標準化 |
| どのモデルが最適か比較できない | `waza compare` で複数モデルの結果を横断評価 |
| 改修のたびに手動確認が必要 | CI/CD 統合で PR ごとに自動 eval |
| スキル開発のスタート地点がバラバラ | `waza new skill` でスキャフォールド一発生成 |
| 「良いスキル」の基準が曖昧 | `waza check` でサブミット基準を自動チェック |
| テスト作成が手間 | `from-prompt` でプロンプト実行から自動的にテスト YAML を生成 |
| A/B テストが困難 | `--baseline` フラグでスキルあり/なしの改善スコアを自動算出 |

---

## 🏗️ 対象ユーザー

* **スキル作成者** — GitHub Copilot などに組み込む専門スキルを開発するエンジニア
* **プラットフォームチーム** — 複数スキルの品質を一元管理したいチーム
* **研究者** — 複数のモデルを同一条件で評価したい人

---

## まとめ

> **「AI スキルの単体テスト + CI/CD パイプライン」を丸ごと提供するフレームワーク。**  
> 手動・目視・属人的だったスキル評価を、YAML 定義 + 自動化 + 数値比較に置き換えるのが最大の革新点。
