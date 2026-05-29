---
id: "2026-05-28-tableau-mcp界隈を理解するために世の中salesforce社tableau社それぞれの動向-01"
title: "Tableau MCP界隈を理解するために世の中/Salesforce社/Tableau社それぞれの動向を整理しなおしてみた"
url: "https://zenn.dev/truestar/articles/9538035762e039"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "LLM", "OpenAI"]
date_published: "2026-05-28"
date_collected: "2026-05-29"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/e57d6ccd72e6-20260528.png)

個人的「Tableau MCP界隈の情報整理をしてみよう」シリーズ第2弾。下記第1弾では、製品レベルの整理を行いました。

当エントリでは、ここ数年における、現時点までの世の中/Salesforce社/Tableau社それぞれの状況・動向を整理して「だから今これ、この流れなんだ」というところを改めて理解・把握していきたいと思います。

## A. 世の中(データの世界)的な動向

まずはSalesforce、Tableauそれぞれの視点で整理する前に更に大きな枠組みとなる『世の中、或いはデータの世界的にどういう流れになっているのか』について整理します。

### A-1. AIが「答える」から「動く」存在へ

2024年後半頃からAI活用の議論の中心が変わりました。**「質問したら答えてくれるAI（会話型）」から、「自分で考えて動くAI」＝AIエージェントの時代へのシフト** です。

PwCが2025年4〜5月に米国の経営幹部308名(C-suite・VP・ディレクタークラス)を対象に実施した調査では、79%の企業がすでにAIエージェントの導入を進めていると回答。さらに導入済みの企業のうち66%が「生産性向上として計測可能な成果が出ている」とも答えており、実証段階に入っていることがわかります。加えて、88%が「エージェントAIの影響でAI関連予算を今後12ヶ月以内に増やす予定」と回答しています。

Databricksもこの傾向を独自データで裏付けています。採用の加速とともにAgentic Analyticsは「補助的なツール」から「エンタープライズの業務に組み込まれた自律型システム」へと進化しており、次のイノベーションの波はスケーラブルなAIの協調・自動化された意思決定ループ・業種特化型インテリジェンスに向かっていると分析しています。

### A-2. 「Agentic Analytics」という発想の転換

この流れから生まれたキーワードが **Agentic Analytics** です。**「人がデータを見に行く」のではなく「AIがデータを見張って自律的に動く分析」** のことで、従来BIとの違いは明確です。

| 項目 | 従来のBI | Agentic Analytics |
| --- | --- | --- |
| 主役 | 人 | AIエージェント(人は監督役) |
| きっかけ | 人が画面を開く | エージェントが自律的に動く |
| 主な成果物 | ダッシュボード・レポート | アクション・通知・提案 |
| 操作方法 | クリック・集計 | 自然言語(話しかけるだけ) |

この変化がどこまでリアルかを示すエピソードが2026年5月のTableau Conference 2026で展開されていました。Disneyの担当者が **「3年以内に私たちのチームはダッシュボードを開かなくなる。データに話しかけて、それに従って動くようになる」** と語りました。世界最大のエンターテインメント企業が、BI活用の前提をここまで変えようとしています。

### A-3. MCP ― AIとツールをつなぐ「共通の差し込み口」の登場

この変化を支える技術の中核が **MCP(Model Context Protocol)** です。2024年11月にAnthropic(Claudeを開発する米AI企業)がオープンソースで公開した「接続規格」で、家電のコンセントに例えるとわかりやすいでしょう。コンセントの形が世界共通なら、どの国の電化製品でも差し込めます。同様に、MCPがあればAIと各種ツールを個別に繋ぎ直す必要がなくなります。

公開からわずか1年半でOpenAI・Google・Microsoftなど主要プレイヤー全社が採用し業界標準に。TableauのMCPも2026年5月に正式リリースされ、ClaudeやChatGPTなどの外部AIからTableauのデータへ直接接続できるようになっています。

参考：MCPが「業界標準」になるまでの動き

* 2024年11月: AnthropicがMCPをオープンソース公開
* 2025年3月26日: OpenAIのSam Altman CEOがX上で全製品対応を表明（"people love MCP..."）。競合の規格採用として大きな話題に
* 2025年4月9日: Google DeepMindのDemis Hassabis CEOがGemini/SDKでの対応を発表
* 2025年12月: AnthropicがMCPをLinux Foundation傘下のAgentic AI Foundation（AAIF）へ寄贈。OpenAI・Blockが共同創設、AWS・Google・Microsoft等が支援メンバーに

### A-4. BI市場の勢力図 ― 「単体ツール競争」の終わり

Gartnerの2025年版Magic Quadrantでは、下記6社がトップ評価を獲得しました。

* Microsoft(Power BI)
* Salesforce(Tableau)
* Google(Looker)
* Qlik
* Oracle
* ThoughtSpot

注目すべきは、**全社が「AI一体型プラットフォーム」へとかじを切っている** ことです。MicrosoftはCopilot、GoogleはGemini、SalesforceはAgentforceをそれぞれ組み合わせ、「データ基盤＋分析＋AI」が一体化したエコシステムとして競い合っています。

ここから見えてくる本質は **「どのBIツールが優れているか」ではなく「どのエコシステムを選ぶか」という問いへの変化です。単体ツールの優劣よりも、プラットフォーム全体としての力が問われる時代になっています。**

### A-5. OSI ― 「データの意味」を業界で統一する試み

MCPで「接続」が解決しつつある一方で、**「データの意味が各社・各ツールでバラバラ」という問題**が残ります。「売上」の定義ひとつとっても、請求・入金・受注ベースと企業によって異なります。AIが複数システムをまたいで分析するとき、この「意味のズレ」は致命的な誤りにつながります。VentureBeatはこれを「1兆ドル規模のAI問題」と表現しています。

この問題を解決しようと2025年9月に発足したのが **OSI(Open Semantic Interchange)** です。

Snowflake・Salesforce（Tableau）・dbt Labsなど競合関係にある企業が手を組んで「ビジネスデータの共通言語をつくる」という取り組みで、15社以上が参加しています。TableauのCPOはこれを「ビジネスデータのロゼッタストーン」と称しており、2026〜2027年にかけて主要ツールへの実装が進む見通しです。

## B. Salesforce社の動向

次いで、Tableauを買収したSalesforce社から見た動向、視点について見ていきます。

### B-1. 買収の歴史から見えてくる「一枚の設計図」

Salesforceの戦略を理解する最大のヒントは、ここ10年の大型買収の流れです。これは単なる規模拡大ではなく、はっきりとした「設計図」に沿っています。

| 年 | 買収先 | 金額 | 目的 |
| --- | --- | --- | --- |
| 2018年 | MuleSoft | 約65億ドル | システム間のAPI統合 |
| 2019年 | Tableau | 約157億ドル | データ可視化・分析 |
| 2020年 | Slack | 約277億ドル | 業務コミュニケーション |
| 2025年 | Informatica | 約80億ドル | データ統合・品質管理 |

2018〜2020年にかけて「繋ぐ(MuleSoft)」「見る(Tableau)」「話す(Slack)」の3つを揃え、2025年には「信頼できるデータ基盤(Informatica)」を加えました。

CEOのマーク・ベニオフ氏はInformatica買収完了時に「データと文脈こそがAgentforceの真の燃料。クリーンで信頼できるデータがなければ、AIは知性どころかハルシネーション(幻覚)しか生まない」と語っています。

### B-2. 「Agentic Enterprise」というビジョン

2024年9月にSalesforceは**Agentforce**を発表し、AIエージェントを企業全体に展開するプラットフォームとして打ち出しました。

2025年10月のDreamforce 2025ではさらに大きなビジョン 「Agentic Enterprise(エージェント型企業)」 を宣言しています。

> "We're entering the age of the Agentic Enterprise — where AI elevates human potential like never before."  
> — Marc Benioff, Chair and CEO, Salesforce  
> 「AIが人を置き換えるのではなく、AIが人を高めるエンタープライズ」  
> — マーク・ベニオフ

Agentforceは2024年10月の初版からわずか12ヶ月で4回のメジャーアップデートを経て「Agentforce 360」に到達。現在は以下の「4本柱」で構成される統合プラットフォームです。

| 柱 | 役割 |
| --- | --- |
| Agentforce 360 Platform | AIエージェントが動く実行基盤 |
| Data 360(旧 Data Cloud) | エージェントに文脈を与えるデータ層 |
| Customer 360 Apps | 業務アプリ群(Sales/Service/Marketing等) |
| Slack | 人とエージェントが対話する"窓口" |

これらが連携することで「データを読んで、判断して、業務システムに動きかける」AIエージェントが実現します。Salesforceは2030年までに年間売上600億ドルという目標を掲げており、この成長の主役がAgentforceです。

### B-3. AnthropicとのAI戦略的提携

SalesforceとAnthropicの関係は、よくある「AIツールのライセンス契約」ではありません。両者の関係は、**Salesforceのベンチャーファンドが2023年のSeries C(初期の資金調達ラウンド)から、Anthropicのほぼ全ラウンドに投資し続けてきた戦略的パートナーです。**

現在、Salesforceは年間約3億ドル分のAnthropicのAI処理(トークン)を消費しており、株式投資も3億ドルを超えています。連携は多岐にわたります。

AgentforceでClaudeが「推奨AIモデル」として採用されているほか、Slack上のAI機能もすべてClaudeが動かしています。さらに全Salesforceエンジニアが開発効率化のためにClaude Codeを利用するなど、技術から投資まで深く結びついた関係です。

### B-4. Slackが「AIの入口」に変わった

2020年に約277億ドルで買収されたSlackは、Salesforceグループの中でいま大きく変貌しています。**2026年3月31日、Slackに30以上のAI機能が一斉追加され、Slack買収以来最大規模のアップデートと評されました。**

最大の変化は**Slackbotの進化**です。かつてリマインダーや簡単な返答をするだけだったSlackbotが、「仕事のための個人AIエージェント」へと生まれ変わりました。しかもSlackbotはMCPクライアントとして機能するため、Slack上からTableau・Google Workspace・Microsoft 365・Notionなど外部ツールをAIで横断操作できます。

> "We see it as the future interface for work. Slack is where you can get the work done."  
> — Parker Harris, Co-founder and CTO, Salesforce  
> 「私たちはSlackbotを仕事の未来のインターフェースと見ている」  
> — Parker Harris（Salesforce共同創業者・Slack CTO）

**2026年夏以降は、新規Salesforceアカウントには自動的にSlackがプロビジョン（利用可能な状態で付与）される予定です。Salesforceを使い始めた瞬間から、AI対応のSlackも手に入る世界になります。**

## C. Tableau社の動向

そして3つめ、(Salesforceに買収された)Tableau社の動向です。いよいよ本題。

### C-1. 「Tableau」が2系統の製品を指すようになった

2025年に登場した**Tableau Next**によって、「Tableau」が2系統の製品を指すようになりました。Tableau公式(ヘルプ参照)はこう説明しています。

> "Tableau"という用語は、Salesforceのエコシステム内では"アナリティクス"を意味する一般語として使われるようになりました。

現在、Tableauブランドは大きく2系統の製品群を指しています。

* **Tableau by Tableau(従来からの製品群)**：
  + Desktop・Cloud・Server・Prep・Pulseなど、多くの方が「Tableau」と聞いてイメージする製品群です。引き続き開発・投資が続けられています。
* **Tableau Next(2025年登場の新製品)**：
  + Salesforceのクラウド基盤(Hyperforce)上に構築された新世代の分析プラットフォームで、AIエージェントとのネイティブ統合が特徴です。2025年6月にGA(一般提供開始)。既存製品の「置き換え」ではなく「追加の選択肢」です。

**この2系統は「移行」ではなく「併存」と明言されています。** 前CEO・Ryan Aytay氏はTC25でこう述べています。

> "The classic Tableau you know and love—Tableau Desktop, Tableau Cloud, Tableau Server, Tableau Prep, Tableau Public—that's not going anywhere. It's the bedrock of what we do, and it's deeply ingrained in our analytics solutions."  
> 皆が知っていて愛してきたDesktop、Cloud、Server、Prep、Public ― これらはどこにも行きません。

### C-2. Tableau Nextの核心 ― 「意味を定義する層」の登場

Tableau Nextで最も重要なのが **Tableau Semantics(タブローセマンティクス)** という仕組みです。

「セマンティクス」とは「意味」のこと。ひと言でいうと **「組織のデータにビジネスとしての意味を付与し、全社で統一管理する層」** です。

![](https://static.zenn.studio/user-upload/fdd26a120024-20260528.png)  
*[先日投稿したブログ](https://zenn.dev/truestar/articles/a514adfdf2f5e3)での構成図におけるこの部分ですね*

なぜ重要なのか。「売上」という言葉ひとつとっても、請求・入金・受注ベースと部門によって定義が異なることはよくあります。AIが複数のデータソースをまたいで分析しようとすると、この「意味のズレ」が致命的な誤りにつながります。Tableau Semanticsはこの問題を解決するために定義を組織全体で一元化し、AIが正しい文脈でデータを理解できるようにします。

重要なのは、Tableau SemanticsはTableau Next専用ではないという点です。Tableau CloudやTableau Serverからも接続できるよう拡張されており、**既存のTableauユーザーもその恩恵を受けられる構造になっています。**

さらに2026年5月のTC26で発表された Auto Knowledge Graph(2026年7月GA予定)は、この仕組みをさらに進化させたものです。データから自動的にナレッジグラフを構築し、「組織が実際に使っている言葉」を学習・整理する機能で、後述する会話型分析(Conversational Analytics)の裏側エンジンとして機能します。

#### Tableau Nextの3つのAIスキル

Tableau Nextには「Agentforce Tableau」と呼ばれる3つのAIスキルが搭載されています。これらはAgentforceというAIプラットフォームの上で動く「分析専門のエージェント」として機能します。

| スキル名 | 説明 |
| --- | --- |
| **Concierge (コンシェルジュ)** | 自然言語で質問すると、信頼できる回答＋可視化＋次のアクション提案 を返してくれる |
| **Data Pro (データプロ)** | データ準備やモデリングを支援 「このデータとあのデータをつなぐべき」という提案や 計算フィールドの自動生成など |
| **Inspector (インスペクター)** | データをリアルタイムで監視し、異常やトレンドを 自律的に検知してアラートを出す |

たとえば「先月の売上が急落した原因を調べて」と話しかけると、ConciergeがTableau Semanticsの定義に基づいて回答を生成し、根拠となるグラフも提示してくれる、といったイメージです。

### C-3. Tableau MCP ― どのAIからでもTableauにつながる「窓口」

2026年5月のTableau Conference 2026(TC26)で最も注目された発表が、**Tableau MCPの正式リリース(GA)** です。

Tableau MCPとは、Claude・ChatGPT・GeminiなどのAIツールから、Tableauのデータへ直接アクセスできる「接続口(MCPサーバー)」です。公式GitHubで提供されており、接続すると具体的には次のことが可能になります。

* 「先月の売上を部門別に見せて」と話しかけるだけでTableauのデータから回答が返ってくる
* ワークブック・データソース・ビューの一覧取得や検索
* グラフや可視化画像のダウンロード
* 音声(MCP Voice)でのデータ問い合わせ(TC26で発表)

TC26ではこのTableau MCPが 「universal translator(万能翻訳機)」 と命名されました。キーノートの背景スクリーンにはClaude・ChatGPT・Geminiのロゴが並んで表示され、「どのAIからでもTableauに接続できる」という方向への明確な宣言となっています。

#### Tableau NextとTableau MCPの違い

Tableau MCPは既存のTableau Cloud/Serverに外部AIから接続するための公式の窓口で、Tableau NextのAIスキルはTableau Next製品に内蔵されたAIエージェント機能です。つまりTableau MCPは「Tableau Nextに移行しなくても使える」もの。現在お使いのCloud/ServerにMCPを設定するだけで、ClaudeやChatGPTから既存環境に接続できます。

Salesforceの公式Summer'26リリースにも「Tableau MCPは、あなたのAIを信頼できるデータエキスパートに変える」と明記されており、TableauだけでなくSalesforceプラットフォーム全体の公式AI連携機能として位置づけられています。

### C-4. TC26が示した戦略の大転換 ― 「内向き」から「外向き」へ

2026年5月5〜7日に開催されたTableau Conference 2026(TC26)は、Tableauの転換点となるイベントでした。新GM・Mark Recher氏はこう宣言しています。

> "For more than 20 years, Tableau has defined how the world sees and understands data. But we've reached a turning point — seeing the truth is no longer enough. Organizations need to act on it instantly."  
> (20年以上にわたり、Tableauは世界がデータをどう見て理解するかを定義してきました。しかしいま転換点を迎えています ― 真実を「見る」だけでは、もはや不十分です。組織は瞬時に行動する必要があります。)

#### 前年(TC25)との最大の違い：全製品のAgentic化

2025年のTC25では「Tableau Next」という新製品だけがAI対応で、既存ユーザーへの恩恵は限定的でした。しかしTC26ではTableau Cloud・Server・Desktop・Nextのすべてに、AIエージェント機能(Agentic capabilities)が拡張されました。新製品に乗り換えなくても、既存のTableauユーザーがAI分析の恩恵を受けられる構造への転換です。

そしてもう一つの大きな変化が、外部AIへの「開放」です。TC25まではTableau SemanticsとAgentforceだけで完結する「内向き」の設計でしたが、TC26ではClaude・ChatGPT・Geminiなどの外部AIとの接続を公式に推奨する「外向き」へと大きくピボットしました。この姿勢の変化は、Tableau MCPのGA(正式リリース)によって具体的な形になっています。

#### TC26で発表された主な新機能

* **Conversational Analytics(会話型分析)**：
  + 既存のTableau Cloud/ServerでGA済み。自然言語でデータに質問すると、アナリストが定義した関係性に基づいてインサイトを返してくれます。LLMで動きながら、データに根ざした回答を担保しています。
* **Knowledge Engine(2026年6月GA予定)**：
  + Tableauの新しい中核コンポーネント。Tableauコミュニティが10年以上かけて構築した「3,300万のセマンティックモデル」を基盤にAIエージェントに信頼できるビジネス文脈を提供します。Recher氏は「ビジネスの文脈を真に理解する知識なしにagentic analyticsは提供できない」と述べています。
* **Agentified Actions(ベータ)**：
  + これまでTableauは「データを見せる」ツールでしたが、CRM・ERP・在庫システムなど実際の業務システムに接続してアクションを実行できるようになります。「Auto Mode」ではエージェントが自律的にデータを監視して業務アクションまで実行します(人間の承認ステップも設定可能)。まさにAgentic Analyticsの中核をなす機能です。
* **Agent Health Monitor/Agentic Command Center(秋GA予定)**：

### C-5. 既存ユーザーへの実質的な影響

「いまTableauを使っているが、何が変わるのか」という疑問について、ここで幾つか整理します。

| 疑問 | Tableauの回答・方針 |
| --- | --- |
| Tableau Nextに移行しないといけない？ | いいえ。既存製品への投資は継続。 Nextは追加の選択肢 |
| Data 360(旧Data Cloud)は必須？ | Tableau Nextなら必要。 既存製品は従来通り |
| AI機能はいつ使える？ | TC26以降、既存のCloud/Serverでも 順次提供中 |
| Tableau MCPはすぐ使える？ | 2026年5月GA済み。 現時点はセルフホスト設定が必要 |
| ライセンスはどう変わる？ | 「Tableau+」という最上位バンドルが登場。 Tableau Next含む |

## まとめ

という訳で世の中/Salesforce社/Tableau社それぞれの情報、動向を整理してみたエントリでした。ここまでの内容を更に要約すると概ね以下となります。

* **A. 世の中（データの世界）的な動向**
  + AIは「答える」から「自律的に動く」へ進化し、データ分析も「人がダッシュボードを見て判断する」時代から「AIエージェントが自律的に動く」Agentic Analyticsの時代へシフトしている
  + この変化を支える技術標準として、AIとツールを繋ぐ「MCP」と、データの意味を業界横断で統一する「OSI」が急速に整備されつつある
  + 主要BIベンダー各社は単体ツールの競争から「データ基盤＋分析＋AI」一体のエコシステム競争へ一斉に舵を切っており、「どのツールが優れているか」ではなく「どのエコシステムを選ぶか」が問われる時代になっている
* **B. Salesforce社の動向**
  + 10年かけた大型買収(MuleSoft・Tableau・Slack・Informatica)で「繋ぐ・見る・話す・信頼する」を揃え、AIと人が協働する「Agentic Enterprise」をビジョンに掲げている
  + その実行基盤がAgentforce 360で、データ層・業務アプリ・AIエージェント・Slackが一体となって動く統合プラットフォーム
  + AnthropicとはAIライセンスを超えた資本・技術両面での戦略的パートナーシップを構築しており、SlackはAIエージェントへの「入口」として大幅に進化している
* **C. Tableau社の動向**
  + 新製品「Tableau Next」と従来の「Tableau by Tableau(Desktop・Cloud・Server等)」は「移行ではなく併存」であり、既存ユーザーが急いで乗り換える必要はない
  + 2026年5月のTC26では全製品にAIエージェント機能が拡張され、ClaudeやChatGPTなど外部AIからTableauへ直接接続できる「Tableau MCP」が正式リリースされた
  + Tableauは「人がダッシュボードを見るツール」から「AIエージェントが信頼できるデータを理解して動くための知識エンジン」へ、その役割を根本から再定義しようとしている

Tableau MCP界隈の情報整理を行うべく[先日投稿したエントリ](https://zenn.dev/truestar/articles/a514adfdf2f5e3)と合わせて全体概況的な情報を今回のエントリでも試みてみたのですが、個人的にもだいぶすっきり整理されてきた気がします。引き続き、実装検証の前段で整理、理解し直しが必要なトピックについては採り上げて行こうと思います。

---

## この記事を読んだ方へ

感想・フィードバックは X（[@shinyaa31](https://x.com/shinyaa31)）までお気軽にどうぞ。
