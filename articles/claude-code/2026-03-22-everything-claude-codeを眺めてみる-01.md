---
id: "2026-03-22-everything-claude-codeを眺めてみる-01"
title: "Everything Claude Codeを眺めてみる"
url: "https://oikon48.dev/ja/blog/everything-claude-code/"
source: "notebooklm"
category: "claude-code"
tags: ["everything-claude-code", "agents", "skills", "hooks", "security"]
date_published: ""
date_collected: "2026-03-22"
summary_by: "cowork"
---

## 概要

Anthropicハッカソン優勝者が公開した「Everything Claude Code（ECC）」リポジトリの構成と設計思想を解説。

## ECCの構成

| コンポーネント | 数量 | 内容 |
|---|---|---|
| ルール | 18+ | コーディング規約、セキュリティ、テスト等 |
| エージェント | 25個 | 設計、品質レビュー、実装支援等 |
| スキル | 108個 | ワークフロー定義（多言語対応） |
| コマンド | 57個 | スラッシュコマンド群 |
| フック | 23個 | セッション管理、品質管理等 |

**重要**: すべてをインストールする必要はなく、必要なものだけ選んでカスタマイズすべき。

## 主要な設計思想

1. **エージェントの役割分担**: 責務を明確に切り分け。機能追加は planner → tdd-guide → code-reviewer → security-reviewer の順。
2. **適切なモデル選択**: ほとんどのタスクはSonnetで十分（タスクのドメイン細分化で実行内容が明確）。
3. **短いDescription文**: 簡潔にすることでエージェント呼び出し確率が向上。

## 自動学習システム（Instinct Model）

- 記録段階: プロンプト・ツール使用・コンテキストを自動保存
- 分析段階: Haikuエージェントがパターン分析（バックグラウンド）
- 生成段階: confidence score付きinstinctファイルを生成
- 進化段階: `/evolve`でcommand・skill・agentを自動生成

## セキュリティ上の注意

- 複数チャネル統合は攻撃面の増加につながる
- 未監査のスキル導入はサプライチェーン攻撃の入口
- 自律エージェントにはsandbox・最小権限・監査ログが必須

## 著者の結論

ECCは「便利なコマンド集」ではなく「AIエージェント運用の設計思想集」として高い価値がある。
