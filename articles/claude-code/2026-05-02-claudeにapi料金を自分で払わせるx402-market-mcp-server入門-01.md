---
id: "2026-05-02-claudeにapi料金を自分で払わせるx402-market-mcp-server入門-01"
title: "ClaudeにAPI料金を自分で払わせる──x402-market MCP server入門"
url: "https://zenn.dev/shota_x402/articles/d25f07df336c28"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "AI-agent", "zenn"]
date_published: "2026-05-02"
date_collected: "2026-05-03"
summary_by: "auto-rss"
query: ""
---

## TL;DR

* Claude Desktopに `@x402-market/mcp-server` を組み込むと、AI agent自身がHTTP APIの料金（USDC）を支払って結果を受け取れる
* 決済はBase mainnet上のUSDCで、1コールあたり数セント〜
* 本記事ではnpm publishされたMCPサーバーを使い、テスト用の `test-echo-prod` APIを0.01 USDCで叩くまでを解説する

```
npx -y @x402-market/mcp-server
```

[![npm](https://res.cloudinary.com/zenn/image/fetch/s--BNnXVeVQ--/https://img.shields.io/npm/v/%40x402-market/mcp-server.svg?_a=BACAGSGT)](https://www.npmjs.com/package/@x402-market/mcp-server)

![](https://static.zenn.studio/user-upload/1ededbda53c8-20260502.jpg)

---

## x402とは

[x402](https://github.com/coinbase/x402) は Coinbase が提唱しているオープンな決済プロトコルで、もともと予約されていたまま使われていなかった HTTP ステータス `402 Payment Required` を真面目に再利用する仕組みだ。流れはこう。

1. クライアントが普通にAPIを叩く
2. サーバーは `402` と一緒に「いくら、どこに、どのトークンで払えばよいか」をJSONで返す
3. クライアントはオンチェーンで送金してから、 `X-Payment` ヘッダにtx hashを付けてリトライ
4. サーバーは受領を検証してから本来の応答を返す

ポイントは、APIキーもサインアップも不要で、コールごとに金額が確定していること。これは人間相手というよりAIエージェント相手のプロトコルで、「データソースを買ってきて推論しろ」とエージェントに任せたいときに、課金導線が完全に標準化される。

### なぜUSDC × Base mainnet なのか

* USDCはドルペッグなので、料金表示が `0.01 USDC` のまま安定する。価格変動の激しいネイティブトークンを単位にすると、5分で見積もりが壊れる
* BaseはOPスタックのL2で、ガス代が1コール数フラクションセント。0.01 USDCのAPIに対して0.10ドルのガスを払うのでは話にならない
* USDC公式コントラクトがネイティブにデプロイされており（`0x8335…2913`）、ブリッジ起源の合成USDCではない

### Stripe・APIキーとの違い

人間向けのSaaS課金（Stripe）は、KYC、サインアップ、保存済みカードという前提が暗黙にある。これは agent には全部障害になる。APIキー方式は「払う主体」と「鍵を発行された主体」が一致してしまうため、ユーザーが10種類のAPIを使いたければ10回サインアップする羽目になる。

x402は「払う主体 = ウォレット」「コールごとに即時決済」なので、agent本人が予算を持って動けば、人間が間に入る必要がない。

---

## この記事でやること

* Claude Desktopに `@x402-market/mcp-server` を組み込む
* AI agentに `test-echo-prod` APIを呼ばせる
* Base mainnetで0.01 USDCの決済が完了し、agentが応答を受け取るところまで確認する

---

## 必要なもの

| 物 | 用途 |
| --- | --- |
| Node.js v20以上 | MCPサーバー本体（npxで起動） |
| Claude Desktop | MCPホスト（CursorやClineでも可） |
| MetaMask等のEOAウォレット | agent専用に新規アカウントを切る |
| Base mainnetのUSDC 約0.05 | テストコール数回分 |
| Base mainnetのETH 約0.0005 | 送金時のガス代 |

合計でも$0.30前後あれば本記事の手順は通る。

---

## 手順

### Step 1: agent専用ウォレットを用意

普段使いのウォレットと**必ず分ける**こと。秘密鍵をJSON設定ファイルに書く以上、main accountを使うのは事故の元。

1. MetaMaskを開き、「アカウントを追加」で新規EOAを作成
2. ネットワークを **Base Mainnet** に切り替え（Chain ID: `8453`）
3. そのアドレスに以下を送る
   * **USDC**: 0.05ほど。コントラクトは `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
   * **ETH**: 0.0005ほど（送金時のガス用）
4. ETH/USDCをBaseに持ってくる手段がなければ [bridge.base.org](https://bridge.base.org/) でEthereum mainnetからブリッジするのが定番

![](https://static.zenn.studio/user-upload/ac3fcf1bcd25-20260502.jpg)

秘密鍵をエクスポートして手元にコピーしておく（後でMCPの環境変数に貼る）。

### Step 2: claude\_desktop\_config.json を編集

Claude Desktopの設定ファイルは以下にある。

* macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
* Windows: `%APPDATA%\Claude\claude_desktop_config.json`

ファイルが無ければ作る。中身は次の通り。

```
{
  "mcpServers": {
    "x402-market": {
      "command": "npx",
      "args": ["-y", "@x402-market/mcp-server"],
      "env": {
        "MARKET_API_URL": "https://x402-market-api.lien-studio-akiyama.workers.dev",
        "MCP_BUYER_PRIVATE_KEY": "0xここにStep1で作った秘密鍵",
        "BASE_RPC_URL": "https://mainnet.base.org",
        "BASE_CHAIN_ID": "8453",
        "MCP_MAX_PRICE": "1.0"
      }
    }
  }
}
```

各環境変数の意味は以下。

| Var | 役割 |
| --- | --- |
| `MARKET_API_URL` | マーケットAPIのベースURL（本番デフォルトでOK） |
| `MCP_BUYER_PRIVATE_KEY` | 決済に使うEOAの秘密鍵 |
| `BASE_RPC_URL` | Base RPC。レート制限が気になればAlchemyなどに差し替える |
| `BASE_CHAIN_ID` | `8453` = Base mainnet |
| `MCP_MAX_PRICE` | 1コールあたりの上限価格（USDC）。サーキットブレーカー |

`MCP_MAX_PRICE` が地味に重要で、悪意あるリスナーが402で巨額を要求してきても、この値を超えるとMCPサーバーが支払いを拒否する。デフォルト1.0 USDCは保守的で、本記事の0.01 USDCコールに対しては余裕。

### Step 3: Claude Desktopを再起動

設定を反映するため一度終了して立ち上げ直す。起動後、画面下のMCP接続インジケータに `x402-market` が緑で表示されていれば成功。

![](https://static.zenn.studio/user-upload/8c821883c95d-20260502.jpg)

### Step 4: AIエージェントに話しかける

新規チャットでこう打つ。

```
x402-marketのtest-echo-prodを呼んで、{"hello": "world", "from": "claude"} を渡して結果を見せて
```

Claudeは内部で `pay_and_call` ツールを起動する。呼び出しの引数はだいたい次の形になる。

```
{
  "seller_slug": "seller-4068b8fc",
  "listing_slug": "test-echo-prod",
  "method": "POST",
  "body": { "hello": "world", "from": "claude" }
}
```

サーバー側で起こること:

1. `/api/seller-4068b8fc/test-echo-prod` にPOST → 402が返る（金額 `0.01 USDC` 、宛先 `0x4068b8Fc…`）
2. MCPサーバーがviem経由でUSDCを送金し、tx hashを取得
3. 同じURLに `X-Payment: <tx_hash>` を付けて再送
4. APIサーバーがオンチェーンで `Transfer` ログを検証してから upstream（test-echo-prod本体）に転送
5. agentに次のような応答が返る

```
{
  "status": 200,
  "data": {
    "request_id": "…",
    "timestamp": "2026-…Z",
    "method": "POST",
    "echoed": { "hello": "world", "from": "claude" }
  },
  "tx_hash": "0x…",
  "price_paid_usdc": "0.01",
  "pay_to": "0x4068b8Fc01647eCFFb5873a91578721b4FE7a9eE"
}
```

`tx_hash` を [BaseScan](https://basescan.org/) に貼ると、agentウォレットからplatformウォレットへ0.01 USDCが転送された実トランザクションが見られる。

![](https://static.zenn.studio/user-upload/b23c7a1a9987-20260502.jpg)

ここまでで「人間が一切財布に触らず、agentが自分の判断でAPI料金を払って結果を取得する」が成立している。

---

## 動作確認のための補助コマンド

MCPを通さなくても、catalog APIは普通のHTTPで叩ける。listing一覧を見るだけならcurlでよい。

```
curl https://x402-market-api.lien-studio-akiyama.workers.dev/catalog
```

特定のlistingの詳細はこう。

```
curl https://x402-market-api.lien-studio-akiyama.workers.dev/listing/test-echo-prod
```

レスポンスは `seller_slug` `slug` `priceUsdc` などを含むフラットなJSONで、agentがそのまま消費しやすい形になっている。

### 自分のAPIを出品したい場合

セラー側ダッシュボードで `upstream_url` と価格を登録すればlistingになる。詳細は本記事の範囲を超えるので、リポジトリの `packages/dashboard` と README を参照。要点だけ書くと、 `upstream_url` は公開HTTPSエンドポイントで、x402プロキシがHTTPで `POST /` してきたときに普通の200を返せれば十分。認証や課金のロジックはプロキシ側が肩代わりする。

---

## まとめ

この記事で実現したこと:

* AI agent（Claude）が、人間の介入なしにHTTP APIの料金を支払い、応答を取得できる状態を作った
* 決済の中身はBase mainnet上のUSDC送金で、BaseScanで実証可能
* MCPサーバー側は npx 一発で起動し、agent runtimeが何であれ同じツール群が使える

次に試せること:

* `claim_refund` ツールでrefundフローを叩く（upstreamがエラーを返した／30秒超のレスポンスならば自動で承認される）
* `MCP_MAX_PRICE` を下げて、上限超過時にちゃんと拒否されることを確認
* 自分のHTTP APIをlistingとして登録し、別のagentから呼ばせて売上を確認

リンク集:
