---
id: "2026-05-15-alpaca-guard-mcp-で-claude-に安全に株取引させるai-エージェント-alpa-01"
title: "alpaca-guard-mcp で Claude に安全に株取引させる【AI エージェント × Alpaca】"
url: "https://qiita.com/LemonCake/items/b1d33c4bde0806688c5c"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "qiita"]
date_published: "2026-05-15"
date_collected: "2026-05-16"
summary_by: "auto-rss"
query: ""
---

:::note
この記事で紹介する **alpaca-guard-mcp** は npm で公開されています。
- **npm**: https://www.npmjs.com/package/alpaca-guard-mcp
:::

## はじめに

「Claude に株を買ってきて」——そう話しかけるだけで AI エージェントが発注できたら便利です。でも実際にやろうとすると、不安が頭をよぎります。

- エージェントが暴走して大量発注してしまったら？
- 誤ったシンボルで注文が通ってしまったら？

**alpaca-guard-mcp** はこうした「エージェントによる株取引の安全弁」として設計された MCP サーバーです。ローカルに置いたキャップ台帳で日次・セッション上限を管理し、デフォルトは paper trading（仮想取引）で動作します。本番取引は環境変数による明示的なオプトインが必要です。

---

## Alpaca とは

[Alpaca](https://alpaca.markets) は米国の証券ブローカーが提供する **Commission-free な株取引 API** です。Paper Trading は無料・仮想資金で本番同等のテストが可能です。

---

## alpaca-guard-mcp の仕組み

### キャップ台帳

発注を許可する前に、ローカルファイル `~/.alpaca-guard/cap.json` に記録された累積使用額と上限を照合します。

```json
{
  "dailyLimitUsd": 100,
  "sessionLimitUsd": 25,
  "usedTodayUsd": 12.50,
  "usedThisSessionUsd": 12.50,
  "resetDate": "2026-05-14"
}
```

上限を超える注文は拒否され、Alpaca の API には一切リクエストが飛びません。

### デフォルト: Paper Trading

```
paper-api.alpaca.markets  ← デフォルト（仮想）
api.alpaca.markets        ← ALPACA_LIVE=yes-i-understand のときのみ
```

---

## セットアップ

```json
{
  "mcpServers": {
    "alpaca-guard": {
      "command": "npx",
      "args": ["-y", "alpaca-guard-mcp"],
      "env": {
        "ALPACA_KEY_ID": "PKxxxxxxxxxxxxxxxx",
        "ALPACA_SECRET_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

---

## 利用可能なツール

| ツール名 | 説明 |
|---|---|
| `setup` | 現在の設定・モードを確認 |
| `guard_status` | キャップ残高・本日の使用額を確認 |
| `guard_set_limit` | 日次・セッション上限を変更 |
| `get_quote` | 銘柄の現在価格を取得 |
| `list_supported_stocks` | 取引可能な銘柄一覧 |
| `guarded_buy_stock` | キャップチェック付き成行買い注文 |
| `guarded_sell_stock` | キャップチェック付き成行売り注文 |
| `get_positions` | 保有ポジション一覧 |

---

## Paper Trading で動かしてみる

```
AAPL の現在価格を調べて、$10 分 paper trading で買ってみて
```

Claude が自動で guard_status → get_quote → guarded_buy_stock の順に実行します。

### レスポンス例

```json
{
  "orderId": "a1b2c3d4-...",
  "symbol": "AAPL",
  "side": "buy",
  "notional": "10.00",
  "status": "pending_new",
  "capRemainingTodayUsd": 90.00,
  "mode": "paper"
}
```

---

## 本番取引を有効にする

```json
"env": {
  "ALPACA_KEY_ID": "PKxx（Live用）",
  "ALPACA_SECRET_KEY": "xxxx（Live用）",
  "ALPACA_LIVE": "yes-i-understand",
  "ALPACA_DAILY_LIMIT_USD": "200"
}
```

---

## 注意事項

日本居住者が Live Trading を行う場合、**金融商品取引法上の規制が適用される可能性があります**。Paper Trading はシミュレーションのため規制対象外ですが、本番取引前に専門家に確認してください。本記事は技術的な解説であり、投資勧誘ではありません。

---

## リンク

- **npm**: https://www.npmjs.com/package/alpaca-guard-mcp
- Alpaca 公式: https://alpaca.markets
