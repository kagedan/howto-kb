---
id: "2026-04-24-google-cloud-next-26-現地レポai-エージェントはパイロット開発から本番へ-01"
title: "Google Cloud Next '26 現地レポ——AI エージェントはパイロット開発から本番へ"
url: "https://zenn.dev/softbank/articles/e9b87af5589994"
source: "zenn"
category: "construction"
tags: ["MCP", "API", "AI-agent", "Gemini", "zenn"]
date_published: "2026-04-24"
date_collected: "2026-04-25"
summary_by: "auto-rss"
query: ""
---

## AI エージェントのパイロット開発は終わり

ラスベガスの Mandalay Bay Convention Center で開幕した Google Cloud Next '26 の Opening Keynote（2026-04-22 PDT）を現地で視聴してきました。

ここ数年Google Cloud Next に来ていると、その年の Google Cloud が「どのモードで来たか」は、キーノート冒頭 10 分で分かります。去年の Next '25 は「Gemini Enterprise を使って生成 AI を仕事に」という**実験と事例紹介のモード**でした。

今年は全く異なる雰囲気となりました。Thomas Kurian（Google Cloud CEO）は開幕早々に **"Today, that future is running in production at a scale that the world has never seen."**（今日、その未来は世界がこれまで見たことのない規模で本番稼働している）と切り出し、続けて **"You have moved beyond the pilot. The experimented phase is behind us, and now the real challenge begins."**（皆さんはすでにパイロットを越えた。実験のフェーズは後ろに、ここから本当の課題が始まる）と宣言しました。会場の密度と反応から、**「もう実験の話はしない、運用と統治の話をする」** という空気がありありと伝わってきたのが今年のハイライトでした。

本記事では、**現地の熱狂をなるべく皆さんにそのまま伝える形**で、テクニカルな面での深掘りを少しだけ交えながら Google Cloud Next '26 Opening Keynote の内容をまとめていきます。Google Cloud が今回打ち出した **5 層スタック**という全体像と、筆者が注目した **4 つの転換点**——Agent ガバナンスの4スタック、Optimize 層の新設、Cross-Cloud Lakehouse、TPU 8t / 8i の分岐——を順に見ていきます。  
![AI agents for every industry——Kurian 氏冒頭の基調スライド](https://static.zenn.studio/user-upload/5f2bf069fbad-20260424.jpg)  
*写真: "AI agents for every industry" のメッセージと 多数のパートナーロゴが並ぶ冒頭のスライド投影（現地撮影）。エージェント時代が「一部の先進企業の実験」ではなく、**全産業のエコシステム** で動き始めたことを一枚で宣言している*

## エージェント運用時代の到来

本題の 4 つの転換点に入る前に、今年のキーノート全体のトーンを決めた **2人の CEO のメッセージ**を紹介させてください。どちらも最初の 15 分で語られ、「エージェントは作れるのか」から「何千個をどう運用するのか」への **問いの転換** が、この節の核です。

**Kurian 氏**の冒頭宣言は、背筋が伸びる種類の言い切りでした。

> "Just one year ago, we stood on this same stage and promised a new future for AI. Today, that future is running in production at a scale that the world has never seen."  
> （わずか 1 年前、同じステージで AI の新しい未来を約束した。今日、その未来は世界がこれまで見たことのない規模で本番稼働している）

> "You cannot deliver AI by piecing together a puzzle piece of fragmented silicon and disconnected models. To drive real value, you need an architecture where chips are designed for the models, models are grounded in your data, agents and applications are built with models and secured by the infrastructure."  
> （断片的なシリコンと切り離されたモデルを継ぎ接ぎして AI を届けることはできない。本当の価値を生むには、チップがモデル向けに設計され、モデルがデータに根ざし、エージェントとアプリケーションがモデルで構築されインフラで守られる——そういうアーキテクチャが必要だ）

去年まで「実験と事例紹介」で済んだ話題が、今年は「本番移行済みの前提」で語られ始める——この空気の転換を、Kurian 氏が開幕で宣言しました。そして、断片的なチップとモデルを継ぎ接ぎしては AI を届けられない、**チップ→モデル→データ→エージェント→インフラ**まで一貫したアーキテクチャが要る、という**垂直統合の必要性**を明示していました。この一言が、後述するGoogle Cloudの「5 層スタック」の伏線となっています。

続く **Sundar Pichai（CEO, Google and Alphabet）** は、さらに踏み込んだ転換を言語化します。

> "The conversation has gone from 'Can we build an agent?' to 'How do we manage thousands of them?'"  
> （話題は「エージェントは作れるのか？」から「その何千個をどう管理するのか？」へと変わった）

エージェント導入の問いが「作れるのか」から「何千個を運用できるのか」へ——これは 1 個から N 個への単純なスケールではなく、**質そのものが変わる転換** です。この一行が、今回の発表の大半（特に後述する Govern 層 4 点セットと Optimize 層の新設）の動機を包括的に説明しています。

さらに Pichai 氏は、Google 自身がこの転換にどれだけ本気で投資しているかを、3 つの数字で示しました。

* **CAPEX**: 2022 年 $31B → 2026 年 $175-185B（4 年で**約 6 倍**）
* **ML コンピュート**: 2026 年は**半分以上を Cloud 事業に振り向ける**
* **社内コード生成**: 75% のコードが AI 生成（半年前の 50% から 25 ポイント上昇）

![Sundar Pichai がステージで示した "~75% of all new code at Google is AI generated" スライド](https://static.zenn.studio/user-upload/300459e986de-20260424.jpg)  
*写真: Pichai 氏の登壇スライド。"~75% of all new code at Google is AI generated and approved by engineers"（Google の新規コードの約 75% は AI 生成）と明示（現地撮影）*

> "A big focus for us is to always be customer zero for our own technologies."  
> （私たちにとって大事なのは、自社の技術の "customer zero"——最初の顧客——であり続けることだ）

3 つの数字は、Pichai 氏が "customer zero"（自社が最初の顧客）と呼ぶ戦略の裏付けです。**Google 自身が本番で使えないものを顧客に売らない**——この姿勢が、後述する Gemini Enterprise Agent Platform の Scale 層の全 GA 昇格や、Govern 層の密度に具体化されていると考えています。

そして Pichai 氏のビデオメッセージを経てKurian 氏がステージに戻ると、**早速Appleとの大型提携**について発表を行いました。

> "Earlier this year, we announced a monumental partnership with one of the world's most iconic brands."  
> "We're collaborating with Apple as their preferred cloud provider to develop the next generation of Apple Foundation models based on Gemini technology. These models will help our future Apple intelligence features, including a more personalized Siri, coming later this year."  
> （今年初め、世界で最も象徴的なブランドの 1 つと記念すべきパートナーシップを発表しました。Apple の優先クラウドプロバイダーとして、次世代 Apple Foundation Model を Gemini ベースで開発することで協業します。これらのモデルは、今年後半に投入される Apple Intelligence 機能——よりパーソナライズされた Siri を含む——に貢献します）

**Apple の次世代 Foundation Model を Gemini ベースで開発、Apple Intelligence と Siri のパーソナライゼーションに今年後半投入**——ステージの大スクリーンに Apple のロゴが一瞬映し出された時、会場の密度が一段上がったのを覚えています。Apple と Google のインフラ層の関係が一段深まるという構造的インパクトを持ちつつ、キーノートの流れでは **Google Cloud の方針宣言の締め** として位置付けられていました。

![Apple 提携発表の瞬間](https://static.zenn.studio/user-upload/26c1cb14d359-20260424.jpg)  
*写真: 巨大スクリーンに Apple ロゴが光り、Kurian 氏がステージ中央で提携を宣言した瞬間（現地撮影）*

## Google Cloud Next '26 で打ち出されたGoogle Cloud 「5 層スタック」

Kurian 氏は冒頭で、Google Cloud の現在提供しているサービスを **5 層のスタック**として再整理してみせました。

1. **AI Hypercomputer**（計算基盤）
2. **Agentic Data Cloud**（データ基盤）
3. **Agentic Defense**（セキュリティ基盤）
4. **Gemini Enterprise Agent Platform**（エージェント基盤 / Agent Platform and Models）
5. **Agentic Taskforce**（業務適用層 / CX、Workspace Intelligence）

![Agentic Enterprise Blueprint——5 層スタック](https://static.zenn.studio/user-upload/f8194c5cc46c-20260424.jpg)  
*写真: ステージに投影された 5 層スタックのビジュアライゼーション。下から AI Hypercomputer、Agentic Data Cloud、Agentic Defense、Agentic Platform and Models、Agentic Taskforceの順で積み重なる（現地撮影）*

この語り口そのものが、今年の最大のメッセージだと私は受け取りました。去年までは「Gemini Enterprise」「Vertex AI」「BigQuery」「Mandiant」などのプロダクトが個別に語られていました。今年は **これらが 5 層の垂直統合スタックとして 1 つの製品** になり、**各層の新機能を共通の設計思想（エージェント駆動）で貫く**、という構造が明示されています。

5 層は下から上に積み重なっています、またこの順序は変えることができません。つまり、コンピュートがなければデータがなく、データがなければエージェントに与えるべき文脈がなく、防御がなければ本番に上げられず、プラットフォームがなければ業務適用できない——**各層が下位の層に明示的に依存する設計**となっています。今年の発表の多くは、最下層（Hypercomputer）から業務層（Taskforce）までの **「積層の継ぎ目」を埋める機能** だった、と現地で聴いていて感じました。

この5層スタックの戦略から読み取れる **Google Cloudの転換点** を、以下に整理していきます。

## 転換点 1: Agent 統治 4 点セット —— Zero Trust for Agents

![Gemini Enterprise Agent Platform の 4 軸（Build / Scale / Govern / Optimize）構造図](https://static.zenn.studio/user-upload/619160a047fa-20260424.jpg)  
*図: Google Cloud Blog より引用（[Welcome to Google Cloud Next '26](https://cloud.google.com/blog/topics/google-cloud-next/welcome-to-google-cloud-next26)）。Agent Platform の Build / Scale / Govern / Optimize の 4 軸配置*

今年のキーノートで **"Vertex AI" という名前がほとんど使われなかった** 事実に一言触れておきます。同日午後の Agent Platform セッションでは **"Agent Platform is the renamed Vertex AI"**（Agent Platform は Vertex AI をリブランドしたものである）と明言され、Vertex AI の全サービスとロードマップ進化は今後 **Agent Platform を通じてのみ提供される** という方針が公式化されました。つまり、これは単なるVertex AI の製品名変更ではなく、Google Cloud が **「AI モデルを中心としたAIアプリ開発プラットフォーム」** から **「エージェント中心のプラットフォーム」** へ と、主戦場を移したという戦略宣言が込められていると受け取っています（Agent Platform 全体像の公式解説は [Introducing Gemini Enterprise Agent Platform](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform?hl=en) を参照）。

そのGoogle Cloudの意思表示の一つが **AIエージェントのガバナンス機能** の拡充です。エージェント導入で PoC から本番に上げるとき必ずぶつかる、「このエージェント、誰の ID で動いてるの？」「何を操作できるの？」「それを誰が監査するの？」という 3 つの問いへの回答が、今回のキーノートで一通り揃いました。

Kurian 氏は基調講演でこう明言しました。

> "We're bringing zero-trust verification to every agent and every orchestration step. With Agent Identity, every agent has a unique cryptographic ID and well-defined authorization policies that are traceable and auditable. They're centrally managed through our Agent Gateway, which provides a single command center for policy enforcement across the organization. Paired with Model Armor, you protect your models and your proprietary enterprise data from threats such as sensitive data leakage."  
> （全てのエージェント、全てのオーケストレーションステップに Zero Trust 検証を導入する。Agent Identity により、各エージェントは一意の暗号化 ID と、トレース・監査可能な認可ポリシーを持つ。これらは Agent Gateway で一元管理され、組織横断のポリシー執行の単一制御面を提供する。Model Armor と組み合わせることで、モデルと企業の機密データを、機密情報漏洩などの脅威から守る）

Zero Trust を人間の認証に使う話は珍しくなくなりましたが、ここでは同じ考え方を**エージェントそのものに適用**する、と宣言されています(なお引用中の **Model Armor** は、プロンプト注入・機密データ漏洩・有害出力を検査・遮断する Gemini などのモデル向けのガードレール機能)。この「Zero Trust for Agents」を構成する4 つのコンポーネントが以下となります。

| コンポーネント | 状態 | 役割 |
| --- | --- | --- |
| **Agent Identity** | New | 全てのエージェントに一意の暗号化 ID、追跡・監査可能な認可ポリシー |
| **Agent Registry** | New | 組織内の全ての内部エージェント・ツール・MCP サーバーを一元カタログ化。発見可能性と統治の両立 |
| **Agent Gateway** | New | エージェント間トラフィックの「航空交通管制」。**MCP（Model Context Protocol、外部ツール・サーバーとの標準接続）** と **A2A（Agent-to-Agent、エージェント同士の通信）** プロトコルを理解し、中央集権的なポリシー執行、Model Armor 統合で機密データ漏洩・プロンプト注入・ツールポイズニングを防ぐ |
| **Agent Anomaly Detection** | New | 推論ドリフト、ツール不正使用、意図しない結果につながる挙動を、**エージェントのアクションの意図を分析**して事前検知 |

注目すべきは、今回発表された Gemini Enterprise Agent Platform 全体の **新機能 11 個** のうち、**Govern 層だけで 4 個** が集中している配分です。Build（ADK / Agent Studio）も Scale（Runtime / Sandbox / Memory Bank 等）も Optimize（後述）も新機能を持ちますが、数として最も重心が置かれているのは Govern 層でした。

この配分から読み取れるのは、**AIエージェントの運用を「自信を持って本番展開できる」状態に引き上げに来ている**ということです。つまり、PoC を超えて本番投入するときに現場で必ず聞かれる典型的な 4 つの問いに対して、**プロダクト名で直接答えられる**という状態になってきているということです。まとめると以下のようになります。

| 現場の問い | その答え（プロダクト名） |
| --- | --- |
| このエージェント、誰の ID で動いているか？ | **Agent Identity** が一意の暗号化 ID を割り当て、監査可能な認可ポリシーを紐付け |
| 組織内のエージェントを把握できるか？ | **Agent Registry** が全エージェント・ツール・MCP サーバーを一元カタログ化 |
| 機密情報の漏洩はどのように防ぐか？ | **Agent Gateway** + **Model Armor** がポリシー執行と内容検査 |
| 想定外の挙動を検知できるか？ | **Agent Anomaly Detection** が推論ドリフトを事前検知、必要時に人間にエスカレーション |

Kurian 氏自身がこの構図のキーメッセージを一言で置いています。

> "Agent Registry provides a single point of control, indexing every intelligent agent and tool across your organization to ensure they are discoverable and governed."  
> （Agent Registry は組織内の全てのエージェントとツールを一元インデックスし、発見可能性と統治の両立を実現する）

**Agent Registry から入り、Agent Identity で ID モデルを固め、Agent Gateway でポリシー執行面を作り、Agent Anomaly Detection で観測を効かせる**——この 4 点セットは、エージェント運用の本番化を現実のものとするでしょう。これまでVertex AIで提供されている製品を利用してスクラッチで組み上げる必要のあったエージェントの運用・ガバナンスの課題をまとめて解決する強力なソリューションとして期待しています。

## 転換点 2: Optimize 層の丸ごと新設 ——「PoC 神話」の終わり

Gemini Enterprise Agent Platform の 4 軸は **Build / Scale / Govern / Optimize** です。4 つ目の Optimize 層は、**今回丸ごと新設**されました(一部の機能は、これまでの Vertex AI Agent Builder の中の機能として提供されていた機能群となります)。

| コンポーネント | 役割 |
| --- | --- |
| **Agent Evaluation** | マルチターン自動採点で、**本番トラフィックに対してリアルタイムスコアリング**。品質劣化と異常を検知 |
| **Agent Simulation** | 合成マルチステップ対話を数千件生成して、ロジックと会話フローをストレステスト |
| **Agent Observability** | OpenTelemetry 準拠テレメトリ、実行パスの完全可視化、推論ループ診断 |
| **Agent Optimizer** | プロンプト / モデル / ツール選択の継続最適化 |

この Optimize 層の新設は 2 つの意味で重要です。

**1 つ目は、本番運用中のエージェントを計測する面が整ったこと**。これまで LangSmith / LangFuse などの外部ツールに頼っていた領域を、Google Cloud が公式でサポートをすることになりました。

**2 つ目が本命**で、Scale 層が**本番運用向けの強化に振り切った**こととの **対応構造**です。

* Scale 層の強化 ＝ **実験から本番へ**（サブ秒コールドスタート、隔離サンドボックス、**Memory Bank**（エージェントがセッションをまたいでユーザー情報を記憶する仕組み）による永続コンテキスト）
* Optimize 層新設 ＝ **本番から最適化へ**（本番トラフィックで評価 → 継続的に改善）

つまり今回の Gemini Enterprise Agent Platform アップデートは、AI エージェントを本番まで稼働させるための **オールインワンキット** が、ついに Google から揃って出てきた、と読むのが一番しっくりくるわけです。

これまで Gemini Enterprise で本番エージェントを組むには、Vertex AI で提供されている機能を組み合わせ、足りない部分はスクラッチで作る必要がありました。Scale（サブ秒コールドスタート・Memory Bank）・Govern（ガバナンス 4 点セット）・Optimize（Evaluation / Simulation / Observability / Optimizer）の各層は、LangSmith / LangFuse / Weights & Biases などのサードパーティを繋いだり独自実装で埋めたりする領域だったわけです。**それを Google 自身が埋めに来た**——ここに今回の Gemini Enterprise Agent Platform の革新性があります。

「PoC（Build）→ 本番（Scale）→ 統治（Govern）→ 最適化（Optimize）」の 4 ステージが、Google 公式のプロダクト群で **垂直統合** された、と整理するのが一番素直な読み方です。冒頭で Kurian 氏が語った「チップ→モデル→データ→エージェント→インフラの一貫したアーキテクチャ」と同じ設計思想が、**AI エージェント基盤の文脈でも徹底された** 形になっています。サードパーティを束ねる以上の意味——**Google Cloudの製品だけで AI エージェントを構築から本番運用、継続的な改善までできる**——が、この垂直統合の本質だと理解しています。

実際に本番で動いている事例も会場で紹介されました。**Honeywell は Gemini を使ってデジタルツインを運用し、100 万超の製品アソシエーションから建物管理を自動化**していると語られました。Optimize 層の新設と Scale 層の本番運用向け強化が、こうした規模の本番案件を支える基盤になることになるでしょう。

Govern と Optimize は、**抵抗突破と成熟度の両輪**です。Govern 層で新設された機能群が「エージェント導入時の抵抗」を下げ、Optimize 層の新設が「導入後の説明責任」を支える——この両輪がないと、去年までの「PoC で止まる」状態は突破できません。

## 転換点 3: データ層の 2 本柱——Knowledge Catalog と Cross-Cloud Lakehouse

3 つ目はデータ基盤です。Karthik Narain 氏(Chief Product Officer, Google Cloud)は、このパートの冒頭で鋭い一言を置きました。

> "Reasoning without context is just a guess."  
> （コンテキストなしの推論は、ただの推測にすぎない）

この一言が、今回 Data Cloud 層で発表された内容全ての設計思想を圧縮しています。エージェント時代のデータ基盤は **2 つの軸**で再設計されました——**データに意味（コンテキスト）を与える層**と、**データを場所に縛らない層**。前者が Knowledge Catalog、後者が Cross-Cloud Lakehouse です（Data Cloud 層全体の公式解説は [What's new in the Agentic Data Cloud: Powering the System of Action](https://cloud.google.com/blog/products/data-analytics/whats-new-in-the-agentic-data-cloud?hl=en) を参照）。

### Knowledge Catalog——データに「意味」を与える層

**Knowledge Catalog** は、エンタープライズ全体の「統合された動的コンテキストグラフ」を構築する、エージェント向けのユニバーサルコンテキストエンジンです。従来のデータカタログが「どこに何があるか」のインデックスだとすれば、Knowledge Catalog は \*\*「それぞれのデータが何を意味していて、互いにどう関係しているか」\*\*をマッピングする層——データに意味を与える層です。

この層は 2 つの構成要素で動きます。

* **Smart Storage**: Google Cloud Storage に到着した PDF・画像などの非構造化ファイルを、エージェントが触れる前に Gemini が即座にタグ付けしメタデータを付加する
* **Knowledge Engine**: エンタープライズ全体の複雑な関係を、Gemini が自律的にタグ付け・ロジック定義・マッピングし、エージェントに欠けていた「セマンティック定義」を提供する

ステージでは Yasmin Amal 氏が Midnight Squirrel Froyo という架空のバイラル流行を題材にしたデモを見せました。新フレーバーの安全性を 5 分以内に判断するシナリオで、Knowledge Catalog が **2 つの別 PDF に分散していた "Base 204 成分 → soy アレルゲン" という間接的な連鎖**を即座に発見する、という場面が核心でした。人間のアナリストならスプレッドシートを何時間も往復して気づく関係を、エージェントが一瞬で辿る——Knowledge Catalog の「意味付け」が効いた瞬間です。

Knowledge Catalog は従来 Dataplex として提供されていた製品の進化形で、BigQuery Graph と measure レイヤーの**上位ホライゾンタルレイヤー**として位置づけられます。

### Cross-Cloud Lakehouse——データの「住所」を動かさない層

Knowledge Catalog が「データの意味」を解く一方、**Cross-Cloud Lakehouse** は「データの場所」の制約を解きます。Karthik 氏はステージでこう宣言しました。

> "Where should your data reside? The reality is it lives everywhere — at Google, AWS, Azure, and across your SaaS applications. ... Today, we are introducing the cross-cloud lakehouse where your analytical engine reasons over data in any cloud. ... No more moving data, no more vendor lock-in, just freedom."  
> （データはどこに置くべきか？ 現実は、Google、AWS、Azure、そして SaaS アプリケーションの至るところに分散しています。……本日、クロスクラウド・レイクハウスを発表します。分析エンジンがどのクラウドのデータでも推論できます。……もうデータの移動もベンダーロックインもない、ただ自由があるだけです）

Narain 氏が説明した Cross-Cloud Lakehouse の構成要素は次の 4 つです。

* **Apache Iceberg の標準化**（Databricks / Palantir / Salesforce Data360 / SAP / ServiceNow / Snowflake / Workday などへのゼロコピーアクセス）
* **Borderless なデータアクセス**（データは元のクラウドに残したまま、分析エンジンがどのクラウドのデータに対しても推論できる）
* **AWS / Azure への低レイテンシ直接接続**（"as if the data sat natively in Google Cloud" — あたかもデータが Google Cloud にネイティブに存在するかのような応答性を実現）
* **複雑なネットワーキングと大量の egress 料金の排除**（従来のマルチクラウド移動で発生していた摩擦とコストをまとめて除去）

これまでの「マルチクラウド戦略」は、**同じデータを両方のクラウドに置く**か、**データを片方に寄せる**かのどちらかでした。どちらも移動コストと整合性の問題を抱えます。Google が今回提示したのは 3 つ目の道で、**データの住所は元のまま、読み手だけが跨ぐ**モデルです。  
![Cross-Cloud Lakehouse の基本アイデア](https://static.zenn.studio/user-upload/a035eed45b5a-20260424.png)  
*図: 従来のマルチクラウドはコピー／レプリケーションで整合性の問題を抱えていた。Cross-Cloud Lakehouse ではデータは S3 に残したまま、BigQuery エンジンが低レイテンシ直接接続で跨いで読む(筆者作成)*

国内エンタープライズの現場感で言えば、これまで「AWS S3 に基幹データの 10 年分が積み上がっているから、GCP には簡単に移れない」と悩んでいた企業にとっては救世主のような発表です。**データは S3 に置いたままで良い、BigQuery の性能と AI を持ってくる**——この発想が成立します。Data Platform の PoC 設計、Landing Zone 設計、そして何より **エンタープライズアーキテクチャの前提** が変わる発表だと考えています。

そして Knowledge Catalog が「このデータが何を意味するか」を、Cross-Cloud Lakehouse が「このデータにどうアクセスするか」をそれぞれ解きます。**意味と場所が同じ Data Cloud 層で同時に解ける**——これが今年の Data Cloud 発表の本質だと考えています。

## 転換点 4: TPU 8t / 8i の分岐 ——「汎用」から「ワークロード最適化」へ

4 つ目はインフラ最下層です。 **Amin Vahdat**（SVP and Chief Technologist, AI and Infrastructure）は、このパートの冒頭でこう宣言しました。

> "In the agentic era, compute is no longer defined by a chip. Compute is the entire data center."  
> （エージェンティック時代において、コンピュートはもはやチップでは定義されない。コンピュートはデータセンター全体だ）

そして、この思想が最も具体的に出たのが **第 8 世代 TPU の完全分離** です。

> "For the very first time, we are launching two specialized platforms, each built from the ground up for the distinct demands of training and service."  
> （史上初めて、トレーニングとサービス（推論）という別々の要求に対して、それぞれゼロから作り上げた 2 つの専用プラットフォームを発表する）

第 8 世代 TPU は、**学習用の TPU 8t と、推論用の TPU 8i に完全分離**されました。

細かいスペックは公式ブログ [TPU 8t and TPU 8i: A Technical Deep Dive](https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive?hl=en) に譲るとして、押さえておきたいのは次の 3 点です。

* **学習用 TPU 8t は Ironwood 比 3 倍の処理性能**。単一 pod で最大規模のフロンティアモデル学習に振り切った設計
* **推論用 TPU 8i は Ironwood 比 9.8 倍、$/推論性能が前世代比 80% 向上**。数百万の同時エージェントをコスト効率で動かすことに振り切った設計
* **設計分岐の方向性が真逆**。学習は大容量共有メモリを優先、推論は低レイテンシ（KV キャッシュをオンシリコン完結）を優先

数値のインパクトは十分ですが、**本当に読むべきは「分岐したこと自体」** だと私は考えています。

学習と推論は、これまで「同じ TPU で両方動かす」モデルでした。Ironwood までは、1 つのチップ設計で両方のワークロードをカバーする汎用性が売りでした。**今回、Google は、この汎用性ではなく用途に応じて最適化する方向へ舵を切ったのだと理解しています**。学習用と推論用でそれぞれ別チップを設計し、それぞれの要求（学習は大容量メモリ、推論は低レイテンシ）に合わせて最適化する——**汎用で全てを賄う設計から、ワークロードごとに最適化された個別設計を高速ネットワークで束ねる設計へ**。2026 年の Google のハードウェア哲学はここで大きく舵を切ったと理解しています。

あわせて、**Axion N4A**（ARM カスタム CPU、x86 比で価格性能 **2 倍**）、**NVIDIA Vera Rubin NVL72** の最速提供、**Managed Lustre の 10 TB/s スループット**、そして **Virgo Network**（134,000 チップをノンブロッキングで束ねる新ネットワーク層）も発表されました。冒頭の Vahdat 氏の言葉どおり、**ワークロードごとに最適化された部品を、高速ネットワークで貼り合わせる**——これが AI Hypercomputer の今のかたちです（AI Hypercomputer 層全体の公式解説は [AI Infrastructure at Next '26](https://cloud.google.com/blog/products/compute/ai-infrastructure-at-next26?hl=en) を参照）。

## YouTube TV の音声エージェントデモ——CX Agent Studio

![CX Agent Studio の Preview agent 画面](https://static.zenn.studio/user-upload/83939484c67b-20260424.png)  
*写真: Patrick Marlow 氏が見せた CX Agent Studio の裏側——YouTube TV の本番エージェントの各実行ステップ（AI reasoning、Pricefinder ツール呼び出し、Technical Support エージェントへの転送）と処理時間がトレースされ、built-in test interface で回答のグラウンディングを検証している（youtubeより）*

例年Google Cloud Nextのステージ上では、その年に発表された先進的なGoogle Cloudのプロダクトを使ったデモが行われます。今年もPatrick Marlow（Google Cloud シニアプロダクトマネージャー）が、NFL Sunday Ticket のサポート番号に電話をかけるところからデモが始まりました。

「NFL Draft が明日なんだけど、スポーツだけ見たいプランある？」と英語で尋ねると、AIエージェントは **"The YouTube TV sports plan has exactly what you're looking for, plus over 30 other sports channels. It's $18 less per month than the base plan."**（YouTube TV のスポーツプランがまさにお探しのもの、加えて他 30 以上のスポーツチャンネル付き、ベースプランより月 18 ドル安い）と応答し、SMS でプラン比較リンクを送ります。ここまではよくある音声エージェントのデモです。

流れが変わるのは次の瞬間でした。Marlow 氏が「隣に義父がいるから、このプランをスペイン語で要約してくれる？ football y fútbol（アメフトとサッカー）両方見たいらしい」と切り出すと、**同じエージェントが同じ会話文脈を保ったままスペイン語で要約**を返しました。

> "Claro, tendrás tanto fútbol como fútbol. El Juan tiene lo que buscas, más canales deportivos y te ahorras 18 dólares al mes."  
> （もちろん、アメフトもサッカーも両方見られます。このプランにお探しのものが揃っていて、さらにスポーツチャンネル多数、月 18 ドルお得です）

セッション状態・ユーザー履歴・価格ロジックを保ちながら、言語だけが英語↔スペイン語でシームレスに切り替わる。**会場全体がざわっと反応したのはこの瞬間でした**。

このデモで効いている技術は 3 つあります。

* **Human-Like Voice**（低レイテンシの音声ストリームイン / ストリームアウト、多言語切替）
* **Universal Consumer Context**（チャンネル・セッションをまたいだ状態保持）
* **Omnichannel Gateway**（Web / Mobile / Voice / WhatsApp / SMS / RCS の単一エントリーポイント）

これらが **別々のプロダクトとして並列にある** のではなく、**CX Agent Studio**（CX 向けのエージェント構築 IDE）**上で 1 つのエージェントの挙動として統合されている**ことが、デモのインパクトを際立たせていました。

そして Marlow 氏は淡々と数字を出します——**6 週間で構築、YouTube TV ユーザーの 100% に本番提供中**。**すでにプロダクションレベルで動いており、しかもこれが 6 週間で作成されたという驚異的なデモ**となりました。

## ウィンタースポーツ AI デモ

![Shaun White の 3D ポーズ推定 × ダイナミクス解析](https://static.zenn.studio/user-upload/0efcc6b16583-20260424.jpg)  
*写真: 実映像に DeepMind の 3D ポーズモデル（黒いワイヤーフレーム）が重ねられ、Gemini が抽出した回転速度・軸角度・滞空時間などがリアルタイムで右パネルに表示されている（現地撮影）*

**Shaun White（冬季五輪スノーボード金メダル 3 回受賞）と Jason Davenport（Technical Lead, Google Cloud）が、2017 Burton US Open で White 氏が決めた大技 "Switch Cab Double Flip 1440"（4 回転 + 2 回の斜め軸回転）を解析するデモ**です。（正直に白状すると、当日の私はここで技の名前を聞いても何を言っているのか全くわかりませんでした笑。ちなみにステージの Davenport 氏自身も技名を聞いた直後に **"That is insane. For everyone else, what does that actually mean?"** と White 氏に聞き返していたので、分からなかったのは私だけじゃなかったはずです）

3 秒弱で決まるこのトリックに、Google DeepMind の 3D ポーズ推定モデルが空間的にオーバーレイし、Gemini がフライトダイナミクスの解析結果をリアルタイムで抽出し、リボン状のグラフィックスで回転軸を可視化するデモでした。

ステージ上で White 氏自身が語った言葉が、このデモの意味を端的に言っています。

> "Back when I was training, our tools were camcorders and basically guesswork. You'd land a trick and watch it back. ... Now Google Cloud is bringing AI to the mountain."  
> （僕がトレーニングしていた頃、ツールはビデオカメラと当てずっぽうだった。技を決めたら録画を見返して「どうすればもっと良くなるか」と考える。……今、Google Cloud が AI をゲレンデに持ち込んでくれている）

そしてデモを終えた White 氏は、この技術が何を変えるのかを、自分の言葉で 2 つの角度から総括しました。

> "Learning a trick on the mountain is one thing, but actually understanding the physics of a trick is a whole other thing."  
> （技をゲレンデで覚えるのと、その技の物理を実際に理解するのは、まったく別の話だ）

> "This is really going to help not only the next generation of athletes learn new skills, but also help the fans at home understand the sport better. And not just for snowboarding, but I think sports globally."  
> （これは次世代のアスリートが新しいスキルを学ぶ助けになるだけでなく、家で観ているファンがスポーツをより深く理解できるようになる。しかもスノーボードだけじゃなく、スポーツ全般にも言えると思う）

**IT エンジニアではないプロアスリート本人がAIの未来を語る**——これこそが、このデモが仕掛けていたメッセージの核でした。AI は「その技が決まる」から「なぜ決まるかを科学的に理解できる」へとアスリートの認知を変え、その視線をファンと共有させる。White 氏自身が「スノーボードだけじゃなく、スポーツ全般にも言えると思う」と締めたように、アスリート支援で磨かれた空間理解モデルはスポーツ全般に波及させたい——このデモは、その ビジョンの予告として位置づけられていたのだと私は受け取りました。

## Workspace アプリを統合するレイヤー——Workspace Intelligence

キーノート終盤、Yulie Kwon Kim（VP of Product, Google Workspace, Google Cloud）が登壇し、こう切り出しました。

> "We've all been there. You're trying to answer one simple question, and 10 minutes later, you have 15 tabs open."  
> （みんな経験があるはずです。一つの問いに答えようとして、10 分後には 15 のタブが開いている）

誰もが経験する日常を、Kim 氏は **Workspace Intelligence** で解決すると宣言しました。

> "Think of it as a unified intelligence layer that lives inside every workspace app."  
> （全ての Workspace アプリの内側に宿る、統合されたインテリジェンスレイヤーだと考えてほしい）

個別アプリに AI 機能を足す発想ではなく、**全アプリを横串で理解するセマンティック統合レイヤー**を Workspace 全体の下に敷く——この設計思想が Workspace Intelligence の核です（公式解説は [Introducing Workspace Intelligence](https://workspace.google.com/blog/product-announcements/introducing-workspace-intelligence?hl=en) を参照）。

この設計思想を具体化したエントリーポイントが、Google Chat 上で動く **Ask Gemini** です。Chat ウィンドウから離れずに **Workspace 全体の情報（メール・Chat・Drive・Docs など）を横断的に統合**し、インサイトを浮かび上がらせ、プロジェクトに関するクエリにその場で答え、**カレンダーでの会議予約や会議前ブリーフ用 Google Doc の自動生成**まで、Chat 内で完結させられる——Kim 氏の言葉を借りれば「タブを切り替えることなく、会話をそのままアクションに変換する」ためのフロントドアです。

ステージデモで示された Ask Gemini の画面がこちらです。  
![Ask Gemini が今日やるべきタスクを処理](https://static.zenn.studio/user-upload/b406083f81e3-20260424.jpg)  
*写真: Ask Gemini が **Awaiting your action**（要アクション）と **Close the loop**（完結させる）の 2 層でタスクリストを整理し、メール・Chat・ドキュメント **7 ソース横断**で生成された優先タスクを提示している（現地撮影）*

続いて「先四半期のグレイチャートどこだっけ？」と問うと、キーワード一致ではなく**会議の文脈と文書内容を理解して**正しいドキュメントを 1 秒で返す。さらに **"Use the HTML Campaign skill to create a deck with a plan for organic living"**（HTML Campaign スキルで、オーガニックな暮らしのプラン用デッキを作って）と指示すると、Workspace Intelligence がメール・チャット・セールスデータを横断参照し、ブランドガイドラインに準拠した Google スライドを生成、**どのメールとチャットから引いたかの citations まで自動表示**しました。Kim 氏は締めに一言こう置きました。

> "Go ahead, close those 15 tabs. Workspace Intelligence is now ready to do the heavy lifting for you."  
> （さあ、15 のタブを閉じてください。Workspace Intelligence があなたの代わりに面倒な仕事を引き受けます）

会場では、適用規模の大きさを示す事例として **Colgate-Palmolive が 34,000 人の全社員に Workspace Intelligence を展開し、数十年分のセールス履歴からアクション可能なインサイトを引き出す運用に入っている**、という紹介もありました。

この発表は、競合が「個別アプリに AI を後乗せする」戦略であるのに対し、Google は **Workspace を AI 前提で再設計**し、アプリごとの境界をセマンティックレイヤーで溶かす方向に進めていくという表明と捉えています。5 層スタックの最上層（業務適用層）で、Agent Platform で作った組織内エージェントと、Workspace Intelligence の横断セマンティック統合が**同じコンテキストで接続**される——これが今年の Workspace 戦略の核となってくるようです。

なお、キーノートのステージでは Ask Gemini のデモ 1 本に絞られていましたが、**Workspace Intelligence は 以下のように5 つの領域にわたって組み込まれる**ことが Welcome Blog に明記されており、同イベントの**ブレイクアウトセッションでも詳しく説明されていました**。

* **Gmail AI Inbox / AI Overviews**: Gemini が積極的な受信トレイアシスタントとして機能
* **Google Chat "Ask Gemini"**（今回のデモで実演）: Chat から Workspace 全体の情報を統合し、会議予約・会議前ブリーフ作成まで即実行
* **Docs / Sheets / Slides のコンテンツ作成再構築**: Drive・Gmail・Web 情報を横断統合し、ユーザーの声を模倣した初稿・インタラクティブダッシュボード・ブランド準拠のプレゼンを単一プロンプトで生成
* **Google Drive Projects**: ファイルとメールを整理するインテリジェントな新スペース。Drive をストレージからアクティブなコラボレーターへ
* **Gemini Enterprise の Workspace エージェント**: Gemini Enterprise を離れずに Workspace アプリ全体でマルチステップタスクを実行

さらに **Rapid Enterprise Migration** も同時発表され、Microsoft 365 から Google Workspace への組織移行が **最大 5 倍速** になる、という方針が示されました。

## まとめ —— Google Cloud Next '26 Opening Keynote の要点

発表内容を 5 層スタックと 4 つの転換点で追ってきました。最後に、キーノートの芯を箇条書きで圧縮しておきます。

* **AI エージェントはパイロットを終え、本番運用の時代に入った**（Kurian 氏 "You have moved beyond the pilot."、Pichai 氏 "How do we manage thousands of them?"）
* **Agent Platform は Vertex AI のリブランド**であり、「モデル中心の IDE」から「エージェント中心のプラットフォーム」への主戦場移行を意味する
* **Agent ガバナンス 4 点セット**（Identity / Registry / Gateway / Anomaly Detection）で、エージェントを本番運用可能な資産に変える土台が揃った
* **Optimize 層の新設**により、PoC（Build）→ 本番（Scale）→ 統治（Govern）→ 最適化（Optimize）の 4 ステージが初めて揃った
* **Knowledge Catalog** と **Cross-Cloud Lakehouse × Apache Iceberg** の 2 本柱で、データ層に「意味」と「場所」の自由度が同時に解ける基盤が揃った
* **TPU 8t / 8i の完全分離**により、学習と推論を別チップで最適化する時代に入った
* **Workspace Intelligence** がアプリ横断のセマンティック統合レイヤーを敷き、Agent Platform と同じコンテキストで接続される
