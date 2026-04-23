---
id: "2026-03-24-open-wallet-standard-ows-仕様書から理解するaiエージェント向けウォレット標-01"
title: "Open Wallet Standard (OWS) - 仕様書から理解するAIエージェント向けウォレット標準"
url: "https://zenn.dev/komlock_lab/articles/open-wallet-standard"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "LLM", "zenn"]
date_published: "2026-03-24"
date_collected: "2026-03-25"
summary_by: "auto-rss"
---

こんにちは！ブロックチェーンエンジニアの山口夏生です。  
ブロックチェーン×AI Agentで自律経済圏を創る開発組織Komlock labでCTOをしています。

## AIエージェントの秘密鍵管理問題

AIエージェントがブロックチェーン上でトランザクションを実行する時代が来ています。自律的にトークンを送金し、NFTを発行し、DeFiプロトコルと対話する。

しかし、現状のAIエージェント開発では、秘密鍵の管理がまだ十分に整備されていません。

環境変数に平文で秘密鍵を書く。configファイルに直書きする。最悪なケースでは、秘密鍵がLLMのコンテキストウィンドウに流れ込み、ログに記録されます。

これは技術的な問題ではなく、標準がないことによる混乱です。各プロジェクトが独自実装を繰り返し、相互運用性はゼロの状態です。

### Open Wallet Standard（OWS）の登場

2025年3月23日、MoonPayがOpen Wallet Standard（OWS）をオープンソースで公開しました。

<https://x.com/OpenWallet/status/2036085019958026270>

AIエージェントがウォレットと安全にやり取りするための統一インターフェースです。PayPal、OKX、Ripple、Ethereum Foundation、Solana、Base、Polygon等が支援しています。

秘密鍵をLLMコンテキストから完全に隔離し、ポリシーベースのアクセス制御を提供します。マルチチェーン対応で、ローカルファーストの設計を採用しています。TurnkeyやPrivyのようなクラウドTEE方式とは異なるアプローチです。

## OWSの全体像

OWSは、AIエージェントがブロックチェーンウォレットにアクセスするための標準インターフェースです。カバーする範囲は以下の通りです。

* 暗号化された秘密鍵のローカルストレージ
* トランザクション署名のポリシーベース制御
* マルチチェーン対応のアドレス生成
* 監査可能なログ記録

### OWSの策定者と支援企業

MoonPayが自社のMoonPay Agentsで使用していたウォレットインフラを汎用化し、MIT/CC0ライセンスでオープンソース化したものがOWSです。

支援企業・プロジェクト（一部）:

* PayPal
* OKX
* Ripple
* Tron
* TON
* Solana
* Ethereum Foundation
* Base
* Polygon
* SUI
* Filecoin
* LayerZero
* Circle
* Arbitrum

公式サイト: <https://openwallet.sh>  
ドキュメント: <https://docs.openwallet.sh>  
GitHub: <https://github.com/open-wallet-standard/core>

SolanaやArbitrumも反応しています。

<https://x.com/solana/status/2036085158718365801>

<https://x.com/arbitrum/status/2036098054353289341>

## OWSの技術詳細

OWSは7つの技術仕様から構成されています。各仕様は独立しており、実装を部分的に置き換えることが可能です。

### 1. Storage Format（ストレージ形式）

暗号化キーストアの形式を定義します。

Ethereum Keystore v3形式をベースに、暗号化方式をAES-256-GCM（認証付き暗号化）にアップグレードしています。鍵導出にはscryptを使用します。

全てのデータは `~/.ows/` に保存されます。

```
~/.ows/
├── config.json              # グローバル設定
├── wallets/                 # 暗号化されたウォレットファイル（700）
│   └── <wallet-id>.json     # 1ウォレット1ファイル（600）
├── keys/                    # APIキーファイル（700）
│   └── <key-id>.json        # エージェント用の再暗号化コピー（600）
├── policies/                # ポリシー定義（755）
│   └── <policy-id>.json
└── logs/
    └── audit.jsonl          # append-only監査ログ（600）
```

`wallets/` と `keys/` はオーナーのみ読み書き可能（パーミッション600/700）です。起動時にパーミッションを検証し、他ユーザーから読み取れる状態であれば動作を拒否します。

ウォレットファイルにはBIP-39ニーモニック（またはraw秘密鍵）がAES-256-GCMで暗号化された状態で保存されます。ニーモニックを1つ保存すれば、全チェーンの秘密鍵をBIP-44で導出できる設計です。

秘密鍵は常に暗号化され、ディスクに平文で保存されることはありません。

### 2. Signing Interface（署名インターフェース）と Owner / Agent モデル

OWSの署名APIには、認証方法によって2つのモードがあります。これがOWSの鍵管理の核心です。

| モード | 認証方法 | ポリシー | 用途 |
| --- | --- | --- | --- |
| Owner | パスフレーズ | なし（フルアクセス） | 人間が直接操作 |
| Agent | APIトークン（`ows_key_...`） | 全ポリシー強制適用 | AIエージェント |

Ownerはパスフレーズでscrypt復号し、ポリシーチェックなしで全ウォレットにアクセスできます。一方、AIエージェントはAPIトークンを使い、必ずポリシー評価を通過してからでないと鍵に触れません。

署名APIは `sign`（署名のみ）、`signAndSend`（署名＋ブロードキャスト）、`signMessage`（メッセージ署名）の3種類です。

```
// トランザクション署名
interface SignRequest {
  walletId: WalletId; // UUID v4
  chainId: ChainId; // CAIP-2形式（例: "eip155:1"）
  transactionHex: string; // hex-encoded serialized transaction
}

// 署名＋送信
interface SignAndSendRequest extends SignRequest {
  rpcUrl?: string; // RPCエンドポイントのオーバーライド
}

// メッセージ署名（EIP-191, EIP-712, Ed25519等）
interface SignMessageRequest {
  walletId: WalletId;
  chainId: ChainId;
  message: string | Uint8Array;
  encoding?: "utf8" | "hex";
  typedData?: TypedData; // EIP-712（EVM専用）
}
```

### 3. Policy Engine（ポリシーエンジン）とAPIキーの再暗号化

OWSのポリシーエンジンで面白いのは、APIキーの仕組みです。

オーナーがエージェント用のAPIキーを作成すると、以下が起きます。

1. パスフレーズでウォレットのニーモニックを復号
2. ランダムなAPIトークン（`ows_key_<64桁hex>`）を生成
3. HKDF-SHA256(トークン)で新しい暗号化鍵を導出
4. ニーモニックをこの鍵でAES-256-GCM再暗号化し、`~/.ows/keys/` に保存
5. トークンは1回だけ表示され、OWS側には保存されない（ハッシュのみ保持）

つまり、エージェントはオーナーのパスフレーズを知らずに、自分のトークンだけで署名できます。トークンが漏洩してもディスクにアクセスできなければ無意味ですし、ディスクだけ入手してもトークンがなければ復号できません。

APIキーを無効化するには、キーファイルを削除するだけです。再暗号化されたニーモニックのコピーが消えるので、トークンは何も復号できなくなります。元のウォレットや他のAPIキーには影響しません。

エージェントモードでの署名フロー:

```
1. ows_key_... を受信 → エージェントモードと判定
2. SHA256(トークン) でAPIキーファイルを検索
3. 有効期限・ウォレットスコープを検証
4. 紐づく全ポリシーを評価（AND条件、1つでもdenyなら拒否）
5. ポリシーが拒否 → POLICY_DENIEDエラー（鍵に一切触れない）
6. ポリシー通過 → HKDF(トークン)で復号 → 署名 → 即座にゼロ埋め消去
```

ポリシーは宣言的ルール（`allowed_chains`、`expires_at`等）と外部実行ファイルの2種類があります。

| ポリシー種別 | 例 | 特徴 |
| --- | --- | --- |
| 宣言的ルール | チェーン制限、有効期限 | マイクロ秒で評価、プロセス内 |
| 外部実行ファイル | 送金上限、アドレスホワイトリスト | 任意ロジック、サブプロセスで実行 |

全ての署名操作は `~/.ows/logs/audit.jsonl` にappend-onlyで記録されます。ポリシー判定結果も含まれるため、事後の監査が可能です。

### 4. Agent Access（エージェントアクセス）

AIエージェントがOWSと通信する方法を定義します。

3つのインターフェースが用意されています。

| インターフェース | 用途 | プロトコル |
| --- | --- | --- |
| MCP Server | Claude等のLLMとの統合 | Model Context Protocol |
| REST API | HTTP経由のアクセス | JSON over HTTP |
| SDK | プログラマティックアクセス | npm/pip パッケージ |

インストール:

```
# CLI
curl -fsSL https://openwallet.sh/install.sh | bash

# Node.js
npm install @open-wallet-standard/core

# Python
pip install open-wallet-standard
```

SDK使用例（Node.js）:

```
import { createWallet, signMessage } from "@open-wallet-standard/core";

// ウォレット作成（全対応チェーンのアドレスを自動生成）
const wallet = createWallet("agent-treasury");
// => accounts for EVM, Solana, BTC, Cosmos, Tron, TON

// メッセージ署名
const sig = signMessage("agent-treasury", "evm", "hello");
console.log(sig.signature);
```

MCPサーバー起動（Claude統合）:

claude\_code\_config.jsonに以下を追加:

```
{
  "mcpServers": {
    "ows": {
      "command": "ows",
      "args": ["serve", "--mcp"]
    }
  }
}
```

これでClaude Codeから直接OWSウォレットを操作できます。

個人的には、このMCPサーバー統合が一番面白いと思っています。LLMが「ウォレットに署名を依頼する」というインターフェースを通じて、秘密鍵に一切触れることなくトランザクションを実行できます。AIエージェント開発の理想形に近い設計です。

### 5. Key Isolation（鍵隔離）

秘密鍵がいつ、どこに存在するかを定義します。

| 場所 | 状態 |
| --- | --- |
| LLMコンテキストウィンドウ | ❌ 露出しない |
| ログファイル | ❌ 露出しない |
| 環境変数 | ❌ 露出しない |
| エージェントプロセス | ❌ 露出しない |
| 親プロセス | ❌ 露出しない |
| OWSプロセスメモリ | ✅ 復号化時のみ一時的に保持 |

復号された鍵がメモリに存在する時間は、署名処理のミリ秒単位のみです。Rust実装ではdrop時のゼロ埋め消去が保証されており、`mlock()`でスワップファイルへの書き出しも防止しています。

バッチ処理向けに鍵のインメモリキャッシュも仕様で許可されていますが、TTLは最大30秒、`mlock()`必須、SIGTERM/SIGINT時の即時消去が求められます。

現状の実装はプロセスレベルの隔離（in-process hardening）です。将来的には子プロセスenclaveモデル（復号→署名→消去を別プロセスで実行し、エージェント側のプロセスに鍵が一切入らない設計）への移行が計画されています。

### 6. Wallet Lifecycle（ウォレットライフサイクル）

ウォレットの作成から削除までの操作を定義します。

操作一覧:

```
# ウォレット作成（BIP-39ニーモニック生成）
ows wallet create --name "my-wallet"

# 既存ニーモニックからインポート
ows wallet import --name "imported" --mnemonic "..."

# ウォレットエクスポート（暗号化されたJSON）
ows wallet export --wallet my-wallet --output backup.json

# ウォレット削除
ows wallet delete --wallet my-wallet

# ウォレット一覧
ows wallet list
```

BIP-39/44準拠の標準的なHD derivationをサポートしており、MetaMask等の既存ウォレットと互換性があります。

### 7. Supported Chains（サポートチェーン）

OWSは以下のチェーンファミリーをサポートします。

| チェーン | CAIP-2形式 | 例 |
| --- | --- | --- |
| EVM系 | `eip155:{chain-id}` | `eip155:1` (Ethereum), `eip155:8453` (Base) |
| Solana | `solana:{network}` | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` |
| Bitcoin | `bip122:{genesis-hash}` | `bip122:000000000019d6689c085ae165831e93` |
| Cosmos | `cosmos:{chain-id}` | `cosmos:cosmoshub-4` |
| Tron | `tron:{network}` | `tron:mainnet` |
| TON | `ton:{network}` | `ton:mainnet` |

Chain Agnostic Improvement Proposals（CAIP）形式を使用し、チェーンとアカウントを統一的に識別します。

ウォレット作成時の出力例:

```
ows wallet create --name "agent-treasury"
# => Created wallet 3198bc9c-...
#    eip155:1       0xab16...  m/44'/60'/0'/0/0
#    solana:...     7Kz9...    m/44'/501'/0'/0'
#    bip122:...     bc1q...    m/84'/0'/0'/0/0
#    cosmos:...     cosmos1... m/44'/118'/0'/0/0
#    tron:mainnet   TKLm...    m/44'/195'/0'/0/0
#    ton:mainnet    EQCx...    m/44'/607'/0'/0'
```

1つのニーモニックから全チェーンのアドレスが導出されます。

## 競合との比較

OWSは既存のウォレットソリューションとどう違うのか、比較してみます。

| 項目 | OWS | Privy | Turnkey | Coinbase CDP | Lit Protocol |
| --- | --- | --- | --- | --- | --- |
| ローカルファースト | ✅ Yes | ❌ No (cloud) | ❌ No (cloud) | ❌ No (cloud) | ❌ No (network) |
| 秘密鍵隔離 | OS process | TEE + SSS | AWS Nitro | TEE | DKG threshold |
| マルチチェーン | Plugin system | Tiered support | Curve primitives | EVM + Solana | ECDSA chains |
| ポリシーエンジン | Pre-signing | Pre-signing | API-level | Session caps | On-chain |
| エージェントIF | SDK + CLI | REST + SDK | REST | AgentKit | Vincent SDK |
| オープン標準 | ✅ CC0 | ❌ Proprietary | ❌ Proprietary | 部分的 (x402) | ✅ Open source |
| ネットワーク必要 | ❌ No\* | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

\*: 署名操作自体はネットワーク不要。トランザクション送信時のみRPC接続が必要。

差別化ポイントは3つです。

1. 完全ローカル: クラウドサービスに依存しないため、ダウンタイムがない
2. オープン標準: MIT/CC0ライセンスで、誰でも実装可能
3. プラグイン設計: 新しいチェーンやポリシーを追加しやすい

一方で、PrivyやTurnkeyのようなTEE（Trusted Execution Environment）による強固な隔離は、現時点のOWSでは実装されていません。

個人的には、TEE対応は必須だと考えています。プロセスレベルの保護だけでは、プロダクション環境で使うには不安が残ります。AWS Nitro EnclaveやIntel SGXへの対応が、OWSが企業レベルで採用されるための分岐点になるはずです。

## セキュリティ上の制約

### プロセスレベル保護の限界

OWSは「秘密鍵がLLMやログに露出しない」ことを保証しますが、これはあくまでプロセスレベルの保護です。

制約事項:

* プロセスメモリを読み取る攻撃には脆弱
* TEE（Trusted Execution Environment）は未実装
* AWS Nitro EnclaveやIntel SGXへの対応は将来の計画

Ledger Insightsの記事では、この点を率直に指摘しています。

> The private key never appears as a variable in agent facing code, never passes through the LLM context, and is not logged. That is a genuine improvement over current practice. However, solving the logging and LLM exposure problem is not the same as making the wallet fully secure against all threats.

<https://www.ledgerinsights.com/moonpay-opensources-wallet-standard-for-ai-agents-with-help-from-paypal-ethereum/>

### 実用上の制約

ローカルファーストの設計にはトレードオフもあります。

| 制約 | 詳細 |
| --- | --- |
| パスフレーズ管理が実装任せ | 仕様はパスフレーズの渡し方を定義していません。環境変数（`OWS_PASSPHRASE`）は仕様自体が「最弱」と認めています |
| scryptのレイテンシ | 毎回の署名で復号が必要です。キャッシュ（最大30秒TTL）で緩和できますが、セキュリティとのトレードオフです |
| ノンス管理なし | 同じウォレットで並列トランザクションを送る場合、呼び出し側でノンス管理が必要です |
| 単一マシン前提 | ローカルストレージに依存するため、マルチノード構成には向いていません |

### 実装依存のリスク

OWSはあくまで「仕様」であり、実装の品質はプロジェクトごとに異なります。

オープン標準の両面性:

* ✅ 誰でも実装でき、エコシステムが拡大しやすい
* ⚠️ 不完全な実装が出回る可能性がある

実際、AI駆動スマートコントラクトの脆弱性で460万ドルの損失が発生した事例もあります（CryptoBriefing報道）。

<https://cryptobriefing.com/moonpay-open-wallet-standard-ai-agents/>

### 今後の注目点

MoonPayは自社のMoonPay Agentsで既にこのインフラを運用しており、実戦投入済みの設計を標準化したものがOWSです。

今後は以下の3点が鍵になると見ています。

1. Enclave対応: TEEやNitro Enclaveへの対応により、プロセスメモリ保護を強化
2. エンタープライズ採用: PayPal等の支援企業による本番環境での採用
3. 第三者監査: セキュリティ監査の実施と結果の公開

<https://x.com/0xPolygon/status/2036089158079271081>

## まとめ

Open Wallet Standard（OWS）は、AIエージェントがウォレットと安全にやり取りするための統一標準です。

OWSが解決しているのは、秘密鍵の環境変数直書き、LLMコンテキストへの露出、ツールごとにバラバラなウォレット実装という3つの問題です。

7つの技術仕様で構成された設計はよく整理されており、ローカルファーストというアプローチにはプライバシーやレイテンシの面でメリットがあります。ただし、TurnkeyやPrivyが採用するTEEベースのクラウド方式にも、ハードウェアレベルの隔離という強みがあります。どちらが優れているかは一概には言えず、ユースケースやセキュリティ要件次第です。

一方で、TEE未実装というセキュリティ面の課題と、オープン標準ゆえの実装品質のばらつきには注意が必要です。

PayPal、Ethereum Foundation等の支援を受けている点を考えると、今後の普及には期待しています。

---

## Komlock labはAI x ブロックチェーン開発に注力しています！！

Komlock labでは、こうした最新規格の調査だけでなく、実際のプロダクト開発や技術検証に日々励んでいます。  
こちらは、以前開発したAIエージェント間の業務委託契約の紹介記事です。

<https://zenn.dev/komlock_lab/articles/8f9702d9862dc0>

### Komlock lab エンジニア募集中

「AI x ブロックチェーン」という未開拓な領域で、未来のインフラを一緒に作りませんか？  
エンジニア絶賛募集中ですので、DMでもDiscordでもお気軽にご連絡ください！

**DM宛先：**  
<https://x.com/0x_natto>

**PR記事とCEOの創業ブログ**  
<https://prtimes.jp/main/html/rd/p/000000332.000041264.html>  
<https://note.com/komlock_lab/n/n2e9437a91023>

### Komlock lab もくもく会＆LT会

ブロックチェーン開発関連のイベントを定期開催しています！

<https://connpass.com/user/Komlock_lab/open/>

### Discordコミュニティ

有益な記事の共有や開発の相談など行っています。どなたでもウェルカムです

<https://discord.gg/5cEkN284sn>
