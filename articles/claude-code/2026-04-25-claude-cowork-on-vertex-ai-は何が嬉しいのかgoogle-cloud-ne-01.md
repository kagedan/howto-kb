---
id: "2026-04-25-claude-cowork-on-vertex-ai-は何が嬉しいのかgoogle-cloud-ne-01"
title: "Claude Cowork on Vertex AI は何が嬉しいのか：Google Cloud Next ’26 現地メモ"
url: "https://zenn.dev/mbk_digital/articles/db99a38e334462"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "LLM", "zenn"]
date_published: "2026-04-25"
date_collected: "2026-04-26"
summary_by: "auto-rss"
---

[株式会社 MBK Digital](https://www.mbk-digital.co.jp/) 執行役員 CTO の岩尾です。

Google Cloud Next ’26 に参加する中で、Anthropic ブースのセッションは期間中ずっと内容が濃く、かなり学びが多い場でした。MBK Digital でも社内で希望者に Claude を使ってもらっていますし、支援先企業でも Claude を使いたいが導入は Google Cloud の Vertex AI の文脈で考えたい、という相談は十分ありえます。

そうした意味で、今回参加した Enterprise-Ready: Introducing Cowork on 3P はかなり興味深いセッションでした。Claude の新機能そのものだけでなく、企業が Claude を業務エージェントとして導入するときの論点や、Google Cloud の Vertex AI 経由で扱う場合の考え方が見えてきたからです。

![](https://static.zenn.studio/user-upload/deployed-images/c20a1d32e903b48834a4337a.jpg?sha=35ade81d78c5b85439ebd16b3e7820232c49dd25)  
*Anthropic ブースのライブセッション一覧。期間中ずっと関連セッションが続いていた*

この記事では、セッションで紹介されていた Claude Cowork の要点と、特にエンタープライズ導入の観点で気になったポイントを整理します。

## まず Cowork 3P とは何か

この記事で出てくる 3P は third-party deployment の意味です。Anthropic が直接提供する Claude Enterprise として使うのではなく、Amazon Bedrock、Google Cloud Vertex AI、Azure AI Foundry、または企業内の LLM ゲートウェイを経由して Claude Cowork を使う構成を指します。

公式 Help Center では、[Claude Cowork with third-party platforms](https://support.claude.com/en/articles/14680729-use-claude-cowork-with-third-party-platforms) として整理されています。重要なのは、3P 版は単に Claude のモデルだけを Vertex AI で呼ぶ話ではないという点です。Claude Desktop が各ユーザーのマシン上で動き、Cowork のエージェントループ、ローカルファイル操作、MCP 連携などを扱いつつ、プロンプトや補完は企業が選んだ推論プロバイダーにルーティングされます。

つまり、ユーザーから見ると Cowork に長めの仕事を委任する体験ですが、管理や推論経路は企業側の基盤に寄せられます。Anthropic が直接提供する Claude Enterprise と比べると、公式にもサブセットと説明されています。たとえば Chat タブ、アカウント管理 UI、Projects の組織共有、Dispatch / mobile、Skills and plugin marketplace などは 3P 版では提供範囲が異なります。

そのため本記事では、セッションで見た Cowork 全体の方向性と、3P 構成で現実に使える範囲を意図的に分けて書いています。

## Claude Cowork は何なのか

このセッションで紹介されていた Claude Cowork は、ひとことで言うと Claude Code の能力を、非エンジニア業務を含む日常業務へ広げた業務支援ツールです。

従来のチャット型 AI は、質問への回答や下書き支援は得意でも、その後の確認、調査、資料化、ツール操作は人間が続けて行う必要がありました。一方で Claude Code は、開発者向けにより長い作業を実行し、コードやファイルを実際に扱える方向へ進んでいました。

Claude Cowork はその延長線上にある存在として紹介されており、セッションでは次のようなイメージで語られていました。

* 単発の応答ではなく、複数ステップの仕事を Claude に委任できる
* 社内ファイルや SaaS と接続し、必要な情報を取りにいける
* 作業計画、実行、確認までを一連の流れとして扱える

つまり、単発の賢いチャットではなく、情報収集から成果物作成までを進める実務エージェントとして位置づけられていたのが印象的でした。

## 既存システムにつながることが前提になっている

Cowork の特徴として強く押し出されていたのが、既存の業務システムとの接続です。セッションでは Gmail、Google Drive、Figma、Slack などとの連携が紹介されていました。

![](https://static.zenn.studio/user-upload/deployed-images/f392dabd759bc39757eb7a81.jpg?sha=efd2fc7dc299c6be743d96c944a5d3c8d26bfe7b)  
*メール、ドキュメント、タスク管理、コラボレーションツールなどを Claude に接続するイメージ*

これによって Claude は、単にユーザーが貼り付けた情報だけを見るのではなく、メール、ファイル、チャット、ドキュメントといった業務データを横断して必要な情報を集められるようになります。

ただし、ここは少し丁寧に読み分ける必要があります。今回のセッションでは Gmail や Google Drive などの接続例が紹介されていましたが、Cowork on Vertex AI などの 3P 構成は Claude Enterprise と完全に同じ提供形態ではありません。公式 Help Center でも、3P 側は local / remote MCP を中心に説明されており、現地スライドでも `1P Anthropic connectors are not available on Cowork 3P` と明記されていました。したがって、3P では管理者が許可した MCP や MDM 構成を前提に接続範囲を理解するのが適切です。

この方向性はかなり重要だと感じました。実際の業務では、価値が出るのはモデルそのものの賢さだけではなく、社内に散らばった情報へどれだけ自然につながれるかだからです。

特にエンタープライズでは、

* ファイルは Drive や SharePoint にある
* やり取りは Slack やメールにある
* 企画やデザインは Figma にある
* 追加の運用手順は社内文書やテンプレートにある

という形で情報が分散しています。Cowork はそこを前提に設計されているように見えました。

## Skills と Plugins が企業利用の肝になる

もうひとつ面白かったのが、Skills と Plugins の考え方です。

Skills は、チームや組織が持つテンプレート、手順、ベストプラクティスを Claude に教え込むための仕組みとして説明されていました。たとえば、

* 競合調査はこの観点で行う
* 提案書はこのフォーマットで作る
* 稟議用の要約はこの粒度でまとめる

といった、組織独自の仕事のやり方を再利用可能な形で埋め込めます。

さらに、Connectors と Skills を組み合わせて Plugins を作成し、それをチーム全体で共有できるという話もありました。営業向けのアカウント調査、商談準備、コールサマリー作成などが例として紹介されていましたが、ここはかなり実務的です。

![](https://static.zenn.studio/user-upload/deployed-images/f9b89f93116a4481bb554a52.jpg?sha=e596e47f4ee5ade78c67f0f1cd9679ea5d664f9b)  
*Connectors と Skills を組み合わせて Plugins として配布する、という考え方の説明スライド*

エンタープライズ導入では、AI の価値はモデルの IQ だけでは決まりません。むしろ重要なのは、

* 自社の業務手順に合わせられるか
* チームで再利用できるか
* 属人的なうまい使い方を共有資産にできるか

です。Cowork はこの点をかなり意識しているように見えました。

3P 版ではここにも差分があります。公式の [Install and configure Claude Cowork with third-party platforms](https://support.claude.com/en/articles/14680741-install-and-configure-claude-cowork-with-third-party-platforms) では、plugins は各マシン上のローカルディレクトリに配布する構成として説明されています。Claude Enterprise のような marketplace や組織共有そのものが使える、という理解ではなく、管理者がローカル配布・MDM 配布する前提で見るのが正確です。

## 仕事の進め方そのものを Claude に委ねる設計

セッションでは、Cowork が単に命令を受けて返答するのではなく、まず確認質問を行い、作業を計画し、サブタスクに分解し、必要なツールを使って進め、最後に品質確認をする流れが説明されていました。

![](https://static.zenn.studio/user-upload/deployed-images/4062c5eaec29328f040a90a3.jpg?sha=443bae00e7ae7fa8b1d162db96b6c06e658cbbec)  
*Understand → Plan → Execute → Verify → Deliver という Cowork の基本フロー*

この設計は、開発者向けエージェントの考え方がそのままビジネス業務にも降りてきた印象があります。

たとえば実務では、曖昧な依頼をそのまま処理すると後で手戻りが起きます。そのため本来は、

1. 依頼の意図を確認する
2. 何を参照すべきか決める
3. 必要なら複数の情報源を横断する
4. 成果物を作る
5. 出典や根拠を残す

という流れが必要です。

Cowork はまさにそこを製品コンセプトとして押し出していました。個人的には、ここが一番、単なるチャット UI の延長ではないと感じたポイントです。

## デモは取締役会向けブリーフィング作成だった

デモでは、Google Drive 上の `Acme Corporation Q1 2026` フォルダやローカルファイルを参照しながら、取締役会向けのブリーフィングを作成していました。

![](https://static.zenn.studio/user-upload/deployed-images/23c9c424647a22fd6653ade3.jpg?sha=5c8f68433354bbd74c0a03534e60caf1a97f5582)  
*Google Drive 上のフォルダを指定し、ボード向けブリーフィングを依頼している Cowork のデモ画面*

Claude は売上データ、プロダクトロードマップ、顧客フィードバックなど複数の情報源を横断し、次のような内容をまとめていました。

* ボードミーティングで話すべき要点
* 意思決定が必要な事項
* 推奨される次のステップ
* 参照したソース情報

ここで良かったのは、各データの出典を明記させることが重要だと発表者が強調していた点です。エンタープライズで AI を使うと、最終アウトプットの良し悪しだけでなく、その結論はどこから来たのかを後から追えることが非常に重要になります。

社内説明や役員報告ではなおさらで、内容がもっともらしく見えるだけでは足りません。根拠に戻れること、必要なら人間が再確認できることが重要です。これは Cowork に限らず、実業務でエージェントを使う際の重要な設計原則だと改めて感じました。

## Office add-ins も 3P 基盤で使える

セッションでは、Claude for Excel、Claude for PowerPoint、Claude for Word も紹介されていました。

* Excel では、シート分析、セル更新、数式追加、集計表作成
* PowerPoint では、既存資料の編集や新規デック作成
* Word では、文書作成や既存文書の編集、テンプレートに沿ったドラフト作成

特に Excel と PowerPoint は、非エンジニア業務で AI を使うときの主戦場です。

ここは Cowork 本体とは分けて理解する必要があります。公式 Help Center では、[Claude for Excel / PowerPoint / Word with third-party platforms](https://support.claude.com/en/articles/13945233-use-claude-for-excel-powerpoint-and-word-with-third-party-platforms) 自体は 3P をサポートする一方で、Cowork 3P とは直接通信しないと説明されています。

つまり、Office 連携の存在そのものは重要ですが、Cowork on Vertex AI の中でそのまま 1 つの統合体験として動くと読むより、Vertex AI や Bedrock など同じ推論基盤を使える周辺機能群として捉えるほうが正確です。

デモでは、Acme 社の Q1 売上データから地域別 ARR、月次成長率、トップ営業担当者などを整理した新しいシートを作成したり、Q1 ボードレビュー資料をもとに 5 枚構成の取締役会向けデックを作ったりしていました。

このあたりは AI に聞くのではなく、AI が業務成果物を直接作る段階に入っていることをよく示していました。経営企画、営業企画、財務、事業開発あたりの仕事とは特に相性がよさそうです。

## Projects / Live Artifacts は方向性として重要

Cowork には Projects 機能があり、顧客や業務テーマごとにファイルや指示をまとめた作業空間を作れるとのことでした。Claude Chat から作ったプロジェクトを取り込んだり、ローカルフォルダから始めたりできるという説明もありました。

また、Live Artifacts では、Claude が生成した成果物を静的なテキストだけでなく、ライブデータを含む動的な形で扱えることが示されていました。

ただし 3P 版では、公式比較表上 `Projects and org sharing` は not available とされています。ここは Claude Enterprise 側も含めた Cowork 全体の方向性として見るべきで、Vertex AI 版で同じ Projects 共有体験がそのまま使える、という意味ではありません。

ここも重要で、エージェントの成果物は最終的に次のような形に落ちることが多いはずです。

* 読み物としてのメモ
* 共有可能なダッシュボード
* 更新し続ける案件ブリーフ
* チームで再利用する下書きやテンプレート

その意味で、Projects や Live Artifacts は、単発の会話を越えて仕事の文脈を保持するための機能として理解すると分かりやすいと思います。

## スケジュール実行まで入ると、本当に業務委任になる

Cowork では、定期タスクの実行も紹介されていました。たとえば毎朝、カレンダーや未読メールを要約して重要事項を知らせる、といった使い方です。

この機能が意味するのは、ユーザーが都度プロンプトを書く世界から、仕事そのものを定常業務として委任する世界に近づいていることです。

さらに、将来的な Dispatch 機能として、スマートフォンで始めた作業をデスクトップで引き継ぐような話も出ていました。こうなってくると、エージェントは単なる UI 上の bot ではなく、ユーザーと並走する作業主体になっていきます。

一方で、3P 版の公式ドキュメントでは Dispatch and mobile は未提供機能として挙げられています。ここも Cowork が向かっている方向と、3P 版で今日使える範囲は切り分けておく必要があります。

## Vertex AI 上で使えることの意味はかなり大きい

このセッションで、私にとって特に重要だったのは後半の Vertex AI 上での Cowork の話です。

セッションでは、Claude Cowork が Vertex AI 上でも利用可能になったこと、また Anthropic API を直接叩く形だけでなく、自社の Vertex AI や既存の LLM ゲートウェイ経由で推論をルーティングできることが説明されていました。

![](https://static.zenn.studio/user-upload/deployed-images/7e1050a75c05f6afef1a39b4.jpg?sha=7ce582829a98006f5538d1e91f135ad1cafce56b)  
*Claude Enterprise と Cowork on Vertex AI の違いを整理したスライド*

ここはエンタープライズ導入において非常に大きいポイントです。企業によっては、

* すでに Google Cloud を標準基盤としている
* モデル利用は Vertex AI 経由に寄せたい
* 監査やガバナンスの都合で API 利用経路を統一したい
* 複数モデルを既存のゲートウェイでまとめて管理したい

という要件があります。

そのとき、Claude を使いたいが導入経路が別立てになると、調達、運用、監査、ネットワーク、権限管理の話が急に重くなります。Vertex AI 版 Cowork は、その壁を下げる可能性があります。

なお、セッション時点では Vertex AI 版は research preview と説明されていました。一方で、現在は third-party deployment 向けの公式ドキュメントも整備されているため、提供ステータスや利用可能機能は公開時点の公式情報を確認する必要があります。とはいえ、

* ファイルアクセス
* ローカル / リモート MCP
* Skills
* ローカルメモリ
* Web 検索

あたりが使えるという話だったので、企業で PoC や限定導入を始めるには十分に面白い状態に見えました。

実際、Anthropic の公式 Help Center でも third-party deployment は Claude Enterprise のサブセットと整理されており、アカウント管理 UI、Projects の組織共有、plugin marketplace など一部機能は提供範囲が異なります。記事前半で触れた接続やプラグインの話も、この差分を踏まえて読む必要があります。

## セキュリティ説明も中身を見ない方向を強く意識していた

セキュリティとデータ管理についても説明があり、3P 構成では推論時のプロンプトや補完、ファイルや文書の内容、認証情報、MCP サーバー名やツール名、ツール呼び出しの入出力などは Anthropic に送られないという趣旨が強調されていました。

![](https://static.zenn.studio/user-upload/deployed-images/7c807081000972d9a7b566e4.jpg?sha=57b0d3cc7b88cbb5937c484d3c5b12e80404d5d5)  
*Cowork on Google Vertex AI のセキュリティ / データコントロールに関する説明スライド*

一方で、受け取る可能性があるのは匿名ユーザー ID、トークン数、モデル名、ツールの成功・失敗、エラー分類など、限定的なテレメトリのみと説明されていました。公式ドキュメントでも、3P 構成ではプロンプトや補完は推論プロバイダーへルーティングされ、Anthropic には送られないとされています。テレメトリも MDM で無効化可能です。

もちろん、ここは今後の正式ドキュメントや契約条件を精査すべき領域です。ただ、セッション全体を通して感じたのは、Anthropic も企業導入の壁はモデル性能ではなく、接続、統制、データ管理にあることをかなり明確に認識しているということでした。

## まとめ

今回のセッションを通じて感じたのは、Claude Cowork が単なるチャット AI ではなく、社内ツールやファイルと接続しながら、複雑な業務を計画し、実行し、検証する業務委任型エージェントとして設計されていることです。

特に印象に残ったのは次の点です。

* 複数ファイルや業務システムを横断して情報整理できること
* Skills と Plugins により、組織固有の業務手順を組み込めること
* Office add-ins も含め、業務成果物に近い場所で Claude を使えること
* Projects や Dispatch など、単発で終わらない仕事の文脈を持たせようとしていること
* Vertex AI などの 3P 構成により、企業の既存基盤に寄せた導入が見えてきたこと
* ただし 3P 版は Claude Enterprise のサブセットであり、提供範囲を確認しながら設計する必要があること

MBK Digital でもすでに Claude を日常的に使うメンバーが増えてきていますが、今後はどのモデルが賢いか以上に、どの企業基盤にどう乗せるか、どの業務手順をどう組み込むかが差になってくるはずです。

その意味で、この Cowork の話は Anthropic 単体の新機能発表としてだけでなく、企業向け AI エージェントが実験から業務実装へ進みつつあるサインとして見るとかなり面白いセッションでした。
