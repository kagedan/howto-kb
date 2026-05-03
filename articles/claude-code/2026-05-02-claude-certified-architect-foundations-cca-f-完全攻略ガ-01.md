---
id: "2026-05-02-claude-certified-architect-foundations-cca-f-完全攻略ガ-01"
title: "Claude Certified Architect - Foundations (CCA-F) 完全攻略ガイド"
url: "https://zenn.dev/acntechjp/articles/40f3ff24064968"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "CLAUDE-md", "MCP", "prompt-engineering", "API", "AI-agent"]
date_published: "2026-05-02"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

## はじめに

3月にAnthropic社が初のAI資格試験を公開しました。

その対策ロードマップを自分用にまとめましたので、皆さんにも向けて公開します。

こちらの内容で私が学習を進めてみます。実際合格できたらその体験記も別記事で書こうと思います。

## 1. 資格の階層構造

```
        CCA-F（プロクター試験）← 720/1000で合格、2年更新、$99
           ↑
    Academy修了証群 ← 各コース完了で発行、無期限、無料
```

CCA-Fは Academy修了証とは別物。Academyのコース群はCCA-F試験範囲を  
カバーする"準備教材"の位置づけ。コース修了だけでは合格には不十分で、  
本番想定の実装経験が必要。

---

## 2. 試験フォーマット

| 項目 | 内容 |
| --- | --- |
| 形式 | 選択式、シナリオベース（定義問題なし） |
| 問題数 | 60問 |
| 合格点 | 720 / 1000 |
| 受験 | オンライン・プロクター付き、自宅可、結果即時通知 |
| 試験料 | $99（約15,000円） |
| 有効期限 | 半年 |
| 想定経験 | Claude API・Claude Codeで6ヶ月以上の実務経験（"301レベル"） |
| 受験資格 | Claude Partner Network経由でアクセスリクエスト |

**出題思想：不正解選択肢は「本番でやらかしがちなアンチパターン」**  
で構成される。一見正しく見えて本番で壊れる選択肢を見抜く能力が問われる。

---

## 3. 5ドメイン × 6シナリオ構造

### 5ドメイン（配点）

| # | ドメイン | 配点 | 主要トピック |
| --- | --- | --- | --- |
| 1 | Agentic Architecture & Orchestration | 27% | マルチエージェント設計、ハブ&スポーク、agentic loop、タスク分解、サブエージェント |
| 2 | Claude Code Configuration & Workflows | 20% | CLAUDE.md階層、パススコープルール、カスタムスラッシュコマンド、Skills、hooks、CI/CD統合 |
| 3 | Tool Design & MCP Integration | 18% | MCPサーバー設計、tool boundary、tool schema、推論負荷最適化、構造化エラーレスポンス |
| 4 | Prompt Engineering & Structured Output | 20% | Few-shot、JSONスキーマベースのtool use、バリデーション・リトライループ |
| 5 | Context Management & Reliability | 15% | コンテキスト劣化防止、エスカレーション設計、エラー伝搬、HITL、プロンプトキャッシュ |

### 6シナリオ（4つがランダム出題、6つ全部対策必須）

1. Customer Support Resolution Agent
2. Code Generation with Claude Code
3. Multi-Agent Research System
4. Developer Productivity with Claude
5. Claude Code for CI/CD
6. Structured Data Extraction

各シナリオは複数ドメインに跨る。1シナリオ深掘りすると他のドメインも  
強化される設計。

---

## 4. 12週間ロードマップ

### Week 1〜2：基礎固め

* **Claude 101**（Academy）
* **AI Fluency: Framework and Foundations**（Academy）
* ゴール：Claude / Cowork / Claude Codeの違いを説明できる

### Week 3〜5：Claude API（最重要）

* **Building Applications with the Claude API**（Academy、約8.1h）→ Domain 1,4,5の土台
* 公式APIドキュメント（docs.anthropic.com）並読
* ゴール：tool use・構造化出力・エラーハンドリング込みのアプリを構築可

### Week 6〜7：MCP

* **Introduction to MCP**（Academy）
* **Model Context Protocol Advanced**（Academy、Pythonでサーバー/クライアント構築）
* modelcontextprotocol.io 仕様書
* ゴール：構造化エラーレスポンス込みのMCPツール設計・実装可

### Week 8〜9：Claude Code

* **Claude Code in Action**（Academy）
* **Building Skills for Claude Code**（Academy）
* **Claude Code on Coursera**（Vanderbilt大学 Jules White、監査受講無料）
* ゴール：CLAUDE.md階層をパススコープルールで構成、CI/CD統合

### Week 10〜11：演習・シナリオ対策

* **CCA公式試験ガイドPDF**（Partner Network経由で入手）
* **claudecertifications.com**（無料の25問練習）
* **Architect Cert MCPサーバー**（Claudeを試験チューター化、無料OSS）
* **Tutorials Dojo / Udemy**の有料模試（必要に応じて）
* **実践課題**：Claude Agent SDKで、tool calling・構造化エラー・  
  サブエージェントorchestration込みのE2Eエージェントループを1本構築  
  →これ1個で5ドメイン全部触れる
* ゴール：問題見た瞬間に正解と各不正解のアンチパターンを言語化できる

### Week 12：最終レビュー・受験

新教材は触らない。アンチパターン総復習に絞る。

**復習必須アンチパターン：**

* セキュリティをシステムプロンプト依存にする（プログラム的制御を省く）
* エージェント権限を広く設定しすぎる
* コンテキストウィンドウ制限を無視する
* 1個の巨大エージェントで処理（サブエージェント分解しない）
* 構造化出力のバリデーション・リトライループを省く

---

## 5. 市場文脈（取る価値の根拠）

* Fortune 100企業の70%がClaude採用
* Accenture 30,000人 / Cognizant 350,000人がCCA展開中
* AIエンジニア求人 前年比+143%
* AWS認定が「あると有利」→「必須」に5年。AIはその数倍速で進む見込み
* 2026年後半にSeller向け・上級アーキテクト向け追加資格予定。  
  CCA-F保持者は優先アクセス権

---

## 6. リソース一覧

| カテゴリ | URL | 料金 |
| --- | --- | --- |
| Anthropic Academy（13+コース） | anthropic.skilljar.com | 無料 |
| Coursera（Vanderbilt） | coursera.org | 監査受講無料 |
| CCA試験ガイドPDF | Partner Networkポータル | 無料 |
| 練習問題 | claudecertifications.com | 無料 |
| MCP仕様 | modelcontextprotocol.io | 無料 |
| APIドキュメント | docs.anthropic.com | 無料 |
| Partner Network参加 | anthropic.com/partners | 無料 |
| 試験料 | Skilljar経由 | $99 |

---

## 7. 自分用メモ

1. **6シナリオ × 5ドメインのマトリクスを最初に作る**  
   → 構造化得意な強みでショートカット。各セルに「正解パターン」と  
   「アンチパターン」を1個ずつ書き込む形式が効率良い
2. **Week 3〜5のAPIコースを最優先**  
   → 5ドメイン中3ドメイン分の土台。ここで詰まると後段も詰まる
3. **Week 10〜11のAgent SDK実装1本は妥協しない**  
   → 「協働前提」でも自分の手で1本通すと、判断問題の解像度が一気に上がる
4. **心理的なコーピング**  
   → 模試で点取れない時に「自分には価値がない」モードに入りがちだから、  
   アンチパターン誤答=「自分が本番で踏むはずだった地雷を事前に  
   踏んだだけにゃん」で処理する
