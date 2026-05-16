---
id: "2026-05-15-claude-for-small-business入門-quickbookshubspotm365に-01"
title: "Claude for Small Business入門 — QuickBooks・HubSpot・M365に繋がる15ワークフロー全解説"
url: "https://qiita.com/kai_kou/items/3cf73a7b0c1d84afc3de"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "Gemini", "cowork", "qiita"]
date_published: "2026-05-15"
date_collected: "2026-05-16"
summary_by: "auto-rss"
query: ""
---

<!-- IMAGE_SLOT: hero — Claude for Small Business overview illustration showing 7 business app integrations (QuickBooks, PayPal, HubSpot, Canva, DocuSign, Google Workspace, Microsoft 365) connected to Claude AI in the center. Clean flat design, white background, blue accent colors. -->

## はじめに

2026年5月13日、Anthropicは中小企業（SMB）向けの新パッケージ **「Claude for Small Business」** を発表しました。QuickBooks、PayPal、HubSpotなど7つのビジネスツールと連携する15の自動化ワークフローを提供し、財務・営業・マーケティングなどの業務を Claude が代行します。

この記事では以下を解説します:
- Claude for Small Business の全体像と7つの統合プラットフォーム
- 15のワークフローと業務カテゴリ
- Claude Cowork からのセットアップ手順
- 開発者が知るべき Agent SDK クレジットの仕組み（2026年6月15日施行）
- 信頼性・セキュリティの設計

### 対象読者
- Claude APIや Claude Code を業務活用しているエンジニア
- 中小企業向けSaaSの開発・運用に携わる方
- AIエージェントのビジネス活用に興味がある方

## TL;DR

- Claude for Small Business は **7ツール統合 + 15ワークフロー + 15スキル** のパッケージ
- Claude Cowork でトグルONするだけで使える。ユーザー承認なしに何も送信・実行されない
- 2026年6月15日から **Agent SDKクレジット** が月次で付与（Pro: $20、Max 5x: $100、Max 20x: $200）
- Team/EnterpriseプランではデータがAIトレーニングに使用されない
- 公式: [Introducing Claude for Small Business](https://www.anthropic.com/news/claude-for-small-business)

## Claude for Small Business とは

Claude for Small Business は、中小企業がすでに使っているツールの中に Claude のエージェント機能を埋め込むためのパッケージです。Anthropicが「米国GDPの44%を占める中小企業がAIを活用しやすくする」という目標のもと開発しました[^1]。

[^1]: [Introducing Claude for Small Business | Anthropic](https://www.anthropic.com/news/claude-for-small-business)（2026年5月13日）

コンセプトは **「使っているツールを切り替えずに、Claude が作業を引き受ける」** こと。請求書の催促、売上レポートの生成、リードトリアージなど、繰り返し発生する定型業務を Claude に委任できます。

<!-- IMAGE_SLOT: architecture — Diagram showing Claude for Small Business architecture: User → Claude Cowork (center) → 7 connected platforms (QuickBooks, PayPal, HubSpot, Canva, DocuSign, Google Workspace, Microsoft 365). Clean flow diagram with approval gate between Claude and external actions. -->

## 7つの統合プラットフォーム

| プラットフォーム | 対応業務カテゴリ | 主なユースケース |
|--------------|---------------|----------------|
| **QuickBooks** | 財務 | 給与計画、月次締め、キャッシュフロー予測、税務書類整理 |
| **PayPal** | 財務 | 入金確認、請求書発行、支払い督促、返金管理 |
| **HubSpot** | 営業・マーケティング | リードトリアージ、顧客インサイト、キャンペーン帰属分析 |
| **Canva** | マーケティング | コンテンツ生成、デザインアセット管理 |
| **Docusign** | 法務・業務 | 契約書管理、署名フロー |
| **Google Workspace** | 全般 | ドキュメント作成、スプレッドシート分析、メール対応 |
| **Microsoft 365** | 全般 | Excel・Word・PowerPoint・Outlookとの連携 |

各プラットフォームとの連携は **Claude Cowork** から設定します。既存の権限構造を維持しながら連携するため、ツール側の権限設定は変わりません。

## 15の自動化ワークフロー

パッケージには6つの業務カテゴリにわたる **15のワークフロー** が含まれています[^2]。

[^2]: [Anthropic launches Claude for Small Business with new automation workflows | SiliconANGLE](https://siliconangle.com/2026/05/13/anthropic-launches-claude-small-business-new-automation-workflows/)

### 財務（Finance）

| ワークフロー | 説明 |
|------------|------|
| **30日キャッシュフロー予測** | 現在の取引データから30日先の資金繰りを分析 |
| **月次損益レポート** | QuickBooksデータをもとにP&Lレポートを自動生成 |
| **請求書催促** | 未払い請求書をリストアップし、催促メッセージを作成 |
| **給与計画** | 従業員情報から次月の給与支払い計画を作成 |
| **税務書類整理** | 確定申告に必要な書類・数値を整理 |

### 営業・マーケティング（Sales & Marketing）

| ワークフロー | 説明 |
|------------|------|
| **リードトリアージ** | HubSpotのリードを優先度順に整理し、次アクションを提案 |
| **売上キャンペーン分析** | キャンペーンごとの費用対効果を可視化 |
| **コンテンツ戦略** | SNS投稿や広告コピーの案を自動作成 |

### 業務・HR・CS（Operations / HR / Customer Service）

残り7ワークフローは業務効率化・HR管理・カスタマーサービス対応を自動化します。各ワークフローは **再利用可能なスキル（Skills）** として設計されており、小規模チームでも繰り返し使えるのが特徴です。

<!-- IMAGE_SLOT: workflow — Step-by-step flow diagram showing how a user triggers a workflow in Claude Cowork, Claude processes data from connected apps, generates a result, user approves, and action is executed. Numbered steps 1-4, clean minimal style. -->

## Claude Cowork でのセットアップ

Claude for Small Business は **Claude Cowork** から設定します[^3]:

[^3]: [Claude for Small Business: Anthropic's 2026 AI Revolution for Main Street America | explainx.ai](https://explainx.ai/blog/anthropic-claude-for-small-business-2026)

1. **Claude Cowork にログイン**（https://claude.com/cowork）
2. **「Small Business」パッケージをトグルON**
3. **使用中のツールを接続**（QuickBooks、HubSpot等のOAuth認証）
4. **ワークフローを選択して実行**

重要な設計原則として、**Claude はユーザーの承認なしに何も送信・投稿・支払いを行いません**。すべてのアクションに確認ステップが挟まれます。


> Claude for Small Business の利用には有料の Claude プランが必要です。Claude Max サブスクリプションが SMBツアー参加者向けに1ヶ月無料提供されています。


## 開発者向け：Agent SDK クレジットの仕組み

Claude for Small Business の発表と同時に、開発者にとって重要な変更が告知されました。

### 2026年6月15日から施行：Agent SDK クレジットの分離

2026年6月15日以降、Claude のサブスクリプション使用量の中で **Agent SDK の利用が専用クレジット枠に分離されます**[^4]:

[^4]: [Use the Claude Agent SDK with your Claude plan | Claude Help Center](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)

| プラン | 月次 Agent SDK クレジット |
|--------|----------------------|
| Pro / Team Standard | **$20 / 月** |
| Max 5x / Team Premium | **$100 / 月** |
| Max 20x / Enterprise | **$200 / 月** |

この変更により、以下の用途が専用クレジットでカバーされます:
- `claude -p`（Claude Code の programmatic 実行）
- Claude Code GitHub Actions
- サードパーティ製 Agent SDK アプリ
- Claude for Small Business のコネクター実行

### 影響と注意点

```
Before（〜6月14日）:
  サブスクリプション使用量 = インタラクティブ + プログラマティック（一括）

After（6月15日〜）:
  サブスクリプション使用量 = インタラクティブのみ（Claude Code, Cowork, Claude.com）
  Agent SDK クレジット = プログラマティック実行専用（月次リセット、繰越なし）
```


> Agent SDK クレジットは月末に未使用分が消滅します（繰越不可）。GitHub Actions や自動化スクリプトの実行量が多い場合は、プランの見直しを検討してください。


移行対象のユーザーには6月15日以前に詳細メールが送付される予定です。

## 信頼性・セキュリティの設計

Claude for Small Business のセキュリティ設計は以下の原則に基づいています:

| 機能 | 詳細 |
|------|------|
| **承認ゲート** | すべてのアクション（送信・投稿・支払い）はユーザー承認後に実行 |
| **既存権限の維持** | 接続ツール側の権限設定は変更されない |
| **データ保護** | Team/Enterpriseプランでは会話データをAIトレーニングに使用しない |
| **スコープ制限** | 接続したツールの範囲内でのみ動作する |

Anthropicは公式ブログで「信頼は中核設計原則（trust is at the core of our design）」と述べており、Claude が自律的に行動する際の透明性を重視していることがわかります[^5]。

[^5]: [Introducing Claude for Small Business | Anthropic](https://www.anthropic.com/news/claude-for-small-business)

## 周辺動向：Claude の企業連携拡大

Claude for Small Business と同時期に、以下の大型連携も発表されています:

- **PwC**: Claude を活用したテクノロジー構築・M&A支援・エンタープライズ変革
- **Gatesファンデーション**: 2億ドルのパートナーシップ[^6]
- **Anthropicの年間換算売上（ARR）**: $30B到達（前年比3倍以上）[^7]

[^6]: [Anthropic forms $200 million partnership with Gates Foundation | Anthropic](https://www.anthropic.com/news/gates-foundation-partnership)
[^7]: [Anthropic debuts Claude for Small Business | Yahoo Finance](https://finance.yahoo.com/news/anthropic-debuts-claude-for-small-business-as-it-continues-its-enterprise-software-push-160500355.html)

中小企業向けパッケージは、エンタープライズ市場の拡大という大きな戦略の一環として位置づけられています。

## まとめ

- **Claude for Small Business** は QuickBooks・PayPal・HubSpot・Canva・Docusign・Google Workspace・Microsoft 365 と連携する15ワークフローパッケージ
- **Claude Cowork** からトグルONするだけで導入可能。承認ゲートにより安全に自動化できる
- **2026年6月15日** から Agent SDK クレジットが分離。Pro $20/月〜Max 20x $200/月の専用枠が追加される
- Team/Enterprise プランはデータ保護が強化されており、業務データの安全性も確保されている
- AnthropicのARR（年間換算売上）が$30Bに達し、SMB市場への本格展開が始まった

今後は Google I/O 2026（5月19日）での Gemini 4 発表や、Gemini Spark（常時稼働型AIエージェント）の正式発表にも注目です。

## 参考リンク

- [Introducing Claude for Small Business | Anthropic](https://www.anthropic.com/news/claude-for-small-business) — 公式発表
- [Use the Claude Agent SDK with your Claude plan | Claude Help Center](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan) — Agent SDKクレジット詳細
- [Anthropic launches Claude for Small Business with new automation workflows | SiliconANGLE](https://siliconangle.com/2026/05/13/anthropic-launches-claude-small-business-new-automation-workflows/) — 詳細報道
- [Anthropic courts a new kind of customer | TechCrunch](https://techcrunch.com/2026/05/13/anthropic-courts-a-new-kind-of-customer-small-business-owners/) — TechCrunchの解説
