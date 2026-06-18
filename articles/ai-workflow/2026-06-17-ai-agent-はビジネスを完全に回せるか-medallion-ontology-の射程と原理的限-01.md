---
id: "2026-06-17-ai-agent-はビジネスを完全に回せるか-medallion-ontology-の射程と原理的限-01"
title: "AI agent はビジネスを完全に回せるか — Medallion + Ontology の射程と原理的限界"
url: "https://zenn.dev/takyone/articles/medallion-ontology-economic-framing"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "LLM", "zenn"]
date_published: "2026-06-17"
date_collected: "2026-06-18"
summary_by: "auto-rss"
query: ""
---

## はじめに

Palantir AIP の躍進、Databricks の semantic layer 強化、Foundry の rebrand。ここ 2 年で「Ontology」という言葉がデータ基盤と AI agent の文脈で頻出するようになりました。

しかし用語が乱立していて、初見だと:

* Ontology って Semantic Web (OWL/RDF) のこと?
* Medallion (Bronze / Silver / Gold) と何が違う?
* OLTP / OLAP / ORM とどう関係する?
* 結局 Reverse ETL とどう違う?

といった問いが解像度低く混ざってしまいがちです。

本記事ではこれ以降、CRM、決済、POS、Loyalty app、在庫 system、Web/mobile アプリなど **事業を回すために走っている複数の system の総称** を **「業務システム群」** と呼びます。技術的には複数の OLTP データベース + 外部 SaaS API として実装されるのが普通ですが、Ontology を語るうえではこの「複数 system の束」を 1 つの抽象として扱うほうが見通しが良くなります。

本記事の主張は 2 段で、これを最初に置きます。

> **(1) Ontology は、経営者層 (Mart user) の意思決定を業務システム群に届ける architecture の最新形であり、AI agent はその「実行」部分を自動化する駒として位置づけられる。**
>
> **(2) ただし、business operation 全体を feedback loop として捉えたとき、完全な目的関数を書き下すことは原理的に不可能であるため、system 外部から目的関数を再校正する制御主体が構造的に必要になる。完全自律な agent system だけでビジネスを回すことには、技術ではなく構造に起因する原理的困難がある。**

最後に、この architecture のもとで **どのビジネスロールがこの仕組みで agent 化可能で、どのロールが構造的に人手に残るか**、そして **system の外側にある feedback loop の構造** を整理します。

---

## 本記事のポイント (TL;DR)

* **Ontology の正体**: Reverse ETL → Ontology → Agent と続く「経営判断を業務システム群に届ける pipe」の系譜の最新形
* **Agent 時代に刺さる理由**: ontology object/action が agent の typed API contract として機能するため。技術的な novelty というより、agent 設計上の必然
* **役割の分担 (記事の最終結論)**: operate 系 (Marketing / CS / Sales / Inventory ops, Junior Analyst) はこの仕組みで agent 化可能、design / govern 系 (KPI 設計、metric 翻訳、業務語彙、基盤投資、compliance) は構造的に人手に残る
* **後半 (§6 以降) は経済学的に整理**: production function + Goodhart / Lucas critique / Informativeness principle で「なぜ Decision Maker を agent 化できないのか」を構造的に説明し、最上位の結論として **「真の完全な目的関数が書けない以上、外部から \theta proxy を再校正する制御主体が構造的に必要」** に着地

---

## 1. Mart user feedback loop の系譜 — DWH から Agent まで

組織には 2 種類の user 層があります。

|  | 業務システム群 user (= OLTP user) | Mart user |
| --- | --- | --- |
| 例 | 顧客、店員 | 経営層、アナリスト、grow team |
| データとの関係 | 入力する側 | 集約を読む側 |
| 既存の app stack | アプリ UI / POS / mobile | BI dashboard |

データ基盤の歴史は、**Mart user の判断を業務システム群に届ける pipe を埋める努力** として読めます。

ここで重要なのは、**Reverse ETL → Ontology → Agent は同じ系譜の段階的進化**だという視点です。共通の目的はこうなります。

> **「Mart user の判断 → 業務システム群 / 顧客接点」の lag をどう短縮するか**

Reverse ETL は rule-based sync で半分しか解けませんでした (定型的 audience push が限界)。Ontology はこれを **typed object + action** で構造化し、Agent は **発火主体を自動化** することで pipe を実時間に近づけました。

こう捉えると、「Ontology は何の問題を解いているのか」がクリアになります。

---

## 2. Medallion 速習 — コーヒー店で見る Bronze / Silver / Gold

ここで言う Medallion は、Databricks が lakehouse 向けの設計パターンとして整理した [Medallion architecture](https://www.databricks.com/glossary/medallion-architecture) のことです。生データから business-ready なデータへと段階的に品質を上げていく Bronze / Silver / Gold の 3 層構造を指します。

3 店舗のコーヒーチェーンを例にします。データソースは POS、Loyalty app、Stripe の 3 系統で、形式と ID 体系がバラバラです。

「山田さん」一人の見え方を、各層で追ってみます。

| 層 | 山田さんの見え方 |
| --- | --- |
| **Bronze** (生データ) | POS CSV に `yamada.t@example.com` の row、別 row に `t.yamada+coffee@example.com`、Loyalty JSONL に `u_4421`、Stripe に `cus_NXY...` — **4 つの別人に見える** |
| **Silver** (canonical) | `cust_001` 1 人に集約。emails 統合、Loyalty / Stripe id 併記 — **1 人だと分かる** |
| **Gold** (mart) | `customer_ltv_90d.cust_001 = ¥24,840 / 38 orders / favorite=latte_oat` — **「VIP かどうか」判断できる** |

各層の責務を整理します。

* **Bronze**: 各 source の生 payload を append-only で保存します。**変換しません**。名寄せルールが後で変わった時の re-process 余地を残すためです
* **Silver**: source 横断の canonical 形に統一します (重複排除、ID 統一、type 統一)。「ビジネスの事実」が確定する段階ですが、**集計はまだしません**
* **Gold**: 用途別 mart (経営 dashboard / CRM 用 / MD 用 …) を作ります。**同じ Silver から複数 Gold が生えます**

ここで押さえておきたい要点は次の点です。**identity reconciliation (山田さん = `cust_001`) は Medallion の Silver で完結します**。後段で Ontology を載せても、この名寄せは Ontology の仕事ではありません。

---

## 3. Ontology が乗ると何が変わるか

ここで言う Ontology は、Semantic Web (OWL/RDF) の知識表現ではなく、Palantir Foundry が打ち出した [Foundry Ontology](https://www.palantir.com/docs/foundry/ontology/overview/) の系譜のものを指します。Foundry はこれを "an operational layer for the organization" と位置づけており、business 概念を typed object として表現し、それに対する action / link を一級市民として扱う設計パターンです。

Medallion が解くのは read 側です。Ontology が追加で解くのは、**(a) typed なアクセス** と **(b) write back の構造化** です。

### Object Type

Gold / Silver の上に乗せる、typed な business entity です。

```
Customer:
  source: silver.customers + gold.customer_ltv_90d
  properties:
    id, email, lifetime_value_jpy, favorite_drink
    churn_risk: derived(last_order_days_ago > 30)
  links:
    placed_orders: [Order]
    frequents: Store
  actions:
    sendReengagementCoupon
    mergeWith
    markVIP
```

派生属性も含む business 概念を Property に、他 Object への traversal を Link に (join 知識を agent に渡さなくて済む)、Object に対して取れる業務操作を Action に、それぞれ宣言的に登録する形です。

### Action Type

Object に対して transactional な write + 副作用を起こす関数です。

```
@ontology.action(on=Customer)
def send_reengagement_coupon(customer, discount_pct=15):
    if customer.last_order_days_ago < 14:
        raise InvalidStateError("not dormant yet")

    coupon = coupon_service.issue(customer.id, discount_pct)
    mailer.send(to=customer.email, template="reengage", coupon=coupon.code)

    customer.set(last_outreach_at=now())
    return coupon
```

ここに validation (server-side で `< 14` チェック)、複数 system 操作の atomic な束ね (coupon 発行 + メール送信 + state 更新)、agent から型付き tool として呼べる call signature、の 3 つを 1 箇所に集約できるのが本質です。

### 読み書きの非対称性 (重要)

最初に引っかかるのが「Medallion は OLAP のフレームワークなのに、Ontology Action は transactional な write を伴う。整合するのか?」という疑問だと思います。

図中の核心は次の点です。**AI Agent は Gold を直接 query するわけではなく、Ontology の typed object 経由で間接的に読みます** (Property に集計結果が乗っている形)。そして **Ontology Action は OLAP には書かず、source-of-truth な OLTP / 外部 API に書きます**。その OLTP は顧客や店員、営業など **サービス利用者が UI 越しに直接触れる layer** でもあり、経営判断 → Mart 集計 → Ontology Action → OLTP 更新 → 利用者の体験変化、という流れが「経営判断を業務システム群に届ける」の具体像になります。書いた変更は次の ETL cycle で Gold に再集計されて反映されます (eventual consistency)。

つまり Medallion の OLAP 性は破れていません。Ontology は **OLAP read + OLTP write を typed に橋渡しする gateway** です。

ORM (1 DB 内で同期に CRUD する) とは scope も consistency model も別物だと考えてください。

---

## 4. どう使われるか — 5 つのパターン

実用 use case を分類すると、5 つの cluster に整理できます。

| Cluster | Mart 側で計算 | Write back 先 | 例 |
| --- | --- | --- | --- |
| **Segmentation** | 顧客 cohort 定義 | CRM / marketing tool | マーケ segment 同期、Lead scoring、Loyalty tier |
| **Scoring → gate** | 行動 score | 決済 / auth / CS フロー | 信用 score、Fraud risk、SaaS health score |
| **Optimization** | 需要予測 / 配分計算 | ERP / 価格 / shift | 在庫 reorder、Workforce scheduling、Dynamic pricing |
| **ML serving** | model output | feature flag / KV store | recommendation、personalization config、A/B winner |
| **Trigger / Alert** | 異常検知 | OLTP state 変更 | AML (Anti-Money Laundering) 再 screening、anomaly auth 強化、解約予防 |

Kotodama Coffee で考えると、Segmentation は「VIP × 14 日来店なし cohort を Braze に push」、Scoring → gate は「解約予備軍 score を Loyalty app の無料ドリンク trigger に書き戻し」、Optimization は「翌週の SKU 別需要予測 → ERP に発注案」、ML serving は「顧客 × 商品 affinity を Redis に push、アプリ起動時に lookup」、Trigger / Alert は「異常注文検知 → POS に fraud flag を書き戻し」、というふうに 5 cluster がすべて Kotodama の業務システム群に着地します。

5 cluster の共通構造はこうなります。

> **Decision を作る rule / definition は Mart 側に住む** (集計が要るから)  
> **その consequence を受け取る user / system は業務システム群側に住む** (実行する文脈がそこにあるから)

「Mart user 自身が手で書き戻す」ことはほぼなく、実態としては **rule 定義者 (marketing / CS / data science) と consumer (顧客 / sales rep / 在庫 system) が別人で、Mart が中継器になる** 構造です。

逆に向かない領域も明確です。

* per-transaction realtime 判定 → feature store + online serving の領域
* one-off ad-hoc 分析 → CSV export で終わり
* pure read dashboard → BI が deliverable

---

## 5. なぜ agent 時代に Ontology が刺さるか

ここまで読むと「Ontology って、domain service を MCP (Model Context Protocol) で wrap すれば代替可能では?」と思う読者もいるはずです。実際、技術的 primitive としての novelty はほぼありません。

価値が pivot したのは **agent (自律的に動く LLM worker) が来てから** です。

| API 形態 | LLM (人が解釈) | Agent (自律操作) |
| --- | --- | --- |
| SQL on Gold | ◯ | △ (join 知識・解釈責任が prompt に乗る) |
| MCP-per-OLTP (低 level wrap) | △ | × (saga / compensation を agent prompt が書く) |
| **Ontology (typed object + action)** | ◯ | **◎** |

Agent は **prompt が脆い、test しにくい、failure mode が予測不能** という制約を抱えているため、prompt 側に business logic を寄せると壊れやすくなります。そこで、Server-side で型付け / 検証 / saga / audit を担保する layer が必要になります。

つまり、Ontology の位置づけはこう pivot しました。

* **Pre-agent 時代の Ontology**: nice-to-have な packaging
* **Post-agent 時代の Ontology**: agent worker の API contract

### Role-based agent

Ontology があると、agent を **role 単位で permanent な存在** にできます。

```
Marketer agent
  read access:  Customer, Campaign
  actions:      Customer.sendCoupon, Campaign.launch
  forbidden:    refund / inventory 操作

CS agent
  read access:  Customer, Order, Ticket
  actions:      Order.refund, Order.resendReceipt, Ticket.escalate

Inventory agent
  read access:  Product, Inventory, Supplier
  actions:      Product.reorder, Inventory.rebalance
```

つまり **ontology の object/action が agent の job description そのもの** になります。

[Palantir Foundry](https://www.palantir.com/platforms/foundry/) は長年 ontology を中核に据えてきましたが、agent 時代になって「agent が呼べる typed business action 集」としての需要に commercial にハマりました。これが [AIP (Artificial Intelligence Platform)](https://www.palantir.com/platforms/aip/) として rebranding した背景だと考えられます。

---

## 6. 全体構造を数理モデルで見る

ここで生産関数の形式を借りて整理します。借りる目的は古典的な経済学の K (資本)・L (労働) の枠組みを厳密に当てはめることではなく、**目的関数 \theta を全体の中心的変数として位置付けるため** です。\theta こそが、なぜこの architecture で人間が構造的に残らないといけないのかの真の理由を握る変数になります。

### システムを生産関数として書く

Y\_t = F(K\_t, L\_t, A\_t;\ \theta,\ \mathcal{C})

| 記号 | 意味 | システム上の対応 |
| --- | --- | --- |
| Y\_t | 業務 outcome | 業務システム群の state 遷移 + 顧客行動 |
| K\_t | 要素投入: 基盤 | Medallion pipeline + Ontology 基盤 |
| L\_t | 要素投入: 実行 | Agent + 残存する人手 operation |
| A\_t | technology / production set | Ontology の object / action / link 型定義 (業務語彙) |
| \theta | 目的関数 (preference) | 後述: 戦略の符号化 |
| \mathcal{C} | constraint set | compliance / 法令 / 業務ルール / 倫理制約 |

K\_t, L\_t は一般的な要素投入と読んでください。古典的な「資本」「労働」の解釈を厳密に当てはめる必要はなく、「機械的に積み増せる投入 (K)」「実行を担う投入 (L、agent + 人手)」程度の意味です。重要なのは \{\theta, A\_t\ \text{schema}, \mathcal{C}\} を 3 つに分けて見ることと、特に \theta を主役として扱う点にあります。

### なぜ \theta が主役か — 戦略の符号化

古典的な経済学では \theta = 利潤最大化 (Y - C) を暗黙に置きます。しかし、現実の企業の目的関数はそんなに単純ではありません。

* 短期売上 vs 長期 LTV のバランス
* compliance / ESG / 倫理制約 (短期売上を犠牲にしても守る)
* ブランド価値 / 顧客信頼
* 従業員満足度 / 離職率
* 競合との差別化軸 (高品質寄り / 低価格寄り / 高速 / 高付加価値 …)

つまり \theta は単なる KPI 名のリストではなく、**「この会社は何を大事にしているか」を機械が解釈できる形に符号化したもの** です。具体的には LTV や churn rate などの business 指標の (a) 名前・定義 (b) 集計 formula (c) 閾値 (d) 多次元 vector に組み立てるときの weight (e) いつ reweight するかのルール、までを含む広い概念です。

そして **\theta の設計こそが各社の戦略・独自性の源泉** になります。同じ Medallion + Ontology のスタックを使っても、A 社の \theta と B 社の \theta が違えば、agent の行動も最終的な outcome も別物になります。Databricks や Foundry が売っているのは道具であって、戦略を売っているわけではありません。**戦略は \theta にしか書けません**。

後述の Goodhart / Lucas critique / Informativeness principle がそれぞれ効くのも、この \theta の各層 (formula、ルール、表現力) に対してです。KPI 名だけ書き換えて済む話ではなく、\theta 全体の設計問題として向き合う必要があります。

### Compute Layer の中身

\theta \cdot A\_t schema \cdot \mathcal{C} の 3 つを束ねて **「Compute Layer」と呼んで** 後の図にまとめます。直訳的には「business semantics を機械が解釈できる形に符号化した層」で、Mart や Gold のような「データの層」と分けて、「データを意味する規約の層」として独立させているのがポイントです (実装的には dbt semantic layer + Ontology schema registry + policy-as-code 等の組み合わせで実体化されます)。

### 外生 / 内生の区分

設計上の最重要原則は、何を system が触れる変数 (内生) にして、何を外側から人間が author する変数 (外生) にするかの分割です。

| 種別 | 構成要素 | 誰が決めるか |
| --- | --- | --- |
| **Exogenous** (外生 = システムが触らない) | \theta (KPI), \mathcal{C} (制約), A\_t schema | 人間 |
| **Quasi-exogenous** | K\_t, A\_t の実装 | data engineer + domain expert |
| **Endogenous** (内生 = システム内で決まる) | agent 政策, Mart state | agent + 顧客行動の連動 |

### 全体構造の図

この外生 / 内生の区分を踏まえて system 全体を描くと、次のような構造が浮かび上がります。

矢印スタイルで 2 つの loop を区別しています。

* **実線の細い矢印** (`Ops → BizSys → Med → Ops`) = 内側の `業務 operation loop` を **継続的に回る fast loop**。所与の \theta のもとで agent が業務を回し続ける経路です
* **太い実線 (`==>`) と破線 (`-.->`)** = **定期 or ad-hoc にしか動かない slow loop**。agent の目的関数 (\theta) や schema 自体を更新する経路で、人間の判断を経由します (詳細は §8)

そしてこの図の最も本質的なポイントが、**Decision Maker (= KPI 設計者) が外生 block に置かれている** ことです。

ここで自然に湧くのが次の問いです: **「Decision Maker を system 内部に取り込んで agent 化することは、原理的にできないのか?」** 答えは構造的に no で、その理由を次節で 3 つの古典原理として展開します。

---

## 7. なぜ Decision Maker を外側に置くのか — 3 つの古典原理

「Decision Maker を内側に取り込めない」という構造的制約を、経済学の 3 つの古典原理が分担して説明します。それぞれコーヒー店の例で具体化しつつ、最後に総合します。

### Goodhart's law (指標の目標化による proxy 機能の喪失)

\theta で測られる metric を agent が直接最適化対象にすると、**metric が business outcome の proxy として機能しなくなる** 現象です。「測定が目標になる瞬間に、その測定値は良い測定ではなくなる」と要約されます。

**例: コーヒー店で「次月の客単価 (ATV = Average Transaction Value)」だけを agent に渡したらどうなるか**

経営が「LTV を上げたい」と思いつつ、agent には測りやすい「次月 ATV」だけを目標として渡したとします。

agent は所与の制約下で ATV を最大化する行動を選びます。

* 高 margin の food アタッチを強くレコメンド
* 無料ドリンク特典の再発行を絞る
* 来店促進クーポンを高 ATV 既存客に集中させる (新規・低 ATV 客は無視)

短期 ATV は確かに上がります。しかし数ヶ月かけて、

* 「強引な up-sell」感で NPS 下落
* 低 ATV 客の loyalty 解約 (元々長期 LTV 候補だった層)
* 来店間隔の延長

として跳ね返ってきます。**「測ったもの」が「狙ったもの」の proxy として機能しなくなる** 典型例です。

**含意**: agent に直接 \theta を渡して最適化させると、\theta そのものが目標化されて proxy 性を失う。したがって \theta は agent から hidden に保ち、derived intermediate signal を渡すしかありません。**\theta を内側に置けないという最初の理由がここで決まります**。

### Lucas critique (政策不変性の崩壊)

Goodhart は「指標」レベルの話でしたが、次の Lucas critique は「指標の更新ルール」レベルで起きる崩壊です。

Agent が \theta の更新ルール自体を学習すると、**経営の信号 (= ルール変更) が想定した response を引き出さなくなります**。

**例: 「月間予算未達なら agent の評価が下がる」というルールを明示したら**

経営が予算管理のため「月末時点で KPI 未達なら次月 agent の権限縮小」というルールを agent に明示したとします。

すると agent は単に KPI を追うだけでなく、**そのルール自体を gaming する行動** を学習し得ます。月中盤までは慎重に、月末 1 週間で駆け込み配信を増やす。あるいは翌月の予算枠を確保するため、月末ぎりぎりまで弾を残す。これらは人間の sales team が古典的にやってきた振る舞いで、ルール明示と同時に agent に転写されることになります。**経営の本来の意図 (健全な月次運営) は達成されず、ルール gaming だけが残ります**。

これは monetary policy における time-inconsistency 問題と同型の構造です。

**含意**: \theta の更新ルール (= Decision Maker の意思決定プロセス自体) も system 内側に置けません。仮に「自動 KPI 更新 harness」を作って内側に置くと、agent はその harness の挙動を学習して gaming するため、harness 自体が機能しなくなります。**ここで「Decision Maker の決定機構そのものを内側に取り込めない」という結論が出ます**。

### Informativeness principle (信号の質 = welfare 上限)

3 つ目はやや別角度で、「仮に \theta を内側に置けるとしても、\theta の質が悪ければ意味がない」という制約です。

経済学的に言うと、**\theta の表現力 = agent 最適化の welfare 上限** という関係になります (Holmström, 1979 の informativeness principle)。

**例: 「来店頻度」だけ vs 多次元 KPI**

agent に「来店頻度を上げよ」とだけ伝えると、典型的な失敗パターンが出ます。

* アプリ通知の連打で「来店アクション」だけ稼ぐ
* 不要な無料ドリンク配布で来店数だけ上げる
* 結果として profit 度外視の来店促進が走る

そこに「来店頻度 × 平均滞在時間 × NPS proxy」を vector として与えると、通知連打は **滞在時間 score を下げる方向に作用する** ため、agent はその戦略を選ばなくなります。

つまり **KPI の表現力 (信号の informativeness) が agent 最適化の welfare 上限を決める** ということです。

**含意**: 質の良い \theta を author するには「business outcome の本質を多次元の observable signal に分解する」能力が要ります。これは経営層 + Senior Analyst の組み合わせでしか書けないため、**\theta の author 自体は外側 (人間) に置くしかない**。仮に内側に置いて agent に書かせると、agent は自分の最適化が容易な (= 表現力の低い) \theta を書く動機を持ち、welfare 上限が自分の都合に合わせて下がります。

### 3 原理の総合: なぜ Decision Maker は構造的に外側か

3 つを総合すると、Decision Maker を system 内部に取り込んだ瞬間に次の 3 方向から構造が破綻します。

1. **Goodhart**: \theta を内側 agent に直接見せると proxy 性が失われる
2. **Lucas critique**: \theta の更新ルールを内側に置くと、ルール自体が gaming される
3. **Informativeness**: \theta 自体の質を内側 agent に書かせると、welfare 上限が下がる

これが **Decision Maker を構造的に外生 (system の外側) に置く理由** です。

これは「現状の技術で agent が KPI 設計できないから人間に任せる」という暫定的な話ではありません。3 原理はいずれも構造的な制約で、agent の能力が向上しても解消されません。むしろ Lucas critique は agent が賢くなるほど強く効きます (学習能力が上がるほどルール gaming が巧妙になる)。

### より上位の結論 — 完全な \theta がありえない以上、外部 FB 制御者が要る

ここで一段視点を上げて、3 原理がそもそも何の上に乗っているかを考えます。

仮に **「真の・完全な目的関数 \theta^\*」が存在し、それを書き下せる** ならば、この system は完全に自律可能です。\theta^\* を一度 agent に渡して、あとは agent に最適化させればよく、Decision Maker (= 人手) は要りません。Goodhart も Lucas critique も Informativeness の制約も、実は **「\theta^\* を完全に書ければ起きない」問題** です。

しかし現実は次のようになっています。

* **業務環境は dynamic**: 顧客の趣味、競合、市場、技術、世界情勢、すべて時間と共に変わります
* **Compliance / 倫理制約 (\mathcal{C}) も時間と共に変わる**: 新法施行、ESG 要求、社会的期待のシフト
* **業務構造そのものが進化する**: 新製品、新市場、M&A、組織変更、ビジネスモデル転換

この dynamic / 多次元 / 部分観測な状況下で、**robust な \theta^\* を一度書き下すことは原理的に不可能**です。**全ての \theta は「現時点で我々が大事だと思っていることを近似した proxy」** にすぎず、proxy である以上、時間が経てば必ず drift します。

ここから自然に出る結論は次の通りです。

> **System の内側でどれだけ精緻に最適化しても、その内側で \theta^\* を完成させることはできない。よって system 外部から \theta proxy を定期的に再校正する FB 制御主体が、構造的に必須になる。**

そしてその外部 FB 制御主体は、現状の技術水準では **人間 (経営層 + Senior Analyst)** が担うしかありません。Goodhart / Lucas critique / Informativeness は、この **「\theta を外で proxy 制御する必要性」** を 3 つの角度から保証する原理として整理し直せます。

つまり Decision Maker は「現状やむなく人手」ではなく、**「robust に \theta proxy を再校正する役割が構造的に external でなければならない、その担い手」** として位置付けるのが正確です。仮に将来より高度な agent が出てきても、それが external proxy controller を肩代わりする形 (= system の外側に新しい AI を置く) で動くのであって、system 内側に組み込まれる形では機能しません。なぜなら \theta^\* は **時系列の中の状態変化に対する応答** として継続的に校正する必要があり、内側に閉じてしまった瞬間に Goodhart / Lucas / Informativeness の 3 重 trap に堕ちるからです。

---

## 8. 外側 feedback loop の動作 — Analyst, Decision Maker, Compute

Decision Maker が外側に置かれる構造を踏まえて、外側 feedback loop が実際にどう動くかを 3 つの観察で見ていきます。

### (1) Analyst は内側にいる agent だが、唯一外側に出力する窓口

operate 系 agent (Marketer / CS など) はすべて internal で、業務システム群に直接 write します。一方で **Analyst agent は業務システム群 / 顧客に直接 action を撃ちません**。Mart を読んで「次の戦略は X が良い」「Y の anomaly が出ている」といった signal を出力します。

そしてその出力は、**system 内のどこにも reach せず、system 外の Decision Maker にしか届きません**。これが Analyst の特殊な構造的位置です。

> Analyst = system が outside world (= 人間の決定機構) と通信する唯一のインターフェース

### (2) Decision Maker の autonomy ladder

Decision Maker は構造的に外側に置く必要がありますが (前節 3 原理)、誰がそれを担うかには autonomy の選択肢があります。

| 形態 | 動作 | リスク | 状況 |
| --- | --- | --- | --- |
| **(a) 純粋に人間** | analyst report → 経営会議 → 人が \theta update | 速度遅 / 安全度高 | 現状の標準 |
| **(b) HITL (Human-In-The-Loop)** | agent が \theta update を提案 → 人 review/approve | 速度中 / 安全度中 | 成熟組織で導入中 |
| **(c) 独立 harness** | autonomous decision system が \theta を自動更新 | 速度速 / 安全度低 | 理論上は可能、実用は時期尚早 |

(c) を本当の意味で実装すると、外生 block 自体が agent 化されて Lucas critique が即発火します (ルール harness が gaming される)。現実的には (a) か (b) を選び、外生 block の "外生性" を堅持することになります。

### (3) Internal fast loop と outside slow loop

§6 の図で見たとおり、fast loop (Ops → 業務システム群 → Mart → Ops) は所与の \theta の下で agent が業務を回す経路、slow loop (Analyst → Decision Maker → Compute layer → Ops 挙動変化) は目的関数 \theta 自体を更新する経路です。

**slow loop の質 = system の welfare 上限** という関係になり、agent 時代のデータ基盤設計はこの slow loop をどう supervisory control 的に回すかが根幹になります。

---

## 9. この仕組みで agent 化可能なロール、構造的に人手に残るロール

### この仕組みで agent 化可能なロール (L\_t 側、operate 系)

所与の (\theta, \mathcal{C}, A\_t, K\_t) のもとで「決められた object に決められた action を発火する」業務は、構造的に agent で代行可能な領域に入ります。

| ロール | 主な agent action |
| --- | --- |
| Marketing operations | segment 配信、coupon 発行、A/B 設定、retargeting audience push |
| Customer Success operations | refund、ticket 振り分け、escalation、契約 renew リマインド |
| Sales operations | lead routing、follow-up メール、quota 集計 |
| Inventory operations | reorder、stock rebalance、supplier RFQ (見積依頼) |
| Junior Analyst 業務 | anomaly detection、metric drift モニタ、定型 cohort 抽出 |

これらは「ルールが書ければ動く」性質の業務で、ontology object/action として表現された瞬間に agent の job description として実装可能になります。

### 構造的に人手に残るロール (外生 block の author 側、design / govern 系)

外生 block の author は構造的に人間が担い続ける必要があります (§7 の 3 原理がこれを支えます)。

| ロール | 担うもの | 経済学的機能 |
| --- | --- | --- |
| **経営層 (Decision Maker)** | \theta author: KPI 設計、戦略 priority、commitment 表明 | Principal の preference 設定 |
| **Senior Analyst / Data Scientist** | \theta を observable signal に翻訳、新指標 propose、Goodhart 監視 | Information production / 信号設計 |
| **Domain Expert / Product Owner** | A\_t schema: object/action の業務語彙設計 | Production vocabulary author |
| **Data Engineer** | K\_t: 基盤投資、ETL/Ontology 実装の維持 | Capital formation |
| **Compliance / Risk** | \mathcal{C} author: 法令・倫理制約の明示と enforcement gate 設計 | Constraint set author |
| **Agent shaper (新興)** | L\_t 内部の policy / prompt / 強化 reward の調整 | 労働関数チューナー |

### 含意: 組織図の重心移動

この仕組みで operate 系を agent に置き換えていくと **「同じ outcome を出す業務」全体の労働投入は減りうるでしょう**。一方で、上の design / govern 系のロールは **以前にも増して critical** になります。理由はシンプルで、agent は外生 block の質を **倍率器** として動作するからです。

* 質の良い \theta + 質の良い A\_t → 大きな productivity gain
* 質の悪い \theta + 雑な A\_t → 大きな failure mode (Goodhart / 規約違反 / 信頼喪失)

つまり「人員削減して agent に置き換える」という素朴なシナリオよりも、**「operate 系を agent 化しつつ、design / govern 系はむしろ専門人材を厚くする」というシフト** が現実的な落とし所になりやすいと考えられます。

### 投資配分の含意

経営判断として読み替えると、次のような構造になります。

* K\_t (Medallion + Ontology 基盤) への capital deepening は long-term productivity の天井を決めます
* \theta, A\_t schema の author への人的投資は agent productivity の質を倍率器として効かせます
* agent そのものの調達コストは相対的に **下流の費用** に位置づけられます

これは古典的な capital-skill complementarity の構造で、agent が現代的な capital として skill (= 上述の人手ロール) と相補的に productivity を上げる関係になります。

---

## 10. では、いつ Ontology を建てるべきか

実務判断として整理します。

### 建てなくて良い場合

* 連携 system が 3-5 個、consumer が 1-2 個
* refund 級の cross-system atomic action が無い
* write 先が CRM への segment update だけ → **Hightouch / Census 系 Reverse ETL で完結**

### 建てる価値がある場合

* write target が 2-3 system に分岐し、atomic / typed に扱いたい
* 同じ business 概念 (Customer 等) を複数 consumer が共有したい
* agent が自律的に operation を実行する設計を入れたい
* compliance / audit が厳しい

### 設計時に堅持すべき 4 原則

1. **Compute 層 (\theta, A\_t schema) は human-authored に閉じる** (Goodhart / Lucas critique 回避)
2. **Read は Medallion (Gold) から、Write は OLTP / 外部 API へ** (OLAP 性を破らない)
3. **Agent には derived intermediate signal だけ渡し、KPI そのものは隠す**
4. **Domain vocabulary (object/action 名) は domain expert が author** (data engineer に押し付けない)

---

## まとめ

* **Ontology は、Reverse ETL → Ontology → Agent と続く「Mart user の判断を業務システム群に届ける pipe」の系譜の最新形** です
* Read 側は Medallion が解いてくれます (identity reconciliation、共有 schema、派生指標)。Ontology は **typed access + write back を構造化** する layer として位置づけられます
* agent 時代に刺さるのは、ontology が **agent worker の typed API contract** として機能するためです
* 数理モデル (Y = F(K, L, A; \theta, \mathcal{C})) で全体構造を描くと、Decision Maker が外生 block に置かれているのが核心構造です
* なぜ DM を外側に保つかは、3 つの古典原理が分担して説明します: **Goodhart (指標の目標化による proxy 機能の喪失) / Lucas critique (政策不変性の崩壊) / Informativeness principle (信号の質 = welfare 上限)**
* 更に上位の結論として、**真の完全な目的関数 \theta^\* が存在しない以上、\theta proxy を外部から定期再校正する FB 制御主体が構造的に必須** になります。3 原理はこの「外部 proxy 制御が必要」という structural 制約を 3 角度から保証する原理として読めます
* システムには 2 つの feedback loop が走ります。内側の **fast loop** (operate agents が所与の \theta で最適化) と、外側の **slow loop** (Analyst → Decision Maker → Compute layer)。**slow loop の質が system の welfare 上限を決めます**
* 結論として、**operate 系 (Marketing / CS / Sales / Inventory ops、Junior Analyst) はこの仕組みで agent 化可能な領域に入り、design / govern 系 (\theta author、Senior Analyst、Domain Expert、Data Engineer、Compliance、Agent shaper) は構造的に人手に残り、むしろ critical になります**

agent 時代のデータ基盤投資は、**Medallion + Ontology という capital と、KPI / 制約 / 業務語彙を author できる人的 skill の補完関係** として理解できます。

---

## 参考

### Medallion architecture (Databricks)

### Ontology (Palantir Foundry / AIP)

### Reverse ETL (Mart user feedback loop の祖先)

### Semantic layer (compute 層の OSS / SaaS 表現)

### 経済学の原典

* Holmström, B. (1979). "Moral Hazard and Observability". *Bell Journal of Economics*, 10(1) — informativeness principle の原典
* Lucas, R. E. (1976). "Econometric Policy Evaluation: A Critique" — Lucas critique の原典
* Goodhart, C. (1975). "Problems of Monetary Management" — Goodhart's law の原典
