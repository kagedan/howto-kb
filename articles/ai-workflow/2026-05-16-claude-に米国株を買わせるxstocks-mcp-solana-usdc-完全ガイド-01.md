---
id: "2026-05-16-claude-に米国株を買わせるxstocks-mcp-solana-usdc-完全ガイド-01"
title: "Claude に米国株を買わせる【xstocks-mcp × Solana × USDC 完全ガイド】"
url: "https://qiita.com/LemonCake/items/168bdf2099d9f7e9bbe0"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "qiita"]
date_published: "2026-05-16"
date_collected: "2026-05-17"
summary_by: "auto-rss"
query: ""
---

:::note
この記事で紹介する **xstocks-mcp** は npm で公開中です。
- **npm**: https://www.npmjs.com/package/xstocks-mcp
:::

## はじめに

「Claude、AAPL を $10 分買っておいて」——そう話しかけるだけで AI エージェントが米国株を購入できたら面白いですよね。

**xstocks-mcp** はそれを実現する MCP サーバーです。証券口座不要、規制準拠のトークン化米国株（xStocks）を Solana 上で USDC を使って直接買えます。デフォルトは **dry-run**（模擬実行）なので、設定を間違えても実際の資金は動きません。

---

## xStocks とは

[xStocks](https://backed.fi/) は Backed Finance が発行する **1:1 裏付けのトークン化米国株**です。

| 項目 | 内容 |
|---|---|
| 発行体 | Backed Finance（スイス規制準拠） |
| 対応銘柄 | AAPL / TSLA / NVDA / SPY / QQQ など 50+ 銘柄 |
| ブロックチェーン | Solana（Token-2022 プログラム） |
| 決済通貨 | USDC |
| 取引所 | Jupiter DEX（分散型 AMM アグリゲーター） |
| 証券口座 | **不要** |
| KYB/KYC | **不要**（Jupiter は公開 DEX） |

---

## xstocks-mcp の仕組み

```
あなた（Claude に話しかける）
    │
    ▼
Claude Desktop（MCP クライアント）
    │  tool: guarded_buy_stock(symbol="AAPL", amountUsd=10)
    ▼
xstocks-mcp
    ├── 1. find_xstock  → 本物の Backed mint アドレスを解決（詐欺フィルター内蔵）
    ├── 2. preflight    → 日次上限（cap.json）チェック
    ├── 3. get_quote    → Jupiter で USDC → AAPLx の見積もり取得
    ├── 4. price impact → 2% 超えたら拒否
    └── 5. (dry-run) シミュレーション結果返却
        OR
        (live) Jupiter swap → Solana に署名・送信
    │
    ▼
~/.xstocks/cap.json（ローカル日次上限台帳）
```

---

## セットアップ

### 1. Claude Desktop の設定

`~/Library/Application Support/Claude/claude_desktop_config.json` に追加：

```json
{
  "mcpServers": {
    "xstocks": {
      "command": "npx",
      "args": ["-y", "xstocks-mcp"],
      "env": {
        "SOLANA_WALLET_PRIVATE_KEY": "（Phantom からエクスポートした秘密鍵 Base58）",
        "XSTOCKS_ALLOW_LIVE": "yes-i-understand",
        "SOLANA_RPC_URL": "https://api.mainnet-beta.solana.com"
      }
    }
  }
}
```

> 🎮 **まず dry-run で試したい場合**: env を空のまま起動すれば Dry-Run Mode になります。全ツールが動作しますが、実際の swap は送信されません。

### 2. ウォレット準備

Phantom や Solflare で Solana ウォレットを作成し、以下を入金：

- **USDC**（購入したい金額分）— mint: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- **SOL**（ガス代）— 約 0.01 SOL（≒ $2）あれば十分

### 3. 秘密鍵のエクスポート

Phantom の場合：設定 → セキュリティとプライバシー → 秘密鍵をエクスポート → Base58 文字列をコピー

> ⚠️ 秘密鍵は絶対に他人と共有しないでください。環境変数として設定し、`.env` ファイルは `.gitignore` に追加してください。

---

## 利用可能なツール

| ツール | 種別 | 説明 |
|---|:---:|---|
| `setup` | 読取専用 | 現在のモード・上限・環境設定を確認 |
| `wallet_status` | 読取専用 | 公開鍵・SOL 残高・USDC 残高を取得 |
| `guard_status` | 読取専用 | 日次上限・使用額・残高・直近10取引を確認 |
| `guard_set_limit` | 書込 | 日次 USD 上限を変更 |
| `find_xstock` | 読取専用 | ティッカーから本物の xStock mint を解決 |
| `get_quote` | 読取専用 | Jupiter で USDC → xStock の見積もり取得 |
| `guarded_buy_stock` | 書込 | 上限チェック付き買い注文（dry-run デフォルト） |

---

## 実際の使い方（Claude との会話例）

### 現在の状態確認

```
ユーザー: xstocks の設定状況を確認して

Claude: setup ツールで確認します...

モード: DRY-RUN（実際の swap は送信されません）
ウォレット: 7xKXt...（公開鍵）
USDC 残高: 150.00 USDC
SOL 残高: 0.052 SOL（ガス代 OK）
日次上限: $25.00（残り $25.00）
```

### 銘柄を調べて買う

```
ユーザー: NVDA の現在価格を調べて、$15 分 dry-run で買ってみて

Claude: まず NVDA の xStock mint を確認します...

find_xstock: NVDAx
  mint: 4k3Dyjz...
  verified: ✅（Backed 公式 mint）

get_quote: USDC 15.00 → NVDAx
  取得予定: 0.11234 NVDAx（≒ $14.89 相当）
  レート: 1 NVDAx ≈ $133.52
  価格インパクト: 0.01%（安全）

guarded_buy_stock (dry-run):
  シミュレーション成功
  実際に送信するなら: 0.11234 NVDAx 取得見込み
  LemonCake 手数料: $0.10
  合計コスト: ~$15.10
  
  ※ dry-run モードです。実行するには XSTOCKS_ALLOW_LIVE=yes-i-understand を設定してください。
```

### 日次上限の設定

```
ユーザー: 日次上限を $50 に設定して

Claude: guard_set_limit を実行します...

日次上限を $25 → $50 に変更しました。
この上限はエージェントが物理的に超えられません。
設定は ~/.xstocks/cap.json に保存済みです。
```

---

## 安全機能の詳細

### 1. 日次上限（Cap Ledger）

```json
// ~/.xstocks/cap.json
{
  "dailyLimitUsd": 25,
  "usedTodayUsd": 10.10,
  "resetDate": "2026-05-16",
  "lifetimeSwaps": 3
}
```

上限超えの注文は **Solana に到達する前に**ブロックされます。

```
上限 $25 / 本日使用 $20 / 残り $5 の状態で $10 注文した場合:
→ { "allowed": false, "status": "BUDGET_EXCEEDED",
    "hint": "$10.00 の注文ですが、本日の残高は $5.00 です" }
```

### 2. 詐欺フィルター（Scam Filter）

Jupiter の検索結果には pump.fun のコピートークンが大量に含まれます。`find_xstock` は以下で本物のみ通過させます：

- `verified` + `xstocks` タグが両方存在する
- アイコンが `xstocks-metadata.backed.fi` ドメイン
- Token-2022 プログラム（Backed 独自の transfer hook 対応）

### 3. 価格インパクト上限

```
XSTOCKS_MAX_PRICE_IMPACT_PCT=2  （デフォルト 2%）
```

スリッページが大きすぎる場合は swap を拒否します。

---

## 費用の内訳

| コスト | 金額 |
|---|---|
| 株式取得コスト | 指定 USD 分 |
| Jupiter AMM スプレッド | ≈ 0〜0.1%（流動性次第） |
| Solana ガス | ≈ $0.001 / tx |
| LemonCake 手数料 | **$0.10 / 取引（定額）** |

$5 の取引でも $1,000 の取引でも手数料は $0.10 固定です。

---

## 対応銘柄（一部）

```
AAPL（アップル）    TSLA（テスラ）     NVDA（エヌビディア）
MSFT（マイクロソフト）AMZN（アマゾン）  GOOGL（グーグル）
META（メタ）        SPY（S&P500 ETF） QQQ（ナスダック100）
```

`find_xstock` で任意のティッカーを検索できます。

---

## 注意事項

- **日本居住者への注意**: xStocks の売買には金融商品取引法上の規制が適用される可能性があります。本番取引前に専門家にご確認ください
- **為替リスク**: xStocks は USD 建て資産です
- **流動性リスク**: 価格インパクトが大きい場合は取引が拒否されます
- 本記事は技術解説であり、投資勧誘ではありません

---

## まとめ

| 項目 | 内容 |
|---|---|
| 証券口座 | 不要（Jupiter DEX は公開 AMM） |
| デフォルト | Dry-Run（実資金は動かない） |
| 安全機能 | 日次上限 + 詐欺フィルター + 価格インパクト上限 |
| 手数料 | $0.10 / 取引（定額） |
| 設定 | `npx -y xstocks-mcp` を Claude Desktop に追加するだけ |

Claude と自然言語で話すだけで米国株の価格確認・購入シミュレーション・本番購入まで一気通貫でできます。

- **npm**: https://www.npmjs.com/package/xstocks-mcp
