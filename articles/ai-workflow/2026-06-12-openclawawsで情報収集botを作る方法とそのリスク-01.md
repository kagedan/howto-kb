---
id: "2026-06-12-openclawawsで情報収集botを作る方法とそのリスク-01"
title: "OpenClaw+AWSで情報収集botを作る方法と、そのリスク"
url: "https://zenn.dev/exwzd/articles/20260522-event-monitor"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "JavaScript", "zenn"]
date_published: "2026-06-12"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

こんにちは、株式会社エクサウィザーズのWANDチームでインターンをしている村井です。

WANDチームでは、クラウドインフラとAIエージェントについての技術検証と開発を行っています。今回はその一環で、OpenClawとAmazon Bedrockなどを使って、関連分野の学会の開催情報をTeamsに自動で投稿してくれるエージェントを作りました。技術的な話に加えて、作る過程で分かったOpenClawのリスクについて扱います。

# 背景

WANDチームは活動の一環として、各種テックイベントや学会にスポンサー・発表者として参加し、情報共有とアウトリーチを行っています。最近の例として、[言語処理学会 (NLP) でのスポンサー参加](https://zenn.dev/exwzd/articles/20260326_nlp2026_report)、[IBIS 2025の聴講参加](https://zenn.dev/exwzd/articles/20251209_ibis2025)、[ICCV 2025 でのワークショップ開催](https://zenn.dev/exwzd/articles/20251209_found_workshop) などのレポートを公開しています。

こうしたイベントの情報収集・選定は手動で行なっていましたが、さらにアウトリーチの幅を広げるために、各サイトをクロールしてイベントの情報を網羅的に選ぶエージェントがあれば便利だということになり、今回のbotを作るに至りました。

# AWS と OpenClaw

今回はAWSの機能を用いて実装を行います。AWSには言語モデルの推論APIであるAmazon Bedrockや、AIエージェントの開発プラットフォームであるAmazon Bedrock AgentCoreが用意されています。AWSから公式に、OpenClawをデプロイするためのサンプルコード ([GitHub](https://github.com/aws-samples/sample-OpenClaw-on-AWS-with-Bedrock))([AWS有志のブログ](https://zenn.dev/aws_japan/articles/edade4a28a8e41)) が提供されているので、これを元に実装を進めます。

# 構成と実験

アーキテクチャ図は以下のとおりです。VPC上にEC2インスタンスを起動し、OpenClaw を常駐させます。OpenClawはEgress (外向き通信) 経由で各種ウェブサイトの情報を取得し、サマリをPower AutomateのWebhookを用いてTeamsに投稿します。各種認証情報 (Teams APIのトークン付きURLなど) は ソースコードからの流出を防ぐためにSSM Parameter Store に保存します。さらに、エージェントが平文で鍵を見ることができると流出リスクがあるため、API呼び出しはToolsに分離し、コンテナ化を用いてエージェントから鍵にはアクセスできないようにします。

![](https://static.zenn.studio/user-upload/deployed-images/5d708fb2646ddf31251c440b.png?sha=156de3dabcf99ef2c12486a5fb3ddd5c933e98d7)

AWS Sampleからの変更点としては、OpenClawを起動するEC2にヘッドレスブラウザ (Chromium) を追加しています。OpenClawにもWeb Fetch機能はありますが、HTMLの取得を行うだけなので、サイトがJavaScriptベースの場合はうまく取得できません。ChromiumにはJavaScriptのレンダラーが搭載されているので、これを使うことで様々なサイトの情報取得が可能です。

また、エージェントにとって難しそうなタスクや、手順が決まっているタスクについては各種Skillsを設定しています。

## 情報源の選定

今回は、学会情報の取得については [CCF Deadlines](https://github.com/ccfddl/ccf-deadlines) を主に使っています。これはコンピューターサイエンス分野の国際会議（学会）の投稿締め切り（Deadline）を自動追跡・管理するためのオープンソースプロジェクトで、中国コンピュータ学会（CCF: China Computer Federation）が定めている学会の重要度ランキング（A、B、Cランク）をベースに、世界中の主要な学会のスケジュールがまとめられています。WebサイトやGitHubリポジトリから情報を取得できるほか、CLIも用意されています。その他には、[AI Deadlines](https://aideadlin.es) も使用しました。

ここで、エージェント任せにして学会を選ばせると、ほとんどの場合でICLR, NeurIPS, ICMLといったトップカンファレンスがヒットします。これらはエージェントを使うまでもなく知られていますし、スポンサー費用は高額なことも多く、あまり有用ではありません。一方で、あまり知名度のない学会も好ましくありません。そこで、[CORE ランキング](https://portal.core.edu.au/conf-ranks/) を参照し、ランクがA, B, Cのものを主に選ぶようにします。A\*ランク (トップティア)と記載なしは除いています。したがって、エージェントの挙動としては、CCF Deadlines を確認 → CORE ランキングを確認 → Web FetchやChromiumで学会HPを取得 → 詳細を確認し、プロンプトで与えた各条件 (締切日、開催地、分野など) と合えばレポートに追加、というようになります。

## Teams 連携

出力先にはPower Automateを使ってTeamsに投稿を行います。次のようなJSONを用意します。  
このJSONの形式が、OpenClawから送信されるものと一緒になるようにします。

```
{
    "date":"",
    "message":""
}
```

Power Automate (<https://make.powerautomate.com/>) の画面で「新しいフロー」「インスタント　クラウド　フロー」を選択し、トリガーに「HTTP 要求の受信時」を選択します。

![](https://static.zenn.studio/user-upload/deployed-images/92b05c7c148331cad2974a04.png?sha=11fe5fa7dad53542f3896531e45988557ebbfaf2)

次に、ノードの「サンプルペイロードからスキーマを生成します」を開き、現れたウィンドウに上のJSONを貼り付けると、「要求本文のJSONスキーマ」には次のように表示されます。この欄に直接JSONを貼り付けないように注意してください。

![](https://static.zenn.studio/user-upload/deployed-images/997f0498664b9a171e6430ae.png?sha=aa1942581e21adf99f182b4e177655d10bc0d590)

その後に「チャネルまたはチームにメッセージを投稿」のノードを足し、スラッシュコマンドから先の `message` を追加します。保存するとURLが表示されるので、あとはエージェントに、成果物を当該URLにPOSTするように指示します。

# 出力ドキュメント

実際に動かすと、以下のようなドキュメントが出力されました。

### テーブル (概要)

| 名称(略称) | 開催地 | 開催期間 | 分野 | CORE | リンク |
| --- | --- | --- | --- | --- | --- |
| [ECML PKDD 2026](https://ecmlpkdd.org/2026/) | ナポリ, イタリア | 2026/09/07–11 | ML / Data Mining | A | [公式](https://ecmlpkdd.org/2026/) |
| [CIKM 2026](https://cikm2026.diag.uniroma1.it/) | ローマ, イタリア | 2026/11/07–11 | IR / KM / DB | A | [公式](https://cikm2026.diag.uniroma1.it/) |
| [RecSys 2026](https://recsys.acm.org/recsys26) | ミネアポリス, MN, USA | 2026/09/28–10/02 | Recommender Systems | A | [公式](https://recsys.acm.org/recsys26) |
| [ACCV 2026](https://accv2026.org/) | 大阪, 日本 | 2026/12/14–18 | Computer Vision | B | [公式](https://accv2026.org/) |
| [BMVC 2026](https://bmvc2026.bmva.org/) | ランカスター, UK | 2026/11/23–26 | CV / Image Processing / Pattern Recognition | A | [公式](https://bmvc2026.bmva.org/) |

---

### 各エントリ詳細

* 開催: 2026年9月7–11日, ナポリ, イタリア
* 分野: Machine Learning / Knowledge Discovery / Data Mining
* 採択率: ~25% (2024 年度実績, 公式発表値)
* Key dates:
  + Paper submission deadline: 2026/04/xx (passed — 査読サイクル終了)
  + Acceptance notification: —
  + Camera-ready: —
  + Early-bird registration: —
* スポンサーシップ:
  + — (公式スポンサーページ `/sponsoring` が 404; 詳細は公式へ直接問い合わせ推奨)
  + 連絡先: ecmlpkdd.org/2026/ より組織委員会へ
* 出典: [公式](https://ecmlpkdd.org/2026/) / [web\_search で日程確認](https://ecmlpkdd.org/2026/)

---

* 開催: 2026年11月7–11日, ローマ, イタリア
* 分野: Information Retrieval / Knowledge Management / NLP / AI
* 採択率: ~22% (過去実績ベース、公式未発表)
* Key dates:
  + Full Research Papers Abstract deadline: 2026/05/16 (passed)
  + Full Research Papers Submission deadline: 2026/05/23 (passed)
  + Short/Resource/Demo Papers deadline: 2026/06/06 (future)
  + PhD Symposium / Industry Day deadline: 2026/06/22
  + Acceptance Notification: 2026/08/07
  + Camera-ready: 2026/08/20
  + Early-bird registration opening: TBA
  + Tutorial / Workshop Proposals: 2026/06/22
* スポンサーシップ:
* 出典: [公式](https://cikm2026.diag.uniroma1.it/) / [重要日程](https://cikm2026.diag.uniroma1.it/important-dates/)

# OpenClaw で情報収集をするリスク

今回の検証を進める上で分かったこととして、OpenClawを使って、特に外向き通信を制限せずに情報収集をすることにはやはり一定のリスクがあります。たとえば、悪意のあるサイトにプロンプトインジェクションを行われ、秘密鍵などをどこかのHTTPサーバにPOSTしてしまう、ということが考えられるでしょう。このためには、コンテナ化で秘密鍵をモデルがアクセスできないように分離する設計をする、外向き通信を制御するなどの工夫が必要になります。

一方で、もう少し分かりづらいリスクとしては、自動クロールを禁じているサイトからの法務リスクが考えられます。サイトによっては有料APIを提供する代わりに、クローラによるクロールなどを規約で禁じている場合があります。通信先を指定せずにエージェント任せで情報収集をさせた場合、このようなサイトからも情報を取得する可能性があります。

例として、[connpass](https://connpass.com/) では有料の商用APIを提供する代わりに、それ以外の方法でのアクセスを禁止しています。connpassの利用規約 (<https://connpass.com/term/>) では以下のように定められています。

> 第７条【禁止事項】
>
> 1. 利用者は当サイトを利用するにあたり、下記に該当する行為またはそのおそれがある行為を行ってはならないものとします。
>
> (中略)
>
> 17. 当社から提供されるAPI以外の方法（自動化した方法であるか否かを問いません。）によって、当サイトへクローリング、スクレイピング、その他のアクセスを行いもしくは行うよう試みる行為

有料APIをバイパスするような自動化をエージェントが行なってしまった場合、このように大きなリスクを負うことがありえます。また、有料APIなどを提供していなくとも、多くのサイトはクローラによる自動アクセスや大量ダウンロードを禁じています。OpenClawエージェントによるアクセスがそれに該当するかどうかは場合によりますが、それでも法務リスクがあることは確かです。OpenClawをそうしたサイトからの情報収集目的で使うことが危ないのはもちろん、潜在的にはOpenClawをアクセス制限なしで運用するだけでも、そうしたサイトの規約に違反するリスクがあると言えます。

今回の検証では、最初はさらに探索範囲を広げて、各種AWSのイベントやLT会など、コミュニティによるイベントの情報も取得する予定でした。しかし、たとえばAWSのウェブサイトの規約 (<https://aws.amazon.com/jp/terms/>) には明確にこのような文言があります。

> AWS は、AWS サイトにアクセスし、これを個人的に使用することはできるものの、AWS の明示の書面による同意のある場合を除き、当該サイトまたはその一部をダウンロード（ページ・キャッシュを除きます。）または変更することはできない限定的ライセンスをお客様に付与します。本ライセンスには、AWS サイトまたはそのコンテンツの再販売または商業的利用、AWS サイトまたはそのコンテンツの派生的使用、他のユーザーのアカウント情報のダウンロードまたはコピー、**データマイニング、ロボットまたは類似のデータ収集および抽出ツールの使用**は含まれません。(強調引用者)

したがって、AWSのサイトから自動で各種イベントの情報を取得することは技術的にはできるが、するべきではない、という判断に至りました。

## robots.txt

また、確認した方が良いこととして各サイトの `robots.txt` があります。これは各サイトの管理者が、様々なクローラに対してどの部分はアクセス可能か、ということを指定するための文書です。たとえば、次のように指定します。

```
User-agent: *
Disallow: /admin

User-agent: Googlebot
Disallow: /secrets
```

robots.txtは厳密な強制力があるわけではなく、利用規約があるサイトはそちらが優先されます。ただし、そのサイトがwebクローラを受け入れているかの指標にすることは可能です。たとえば、すべてのエージェントにアクセスを禁じる (`Disallow: /`) robots.txt がある場合は、エージェントからそのサイトにアクセスするのは避けるべきでしょう。

# まとめ

本記事では、OpenClaw + Amazon Bedrock を用いて学会情報を自動収集し、Teamsに投稿するbotの構築方法を紹介しました。ポイントをまとめると以下のとおりです。

* 構成: EC2上のOpenClawにChromiumを追加し、JSベースのサイトにも対応。
* 情報源の工夫: CCF DeadlinesとCOREランキングを組み合わせ、トップティアでもマイナーでもない「ちょうどいい」学会を選定
* Teams連携: Power AutomateのHTTPトリガーを使い、エージェントの出力をそのままチャネルに投稿
* リスク: プロンプトインジェクションによる情報漏洩リスクに加え、自動クロールを禁じるサイトへの法務リスクが存在する。Egress制御やアクセス先のホワイトリスト化が重要
