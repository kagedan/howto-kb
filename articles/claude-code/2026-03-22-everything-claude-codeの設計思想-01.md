---
id: "2026-03-22-everything-claude-codeの設計思想-01"
title: "everything-claude-codeの設計思想 - 「考え方」をわかりやすく解説"
url: "https://zenn.dev/tmasuyama1114/articles/everything-claude-code-concepts"
source: "notebooklm"
category: "claude-code"
tags: ["everything-claude-code", "context-engineering", "agents", "skills", "hooks"]
date_published: ""
date_collected: "2026-03-22"
summary_by: "cowork"
---

## 核心

設計哲学は「コンテキストを最適化する」の一言に尽きる。AIに渡す情報を整理し、必要なときに必要なものだけ提供する仕組みづくりが本質。

## 5つの主要ポイント

### 1. 専門家チームの構築
一人で全部処理させるのではなく、特化したエージェントに役割分担。各エージェントには最小限のツールだけ付与。

### 2. マニュアル整備
rulesとskillsファイルで暗黙知を明文化。セキュリティチェック項目、コーディング規則、テスト要件を文書化し、毎回の説明手間を削減。

### 3. 自動化による確実性
hooksで特定イベント時に確実に実行される自動処理を実装。AIの判断に頼らず機械的に実行。

### 4. リソース管理
MCPを有効にしすぎるとコンテキストウィンドウが200kから70kに縮小する可能性。推奨: 設定で20〜30個、プロジェクトで10個以下、有効ツール80個以下。

### 5. コンテキストエンジニアリング
Anthropic社が提唱する概念の実践。プロンプトのみでなく、AIに渡す全情報を管理する戦略的アプローチ。

## 6つのファイルタイプ

| ファイル | 役割 |
|---|---|
| agents | 専門部署 |
| skills | 業務マニュアル |
| commands | ショートカット |
| rules | ポリシー・行動指針 |
| hooks | 自動チェック機構 |
| mcp-configs | 外部連携設定 |

## 導入のTips

- 段階的に導入する（一度に全部やらない）
- 最初の一歩はconsole.log警告フック（シンプルで効果的）
- 毎回の同じ指示→ルール化、繰り返しタスク→エージェント化、忘れがちなチェック→フック化

## 注意

設定が増えすぎるとコンテキストを逆に圧迫する。バランスが重要。
