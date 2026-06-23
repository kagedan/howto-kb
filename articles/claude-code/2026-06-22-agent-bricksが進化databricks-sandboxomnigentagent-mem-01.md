---
id: "2026-06-22-agent-bricksが進化databricks-sandboxomnigentagent-mem-01"
title: "Agent Bricksが進化！Databricks Sandbox・Omnigent・Agent Memoryを早速試してみた💨"
url: "https://zenn.dev/nttdata_tech/articles/98be21f3848a8e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "Python"]
date_published: "2026-06-22"
date_collected: "2026-06-23"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは、Databricksビジネス推進室の澁谷です。

Databricksの**Agent Bricks**は、2025年に登場した、企業データに基づく高品質なAIエージェントを簡単に構築することができる機能です。  
2026年6月15-18日に行われた、Databricksの年次カンファレンス「**Data + AI Summit 2026**」にて、このAgent Bricksの機能がさらに大きく拡張されることが発表されました！  
![](https://static.zenn.studio/user-upload/ecc8eaf38976-20260618.png)  
*出典：Data + AI Summit 2026 Keynote Day2 Live配信の画面キャプチャ*  
特筆すべきは、「Agent Bricks **powered by Omnigent**」とあるようにOmnigentによって強化されたことです。  
Omnigentとは、2026年6月にDatabricksが公開したオープンソースのメタハーネスです。  
<https://www.databricks.com/blog/introducing-omnigent-meta-harness-combine-control-and-share-your-agents>

DatabricksはこのOmnigentをOSSとして公開するとともに、Databricksの中では**Omnigent on Databricks**として、複数の異なるハーネスをオーケストレーションできるサービスをAgent Bricksのコンポーネントの位置づけで提供開始しました。

Omnigentに関するzenn記事はこちらをご覧ください▼  
<https://zenn.dev/nttdata_tech/articles/2fe14c8819557c>

本記事では、強化された**Agent Bricks**を実際に触りながら、Agent Bricksの何がどう変わったのか、そして企業でのAIエージェント活用にどのような可能性をもたらすのかについて考えてみます。

## 目次

1. Agent Bricksの進化
2. さっそく触ってみた
3. 考察

## 1. Agent Bricksの進化

### ・Agent Bricksとは

Agent Bricksは、企業データに基づく本番品質のAIエージェントを、より簡単に構築するためのDatabricksの機能です。  
<https://www.databricks.com/blog/introducing-agent-bricks>  
従来、企業でAIエージェントを作るには、プロンプト、モデル、検索方法、評価方法、コスト最適化など、多くの要素を個別に調整する必要がありました。  
Agent Bricksは、こうしたエージェント開発の複雑さを軽減するために公開されました。  
ユーザーが自然言語でタスクを定義し、データソースを接続すると、**Agent Bricksがタスクに応じて**評価ベンチマークやLLM Judgeを作成し、プロンプト、モデル、検索方法、ファインチューニングなどを**自動的に探索・最適化**してくれます。  
より少ない手作業で本番利用も見据えた品質に近づけられることは、当初からのAgent Bricksの大きな価値です。

2025年時点でのAgent Bricksを「触ってみた」記事はこちらをご覧ください▼  
<https://zenn.dev/nttdata_tech/articles/e231bcf752d948>

### ・強化されたAgent Bricks

2025年時点のAgent Bricksは、エージェントを作成しやすくすることに主眼がありました。  
2026年のアップデートでは、それに加えて「作ったエージェントを使い分ける・組み合わせる、制御する、安全に使う」といった**運用をしやすくする機能**が拡張されました。  
<https://www.databricks.com/blog/agent-bricks-dais-2026>  
背景にあるのは、AIエージェント開発の難しさが「エージェントを作ることだけではなくなってきている」という変化です。  
企業でエージェントを活用するには、モデル選択、データアクセス、ツール実行、権限、コスト、監視、共有といった運用上の課題が付き物です。  
Databricksのブログでも、「エージェントの中核となるループ自体は全体の1%にすぎず、残りの99%は token capacity、deployment、security、evaluation、monitoring、context、sharing といった周辺の技術的負債だ」と説明されています。  
こうした**周辺の複雑さを扱うための機能が拡張**されたことで、単にエージェントを作るための機能ではなく、複数のモデルやハーネス、エージェントを企業の中で安全に扱うための包括的な機能群へと**進化**しました。

### ・拡張された機能

**Choice / Context / Control** の3つの観点で拡張されました。  
![](https://static.zenn.studio/user-upload/ca485ca9b6e7-20260618.png)  
*出典：Data + AI Summit 2026 Keynote Day2 Live配信の画面キャプチャ*

* **Choice ：どのモデルやハーネスを使うかを選べる**  
  Kimi、Grokなどのモデル、LangGraph、Agno、CrewAIといったハーネスがサポートされ、エージェントを構成する部品の選択肢が大幅に拡大しました。さらに、**Omnigent on Databricks** が提供され、異なるハーネス上で動くエージェントをオーケストレーションできるようになりました。
* **Context ：エージェントが必要な業務文脈にアクセスできる**  
  既存機能のDocument IntelligenceやマネージドMCPによる外部データ接続に加えて、同年発表の新機能である**Genie Ontology**、**Agent Memory Service**を通じて、Lakehouse上のデータに限らず、業務に必要な様々なデータや文脈をエージェントが参照できるようになりました。  
  ![](https://static.zenn.studio/user-upload/d8f2a9aa093c-20260618.png)  
  *出典：Data + AI Summit 2026 Keynote Day2 Live配信の画面キャプチャ*
* **Control ：エージェントを安全に制御できる**  
  新機能**Databricks Sandbox**が発表され、エージェントが生成したコードやツール実行を、企業データや本番環境への影響を抑えながら安全に検証できるようになりました。  
  ![](https://static.zenn.studio/user-upload/d24ae5d8ef07-20260618.png)  
  *出典：Data + AI Summit 2026 Keynote Day2 Live配信の画面キャプチャ*  
  さらにUnity AI Gatewayを通じて、Agent Bricksで構築したエージェントを含む様々な部品に対し、細かなアクセス制御や予算管理、ポリシーに基づくルーティングなどを行えるようになりました。

実は、昨年投稿したZenn記事にて「Agent Bricks カスタムLLMでは、裏側でどのモデルが使われているのかが分からない点に不便やもどかしさがある」と指摘していました。  
今回"Choice"のアップデートの1つ、Omnigent on Databricksの中で、モデルやハーネスを明示的に選べるようになったことで、用途や要件に応じてエージェントをより柔軟に設計しやすくなったのは、個人的にかなり嬉しいアップデートです！  
<https://zenn.dev/nttdata_tech/articles/e231bcf752d948>

## 2. さっそく触ってみた

ここからは、2026年アップデートで追加された機能を実際に確認していきます。  
今回試したのは、以下の3つです。

なお、今回触る機能には Beta / Preview として提供されているものが含まれます。  
2026年6月現在、Omnigent on Databricksを利用するには Omnigent preview の有効化が必要です。Databricks Sandboxを利用するには、Sandbox preview の有効化と、対応リージョンのワークスペースが必要です。  
今回の検証では、Databricks Sandboxの対象リージョンに含まれている **AWS us-west-2** のワークスペースを利用しました。

### 2-1. Databricks Sandboxを試す

まず、Databricks Sandboxを作成してみます。  
Databricks Sandboxは、人やエージェントがコードを安全に実行するための分離された実行環境です。特にAIエージェントにコード実行やファイル操作を任せる場合、意図しない処理が業務データや本番環境へ影響しないよう、実行先の分離を可能にします。  
Databricks CLIから作成し、SSHで接続して利用する機能です。

まずは、手元のターミナルからDatabricks CLIを使ってSandboxを作成しました。

```
databricks auth login --host https://<your-workspace-host>
databricks sandbox create --profile sandbox-demo
databricks sandbox register --profile sandbox-demo
databricks sandbox ssh --profile sandbox-demo
```

ここまでで、Databricks SandboxにSSH接続できました。  
![](https://static.zenn.studio/user-upload/d6ef0f73c677-20260618.png)

続いて、Sandbox上で簡単なCSV分析を実行してみます。  
まず作業ディレクトリを作成し、売上データのCSVファイルを作成します。  
![](https://static.zenn.studio/user-upload/a99d76e91c0e-20260618.png)

続いて、このCSVを読み込み、カテゴリごとの件数、合計金額、平均金額を計算し、その結果をMarkdown形式のレポートとして出力するPythonスクリプトを作成しました。  
入力した10行の売上データがカテゴリごとに正しく集計され、`sales_report.md` に集計結果が保存されることを確認します。

以下は、作成したコードの一部のスクリーンショットです。  
![](https://static.zenn.studio/user-upload/a5708628f4c4-20260618.png)

作成したスクリプトを実行します。  
![](https://static.zenn.studio/user-upload/a7ce4764ce85-20260618.png)

実行結果として、10行のCSVデータが読み込まれ、カテゴリごとの件数、合計金額、平均金額がMarkdownレポートとして出力されました。出力されたMarkdownレポート上でも、カテゴリごとの件数、合計金額、平均金額が確認でき、入力したCSVの内容と照合して期待どおりの結果になっていることが確認できました。  
また、Sandbox上に `sales.csv`、`analyze_sales.py`、`sales_report.md` が作成されていることも確認できました。  
これにより、Sandbox上でファイル作成、コード実行、成果物生成まで一連の処理を実行できることが確認できました！

以上の手順で、Databricks Sandboxでは「ファイルを読む」「コードを実行する」「結果を成果物として残す」といった作業を、Databricks上の分離された実行環境で行うことができます。  
今回は人の手でSSH接続して成果物作成を実施しましたが、**エージェント**にこのような作業を実施させる際に、安全な実行環境としてSandboxは価値があると感じました。  
そこで次の章では、このSandboxをエージェントの実行先として選び、Omnigent on Databricksから利用してみます。

### 2-2. Omnigent on Databricksを試す

次に、Omnigent on Databricksを試してみます。

まず、手元のWSL環境にOmnigent CLIをインストールしました。

```
curl -fsSL https://omnigent.ai/install.sh | sh -s -- --extra "databricks"
source ~/.bashrc
```

Omnigent CLIのインストール後、Databricks Workspaceにログインし、手元のWSL環境をOmnigentの実行ホストとして接続しました。

```
omni setup
omni login https://<your-workspace-host>
omni host --server https://<your-workspace-host>
```

`omni host`を実行すると、手元のWSL環境がDatabricks Workspace上のOmnigentに接続されます。これで、Omnigent UIからローカル環境を実行先として選べる状態になりました！  
![](https://static.zenn.studio/user-upload/9885224a7608-20260618.png)  
Omnigent on Databricksを開くと、タスクを入力する画面が表示されました。  
まず確認できたのは、**利用するハーネスを選べる** ことです。  
画面上では、`Claude Code`、`Codex`、`Polly`、`Debby` を選択できました。Claude CodeやCodexのような単体のコーディングエージェントだけでなく、PollyはMulti-agent coding、DebbyはMulti-agent debateとして表示されていました。  
![](https://static.zenn.studio/user-upload/fcacf7225c99-20260618.png)

次に、**実行環境を選べる** ことも確認できました。  
実行先として、`Databricks Sandbox` と、先ほど `omni host` で接続した手元のローカル環境が表示されていました。今回は、Omnigentからエージェントを実行する際の実行先として、先ほど作成したDatabricks Sandboxを選択しました。  
![](https://static.zenn.studio/user-upload/dda9f8267db7-20260618.png)

つまりOmnigent UIでは、「どのエージェントに任せるか」と「どこで実行させるか」を選んでからタスクを開始できます。  
エージェントがファイルを書いたり、コードを実行したりすることを考えると、実行環境を明示的に選べるのはかなり重要だと感じました。

さらにOmnigent UIでは、セッションにPolicyを簡単に追加できます。  
![](https://static.zenn.studio/user-upload/9d66819bc45c-20260618.png)  
+にカーソルを合わせると、Add Policyと出てきます  
![](https://static.zenn.studio/user-upload/e92c040fbaf5-20260618.png)  
`Enforce Sandbox on Agent Start`、`Deny PII in LLM Requests`、`Session Cost Budget`などのデフォルトポリシーを追加できることが確認できました。

さらに、Share機能も確認できました。  
この機能により、セッション（AI Agentのやり取り）をWorkspace内のユーザーや特定のユーザーを指定して共有することができます。  
![](https://static.zenn.studio/user-upload/40445c7ae65e-20260618.png)

DATA+AI SUMMIT 2026 Keynote Day2で行われたデモの中でも、Matei氏がバカンス中のAnkit氏に簡単に状況を共有できていたのが印象的でしたね！  
![](https://static.zenn.studio/user-upload/9fd6d19f63c3-20260618.png)  
*出典：Data + AI Summit 2026 Keynote Day2 Live配信の画面キャプチャ*

### 2-3. Agent Memoryを試す

最後に、Agent Memoryを確認しました。  
Agent Memoryは、エージェントが会話中または過去の会話から情報を記憶し、文脈に応じた応答を返せるようにする仕組みです。Databricksでは、Lakebaseを使ってconversation stateやhistory を管理します。

今回は、Databricks Apps向けの `agent-langgraph-advanced` テンプレートを使い、新しくLakebaseを用意してmemory storeとして設定しました。  
![](https://static.zenn.studio/user-upload/4078d55535e0-20260618.png)

Memoryの挙動を確認するため、テンプレートで起動したエージェントアプリに対してAPI経由でリクエストを送りました。  
「同じ画面の会話履歴を見ているだけなのか」「Lakebaseに保存されたMemoryを取りに行っているのか」を確認するため、1回目でMemoryを保存し、2回目では`thread_id`を変えて、同じ `user_id`のMemoryを参照できるかを見ていきます。

1回目のリクエストでは、以下のように「ブログ執筆スタイルを覚えてください」という依頼を送りました。このとき、`thread_id` と `user_id` を指定しています。

```
{
  "input": [
    {
      "role": "user",
      "content": "私のブログ執筆スタイルを覚えてください。私はDatabricks関連の新機能を、初心者にもわかりやすく、でも技術的に正確に説明する記事を書きたいです。記事では、まず実際に触った画面やデモを紹介し、そのあと考察を書く構成が好きです。"
    }
  ],
  "custom_inputs": {
    "thread_id": "blog-memory-demo-thread",
    "user_id": "user@example.com"
  }
}
```

レスポンスを見ると、`save_user_memory`が呼ばれ、情報がMemoryとして保存されたことを確認できました。  
![](https://static.zenn.studio/user-upload/a035321c9eca-20260618.png)

次に、`thread_id`を変えて、同じ`user_id`で問い合わせてみました。

```
{
  "input": [
    {
      "role": "user",
      "content": "以前伝えた私のブログ執筆スタイルを踏まえて、Agent Memoryの記事タイトル案を3つ出してください。"
    }
  ],
  "custom_inputs": {
    "thread_id": "blog-memory-demo-thread-2",
    "user_id": "user@example.com"
  }
}
```

すると、レスポンスでは`get_user_memory`が呼ばれ、保存済みのMemoryが検索されました。そのうえで、以前伝えたブログ執筆スタイルを踏まえた回答が返ってきました。同じ `user_id` のまま `thread_id` を変えて複数回問い合わせても、保存済みのMemoryが参照されました。  
![](https://static.zenn.studio/user-upload/c870b3753b40-20260618.png)

この挙動から、Memoryが単なる画面上の会話履歴ではなく、Lakebase-backed storeに保存されたユーザー単位の情報として扱われていることが分かります。

ここで重要なのは、単に「チャットが前の会話を覚えていた」という話ではないことです。  
Agent Memoryでは、`thread_id` による会話単位の短期記憶と、`user_id` によるユーザー単位の長期記憶を分けて扱えます。さらに、そのMemoryはLakebaseをbacking storeとして保存され、エージェントが必要に応じて検索・保存・削除できる構成になっています。  
短期記憶として会話単位で扱う情報と、長期記憶としてユーザー単位で保持する情報をどう分けるかを設計しないと、企業利用ではリスクにもなります。特に個人情報、機密情報、業務上の判断根拠に関わる情報をMemoryとして扱う場合は、保存対象、参照範囲、保存期間、必要に応じた更新・削除の考え方をあらかじめ整理しておく必要があります。  
つまり、企業が自社のエージェントアプリケーションに組み込める**管理可能なMemory**として扱える点に価値があります。

## 3. 考察

ここからは、実際に触ってみて感じたことや考えたことを述べていきます。

### OSS版Omnigentとの違い

OmnigentはOSSとして公開されており、ローカル環境でも利用できます。  
一方で、Databricks上で提供される Omnigent on Databricks では、Databricksが運用するOmnigent server、ワークスペースのIDプロバイダーとの統合、Foundation Model APIs / AI Gateway経由のモデルアクセス、Databricks Sandboxによる安全な実行環境が提供されます。  
つまりDatabricks版では、OSS版Omnigentの機能に加えて、Databricksのワークスペース、認証、モデルアクセス、Sandbox、AI Gateway等の既存アセットと統合して利用できる点が、Omnigent on Databricksの大きな特徴です。  
既にDatabricksを活用している企業にとっては、アセットを組み合わせてユースケースに適したエージェントをどんどん生み出し、運用していくことができるので、これからエージェントを「作る」に留まらず「業務に組み込んでいく」ために**強いブーストをかけるアップデート**だと感じました。

### Agent Bricksはエージェントのライフサイクル全体を担うブランドへ

今年発表された新機能を実際に触ってみて、エージェントに関わるあらゆる人間の作業を、より楽に、安全に、高品質に進めやすくなることを実感しました。  
Omnigentによるハーネスの選択、Sandboxによる安全な実行環境、Agent Memoryによる記憶、AI Gatewayによるモデルアクセスやガバナンス…これら全てがAgent Bricksという名のもとで提供されたことで、「エージェントを簡単に作るGUI」の位置づけからスコープを大きく広げ、エージェント活用に必要なあらゆる機能群を束ねる**包括的なブランド**へと進化していました。  
公式ブログで、2026年のAgent Bricksについて「comprehensive agent platform for developers」と説明されています。その言葉の通り、Agent Bricksはエージェントのライフサイクルの全体を担った、これから企業がAIエージェントを本格的に利活用するうえで十分頼もしい土台と言えそうです。

### 任せるためには、理解する力も必要

Agent Bricksは、Omnigent、Sandbox、Agent Memory、AI Gateway、Lakebaseなど、Databricksが提供するさまざまな機能を**横断的に取り込みながら進化**しています。  
だからこそ、使う側もそれぞれの機能や制約を理解しておく必要があると感じました。  
たとえば今回も、Sandboxを使うには対応リージョンやPreview設定の確認が必要でしたし、Agent Memoryを試すにはLakebase等の機能も把握する必要がありました。  
エージェント基盤は、業務データへのアクセス、コード実行、記憶、権限、コスト管理などに関わる責任ある土台です。その基盤としてAgent Bricksを扱うからこそ、各種機能を正しく理解し、環境や制約を踏まえて使いこなすための努力は怠ってはいけないと感じました。

## おわりに

今回は、Data + AI Summit 2026で強化が発表された **Agent Bricks** について、新機能を中心に試しながら、その進化のポイントを整理しました。  
OmnigentやUnity AI Gatewayのサポートを追い風に、Agent Bricksはもはや「エージェントを作る機能」から、実行環境、ハーネス選択、制御、共有、記憶まで含めてエージェント活用に必要な幅広い領域を扱うブランドへ広がっていました。  
今回は分量の都合上、すべての新機能を試すことはできませんでしたが、Agent Bricks周辺では、他にもDocument Intelligence、Genie OntologyやUnity AI Gatewayなど、企業でのエージェント活用を支える機能が多数発表されおり、非常にワクワクします。  
まだBeta/Previewの機能もあり利用条件には注意が必要ですが、既にDatabricksを活用している企業にとってAgent Bricksは、AIエージェント活用を一歩先に進めるための強力な追い風になりそうです！

# 仲間募集

NTTデータ ソリューション事業本部 では、以下の職種を募集しています。

Databricks、生成AIを活用したデータ基盤構築/活用支援（Databricks Championとの協働）
Snowflake、生成AIを活用したデータ基盤構築/活用支援（Snowflake Data Superheroesとの協働）
プロジェクトマネージャー（データ分析プラットフォームソリューションの企画～開発～導入／生成AI活用）
クラウドを活用したデータ分析プラットフォームの開発(ITアーキテクト/PM/クラウドエンジニア)
データドリブンDXを推進するデータサイエンティスト

# ソリューション紹介

Trusted Data Foundationについて

～データ資産を分析活用するための環境をオールインワンで提供するソリューション～  
<https://www.nttdata.com/jp/ja/lineup/tdf/>  
最新のクラウド技術を採用して弊社が独自に設計したリファレンスアーキテクチャ（Datalake+DWH+AI/BI）を顧客要件に合わせてカスタマイズして提供します。  
可視化、機械学習、Deep Learningなどデータ資産を分析活用するための環境がオールインワンで用意されており、これまでとは別次元の量と質のデータを用いてアジリティ高くDX推進を実現できます。

TDFⓇ-AM（Trusted Data Foundation - Analytics Managed Service）について

～データ活用基盤の段階的な拡張支援（Quick Start) と保守運用のマネジメント（Analytics Managed）をご提供することでお客様のDXを成功に導く、データ活用プラットフォームサービス～  
<https://www.nttdata.com/jp/ja/lineup/tdf_am/>  
TDFⓇ-AMは、データ活用をQuickに始めることができ、データ活用の成熟度に応じて段階的に環境を拡張します。プラットフォームの保守運用はNTTデータが一括で実施し、お客様は成果創出に専念することが可能です。また、日々最新のテクノロジーをキャッチアップし、常に活用しやすい環境を提供します。なお、ご要望に応じて上流のコンサルティングフェーズからAI/BIなどのデータ活用支援に至るまで、End to Endで課題解決に向けて伴走することも可能です。

NTTデータとDatabricksについて

NTTデータは、お客様企業のデジタル変革・DXの成功に向けて、「Databricks」のソリューションの提供に加え、情報活用戦略の立案から、AI技術の活用も含めたアナリティクス、分析基盤構築・運用、分析業務のアウトソースまで、ワンストップの支援を提供いたします。  
<https://www.nttdata.com/jp/ja/lineup/databricks/>

NTTデータとSnowflakeについて

NTTデータとSnowflakeについて  
NTTデータでは、Snowflake Inc.とソリューションパートナー契約を締結し、クラウド・データプラットフォーム「Snowflake」の導入・構築、および活用支援を開始しています。  
NTTデータではこれまでも、独自ノウハウに基づき、ビッグデータ・AIなど領域に係る市場競争力のあるさまざまなソリューションパートナーとともにエコシステムを形成し、お客さまのビジネス変革を導いてきました。  
Snowflakeは、これら先端テクノロジーとのエコシステムの形成に強みがあり、NTTデータはこれらを組み合わせることでお客さまに最適なインテグレーションをご提供いたします。  
<https://www.nttdata.com/jp/ja/lineup/snowflake/>

NTTデータとInformaticaについて

NTTデータとInformaticaについて  
データ連携や処理方式を専門領域として10年以上取り組んできたプロ集団であるNTTデータは、データマネジメント領域でグローバルでの高い評価を得ているInformatica社とパートナーシップを結び、サービス強化を推進しています。  
<https://www.nttdata.com/jp/ja/lineup/informatica/>

NTTデータとTableauについて

NTTデータとTableauについて  
ビジュアル分析プラットフォームのTableauと2014年にパートナー契約を締結し、自社の経営ダッシュボード基盤への採用や独自のコンピテンシーセンターの設置などの取り組みを進めてきました。さらに2019年度にはSalesforceとワンストップでのサービスを提供開始するなど、積極的にビジネスを展開しています。  
これまでPartner of the Year, Japanを4年連続で受賞しており、2021年にはアジア太平洋地域で最もビジネスに貢献したパートナーとして表彰されました。  
また、2020年度からは、Tableauを活用したデータ活用促進のコンサルティングや導入サービスの他、AI活用やデータマネジメント整備など、お客さまの企業全体のデータ活用民主化を成功させるためのノウハウ・方法論を体系化した「デジタルサクセス」プログラムを提供開始しています。  
<https://www.nttdata.com/jp/ja/lineup/tableau/>

NTTデータとAlteryxについて

NTTデータとAlteryxについて  
Alteryxは、業務ユーザーからIT部門まで誰でも使えるセルフサービス分析プラットフォームです。  
Alteryx導入の豊富な実績を持つNTTデータは、最高位にあたるAlteryx Premiumパートナーとしてお客さまをご支援します。  
導入時のプロフェッショナル支援など独自メニューを整備し、特定の業種によらない多くのお客さまに、Alteryxを活用したサービスの強化・拡充を提供します。  
<https://www.nttdata.com/jp/ja/lineup/alteryx/>

NTTデータとDataRobotについて

NTTデータとDataRobotについて  
DataRobotは、包括的なAIライフサイクルプラットフォームです。  
NTTデータはDataRobot社と戦略的資本業務提携を行い、経験豊富なデータサイエンティストがAI・データ活用を起点にお客様のビジネスにおける価値創出をご支援します。  
<https://www.nttdata.com/jp/ja/lineup/datarobot/>
