---
id: "2026-06-30-kiro-にセキュリティ運用を任せるために必要なことaws-summit-japan-2026-セッ-01"
title: "Kiro にセキュリティ運用を任せるために必要なこと〜AWS Summit Japan 2026 セッションレポート〜"
url: "https://zenn.dev/hkdeveloper/articles/kiro-security-ops-aws-summit-2026"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "Python", "zenn"]
date_published: "2026-06-30"
date_collected: "2026-07-02"
summary_by: "auto-rss"
query: ""
---

こんにちは！廣田です。

先日、AWS Summit Japan 2026 に参加してきました！  
今回は数あるセッションの中から、「Kiro にセキュリティ運用を任せるために必要なこと」というセッションが特に印象に残ったので、内容をまとめてご紹介します。

セッション後に登壇者の保里さんに直接質問しに行き、有意義な意見交換ができたのでその内容も最後にご紹介します！

## イベント情報

* イベント名: AWS Summit Japan 2026
* 日時: 2026年6月
* 場所: 幕張メッセ

## 本セッションについて

![本セッションについて](https://static.zenn.studio/user-upload/deployed-images/cdc0848f70044fb7a4e76652.jpeg?sha=5c788f554825bbdeef4b27e63e2f1af47b235cb3)

このセッションの対象者は以下のような方々でした。

* SOC/CSIRT の運用を効率化したいセキュリティエンジニア
* セキュリティ運用の体制ができていないと悩む開発リーダー・ビジネス担当者

セッションのゴールとしては、AIエージェントを活用した効率的なセキュリティ運用の方法を知ること、そして今からすぐにできるセキュリティ対策を始めることが掲げられていました。

Agendaはこちらです。

![Agenda](https://static.zenn.studio/user-upload/deployed-images/86e4e010a79d1d696d416359.jpeg?sha=9eed323c3d66c5dbcd3f94e7822e127102aa33c2)

* セキュリティ運用の課題と AI エージェントの活用
* 基礎編：セキュリティ運用への AI エージェント活用例
* 発展編：コンテキストとルールを定めた運用
* AI エージェントを安全に活用するために
* 最後に

## セキュリティ運用の課題とAIエージェントの活用

### セキュリティ運用の課題

![セキュリティ運用の課題](https://static.zenn.studio/user-upload/deployed-images/560bdfc691b9d1b412a6a39d.jpeg?sha=83e8569ed39825509bdd4be622667de5f1013862)

セキュリティ運用には大きく4つの課題があると整理されていました。

* どのように取り組めばよいのか、全体像がわからない
* セキュリティ運用ができる体制の強化が思うように進まない、人がいない
* 莫大なログやアラートにどう対処したらいいかわからない
* 限られたリソースでも素早く対応し、ビジネス影響を最小限に抑えたい（ダメージコントロール）

この4つ、しっかり運用設計の経験がない私でも容易に想像できるものばかりでした。特に人材不足とログの量の多さは、セキュリティ担当者なら誰もが頭を抱えていそうな課題だと思います。

### AIエージェントによる運用のモダナイズ

![AIエージェントによる運用のモダナイズ](https://static.zenn.studio/user-upload/deployed-images/f2f9297f298af0c2c2e77582.jpeg?sha=acb57088b6e86db535d0d9b0bc6fb9aedc5ca1b1)

これらの課題に対してAIエージェントがどう解決するかが整理されていました。

| 手動による運用課題 | AIエージェントによる解決 |
| --- | --- |
| AWS コマンドやサービスの知識が必要不可欠 | コマンド知識不要で自然言語による指示 |
| 脅威分析と対応に時間を要する | AI 駆動の脅威検出と対応により時間の短縮化 |
| スキルを必要とする属人的な仕事 | 学習コストを大幅に下げ属人性を排除 |
| セキュリティエンジニアの不足 | 人材不足の解消 |
| 複数のサービスやリソースを行き来する横断的な分析が必要 | 分散したサービスやリソースを一元的に分析可能 |

AIエージェント(Kiro)を使うことで、AWSにおいて専門知識がなくても自然言語で指示できる点と、複数サービスを横断して分析できる点が特に魅力的だと感じました！

### AWS DevOps Agent と Kiro の関係

![サーバー運用の効率化をもたらすAIエージェント](https://static.zenn.studio/user-upload/deployed-images/ec3bb81aa77c9c97993731db.jpeg?sha=8253120035409d40a4d8cc9cdbec3dfc2b058937)

サーバー運用を効率化するAIエージェントとして、2つのサービスが紹介されました。

* **AWS DevOps Agent**：自律的インシデント対応に特化した運用の卓越性を実現する自律型AIエージェントサービス
* **Kiro**：開発のためのAIコーディングから、サーバー運用まで幅広く利用可能な汎用型AIエージェント

![AWS DevOps Agentの特徴](https://static.zenn.studio/user-upload/deployed-images/e580eaf5106409cf4e489c1d.jpeg?sha=bb53ad68dd79c319082a6a00cc1542e809ee58b8)

AWS DevOps Agentは主にサービス障害などの可用性に関わる障害対応に最適で、セキュリティインシデント対応までを網羅的にカバーしているわけではないとのことでした。そこでKiroによるセキュリティ運用と補完的に活用できるという話でした。最近、[AWS Security Agent のオンデマンドペネトレーションテストの一般提供を開始](https://aws.amazon.com/jp/blogs/news/aws-security-agent-on-demand-penetration-testing-now-generally-available/)されましたが、より運用面に特化した活動であればKiroを動かすのがいいのかもしれません。

### Kiroの利用形態

![Kiroの利用形態](https://static.zenn.studio/user-upload/deployed-images/c32c0bed185b81e45c3e732d.jpeg?sha=95c54eeb896255861f5e19f25c59bb4db4418fe7)

Kiroはソフトウェア開発から運用全般においてIDEとCLIを提供しています。

* **Kiro IDE**：AI開発エージェントを搭載したIDEアプリケーション
* **Kiro CLI**：CLIからKiroに開発指示を出せるコマンドラインアプリケーション

今回のセッションでは、Kiro CLIを使ってセキュリティ運用を行うシナリオが中心でした。

### KiroによるAWS環境操作の仕組み

![KiroによるAWS環境操作の仕組み](https://static.zenn.studio/user-upload/deployed-images/55620a5d58db957b449c4d08.jpeg?sha=90041357a6952b8880c37bee388dda67739ba617)

KiroがAWS環境を操作する仕組みは3つのルートがあります。

* **ルート1**：Kiro組み込みツール（use\_aws / execute\_bash）→ AWS CLI / AWS Tools and SDKs → AWS API Services
* **ルート2**：ローカルAWS MCP Server（プロセス間通信）→ AWS CLI / AWS Tools and SDKs → AWS API Services
* **ルート3**：クライアントMCP Proxy for AWS → HTTP + SigV4 → リモートAWS MCP Server（AWS Managed Server）

### Kiroを運用に活用する利点

![Kiroを運用に活用する利点](https://static.zenn.studio/user-upload/deployed-images/a23afb61f01a8ff7ef35933a.jpeg?sha=fc72f5fcb3e4cc84aa28047054c43957a19fcb37)

Kiroをセキュリティ運用に活用する利点として、以下が紹介されていました。

* 日常的なセキュリティ運用からインシデント対応までカバー
* 分析と修正方法の提案にとどまらず、人によるレビューを経て対応まで実施させることができる
* 各社のセキュリティガイドラインに則ったカスタマイズされたインシデント対応やセキュリティ運用が可能
* 全てのAWSリソースをKiroという単一チャネルで一元管理できる
* AWS DevOps Agentをも包含した運用が一元的に行える

## 基礎編：セキュリティ運用へのAIエージェント活用例

### 活用例1：定期的なセキュリティチェック

![活用例1 定期的なセキュリティチェック](https://static.zenn.studio/user-upload/deployed-images/e57bb73cc178f37e5bfde734.jpeg?sha=50980ca41889c405bc99eb52200165eaf403d23e)

定期的なセキュリティチェックとして、Kiro CLIに対して次のようなプロンプトを投げます。

> 「AWS環境の重要なセキュリティ検知項目と対応方法を教えて。セキュリティガイドライン違反も教えて。」

これだけで、AWS Systems Manager、Amazon Inspector、AWS Security Hub、AWS Config、AWS IAMを横断的にチェックして結果を返してくれます。

![活用例1 セキュリティチェック結果例](https://static.zenn.studio/user-upload/deployed-images/a6723a64a70c311d22c921fb.jpeg?sha=c8fedf37b5e26af36a00fe84eadad42a1428d07f)

AIの応答では、即時推奨アクションを優先度順に出力してくれていました。例えば以下のような感じです。

1. 🔴 即時：ルートアカウントにハードウェアMFAを設定
2. 🔴 即時：launch-wizard系SGのSSH 0.0.0.0/0を削除
3. 🔴 即時：全ポート公開ルールを内部CIDR制限に変更
4. 🟡 今週：EBSデフォルト暗号化を有効化
5. 🟡 今週：残り3名のIAMユーザーにMFA設定
6. 🟡 今月：未使用Security Groupの棚卸し・削除（60件のレビュー）

優先度が色分けで表示されているのがAIっぽいなと思いました！w  
ただ特にプロンプトで指示していなくても優先度分けしてくれるのは良く推論されているなという印象です。

### 活用例2：AWS WAFルールの分析・最適化

![活用例2 AWS WAFルールの分析・最適化](https://static.zenn.studio/user-upload/deployed-images/d54e62ab745caff0be529dd0.jpeg?sha=2706da3fd2f3b7997e5a928985706e6d58f36e5d)

WAFの運用もKiroで効率化できます。「現状WAFの設定はどうなっていますか？」と聞くだけで、WAFの設定を分析してくれます。

![WAFの設定分析例](https://static.zenn.studio/user-upload/deployed-images/1a0b8325d3a8feaadc5b1697.jpeg?sha=8c39065678155c9838a04890ce5025fa8263d11b)

設定を確認すると、「すべてのルールがCOUNTモード（監視のみ）で動作しています」という重大な問題を即座に指摘してくれていました。

さらに「WAFログから攻撃パターンを見つけて分析してください」と依頼すると...

![WAFログ攻撃パターン分析例](https://static.zenn.studio/user-upload/deployed-images/d13c230790ab0a625c8e6c44.jpeg?sha=639bef6a6e248aaa89c26ef49b545223bd728b7c)

DoS攻撃のパターン（レート制限違反115件検出、攻撃期間約10分間継続）や、Pythonスクリプトによる自動化攻撃（User-Agent: python-urllib3/1.26.19で100%）まで特定し、緊急対応として「WAFルールをBLOCKモードに変更」「攻撃元IPを即座にブロック」などの推奨アクションも提示してくれていました。

手動対応だとWAF専門知識 + ログ分析に数日かかるところが、AIエージェントを使えば自然言語で問い合わせるだけで数分で最適化提案が得られるのは圧巻でした！

### 活用例3：インシデント対応

セッションで一番力が入っていた部分がこのインシデント対応のデモでした。

![NISTインシデントレスポンスプロセス](https://static.zenn.studio/user-upload/deployed-images/e214b4a86d933b7b8f184bf0.jpeg?sha=790ae271e125cd22f3d04d64fe9d631eca05df66)

NISTのインシデントレスポンスプロセスに沿って、Kiroがどこまで支援できるかが示されました。

![セキュリティインシデントレスポンスの効率化 - 手動 vs AI](https://static.zenn.studio/user-upload/deployed-images/273646023c26ee96f58c52b5.jpeg?sha=9e125d4beb2d707147553dac45e189e2b346765c)

手動 vs AIの比較表がとてもわかりやすかったです。

| セキュリティインシデント対応プロセス | 手動による対応 | AIエージェント（Kiro）による対応 |
| --- | --- | --- |
| 検知と分析（GuardDuty / Security Hub / IAM / CloudTrail / Detective） | 各サービスを横断的に一つ一つ個別実行して地道に調査 / ログを手動で突合・分析 | 1プロンプトで全サービス横断分析 |
| 封じ込め（キー無効化 + Denyポリシー） | AWS IAMを使ったGUI/CLI操作を順次実行 | 1プロンプトで実行指示 |
| 影響範囲の確認（不正リソースの特定・停止） | CloudTrail検索により不正リソースの特定・停止操作など複数の操作が必要 | 1プロンプトで実行指示 |
| 根絶/復旧（キーローテーション） | AWS IAMを使ったGUI/CLI操作を順次実行 | 1プロンプトで実行指示 |
| 事後対応（レポート作成） | 手作業でレポート作成 | 1プロンプトでレポートの自動生成 |

実際のデモとして、「GuardDuty で IAM認証情報の侵害が検知されました。どうやってインシデント対応をしたらいいですか？」というプロンプトから始まり、検知と分析 → 封じ込め → 影響範囲の確認 → 復旧 → レポート生成まで一連の流れが示されていました。

封じ込めでは「CompromisedUserのアクセスキーを全て無効化（Inactive）してください」と指示するだけで、アクセスキーの無効化、拒否ポリシーの適用まで実施されます。最終的にはインシデント調査レポートをPDF形式で保存するところまで！

この一連のデモを見て、「すごい...」と思うと同時に、適切な権限設計とレビューの重要性も実感しました。

## 発展編：コンテキストとルールを定めた運用

### AI活用の前提条件：Observabilityの確保

![AI活用の前にObservabilityの確保が大前提](https://static.zenn.studio/user-upload/deployed-images/e98450463209969f7545945b.jpeg?sha=8a173914018dc4d816917b6ddeeca628b745b0fb)

ここで重要なポイントが語られていました。

> **いくら生成AIで効率化しても重要なログの取得がされていなかったり検知機能が有効になっていなければ意味がない**

AI活用の前提として、まず以下のサービスが有効化されていることが必須とのこと。

* AWS Security Hub
* Amazon Inspector
* AWS Config
* AWS CloudTrail
* Amazon GuardDuty

「これらは有効化されていますか？適切にログは取得できていますか？通知は有効化されていますか？」という問いかけが印象的でした。土台なくしてAIエージェントを使っても効果が出ないというのは確かにそのとおりですね。

### アドホックなチャット運用の限界

![AIエージェントのアドホックなチャット運用の限界](https://static.zenn.studio/user-upload/deployed-images/1c5dc293fa8e1ee75ba575b4.jpeg?sha=35939ce39c9dbf739f2f8df4c675c94c15455c84)

基礎編でのデモのように毎回チャットで指示するだけでは、実運用では限界があります。

* AIエージェントは確率論的に振る舞うので毎回方法論も出力結果もフォーマットも同一とは限らない
* 統一的な運用に限界がある
* 毎回同じようなプロンプトを入力する必要がある
* セッション終了時にコンテキストが失われるので、毎回実行時に必要な事前情報をプロンプトで入力し直す必要がある
* 社内の運用ルールやセキュリティガイドラインなどに則った厳密な運用が難しい

この課題に対してKiroは「コンテキストの永続化」と「手順のルール化」で解決できると提示されていました。

### Kiroのコンテキスト永続化と手順のルール化

![Kiroのコンテキストの永続化/手順のルール化](https://static.zenn.studio/user-upload/deployed-images/43e202ee32331dee45d31036.jpeg?sha=882034dd47fce273870361030510122090f5d767)

Kiroには3つの仕組みが用意されています。

| 仕組み | 説明 |
| --- | --- |
| **Agent Steering** | プロジェクトの技術スタック・規約・構造を永続的にAIに伝達。毎回説明し直す必要なし。エージェント自体の動作を規制する共通ルールとガードレール |
| **Agent Skills** | 指示・スクリプト・テンプレートのポータブルパッケージ。Anthropic オープン標準。再利用可能なワークフロー定義 |
| **Kiro Powers** | ドメイン専門知識とMCP接続を動的にロード。必要な知識を必要な時に。ドキュメント + MCP + Steeringをバンドルしたパッケージ |

これにより、ルールに則ったセキュリティチェックが実現できます。

![ルールに則ったセキュリティチェック](https://static.zenn.studio/user-upload/deployed-images/796438b64b19e5ea31f9e06f.jpeg?sha=819d6623ab5a212511d3ef61d0998620ed6a5504)

具体的には、脆弱性管理Skill・設定監査Skill・セキュリティガイドラインSkillと、Agent Steeringによる安全ルール事前定義を組み合わせて、Amazon EventBridgeでのイベント発生時実行やSchedulerでの定期実行も設定できるアーキテクチャが示されていました。

### Skillによる手順のルール化の例

脆弱性管理Skillでは `.kiro/skills/patch-compliance.md` というファイルにワークフローを定義します。

1. AWS Systems Manager Patch Manager 管理インスタンスのパッチ適用状態を確認
2. Amazon Inspector の Findingsを取得
3. Patch Manager + Inspector の脆弱性結果を相関分析、重複排除
4. 優先度分類
5. 重要度の高い Findingsについてエスカレーション

設定監査Skillでは `.kiro/skills/security-audit.md` に、Security Hub / AWS Config / IAM Access Analyzer / Amazon S3パブリックアクセス / 危険なSecurity Groupルール / AWS IAMセキュリティ状態を横断チェックするワークフローを定義します。

セキュリティガイドラインチェックSkillでは Well-Architected Security Pillar、CIS Benchmarks（Security Hub経由でFAILEDを取得）、NIST CSF 2.0の6機能にマッピングして成熟度を5段階評価するといったこともできるとのことでした！

## AIエージェントを安全に活用するために

![Kiroを安全に活用するために](https://static.zenn.studio/user-upload/deployed-images/81e6ffcc74789d993258bc75.jpeg?sha=43f1bf09b6f104fb04706121a594828ca6eb88a3)

セキュリティを強化するAIエージェントが事故を起こしたら元も子もないということで、安全に活用するための6つの原則が示されていました。

1. **AIの出力は必ずレビューしてから適用する**：allow once を選択し出力を必ずレビュー。最終判断と実行は人間が行う（Human in the Loop）
2. **最小権限で動かす**：ReadOnlyプロファイルで起動。Write権限は別セッション・別承認フローで
3. **機密情報をエージェントに渡さない**：シークレットは環境変数 / AWS Secrets Manager。プロンプトに直接書かない
4. **インフラ変更などの破壊的操作の実行は慎重に**：denyByDefault: true に設定。allowCommandsでホワイトリスト化
5. **Steeringでガードレールを事前定義する**：禁止事項・対象環境・エスカレーション基準を明示
6. **調査と対処を分離し段階的に実行する**：Readで調査 → レビュー → 別プロンプトで対処

まとめると **「AIは提案まで、判断と実行は人間が責任を持つ」** ということですね。

### Steeringでガードレールを事前定義する

![Steeringでガードレールを事前定義する](https://static.zenn.studio/user-upload/deployed-images/4b6c7075c69a7515218bbc8f.jpeg?sha=9c897024427306fb4afd9aeb079964bc53cfe72b)

Steeringでは `.kiro/steering/production-safety.md` にガードレールを定義します。主に3つのカテゴリで設定します。

**A. 認証情報・権限**

* ReadOnly / 最小権限の認証情報をデフォルトで使用すること
* Admin認証情報で起動しないこと
* 権限昇格が必要な場合は別セッション・別プロファイルで実施すること

**B. 本番環境の保護**

* 本番か不明なリソースは本番と仮定し、最大限の注意を払うこと
* 本番リソースの変更・削除は明示的なユーザー指示なしに実行しないこと

**C. 操作ルール**

* 非破壊的操作（Read）を優先すること
* 破壊的操作（Delete、Terminate、Modify）の前に必ず確認を求め、影響を説明すること
* 調査（Read）と対処（Write）は別プロンプトで分離すること

「まずは設定しなくても実行環境のIAMを最小権限にしてスモールスタートでKiroを使うことも可能」というアドバイスも参考になりました！

## 今からすぐにできること

![今からすぐにできること](https://static.zenn.studio/user-upload/deployed-images/f94e8aec8809c07fa1fe6493.jpeg?sha=3b551efd6ecadb42780b7ed1b01c2dbbfb78aa4d)

セッションの締めくくりとして「今からすぐにできること」が提示されていました。

1. まずは必要な検知サービスを有効化、必要なログを収集する
   * CloudTrail, VPC Flow Logs, GuardDutyを有効化
   * Security Hubでセキュリティ基準を有効化
   * → **これがAI活用の前提条件**
2. Kiroなどの AI エージェントをインストールして試す
   * 今日お見せした事例はすべてKiroで試せます
   * → **まずはReadOnly権限で始めてみましょう**

段階を踏んで始められるという提案が現実的で良かったです！

## セッション後に保里さんと話したこと

このセッションの後、登壇者の保里さんに直接質問しに行きました！

今回はローカルPC上でKiroを動かしながら使用することを前提とした話でしたが、私が気になっていたのは「これをローカルではなくクラウド上で運用エージェントとして利用するようなことは考えていないか？」という点でした。

結果的に質問ではなく意見交換会と化しましたww

確かに現状そういった運用方法も実現できそうではあるものの、定義ファイルをチームで共有する仕組みがまだ足りていないという課題があります。結論としては、スキルやステアリングの定義はGitHubでチームに共有しつつローカルで実行していくのが現実的な運用として良さそう、という意見で一致しました。

これは Claude Code を使っていてもまさに同じ課題を感じているところで、「チームでどうAIエージェントの定義を共有するか」という問題はまだ発展途上の領域だなと感じました。

## まとめ

今回のセッションを通じて、KiroをAWSのセキュリティ運用に活用するための具体的なイメージを掴むことができました！

特に印象的だったのは以下の点です。

* AIエージェントはあくまで「提案まで」であり、判断と実行は人間が責任を持つという姿勢
* チャットでのアドホック運用には限界があり、SkillとSteeringによるルール化が重要
* AI活用の前に、まずObservabilityの確保（GuardDuty、Security Hubなど）が前提

「まずReadOnly権限でスモールスタート」というアドバイスはとても実践的で、早速試してみようと思っています！

セキュリティ運用にAIエージェントを活用することに興味がある方は、ぜひKiroを触ってみてください！

最後まで読んでいただき、誠にありがとうございました。

## 参考リンク
