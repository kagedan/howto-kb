---
id: "2026-06-08-全部知ってるanthropicclaude関連のサービス総まとめ-01"
title: "【全部知ってる？】Anthropic・Claude関連のサービス総まとめ"
url: "https://qiita.com/kyuko/items/2d8032c413ec1fb5e316"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "Gemini", "GPT"]
date_published: "2026-06-08"
date_collected: "2026-06-09"
summary_by: "auto-rss"
query: ""
---

こんにちは！ひさふるです。

最近、Claude Opus 4.8をはじめとして、Anthropicから様々な新機能やサービスの発表がありましたね。

中でも、Claudeを使って非常にレベルの高いデザインを生成できる **Claude Design** は大きな話題になりました。

https://www.anthropic.com/news/claude-design-anthropic-labs

Claude Codeやモデルの質の高さが着目されがちなAnthropic・Claudeですが、こうして見ると意外とその他のサービスも多いんですよね。

というより、最近のClaudeはもはや単なるチャットAIではなく、

- Claude本体
- Claude Code
- Claude Cowork
- Claude Design
- Microsoft 365 / Chrome / Slack連携
- API / Managed Agents
- Connectors / MCP

などを含む、かなり大きな **AI作業環境** になりつつあります。

そこで今回は、Claude関連のサービスをまとめてみました。

## 1. 現行モデル

まずは基本中の基本、提供されているモデルについてです。

Claudeのモデルには **Opus**、**Sonnet**、**Haiku** の3種類があり、それぞれ以下のような特徴があります。

| モデル | 説明 |
|---|---|
| **Opus** | 最高性能・最高価格で、深く考えるタスクに向いている |
| **Sonnet** | 速度と性能のバランス型で、広い用途で使える |
| **Haiku** | 軽量・低価格・高速 |

現在では、それぞれ以下のようなバージョンが選べるようになっています。

| モデル | 現行世代の例 | 向いている用途 |
|---|---|---|
| **Claude Opus** | Claude Opus 4.8 | 高度な推論、複雑な設計、長時間のエージェントタスク、重要なコーディング |
| **Claude Sonnet** | Claude Sonnet 4.6 | 普段使い、コーディング、文章作成、業務利用全般 |
| **Claude Haiku** | Claude Haiku 4.5 | 軽量な処理、大量処理、分類、低コスト・高速応答が重要なタスク |

ざっくり使い分けるなら、重い推論や重要な設計にはOpus、普段使い・コーディング・文章作成にはSonnet、軽量な分類や大量処理にはHaiku、というイメージです。

### 次の世代は？ 〜Claude Mythosについて〜

現在も様々な次世代モデルを開発中と思われるAnthropicですが、そのうち1つが **Claude Mythos Preview** です。

https://www.anthropic.com/glasswing

ただし、このモデルは通常の新モデルというより、サイバーセキュリティ領域において非常に高い能力を持つ研究プレビューのモデルとして紹介されています。

特に、セキュリティやサイバー攻撃に関連する能力が過去のモデルとは比較にならないほど高く、実際にOSSで長年放置されていた脆弱性を発見するなど、既に十分に実用レベルにあるようです。

一方で、Claude Mythos Preview自体は一般提供されておらず、Project Glasswingに参加する一部のパートナー向けに提供されています。

Anthropicとしては、こうした高性能モデルを安全に展開するための仕組みもあわせて整備している段階のようです。

## 2. 基本チャット機能

Claudeのモデルは様々な形態で提供されていますが、まず試してみるなら最もオーソドックスなチャットで使ってみるのが良いでしょう。

Webアプリとして利用できるほか、iPhone・Android向けにもアプリが提供されています。

https://claude.ai/new

![スクリーンショット 2026-04-22 4.43.56.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/655545/37dd4040-f8b2-4a4d-89fb-21aa4e84f801.png)



### 特徴①：Artifacts

チャットについては説明不要な気もしますが、一応Claudeならではの特徴も紹介しておきましょう。

Claudeは **Artifacts** という形で、チャット内でコンテンツを生成・保存・共有できる機能を有しています。

**Artifacts** ではテキストベースのドキュメントやSVG画像、コードスニペットを生成できます。

さらに、Reactコンポーネントとして簡易的なWebアプリを作成し、その場で動かすこともできるようになっています。

以下はテトリスを生成させてみた例です。

![スクリーンショット 2026-04-22 17.49.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/655545/669c014c-a92f-493b-a446-4e2f8a1fa924.png)

動くプロトタイプをパッと作って共有、という体験においては非常に優れています。

とはいえ、ChatGPTやGeminiもCanvasという形で似たような機能を提供しているので、今後の更なる差別化にも期待ですね。

https://support.claude.com/ja/articles/9487310-%E3%82%A2%E3%83%BC%E3%83%86%E3%82%A3%E3%83%95%E3%82%A1%E3%82%AF%E3%83%88%E3%81%A8%E3%81%AF%E4%BD%95%E3%81%A7%E3%81%99%E3%81%8B-%E3%81%9D%E3%81%97%E3%81%A6%E3%81%A9%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E4%BD%BF%E7%94%A8%E3%81%97%E3%81%BE%E3%81%99%E3%81%8B

### 特徴②：Projects / Project RAG

Claudeには、会話単位ではなくプロジェクト単位で知識やファイルを管理できる **Projects** 機能があります。

プロジェクト内に関連するドキュメントや前提知識を置いておくことで、Claudeがそれらを参照しながら回答できるようになります。

また、**Project RAG** により、プロジェクト内の情報を検索・参照しながら回答するような使い方もできます。

個人的には、Claudeを単発のチャットとして使うよりも、何らかのプロジェクト単位で継続的に使う場合にかなり便利な機能だと感じています。

たとえば、

- サービスの仕様書
- 既存の設計メモ
- 記事の下書き
- 社内ドキュメント
- 調査資料

などを入れておき、その文脈をもとにClaudeに相談するような使い方ができます。

### 特徴③：スキル・コネクタ・プラグイン

チャット機能からも、スキル・コネクタ・プラグインといったカスタマイズ要素を利用できます。

![スクリーンショット 2026-04-22 17.53.48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/655545/0d699847-500f-4c26-ad8e-d3a8abccd0c4.png)

「スキル」はClaude Codeを使っている方ならおなじみ **Skills** のことです。

何らかのタスクを実行するための指示や手順、補助ファイルなどを定義しておき、必要なときにClaudeから呼び出せます。

「コネクタ」は様々な他アプリとの連携を可能にする機能です。

代表的なコネクタとしては、Slack、Google Workspace、GitHub、Microsoft 365などがあります。

また、Remote MCPを使って独自のカスタムコネクタを構築することもできます。

「プラグイン」は、スキルやコネクタ、slash commands、sub-agentsなどをまとめたものです。

Claude Codeにも似た機能がありますが、Hooksなど一部の機能はClaude Code専用となっています。

## 3. コーディング・開発者向け

次は、主に開発者などIT関連の開発を行う方向けの機能を紹介します。

### Claude Code

最近の開発者にはおなじみ **Claude Code** ですね。

私もいつもお世話になっています。

Claude Codeは、もともとはターミナルでの利用が印象的なコーディングエージェントですが、現在ではターミナルだけでなく、IDE、デスクトップアプリ、ブラウザなどにも展開されています。

https://code.claude.com/docs/ja/overview

![スクリーンショット 2026-05-01 13.18.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/655545/1ac326c0-aa92-4b4c-8408-549821f6eb8a.png)

単にコーディングやレビューができるだけでなく、Skills、Sub Agents、Hooksといった幅広いカスタム要素が魅力です。

詳しくはこちらの記事をご確認ください🙇

https://qiita.com/kyuko/items/77e9e022860b57e4bd4d

また、最近のClaude Codeはターミナルだけではなく、Web上での利用やCode Review、自動セキュリティレビュー、デスクトップアプリなどにも展開されています。

つまり、単に「ローカルで動かすCLIツール」というより、GitHubやCI、Web UI、セキュリティレビュー、デスクトップアプリなどを含む開発支援基盤に広がりつつある印象です。

### Claude Code Action

Claude Codeファミリーとして、Claude Code Actionが存在します。

https://github.com/anthropics/claude-code-action

これは、Claude Codeのようなエージェントによるレビュー等を、GitHub Actions上で実行するための仕組みです。

**Pull Requestsを作成したときに自動的にAIによるレビューを実行したり**、発行したIssueに関する修正や実装を行わせたりといった使い方が多い印象です。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/655545/c8e65e78-c617-45f0-a67a-713ebd05565b.png)

AI関連の処理を自動化することができるため、上手く活用できれば大幅なコーディング効率アップを狙えることでしょう。

### Claude API / Claude Console / Workbench

開発者向けには、Claudeをアプリケーションに組み込むための **Claude API** も提供されています。

https://platform.claude.com

APIを使うことで、自分のWebアプリや社内ツール、エージェント、チャットボットなどにClaudeを組み込むことができます。

Claude Consoleでは、APIキー管理や利用量確認、ワークスペース管理などが可能です。

また、**Workbench** を使うことで、プロンプトを試したり、モデルごとの出力を比較したり、API経由での挙動を確認したりできます。

Claude Codeのような完成されたツールだけでなく、自分のサービスやプロダクトにClaudeを組み込みたい場合は、このあたりが中心になるでしょう。

### Claude Managed Agents

Claude Managed Agentsは比較的最近登場したベータ機能で、サーバー側でエージェント機能を実行できるマネージドインフラストラクチャです。

Claude Console上からアクセスできます。

https://platform.claude.com

https://platform.claude.com/docs/ja/managed-agents/overview

Claude Managed Agentsの面白いところは、ファイルの読み書き、コマンド実行、Web検索、MCPサーバーとの接続といったツールを、サーバー側のサンドボックス環境で実行できるところです。

|  | Messages API | Managed Agents |
|:-:|:-|:-|
| 説明 | モデルのAPI呼び出し | マネージドインフラストラクチャ上でのエージェント実行 |
| 実行主体 | モデル実行の結果を逐一受け取り、ツール使用等は主にクライアント側で実行する<br>⇒ エージェントループをクライアント側で実行 | サーバー側でサンドボックス環境を作り、ファイル読み取りやWeb Search等のツール使用まで完結する<br>⇒ エージェントループをサーバー側で実行 |

従来、例えばWebアプリにエージェントを組み込む場合、APIでモデルだけ呼び出し、その結果をもとにツール呼び出し等の次の行動の決定をクライアント側で行う必要がありました。

対して、Managed Agentsはサーバー側でエージェントとしての動作が完結するため、クライアント側で複雑な処理を実装する必要がなく非常に便利です。

また、長時間かかるタスクや非同期で進めたいタスクにも向いているため、今後、簡単にエージェントを実装するための1つの選択肢として、採用されることが増える気がしますね。

### Claude on Amazon Bedrock / Vertex AI / Microsoft Foundry

ClaudeはAnthropic公式APIだけでなく、Amazon Bedrock、Google Cloud Vertex AI、Microsoft Foundry経由でも利用できます。

既にAWSやGCP、Microsoft Azure系の基盤を使っている企業では、こちらの経路からClaudeを導入することも多いでしょう。

特にAmazon Bedrock経由のClaudeは、AWSを使っている開発者にとってかなり馴染み深いと思います。

AnthropicのAPIを直接使うのではなく、既存のクラウド基盤や権限管理、請求管理に乗せてClaudeを使えるのが大きなメリットです。

## 4. デザイン・制作

### Claude Design

開発者というよりデザイナー向けですが、アプリ開発や資料作成に関する機能として **Claude Design** も紹介しておきます。

https://claude.ai/design

Claude Designは、Anthropic Labsのresearch previewとして公開されている機能で、Webページやアプリのプロトタイプ、発表用スライド、one-pager、micrositeなどを作ることができるサービスです。

![スクリーンショット 2026-05-05 2.30.40.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/655545/6c5f94b7-f0df-4c91-895e-87a6ee23a497.png)

AIでデザインできる似たようなサービスは複数ありますが、そのデザインの完成度の高さや他のClaude関連サービスとの親和性、スライド作成までできる汎用性等から一気に知名度を獲得しました。

特に面白いのは、単なる画像生成ではなく、Webやスライド、プロトタイプといった「編集可能な成果物」に近いものを作れる点です。

また、Claude Codeへのハンドオフも意識されており、デザイン案やプロトタイプをそのまま実装側に繋げていくような使い方も想定されています。



## 5. 一般事務作業等

### Claude Cowork

Claude Coworkは、Claudeに様々な日常業務を依頼することができるデスクトップエージェントです。

Claudeのデスクトップ版から利用できます。

![スクリーンショット 2026-05-06 0.16.23.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/655545/6c1450a8-8551-4b93-b91f-d3063e25bee0.png)

開発者の方向けには、Claude Codeのエージェント的な考え方を、非エンジニア向けのナレッジワークにも展開したもの、と言えばイメージが付きやすいと思います。

厳密には用途やUIは異なりますが、Claude Codeで培われた「AIに複数ステップの作業を任せる」という考え方を、非エンジニア向けにも展開したものと見ると理解しやすいでしょう。

正直、Claude Codeを使いこなせている方であれば不要なツールかもしれません。

ただ、Claude Codeの持つ汎用性や技術的インパクトをあらゆる人に展開したという観点では、非常に素晴らしいツールであると個人的には感じています。

また、Claude Codeを培ったノウハウを非技術者の方と共有しやすいという点も、このツールの良いところかと思います。

### Claude for Chrome

Claude for Chromeは、Chrome上のWebページをClaudeに読み取らせたり、ブラウザ上の作業を支援させたりできる拡張機能です。

https://support.claude.com/ja/collections/18031491-chrome%E3%81%AEclaude

Web調査やフォーム入力、業務システム上での作業支援など、Claude CoworkやClaude Desktopと組み合わせることで、かなり「ブラウザ操作エージェント」に近い体験を提供します。

多くの業務ツールは結局ブラウザ上で動いているため、ブラウザを直接操作できるエージェントは汎用性が非常に高いです。

一方で、ブラウザ操作はリスクも大きいため、重要な操作や個人情報、金融取引などに関しては慎重に使う必要がありそうです。

### Claude for Slack

ClaudeはSlackにも連携できます。

Slack上でClaudeを呼び出し、スレッドの要約、返信案の作成、会議準備、チーム内ナレッジの整理などを行える連携機能です。

開発チームでは、SlackからClaude Code関連のタスクにつなげるような使い方も想定されます。

Slackは多くの企業でコミュニケーションの中心になっているため、そこにClaudeが直接入ってくるのはかなり自然な流れですね。

### Claude for Microsoft 365（PowerPoint, Excel, Word, Outlook）

ClaudeはPowerPoint、Excel、Word、Outlook等のMicrosoft 365製品にもエージェントを展開しています。

![スクリーンショット 2026-05-06 0.45.08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/655545/15de6a93-0263-431f-b70f-a6f084295f36.png)

他のClaude製品と同様に、チャット形式のエージェントが常駐し、様々な業務を実行させることができます。

資料作成を始めとして、事務作業全般をClaudeにサポートさせることができるのは、業務効率化の観点でも非常に有用と言えるでしょう。

## 6. 外部連携・拡張

### Connectors

Claudeには、外部サービスと連携するための **Connectors** が用意されています。

代表的なものとしては、以下のようなものがあります。

| コネクタ | できることの例 |
|---|---|
| Google Workspace | Gmail、Google Drive、Google Docs、Google Sheets、Google Calendarなどとの連携 |
| GitHub | リポジトリ、Issue、PR、コード文脈の参照 |
| Microsoft 365 | Outlook、OneDrive、SharePoint、Word、Excel、PowerPointなどとの連携 |
| Slack | Slack上の会話やスレッドとの連携 |
| Custom Connectors | 独自サービスとの連携 |
| Remote MCP | MCP経由で外部ツールやデータソースに接続 |

このあたりは、Claudeを単なるチャットAIから「実際の業務環境に接続されたAI」にするための重要な機能です。

どれだけモデルが賢くても、必要な情報にアクセスできなければ実務では使いづらいです。

その意味で、ConnectorsやMCPは今後かなり重要になると思います。

### MCP

MCPは、Model Context Protocolの略です。

ざっくり言うと、ClaudeなどのAIモデルから外部ツールやデータソースを扱えるようにするためのプロトコルです。

Claude DesktopではローカルMCPを使うことができ、ローカル環境上のツールやデータとClaudeを接続できます。

Claude CodeやClaude Desktop、Coworkなどを横断して考えると、MCPはAnthropic製品群のかなり中心的な拡張レイヤーになっている印象です。

### Organization Skills / Organization Instructions

個人向けのSkillsだけでなく、組織向けには **Organization Skills** や **Organization Instructions** もあります。

これは、組織全体でClaudeに共通の指示や手順を持たせるための機能です。

たとえば、

- セキュリティルール
- ドキュメント作成ルール
- 営業資料のフォーマット

などをClaudeに共有しておくことで、組織全体で出力を揃えやすくなります。

個人利用ではあまり意識しないかもしれませんが、企業導入ではかなり重要な機能ですね。


## おわりに

今回は、Claude関連のサービスをまとめてみました。

昔は単なるモデルプロバイダーだと思っていましたが、いつの間にか様々なサービスを総合的に提供する会社になっていましたね。

また、最近では金融向けのプラグイン等も公開されており、今回紹介した以外にも様々なプラグインやSkillsが提供されています。

https://github.com/anthropics/financial-services/tree/main?tab=readme-ov-file#claude-for-financial-services-plugins

自分たちでAIモデルを作りつつ、その利活用の例をアプリやSkillsといった形式で提供し続けているという点で、単にサービスを利用する以外にも参考になる要素がたくさんありそうです。

## 参考

https://www.anthropic.com/glasswing

https://www.anthropic.com/news/claude-opus-4-8

https://www.anthropic.com/news/claude-design-anthropic-labs

https://support.claude.com/ja/

https://support.claude.com/ja/collections/4078531-claude

https://support.claude.com/ja/collections/14445694-claude-code

https://support.claude.com/ja/collections/5370014-claude-api%E3%81%A8%E3%82%B3%E3%83%B3%E3%82%BD%E3%83%BC%E3%83%AB

https://support.claude.com/ja/collections/15399129-%E3%82%B3%E3%83%8D%E3%82%AF%E3%82%BF

https://support.claude.com/ja/collections/16163169-claude-desktop

https://support.claude.com/ja/collections/18031491-chrome%E3%81%AEclaude

https://support.claude.com/en/articles/13892150-work-across-microsoft-365-apps

https://support.claude.com/ja/collections/9387370-%E3%83%81%E3%83%BC%E3%83%A0%E3%81%A8%E3%82%A8%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%97%E3%83%A9%E3%82%A4%E3%82%BA%E3%81%AE%E3%83%97%E3%83%A9%E3%83%B3

https://code.claude.com/docs/ja/overview

https://github.com/anthropics/claude-code-action
