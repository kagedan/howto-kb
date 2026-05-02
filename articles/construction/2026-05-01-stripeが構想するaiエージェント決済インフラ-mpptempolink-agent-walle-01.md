---
id: "2026-05-01-stripeが構想するaiエージェント決済インフラ-mpptempolink-agent-walle-01"
title: "Stripeが構想するAIエージェント決済インフラ - MPP、Tempo、Link Agent Wallets...etc"
url: "https://zenn.dev/komlock_lab/articles/stripe-sessions-2026"
source: "zenn"
category: "construction"
tags: ["API", "AI-agent", "LLM", "OpenAI", "Gemini", "zenn"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

こんにちは！ブロックチェーンエンジニアの山口夏生です。  
ブロックチェーン×AI Agentで自律経済圏を創る開発組織Komlock labでCTOをしています。

この記事では、いま話題になっている Stripe Sessions 2026 の発表を、 **AIエージェント決済インフラ** という観点で4つの軸に分けて解説していきます。

2026年4月29日に開催された **Stripe Sessions 2026** で発表された新機能は288個。前年Sessions 2025の約100から3倍弱、参加者は9,000人以上、Q1 2027までの公開ロードマップは334項目です。

発表の中には、自前のブロックチェーン（Tempo）、AIエージェント向け決済プロトコル（MPP）、開発スタック全体の請求統合（Stripe Projects）── どれも「決済API」の延長線上にはない、新領域への踏み込みが含まれています。

> "AI is the biggest platform shift for the economy since the internet, and in the not-too-distant future agents will account for most transactions online."
>
> — Patrick Collison（Stripe CEO・共同創業者）

「AIはインターネット以来の経済における最大のプラットフォームシフトであり、近い将来、エージェントがオンライン取引の大半を占める」。Sessions 2026の発表は、すべてこの一文を起点に組み立てられています。

<https://stripe.com/blog/everything-we-announced-at-sessions-2026>

Sessions 2026 当日にStripe公式アカウントが出した投稿のうち、特に反響が大きかったのが Link Agent Wallet の発表でした。エージェントへの支払い権限委任、決済情報の非露出、購入ごとの承認、という3点が要点です。

<https://x.com/stripe/status/2049529444092838116>

もう一つ反響が大きかったのが、新しい Stripe Treasury です。多通貨とステーブルコインの保管、米国企業間の即時無料送金、メールアドレスだけで160カ国に送金、といった機能が並びます。

<https://x.com/stripe/status/2049621560743608481>

## Sessions 2026の全体像

### Stripeの自己定義の変化

Sessions 2026のキーフレーズは「**Building the economic infrastructure for AI**」。Stripeは自社を「インターネットの経済インフラ」から「**AIの**経済インフラ」へと再定義しました。

これは大きな違いです。インターネット時代の決済は「人がボタンを押す」前提で設計されてきました。AIエージェントは人間のレイテンシを持たず、1秒間に何度もマイクロトランザクションを発生させます。前提条件が変われば、抽象化レイヤーも作り直す必要が出ます。

### 4つの軸で整理する

288件の新機能は、以下の4軸で整理できます。

* 軸①: AIエージェント時代の決済プリミティブ（MPP / Link Agent / Agentic Commerce）
* 軸②: 自前ブロックチェーンとマイクロペイメント基盤（Tempo / Streaming Payments）
* 軸③: 開発者プラットフォーム化（Database / Projects / Workbench）
* 軸④: 従来決済の継続深化（Radar / Treasury / Tax / Terminal）

ここからが本題。それぞれの軸を順に見ていきます。

## 軸①: エージェント時代の決済 - Link Agent Wallet と MPP

今回の発表の中で最も象徴的だと考えているのが **Link Agent Wallet** と **Machine Payments Protocol（MPP）** の組み合わせです。前者がユーザー側の「誰が支払うか」、後者がプロトコル側の「どう支払うか」を埋めます。

### Linkとは何か - 2.5億ユーザーの「ワンクリック決済」

Linkは、Stripeが提供する **加盟店横断のワンクリック決済ウォレット** です。一度カード情報を登録すれば、別のLink対応加盟店でもメールアドレスとSMSコードだけで決済が完了します。Apple Pay や Google Pay が OS に紐づくのに対し、Link はブラウザ・アプリ・OS問わずどこでも使えます。

ローンチ後の数年で、グローバルで **2億5000万ユーザー** に到達しました。Shop Pay（Shopify）の規模感を超え、Apple Pay や PayPal に次ぐ位置にあります。2億ユーザー到達時の Patrick Collison の投稿が背景として参考になります。

<https://x.com/patrickc/status/1973031173141012943>

| ウォレット | 主な紐付け | グローバルユーザー規模 | 特徴 |
| --- | --- | --- | --- |
| Apple Pay | iOSデバイス | 推定6億〜 | ハードウェア依存 |
| Google Pay | Androidデバイス | 推定数億 | OS依存 |
| Shop Pay | Shopifyストア | 約1.5億 | Shopify特化 |
| PayPal | 単独アカウント | 4.3億 | 老舗、独立系 |
| **Link** | **メール + SMS** | **2.5億以上** | **OS非依存、加盟店横断** |

伸びた要因は、**Stripe加盟店であれば追加実装ほぼゼロでLinkが使える**こと。チェックアウト画面に組み込まれたLinkボタンを通じて、ユーザーが意識せずアカウントを作るケースが多くなっています。

### Link Agent Wallet - エージェントに支払いを委任する

Sessions 2026の目玉が **Link Agent Wallet** です。Linkに「ユーザーが自分のAIエージェントに支払い権限をスコープ付きで委任できる」機能が追加されました。

ポイントは3つ。

1. **スコープ制限** - 金額上限・カテゴリ・加盟店リストでエージェントを縛れる
2. **承認フロー** - 一定額を超える購入は人間の承認が必要
3. **クレデンシャルの分離** - エージェント用のクレデンシャルはユーザー本人と別に発行され、漏洩時の被害を限定できる

Stripeは別途 **Agent Guardrails** も発表しており、エージェントID割り当て・スコープ制限・承認フローが一元管理されます。

### Linkロードマップ - ネイティブアプリとAdaptive Pricing

公開ロードマップによれば、Linkは2026年中に以下が予定されています。

| 時期 | 機能 | 内容 |
| --- | --- | --- |
| Q2 2026 | Linkネイティブアプリ GA | iOS / Android のスタンドアロンアプリ |
| Q2 2026 | Adaptive Pricing 拡大 | 為替レートとリスクに応じた価格自動調整 |
| Q3〜Q4 | Issuing 連携強化 | Linkユーザー向けカード発行（消費者向け） |

ネイティブアプリの登場は、Linkを「加盟店のチェックアウトに組み込まれた決済手段」から **自立した消費者向け金融アプリ** へ転換させます。Cash App や Venmo の競合領域に踏み込む動きです。

### Machine Payments Protocol（MPP）とは何か

ここまではユーザー側の委任の話。次にプロトコル側を見ていきます。

MPPは、AIエージェントが他のサービスに支払うためのオープンスタンダードで、Stripeとブロックチェーン企業 **Tempo** が共著で策定しました。特徴は3つ。

1. **「sessions」プリミティブ** - 事前にspending limitを設定し、その範囲内で連続的にマイクロペイメントを発生させられる
2. **Shared Payment Tokens（SPT）** - ステーブルコイン・カード（Visa、Mastercard）・Klarna・Affirm を同じ抽象化で扱える
3. **オープン標準** - Visa、Mastercard、Cloudflare、Anthropic、OpenAI、Lightspark がすでに対応表明

<https://stripe.com/blog/machine-payments-protocol>

Tempo公式の発表投稿はこちらです。Day 1 でステーブルコインとカードの両方をサポートしている点が要点です。

<https://x.com/tempo/status/2034253707303338264>

### MPPの決済フロー

ポイントは「session一発でauthorizeすれば、その後は連続支払いができる」こと。PaymentIntent単位の従来Stripe決済でも、トランザクション単位のブロックチェーン送金でも実現できなかった粒度です。

実装詳細と、CoinbaseとAnthropicが推進している **x402** との違いについては、Komlock labで別記事にまとめています。

<https://zenn.dev/komlock_lab/articles/mpp-hands-on>

「AIエージェントには手がない」という切り口でMPPを解説した投稿も、イメージしやすくて参考になります。

<https://x.com/akshay_pachaar/status/2034624014153556263>

Linkの隣で発表された **Agentic Commerce Suite** は、加盟店がAIエージェント経由で商品を売るための機能群です。

* **Stripeダッシュボードから商品カタログをアップロード**
* **Meta（Facebook広告）内でネイティブチェックアウト** - 広告から離脱せず購入完了
* **Google AI Mode / Gemini アプリでの購入** - Universal Commerce Protocol で接続
* **プラットフォームの connected account も「agent-ready」化可能**

加盟店は自前でAIエージェント対応の実装をせず、ダッシュボード操作だけで Meta / Google のエージェント経済圏に商品を流通できます。

> "If AI can solve Nobel level physics problems but can't buy a domain, something's gone wrong."
>
> — Patrick Collison（基調講演）

「ノーベル賞レベルの物理問題は解けるのに、ドメイン1つ買えないのはおかしい」。この問題意識が Link Agent Wallet・MPP・Agentic Commerce Suite を一つの絵に繋いでいます。

| レイヤー | プロダクト | 役割 |
| --- | --- | --- |
| 経済主体 | Link Agent Wallet | 「誰が」支払うかの委任 |
| 通信プロトコル | MPP | 「どう」支払うかの標準 |
| 商業流通 | Agentic Commerce Suite | 「何を」売買するかの市場接続 |

## 軸②: Tempo Mainnet と Streaming Payments

### なぜStripeが自前のブロックチェーンを持つのか

Tempoは、StripeとParadigmが共同で開発した決済特化型ブロックチェーンで、2026年3月18日にmainnetが稼働しました。MPPはこのmainnetローンチと同時に公開されています。

<https://tempo.xyz/blog/mainnet/>

自前のチェーンを持つ理由はレイテンシとコストの2点です。

* **レイテンシ**: Ethereum L1のブロック生成は12秒、Solanaでも400ms。マイクロペイメントには遅すぎる
* **コスト**: ガス代が$0.001の取引で1セント以上かかると、ストリーミング決済は成立しない

Tempoは payment-specific blockchain として、これらの制約を解消するために設計されています。100以上のサービスがmainnetと同時に互換性を表明しました。

### Streaming Payments のアーキテクチャ

Tempoの代表的ユースケースが **Streaming Payments**。課金SaaSの **Metronome**（usage tracking）と Tempo（settlement）の組み合わせで、LLM APIの「1トークン = 1マイクロペイメント」を可能にします。

LLM APIの課金は「月末まとめてカード請求」が標準でしたが、Streaming Paymentsではトークンを消費した瞬間に支払いが完了します。**与信を持ちたくない売り手が、即時決済の安心感でAIエージェントに API を売れる**ようになることのインパクトは大きいと考えています。

### ステーブルコイン関連の拡張

| 機能 | 拡張内容 |
| --- | --- |
| ステーブルコイン決済 | 32カ国を追加対応 |
| Crypto Onramp | ヘッドレス実装、カスタムステーブルコイン対応 |
| ステーブルコインカード（Issuing） | 30カ国で消費者・商用カード発行 |
| Privy統合 | デジタル資産アカウント、DeFi yield、マルチチェーン残高 |
| Bridge（Open Issuance） | ビジネス向けステーブルコイン発行・管理 |

Stripeはステーブルコインを単なる決済手段ではなく **計量単位** として再定義し、その上に Issuing・Treasury・Onramp を一気通貫で組み上げています。

### Treasury × 暗号資産 - 「資金管理」のレイヤー再定義

最も大きな転換点だと考えているのが **Stripe Treasury の暗号資産対応** です。

Stripe Treasuryは **B2B向けのバンキング・アズ・ア・サービス（BaaS）** で、Stripeを使う企業が自分たちのプラットフォーム上でユーザーに銀行口座機能を提供する仕組み。ACH送金、SWIFT、複数通貨保管、即時送金が抽象化されています。

これまで「法定通貨ベースのデジタル銀行口座」だったTreasuryに、Sessions 2026では3つの拡張が入りました。

#### 拡張①: 法定通貨で15通貨対応

USD・EUR・GBP・JPY・AUDなど **15通貨** に年内対応。これまで主にUSDだったため、グローバル企業が複数通貨で残高を持ち、必要に応じて両替・送金できるようになります。

#### 拡張②: ステーブルコイン残高サポートが160カ国に

| 対応範囲 | 国数 | 意味 |
| --- | --- | --- |
| 法定通貨ベース | 100カ国以上 | 銀行ライセンス・規制対応が必要 |
| **ステーブルコインベース** | **160カ国** | 銀行に依存せず、ブロックチェーン上で完結 |

法定通貨対応は現地の銀行ライセンスとレールが必要で、拡大には数年単位のリードタイムがかかります。一方、ステーブルコインは **Tempo や既存EVMチェーン** で完結するため、規制対応さえクリアすれば一気に展開できます。

つまり、Stripeは「銀行レールが届かない60カ国」をステーブルコインで先取りに行っています。新興国向けB2Bフィンテックの構造を変える動きです。

#### 拡張③: Bridge × Privy による「Treasury × DeFi」スタック

新しいユースケースは3つ。

1. **企業独自ステーブルコインの発行** - Bridge の Open Issuance で自社ブランドのステーブルコインを発行（PayPal USD のようなもの）
2. **Treasury 残高のDeFi yield** - 遊休資金をPrivy経由でAave / Morpho 等に預けて利息収益を得る
3. **クロスボーダー送金の「銀行スキップ」** - SWIFTを通さず、Tempo + ステーブルコインで国際送金を即時化

特に3点目は、送金代行で稼ぐ Wise（旧TransferWise）や Revolut のビジネスを直接侵食します。Stripeが「銀行ではなくブロックチェーン経由で国際送金プラットフォームを作る」と宣言したに等しい動きです。

#### 拡張④: ステーブルコインIssuing（カード発行）

**Stablecoin Card** が30カ国で利用可能に。ステーブルコイン残高を担保に物理・仮想カードを発行し、Visa/Mastercardネットワーク上で使える仕組みです。

ユーザーから見ると「USDCを保有しているけど、コンビニでも使える」体験。Stripeが **「保有はオンチェーン、消費はオフチェーン」のブリッジ役** を担います。

総合すると、Treasuryは「Stripe版マネーフォワードクラウド」ではなく **法定通貨とステーブルコインをシームレスに扱う企業向け金融OS** になっています。Sessions 2026 で最も「規制業界の既得権益」に踏み込んだ発表だと考えています。

## 軸③: 開発者プラットフォームへの拡張 - Stripe Database / Projects

### "Vibe deploying" の宣言

Stripeは「決済API」から「開発者向け統合プラットフォーム」へ拡張しています。象徴的だったのが John Collison のキーノートでの発言です。

> "Vibe coding is so 2025. The leading edge is now in vibe deploying, and Stripe Projects lets you do just that."
>
> — John Collison（Stripe President・共同創業者）

「Vibe codingはもう2025年の話。最先端は今やvibe deployingで、Stripe Projectsがそれを可能にする」。

Patrick Collison は、Andrej Karpathy が MenuGen をデプロイする際に「IKEA家具を組み立てるような苦痛」だったというコメントを引き合いに、Stripe Projects の動機を説明しています。

<https://x.com/patrickc/status/2037190688950161709>

### Stripe Database

**Stripe Database** はStripeのデータをリードオンリーのマネージド Postgres として提供します（プレビュー）。

* 1コマンドでスピンアップ
* ライブデータに直接SQL
* Webhook や API ポーリングが不要

これまではWebhookを受けて自前DBに同期するか、APIを定期ポーリングするか、Stripe Sigma を使うしかありませんでした。Stripe Databaseは中間レイヤーを丸ごと不要にします。

### Stripe Projects

**Stripe Projects** はもっと野心的です。Stripeダッシュボードから、ホスティング・データベース・認証・オブザーバビリティ・分析・AIまで開発スタック全体をプロビジョニングし、**請求も Stripe に集約**できます。

公式の発表投稿にコンセプトが端的にまとまっています。

<https://x.com/stripe/status/2037197998074335292>

ローンチ時点で32パートナーが統合済み、新たに14社が追加。**PlanetScale** は co-design partner として深く関与しています。

```
# Stripe CLIから1コマンドでPlanetScale Postgresがプロビジョニングされる例
stripe projects add planetscale-postgres --name my-app-db
```

Supabaseを1コマンドで追加した実例はこちら。

<https://x.com/jonmeyers_io/status/2037291814856913221>

つまり、**Vercelが「デプロイのHeroku」を再発明したのと同じ抽象化を、Stripeは課金とインフラ全体に対して行っている**ということです。

### その他の開発者向け発表

| 機能 | 概要 |
| --- | --- |
| Stripe Workflows | GA。ループ・カスタムアクション対応のワークフローエンジン |
| Custom Objects | 独自のビジネスデータをStripeに直接モデル化 |
| Reports API v2 | プログラマティックな財務レポート取得（プレビュー） |
| Workbench強化 | API traffic、rate limit、integration health をダッシュボード内で監視 |
| Claimable Sandboxes API | サンドボックス環境のプラットフォーム統合 |
| Automated Key Exchanges | ライブAPIキーの安全な受け渡し（プレビュー） |

## 軸④: 従来決済の深化 - 速報まとめ

Stripe本業の機能拡張も今回の発表に多数含まれています。要点を表で整理します。

| カテゴリ | 機能 | 内容 |
| --- | --- | --- |
| Radar | Bot Abuse Prevention | AIエージェントと詐欺者を区別（プレビュー） |
| Radar | Free Trial Abuse | 無料試用悪用検出 |
| Radar | Stripe Signals | オフプラットフォーム決済の不正検出 |
| Treasury | 多通貨対応 | 年内に15通貨対応予定 |
| Treasury | 無料即時送金 | 米英企業間 |
| Issuing | Stripe Card | 2%キャッシュバック付きMastercard |
| Tax | 米国税申告自動化 | TaxJar連携 |
| Capital | 地域拡大 | フランス・ドイツで利用可能、豪州・カナダ近日 |
| Terminal | Reader T600 | 8インチスクリーンPOS、カスタムアプリ実行可 |
| Terminal | 地域拡大 | 香港・メキシコ含む15市場追加 |
| 決済手段 | 新規対応 | Pix、UPI、Sunbit、Bizum、Pay by Bank、TWINT |
| Platforms | Network Cost Passthrough | IC++ を45市場で利用可能 |
| Platforms | Cross-border Payouts | 米英EU加間の越境送金 |

特に注目したのが **Radar の Bot Abuse Prevention** です。AIサービスへの新規サインアップは **6件に1件が詐欺アカウント** で、Radarは月間 **330万件以上の危険なサインアップをブロック** しています。AIエージェント自体は正当な利用者として扱う必要があり、「悪意あるbot」と「正当なエージェント」を区別する技術が決済インフラに不可欠になっています。

## 数字で見るStripeの規模

| 指標 | 値 |
| --- | --- |
| Linkユーザー数 | 2億5000万以上 |
| 1日の企業間決済件数 | 480万件 |
| Stripe Connect利用プラットフォーム数 | 16,000以上 |
| プラットフォーム経由で決済処理するビジネス数 | 1,100万 |
| Authorization Boost効果 | 平均3.8%の認可率向上、最大3.3%のコスト削減 |
| Treasury対応国（法定通貨） | 100カ国以上 |
| Treasury対応国（ステーブルコイン） | 160カ国 |
| AI新規サインアップの詐欺率 | 6件に1件 |
| Radarの月間ブロック数 | 330万件以上 |

Stripeはすでに「決済処理量」では十分すぎる規模を持っています。Sessions 2026の発表が **「AI / 開発者 / ブロックチェーン」という新領域への横展開** に振り切れているのは、本業がもう成熟段階にあるからです。

## 個人的な考察 - Stripeは何になろうとしているのか

### 「決済会社」から「経済OS」への変質

**Stripeは決済会社であることをやめつつあります**。正確には、これまでの決済事業を土台にして、その上に「AI時代の経済OS」を構築しようとしています。

### ブロックチェーン視点での評価

Tempoは「企業主導 + オープンスタンダード」という新しいタイプのチェーンです。Solana、Base、Arbitrum のような汎用チェーンと違い、**ペイメントに用途を絞った**点が特徴。Consensusレイヤーまで含めて決済最適化されており、Visa/Mastercard の暗号版とも言えます。

ただし矛盾もあります。Tempoがオープンスタンダード（MPP）の上に乗る以上、エコシステムが育てば「Stripe以外の決済プロバイダ」がTempo上で同じMPPを実装するのは原理的に可能です。Stripeはこの矛盾を承知で、**「先行者として標準を定義する」ことの戦略的価値** に賭けています。

結果が出るには3〜5年かかると見ています。

### 開発者として注目すべきAPI

今回の発表の中から、今すぐ触っておく価値があるものを3つ。

1. **MPP** - エージェント決済を実装するなら、Stripe + Tempo の標準として最初に触る
2. **Stripe Database** - これまでWebhook → 自前DBで書いていたコードがほぼ不要になる
3. **Stripe Projects** - 個人開発・スタートアップで「請求と契約管理」を一元化したい人向け

逆に追わなくてよさそうなのは、Tempoのアプリケーション開発（mainnet直後でエコシステムが薄い）と、Privy統合のDeFi yield周り（現状Stripe顧客のメインユースケースには遠い）です。

## まとめ

Sessions 2026の288件の新機能は、4軸で整理してみると、ばらばらの機能リストというより一つの方向に向かう動きとして読めます。

* 軸①: AIエージェント時代の決済プリミティブ（MPP / Link Agent / Agentic Commerce）
* 軸②: 自前ブロックチェーンとマイクロペイメント基盤（Tempo / Streaming Payments）
* 軸③: 開発者プラットフォーム化（Database / Projects / Workbench）
* 軸④: 従来決済の継続深化（Radar / Treasury / Tax / Terminal）

4軸が「AIのための経済インフラを構築する」というメッセージで貫かれています。**機能が増えたのではなく、Stripeの定義そのものが変わった** と表現するのが近いです。

引き続き、AIエージェント × ブロックチェーン × 決済の交点で起きている動きを追っていきます。

---

最後まで読んでいただきありがとうございました！  
この記事が参考になったら、ぜひいいねやコメントをお願いします。

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

## 参考リンク
