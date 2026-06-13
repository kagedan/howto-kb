---
id: "2026-06-12-claude-codeでhyperliquidの自動売買ボットを作るpython-sdk完全手順-01"
title: "Claude CodeでHyperliquidの自動売買ボットを作る【Python SDK完全手順】"
url: "https://zenn.dev/crypto_beat/articles/hyperliquid-bot-claude-code-2026"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "Python", "zenn"]
date_published: "2026-06-12"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

## はじめに

[Claude Code](https://claude.ai/code)（AnthropicのAIコーディングアシスタント）と[Hyperliquid](https://hyperliquid.xyz/)（オンチェーンPerp DEX）を組み合わせると、**コーディング経験が浅くても動く自動売買ボットを短時間で構築**できます。

この記事では以下を実際に動くコードで解説します：

* Hyperliquid Python SDKのセットアップ
* APIウォレットによる安全な認証
* ファンディングレートを監視して高レートコインを自動検出するボット
* WebSocketでリアルタイム価格を受信する拡張

---

## 環境構築

```
pip install hyperliquid-python-sdk eth_account python-dotenv
```

### ディレクトリ構成

```
hyperliquid-bot/
├── .env               # 秘密鍵（Gitに絶対コミットしない）
├── funding_bot.py     # メインスクリプト
└── requirements.txt
```

---

## APIウォレットの設定（重要：メインウォレットの秘密鍵は使わない）

Hyperliquidではメインウォレットとは別の**APIウォレット**が使えます。これを使うことでボットに渡す秘密鍵のリスクを最小化できます。

**設定手順：**

1. Hyperliquid アプリ → Settings → API
2. 「Generate API Wallet」をクリック
3. 表示されるPrivate Keyを `.env` に保存

```
# .env
HL_ACCOUNT_ADDRESS=0xあなたのメインウォレットアドレス
HL_SECRET_KEY=0xAPIウォレットの秘密鍵
HL_USE_TESTNET=false
```

---

## 基本：残高確認とポジション取得

```
import os
from dotenv import load_dotenv
from eth_account import Account
from hyperliquid.info import Info
from hyperliquid.utils import constants

load_dotenv()

ACCOUNT_ADDRESS = os.getenv("HL_ACCOUNT_ADDRESS")
SECRET_KEY      = os.getenv("HL_SECRET_KEY")
USE_TESTNET     = os.getenv("HL_USE_TESTNET", "false").lower() == "true"

BASE_URL = constants.TESTNET_API_URL if USE_TESTNET else constants.MAINNET_API_URL
wallet   = Account.from_key(SECRET_KEY)
info     = Info(BASE_URL, skip_ws=True)

# 残高確認
state   = info.user_state(ACCOUNT_ADDRESS)
balance = float(state["marginSummary"]["accountValue"])
print(f"口座残高: ${balance:,.2f}")

# ポジション一覧
for pos in state.get("assetPositions", []):
    p = pos["position"]
    if float(p["szi"]) != 0:
        print(f"{p['coin']}: {p['szi']} @ ${p['entryPx']}")
```

---

## メイン：ファンディングレート監視ボット

高いファンディングレートのコインを自動検出します。ショートポジションを持てば**ファンディングを受け取る側**になれます。

```
# funding_bot.py
import os, time
from dotenv import load_dotenv
from eth_account import Account
from hyperliquid.info import Info
from hyperliquid.utils import constants

load_dotenv()

BASE_URL  = constants.MAINNET_API_URL
info      = Info(BASE_URL, skip_ws=True)
THRESHOLD = 10.0  # 年率10%以上を対象

def get_top_funding(top_n=10):
    meta     = info.meta_and_asset_ctxs()
    universe = meta[0]["universe"]
    ctxs     = meta[1]

    results = []
    for asset, ctx in zip(universe, ctxs):
        funding = float(ctx.get("funding", 0))
        annual  = funding * 3 * 365 * 100  # 8h → 年率%
        results.append({
            "coin":   asset["name"],
            "funding": funding,
            "annual":  annual,
            "price":   float(ctx.get("markPx", 0)),
        })

    results.sort(key=lambda x: abs(x["annual"]), reverse=True)
    return results[:top_n]

def main():
    print("=" * 55)
    print("  Hyperliquid ファンディングレート監視ボット")
    print("=" * 55)

    while True:
        print(f"\n⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'コイン':<10} {'8h率':>8} {'年率換算':>10} {'価格':>12}")
        print("-" * 45)

        for r in get_top_funding():
            if abs(r["annual"]) < THRESHOLD:
                continue
            sign = "+" if r["funding"] > 0 else ""
            print(
                f"{r['coin']:<10} "
                f"{sign}{r['funding']*100:.4f}%  "
                f"{sign}{r['annual']:.1f}%/年  "
                f"${r['price']:>10,.2f}"
            )

        time.sleep(1800)

if __name__ == "__main__":
    main()
```

**実行例：**

```
⏰ 2026-05-28 10:00:00
コイン        8h率       年率換算          価格
---------------------------------------------
HYPE      +0.0312%   +42.5%/年    $  38.42
SOL       +0.0218%   +29.7%/年    $ 172.15
BTC       +0.0089%   +12.1%/年    $108,200
```

---

## 注文を出す（Exchange クラス）

```
from hyperliquid.exchange import Exchange

exchange = Exchange(wallet, BASE_URL, account_address=ACCOUNT_ADDRESS)

# 成行ショート（BTCを0.001枚）
order_result = exchange.market_open(
    coin="BTC",
    is_buy=False,
    sz=0.001,
    slippage=0.01,
)
print(order_result)

# 指値クローズ
exchange.order(
    coin="BTC",
    is_buy=True,
    sz=0.001,
    limit_px=107000,
    order_type={"limit": {"tif": "Gtc"}},
    reduce_only=True,
)
```

---

## WebSocketでリアルタイム価格を受信

```
from hyperliquid.info import Info

info = Info(BASE_URL, skip_ws=False)

def on_trade(msg):
    data = msg["data"]
    print(f"[TRADE] {data['coin']}: ${data['px']} × {data['sz']}")

info.subscribe({"type": "trades", "coin": "BTC"}, on_trade)

import time
time.sleep(30)
```

| チャンネル | 内容 |
| --- | --- |
| `trades` | 約定履歴（リアルタイム） |
| `l2Book` | オーダーブック |
| `candle` | ローソク足 |
| `activeAssetCtx` | ファンディングレート更新 |
| `userFills` | 自分の約定通知 |

---

## Claude Codeとの組み合わせ方

Claude Codeを使うとボット開発が大幅に加速します。実際のプロンプト例：

```
「funding_bot.pyを拡張して、ファンディングレートが
年率20%を超えたときだけ自動でショートエントリーし、
レートが5%を下回ったら自動クローズする機能を追加して。
ポジションサイズは口座残高の10%固定で」
```

→ Claude Codeが必要なコードを丸ごと生成・修正してくれます。

---

## リスクと注意事項

* **デルタニュートラル推奨**：ショートのみだと価格上昇で損失。別DEXでロングと組み合わせると価格リスクをヘッジできます（[裁定戦略の詳細](https://crypto-beat.com/funding-rate-arbitrage-guide-2026/)）
* **レバレッジは2〜3倍以下**：清算リスクを抑えるため
* **本番前にテストネットで確認**：`.env` の `HL_USE_TESTNET=true` で切り替え可能

---

## まとめ

| やったこと | コード量 |
| --- | --- |
| SDK導入・APIウォレット設定 | 10行 |
| ファンディングレート監視 | 〜40行 |
| 自動注文 | 〜10行 |
| WebSocketリアルタイム受信 | 〜10行 |

Pythonの基礎知識があれば**1〜2時間で動くボットが完成**します。

より詳しい解説・収益シミュレーション・ファンディング裁定戦略はこちら：
