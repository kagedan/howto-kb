---
id: "2026-07-10-databricksのgenieがリニューアル何ができるのかまとめてみた-01"
title: "DatabricksのGenieがリニューアル！何ができるのかまとめてみた"
url: "https://zenn.dev/nttdata_tech/articles/18b00a4a12aa33"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "AI-agent", "LLM", "GPT", "cowork", "zenn"]
date_published: "2026-07-10"
date_collected: "2026-07-11"
summary_by: "auto-rss"
query: ""
---

# はじめに

こんにちは、NTTデータグループAI技術部の太田です。  
先日サンフランシスコで開催されたDatabricksのイベント「Data + AI Summit 2026」に現地参加してきました。

本カンファレンスでの注目トピックの一つとして「Genie」が大きく進化しました。これまでGenieというと「自然言語でデータに質問できるAI/BIアシスタント」という印象が強かったと思います。今回の発表では、Genieが単なる分析アシスタントから、ビジネスユーザから開発者まで幅広いユーザと共に業務を遂行する**AI Coworkerなサービス群**へと再定義されました。

本記事では、Data + AI Summit 2026のKeynoteやDatabricksの公式情報をもとに、主要なGenieファミリーの各機能を整理しつつ、ハンズオンを交えて今後のデータ活用/AI活用がどう変わりそうかを考えてみます。

# これまでのGenie

もともと、GenieはDatabricks AI/BIの1機能として、ダッシュボードでは対応できない質問に回答するための対話型インターフェースとしてリリースされました。  
![](https://static.zenn.studio/user-upload/49b92daed07e-20260629.png)  
*引用：[Introducing AI/BI: Intelligent Analytics for Real-World Data](https://www.databricks.com/blog/introducing-aibi-intelligent-analytics-real-world-data)*  
この時点でも、既にUnity Catalogと統合され権限に基づいた回答や、データリネージ機能によるデータセットの起源をデータ取り込み時点まで遡って追跡するといった機能は備えていたものの、主な役割は**Databricks上のデータを自然言語で分析・検索するAIアシスタント**でした。  
![](https://static.zenn.studio/user-upload/c27a26d54254-20260629.png)  
*引用：[Introducing AI/BI: Intelligent Analytics for Real-World Data](https://www.databricks.com/blog/introducing-aibi-intelligent-analytics-real-world-data)*  
<https://www.databricks.com/blog/introducing-aibi-intelligent-analytics-real-world-data>

# Genieファミリーとしての再出発

![](https://static.zenn.studio/user-upload/bc379e0329ac-20260629.png)  
*引用：[Data + AI Summit Keynote 2026 | Day 1](https://www.youtube.com/watch?v=Qux8E-L1mk8&t=2752s)*  
今回の発表では、Genieに加えこれまでDatabricks One、Databricks Assistantといった各サービスを強化・リネームする形で統合が図られています。  
すべてGenie○○という形でリネームされており、Genieを単純なチャットボットから**ユーザと共に業務を遂行するAgenticサービス群**として位置付けたいというDatabricksの意図を感じられます。  
そして、各Genieサービスを使ってAgenticに業務を遂行するために、Databricksは「利用者ごとに最適化されたインターフェース」と「それらを支える共通の文脈基盤」の整備を進めるアプローチをとっており、今回リニューアルされたGenieファミリーにも、各サービス毎に明確な役割が与えられています。

# Genie One

Genie Oneは、これまでDatabricks Oneとして知られていた**ビジネスユーザ向けのシンプルなDatabricks UI**です。Lakehouse、つまりこれまでのDatabricksワークスペースで意識せざるを得ないコンピュート、クエリ、モデル、ノートブックなどの技術的な概念を知る必要なく、AI/BIダッシュボードの閲覧、自然言語での質問、Databricks Appsの利用を単一の入口から実行できるようにするものです。  
![](https://static.zenn.studio/user-upload/4681d9dae290-20260701.png)  
*ChatGPTやClaudeのようなシンプルなUI*

公式ブログでは、Genie Oneは従来の会話型分析アシスタントとしてのGenieから一歩進み、洞察を得るだけでなく、そこから業務アクションにつなげるAI Coworker として説明されています。

これまではDatabricksに保存されたデータに対する対話型分析のみを提供していましたが、Genie OneはDatabricksだけでなく、豊富に用意されたコネクタを通じてアプリケーションすべてのデータを利用可能になりました。

Keynote Day1のデモでは、**Genie Oneに入力した指示を解釈してGoogle Drive上のファイルやJiraチケットを参照、またMCPを通じてチケットにコメントを残しつつレビューのレポートを作成するといったタスク**を実行していました。  
![](https://static.zenn.studio/user-upload/295c4c95e7b1-20260701.png)  
*引用：[Data + AI Summit Keynote 2026 | Day 1](https://www.youtube.com/watch?v=Qux8E-L1mk8&t=4280s)*  
Genie Oneのもう一つのトピックとして、モバイルアプリのリリースもアナウンスされています。  
既に進行中のチャットはもちろん、作成されたダッシュボードやAppをスマートフォン上からも実行可能なことがアピールされていました。

![](https://static.zenn.studio/user-upload/1919ec04e0ff-20260701.png)  
*引用：[Data + AI Summit Keynote 2026 | Day 1](https://www.youtube.com/watch?v=Qux8E-L1mk8&t=4280s)*  
既にアプリはApp StoreとGoogle Playでリリースされており、誰でもインストール可能です。  
<https://apps.apple.com/app/genie-one-by-databricks/id6758961415>  
<https://play.google.com/store/apps/details?id=com.databricks.one.mobile&pcampaignid=web_share>

# Genie Agents

**Genie Agentsは、特定の業務領域に特化した共有可能なAIエージェント**です。公式ブログでは、Genie SpacesがGenie Agentsへ進化し、構造化データだけでなくドキュメントやファイルなどの非構造化データも参照しながら、MCP接続、スケジュールされたタスク、文書/成果物生成、外部システムへの書き込みなどを用いて複数ステップのワークフローを実行できると説明されています。従来のGenie Spacesをベースに、エージェントとしてワークフロー実行や成果物生成まで担えるよう拡張されました。

特に面白い点は、専門家が持っている業務ルール、データの見方、判断基準をGenie Agentとして共有し、チーム全体で再利用できるようにする、という構想です。データアナリストや業務部門の暗黙知を、AIエージェントとしてスケールさせる機能と捉えると分かりやすいです。

Keynote Day1のデモでは、**先ほど紹介したGenie Oneで指示したレビュータスクをエージェントとして保存し、チーム内でレビューエージェントとして共有する**、といった具体的なユースケースが紹介されました。  
![](https://static.zenn.studio/user-upload/01c592aa4c39-20260701.png)  
*引用：[Data + AI Summit Keynote 2026 | Day 1](https://www.youtube.com/watch?v=Qux8E-L1mk8&t=4280s)*  
Genie OneとGenie Agentは別々の機能ではあるものの、上記のデモのようにシームレスな連携が可能となっており、**ビジネスユーザはGenie Oneを入り口として定型業務を自然言語で依頼し、その作業が良いものであればそのままエージェント化する、といった一連の流れが簡単に実現できるようになっている**ことに感動しました。  
一方で、エージェントの乱立を防ぐライフサイクル管理やガバナンスの検討がユーザに求められそうです。

# Genie ZeroOps

Genie ZeroOpsは、Databricks上のパイプラインやジョブで発生した異常に対して修正案の提示や検証までを行うことで、運用業務の負荷を低減する運用特化型のAIエージェントです。  
こちらの詳細は弊社の中川さんが詳細をまとめてくれているので、ぜひこちらも参照ください。  
<https://zenn.dev/nttdata_tech/articles/4ff330c3988089>

# Genie Ontology

これまでご紹介したGenieファミリーがAgenticに業務を遂行するための基盤となるのが、Genie Ontologyです。  
Genie Ontologyは、テーブル、クエリ、ダッシュボード、パイプライン、接続した外部サービスやアプリケーションなどから知識の断片を自動抽出するコンテキストレイヤーで、Databricksが保持するメタデータや接続先情報をもとに、利用可能なコンテキストを整理する仕組みとなっています。  
![](https://static.zenn.studio/user-upload/f23f8906481d-20260701.png)  
*引用：[Data + AI Summit Keynote 2026 | Day 1](https://www.youtube.com/watch?v=Qux8E-L1mk8&t=3659s)*

## Genie Ontologyの仕組み

Genie Ontologyは「自動的」に作成されますが、どのような仕組みで動作するのでしょうか。  
Keynoteの中で語られた流れは以下です。

1. Databricks内外のソースから情報の断片**Ontology Snippet**を抽出する
2. 独自のアルゴリズム**OntoRank**を使用して
   * ソースの作成者
   * 参照頻度
   * 検証済みアセットとの密接度
   * 新しさ  
     といった尺度などを評価し、情報の権威性・重要性を判断する
3. 情報の取得時に権限を適用する
4. エージェントループにコンテキストを注入する

OntoRankによってコンテキストレイヤを整備し、エージェントが情報を集める際に実行者が見える範囲のコンテキストを反映して回答できる、という仕組みですね。  
![](https://static.zenn.studio/user-upload/59efd6d0b910-20260701.png)  
*引用：[Data + AI Summit Keynote 2026 | Day 1](https://www.youtube.com/watch?v=Qux8E-L1mk8&t=4049s)*  
Genie Ontologyが導入されることによって、エージェントが情報の重要性や妥当性を判断するといった負荷が軽減し、**より適切なコンテキストを元に回答できる**ことが期待されます。  
実際にDatabricks社の内部テストでは、他のコーディングエージェント、特に最も正確なエージェントと比較して30%近い正確性を1/2の時間で実行できる、と謳っていました。  
![](https://static.zenn.studio/user-upload/3e45d5c29829-20260701.png)  
*引用：[Data + AI Summit Keynote 2026 | Day 1](https://www.youtube.com/watch?v=Qux8E-L1mk8&t=4049s)*

# 注意点

Genie機能はこれまでDatabricks上で無料で利用できましたが、2026年7月6日から従量課金モデルに移行します。

* 毎月の無料使用量 : 各ユーザは毎月、LLMの無料使用枠が設けられる。
* 従量課金の使用量 ：無料枠を超えた使用量は、基盤となるLLMの使用量に基づいてDBUで請求される。

同時に、管理者は予算やコスト制御を設定できるようになるとアナウンスされています。  
最新情報及び詳細については[Genieの予算とコスト管理](https://docs.databricks.com/aws/ja/genie/budgets)をご確認ください。

# おわりに

本記事では、Data + AI Summit 2026で発表されたGenieファミリーの概要についてご紹介しました。  
個人的には、今回のリネームや機能追加の本質は、単なるブランド整理ではなく**利用者ごとのAI体験と共通のコンテキストレイヤをセットで作りに来ている**点にあると感じました。各ユーザにはそれぞれの業務に合ったGenieを提供しつつ、その裏側ではGenie Ontologyによって同じ業務文脈を参照させる。これにより、Databricks上のAI活用は各個人に閉じたチャットや分析支援から、**組織全体で一貫した判断とアクションをGenieと共に推進していく形になる**のではないでしょうか。

# ソリューション紹介

NTTデータとDatabricksについて

NTTデータは、お客様企業のデジタル変革・DXの成功に向けて、「databricks」のソリューションの提供に加え、情報活用戦略の立案から、AI技術の活用も含めたアナリティクス、分析基盤構築・運用、分析業務のアウトソースまで、ワンストップの支援を提供いたします。  
<https://www.nttdata.com/jp/ja/lineup/databricks/>
