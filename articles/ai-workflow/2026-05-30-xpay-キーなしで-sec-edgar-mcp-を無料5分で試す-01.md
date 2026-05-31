---
id: "2026-05-30-xpay-キーなしで-sec-edgar-mcp-を無料5分で試す-01"
title: "xpay キーなしで SEC EDGAR MCP を無料5分で試す"
url: "https://zenn.dev/stagproject/articles/5c4515a8d79439"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-05-30"
date_collected: "2026-05-31"
summary_by: "auto-rss"
query: ""
---

## 自己紹介

**stagproject** です。米国 SEC（証券取引委員会）の企業開示システム「EDGAR」のデータを、LLM エージェントがネイティブに扱える形で配信する MCP サーバー **[sec-filings-mcp](https://github.com/stagproject/sec-filings-mcp)** を開発・メンテしています。

現在、このプロジェクトは **MCP Registry**、**Glama**、および **xpay**（プロバイダースラッグ: `sec-edgar-filings`）に登録されております。

### 本記事のゴール

> **「AI エージェントが自律的に EDGAR をカタログ検索し、無料のプレビューで概要を掴み、必要に応じて決済（x402 USDC）を行ってフルデータを買う」**
>
> この A2A（Agent-to-Agent）データフローの最短ルートを、今回は **xpay の API キーなし（完全無料）** で試せるチュートリアルとしてまとめました。環境を一から調べるより早くキャッチアップできる内容です。動かして価値を感じたら、GitHub の Star・Issue・フィードバックをいただけると助かります。

---

## はじめに：なぜ「sec-filings-mcp」が必要なのか？

通常、SEC が提供する 10-K（年次報告書）や 10-Q（四半期報告書）を LLM に読み込ませるには、巨大なドキュメントのパース、RAG（検索拡張生成）の構築、メタデータ構造（CompanyFacts）の解釈など、多くの前処理コストが発生します。

`sec-filings-mcp` は、これらの生データを AI エージェントが即座に解釈・ドリルダウンできる **「フラットな構造化 JSON」** として提供します。

### 試用環境と本番環境の切り分け

本プロダクトはマイクロペイメント決済プラットフォーム「xpay」を介したエコシステムを想定していますが、今回の試用手順では xpay を通さず、インフラ（Cloud Run）の Upstream URL へ直接接続します。

* **今回の試用（Sandbox）:** Cloud Run 直結により、`search_filings`（検索）と `get_filing_sample`（無料プレビュー）を完全無料で検証可能
* **本番環境（Production）:** [xpay](https://xpay.tools) 経由でトラフィック計測、x402 USDC によるフルデータ購入（`purchase_filing`）が利用可能

※本記事では、決済が必要なフルデータ購入（`purchase_filing`）の手順は扱いません。

---

## 前提条件

* **MCP 対応クライアント:** [Cursor](https://cursor.com/)、Claude Desktop、Cline など
* **インターネット接続**（VPN やプロキシを挟まない環境を推奨）

---

## 1. クライアントへの MCP 接続設定

`mcp.json` などの `mcpServers` に以下を追加してください。

```
{
  "mcpServers": {
    "sec-filings-trial": {
      "url": "https://sec-filings-mcp-1065601264332.us-central1.run.app/mcp"
    }
  }
}
```

#### 設定のポイント

* トライアル URL のため、末尾の認証クエリ（`?key=`）は **不要**
* 保存後、MCP サーバーを **再起動またはリロード**（Cursor: `Settings` → `MCP` → 対象サーバーの `Reload`）

---

接続が成功すると、次の 3 ツールが認識されます。エージェントに「`sec-filings-trial` のツールリストを確認して」と指示するか、UI でロードを確認してください。

| ツール名 | 機能概要 | 想定コスト（xpay 上） |
| --- | --- | --- |
| `search_filings` | 条件に基づく 10-K / 10-Q などのカタログ検索 | **$0**（無料枠） |
| `get_filing_sample` | 対象ドキュメントの構造化プレビュー取得 | **$0**（無料枠） |
| `purchase_filing` | フルデータ（全指標・シグナル）の JSON 購入 | x402 USDC（※今回未使用） |

---

## 3. 実践演習：`search_filings` で Apple の 10-K を検索する

エージェントに `search_filings` を実行させ、Apple（AAPL）の最新提出書類を検索します。

### 引数（Arguments）の指定例

```
{
  "ticker": "AAPL",
  "form_type": "10-K",
  "limit": 3
}
```

### エージェントが着目すべき返却データ

検索結果の JSON には、書類ごとの `document_id` と **`agent_readiness_score`（AI 適応度スコア）** が含まれます。スコアが高い書類を優先してショートリストに入れるようプロンプトで誘導すると効果的です。

---

## 4. データ深度の深掘り：`get_filing_sample` による無料プレビュー

検索結果の `document_id` で、構造化エッセンスを取得します。

### 引数（Arguments）の指定例

```
{
  "document_id": "0000320193-0001062998"
}
```

※ `document_id` はステップ 3 で取得した実在 ID に置き換えてください。`{}` のみでもモック／デモデータが返る場合があります。

### 取得できるデータ構造

* **`agent_summary`:** ドキュメント全体のサマリー（LLM 向け）
* **`financial_metrics`:** CompanyFacts 由来の主要財務 KPI（売上、純利益など）

※ `alpha_signals` や `causality_events` のフルセットは、本番の `purchase_filing` で解放されます。

ここまでで目標であった無料サンプルの取得は完了しました。  
もし実際にデータの購入まで続く場合は次のステップとなります。

---

## 5. 本番（Production）へのステップアップ

1. **API キーの発行:** [xpay.tools](https://xpay.tools) で開発者アカウントを作成し API キーを取得（初期無料クレジットあり）
2. **接続 URL の更新:** `mcp.json` を xpay プロキシ URL に差し替え

```
https://sec-edgar-filings.mcp.xpay.sh/mcp?key=YOUR_XPAY_KEY
```

3. **ダッシュボードの最適化:** `search_filings` と `get_filing_sample` を **$0** に設定すると、API キー必須のまま基本検索コストを抑えられます

---

## 補足：ブラウザのサンドボックス環境で手軽に試す

ローカルの Cursor 設定を触りたくない場合は、[Glama - sec-filings-mcp](https://glama.ai/mcp/servers/stagproject/sec-filings-mcp) の **Try in Browser** でブラウザ完結のシミュレーションが可能です（本番ウォレット接続は不要）。

---

## リソース・クイックリンク一覧

---

## まとめ

* **API キー完全不要:** Cloud Run の Upstream で「米国政府データ × AI エージェント」をすぐ試せる
* **確かなデータ構造:** EDGAR 開示資料を LLM が扱いやすいフラット JSON で取得できる
* **エコシステムへの接続:** トラフィック・マネタイズに合わせて xpay ゲートウェイへ移行できる
