---
id: "2026-06-03-snowflake-summit-2026-platform-keynote-まとめ-01"
title: "【Snowflake Summit 2026】 Platform Keynote まとめ"
url: "https://zenn.dev/finatext/articles/snowflake-summit-2026-platform-keynote"
source: "zenn"
category: "cowork"
tags: ["MCP", "AI-agent", "LLM", "cowork", "zenn"]
date_published: "2026-06-03"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは！ナウキャストのけびんと[庵原](https://zenn.dev/lana2548)です。今年も Snowflake Summit に参加してきました！今回は2人で Platform Keynote のレポートをお届けします。

2026年6月2日の朝、サンフランシスコで開催された Snowflake Summit のメインイベント、Platform Keynote が実施されました。Keynote は EVP of Product を務める Christian Kleinerman が主に進行し、「4つの幕（4 Acts）」という構成で新機能が紹介されました。それぞれの Act には独立したテーマとメッセージがあり、全体としてひとつの大きな物語を形成しています。本記事でもこの構成に沿って、各 Act のメッセージと注目の機能をお伝えします。

## Snowflake のアーキテクチャ哲学

今年の Keynote を語る前に、Snowflake という会社が何を大切にしてきたのかをあらためて振り返っておきたいと思います。各 Act の発表の意味がより深く伝わるはずです。

2012年、Michael Stonebraker らが直面したのは「データウェアハウスの設計が根本的に壊れている」という事実でした。当時のシステムが抱えていた問題は大きく2つでした。ひとつは**サイロの存在**。構造化データは従来型ウェアハウスに閉じ込められ、ストリーミングデータは別システムへ。単一クラスターの容量が上限に達した瞬間、また新しいサイロが生まれる悪循環です。もうひとつは**ガバナンスの困難さ**。データが複数システムに散在すると、一元的なガバナンスはほぼ不可能でした。

この問題を根本から解決するため、Snowflake は **3 つの設計原則** を掲げてプラットフォームを作り上げました。

1. **すべてのデータを1か所へ** — 構造化・半構造化データをシームレスにクエリできる単一ストレージ層
2. **ストレージとコンピュートの完全分離** — ワークロード干渉を排除し、コンピュートを独立してスケール可能に
3. **ゼロメンテナンス** — あらゆるユーザーに対して「ただ動く」フルマネージド体験

2016年、Snowflake はデータ管理の権威ある国際学会 SIGMOD に[この設計思想を論文](https://www.snowflake.com/resource/sigmod-2016-paper-snowflake-elastic-data-warehouse/)として発表しました。その論文は後に **Test of Time Award** を受賞し、ACM SIGMOD はこう評しています。

> Snowflake's profound influence on the research community shaped the design of modern cloud data systems and driving innovations adopted by millions of users today."  
> 「Snowflake が研究コミュニティに与えた深遠な影響は、現代のクラウドデータシステムの設計を形成し、今日何百万人もの人々に採用されているイノベーションを牽引してきた。」

![acm-sigmod](https://static.zenn.studio/user-upload/deployed-images/c240ef261962927926f2c94a.jpg?sha=3a32cdc59c84a4c143306a26f3917c0eba087cff)

その後も Snowflake は「サイロの解消」という原点を起点に進化し続けます。地理的境界を超えたクロスクラウド・クロスリージョンへの展開、オープンフォーマット（Apache Iceberg）の積極的な採用、非構造化データ（ドキュメント・音声・画像・動画）のネイティブサポートへと、一貫してデータの民主化を推し進めてきました。

そして 2026 年の今、AI エージェントの時代に Snowflake が改めて示したのは、ひとつの確信です。

> "The world's best AI agents must be powered by the world's best data platform."  
> 「世界最高の AI エージェントは、世界最高のデータプラットフォームの上に構築されなければならない。」

AI と Data が同一プラットフォームに統合されることで、初めてスマートで高速なエージェントが実現する、この信念は Keynote 全体で表れていました。

## 今回の Keynote で感じたこと

今年の Platform Keynote を一言で表すなら、「**エージェント時代への本格的な回答**」です。

昨年・一昨年の Summit でも AI や LLM の活用は大きなテーマでしたが、どこか「これから何ができるか（Can we?）」という問いが漂っていました。今年は違いました。Samsung が Galaxy S26 のグローバル同時発売をリアルタイムで管理し、Thomson Reuters が 100 万人以上のプロフェッショナルに受託者責任レベルの AI アドバイザーを提供し、Under Armour がリアルタイムの会話型 AI でリーダーの意思決定を加速している——これらはすべて**稼働中の事例**として紹介されています。「実証段階」ではなく「業務の標準」として AI が機能している姿が、今年はっきり見えました。

特に印象的だったのは、今年の発表が「AI をどう使うか」だけでなく、「ヒトから信頼されるデータ・AIプラットフォームをどう作るか」という問いにも真剣に向き合っていた点です。エージェントが組織内を自律的に動き回る時代には、「どのエージェントが何をしたか」を把握し、「エージェントでも単独では越えられない一線」を設ける設計が不可欠です。今年の Keynote はその答えを、セキュリティとガバナンスの具体的な機能群として提示していました。

4 つの Act はそれぞれ独立したテーマを持ちながら、ひとつの大きな物語の章立てをなしています。摩擦を取り除き（Act 1）、信頼の基盤を固め（Act 2）、データを解放し（Act 3）、あらゆる人に知性を届ける（Act 4）。この流れが Snowflake の 2026 年のビジョンです。

## Act 1: Erasure of Friction / 摩擦の解消

> "We are the frictional elimination business. If anything you do, you encounter friction, we want us to help you."  
> 「私たちは摩擦を取り除くビジネスをしています。あなたがやることに摩擦を感じたとき、私たちが手助けしたいのです。」

Act 1 のメッセージは明快でした。本来やりたいことである「価値の創出」ではなく、そのための準備や手続きに時間を取られてしまう。それが「摩擦」です。Snowflake はこれを、AI によって徹底的に取り除いていくと宣言しました。その中核を担うのが **CoCo** と **Cowork** です。

### CoCo / Cowork へリネーム

"Cortex Code" として知られていた AI コーディングエージェントが **CoCo** に、そして Snowflake Intelligence は **Cowork** に名称が変更になりました。

![coco-rename](https://static.zenn.studio/user-upload/deployed-images/8e8e5f7be70bc3105cee0013.jpg?sha=59f59f9660e008ce2cfc3ac3494ae6c9aaba86f4)

CoCo は Snowsight と CLI そしてデスクトップアプリのそれぞれから利用可能で、MCP（Model Context Protocol）サポート、ローカル開発環境とのサンドボックス統合、スケジュール自動化、そして共有・再利用可能なスキルカタログなどが揃いました。

CoCo は単なる「コーディング補助」にとどまらず、データパイプラインの診断・修復から SQL の最適化、アプリケーションのビルドまで、**データエンジニアリングやデータ分析の全工程を自然言語でドライブするエージェント**として位置づけられています。「今まで数時間かかっていた作業が数分で終わる」という体験が、すでに多くの組織で現実になっています。

![coco-image](https://static.zenn.studio/user-upload/deployed-images/d002144a3d282deb150a5872.jpg?sha=2558336703e713e2ed92e2dc5a91e96f2d46dac1)  
*CoCo in Snowsight で SiS アプリの問題の調査をしているデモの様子*

### Snowflake Datastreams の発表

これまで Kafka や Confluent など外部のストリーミング基盤を別途用意・管理してきたユーザーにとって、特に大きなニュースです。**Snowflake Datastreams** は Kafka 互換のフルマネージドストリーミングサービスで、Snowflake にネイティブ統合されています。ストレージとコンピュートの分離設計はそのままに、**1秒以下の低遅延**でのデータ取り込みが可能になりました。既存の Kafka クライアントやアプリケーションをそのまま接続できる互換性を保ちながら、ストリーミング基盤の運用コスト・複雑さを丸ごと Snowflake に委ねられます。「Snowflake を中心にすべてのデータフローを統合できる」というビジョンが、いよいよ現実のものとなります。

## Act 2: The Bastion of Trust / 信頼の砦

> "Trust and governance comes together through the Horizon."  
> 「信頼とガバナンスは、Horizon を通じてひとつになります。」

Act 2 のキーワードは **「要塞（Bastion）」** です。信頼は自然に生まれるものではなく、意図的に設計・構築・維持するものだという姿勢が、このセクション全体を貫いていました。エージェントが組織内を自律的に動き回る AI の時代に、セキュリティとガバナンスをプラットフォームの中核に「要塞のように」組み込むことが示されました。

### Agent Identity

エージェント時代の新たな課題として「**誰がこの操作をしたのか**」の追跡と制御があります。従来のアクティビティログは人間のユーザーを前提に設計されていましたが、**Agent Identity** により「これはエージェントによる操作である」と識別できるようになります。さらに重要なのは、マスキングポリシーや行レベルセキュリティに「エージェントによる操作であれば制限を強化/緩和する」という条件を書けるようになった点です。人間には閲覧を許可しているデータをエージェントには隠す、あるいはその逆の制御を、ポリシーとして宣言的に管理できます。「エージェントを信頼するが、信頼の範囲は人間と同一ではない」という AI Security の実務ニーズに正面から応える機能です。

![agent-identity](https://static.zenn.studio/user-upload/deployed-images/6740cfe6840d7ceebf1831c1.jpg?sha=c9d68eb529b7ab341be8eca8c9426fedc1991983)  
*`is_agent_activated` により、エージェントによる実行かどうかが判別可能に。*

### Multi-Party Approvals

管理者権限を持っていても、あるいは強力なエージェントであっても、**単独では実行できない操作**を設定できる仕組みが **Multi-Party Approvals** です。たとえば「監査ログの無効化」「最高権限の付与」のような高感度操作には、二者承認を必須化できます。内部不正やエージェントの意図しない動作に対する防衛策として、「2人の Admin が同意しない限り実行不能」というガードレールを設けられます。単純なロールベースアクセス制御では守りきれなかった「高権限ユーザーによるミスや悪用」に対して、プロセスレベルで応えるものです。

![mpa](https://static.zenn.studio/user-upload/deployed-images/9cd646968998cfbd29297fd6.jpg?sha=9f7ea199e84d74bdb1f0acadb9021710b10461a0)

詳細はこちらもご覧ください。  
<https://www.snowflake.com/en/blog/enterprise-ai-security/>

### Horizon Context

AI エージェントの回答精度は、与えられるコンテキストの質に依存します。**Horizon Context** は、Snowflake の Horizon Catalog 上に蓄積されたメタデータを CoCo や Cortex Agent に供給する仕組みです。ここでのメタデータには、データリネージュ、利用頻度、説明文、タグ、セマンティックビュー、ビジネス用語などが含まれます。 BI ツールや他の DB からのメタデータコネクタも統合されており、エージェントは「会社の業務文脈を理解した上で」回答を生成できるようになります。今まで「エージェントが業務文脈を知らず的外れな回答をする」という課題を抱えていた組織には、根本的なアップグレードになるはずです。

![horizon-context-1](https://static.zenn.studio/user-upload/deployed-images/b2977bad744dc793f8d8f79d.jpg?sha=4c300f3983bf8fcfec5530d4ca77c141f1915a37)  
*Snowflake全体における Horizon Context の立ち位置*

![horizon-context-2](https://static.zenn.studio/user-upload/deployed-images/027763a8326f08ac819f3e03.jpg?sha=26a931374795e5e84bb8e731a544af04268e028c)  
*別のセッションで紹介されていた Horizon Context の概要*

### Cost Governance

AI・エージェントのワークロードが増えるにつれ、コストの予測・管理はより難しくなります。そこで今回、単なる可視化にとどまらないアクションまで含めたコストガバナンスの仕組みが整備されました。ユーザー単位で使用量の上限を設定するユーザークォータ、AI系サービスのコスト管理、組織レベルでのコスト管理、といった機能が新しく紹介されました。さらに予算のカスタムアクションにより、閾値に達したタイミングでストアドプロシージャの実行や通知を自動でトリガーできます。これらの機能拡充によって、柔軟なコスト管理が可能になります。

![cost-governance](https://static.zenn.studio/user-upload/deployed-images/30b8d3e318b0cc9a9677a462.jpg?sha=0490d969ac1117536f60d286af14dee37fe4577b)

## Act 3: The Liberation of Data / データの解放

> "We are very committed to helping you access your data... open and interoperable."  
> 「私たちは、あなたのデータへのアクセスを支援することに全力を尽くしています。オープンで相互運用可能な形で。」

Act 3 のテーマはデータの「解放」です。特定のベンダーやプラットフォームにロックインされることなく、データを自由に使えるようにするというコミットメントです。Snowflake はここ数年、Apache Iceberg の推進、Open Semantic Interchange Group の設立など、「オープン性と相互運用性」を戦略の中心に据えています。

「私たちは Apache Iceberg の仕様策定に主導的に参加しており、外部カタログ・エンジンとの**双方向サポートを提供できる唯一のベンダー**だ」というSnowflakeの自信は、創業時から一貫してきた「サイロを作らない」という約束を今度はエコシステム全体のレベルで実現しようとする宣言でした。

### Multi-Party Collaborationの一般公開

これまで「複数の組織がデータを持ち寄って共同分析したい」というニーズには、一方の組織にデータを送るか、高コストな専用インフラを用意するしかありませんでした。**Multi-Party Collaboration** が 一般公開になったことで、複数の組織が単一のセキュアな環境に参加し、それぞれのデータを外部に出すことなく共同分析できるようになります。「データを提供する側」「分析を実行する側」など異なるロールを同一環境内で割り当てられるこの仕組みは、広告効果測定や金融リスク分析、医療データの産学連携など、業界横断のコラボレーションを根本から変える可能性を持っています。創業時から技術的な下地を積み上げてきたクリーンルーム技術が、ここにも活かされました。

### Zero-Copy パートナーシップの拡大

**Zero-Copy パートナーシップ** は、外部アプリケーション内のデータを Snowflake にコピーすることなく直接連携できる仕組みです。今年は既存の Salesforce に加え、**Workday**（HR データ）が Private Previewに、そして最も多くのリクエストを受けていた **SAP**（ERP データ）が GA になりました。基幹システムのデータをコピー・変換なしで Snowflake の AI・分析基盤から直接活用できることで、「データ連携コスト」と「データの鮮度」という長年のトレードオフが解消されます。

![zero-copy](https://static.zenn.studio/user-upload/deployed-images/2e4f8aac651f6c14983cd7a2.jpg?sha=068a2b23024ad14c54545b2bf802514e6c71aaa1)

## Act 4: Omnipresence of Intelligence / 知性の普遍化

> "We are in the age of ubiquitous intelligence. Each of us can have the power of a data scientist, analyst, and statistician." ——Christian Kleinerman  
> 「私たちは知性が遍在する時代にいます。私たち一人ひとりが、データサイエンティスト・アナリスト・統計家の力を持てるのです。」

Act 4 が描くのは「**誰でも自分専用のアナリストを持てる世界**」です。これまでデータ分析は「データチームに依頼して待つ」ものでした。そのモデルが根本から変わりつつあります。

F1 チームには専任ピットクルーがいます。アイアンマンには Jarvis がいます。CEO だけでなく、現場のフロントライン担当者ひとりひとりが自分専用に最適化されたエージェントを持ち、効率的に業務をこなす。これが Act 4 の機能で Snowflake が目指す世界です。

### Personal Work Agent の発表

**Personal Work Agent** は、Snowflake Cowork（エンタープライズ向けエージェント基盤）が「個人に最適化された」形で進化したものです。今まではどのエージェントを使うかをユーザーが選ぶ必要がありました。Personal Work Agent ではその選択が不要になり、**「何をしたいか」を言うだけ**でよくなります。内部では複数のエージェントがオーケストレーションされ、ユーザーの行動・好みを学習する **User Memory** によって回答がパーソナライズされていきます。個人スキル・個人 MCP コネクタ・スケジュールタスクも設定可能で、「毎朝 6 時にメールで一日のブリーフィングを届ける」ような自律的な働き方を支援します。「どのエージェントを使うか」という認知負荷から解放され、「何をしたいか」だけに集中できる体験への転換という点が大きな進化です。

![cowork-1](https://static.zenn.studio/user-upload/deployed-images/0e14f17296a5427eea18f4f8.jpg?sha=bcfc283f6466a55e128150a67dc08a09ccb70695)  
![cowork-2](https://static.zenn.studio/user-upload/deployed-images/5630ae1b8e3f2c5f54fb9111.jpg?sha=93cc778d840e9b40e5a12be2f9cb5a2ded412731)

### Cortex Sense

どれだけ優れた AI エージェントでも、コンテキストが不十分では的外れな回答しか返せません。**Cortex Sense** は、Snowflake 上のデータと活動シグナル（誰がどのデータにアクセスしたか、どのアーティファクトが活用されているか、など）を自動的に収集・分析し、エージェントのコンテキストを**継続的に強化**する仕組みです。エージェントの精度問題は「プロンプトエンジニアリング」だけで解決するものではなく、プラットフォームレベルの**コンテキスト強化**が鍵だということが示されています。

![cortex-sense-1](https://static.zenn.studio/user-upload/deployed-images/4bf7809aa0d08a8fa2261704.jpg?sha=f5c1098111a7a3d39224115e91688b95b4d733df)

![cortex-sense-2](https://static.zenn.studio/user-upload/deployed-images/89cfd71c438a51098f1fcad1.jpg?sha=4aefe881037b87c866990f99cfc69d617ee2cf67)

### MCP Gateway / Natoma

エージェントが組織全体に遍在するためには、社内の業務システムとの安全に接続するための基盤が不可欠です。Snowflake は MCP ガバナンスプラットフォームの **Natoma** を買収し、CoCo や Cowork から Salesforce・Workday・ServiceNow など 100 以上のビジネスシステムに対して、エージェント ID 管理・ポリシー制御・監査ログを備えたエンタープライズグレードの接続を実現します。

![natoma](https://static.zenn.studio/user-upload/deployed-images/c6696ef053701c4ba0006fcd.jpg?sha=3414c36b3696343a3095676b03504fb4cb9bd66a)

## まとめ: "Can we?" から "Shall we?" へ

4 つの Act を振り返ってみましょう。

* **Act 1 Erasure of Friction** — CoCo / Cowork / Snowflake Datastreams / Agentic Search などにより、データを使うためのあらゆる摩擦を AI と自動化で取り除く
* **Act 2 The Bastion of Trust** — AI Security や Horizon Context により、AI エージェントが飛び回る時代のガバナンスを要塞のように強固にする
* **Act 3 The Liberation of Data** — Multi-Party Collaboration や Zero-Copy パートナーシップの拡大で、データをサイロから解放しオープンなコラボレーションを実現する
* **Act 4 Omnipresence of Intelligence** — Personal Work Agent と Cortex Sense により、データ分析の力を組織のすべての人に届ける

Keynote の最後、Christian はこう締めくくりました。

> "Snowflake takes it from the era of 'Can we?' to 'Shall we?'"  
> 「Snowflake は、"できるのか？" という時代から "さあ、やろうか" という時代へと連れて行きます。」

「技術的に可能かどうか」を問う時代は終わりました。今問うべきは「**それをやるかどうか**」です。Snowflake Summit 2026 のメッセージを受け取り、ぜひ皆さんの組織でも「Shall we?」と問い直してみていただければ嬉しいです！最後まで読んでいただきありがとうございました！
