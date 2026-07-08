---
id: "2026-07-08-aws-summit-japan-2026現地報告aiエージェントの成熟とphysical-aiの萌-01"
title: "AWS Summit Japan 2026現地報告：AIエージェントの成熟とPhysical AIの萌芽"
url: "https://zenn.dev/exwzd/articles/20260701_aws_summit_builders_fair"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "AI-agent", "LLM", "GPT", "cowork", "zenn"]
date_published: "2026-07-08"
date_collected: "2026-07-09"
summary_by: "auto-rss"
query: ""
---

先端技術開発グループ（WAND）の小島です。2026年6月に幕張メッセで開催された[AWS Summit Japan](https://aws.amazon.com/jp/events/summits/japan/)にWANDのメンバーで参加してきたので、Builders' Fairを中心に現地参加報告を書いていきます。

## AWS Builders' Fair

昨年は、[現地のデモ展示などを行っている「Builders' Fair」を中心にレポートしましたが](https://zenn.dev/exwzd/articles/20250715_aws_summit_builders_fair)、Summitはこのエリアが楽しいので、今年も同様に見てきました。

![](https://static.zenn.studio/user-upload/deployed-images/5db16f615e5e949295f63c23.jpg?sha=8b87232282a0c718f101bbc992a0656cd1e0b72a)

このエリアは、「開発者の心をくすぐる」をテーマに、AWSの方が作ったデモアプリを展示しており、その場で自由に質疑応答できます。レベルが高く、そのまま使えそうなものも多数あります。

セッション類はあとからアーカイブ配信がありますが、このエリアはデモアプリを用いたインタラクティブコンテンツであるため、現地でしか体験できない内容となります。昨年と今年でトレンドが変わっており、その違いを見るのも面白いです。

## 昨年と今年のトレンドの違い

昨年は、「**生成AIの台頭**」と「**AIエージェントの萌芽**」という印象で、AIエージェントで作ってみた系のものが多数ありました。

今年は、AIエージェントは引き続きあるものの、**Bedrock AgentCoreの確立などもあり、それがより成熟し、エンタープライズ用途で使えそうな**感じになってきました（Amazon Quickなど）。

デモアプリでは「**Physical AI**」への注目が高まっており、**ロボットに何かをさせるものが増えたのが今年のトレンド**です。以前からロボットの展示はいくつかありましたが、それらが「Physical AI」というパワーワードでまとめられているのが今年の特徴でした。

![](https://static.zenn.studio/user-upload/deployed-images/d7c2ae5846fd75c6be97820e.jpg?sha=4ecad0094e907085ab1164d96f4a5aab41b1bbcf)

また、VLA（Vision-Language-Action）モデルを使った近年注目のPhysical AIだけでなく、古くからあるIoT Coreを使ったカメラAIや、OpenCVによるロボット処理に生成AIを組み合わせたものなども、一括りにPhysical AIとされており、ビッグウェーブに乗ろうとする雰囲気が各所で感じられる展示となっています。

## Builders' Fairのアプリたち

それでは各アプリを個別に見ていきます。時間の関係で見られなかったものもいくつかありますが、ご了承ください。

### クラウドVLAが操るミニロボたち

![](https://static.zenn.studio/user-upload/deployed-images/e602e54b1a78d85e1c145f20.jpg?sha=bfa5559532c34d1bbbfd0a8cbd93397d8484e969)

![](https://static.zenn.studio/user-upload/deployed-images/70047f0ac9684ec729c8f27a.jpg?sha=8f0bf5a4d307d073fa3fd30ad855b764926fa0b7)

<https://aws.amazon.com/jp/builders-flash/202606/control-robots-vla/>

<https://aws.amazon.com/jp/blogs/news/aws-summit-japan-2026-aws-iot-servies-booths/>

詳細は上記のAWSのページで紹介されていますが、俯瞰カメラからオブジェクトを読み取り、最適な経路計算を実況風に（右モニター）見せるというものです。**経路計算は「CBS Solver」で行い、その結果をBedrockで臨場感たっぷりに演出**しています。ソルバーの計算結果を、**あたかも考えているように見せる組み合わせが面白い**です。

下のボードにあるオブジェクトの位置を手で変えると、経路を再計算します。ボードが格子状になっていたので、オブジェクトの認識は物体検出などの古くからある画像処理ではないかと思います。

アーキテクチャもIoT Greengrass + IoT Coreという古くからのパターンですが、エッジ側にStrands Agentが入っており、ここからクラウドのBedrockをコールしている点が今風と言えるでしょう。

### ペン字見ます！AI Agent 先生の辛口評価

![](https://static.zenn.studio/user-upload/deployed-images/0dbee27eebe4cd9727ec4288.jpg?sha=9c6a106f0135db52058acc4c0e5f98be179bfaf5)

![](https://static.zenn.studio/user-upload/deployed-images/0f0e21fc82410039071d1aad.jpg?sha=c1512c58f1ef8777944dd1b7cf597d68b0318511)

これは自分が書いた字をAIエージェントが評価してくれるものです。例えば2枚目の左上のように「上下左右」を紙に書いてカメラで撮影すると、辛口・バランス型・甘口の3人の先生（エージェント）が対話形式で評価してくれます。

![](https://static.zenn.studio/user-upload/deployed-images/a3563e672fba4810a6921189.jpg?sha=75a7b4eda088c0e1778e1cf4450bf89c57ca44d4)

興味深い点は2つあります。**1点目はマルチエージェントのユースケースになっていること**です。少し前まで、マルチエージェントの採択理由は「なんとなくかっこいいから」というふわっとしたものが多かった気がします。このケースでは、各先生にペルソナ（甘口・辛口）を持たせ、シングルではなくマルチエージェントにすることで、**より自然な会話にするという具体的なメリット**が見えています。

マルチエージェントが登場する前は、LLMに役割を演じさせるためにペルソナベースでファインチューニングするという方法がありました。それ自体の有用性は残りつつも、手軽さという観点ではBedrock AgentCoreを用いたマルチエージェントのほうが便利です。AgentCoreという足回りが整備されてきたおかげでしょう。

**2点目は、ストローク抽出モデルを作っていること**です。実はこのモデル、単に漢字を抽出してVLM（Vision Language Model）に食わせているだけではありません。**別途ストローク（漢字の一画一画）を抽出するモデルを訓練し、漢字全体の画像とストローク単位のパッチを両方与えてエージェントに会話させています**。ストローク抽出は物体検出などで実現できますが、手書き漢字だとOSSで公開されているものは少なそうで、作るのが結構大変なモデルだと思います。この下回りの技術的な工夫には（着目する人はあまり多くないですが）感心しました。

あとは、AWS Lambda Durable Functionsという最新の技術を使っている点でしょうか。これはAIエージェントと相性が良いそうです。AgentCore Memoryは採点結果のフォローアップ問い合わせ用に置いているとのことでした。

### AIパワポカラオケ

![](https://static.zenn.studio/user-upload/deployed-images/122df3f8f208a27280389da8.jpg?sha=8b6875bfa42e57f3895fdbdeaf5a57bda0a87dd5)

![](https://static.zenn.studio/user-upload/deployed-images/af3ce34caf329ba8490ca314.jpg?sha=4cb92f827f2158a8a591b5c1d092e8b917040a74)

Amazon Quickを使ったスライド作成の紹介です。単なる資料作成ではなく、**ランダムに選んだお題からAIがその場でスライドとトランスクリプトを作り、人間がカラオケ方式でLTを行う**というものです。

Amazon Quick自体がかなり興味深かったです。QuickというとどうしてもBIツールのQuickSightのイメージがありますが、それは古い名前で、現在はQuickとして統合されています。Quickでは今風の（ChatGPTやClaudeのような）チャットベースのUIが前面に出ており、**資料作成からデータ分析、ダッシュボード作成まで同一プラットフォーム上でできる**のが面白いです。

また、エンプラ向けの機能も強化されており、Claude CodeやCoworkとどの程度違うのかは気になるところです。おそらくCoworkを意識しているのか、Quickにはデスクトップ版もあり、ローカルファイルをどの程度安全に使えるのかは今後注目されそうです。

### Spatial Agent：空間を理解する次世代Agentic RAG

![](https://static.zenn.studio/user-upload/deployed-images/748f509eecd73f262c9bf076.jpg?sha=8e1e0205b7c6eaa044a580ddcbbd8af11e0ed156)

ゲーム業界のQAの仕組みを最新の生成AIと組み合わせて再現したもので、壁抜けや表示欠けなどのバグ検知を目的としています。3Dゲーム空間を動く自動操作プレイヤー（AI）から観測情報を抽出してデータベースに保存し、「バグの検出状況を教えてください」などと自然言語で問い合わせます。また、自動操作AIへの「3D空間に散らばったアイコンから指示されたものを探し出せ」といった探索ポリシーも自然言語で指定できます。

![](https://static.zenn.studio/user-upload/deployed-images/4ec8c0d6c8ed42675088aa1a.png?sha=ad229993b6982103120cfd7b70205640229fef35)

![](https://static.zenn.studio/user-upload/deployed-images/f4f6024908bb8119f5544fbe.png?sha=e5523047b17053c1f448e6bb348d27ac91adabe9)  
*公開資料：<https://pages.awscloud.com/rs/112-TZM-766/images/AWS-Summit-Japan-2026_A090_2.pdf> より*

一見すると、AIの視覚情報から世界情報を取ってくる、つまりSfM（Structure from Motion）的なことをやっているのかなと思うのですが、**実は画像情報を一切使っていない**そうです。もともとゲーム業界での活用を想定しており、JSONで送られてくるログを空間情報として使える形で保存しています。**3Dの世界情報を点群などで持つのではなく、PostgreSQLに保存してGISクエリで問い合わせている**のです。

このアプリの面白いところは、**3Dゲームの探索の仕組みをエージェントに落とし込んだ点と、GISクエリに変換するというドメイン設計**の点です。画像屋さんが普通は思いつかないやり方で、かなり斬新で個人的に刺さりました。JSONに変換する部分さえ作れれば、ゲーム業界以外でも汎用的に使える仕組みだと思います。

### その手元、安全ヨシ！と言わせろ。

![](https://static.zenn.studio/user-upload/deployed-images/b2f0aec45ba8e3517d01f6d2.jpg?sha=dbc27708eef2883211fce3c3b06d6b61e12ada18)

![](https://static.zenn.studio/user-upload/deployed-images/b41e11541ea5a79e51f2f5f6.jpg?sha=9833c6f2e466fe71a496e3d6e44895307fef951b)

製造業向けの利用を想定した、「**通電中なのに触ろうとしている**」という文脈まで理解できるAI現場監督のデモです。従来この手の検知は物体検知で行うことが多く、ヘルメットを被っているかどうかは分かっても、「通電中に触ろうとしている」という文脈までは理解できませんでした。ここを**世界モデルベースのVLM（Cosmos-Reason2-8B）によるエッジ側推論**で解決します。このデモではVLMへの追加学習を行っておらず、通電中というコンテクストはCosmosベースのゼロショットで十分検知できるそうです。

**エッジ側とクラウド側の役割を明確に切り分けている点**も興味深く、エッジ側は音声警告やパトライト点灯といった警告に注力します。警告をクラウド側で行うと、触ろうとしたタイミングに間に合わなかったり（結果、感電して大事故になる）、通信が途切れた際に危険検知ができなかったりするためです。エッジ側のVLMにはNVIDIA Jetson AGX Orinを使い、8Bのモデルで遅延を1秒以内に収めています（このVLMまでPhysical AIと呼んでいるのは面白いです）。具体的には、モデルサイズを小さめにするほか、時空間推論を行わずプロンプトを短くするといった工夫をしています。

一方のクラウド側は、即時性を求めない蓄積や監査の役割を担います。JSONログやビデオフレームを格納し、Bedrock（VLM）で時空間推論を行うことで、手順の前後違反のスコアリングや減点理由の可視化といった安全教育にも活用できます。

![](https://static.zenn.studio/user-upload/deployed-images/02450a5897b46f06242c42f2.png?sha=7570c1da4ce420a28d9fb1d80ac0ae270f904e50)  
*公開資料：<https://d2ty02cp72ivkv.cloudfront.net/> より*

現場のドメイン知識がかなり盛り込まれていてすごいなと思ったのですが、AWSプロフェッショナルサービスの方のデモでした。このブースとは別のVillage側で、プロフェッショナルサービスのブースの方がこんな看板を持っていらっしゃったのも印象的でした。

![](https://static.zenn.studio/user-upload/deployed-images/d22c984085eb17588e729981.jpg?sha=8dbcc6ae085bd7b99a5c6fee9a29bdb155580bab)

### AI エージェント vs 悪質ボット!

![](https://static.zenn.studio/user-upload/deployed-images/91cbbca0622d4c5fbd5a61c2.jpg?sha=8ed6b4f20a53bb9a2dcbbe6d3a736b169e3d821f)

**転売ボットをAWS WAFでハニーポットに誘い込む**というデモです。単なるWAFの宣伝ではなく、**WAFが配置されているCloudFrontのKVS（Key Value Store）をBedrockと組み合わせ、AIによる動的なハニーポットを生成できる**というモダンなものです。

なぜWAFとAIを組み合わせるのかというと、旧来の方法ではボットが新たな攻撃手法で来襲するたびに検知ロジックやブロックルールを変更する必要があったからです。これは終わらないいたちごっこになるうえ、ブロックするだけでは攻撃者の意図を観察できません。

![](https://static.zenn.studio/user-upload/deployed-images/fdfc082adde25d57d18213b0.png?sha=2f0617b436155cd405c84965e86eedc8a0b2b5cb)

![](https://static.zenn.studio/user-upload/deployed-images/6d6add5e7e68a0c1c8479cc4.png?sha=8f6fa015959fc5b0f2b17f7b0324d9c9692ee2c3)  
*公開資料：<https://dvyhavqqm554u.cloudfront.net/visitor-deck.pdf>より*

そこで、ボットをハニーポットLambdaに誘導してログを収集し、Bedrockを通じて振り分けやブロックルール（CloudFront KVS）をアップデートし続けます。従来はブラウザ+WAFだけでボット検知していましたが、これにCloudFront Functionsが加わります。CloudFront Functionsから読み出されるKVSがAIによってアップデートされ続けるため、柔軟な判断が可能になります。

これにより、手動でのルール変更や更新を自動化でき、**単にブロックしてボットの情報を捨てるのではなく、ハニーポットを通じて情報を蓄積し、ボットを観察可能な研究対象にできます**。また、AWS WAF AI Traffic Monetizationやx402課金フローなどを通じて、**AIによるコンテンツのただ乗りを逆手に取り、AIボットを収益源に変える**という、いい意味で攻めた戦略も展開されています。興味があれば資料を参照してみてください。

あと小ネタですが、可視化に使っているGrafanaのログ出力を、Bedrockで要約させているところが個人的に好きでした（下図の赤枠の部分）。これはCloudWatch Logsにログの要約を出力し、それをGrafana側で取り込むことで実現できるそうです。

![](https://static.zenn.studio/user-upload/deployed-images/586c3d11cb6460c105ea5001.jpg?sha=62e80f1bc4c20d89bfc8b297570eef64547e6347)

### しまってAI

![](https://static.zenn.studio/user-upload/deployed-images/c4d53905667c263c2a1c7ecf.jpg?sha=3b9152999466947737d96e8bdbaf2fbb08d2e9c5)

![](https://static.zenn.studio/user-upload/deployed-images/cbed863186c3488b575e2d39.jpg?sha=d0a521a36d7dad7ce152d7eb7f27b022b4483b13)

「**消しゴムを取って**」とロボットアームに話しかけると、**自動的に動いてものを掴んでくれる**（かもしれない）という、Physical AIらしい展示です。**ロボットをどう学習させ、どう推論させるかをしっかり実践している**のが好印象でした。

ロボットには教育用のSO-101（実売4万円級）を使い、推論用エッジ計算機にはNVIDIA Jetson AGX Thor開発キット（約3,499ドル）を使用しています。エッジ側で、ロボットの動作を決めるモデルを動かします（※2026年6月末時点）。

![](https://static.zenn.studio/user-upload/deployed-images/3c4b617c47a2f3e93ffb218c.png?sha=68357d146678d80f7ad972f7ab2025ae6695bcde)  
*公開資料：<https://d2n6k30rxqc18u.cloudfront.net/overview.html>より*

VLAモデルは、(1)π0.5、(2)ACT、(3)GR00T N1.5〜N1.7系の3種類を試し、**本番展示では最も精度が良かったACTを使用**していました。訓練データはテレオペで収集し、模倣学習から行っています。また、NVIDIAのロボットシミュレーター[Isaac Sim](https://github.com/isaac-sim/IsaacSim)をGPUインスタンスでホストし、訓練の補助に使っているそうです。訓練はすべてSageMaker上で行っています。音声出力を可愛く見せるために、Amazon PollyではなくQwen3-TTSを使っている点も工夫でしょう。

**開発時は8割程度の確率で消しゴムを掴めていたものの、Summitの本番展示では3割ほどしか掴めない**という課題もありました。あくまで推測ですが、開発時と会場でカメラの照明条件が違うことや、カメラ設定が微妙にずれることによる誤差などが考えられます。Physical AIと大きく騒がれていますが、**シミュレーター上ではうまくいっても実際に蓋を開けてみるとまだこの程度、というリアルな感触を掴めた**のが有意義でした。

AIエージェント（当時はReActなどと呼んでいました）も、2年前ぐらいはツールを呼んでくれない・間違って呼んでしまうなど、かなりもどかしいものでした。それがここ1〜2年のコーディングエージェントの台頭で急に使い物になったので、Physical AIもこの速度感で進歩してくるのか、あるいは期待先行なだけなのかは今後の注目点です。

### Costrimly Dojo：AI Agents で外部支出を削減

![](https://static.zenn.studio/user-upload/deployed-images/a7294f10ced0461c86ea1ad8.jpg?sha=1100f8241d09651dec25f978aa44f7c557dcdfcc)

![](https://static.zenn.studio/user-upload/deployed-images/c83951e883c86edac944e156.jpg?sha=94357ca0234a9665e1a6b8defc31d6b2b4a02e9f)

これはAmazon Quickのデモで、ビジネス・コーポレートユーザー向けを想定しています。「**外部支出のコストを削減せよという指示が降ってきた**」という設定で、**どうコスト分析を行い棚卸ししていくかをゲーム感覚で体験する**ものです。左側がAmazon Quickの画面、右側がチュートリアル形式のゲーム（ヒントが出てくる）です。

Amazon Quickは流行りのチャットアプリの見た目をしていますが、BIツールとしての歴史があるためこの手の分析はかなり得意で、専門知識のない方でも自然言語でデータ分析ができます。また、GoogleドライブやMicrosoft 365などのコネクタも備えています。

LLMのモデル選択も、Claude 4.8 Opusのように特定のモデルを明示させるのではなく、「**高速・バランス・スマート・自動**」のように**ビジネスユーザー向けに内部で隠蔽し、迷わないように**しています。モデルをあまりいじれない点は好みが分かれるかもしれません。

![](https://static.zenn.studio/user-upload/deployed-images/b865a5d893685643881d46c9.png?sha=38bbceba3ff7355013ea7dddb8857864590a647b)  
*公開資料：<https://pages.awscloud.com/rs/112-TZM-766/images/AWS-Summit-Japan-2026_A091_1.pdf>より*

エンジニア以外が使うデータ分析基盤としてはSageMaker Unified Studioがそれかなと思っていましたが、Amazon Quickもかなり有力そうです。この辺はMicrosoftが得意な領域なので、そこに切り込んでいこうというAWS側の意図を垣間見られました。

### AI営業ロールプレイ

![](https://static.zenn.studio/user-upload/deployed-images/c7aa4181525930d4c4ef6eda.jpg?sha=754c0705a1de8bb56a817b42dbad8ec40cc55033)

**<https://github.com/aws-samples/sample-ai-sales-roleplay>**

AIアバターを活用した営業ロールプレイングで、aws-samplesとして公開されているOSSがもとになっています。画像に映っているのは最高情報責任者を想定したロープレで、不適切な発言をしたときの反応を試したものです。

技術的に興味深い点として、まず**動画分析（VLM）にAmazon Nova Premierを使っており、これが結構使える**とのことでした。

また、アバターの表示にはThree.js + [@pixiv/three-vrm](https://github.com/pixiv/three-vrm)を活用しており、VRMフォーマットの3Dモデルを投入できます。**VRMは母音（A,E,I,O,U）ごとに専用の口形を持っており、音声生成に使うAmazon Pollyが[speech marksを出力できる](https://docs.aws.amazon.com/polly/latest/dg/using-speechmarks.html)ため、両者を組み合わせるとルールベースでリップシンクができる**とのこと。このやり方はなるほどと思いましたし、実際にアバターがあるとロープレっぽさが出てかなり効いていました。

![](https://static.zenn.studio/user-upload/deployed-images/6846d338b11b12bf3d96f2f6.png?sha=bcb14ae92f4266208c31d2ce6dc5c58d63ee688e)  
*GitHubより：<https://github.com/aws-samples/sample-ai-sales-roleplay>*

### ババ抜きAI

![](https://static.zenn.studio/user-upload/deployed-images/4ad890fe310305f9483b01fc.jpg?sha=876ae5d400f8179b4e2b30ed65e537c9f28fdcb3)

![](https://static.zenn.studio/user-upload/deployed-images/d7c2ae5846fd75c6be97820e.jpg?sha=4ecad0094e907085ab1164d96f4a5aab41b1bbcf)

**脈拍や顔の表情といった生体データをAIに与えて対戦するババ抜き**です。ロボットアームのカードを掴む操作はARマーカーで補助しています。資料をいただくのを忘れてしまい詳細はうろ覚えですが、**VLM/VLAを使っているため、ユーザーに対してブラフをかけることも可能**だそうです。

ちなみに、生体データをほぼ与えているとはいえ、人間に絶対勝てるわけではなく、勝率はせいぜい五分五分だそうです。そもそものババ抜きのアルゴリズム部分がボトルネックになっているとのことでした。

### AI Game Forge

![](https://static.zenn.studio/user-upload/deployed-images/7846a59e8d03caa1122d4ccd.jpg?sha=1067a94d5b437c3ca06860d978de248beffbeaa7)

![](https://static.zenn.studio/user-upload/deployed-images/95f938a663153f63d0c04c48.jpg?sha=03e7698ac5ee31d443150eac414aa211bdcc45bd)

**AIがマーダーミステリー（体験型推理ゲーム）を自動生成し、AIと一緒に遊ぶ**ことをコンセプトにしたものです。技術詳細が渋くて個人的に好きな展示でした。

ストーリー生成を開始すると、事件をエージェント風に作り込んでいきます。まず「ストーリー概要」を作り、次に「キャラ・手がかり詳細」「フェーズ・結末」「所持品・行動」、その次に「キャラ画像」「キャラ動作」……と**階層的かつ連鎖的に作っていく**のが特徴です。これは**Step Functionsのファンアウトで実装**しており、Bedrock AgentCoreのような最近流行りのエージェント型ではなく、**少し前のワークフロー型の自動化**です。ワークフロー型で生成過程を固定することで、ストーリー生成の安定性が向上します。

また、画像生成・音声生成（Text to Speech）・リップシンク・BGM生成といったMLモデルの推論にはGPUワークロードが必要ですが、**これをEKS Auto Modeでホスト**しています。この手の展示ではSageMakerのエンドポイントを使うことが多く、**あえてEKSで実装しているのが渋い部分**です。GPUインスタンスのコスト対策として、**KEDAでアイドル60分後に全Podを完全停止**させるようスケールしています。

実際にプレイしてみると、**ストーリーはかなり安定しており、キーアイテムもちゃんと機能**していました。対話生成のLLMがClaude HaikuやSonnet 4.xのため、犯人が「私は犯人ではありません」とあからさまに怪しい言動をしても疑われないガバさはありましたが、Opusなどを使えば「あなた犯人ですよね」と詰められるのかもしれません。

![](https://static.zenn.studio/user-upload/deployed-images/76eda6301599dd059b50c563.png?sha=349dae9c68e611d85f0a6688d75525dcc7eabe08)

![](https://static.zenn.studio/user-upload/deployed-images/ae8972ce5123c4c92c0f135c.png?sha=319bb4734ec4f26ded65dccad492b710dbd3982e)  
*公開資料：<https://dev.d3n7qn00zvdwg4.amplifyapp.com/docs/gameforge-summit-pitch-final.pdf>　より*

### AI Agentでゲーム実況

![](https://static.zenn.studio/user-upload/deployed-images/ab2a85291afc63e38a5b2d9f.jpg?sha=08daed4eeedb320517f4517e9e9969b70f863cb2)

**サッカーゲームの実況生成をAIエージェントが行う**ものです。[Google Research Football（GRF）](https://github.com/google-research/football)というOSSのゲームをプレイさせ、**ゲームから吐き出されるJSONイベントをもとにLLMが実況を生成**します。

JSONイベントは「誰から誰にボールが渡った」といったイベントを表すもので、これをBedrock AgentCoreで実況します。実況音声は、GRFサーバー内にホストされた[Style-BERT-VITS2](https://github.com/litagin02/Style-Bert-VITS2)で、より実況らしいスタイルのTTSとして生成しています。設定はスピードを1.5倍にしたNeutralスタイルだけで、十分それっぽくなっていました。

かなり直前まで試行錯誤なさっていたデモで、すべてを1つのGPUインスタンスに押し込めるなど、ある意味手軽に作りやすいものかもしれません。

![](https://static.zenn.studio/user-upload/deployed-images/d722d421a9991bf0b70f4052.jpg?sha=37096d3627fd7b71645ac0c0927d93bee5a26419)

![](https://static.zenn.studio/user-upload/deployed-images/22331bff605895d58d2db435.jpg?sha=9845af6ac0b3b84b6983c97a113b3455496db049)

## 興味深かったVillageエリアの展示・セッションなど

ここまでBuilders' Fairを中心に紹介しましたが、Villageエリアやセッションで興味深かった内容もいくつか紹介します。

### サンドボックス環境管理を効率化しよう！

![](https://static.zenn.studio/user-upload/deployed-images/2dcd039ee6e7ae5503683dc9.jpg?sha=52d25030bcac4a9b591d63565f9aa610b943d874)

**<https://github.com/aws-solutions/innovation-sandbox-on-aws>**

Innovation Sandbox on AWSというソリューションの紹介です。**個人単位で使えるサンドボックス用AWSアカウントを、ガバナンスとコスト管理を保ちつつ提供する**ものです。AWS Organizations下にOUを作って管理するため、Organizationsの権限が必要です。

私も長らく共用のAWSデモ環境を管理していますが、2年も経つとゴミリソースが増え、その棚卸しや管理の自動化が結構大変だと感じています。このソリューションはあくまで個人単位のため、皆で共有環境を使ってハンズオンやデモを社内展開する用途にはハマりませんが、Organizationsの権限があってデモ環境を提供するならこれかなと思いました。Identity Centerと連携しており、退職すると自動的にアクセスできなくなる点も便利です。

### 完全自律型 AI Agentが変えるSaaSの世界

![](https://static.zenn.studio/user-upload/deployed-images/d1876c02cc0bb8acb101b335.jpg?sha=07c4797fbe3ca08e5cd1603b7378c4168fd91058)

![](https://static.zenn.studio/user-upload/deployed-images/0586bd2c75226541e5d5bbf4.png?sha=64fd2bc19a815c183ba0b79e3e4a75e59b2fb093)  
*公開資料：<https://pages.awscloud.com/rs/112-TZM-766/images/AWS-Summit-Japan-2026_A135_1.pdf>　より*

当社もお世話になっているISV/SaaSの方が中心の展示で、Bedrock AgentCoreを用いた完全自律型SaaSのデモを展示されていました。

背景としては、**AIエージェントのPoCを進めている企業は多いものの、それを実際にSaaSへ組み込む例はまだ少ない**ため、モック的に展示したとのことです。デモは、**顧客からの問い合わせに対して金額見積もりや担当者のアサイン、返答メールなどをAIエージェントに作らせる**というものでした。生成結果は承認キューに溜まっていき、**最終的なGoのボタンは人間が押す**、という流れに見えました（展示資料が公開されておらず、ややうろ覚えです）。

AIエージェントのユースケースとして非常に良いものだと思います。どういう思想で作ったのか伺ったところ、CRMのSaaS一般論から生まれたもので、旧来の業務フローでは担当者が分かれて各所に承認プロセスがあり時間がかかっていたものを、すべてAIエージェントで自律的に動かすという発想から来ているようでした。

アーキテクチャ図は、この手の自律型SaaSを作るとこうなるだろうというもので、この発想を横展開するとエージェントSaaSを作りやすくなりそうです。かなり有益なスライドがブース配布資料として公開されていたので、ぜひご覧ください。

### 生成AIを支えるインフラ技術

![](https://static.zenn.studio/user-upload/deployed-images/516481b78c39dd4a63ecaac1.jpg?sha=b87536706e23c03afb80de74e85248013556a131)

![](https://static.zenn.studio/user-upload/deployed-images/2516eedf86087bd924ea4c1e.jpg?sha=5ea796919104f678c2da3ea8fdc8de3a8ba64a24)

（私にとっては）おなじみのAWS Neuronの展示です。Neuron（Inferentia/Trainium）は安価に使えるML専用チップですが、現状まだ対応モデルが限られており、GPUほどの自由度では使えないというもどかしさがあります。

右側のデモでは、Qwen3-VL-8B-Instruct、Qwen-Image-Edit-2511、xTTS-v2がNeuron上で動作していました。ただし**後ろの2つはそのままでは動かず、特にxTTS-v2はかなり黒魔術的な工夫でモデルをハックしたうえでデプロイ**しているので、簡単に動くと期待しないほうが良いです。詳細は以下の記事が非常に詳しいのでご参照ください。

<https://zenn.dev/tosshi/articles/53cc505a8d85e2>

ただ、昨年のre:Invent 2025でも発表されたように、NeuronのPyTorchネイティブサポートがGAされればこの取り回しはかなり良くなるとのことなので、今後の動きに期待したいです。

また、Neuron Communityも7月15日(水)にリモート開催されるとのことなので、こちらも楽しみです。

### Amazon Bedrock AgentCoreによる堅牢なSaaSデータエージェントの設計

![](https://static.zenn.studio/user-upload/deployed-images/a2b61d0c2dda78189140981d.jpg?sha=0532047bd30f4864995a6bf58b8013464c5560ce)

![](https://static.zenn.studio/user-upload/deployed-images/a2bff8ac69ed9effea1d5199.jpg?sha=0f1ae7f2f8b1ab069af11e7e22e9cd7bb8ab3110)

こちらはセッションです。AIエージェントは「とりあえず作ってみた」なら簡単ですが、エンタープライズ向けの堅牢なSaaSとして展開するには、従来のSaaSとは異なるさまざまな設計上の工夫が必要です。

このセッションでは、**防御点を「LLM層」「呼び出し層」「ツール層」「リソース層」の4つのレイヤーに分解し、それぞれで守るべき対象や対策の原則をまとめて**います。「ここを守っておけばAIエージェントSaaSは大丈夫」という、**地に足のついた俯瞰論として非常に有益**でした。

アーカイブ配信もされている（はず）なので、ぜひご視聴ください。

<https://zenn.dev/aws_japan/articles/b75232a7fa8a70>

## 総評

かなり長い記事になってしまいましたが、総評としては「**昨年一大ブームとなったAIエージェントが、ようやく地に足のついた形で実装できるようになった。一方でPhysical AIは期待が先行しつつも、まだ未整備の部分が多く萌芽的である**」というのが実感でした。昨年にも増してAWS側も「AIにオールイン」している感が強く、展示やセッションの多くがAI関連でした。ただ、流行りに乗っている部分もありつつ、他サービスの進化や工夫も押さえており、全般的にはバランスが良かったように思います。

個人的には2日間参加してもまだ足りないほどで、見られていないセッションも多く、参加して本当によかったイベントでした。この他にも当社メンバーによるSummit参加報告記事があるはずなので、ぜひご期待ください！
