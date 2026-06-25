---
id: "2026-06-23-mastra-announce-テンプレを使って一気にデプロイ-deployable-templat-01"
title: "[Mastra Announce] テンプレを使って一気にデプロイ！ Deployable Templates"
url: "https://zenn.dev/shiromizuj/articles/63ad0b47ddfc24"
source: "zenn"
category: "construction"
tags: ["prompt-engineering", "API", "AI-agent", "OpenAI", "civil-engineering", "zenn"]
date_published: "2026-06-23"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

[Mastra](https://mastra.ai/) の[公式Blog](https://mastra.ai/blog)で公開された発表をもとに、何が変わったのか、誰に効くのか、どう始めればよいのかを分かりやすく整理します。直訳ではなく、関連ドキュメントと各テンプレートの README も合わせて見ながら、実際に使うときのイメージが湧くように補っています。

[Mastra Announcements 速報解説一覧](https://zenn.dev/shiromizuj/articles/cc91bb06db5b5b)

---

2026年6月22日、Mastra は **Introducing deployable templates in Mastra platform** を公開しました。

今回の発表をひとことで言えば、**Mastra のテンプレートを、単なる雛形コードではなく、実際にデプロイして使い始めるための入口にした**アップデートです。

従来もテンプレート相当のサンプルコードは存在しましたが、そこから自分でリポジトリを切り、環境変数を集め、必要なら DB を作り、Platform に接続し、デプロイ導線を整える必要がありました。今回の deployable templates は、その一連の初期配線を Mastra Platform 側に寄せています。

---

## 今回の発表をひとことで言うと

**「作りたいエージェントの型を選ぶと、GitHub リポジトリ、必要な DB、最初のデプロイがひとかたまりで用意される」** ようになりました。

具体的には、次のことができます。

1. Mastra Platform のダッシュボードからテンプレートを選ぶ
2. Mastra Platform に GitHub リポジトリを作ってもらう
3. Mastra Platform 上の作成フローで、テンプレートが必要とする managed database を選んでプロビジョニングする
4. 同じく Mastra Platform 上で、AI プロバイダや外部 SaaS の API キーを追加する
5. 初回の Studio / Server デプロイを自動で走らせる
6. 以後は GitHub リポジトリ `main` へのマージごとに継続デプロイする

ここでいう「テンプレート」は抽象的な雛形ではなく、たとえば次のような用途別プロジェクトを指します。

* Docs Expert: Web を検索しながら、ライブラリや API の使い方を出典付きで答える調査エージェント
* Company Knowledge Agent: Linear や Notion の内容を取り込み、社内ナレッジを横断検索できる RAG エージェント
* Autonomous Personal Assistant: ファイル操作や shell 実行を含む複数ステップの作業を自律的に進めるアシスタント
* Browser Agent: 実際の Web ページを開き、クリックや入力を伴うブラウザ操作を行うエージェント

重要なのは、今回の主役が新しい Agent API ではないことです。変わるのは **Mastra を試すまでの初期導線** です。コードを書く前のセットアップで止まりやすかった人ほど、恩恵を受けやすい発表です。

---

## 背景: なぜこの発表が必要だったのか

### 「何を作るか」より前に「土台づくり」で止まりやすかった

Mastra のようなエージェントフレームワークを触るとき、最初にやりたいのは本来こういうことです。

ところが実際には、その前に次の作業が入ります。

* どのサンプルを出発点にするか決める
* GitHub リポジトリを用意する
* DB が必要なら外部サービスを用意する
* 環境変数を揃える
* Platform と GitHub をつなぐ
* 初回デプロイが通るところまで持っていく

この「最初の 30 分から数時間」の摩擦は、初学者だけでなく、忙しい実務チームにも重いです。今回の発表は、その摩擦を減らすためのものです。

### 直近の Platform 強化とつながっている

6月16日には Managed Databases が公開され、DB の用意と接続情報の注入が Platform の中でできるようになりました。6月19日には GitHub 連携による自動デプロイが入り、`main` へのマージで Server と Studio を更新できるようになりました。

今回の deployable templates は、その 2 つを onboarding にまとめた形です。

1. テンプレートで出発点を選ぶ
2. 必要な DB を作る
3. GitHub リポジトリを作る
4. 初回デプロイを走らせる
5. 以後は merge-to-deploy で育てる

つまり Mastra は、単にサンプルを配るのではなく、**サンプルから本番っぽい運用導線までを 1 本につなぎ始めた** と見ると分かりやすいです。

---

## 何が追加されたのか

### 1. テンプレートが「そのまま動くプロジェクト」になった

今回用意された 4 つのテンプレートは、どれも単なるコード片ではなく、実際に起動できる Mastra プロジェクトです。エージェント、ツール、必要な統合、クイックスタートまで含んでいます。

現時点の 4 種類は次のとおりです。

ここで大事なのは、テンプレートの価値が「雛形コードがある」だけではないことです。**Mastra Platform がそのテンプレートの前提を理解して、周辺の準備まで肩代わりする** ところに意味があります。

### 2. 必要な managed database を作成フローに組み込める

GitHub integration docs によると、テンプレート作成時には、そのテンプレートが必要とするデータベース要件が表示されます。利用者は provider と region を選ぶだけでよく、Platform がプロビジョニングを行います。

例えば次のような違いがあります。

* Docs Expert は Turso / libSQL 系のストレージで会話状態を持てる
* Company Knowledge Agent は Postgres と `pgvector` を使う前提で、Linear や Notion の内容を埋め込み検索できる
* Browser Agent も Turso を前提にしつつ、ブラウザ操作を組み込める

つまり「テンプレートを選ぶこと」が、そのまま **必要な永続化方式の選択** にもつながります。

### 3. Gateway 系の基本キーは初回から自動投入される

ドキュメントでは、`MASTRA_GATEWAY_API_KEY` と `MASTRA_PLATFORM_ACCESS_TOKEN` は Platform 側で自動投入されると説明されています。これにより、Mastra Gateway を使うテンプレートは、最初のデプロイ時点で動きやすくなります。

一方で、すべてが完全自動になるわけではありません。テンプレート固有の外部連携キーは引き続き自分で入れる必要があります。

* Company Knowledge Agent なら `LINEAR_API_KEY` や `NOTION_API_KEY`
* Browser Agent や Docs Expert なら必要に応じてブラウザや AI プロバイダ周辺の設定
* Autonomous Personal Assistant ならブラウザやワークスペース運用に関する設定

要するに、**Mastra 共通部分は自動化し、あなたの業務固有部分は手で与える** という分担です。

### 4. 初回デプロイまで自動で進む

テンプレートからプロジェクトを作ると、Platform はリポジトリ作成、`.mastra-project.json` の書き込み、DB の作成、初回の Studio / Server デプロイまでまとめて実行します。しかも初回デプロイは DB の作成完了を待ってから走るため、最初のビルド時点で接続情報が見える設計です。

これは見た目以上に大きいです。よくある失敗は「コードはあるのに、最初のデプロイだけ通らない」だからです。今回の仕組みは、そこをかなり減らします。

---

## どんな人にとって、どんなことが可能になるのか

### 1. Mastra を初めて触る個人開発者

いちばん分かりやすいのはこの層です。たとえば「Mastra で何が作れるのかまず見たい」人は、Docs Expert から始めると理解しやすいはずです。

可能になることの例:

* ライブラリや API の使い方を調べる出典付きアシスタントを、最初から動かして触れる
* ローカルでゼロから構成を組まずに、Platform に載る前提のプロジェクト構成をそのまま眺められる
* `main` へ修正をマージしたら再デプロイされる流れまで含めて学べる

具体例としては、「OpenAI SDK の `webSearch` 周りを調べたい」「Node 22 と 20 の差分を質問したい」といった用途です。これまではまず検索ツールや保存先を配線しなければなりませんでしたが、テンプレートならそこを飛ばして質問から入れます。

### 2. 社内向け検索を早く形にしたい小規模チーム

Company Knowledge Agent は、PM、情シス、開発マネージャー、社内問い合わせ対応チームに向いています。Linear と Notion をまたいで答える RAG エージェントが、最初から 1 つの型として置かれているからです。

可能になることの例:

* 「先週 onboarding 周りで誰が何を決めたか」を Linear と Notion 横断で聞ける
* 定期的な再インデックスを含む知識更新フローを短時間で試せる
* `pgvector` 前提の実装例を、RAG 設計の叩き台としてそのまま流用できる

特に、RAG のサンプルコードだけ欲しいのではなく、**Studio で試せて、GitHub 管理されて、再デプロイされる形** まで最短で持っていきたいチームには相性が良いです。

### 3. 業務自動化を試したい開発者や運用担当

Autonomous Personal Assistant と Browser Agent は、ファイル操作、シェル実行、ブラウザ操作を含む agentic な動きの出発点になります。

可能になることの例:

* ブラウザを開いて情報収集し、その結果を整理するエージェントを試す
* サンドボックス環境でファイル編集やコマンド実行を行う自律エージェントを検証する
* Playwright ベースのブラウザ操作や、Mastra の browser tool 群の使い方を実例から学ぶ

具体例としては、「競合 3 社の価格ページを見て差分をまとめる」「社内検証用の sandbox でファイルを編集して整形する」といった用途が考えやすいです。ゼロから browser tool や workspace 制約を組むより、動くテンプレートから削る方がずっと速いです。

---

## まずはどう始めるか

ここからは、今回の発表を実際に試すための最短手順を、ドキュメントに沿って具体化します。

### 手順 1. Mastra GitHub App をインストールする

1. Mastra Platform ダッシュボードの Organization Settings を開く
2. GitHub App セクションから Install GitHub App を選ぶ
3. インストール先の GitHub アカウントまたは Organization を選ぶ
4. App がアクセスできるリポジトリ範囲を決める

組織に対して非管理者が申請する場合、GitHub 側で admin 承認待ちになります。ここで詰まる可能性があるので、業務利用なら最初に管理者承認フローを確認しておくのが安全です。

### 手順 2. Create project から Start from a template を選ぶ

1. ダッシュボードで Create project を押す
2. Start from a template を選ぶ
3. テンプレートを 1 つ選ぶ

選び方の目安は次のとおりです。

* Docs Expert: まず Web 検索エージェントを試したい
* Company Knowledge Agent: 社内ナレッジ検索を作りたい
* Autonomous Personal Assistant: ファイル操作や shell 実行を含む自律タスクを試したい
* Browser Agent: 実ページ操作を伴う agent を試したい

### 手順 3. GitHub リポジトリの作成先を決める

1. 新規リポジトリを所有する GitHub アカウントを選ぶ
2. リポジトリ名を決める
3. private にするか public にするかを選ぶ

ここで Mastra がリポジトリを作ってくれるため、自分で空リポジトリを用意して import する必要はありません。

### 手順 4. テンプレートが要求する DB を設定する

1. 必要な managed database の要件を確認する
2. provider を選ぶ
3. region を選ぶ
4. 作成内容を確定する

雑に決めず、次の観点で選ぶのがよいです。

### 手順 5. テンプレート固有の環境変数を入れる

ここはテンプレートごとに違います。例えば:

* Company Knowledge Agent: `LINEAR_API_KEY`, `NOTION_API_KEY`, `DATABASE_URL` 周辺の確認
* Browser Agent: 必要なら `BROWSER_CDP_URL` や headless 関連設定
* Docs Expert: 手元で試すなら `.env` とクイックスタートに従って必要キーを補う

ただし、Mastra Gateway 系の基本キーは自動投入されるので、毎回そこから設定しなくてよいのが今回の利点です。

### 手順 6. Create project を実行して初回デプロイを待つ

1. Create project を押す
2. Platform がリポジトリ作成、`.mastra-project.json` 書き込み、DB 作成、初回 deploy を行う
3. Setup 画面で Studio / Server の状態を確認する
4. ログを見て初回起動を確認する

もし DB が必要なテンプレートなら、初回 deploy はプロビジョニング完了後に始まります。ここは手動構成より安心できるポイントです。

### 手順 7. コードを少し変えて `main` にマージし、継続デプロイを確認する

テンプレートが立ち上がったら、次は必ず小さな変更を入れて `main` にマージしてみるとよいです。例えば:

* system prompt を 1 行だけ変える
* モデル ID を変える
* 説明文やサンプル質問を変える

そうすると、「テンプレートを作った」だけで終わらず、**GitHub 管理の実運用導線に本当に乗っているか** まで確認できます。

---

## 既存手法との違い

今回の発表は、「テンプレートが増えた」だけと見ると小さく見えます。ですが本質はそこではありません。

以前の流れ:

* テンプレートやサンプルコードを見つける
* 自分でリポジトリを作る
* DB を外部で作る
* 環境変数をつなぐ
* Platform と GitHub を接続する
* 初回 deploy を通す

今回の流れ:

* Platform でテンプレートを選ぶ
* 必要な DB を選ぶ
* 必要な外部 API キーだけ入れる
* 初回 deploy まで進める
* 以後は merge-to-deploy

つまり、**自分で配線すべき範囲が、アプリ固有の部分へかなり絞られた** ということです。

---

## 注意点

### 1. 完全自動ではない

テンプレートごとの外部サービス連携は、当然ながら自分の API キーや認証が必要です。特に Company Knowledge Agent は Linear / Notion 接続が前提なので、社内利用では権限設計も含めて考える必要があります。

GitHub integration docs では、self-hosted GitHub Enterprise は非対応です。GitHub.com ベースで使う前提になります。

### 3. テンプレートは完成品ではなく出発点

テンプレートはすぐ動きますが、そのまま本番完成という意味ではありません。実際には、モデル選定、権限制御、監視、プロンプト調整、データ設計などを自分の要件に合わせて詰める必要があります。

とはいえ、そこは欠点というより役割分担です。今回の発表は **「何を作るか」の前に必要だった土木工事を短くする** ことに価値があります。

---

## まとめ

Deployable templates は、Mastra のサンプル群を「読むもの」から「そのまま始めるもの」へ引き上げた発表です。GitHub リポジトリ作成、managed database の準備、初回デプロイまでがひとかたまりになったことで、特に初学者、小規模チーム、社内 PoC を急ぎたい人に効く更新になっています。

Docs Expert のような軽めの調査エージェントから始めてもよいですし、Company Knowledge Agent のように業務に近いテンプレートから入ってもよいです。重要なのは、今回から Mastra Platform が **テンプレート選択から継続デプロイまでの最短ルート** を product surface として明示し始めたことです。

---

## 参考リンク
