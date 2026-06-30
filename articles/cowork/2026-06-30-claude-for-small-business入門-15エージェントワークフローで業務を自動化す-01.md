---
id: "2026-06-30-claude-for-small-business入門-15エージェントワークフローで業務を自動化す-01"
title: "Claude for Small Business入門 — 15エージェントワークフローで業務を自動化する"
url: "https://qiita.com/kai_kou/items/02092d136350d254f4ee"
source: "qiita"
category: "cowork"
tags: ["API", "AI-agent", "LLM", "cowork", "qiita"]
date_published: "2026-06-30"
date_collected: "2026-07-01"
summary_by: "auto-rss"
query: ""
---

![Claude for Small Business — SaaSコネクターハブ・アーキテクチャ図](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/353-claude-small-biz-agent-workflows-guide/01-connector-hub-architecture.png)

## はじめに

2026年5月13日、Anthropicが **Claude for Small Business** を正式リリースしました。QuickBooks・HubSpot・Canvaといった中小企業が日常的に使うSaaSツールに、Claudeのエージェント機能を直接組み込む新プロダクトです。

エンジニアの観点では「AIエージェントが外部SaaSをオーケストレーションするアーキテクチャの実装例」として読み解けます。本記事では15種類のエージェントワークフローの構成と、開発者が参考にできる設計パターンを公式情報をもとに解説します。

### この記事で学べること

- Claude for Small Businessの全体アーキテクチャ
- 6カテゴリ・15ワークフローの具体的な動作内容
- 10+コネクターの一覧と連携の仕組み
- 承認フロー（Human-in-the-loop）設計のポイント
- 価格・プランと導入方法

### 対象読者

- AIエージェントのSaaS連携アーキテクチャに興味があるエンジニア
- Claude Coworkを業務自動化に活用したいチーム
- 中小企業向けAI自動化システムを設計・開発している方

---

## TL;DR

- **Claude for Small Business** はClaudeをQuickBooks・PayPal・HubSpot・Canva・Docusign・Google Workspace・Microsoft 365に接続するClaude Coworkのプラグイン
- 6カテゴリにわたる **15の定型エージェントワークフロー** がすぐに使える状態で提供
- **Human-in-the-loop設計**：送信・投稿・支払いの前に必ずオーナーの承認が入る
- Pro・Max・Teamsプランの追加料金なし（Claude Coworkに同梱）
- 設定はClaude Coworkデスクトップアプリのトグルをオンにするだけ

---

## Claude for Small Businessとは

Claude for Small Businessは、Anthropicが中小企業向けに設計した **AIエージェント自動化パッケージ** です。Claude Cowork（Anthropicのエンタープライズワークスペース）のプラグインとして動作し、既存のSaaSツールとClaudeを接続します。

### 特徴

| 項目 | 内容 |
|------|------|
| 発表日 | 2026年5月13日 |
| 提供形態 | Claude Coworkのトグルインストール |
| 対応プラン | Pro、Max、Teams（追加料金なし） |
| ワークフロー数 | 15種類（定型） |
| コネクター | 10+（QuickBooks、PayPal、HubSpot、Canvaなど） |
| データポリシー | Team/EnterpriseプランはAI訓練に使用しない |

![Human-in-the-loop承認フロー — 5ステップの実行プロセス](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/353-claude-small-biz-agent-workflows-guide/02-human-in-the-loop-flow.png)

---

## アーキテクチャ概要

Claude for Small Businessの動作は3つのレイヤーで構成されています。

### 1. コネクターレイヤー（10+種類）

以下のSaaSと双方向に接続します：

**ファイナンス・決済系**
- Intuit QuickBooks（会計・給与）
- PayPal（決済）
- Square（POS・決済）
- Stripe（決済）

**営業・CRM系**
- HubSpot（CRM・マーケティング）

**クリエイティブ・ドキュメント系**
- Canva（デザイン）
- Docusign（電子署名）
- Webflow（Webサイト）

**コラボレーション系**
- Google Workspace（Docs・Gmail・Calendar）
- Microsoft 365（Word・Excel・Outlook）
- Slack（コミュニケーション）

### 2. ワークフローエンジン

15の定型ワークフローは、単一ツールで完結するものから複数ツールをまたぐマルチツールオーケストレーションまで幅があります。

例：**Payroll Preparationワークフロー**
```
QuickBooks → アクティブ従業員・支払い期間データを取得
    ↓
PayPal → 受領済み決済とのキャッシュポジションを照合
    ↓
30日予測を構築 + 未払い分を優先度付けでリスト化
    ↓
フォローアップメッセージをキュー（オーナー承認待ち）
```

### 3. Human-in-the-loop承認レイヤー

送信・投稿・支払いなど **外部に影響する操作は必ず人間の承認が必要** です。この設計原則は「approve before anything sends, posts, or pays」と公式に表現されています。

既存のツール側の権限設定（ロール・アクセス制限）はそのまま引き継がれるため、Claudeが権限外の操作を行うことはありません。

---

## 15ワークフローの詳細

### Finance & Accounting（5種類）

![Finance & Accounting 5ワークフロー — QuickBooksとPayPalを活用した財務自動化](https://pub-2687e67855c941a0a1a9e1ad51ffc967.r2.dev/images/353-claude-small-biz-agent-workflows-guide/03-finance-workflows.png)

#### 1. Payroll Preparation
QuickBooksから従業員データと支払い期間を取得し、PayPalの受領決済と照合。キャッシュポジションを確定し、期限超過分の督促メッセージをキュー。

#### 2. Month-End Close
全トランザクションを調整し、損益計算書を平易な英語で作成。会計士に転送可能なクローズパッケージとしてエクスポート。QuickBooksを中心に複数システムのデータを統合。

#### 3. Cash Flow Forecasting
取引履歴と保留中のアイテムから **30日先の資金繰り予測** を構築。収支のギャップを事前に可視化します。

#### 4. Invoice Chasing
未払い請求書を特定し、優先度順にリスト化。フォローアップメッセージを自動下書き（送信前にオーナーが承認）。

#### 5. Tax Preparation Pack
年次財務データをIRS関連カテゴリ別に集約し、税務申告準備を効率化。

---

### Operations（3種類）

#### 6. Vendor Contract Review
有効な取引先契約を期限日・自動更新条項付きで一覧表示。見落としがちな自動更新を事前にキャッチできます。

#### 7. Employee Onboarding
役割と部門に応じたオンボーディングタスクリストを自動生成。Google Workspace・Slack等と連携してアカウントプロビジョニングを補助。

#### 8. Scheduling & Capacity Planning
カレンダーデータから過密スケジュールの期間を特定し、調整案を提案。

---

### Sales & CRM（3種類）

#### 9. Lead Triage
HubSpotの受信リードをオーナー定義の基準でスコアリング。優先連絡先を絞り込みます。

#### 10. Pipeline Health Check
停滞している商談をフラグし、再エンゲージメントメッセージを下書き。パイプラインの健全性をリアルタイムで把握できます。

#### 11. Campaign Attribution
マーケティングキャンペーンのアクティビティと成約案件を紐付け、ROIを可視化。

---

### Marketing（2種類）

#### 12. Content Calendar Generation
SNS用の **30日分コンテンツカレンダー** をCanvaと連携して下書き。ブランド資産のチームコラボレーション・パフォーマンストラッキングにも対応。

#### 13. Email Campaign Draft
プロモーションメールキャンペーンを作成。オーナーが確認・承認後に送信。

---

### Human Resources（1種類）

#### 14. Performance Review Prep
Slackアクティビティとプロジェクト履歴から各従業員のパフォーマンス評価草案を生成。定量的な根拠に基づいたレビューを効率化。

---

### Customer Service（1種類）

#### 15. Support Ticket Triage
受信した問い合わせを内容別に分類し、よくある質問への返信草案を作成。対応スピードを向上させながら最終承認は人間が担います。

---

## セットアップ方法

Claude for Small BusinessはIT担当者なしで導入できるように設計されています。

### 手順

1. **Claude Coworkデスクトップアプリ** を開く
2. 設定から **Claude for Small Business** プラグインをトグルオン
3. 使用するSaaSツール（QuickBooks・HubSpotなど）を接続認証
4. 実行したいワークフローを選択
5. Claudeがプランを提示 → 承認後に実行


> セットアップにかかる時間は数分程度。既存ツールのOAuth認証を通じて接続するため、パスワードの共有は不要です。


---

## 価格・プラン

Claude for Small Businessは **Claude Coworkに同梱** されており、Pro・Max・Teamsプランの利用者は追加料金なしで利用できます。

各プランの詳細については[Anthropic公式サイト](https://claude.com/pricing)を参照してください。


> EnterpriseプランではデータがAIの訓練に使用されません。機密性の高い財務データを扱う場合はプラン選択に注意してください。


---

## エンジニアが注目すべき設計パターン

Claude for Small Businessの実装から読み取れる、エージェントシステム設計のポイントを整理します。

### 1. ツール統合のレイヤー化

単一のLLMがすべての外部APIを直接呼び出すのではなく、**コネクターレイヤー** が各SaaSの認証・データ変換を担当しています。Claude自体はビジネスロジックの推論に集中できる設計です。

### 2. Human-in-the-loop の組み込み

「外部に影響する操作（送信・投稿・支払い）は必ず人間が承認」という原則を一貫して守ることで、エンドユーザーの信頼を維持しています。完全自動化より **部分自動化** を選択した設計判断です。

### 3. 既存権限の継承

Claudeに新たな権限を付与するのではなく、**既存ツール側の権限設定を引き継ぐ** 設計は、セキュリティリスクを最小化する実践的なアプローチです。

### 4. 定型ワークフローによる品質保証

完全自由なエージェントタスクより、**定型ワークフロー** として提供することで：
- プロンプトの品質を事前に検証済みの状態に保つ
- ユーザーがAIに何ができるか直感的に把握できる
- 予期しない動作のリスクを低減できる

---

## 同時発表：AI Fluency for Small Business

Claude for Small Businessと合わせて、AnthropicはPayPalと共同で **AI Fluency for Small Business** という無料オンラインコースも公開しました。

- 9レッスン構成
- AI流暢性研究者と中小企業オーナーによる動画
- Anthropicの「4D AI Fluency Framework」に基づく構成

さらに、2026年5月14日から **10都市を巡るライブトレーニングツアー** も開始（シカゴ、タルサ、ダラス、ニュージャージー、バトンルージュ、バーミンガム、ソルトレイクシティ、ボルチモア、サンノゼ、インディアナポリス）。各都市で中小企業リーダー100名を対象に半日ワークショップを実施します。

---

## まとめ

Claude for Small Businessは、AIエージェントが実際のビジネスワークフローに統合される際の設計パターンを体系化した製品です。

- **15ワークフロー**：Finance・Operations・Sales・Marketing・HR・CSの6カテゴリを網羅
- **10+コネクター**：QuickBooks・HubSpot・Canvaなど主要SaaSに対応
- **Human-in-the-loop**：外部操作前の必須承認フローでリスクを制御
- **権限継承**：既存ツールの権限設定をそのまま活用

エンジニアにとっては「エージェントをどう外部SaaSと接続し、人間の承認をどこに組み込むか」という設計の実例として参考になります。

## 参考リンク

- [Introducing Claude for Small Business](https://www.anthropic.com/news/claude-for-small-business) — Anthropic公式発表（2026-05-13）
- [Claude for Small Business: 15 Agentic Workflows, 15 Skills, and 10+ Connectors Explained](https://chatforest.com/guides/claude-for-small-business-agentic-workflows-connectors/) — ワークフロー詳細解説
- [Anthropic launches Claude for Small Business](https://siliconangle.com/2026/05/13/anthropic-launches-claude-small-business-new-automation-workflows/) — SiliconANGLE（2026-05-13）
- [Claude for Small Business ships 15 agent workflows](https://the-decoder.com/anthropic-launches-claude-for-small-business-to-embed-ai-into-the-tools-you-forgot-you-pay-for/) — The Decoder（2026-05-13）
