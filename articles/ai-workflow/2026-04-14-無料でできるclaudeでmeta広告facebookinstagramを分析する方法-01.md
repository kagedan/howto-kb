---
id: "2026-04-14-無料でできるclaudeでmeta広告facebookinstagramを分析する方法-01"
title: "【無料でできる】ClaudeでMeta広告（Facebook/Instagram）を分析する方法"
url: "https://note.com/rips_gh/n/na007ca332ac0"
source: "note"
category: "ai-workflow"
tags: ["note"]
date_published: "2026-04-14"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

みなさんこんにちは。株式会社INVOXの佐藤です。

今回は、Claudeを使ってMeta広告（Facebook広告・Instagram広告）のデータを分析する方法を解説します。

「Meta広告のキャンペーン別パフォーマンスを教えて」と指示を出すだけで実際のMeta広告のデータにアクセスし、高度な分析が一瞬でできるようになります。

![](https://assets.st-note.com/img/1776068516-Bft8Ixd5EA6qUXpr9vV74L1N.png?width=1200)

分析結果（ダミーデータ）

Meta広告は**クリエイティブ（画像や動画）の良し悪しがパフォーマンスに直結**します。

だからこそ「どのクリエイティブが、どの配置面で、どのくらい成果を出しているのか」をサクッと聞ける環境があると、運用の意思決定が速くなります。

ちなみに以前、同じ構成でGoogle広告版の記事も書いています。Google広告のデータも分析したい方はこちらもご覧ください。

  

## Claude×Meta広告分析の全体像（3ステップ）

まず、全体像としては以下のようになります。

![](https://assets.st-note.com/img/1776072539-3OhQmyBNLHRJlKjP2t0bIoWw.png?width=1200)

全体のアーキテクチャ

* **Meta広告**：元となるデータ
* **Fivetran**：Meta広告のデータを分析しやすい形に整形し、BigQueryへ転送するサービス（無料枠あり）
* **BigQuery**：Google Cloudが提供する、データの保管庫（無料枠あり）
* **MCP**：ClaudeとBigQueryを接続する規格
* **Claude**：分析に利用する生成AI。BigQueryと直接接続できるコネクタ機能あり

ClaudeにはBigQueryと直接つながるコネクタ機能が用意されているので、[claude.ai](https://claude.ai/new)の画面からそのまま接続して使えます。

## ClaudeとBigQueryを接続してMeta広告を分析する手順

### 1. Claude・BigQuery・Fivetranの登録

### 2. Meta広告のデータをBigQueryに転送

Fivetranを使ってMeta広告のデータをBigQueryに転送します。

**Destinationの設定**

[Destinations](https://fivetran.com/dashboard/destinations)→「Add destination」をクリックし、「BigQuery」を選択。Setup Guideに沿って設定を実施し、「Save & Test」を実行。

![](https://assets.st-note.com/img/1776068908-1Z3mKW90xLFwzcXkN5yCprtP.png?width=1200)

設定完了画面

> 💡 **ロケーションについて**  
> データの保存場所や計算を行うロケーションの選択画面がありますが、基本的にはデフォルトのUSで問題ありません。しかし、エンプラ企業などセキュリティが厳しい企業ではデータの保管場所を日本に制限する必要がある場合があるので、確認しておきましょう。

**Meta広告コネクタの設定**

次に、Meta広告のデータをBigQueryに転送する設定を行います。[Connections](https://fivetran.com/dashboard/connections)→「Add connection」をクリックし、「Facebook Ads」を選択します。

（Fivetran上では「Meta Ads」ではなく「Facebook Ads」という名称になっています。検索で見つからない場合は「Facebook」で探してみてください。）

![](https://assets.st-note.com/img/1776071206-aT19gxjSkoIFVi280DQtJhKm.png?width=1200)

Connection設定画面

Setup Guideに沿って設定を進めます。途中でMeta（Facebook）アカウントへのログインが求められるので、**広告アカウントの管理権限を持つアカウント**でログインしてください。

認証はOAuth（Facebookログイン）なので、画面の指示に従ってログインし、権限を許可するだけです。APIキーの発行などは不要。複数の広告アカウントを持っている場合は、分析したいアカウントを選択してください。

設定が完了すると、Quickstart transformationの設定画面が出てきます。これは、デフォルトのさまざまなローデータに対して、分析しやすいテーブルを事前に用意してくれる機能です。

**キャンペーン・広告セット・広告単位の集計**がわかりやすい形でまとまっているので、有効にすることをお勧めします。

![](https://assets.st-note.com/img/1776071328-ShUbzC1nyrdDAZE67ajxekBi.png?width=1200)

Quickstart transformationの設定画面

### 3. BigQueryのMeta広告データをClaudeに接続

ClaudeにはBigQueryと直接つながるコネクタ機能があります。Google Cloud側でOAuthクライアントを作成し、Claudeのコネクタ設定に入力するだけで接続できます。

まず、OAuthクライアントを作成します。

これはClaudeがBigQueryに安全にアクセスするための「通行証」のようなものです。

1. Google Cloud Consoleで [Google Auth Platform > クライアント](https://console.cloud.google.com/auth/clients) にアクセス
2. 「クライアントを作成」をクリック
3. アプリケーションの種類：**ウェブ アプリケーション**を選択
4. 名前：何でもOK（例：「BigQuery MCP」）
5. 承認済みのリダイレクトURI：`[https://claude.ai/api/mcp/auth\_callback`](https://claude.ai/api/mcp/auth_callback%60) を追加
6. 「作成」をクリック

![](https://assets.st-note.com/img/1776071418-0b8XUZ3AdxaPoYQpqsHc7tmL.png?width=1200)

作成完了後の画面

作成が完了すると、**クライアントID**と**クライアントシークレット**が表示されます。この2つをメモしておいてください（後でClaudeの設定に使います）。

> 💡 **クライアントシークレットについて**  
> クライアントシークレットはパスワードのようなものです。この画面でしかコピーできないので、必ずこのタイミングで控えておいてください。

**次に、Claudeにコネクタを追加します。**

1. [claude.ai](https://claude.ai/) にログイン
2. 「カスタマイズ」→「コネクタ」→＋ボタンから「コネクタを参照」を開く
3. 以下の情報を入力
4. 「続ける」をクリック

![](https://assets.st-note.com/img/1776071492-nSaLzdjZbvmOU0BMKfw8g9Tl.png)

コネクタ設定画面

追加後、コネクタを有効にするとGoogleアカウントへのログイン画面が表示されます。BigQueryにアクセス権のあるGoogleアカウント（ステップ2でFivetranの転送先に設定したプロジェクトの権限を持つアカウント）でログインすれば、接続完了です。

これでセットアップは完了です！チャット画面で早速Meta広告のデータについて質問してみましょう。

## ClaudeでMeta広告分析してできる3つのこと

Meta広告ならではの分析例を紹介します。

### 1. Meta広告のテーブル構造を理解する

まずはどんなデータが使えるか確認します。

**「facebook\_adsにあるテーブルについて、どんなテーブルが存在するのか教えて。」**

![](https://assets.st-note.com/img/1776071850-S9h7DxfBEFQu52yHC1ZIgbd8.png?width=1200)

実行結果

dbt Packageを有効にしていると、以下のような分析しやすいテーブルが用意されています：

* **アカウントレポート**: アカウント全体の日別パフォーマンス
* **キャンペーンレポート**: キャンペーンごとの日別パフォーマンス
* **広告セットレポート**: 広告セット（ターゲティング）ごとの日別パフォーマンス
* **広告レポート**: 個別広告ごとの日別パフォーマンス（クリエイティブレベル）

**「広告レポートにはどんなデータがある？」**

![](https://assets.st-note.com/img/1776071917-K3NX17qyQsERYnPpvWABrhOa.png?width=1200)

実行結果

個別の広告レポートには、クリック数・インプレッション数・費用・コンバージョン数などの主要指標が日別で入っています。

### 2. クリエイティブ・オーディエンス・予算配分のパフォーマンス分析

Meta広告で一番知りたいのは、**どのクリエイティブが効いているか**ですよね。

**「各広告のクリック率・CPM・CPCを比較して、パフォーマンスが良い広告と悪い広告の特徴を教えて」**

![](https://assets.st-note.com/img/1776072086-1lbi9Wj8eCSqczUs54NX7YAk.png?width=1200)

実行結果（ダミーデータ）

Meta広告は**クリエイティブ（画像・動画）とターゲティングの組み合わせ**が分析の肝になります。Google広告がキーワードの良し悪しを見るのに対して、Meta広告は「どの素材が」「どのターゲティングで」効いているかを見ます。

さらに、Meta広告ならではの分析として：

**「キャンペーン別に、コンバージョン単価とコンバージョン数の推移を月別で見せて」**

![](https://assets.st-note.com/img/1776125442-PJcTvg5O7BdZw6D9fubpQRE8.png?width=1200)

実行結果（ダミーデータ）

Meta広告はキャンペーンの目的（認知・検討・コンバージョン）によってパフォーマンスの見方が変わるので、キャンペーン単位で傾向を把握するのが重要です。

**「広告セット別のパフォーマンスを比較して、どのターゲティングが一番効率がいいか教えて」**

![](https://assets.st-note.com/img/1776125572-35T2wUOyIqtsMo1YPKxlEGrC.png?width=1200)

実行結果（ダミーデータ）

Meta広告の広告セットにはターゲティング情報（オーディエンス）が紐づいているので、「どの層に当てた広告が一番成果が出ているか」がわかります。

### 3. ClaudeでMeta広告レポートを自動生成

**「直近3ヶ月のキャンペーン別パフォーマンスを.md形式のレポートにまとめて」**

![](https://assets.st-note.com/img/1776125724-LOpWNMldgqI0xu8TG6BwUmJe.png?width=1200)

実行結果（ダミーデータ）

レポート全文は[こちら](https://claude.ai/public/artifacts/043e53ef-029b-40c8-885d-875baeea3724)で公開しています。

**「月次のMeta広告パフォーマンスダッシュボードを作成して。インプレッション・クリック・コンバージョン・費用の推移がわかるように」**

![](https://assets.st-note.com/img/1776126035-hMOWIV4QZHns7CgaXBDmNlyE.png?width=1200)

実行結果（ダミーデータ）

ダッシュボード全体は[こちら](https://claude.ai/public/artifacts/182e44c4-abf0-4cd9-a895-419ba3ee1671)で公開しています。

Claudeにレポートやダッシュボードの作成も任せられるので、毎週の定例レポートを手作業で作っている方は、この環境があるだけでかなり楽になると思います。

### 応用編：Claudeのスキルで専属アナリストを作る

ここまでの環境構築ができたら、次はClaudeのプロジェクト機能と「スキル」を使って、もっと実用的にするのがおすすめです。

具体的には、テーブル構造やKPIの定義を「指示書」として事前に設定しておくことで、毎回の前提説明が不要になります。

さらに、週次レポートやキーワード分析などの手順を「スキル」としてファイルにまとめておけば、「今週のレポートを出して」の一言で分析が完結します。

詳しいやり方とすぐに使えるテンプレートは、こちらの記事で解説しています。Google広告版の記事ですが、Meta広告でも同じ仕組みがそのまま使えます。

## おまけ：Google広告と統合してClaudeで分析する

今回の手順でMeta広告のデータがBigQueryに入りました。同じ要領でGoogle広告やTikTok広告のデータも入れられます（FivetranにはTikTok広告やLINE広告のコネクタもあります）。

複数の広告媒体のデータが同じBigQueryに入っている状態で、Claudeに「Google広告とMeta広告の直近3ヶ月のCPAを比較して」と聞くだけで、チャネル横断の分析ができます。

![](https://assets.st-note.com/img/1776126276-FCETNyaLYfBo9I8e5pScrbhn.png?width=1200)

実行結果（ダミーデータ）

広告管理画面を複数開いてスプレッドシートにコピペして…という作業は不要です。**データを一箇所に集めておくと、AIへの質問ひとつで横断分析ができる**。これが一番大きなメリットだと思います。

## まとめ：ClaudeでMeta広告を分析する最短ルート

今回はClaudeでMeta広告のデータを分析する方法をご紹介しました。

Meta広告は**クリエイティブの分析がパフォーマンスに直結する**ので、「どのクリエイティブが効いていて、どこに出していて、誰に当たっているのか」をサクッと聞ける環境は、運用者にとってかなり便利だと思います。

弊社では、より簡単にAIで分析する環境を構築したり、社内のナレッジや業界用語を学習させた分析AIエージェントの開発を行っています。

「自社でもやってみたいけど、セットアップが不安」「複数の広告媒体をまとめて分析したい」という方は、無料相談も行なっておりますのでお気軽にご相談ください。

## 関連記事（AIマーケティング分析シリーズ）

AIマーケティング分析シリーズの記事一覧はこちら
