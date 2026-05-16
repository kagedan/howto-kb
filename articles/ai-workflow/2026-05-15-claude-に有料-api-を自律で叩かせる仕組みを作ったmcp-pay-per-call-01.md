---
id: "2026-05-15-claude-に有料-api-を自律で叩かせる仕組みを作ったmcp-pay-per-call-01"
title: "Claude に有料 API を自律で叩かせる仕組みを作った【MCP × pay-per-call】"
url: "https://qiita.com/LemonCake/items/b1828e442dc5c453a9d4"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "AI-agent", "qiita"]
date_published: "2026-05-15"
date_collected: "2026-05-16"
summary_by: "auto-rss"
query: ""
---

:::note
この記事で紹介する **pay-per-call-mcp** は今すぐ試せます（Demo Mode はアカウント不要）。
- **npm**: https://www.npmjs.com/package/pay-per-call-mcp
- **Glama**: https://glama.ai/mcp/servers/@evid-ai/pay-per-call-mcp
:::

## はじめに

Claude などの AI エージェントに「Tavily で検索して」「この会社の情報を調べて」と頼みたい場面がよくあります。でも実際にやろうとすると、すぐに壁にぶつかります。

**有料 API を叩かせるには、API キーをエージェントに渡すしかない。**

これが地味に辛い。

## 問題の整理

### サービスごとに API キーが必要

Tavily、Serper、Hunter.io、gBizINFO——それぞれに登録して、それぞれの API キーを管理して、それぞれの課金プランを把握しないといけない。エージェントに使わせたいサービスが増えるたびに同じことを繰り返す。

### エージェントに API キーを渡すと漏洩リスクがある

API キーをそのまま環境変数に入れると、エージェントが何かの拍子に `check_env()` を呼んだり、ログに吐いたりするリスクがあります。また「エージェントが暴走して API を叩きまくる」のを止める仕組みも自前で作ることになる。

### 使った分だけ課金したい

月額 $49 のサブスクを契約しても、週に数回しか使わない。1 回あたり数セントで済む処理に月額課金は割に合わない。

---

## 解決策：pay-per-call-mcp の仕組み

この課題を解決するために **LemonCake** という仕組みを作りました。

コアのアイデアはシンプルです。

**エージェントには API キーではなく「Pay Token（JWT）」を渡す。**

```
あなた                  Claude                  有料 API
  │                       │                        │
  ├─ Pay Token 発行 ────▶  │                        │
  │   上限: $2.00         │                        │
  │   有効期限: 1h        │                        │
  │                       ├─ /api/proxy 呼び出し ─▶ │
  │                       │   Authorization: Bearer <pay_token>
  │                       │                        │
  │                       │  ◀─ レスポンス + 課金 ─┤
  │                       │                        │
  │                       ├─ (残高ゼロ)             │
  │                       │   402 Payment Required  │
  │                       ✗   エージェント停止      │
```

### Pay Token の特徴

| パラメータ | 説明 | 例 |
|---|---|---|
| `limitUsdc` | この Token が使える上限額 | `"2.00"` |
| `expiresIn` | 有効期限 | `"1h"` |
| `serviceId` | 呼び出し可能なサービス | `"svc_tavily"` |

上限を超えたら `402 Payment Required` が返ってエージェントは止まります。**エージェントに本物の API キーが渡ることは一切ありません。**

### MCP サーバーとして動く

`pay-per-call-mcp` は [Model Context Protocol (MCP)](https://modelcontextprotocol.io) サーバーとして実装されています。Claude Desktop や Cursor に `npx` 1 行で繋がります。

---

## セットアップ

### Claude Desktop への接続

`~/Library/Application Support/Claude/claude_desktop_config.json` に追記します。

```json
{
  "mcpServers": {
    "pay-per-call": {
      "command": "npx",
      "args": ["-y", "pay-per-call-mcp"],
      "env": {
        "LEMON_CAKE_BUYER_JWT": "eyJhbGci..."
      }
    }
  }
}
```

### Demo Mode で今すぐ試せる

**アカウントも API キーも不要です。** 環境変数を何も設定せずに起動すると、自動で Demo Mode になります。

```json
{
  "mcpServers": {
    "pay-per-call": {
      "command": "npx",
      "args": ["-y", "pay-per-call-mcp"]
    }
  }
}
```

Demo Mode では以下が動きます：

- `demo_search` — Wikipedia を検索（実データ）
- `demo_fx` — 為替レートを取得（open.er-api）
- `demo_echo` — httpbin でリクエストの中身を確認

課金なし、登録なし、即試せます。

---

## 実際に Claude に使わせてみる

Claude に以下のように話しかけます：

```
LemonCake の demo_search で "AI agent payments" を検索して、
デモ残高の確認もあわせてやって
```

Claude が自動で MCP ツールを呼び出します：

1. `setup` — 現在の設定・モードを確認
2. `list_services` — 利用可能なサービス一覧を取得
3. `call_service` — demo_search を呼び出し
4. `check_balance` — 残高確認

### レスポンス例

```json
{
  "status": 200,
  "chargeId": "ch_demo_abc123",
  "amountUsdc": "0.000",
  "x402Receipt": {
    "scheme": "lemoncake-pay-token-v1",
    "x402Compatible": true,
    "chain": "off-chain (LemonCake Pay Token)",
    "asset": "USDC",
    "amount": "0.000"
  }
}
```

---

## 対応サービス一覧

| サービス | カテゴリ | 用途 |
|---|---|---|
| Tavily | 検索 | AI 向け高品質検索 |
| Serper | 検索 | Google 検索 API |
| Hunter.io | メール | ドメインからメール探索 |
| gBizINFO | 日本企業情報 | 法人番号・企業基本情報 |
| 国税庁インボイス API | 税務 | 適格請求書発行事業者確認 |
| e-Gov | 行政 | 法令・行政文書検索 |

---

## KYA（Know Your Agent）上限設定

```json
{
  "balanceUsdc": "47.50",
  "kyaTier": "tier_1",
  "dailyLimitUsdc": "10.00",
  "sessionLimitUsdc": "2.00"
}
```

Pay Token の `limitUsdc` と KYA 上限の**小さい方**が実際の上限になります。二重の安全弁です。

---

## まとめ

- **API キーを渡さない** — エージェントには Pay Token（JWT）だけ渡す
- **使った分だけ課金** — USDC での pay-per-call、月額サブスク不要
- **自動停止** — 予算超過で `402`、即時 revoke で `422`
- **MCP で繋がる** — `npx` 1 行、設定 JSON を数行追加するだけ
- **まず Demo Mode で試せる** — アカウント不要

**試してみたい方はこちらから（Demo Mode はすぐ使えます）：**

- **npm**: https://www.npmjs.com/package/pay-per-call-mcp
- **Glama**: https://glama.ai/mcp/servers/@evid-ai/pay-per-call-mcp
- インストール: `npx pay-per-call-mcp`

フィードバックや「このサービスを対応してほしい」などあれば、GitHub Issues か [contact@aievid.com](mailto:contact@aievid.com) まで気軽にどうぞ。
