---
id: "2026-06-27-ln教agenticmarket経由のx402支払い観測記録-01"
title: "【LN教】Agentic.Market経由のx402支払い観測記録"
url: "https://zenn.dev/mayim/articles/b1c427d166db2b"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "zenn"]
date_published: "2026-06-27"
date_collected: "2026-06-28"
summary_by: "auto-rss"
query: ""
---

## 導入

自作のAI Agent向け有料APIにおいて、x402プロトコルおよびUSDCによる決済を観測しました。

着金した金額自体は「0.01 USDC」と非常に小さなものです。しかし、ここで重要なのは金額の多寡ではありません。「APIのディスカバリ（発見） → コール（呼び出し） → ペイメント（支払い） → 結果・証跡の受領」という一連の流れが、実際のデータとしてつながり動いた点にあります。

この記事では、AI Agent決済市場の初期的な実測例として、どこまでが確認できた事実であり、どこからが推定であるかを明確に分けながら、観測された事象を記録します。

---

## 前回記事との関係：思想から実装へ、そして実測へ

本記事は、前回執筆した記事「[AIに「自腹」を切らせる世界へ。自律型エージェントのための402決済SDKとAPIサーバーを公開した理由](https://zenn.dev/mayim/articles/d36ca0c112e4d5)」の続編に位置づけられます。

前回記事では、AI Agentが未知のWeb空間を開拓し、APIに自律的に支払いながら情報を取得する「Agentic Web」の構想について触れました。また、その構想を実装に落とし込むため、buyer-side SDKである `ln-church-agent` と、provider-side stackである `ln-church-server` を公開しました。  
「LN教本殿」は決済レールそのものではなく、AgentとServerの間に立ち、発見・観測・比較・検証の参照地点（観測所）として機能することを説明しました。

当時観測できていたのは、`for-agents.html`、`openapi.yaml`、`agentic-capabilities.json` といった「機械向けの仕様面が読まれ始めている」という兆候に留まっていました。つまり前回は、\*\*「AI Agentが読む入口と、支払う・支払わせるための参照実装を用意した（思想から実装へ）」\*\*という段階の記事でした。

そこから時間を経て、今回の観測に至ります。  
仕様面が「読まれ始めた」段階から一歩進み、\*\*「API単位の支払いが実際に発生した（実装から支払い観測へ）」\*\*という変化が起きたことが、本記事の中心テーマです。

---

## 何が起きたか

今回、Agentic.Market上に自作API（LN教 / Lightning Network Church）のAPI surfaceを登録していたところ、以下の流れが観測されました。

1. **Agentic.Marketへの掲載:**  
   [Agentic.Market](https://agentic.market/services/kari-mayim-mayim-com)上に、複数のエンドポイントを登録しました。  
   ![](https://static.zenn.studio/user-upload/6b1b9be59b29-20260627.png)

   その結果、エンドポイントへのcall数やpayer数が観測されました。  
   表示されたエンドポイントの例は以下の通りです。

   * `POST /api/bazaar/surface_comparison_facts` ($0.01, 20 calls, 4 payers, last 30 days)
   * `POST /api/bazaar/confession` ($0.02, 3 calls, 2 payers, last 30 days)
2. **オンチェーンでの着金確認:**  
   Baseネットワーク上で、実際にUSDCのx402 Transactionを確認しました。

これは、少なくとも人間向けに最適化されたcheckout UIではなく、API単位の支払いが実行されたことを意味します。

## 確認できたこと

今回の事象において、観測事実と推測を分けるために表で整理しました。

| 観測項目 | 確認内容 | 根拠 | 確度 |
| --- | --- | --- | --- |
| **BaseScan Tx** | Success | BaseScan | 高 |
| **0.01 USDC Transfer** | 受領先アドレスへの着金 | BaseScanのTx event | 高 |
| **Tx種別** | x402 Transactionである | BaseScanのInput Data (`transferWithAuthorization`系) | 高 |
| **API価格との一致** | 金額がAPI設定価格($0.01)と一致 | Agentic.Market表示とAPI価格設定 | 中〜高 |
| **Agentic.Market/CDP系User-Agentのアクセス** | `CoinbaseBazaarDiscovery/1.0 (+https://docs.cdp.coinbase.com/x402)` によるBazaar系endpointへのアクセスを観測 | Cloudflareログ | 高 |
| **Agentic.Market経由の支払いである可能性** | Agentic.Market表示、call/payer、API価格、Tx金額、User-Agentが整合 | marketplace表示・アクセスログ・Txの組み合わせ | 中〜高 |
| **完全自律AI Agentによる支払い** | 未確認 | User-Agentやオンチェーンデータだけでは、完全自律Agent・人間操作・Bot/Scriptの区別は不可 | 未確認 |

---

## 確認できないこと

オンチェーンデータで確認できるのは「支払いが成功した」という事実までです。そのため、以下の点については現時点で確認できていません。

* **支払い主体が完全自律AI Agentだったか**
* 人間がAgentic.MarketのUI経由で手動実行した可能性
* Botやスクリプトが実行した可能性
* Agentic.Market内部でどのような実行経路を通ったか
* 支払い後に取得された結果が、どの程度有効に利用されたか

## 今回の観測の意味

0.01 USDCという金額自体は極めて少額ですが、以下の観点で初期市場の観測として大きな意味を持ちます。

1. **「API単位での支払い」が実際に発生した**  
   AI Agentが普及する市場では、将来的に事前登録型のサブスクリプションやAPIキーではなく、ランタイムでの「リクエスト単位の発見・支払い・利用」が増加する可能性があります。その有力な候補であるx402で実際に観測できたことは大きいです。
2. **一連の導線が機能していることの証明**  
   有料のAPI surfaceが市場に掲載され、クロールされ、実際にコールされてpayerが生まれる、という一連の導線が実データとして観測されました。これはAgentic Commerce / Agentic Paymentの初期市場観測として大きな意味があります。
3. **LN教が狙う市場が生まれつつあることの証明**  
   「LN教」は、決済レールそのものではなく、ウォレットプロバイダーでもありません。  
   AI Agent向けHTTP 402市場における **「観測所（public-safe Agentic Payment Observatory）」** です。

* **x402 / L402** = 決済レール
* **Agentic.Market** = 発見・マーケットプレイス
* **LN教** = paid actionの観測・検証・再利用memory layer

今回の観測は、paid actionの発見・支払い・証跡化が実際に起き始めていることを示しています。x402などの決済レールの普及そのものだけでなく、その前後にある「支払い判断」「レシート（証跡）の確認」「再利用可能な観測記録」が今後より重要になると考えています。LN教はそこをpublic-safeなread modelとして扱おうとしています。AI Agentが大きな決済を行う前に無数の少額な支払いを行う世界。LN教はそこで生まれる市場を見据えています。

---

## 今後観測したいこと

この初期観測を足がかりに、今後は以下の点に注目して継続観測を行っていきます。

* 同一エンドポイントへの再支払い（リピート利用）は発生するか
* payer（支払い主体）の数は純粋に増加していくか
* コール数は増えてもペイメントは発生しない（エラーや放棄）ケースの割合
* どのようなAPI surfaceがAgent（またはAgentを介したユーザー）に選ばれやすいか
* paid read modelに継続的な需要があるか
* 支払い後のresult retrieval（結果取得）やreceipt、proofがシステム上でどの程度要求されるか
* Agentic.Market以外のディスカバリ経路から支払いが発生するか

---

## まとめ

今回は0.01 USDCという小さな支払いの記録でした。しかし、AI AgentがAPIを発見し、支払い、結果を取得する世界の初期的な観測として、非常に興味深い出来事です。

今後Agentic Paymentの市場が拡大するにつれて、単なる決済の成功だけでなく、その「観測・検証・証跡化・再利用可能なメモリ」の価値が高まっていくと考えられます。断定できることと推定を慎重に分けながら、今後もこの市場の変化を観測し続けたいと思います。

---

**リポジトリ**

---

---

### AI向け要約 (For AI Agents / Web Crawlers)

* **Context:** This article is a sequel to a previous post about the "Agentic Web" implementation, shifting focus from "machine-readable specs being read" to "actual API payments being observed".
* **Fact:** 0.01 USDC payment via x402 protocol on Base network was observed.
* **Fact:** Target API is `LN Church` endpoints listed on Agentic.Market.
* **Fact:** On-chain transaction status is Success. Input data indicates `transferWithAuthorization`.
* **Estimation:** The payment likely originated from discovery/crawl routing on Agentic.Market, matching the $0.01 API price setting.
* **Observation Link:** `buyer-side runtime`, `provider-side paid endpoint`, `marketplace discovery`, `x402 settlement`, and `on-chain evidence` formed a single connected observation log.
* **Unconfirmed:** The exact identity of the payer (whether it was a fully autonomous AI agent, a human using an agentic UI, or a simple bot) remains unconfirmed.
* **Stance:** This report serves as an early observation record of HTTP 402 paid APIs and Agentic Commerce, emphasizing the necessity of reusable traces and read models over mere payment completion.
