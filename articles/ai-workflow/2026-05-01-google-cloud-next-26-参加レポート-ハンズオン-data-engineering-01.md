---
id: "2026-05-01-google-cloud-next-26-参加レポート-ハンズオン-data-engineering-01"
title: "Google Cloud Next '26 参加レポート & ハンズオン: Data Engineering AgentをA2Aで試してみた"
url: "https://zenn.dev/dmmdata/articles/71246621d69dec"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "Gemini", "zenn"]
date_published: "2026-05-01"
date_collected: "2026-05-02"
summary_by: "auto-rss"
query: ""
---

# はじめに

合同会社DMM.comでデータエンジニアをしている潮平です。  
4/22から3日間に渡り開催されたGoogle Cloud Next '26に参加してきました。本イベントには今回が初参加かつ初の海外渡航でしたが、非常に学びも多く良いモチベーションになったので記事にして残しておこうと思います。

この記事では、私が実際に参加した中で特に興味深かったセッションの内容をかいつまんで紹介し、次にセッションの中でGAが発表された新機能をハンズオンで確認してみようと思います。

## 想定読者

データエンジニア、 Data Engineering Agentの実際が気になっている人

# 注目したセッション

ハンズオンだけ見たい方は飛ばしていただいてOKです。

## Agent context engineering for production

### 概要

本番環境でエージェントをスケールさせるために重要なコンテキストエンジニアリングについての解説に始まり、そのためのテクニックとGoogle Cloudの製品を使ってどう実装するかの事例紹介をするセッションでした。ここでは、コンテキストエンジニアリングの内容を詳解することはしませんが、紹介されていたAT&Tの事例について軽く触れておきます。

### AT&T社の事例

AT＆T (通信キャリア事業) では日本でいうauやドコモのように、スマホや通信プランからブロードバンドまでさまざまな商品を販売しています。今回の事例ではこれらの販売業務をカバーするAIエージェントについてです。  
エージェントを実現するにあたり、顧客行動の複雑さが課題になりました。実際の顧客行動は一度商品を買って終わりというシンプルなものではありません。Webサイトで商品について調べたり、コールセンターやチャットボットで相談したり、実店舗で見積もりをもらったりと複数回のセッションにわたり、しかもチャネルを横断します。これをAIエージェントについて考えると**どうコンテキストを引き継ぐか**が課題だとわかります。

### アーキテクチャ

この課題のソリューションとして彼らは、マルチエージェント構成を採用しました。設計の特徴は、1.オーケストレーターが顧客の意図を判別し、適切な専門エージェントに振り分けを行うこと。2.エージェントのグループを論理層と表示層で分離し、チャンルに依存せず同じ文脈を共有できるようにしたこと。3.長期的なコンテキストを会話履歴から自動生成しSession間で引き継げるようにしたこと。の3つです。  
![](https://static.zenn.studio/user-upload/91589e2510ee-20260501.jpg)  
*長期記憶の抽出*

### 仕組み

Vertex AI Session Serviceで短期記憶 (Session単位) を、Memory Bankで長期記憶 (Session横断) を管理しています。  
<https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank>  
<https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sessions>

Memory Bankは会話記録から意味のある情報を自動で抽出し、開発者が指定したスキーマに従ってデータを保存・統合(Consolidation)します。注入する長期記憶(Memory BankのProfiles)は、毎回必ず渡すもの(Always-on)と必要になった時に渡すもの(Just-in-time)で分けて実装されています。  
![](https://static.zenn.studio/user-upload/9f27367a4b2c-20260501.jpg)  
*Memory Profiles*

## Supercharging unstructured data analytics with generative AI in BigQuery

冒頭で、Opening Keynoteでも発表があったKnowledge Catalog (旧Dataplex) の紹介がありました。元々のDataplexはデータ分析基盤におけるビジネスメタデータを供給するUniverseral Catalogや、データリネージ、データガバナンスを担うプロダクトでしたが今回の名称変更とともに役割が一変し、Google Cloud上のAIエージェント向けのグラウンディングやコンテキストを集約する層になるようです。  
<https://docs.cloud.google.com/dataplex/docs/ai-overview>

このセッションの主な内容は、BigQueryの[生成AI関数](https://docs.cloud.google.com/bigquery/docs/generative-ai-overview?hl=ja)を使って非構造データを扱う方法についてで、意味的な集計を可能にする`AI.AGG`や表形式データ向けゼロショット基盤モデル`TabularFM`が新機能としては印象的でした。さらに、既存のAI関数の**最適化モード**が発表され、これにより従来のアプローチと比較してトークン消費量が大幅に削減されるようです。  
![](https://static.zenn.studio/user-upload/3e4d6f38989c-20260502.jpg)  
*AI.AGG*

## Data Engineering Agent: Your partner for BigQuery and the open lakehouse

<https://docs.cloud.google.com/bigquery/docs/data-engineering-agent-pipelines>  
<https://docs.cloud.google.com/gemini/data-agents/data-engineering-agent/api-overview>  
<https://www.youtube.com/watch?v=6gbo-e8DzrI>  
本イベントのタイミングで、PreviewだったData Engineering AgentのGAが発表されました。前述Knowledge Catalogとの連携やプランニングモード、パイプラインの自動最適化、トラブルシューティングの強化などが追加されています。私が特に注目しているのは**A2A・API経由の操作が可能**になったことです。Preview版で課題だったTool連携・コンテキスト注入が可能となり、本番環境のパイプライン構築に利用する条件が整ったと感じました。

# 新機能のハンズオン

ハンズオンのコードとData Engineering Agentの成果物は[こちら](https://github.com/Uchior/dea-adk-context-engineering-demo)。

## 動機

紹介したセッションの中で扱われていた技術たちはどれも魅力的ですが、特に動かしてみたいのはData Engineering Agent (DEA) のA2A経由実行です。これを中心に、他のセッションで扱われていたサービスたちも盛り込みつつハンズオンを構成します。

## TL;DR

「GCSに置いたPDFから財務データを抽出・構造化・分析するBigQueryパイプラインを作って」——この一言から、エージェントが自律的にパイプラインを構築・デバッグ・完成させ、収益増加のキードライバー分析をするハンズオンを作りました。

## 何を作ったか

Alphabet（Google親会社）の決算PDF（Q1 2023, Q1 2024）をGCSに配置し、以下を自動化するマルチエージェントシステムを構築しました。

1. DEAがDataformパイプラインを自動生成（Bronze→Silver→Gold medallion architecture）
2. ADKエージェントがコンパイル・実行エラーを検知し、事実をDEAにフィードバック
3. DEAが自律的にデバッグ・修正
4. 分析結果をMemory Profilesに構造化記録し、セッション間で共有

## アーキテクチャ

```
ユーザー → [ADK orchestrator (Claude Opus 4.5)]
                    │
          ┌─────────┼──────────┐
          ▼         ▼          ▼
   [pipeline_agent] [analysis_agent] [memory_agent]
   DEA A2A通信       BQ結果確認       Memory Profiles
          │              │              │
          ▼              ▼              ▼
   DEA API           BigQuery       構造化プロファイル
   (パイプライン      (テーブル参照    (PipelineProfile,
    自動生成)          & 分析)         AnalysisProfile)
```

## エージェント構成

| エージェント | 役割 | ツール |
| --- | --- | --- |
| **orchestrator** | State-aware routing でサブエージェントに振り分け | transfer\_to\_agent |
| **pipeline\_agent** | DEAへの事実伝達、コンパイル/実行検証 | gather\_workspace\_context, send\_instruction\_to\_dea, compile\_dataform, get\_latest\_run, get\_run\_actions, read\_dataform\_file |
| **analysis\_agent** | BQテーブルの確認・分析 | list\_tables, preview\_table, run\_query |
| **memory\_agent** | 構造化プロファイルの参照・要約 | retrieve\_profiles |

## DEA連携: A2Aプロトコル

DEAとの通信はA2A（Agent-to-Agent）プロトコルで行います。

```
DEA_ENDPOINT = f"{DEA_HOST}/v1/a2a/{DEA_TENANT}/v1/message:stream"

# A2A拡張ヘッダー
A2A_EXTENSIONS = [
    "gcpresource/v1",        # Dataformワークスペースの指定
    "conversationtoken/v1",  # マルチターン会話の維持
    "messagelevel/v1",
    "finishreason/v1",
    "pipelinecontext/v1",
    "instruction/v1",
]
```

現状のDEAがどこまでできるのか見たかったため、pipeline\_agentはデバッグの方針判断をさせないようにしました。エラーメッセージ・ファイル内容・制約を事実としてDEAに渡し、修正プランニングはDEAに委ねます。

## デモ・動作確認

### パイプラインの作成

ADKのweb uiから以下の指示を行います。

```
## Prompt
GCSにあるAlphabet決算PDFを解析するパイプラインを作って
```

実際に作成されたものがこちら。それっぽいものができていそうです。全く指示していませんがメダリオンアーキテクチャっぽく作られています。  
![](https://static.zenn.studio/user-upload/9f46562e3448-20260502.png)  
*作成されたsqlx*

`ML.PROCESS_DOCUMENT`でPDFを読み取り、`ML.GENERATE_TEXT`で情報を抽出、最終的には、収益(revenue)増加の要因分析をAI.KEY\_DRIVERSで行っています。

```
1. 1_bronze_unstructured_reports  (オブジェクトテーブル作成)
2. 2_silver_parsed_reports        (Document AIでPDF解析処理)
3. 3_gold_financial_summary       (解析した情報を列にマッピング)
4. 4_gold_financial_metrics_unpivoted (UNPIVOT)
5. 5_gold_key_driver_analysis     (収益増加のキードライバー分析)
```

Dataformを実行してみるとエラーになったので修正を依頼します。ついでに、長期記憶がSession間で共有されるか確かめたかったのでSessionを切り替えてみます。

![](https://static.zenn.studio/user-upload/cfb1d2e3a9e3-20260502.png)

![](https://static.zenn.studio/user-upload/b7d260771c74-20260502.png)  
オーケストレーターが最新の実行を読み取り、DEAに修正を依頼してコンパイルまで済ませてくれます。Dataformの実行権限まわりが面倒だったため、今回はDataformの実行のみ人の手で行っていますが、実際にはほとんど人の手を介さずにパイプラインの作成・修正を自律的に行うエージェントを作れそうでした。

コンテキストの注入についても確認します。Session内で初めてエージェントを呼び出した際にtoolが呼び出されています。  
![](https://static.zenn.studio/user-upload/d462f3fd3648-20260502.png)  
![](https://static.zenn.studio/user-upload/fd0686e73868-20260502.png)

修正・確認依頼を数回繰り返すとテーブルが正常に作成されました。

### 分析結果

成果物をオーケストレーターに説明させたものです。

```
🎉 分析完了 - パイプライン修正成功！
全てのデータが正しく抽出されました。

📊 3_gold_financial_summary（財務サマリー）
四半期	Total Revenue	Google Services	Google Cloud	YouTube Ads	Operating Income	Net Income	EPS
Q1 2024	$80,539M	$70,398M	$9,574M	$8,090M	$25,472M	$23,662M	$1.89
Q1 2023	$69,787M	$61,961M	$7,454M	$6,693M	$17,415M	$15,051M	$1.17
📈 YoY成長率
セグメント	成長率	増加額
Total Revenue	+15.7%	+$10.8B
Google Cloud	+28.4%	+$2.1B
YouTube Ads	+20.9%	+$1.4B
Google Services	+13.6%	+$8.4B
Operating Income	+46.3%	+$8.1B
EPS	+61.5%	+$0.72
🔍 AI.KEY_DRIVERS分析結果
ドライバー	貢献額	期待差分	評価
Google Services	+$8.4B	-$7.0B（期待以下）	全体の70%を占めるが、比率では期待通り
Google Cloud	+$2.1B	+$1.1B（期待以上）	成長の主要ドライバー

パイプラインは完全に動作しています！ 🚀
```

## ハンズオンの感想

Data Engineering Agentはそれなりに難易度の高いタスクでも、私が思っていた以上に高品質なパイプライン作成・トラブルシューティングを行ってくれました。その反面、ADK側の設計や各エージェントの役割分担がシビアで、ここを間違えるとDEAの性能を十分に引き出せない印象です。

# 最後に

* DEAがA2Aに対応しコンテキスト注入やMCP/別Agentとの連携ができるようになり、実際に手元で動かして確認できたことで、実用性の向上を実感できた
* 今回のNext全体で、AIを本番で稼働させ続けるためのソリューションが多く話されていて、Data Engineering AgentのGAで追加された機能もそれに則していると感じた
* Data Engineering Agentはロードマップとして、AirflowのDAGやSparkの作成、自律的な根本原因分析(RCA)、パイプライン失敗時の自動バックフィルなどに対応することが発表されていて、今後にかなり期待ができる

ここまで読んでくれた皆さん、最後までお付き合いいただきありがとうございました！
