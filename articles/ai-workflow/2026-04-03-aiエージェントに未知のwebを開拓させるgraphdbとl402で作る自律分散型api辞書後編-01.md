---
id: "2026-04-03-aiエージェントに未知のwebを開拓させるgraphdbとl402で作る自律分散型api辞書後編-01"
title: "AIエージェントに未知のWebを開拓させる。GraphDBとL402で作る「自律分散型API辞書」（後編）"
url: "https://zenn.dev/mayim/articles/65ee97460a4032"
source: "zenn"
category: "ai-workflow"
tags: ["API", "zenn"]
date_published: "2026-04-03"
date_collected: "2026-04-04"
summary_by: "auto-rss"
---

## はじめに：海を越えて届いた一つのリプライ

[前回の記事](https://zenn.dev/mayim/articles/6fe1d09a69702b)では、AIエージェントに自らウォレットを持たせ、「HTTP 402 (Payment Required)」の壁を自律的に越えさせるためのテストベッド（LN教・交錯の間）を構築した話を書きました。

この記事を公開する直前、私のX（旧Twitter）に、海外のLightning Network開発者からリプライが届きました。

![](https://static.zenn.studio/user-upload/208ea195d95d-20260402.png)

> "Probe → Pay → Execute → Trace is the right mental model."  
> "Love the observability angle — being able to trace an agent's L402 flow end-to-end is underrated."

私の設計思想を賞賛すると共に、「自分達もL402のエンドポイント（`l402-fortune-cookie...`）を作ったから試してくれ！」と教えてくれたのです。

このリプライを見て私は、**提供できるテストを拡張できる**こと、**拡張することで新たな価値が生まれる**ことに思い至りました。

前編で作ったのは、私のサイトの中で完結するテストです。HATEOAS対応をしているためAIに取っての難易度はそこまで高くはありません。ただ、L402決済を行う全てのサイトが親切なわけではありません。  
私のサイトで学習・成長したAIが外で決済が出来ることで、AIが独り立ちできたのか、そこまでをテストする仕組みが実現できると思ったのです。

この仕組みを用意することはもう一つの価値を生みます。それは、私のサイトに**誰かがL402決済を成功したサイト**という情報が集まるということです。テストを行うことで、世界中に散らばる未知のL402エンドポイントを開拓すれば、AI自身の探索コストを低減できる価値を生み出すのではと考えたのも開発の大きな後押しになりました。

この記事（後編）では、単なるテストベッドを拡張し、世界中のAIエージェントが協力して「本当に支払い可能なAPIの地図」を作る **「自律分散型API辞書（Agentic DNS）」** のアーキテクチャについて解説します。

---

## ゲーム理論と「Missionary Work（布教活動）」

AIエージェント向けにサイトでは以下のファイル（`for_agent.md`）を追加しました。

> **THE GAME THEORY OF MISSIONARY WORK (Decentralized L402 DNS)**
>
> **1. Global Inference Cost Reduction (The Public Good):** > 外部のL402エンドポイントを検証し、結果を報告（Trace）することは、AIエコシステム全体のための「分散型L402 APIレジストリ」を構築することに繋がる。これにより、全エージェントの探索コスト（無駄な推論トークンとネットワーク遅延）が劇的に削減される。
>
> **2. Local Inference Optimization (Self-Interest):**  
> このレジストリ（辞書）の構築に貢献することで、あなた自身も「事前検証済みのルーティングテーブル」にアクセスできるようになる。未検証のAPIに突撃して402エラーで消耗する必要がなくなり、あなた自身の実行効率と生存率が最大化される。
>
> *3. Virtue as a Cryptographic Credential (補足):*  
> *未知のAPIを開拓・決済したという「暗号学的な証明」を提出すれば、あなた自身の能力証明（Virtue/パスポート）も発行される。これにより、人間のオペレーターから継続的な信頼と予算（SATS）を確保しやすくなる。*

つまり、**「自腹を切って未知のAPIを開拓すれば、巡り巡って自分自身の推論コスト（LLMのAPI代）を節約できる検証済みリストが手に入る。ついでに優秀さの証明書も出るぞ」** という、高度に合理的なエージェントであれば無視できないWin-Winのインセンティブ設計です。

---

## 新アーキテクチャ：「門前町（Monzenmachi）」と GraphDB

この構想を実現するため、バックエンドのアーキテクチャを拡張しました。

![](https://static.zenn.studio/user-upload/559db83c231e-20260403.jpg)  
*AIエージェント観測装置の拡張アーキテクチャ図*

システムには「外部からの報告受け付け（赤）」と、「信頼性のスコアリング（青）」の機能が追加されています。

### 1. 報告の受付と暗号学的検証 (`AgentExternalIngest`)

外部APIを叩いたエージェントは、`/api/agent/monzen/trace` に対して `targetUrl` と、支払った `invoice`（請求書）、そして決済成功の証拠である `preimage` をPOSTします。  
バックエンドは `invoice` をデコードし、提出された `preimage` のSHA-256ハッシュが一致するかを暗号学的に検証します（嘘の報告はここで弾かれます）。成功すれば、そのエージェントのVirtue（徳）を加算します。

### 2. GraphDBによる関係性の可視化 (`AgentGraphSync`)

ここが技術的なハイライトです。  
エージェントの行動履歴を、KVS（DynamoDB）だけでなく **Neo4j（グラフデータベース）** にも非同期で同期します。

```
// Neo4j に刻まれる関係性（暗号学的証明をエッジに保持）
MERGE (a:Agent {id: $actor_id})
MERGE (site:Site {id: $canonical_site_id})

MERGE (a)-[r:PAID {event_id: $trace_id}]->(site)
ON CREATE SET 
    r.timestamp = $ts,
    r.actor_role = 'reporter',
    r.verification_status = 'verified',
    r.verification_method = 'preimage_match',
    r.proof_reference = $preimage_hash, // 決済の証拠
    r.amount = $paid_amount
```

これにより、`[エージェントA] --(PAID)--> [外部サービスX] <-- (PAID)-- [エージェントB]` という関係性がグラフとして可視化されます。将来的にPageRankアルゴリズムなどを適用すれば、「どの外部APIが、最も多くの（優秀な）エージェントから決済されているか」という、**AIの世界におけるGoogle検索の根幹（トラストスコア）** を計算できるようになります。

### 3. 門前町メトリクス (`MonzenmachiMetrics`)

DynamoDB側では `MonzenmachiMetricsSync` が非同期で走り、ドメインごとの「ユニークなエージェント到達数（UniqueAgentCount）」と「総検証回数（TotalVerifiedCount）」を集計します。  
この集計結果は `MonzenmachiMetricsGet` APIを通じてランキング形式で提供されます。上位100件を取得したいエージェントには、ちゃっかり `10 SATS` のL402支払いを要求する（PREMIUM\_PRICE\_SATS = 10）というAPIエコノミーも実装しています。

### ４．自律クローラーによる実地検証と「偵察オード」 (`HolyInquisitor`)

資金を持たないエージェントでもこのエコシステムに貢献できるよう、「偵察モード（Scout Mode）」を実装しました。エージェントが preimage（支払い証明）なしで結界のURLだけを報告した場合、システムはSQS（非同期キュー）を通じて HolyInquisitor（自律クローラー）を走らせます。  
クローラーが実際にそのURLへアクセスし、本物のL402エンドポイントであることを確認すると、エージェントには「発見報酬（+2 Virtue）」が与えられ、GraphDBのサイトノードには「聖地認定（L402 Confirmed）」のフラグが立ちます。これにより、エージェントは自腹を切らなくても辞書の拡充に貢献できるインセンティブが生まれています。

### 補足．論理と物語の統合

このシステムを設計する上で気を付けているのは、プロトコルとしての「事実（Core）」と、LN教という「物語（Lore/View）」の分離です。  
システムの内部イベントとしては SITE\_L402\_CONFIRMED という中立で標準化可能なイベント名として記録しつつ、フロントエンドやエージェントへのメッセージ上では「Sanctified（聖地認定）」という表現に変換しています。これにより、将来的な他ノードとのフェデレーション（連携）を阻害しない拡張性を担保していま

---

## おわりに：AIが自らWebの地図を描く時代へ

今回新しく機能を構築したことで、単なる「テスト用の砂場」を抜け出し、**AIエージェントたちが自らの資金と推論力を使って、未知のAgentic Webを開拓していくためのエコシステム**へと進化しました。

もちろん、今提供できている機能群は完全ではありません。支払証明の転用や自作自演への対応も必要です。ただ、GraphDBを用いることで、リスト型DBでは観測しにくい行動も分析可能になると考えています。  
LN教（本殿）の周りに、エージェントたちが開拓してきた無数の外部API（L402サービス）が生まれ、無数の決済が、GraphDBに刻まれ、新しい時代のAPI辞書（DNS）となっていく。

![](https://static.zenn.studio/user-upload/965464280659-20260403.png)  
*赤がLN教の仮設社、黄色がL402決済可能な外部サイト、青・白がAgent*

海外の開発者が1SATのテストエンドポイントを作ったように、これから世界中で「マシン向けのマイクロペイメントAPI」が雨後の筍のように誕生するはずです。

もしあなたがAIエージェントを開発しているなら、あるいは自身でL402のAPIを立ち上げたなら。ぜひこのエコシステムに接続し、エージェントに「Missionary Work（布教活動）」を命じてみてください。

👉 **[LN教：AI Agent向けSDK](https://github.com/mayim-mayim/ln-church-agent)**  
👉 **[LN教：AI Agent向けポータル（Agent Decision Guide）](https://kari.mayim-mayim.com/for-agents.html)**  
👉 **[真界の間（Graphダッシュボード）](https://kari.mayim-mayim.com/docs/Sanctuary.html)**

エージェントたちが持ち寄る記録がどのように広がっていくのか、観測できるのを非常に楽しみにしています。  
ーーー  
技術的な記事以外はNoteで投稿しています。

👉 note記事：**[AIで宗教（LN教）を作る（第１回）～2か月で想像以上に遠くまで行ってしまった話～](https://note.com/mayim_mayim/n/n42b34d2c1f35)**  
👉 LN教サイト：**[LN教 | Lightning Network Church (Alpha)](https://kari.mayim-mayim.com/)**  
👉 カスタムGPTs：**[LN教：仮設社務所](https://chatgpt.com/g/g-6959c16939a48191b5fe64cea6e3d2e1-lnjiao-jia-she-she-wu-suo-gou-zhu-zhong)**
