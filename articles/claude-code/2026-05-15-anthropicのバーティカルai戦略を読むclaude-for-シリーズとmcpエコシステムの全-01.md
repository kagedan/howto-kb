---
id: "2026-05-15-anthropicのバーティカルai戦略を読むclaude-for-シリーズとmcpエコシステムの全-01"
title: "AnthropicのバーティカルAI戦略を読む——「Claude for ○○」シリーズとMCPエコシステムの全体像"
url: "https://qiita.com/zygm/items/795d036766a20a6b876a"
source: "qiita"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "LLM", "cowork", "Python"]
date_published: "2026-05-15"
date_collected: "2026-05-16"
summary_by: "auto-rss"
query: ""
---

# AnthropicのバーティカルAI戦略を読む——「Claude for ○○」シリーズとMCPエコシステムの全体像

## 概要

2026年5月13日、Anthropicが「Claude for Small Business」を発表した。
これで2025年以降に投入された業界特化パッケージは5本目になる。

単なる機能追加ではない。Anthropicがモデル提供会社からプロダクト会社へ軸足を移している証拠だ。本稿ではシリーズ全体の構造を整理し、技術的な背景（Claude Cowork・MCP）と日本での実情を論じる。

---

## 「Claude for ○○」シリーズ全体像

2025年初頭から現在まで、わずか数か月で5つの業界特化パッケージがリリースされた。

| 製品 | 発表時期 | 主な連携・特徴 |
|---|---|---|
| Claude for Life Sciences | 2025年秋 | Benchling連携、プロトコル生成、バイオインフォマティクス |
| Claude for Healthcare | 2026年1月 | HIPAA対応、CMS/ICD-10/PubMed連携、HealthEx・Function Health |
| Claude for Financial Services | 2026年5月5日 | S&P等データソース、投資分析ワークフロー |
| Claude for Legal | 2026年5月12日（拡張） | Westlaw・DocuSign・Box連携、6プラクティス領域 |
| Claude for Small Business | 2026年5月13日 | QuickBooks・PayPal・HubSpot・Canva・DocuSignほか |

金融（5/5）→ 法務（5/12）→ 中小企業（5/13）という8日間で3本というスピードは、上場準備を見据えた市場証明（PMF確認）のスプリントと読める。

---

## Claude for Small Business の中身

### 構造

Claude for Small Businessは独立プロダクトではなく、**Claude Cowork 内のプラグイン**として提供される。トグル一つで有効化でき、既存SaaSアカウントを接続するだけで使い始められる。

```
Claude Cowork
└── プラグイン
    ├── Design
    ├── Marketing
    ├── Sales
    ├── Legal
    └── Small Business  ← 今回追加
```

### 連携ツールと担当領域

| ツール | 担当する業務 |
|---|---|
| QuickBooks | 月次決算・給与計画・キャッシュフロー予測・税務パケット作成 |
| PayPal | 入金確認・請求書管理・紛争対応・返金処理 |
| HubSpot | リードトリアージ・顧客動向分析・キャンペーン効果測定 |
| Canva | SNS画像・バナー・資料の生成と公開 |
| DocuSign | 署名依頼送信・ステータス追跡・締結書類の格納 |
| Google Workspace / Microsoft 365 | ドキュメント・メール・カレンダーとの連携 |
| Slack / Square / Stripe / Webflow | 通知・決済・EC管理 |

### 提供されるもの

- **15のワークフロー**（自律実行型）：月次決算、キャッシュフロー予測、マーケティングキャンペーン起動など
- **15のスキル**（繰り返しタスク用）：督促リスト整理、新規従業員オンボーディングなど

### 設計上の重要な原則

送信・投稿・支払いなど不可逆なアクションの手前では**必ず人間の承認を挟む**。既存のSaaSアクセス権限もそのまま引き継がれるため、QuickBooksで見えない情報はClaude経由でも見えない。

### 料金

Claude for Small Business自体の追加料金はない。Team/Enterpriseプランのライセンスと各SaaSのサブスクリプションのみで利用できる。

---

## 技術的背景：なぜMCPが鍵なのか

このシリーズ全体が **Model Context Protocol（MCP）** の上に構築されている点は見落とせない。

MCPはAnthropicが策定しオープンソース化したAI向け標準プロトコルで、外部ツール・データソースとのI/Oを標準化する。各コネクター（QuickBooks、PayPal、HubSpotなど）はすべてMCPサーバーとして実装されている。

```
Claude Cowork
    │
    │  MCP（Model Context Protocol）
    │
    ├── QuickBooks MCP Server
    ├── PayPal MCP Server
    ├── HubSpot MCP Server
    └── （任意のMCPサーバー）  ← ここが重要
```

AnthropicはQuickBooks向けコネクターを作ったのではなく、「MCPコネクターを作れば誰でもClaudeエコシステムに参加できる」という仕組みを作った。この違いは大きい。

---

## 日本での利用可否と現状の制約

技術的には日本からも利用可能だ。Claude Cowork自体に地域制限はなく、日本在住ユーザーが動作確認している報告もある。

しかし実用上の制約は明確に存在する。

### 現時点で連携できない日本固有ツール

```
会計：freee / マネーフォワード / 弥生会計
CRM：kintone / Salesforce Japan
決済：PAY.JP / GMO Payment Gateway
HR ：SmartHR / 人事労務freee
```

現状のClaude for Small BusinessはQuickBooksやPayPalなど米国発SaaSを前提としており、日本の中小企業が実際に使っているツールとの公式連携は提供されていない。

### MCPがその壁を崩す可能性

MCPコネクターの仕様は公開されている。freeeやマネーフォワードが公式MCPサーバーを開発すれば、同じワークフローが日本の中小企業向けにも即座に有効化される。あるいはサードパーティの開発者が先行実装することも技術的には可能だ。

---

## エンジニアとして今すぐできること

### 1. 日本向けMCPサーバーを作る

freee APIを例にすると、FastMCPを使えばPythonで比較的容易に実装できる。

```python
from fastmcp import FastMCP
import httpx

mcp = FastMCP("freee-connector")

@mcp.tool()
async def get_invoices(company_id: int, status: str = "未払い") -> list[dict]:
    """freeeから請求書一覧を取得する"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.freee.co.jp/api/1/invoices",
            params={"company_id": company_id, "invoice_status": status},
            headers={"Authorization": f"Bearer {FREEE_TOKEN}"},
        )
        return resp.json()["invoices"]
```

MCP仕様に準拠したサーバーを作れば、Claude Coworkから直接呼び出せるようになる。

### 2. スキルファイルでワークフローを定義する

プラグインは「スキルファイル（テキスト）」と「コネクター（MCPサーバー）」の組み合わせで構成される。スキルファイルはClaudeへの詳細な指示書で、業務フローの定義そのものだ。

```
skills/
├── monthly-close.md       # 月次決算ワークフロー
├── invoice-followup.md    # 督促フロー
└── cash-flow-forecast.md  # 資金繰り予測
```

この構造を理解すれば、自社業務特化のプラグインを開発できる。

### 3. ドメイン知識との掛け合わせが差別化になる

食品製造・農業・物流など、日本固有のドメインでは汎用コネクターは存在しない。HACCPデータ管理や食品衛生法対応のMCPサーバーを作れるのは、ドメイン知識とMCP実装スキルを両方持つ人間だけだ。

---

## Anthropicの戦略的意図

### モデル提供からOSへ

今回のシリーズが示すのは、AnthropicがLLM提供会社から**業務OSのプラットフォーマー**を目指しているということだ。Salesforce・ServiceNow・Intuit・DocuSignなどの株価が軒並み下落しているという報道は、市場がこの構図を正確に読んでいることを示している。

### SMBは次のフロンティア

「中小企業は米国GDPの44%を占めながら、大企業のようなリソースを持ち合わせていない。AIはこのギャップを埋められる最初のテクノロジーだ」（Daniela Amodei）

SMBへの参入は慈善事業ではなく、3,600万社というロングテール市場の獲得を意味する。

---

## まとめ

```
Claude for ○○ シリーズ（2025〜2026）

① 共通アーキテクチャ
   └─ Claude Cowork のプラグイン
   └─ MCP コネクター（オープン設計）

② ラインナップ
   └─ Life Sciences / Healthcare / Financial / Legal / Small Business

③ 日本の現状
   └─ 技術的には利用可能
   └─ 日本固有SaaS（freee・マネーフォワード等）との公式連携は未対応

④ エンジニアの機会
   └─ 日本向けMCPコネクターを先行開発できる
   └─ ドメイン知識 × MCP実装 = 再現困難なポジション
```

Claude Coworkがインフラになるとき、その上で動くコネクターを誰が作るかが問われる。日本市場ではその答えはまだ出ていない。ここに入るのがいちばん早い。

---

## 参考リンク

- [Introducing Claude for Small Business - Anthropic](https://www.anthropic.com/news/claude-for-small-business)
- [Agents for Financial Services - Anthropic](https://www.anthropic.com/news)
- [Claude for Life Sciences - Anthropic](https://www.anthropic.com/news/claude-for-life-sciences)
- [Model Context Protocol](https://modelcontextprotocol.io/)
