---
id: "2026-06-03-snowflake-summit-2026open-data-infrastructureai-ag-01"
title: "【Snowflake Summit 2026】Open Data Infrastructure：AI Agentを支えるデータ戦略と新機能"
url: "https://zenn.dev/finatext/articles/b7f92664bd18d2"
source: "zenn"
category: "construction"
tags: ["MCP", "AI-agent", "OpenAI", "Gemini", "zenn"]
date_published: "2026-06-03"
date_collected: "2026-06-04"
summary_by: "auto-rss"
query: ""
---

※ 本記事は Snowflake Summit 2026 のセッション「Open Data Infrastructure: The Next Era of Data Architecture」(DE104) を現地で聴講したメモを元にした参加レポートです。スライドの図と、登壇内容の要約を再構成しています。

## セッション概要

**タイトル:** Open Data Infrastructure: The Next Era of Data Architecture  
**セッションコード:** DE104  
**登壇:** Fivetran + dbt Labs

Fivetranとdbt Labsが共同で提唱する「Open Data Infrastructure」のデータ戦略と、それを実現する3つの新機能（dbt State、dbt Wizard、Agents Schema）が発表されました。

## はじめに

こんにちは。Nowcastのmariです。

本記事では、Snowflake Summit 2026のセッション「Open Data Infrastructure: The Next Era of Data Architecture」で発表された内容をお伝えします。

セッションでは、データ連携ツールのFivetranと、データ変換ツールのdbt Labsが共同で「Open Data Infrastructure（オープンデータインフラストラクチャ）」というデータ戦略を提唱し、それを実現する3つの新機能を発表しました：

* **dbt State：** データ処理コストを30%以上削減する機能
* **dbt Wizard：** AI Agentにデータの「文脈」を自動提供する機能
* **Agents Schema：** 組織全体でデータの意味を統一する機能

本記事では、AI Agent時代に求められるデータ基盤のあり方として提唱された「Open Data Infrastructure」の考え方と、それを実現するために発表された3つの新機能について紹介します。

## なぜOpen Data Infrastructureが必要なのか

### AI時代のデータインフラへの課題

![AI Is Raising The Stakes](https://static.zenn.studio/user-upload/7ffa608ac5ec-20260603.jpg)

セッションでは、AIが業界全体の重要性を高めていることが、3つの統計データで示されていました：

* **77%** のデータリーダーが、生産性向上のためにAIを重視している
* **71%** が、ハルシネーションや不正確なデータについて懸念している
* **57%** が、データウェアハウスとコンピュートの支出増加を報告している

このようにAI活用への期待が高まる一方で、コストや品質への懸念も大きくなっています。その背景にあるのが、データ利用者の根本的な変化です。

![Your data stack was built for humans, but agents are the new primary data consumers](https://static.zenn.studio/user-upload/cc02968f8621-20260603.jpg)

セッションでは、データの主要なコンシューマーが「人間のアナリスト」から「AI Agent」へと移行しつつあることが、最も重要な変化として挙げられました。従来のModern Data Stack（MDS）は人間向けに最適化されていましたが、今後はAI Agentがデータを直接消費し、意思決定や業務実行を行う時代になります。

### AI Agent時代のデータインフラに求められる3つの要件

![Do you trust your data infrastructure to power agents?](https://static.zenn.studio/user-upload/813968dc6ffe-20260603.jpg)

AI Agentをデータコンシューマーとして想定する場合、データインフラに求められる要件は以下の3つです：

1. **AI Agentのコストを効率的に管理できるか？** - コンピュート、トークン、運用コストが急増する可能性
2. **データは適切に管理され、正確で、追跡可能か？** - AI Agentの回答品質は、提供されるデータの品質に完全に依存
3. **標準的な技術で構築され、他のシステムでも使えるか？** - 特定のサービスに依存しない柔軟性

こうした課題と要件に対応するために、FivetranとdbtLabsが共同で提唱したのが「Open Data Infrastructure」です。

## Open Data Infrastructureのアーキテクチャと3つの新機能

![Agents need a trusted data infrastructure](https://static.zenn.studio/user-upload/17502f428cb5-20260603.jpg)

Fivetranとdbt Labsが提唱する「Open Data Infrastructure」は、AI Agentに必要なデータインフラを実現するための包括的なデータ戦略です。その戦略は3つの柱で構成されています。

### データ戦略の3つの柱

1. **信頼性が高く、適切に管理され、AI Agentに対応したデータ** - 生データから信頼できるAI Agent対応データへの高速な移行
2. **柔軟で、すべてのインフラで利用可能なデータ** - すべてのクラウド、エンジニア、モデル、ツールで一貫した定義、リネージ、ビジネスロジック
3. **拡張可能で最適化されたデータ基盤** - AIワークロードが効率的にスケールし、暴走するコストを回避

### アーキテクチャ全体像

![Fivetran + dbt Labs trusted infrastructure](https://static.zenn.studio/user-upload/2025782f39e1-20260603.jpg)

Fivetranとdbt Labsが共同で提供するOpen Data Infrastructureは、以下のレイヤーで構成されています：

**最上位レイヤー: Intelligence、Operations、Applications**

* AI Agents、AI、Analytics & Operationsが利用

**Any model & Any compute**

* 任意のAIモデル（OpenAI、Anthropic、Geminiなど）
* 任意のコンピュートエンジン（Snowflake、Databricks、BigQueryなど）

**Governed context**

* Lineage
* Semantic layer
* Metadata

**Management**

* Orchestration
* Observability
* Security

**Pipelines**

* Ingestion
* Transformations
* Activation（データ活用）

**Fivetran Managed Data Lake service**

* Open format（Delta Lake、Iceberg）
* Catalogs（複数のカタログサービスに対応）

このアーキテクチャの特徴は、各レイヤーでオープンスタンダードとリファレンス実装が明示されていることです。これにより、ベンダーロックインを避け、将来の技術変化に柔軟に対応できる設計になっています。

### データ提供戦略：共有コンテキストとパーソナルコンテキスト

![Shared context vs. personal context](https://static.zenn.studio/user-upload/653a25c101c1-20260603.jpg)

データソースは、「共有コンテキスト」と「パーソナルコンテキスト」の2つに分類されます。

**共有コンテキスト（Shared context）**

* Salesforce、Zendesk、Postgresなど組織全体で使うデータ
* データの整理・加工が重要で、データプラットフォーム経由で提供すべき

**パーソナルコンテキスト（Personal context）**

* GDrive、Gmailなど個人ごとに異なるデータ
* 個別のアクセス権限が重要で、MCPやフェデレーション（直接接続）で提供が適している

業務システムデータ（Salesforceなど）は複雑なスキーマ構造で、そのまま使えません。dbtなどでビジネスロジックを適用し、AI Agentが直接使える形に整理することが重要です。

### 新機能の発表

![Innovating together for the agentic era](https://static.zenn.studio/user-upload/f1138198a9f5-20260603.jpg)

ここまで見てきた「Open Data Infrastructure」のデータ戦略を具体的に実現するため、Agentic時代に向けてFivetranとdbtが共同で開発した3つの新機能が発表されました。

セッションでは、これらの新機能が前述のデータ戦略の3つの柱に対応するものとして紹介されていました：

* **dbt State** → 拡張可能で最適化された基盤（コスト削減）
* **dbt Wizard** → 信頼性が高く、適切に管理されたデータ（文脈提供）
* **Agents Schema** → 柔軟で、すべてのインフラで利用可能なデータ（標準技術）

#### 1. dbt State：データ処理コストを30%以上削減

![dbt State の仕組み](https://static.zenn.studio/user-upload/c9ac24ed6510-20260603.jpg)

dbt Stateは、「変更があったデータだけを処理する」機能です。従来は、データパイプライン全体を毎回最初から実行する必要がありましたが、dbt Stateを使うと、実際に変更があった部分だけを自動検知して処理します。

セッションでは、平均30%以上のコンピュートコスト削減が可能と紹介されていました。AI Agentが大量のクエリを実行する環境では、このコスト削減効果がさらに大きくなります。コストを気にせず頻繁にデータを更新できるため、より新鮮なデータでビジネス判断ができます。

#### 2. dbt Wizard：AI Agentにデータの「文脈」を提供

dbt Wizardは、AI Agentがデータを正しく理解して使えるように、データの「文脈情報」を自動的に提供する機能です。

* **データの系譜（リネージ）：** このデータがどこから来て、どう加工されたか
* **テスト結果：** このデータの品質は保証されているか
* **メトリックの定義：** 「売上」や「顧客数」などのビジネス用語が、データ上ではどう定義されているか

これにより、AI Agentは「売上」の定義（どのテーブルのどのカラムを、どう計算するか）を自動的に理解し、より正確な分析結果を返せるようになります。

#### 3. Agents Schema：組織全体でデータの意味を統一

Agents Schemaは、組織内のすべてのAI Agent、アプリケーション、ワークフローが、同じ「データの辞書」を参照できる機能です。データウェアハウス内に「共通のビジネス用語集」を作り、全社で統一的にデータを使えるようにします。

これにより、「売上」の定義が部門ごとに異なるといった問題を防ぎ、新しいAI Agentを導入する際もデータの意味を毎回教える必要がなくなります。オープンソースとして提供されるため、特定のベンダーに依存せず、自社の環境に合わせてカスタマイズできます。

---

これら3つの機能は相互に補完し合う関係にあり、AI Agentが「正確に」「効率的に」「信頼できる形で」データを活用できる基盤が整います。

## ケーススタディ：Open Data Infrastructureの実践事例

### Fivetran社内での活用例

![Fivetran Chat](https://static.zenn.studio/user-upload/8f1cf80d11e1-20260603.jpg)

Fivetran社内では、「Fivetran Chat」という社内向けAI Agentが構築されています。構造化データと非構造化データを横断して分析し、データチームを介さず数分で回答を得られることが示されました。

デモでは「Why are customers using data lakes?（顧客はなぜデータレイクを使っているのか？）」という質問に対して、AI Agentが顧客リストの抽出、顧客タイプ別の分析、さらに通話記録を読み込んで「理由」を分析していました。従来は「データチームに依頼して数日後に回答をもらう」という流れでしたが、Fivetran Chatを使うことで、**質問から回答までが数分で完結**し、会話のコンテキストを維持したまま追加の深掘り質問も可能になっています。

### 他社の成果事例

![](https://static.zenn.studio/user-upload/1c7005d66d4f-20260603.jpg)

セッションの最後に、コンテキストリッチなデータ基盤による実例が紹介されました：

* **ramp：** 50%以上のマージされたPRが、コンテキストリッチなコーディングAI Agentによって駆動
* **OpenAI：** テーブルレベルの知識と製品・組織のコンテキストを使用して、影響の大きなデータ質問に**数日ではなく数分で回答**
* **INFINITE LAMBDA：** 構造化されたビジネスコンテキストを使用して、**18ヶ月を数週間に圧縮**

これらの事例は、データインフラに適切なコンテキスト（リネージ、セマンティック定義、ビジネスロジック）を組み込むことで、AI Agentのパフォーマンスが飛躍的に向上することを示しています。

## まとめと感想

今回のセッションで興味深かったのは、新機能そのものよりも「AI Agentを前提にデータ基盤を再設計する」という問題提起でした。

これまでのデータ基盤は、人間のアナリストやBI利用者が最終的な利用者でした。そのため、多少データモデルが複雑でも、ドキュメントを読んだり担当者に確認したりしながら解釈することができました。

一方でAI Agentは、人間のように暗黙知を補完できません。「売上とは何か」「顧客数はどう定義されるのか」「このテーブルは信頼してよいのか」といった情報を機械的に参照できなければ、期待した回答品質は得られません。

その意味で今回発表された dbt Wizard や Agents Schema は、単なる新機能というより、これまで人間同士のコミュニケーションで補っていたコンテキストをデータ基盤側に埋め込むための仕組みとして位置付けられているように感じました。

また、従来のModern Data Stackが「データを集めて活用するための基盤」だったとすれば、Open Data Infrastructureは「AI Agentが安全かつ継続的に利用できる基盤」を目指しているように見えます。利用者が人間からAI Agentへ広がることで、データ品質や定義管理、リネージといった従来から重要だった要素が、さらに基盤の中心へ移動している印象を受けました。

Open Data Infrastructureは、AI Agentを主要なデータ利用者とみなし、データそのものだけでなく意味や文脈も管理対象に含めるアーキテクチャとして提案されていました。発表されたdbt State、dbt Wizard、Agents Schemaはいずれもその実現に向けた取り組みであり、今後のデータ基盤設計の方向性を示す内容だったと感じました。

Nowcastでも、業務システムのデータをdbtでモデリングし、共通定義を整備しながら活用しています。今回の発表を聞いて、AI Agent活用が進むほど「どのデータを持っているか」以上に、「そのデータの意味や定義をどこまで機械が理解できる形で管理できているか」が重要になると改めて感じました。

---

本記事はセッション聴講メモを元にした個人の参加レポートです。スライドの画像や引用は聴講時のメモに基づくため、正確性は公開資料をご確認ください。
