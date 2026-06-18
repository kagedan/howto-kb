---
id: "2026-06-17-databricks発ossのメタハーネスomnigentを触ってみた-01"
title: "Databricks発OSSのメタハーネス『Omnigent』を触ってみた！🪸⭐"
url: "https://zenn.dev/nttdata_tech/articles/2fe14c8819557c"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "OpenAI", "GPT"]
date_published: "2026-06-17"
date_collected: "2026-06-18"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは、Databricksビジネス推進室の澁谷です。

Databricksのブログで紹介されていたOSS「**Omnigent**」が気になったので、実際にローカル環境で触ってみました。  
<https://www.databricks.com/jp/blog/introducing-omnigent-meta-harness-combine-control-and-share-your-agents>  
Omnigentは、Claude Code、Codex、自作エージェントなど、複数のAIエージェントをまとめて扱うための「**メタハーネス**」です。  
要するに、既存のハーネスやモデルで動く複数のエージェントを、そのさらに上のレイヤーから束ね、**組み合わせ、制御し、共有する**ための仕組みです。

Omnigentには、DebbyやPollyといった組み込みサンプルに加えて、credential管理、YAMLによるエージェント構成定義、ポリシー制御、セッション共有など、複数エージェントを運用するための機能が用意されています。

今回はOmnigentの理解を深める第一歩として、組み込みサンプル「**Debby**」を動かして、複数のエージェント同士にディベートをさせてみました。  
この記事では、Debbyを通じてOmnigentの基本的な使い方を確認しつつ、**Omnigentで実現する近未来のAI・エージェント利活用の形**を考えてみます。

## 目次

1. Omnigentとは
2. Omnigentを動かしてみる
3. Debby検証：複数エージェントにディベートさせる
4. Omnigentで実現する「エージェント利活用のこれから」

## 1. Omnigentとは何か

Omnigentは、Databricksが公開した**オープンソースのメタハーネス**です。  
メタハーネスとは、Claude Code、Codex、Pi、自作エージェントなど、既存のエージェントやエージェントハーネスの上に立ち、それらを一元的に扱えるようにするレイヤーです。  
![](https://static.zenn.studio/user-upload/72096edbcd51-20260618.png)  
Omnigentのアーキテクチャでは、**Runner**が任意のエージェントをサンドボックス化されたセッションとして実行し、統一APIでラップします。  
その上で**Server**が、履歴、ポリシー、成果物、カタログ、MCP、スキルなどを管理し、チームでの共有や制御を担います。

具体的には、「どのハーネスを使うか」「どのモデルを使うか」「どのような役割を持たせるか」等をYAMLで定義しておくことで、**複数エージェントを同じ土台の上で起動し、用途に合わせて呼び出したり、組み合わせたり**できます。  
さらに権限やコストもOmnigentで制御でき、チームや組織でのAI・エージェント利活用を見据えた設計になっています。

従来のAIエージェント利用では、以下のような状態になりがちでした。

* Claude CodeはClaude Codeとして開く
* CodexはCodexとして開く
* 別の自作エージェントは別のCLIやAPIで動かす
* それぞれの結果を人間がコピー＆ペーストして比較する
* 必要に応じて、別のチャットやドキュメントに貼り直す

Omnigentを使うことで、このような「人間がエージェント間の交通整理をしている状態」を脱することができます。

---

### Omnigentでできること

Omnigentには以下のような機能があります。

#### ・組み込みサンプルDebby・Pollyによる複数エージェント活用

Omnigentには、DebbyやPollyといった組み込みサンプルが用意されています。  
Debbyは、複数のエージェントに同じ質問を投げ、回答を比較したり、`/debate` で相互批評させたりできます。  
Pollyは、複数のエージェントを使ってソフトウェア開発タスクを進めることができます。  
これらはClaude Code、Codexなどを組み合わせた複数エージェント構成としてすぐに  
使用できます。

#### ・エージェントの制御

エージェントに自由に動かせるだけでなく、ポリシーやサンドボックスで**制御**できます。  
たとえば、ファイルシステムやネットワークアクセスを制限したり、コストが一定額を超えたら止めたり、人間の承認を挟んだりするような制御が可能です。  
AI・エージェントをチームや組織といった大きな単位で安全に利活用していくうえで重要な機能です。

#### ・セッションの共有

Omnigentでは、エージェントのセッションを**URLで共有**し、チームメンバーと一緒に確認したり、コメントしたり、操作したりできます。  
これは、AIエージェントの作業を個人のローカル端末に閉じず、チームで見える形にするための機能です。

#### ・YAMLによるカスタムエージェント定義

エージェントの構成を**YAMLで定義**できます。  
「どのハーネスを使うか」「どのモデルを使うか」「どのような役割を持たせるか」等を設定として記述し、自分たちの業務や開発スタイルに合わせた**マルチエージェント構成**を作ることができます。  
先述のDebbyやPollyのYAMLを参考にして書き換えることで、比較的簡単に独自の構成を作れます。

## 2. Omnigentを動かしてみる

### 検証環境

今回の検証環境は以下です。

* Windows + WSL2
* WSL Ubuntu 24.04.1 LTS
* Python 3.12+
* Node.js 22 LTS
* tmux 3.4
* Omnigent 0.1.0
* Claude Pro Subscription
* ChatGPT / Codex Subscription

Windows上で直接動かすのではなく、WSL Ubuntu上でOmnigentを動かしました。  
OmnigentはtmuxなどのLinux系ツールを使うため、Windows環境ではWSLを使うのがやりやすそうです。

### Omnigentをインストールする

まず、WSL Ubuntu上で必要なツールを入れました。

```
sudo apt update
sudo apt install -y tmux curl git build-essential
```

Node.js 22 LTSも必要だったため、NodeSource経由でインストールしました。

```
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
```

Omnigent本体は以下でインストールしました。

```
curl -fsSL https://omnigent.ai/install.sh | sh
```

### Codexを接続する

OmnigentからClaudeとCodexを呼び出せるようにするため、`omni setup` でcredentialを設定します。

まずCodexを設定しました。  
`omni setup` のメニューから以下のように進めます。

```
Codex
→ Add a credential
→ Subscription / Login
```

ブラウザでOpenAI / ChatGPT側にログインすると、Codexの接続に成功しました。

```
Successfully logged in
✓ Added codex-subscription - default for Codex
```

これでCodex側はOmnigentから使える状態になりました。

### Claudeを接続する

次にClaudeを設定しました。`omni setup` のメニューから以下のように進めます。

```
Claude
→ Add a credential
→ Claude - subscription (Pro/Max)
```

Claude側もブラウザでログインします。  
※Claude Codeの利用にはClaude ProまたはMaxが必要です。

ログイン後、Claude Subscriptionの追加に成功しました。

```
Login successful.
✓ Added claude-subscription
```

最後にDebbyを起動し、ClaudeとCodexが認識されていることを確認しました。  
![](https://static.zenn.studio/user-upload/2a8dfc3b4b0f-20260616.jpg)

これで、ClaudeとCodexの両方をOmnigentから呼び出せる状態になりました。

### 少し詰まったポイント

途中で少し詰まったのが、Claudeの接続方式です。  
Databricks Workspace経由のClaude接続も試しましたが、credentialの追加まではできたものの、実行時に401エラーとなったため、今回は断念しました。  
最終的には、Claude Pro SubscriptionとCodex Subscriptionをそれぞれ接続する構成に切り替えました。

## 3. Debby検証：複数エージェントにディベートさせる

準備ができたので、Debbyに質問してみます。  
![](https://static.zenn.studio/user-upload/f48d97de059d-20260616.jpg)

すると、Debbyが内部でClaudeとCodexの両方に依頼を送っていることが確認できました。  
しばらく待つと、ClaudeとCodexそれぞれの回答が返ってきました。  
![](https://static.zenn.studio/user-upload/ea2e7beb285c-20260616.jpg)

Debbyが最後に「まとめると…」という形で、両者の回答を整理してくれています。  
![](https://static.zenn.studio/user-upload/45a1a1ff6720-20260616.jpg)

Omnigentが単なるチャットUIではなく、複数のサブエージェントを束ねて結果を集約するレイヤーであることが実感できました。

次に、Debbyの特徴的な機能である`/debate`を試しました。  
![](https://static.zenn.studio/user-upload/f5f22f0486d3-20260616.jpg)

すると、ClaudeとCodexが互いの回答を批評し、それぞれ改善版の最終回答を出してくれました。  
![](https://static.zenn.studio/user-upload/0b68e3bcb578-20260616.jpg)  
![](https://static.zenn.studio/user-upload/fbf73b09cb0f-20260616.jpg)

面白かったのは、単に「複数の回答を並べる」だけではなかった点です。  
相手の回答に対して、説明が曖昧な部分や不足している観点を指摘し、そのうえで自分の回答を改善していました。

Debbyを使うと、複数のエージェントに同じ問いを投げるだけでなく、回答同士を比較し、相互批評させ、改善版まで出させる流れを自然に作れました。  
今回の検証は小さなデモですが、「複数のエージェントを同じ土台で呼び出し、組み合わせ、制御する」というOmnigentの基本的な考え方を理解することができました。

## 4. Omnigentで実現する「エージェント利活用のこれから」

実際にOmnigentを触ってみて、わかったことや感想、考えを以下に述べます。

### Debbyはあくまで入口

Debbyはあくまでサンプルです。  
Omnigentの面白さは、Debbyのようなマルチエージェント構成を、自分たちの業務や開発スタイルに合わせて作れるところにあります。  
DebbyのYAMLをコピーして少し書き換えれば、自分たちの用途に合わせたマルチエージェント構成を作りやすそうです。

### Databricksの抽象化と似ている

Omnigentを触っていて感じたのは、Databricksの抽象化の思想に通ずるものがあるということです。  
Databricksは、AWS（Amazon Web Services）、Azure、Google Cloudなどのクラウド上で動きます。たとえばAWS上で使う場合、裏側にはS3、EC2、IAM、VPCなどのクラウドリソースがあります。ただ、利用者はそれらを常に個別に意識するわけではありません。

Omnigentも同じように、Claude Code、Codex、MCP、A2A、credential、セッション管理などの部品を、メタハーネスとして一段上から扱えるようにしています。  
Databricksがクラウドリソースの複雑さを吸収し、データ+AI開発者にとって扱いやすい形で提供しているように、Omnigentも複数エージェントや周辺技術の複雑さを吸収し、エージェント利用者にとって扱いやすい形に変えて提供しています。  
「複雑な基盤をそのまま見せるのではなく、利用者が本来やりたいことに集中できる形で提供する」という思想が、DatabricksとOmnigentには共通していると感じました。

### Omnigentから見えてくる近未来のAI・エージェント利活用の形

MCPやA2Aのような共通プロトコルは、エージェントがツールや他のエージェントとつながるための接続部分を標準化してくれます。  
MCPは、エージェントが外部ツールやデータソースにアクセスするための仕組みです。  
A2Aは、異なるフレームワークやベンダーで作られたエージェント同士が連携するための仕組みです。  
一方で、接続が標準化されたとしても、接続した後に「どう使い、どう制御し、どう共有するか」という運用面の課題は残ります。今後、エージェントや周辺技術がさらに進化していくほど、現場で扱う対象もさらに増えていくはずです。  
その目覚ましい進化に伴って、運用苦も増えてしまわないように、エージェントの実行・制御・共有・最適化を扱うOmnigentのような上位レイヤーが重要になっていくのだと思います。

冒頭で紹介したブログでも、  
「これらの機能はメタハーネスレイヤーで実現できることのほんの一部にすぎません。今後、私たちのチームやオープンソースコミュニティからさらに多くのアイデアが生まれることを期待しています。」と述べられていました。  
**メタハーネス**という新しい考え方は、今後さらに広がっていきそうです。  
そしてOmnigentはメタハーネス界のパイオニア的存在として、今後のAI・エージェント利活用において重要な役割を果たしそうです。

（6/18加筆：DATA+AI SUMMIT2026 Keynote Day2より）  
![](https://static.zenn.studio/user-upload/b44755ffa2b9-20260618.jpg)

## おわりに

今回は、Databricks発OSS「Omnigent」をWSL Ubuntu上で触り、ClaudeとCodexを接続して、サンプルのDebbyを試してみました。  
Debbyはあくまで入口ですが、「複数エージェントを同じ土台の上で扱う体験」が提供する価値を実感することができました。  
今後、AI・エージェントをチームや組織で利活用していくうえで、Omnigentのようなメタハーネスレイヤーを取り入れることは重要な選択肢になっていきそうです。  
気になった方は、ぜひ一度触ってみてください。

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
