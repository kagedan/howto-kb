---
id: "2026-05-29-tableau-mcpの世界にがっつり踏み込む前に今一度mcpの基本をおさらいしておく-01"
title: "Tableau MCPの世界にがっつり踏み込む前に、今一度MCPの基本をおさらいしておく"
url: "https://zenn.dev/truestar/articles/a107673805a86e"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "prompt-engineering", "API", "AI-agent", "LLM"]
date_published: "2026-05-29"
date_collected: "2026-05-30"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/80c614bdd49a-20260529.png)

個人的「Tableau MCP界隈の情報整理をしてみよう」シリーズ第3弾。下記第1弾では、製品レベルの整理を行いました。

そして第2弾ではTableauとSalesforceの動向を中心に、Tableau MCPを取り巻く状況がどういう経緯を経て今の状態になっているのか、についてまとめました。

---

最近は仕事に、そして生活に欠かせない(？)ものとなりつつある生成AI。ことデータ分析に於いてもその流れは留まることを知らず、Tableauについても先に開催された「Tableau Conference 2026」で更なる生成AIとの連携方針が大々的にアナウンスされていました。

これを踏まえて私自身も直近、Tableauを含めた様々な生成AI、その中のMCPという規格、サービスにその調査実践リソースを割くようになりました。ですが実のところ、MCPについては"何となく"の意識で触っていた部分もあり、どういう仕組みや分類が為されているのかについてはそこまで強い意識を持っていませんでした。

というのもあり、当エントリでは改めて「MCP」とは何か、MCPの仕組みや概念等をおさらい、学習し直して今後の活動に役立てようと思い、その内容をまとめておこうと思います。

## Part1: MCPの全体像を掴む

### 1. MCPとは何か

**MCP(Model Context Protocol)は、AI(特にClaudeやChatGPTのようなLLM)が外部のツールやデータと"会話"するための共通規格です。**

公式の説明を借りると、MCPは「**AI向けのUSB-Cポート**」と表現される事が割と引用されています。USB-CがどのメーカーのPCにもどの周辺機器にもつながる共通端子であるのと同じように、MCPは「どのAIアプリ」と「どのデータソース・ツール」も共通の作法でつなげるようにする標準です。

![](https://static.zenn.studio/user-upload/515bd67d3131-20260528.png)  
*引用：[Notion MCPの解説｜Notion](https://notion.notion.site/Notion-MCP-1d0efdeead058054a339ffe6b38649e1)*

#### MCPを使うと何が嬉しいのか(MxN問題の解消)

MCPが登場する前、AIに外部ツールやデータをつなぐには「**AIアプリの数 × ツールの数**」だけ個別の接続コードを書く必要がありました。たとえばAIアプリが3つ、ツールが10個あれば30本の連携を作る必要があるという話です。

MCPはこれを「**AIアプリの数 + ツールの数**」に変換します。ツール側は「MCPサーバ」を1つ用意すれば、MCP対応のすべてのAIアプリから使えるようになる。AIアプリ側は「MCPクライアント」を1つ実装すれば、世にあるあらゆるMCPサーバを呼び出せる。

掛け算が足し算に変わる、というのがMCPの最大の価値です。

#### 登場人物3者

MCPの世界には3種類の主役がいます。詳しくはPart2で扱いますが、ここで先に名前だけ押さえておきます。

| 登場人物 | 役割 | 具体例 |
| --- | --- | --- |
| **MCPホスト** | AIアプリそのもの。 クライアントを束ねる | Claude Desktop, ChatGPT, Cursor, VS Code |
| **MCPクライアント** | ホストとサーバを つなぐ接続役 | ホストの中に内蔵されている |
| **MCPサーバ** | AIに「使わせたい道具・データ」 を提供する側 | GitHub, Slack, Google Drive など |

### 2. なぜ今MCPが重要なのか - 業界動向を追う

MCPは2024年11月にAnthropicがオープンソースとして公開した、まだ1年半ほどの若い規格です。にもかかわらず、**業界の主要プレイヤーがほぼ全員参加する事実上の標準になりました。** タイムラインを追うとそのスピードがわかります。

#### MCP年表

| 年月 | 出来事 |
| --- | --- |
| 2024年11月 | Anthropicが MCP を公開(Python・TypeScript SDK同時リリース) |
| 2025年03月 | OpenAIが Agents SDK・Responses API・ChatGPT Desktopで MCP対応を発表。Sam Altmanが「人々はMCPを愛している。 我々の製品全体でサポートを追加できることを嬉しく思う」と表明 |
| 2025年04月 | Google DeepMindのデミス・ハサビスCEOがGeminiでのMCP対応を表明 |
| 2025年05月 | Microsoft Build 2025でGitHubとMicrosoftが MCPのステアリングコミッティに参加。 Windows 11へのMCP統合も発表 |
| 2025年09月 | 公式の MCP Registry(サーバの中央インデックス)が公開 |
| 2025年11月 | 大規模仕様アップデート(非同期処理、ステートレス対応、サーバアイデンティティなど) |
| 2025年12月 | AnthropicがMCPをLinux Foundation配下の **Agentic AI Foundation(AAIF)** に寄贈。 Anthropic・OpenAI・Blockが共同設立者、Google・Microsoft・AWS・ Cloudflare・GitHub・Bloomberg が支援メンバーとして参画 |
| 2026年現在 | Python/TypeScript SDKだけで月間 約9,700万 ダウンロード。 アクティブな公開 MCP サーバは1万件以上 |

#### なぜこれほど早く広がったのか

理由は大きく3つ。

* **AIエージェント時代の到来**：
  + AIが「答える」だけでなく「実際に作業する」段階に入り、外部システムと安全につながる標準的な作法が業界全体で必要になっていました。
* **オープン性**：
  + Anthropicは公開当初からプロトコル仕様・SDK・サンプル実装をすべてオープンソース化し、競合のOpenAIやGoogleが採用することに抵抗のない設計にしました。
  + さらに2025年12月にLinux Foundationに寄贈することで「特定企業の標準」ではなく「業界の共通インフラ」になりました。
* **早期の参考実装**：
  + Block、Apollo、Stripe、Cloudflare、GitHub、JetBrains などが早期に MCP サーバを公開し、「使える」状態が即座にできあがったこと。これにより様子見していた企業も一気に追随しました。

#### 業界での位置づけ

NVIDIAのJensen Huang CEOはMCPについて「AIランドスケープを完全に革命した」と発言。BCG の分析では「MCPがなければ統合の複雑性は二次関数的に増えるが、MCPがあれば線形に収まる」と表現されています。

**OAuthが認証認可の標準になったように、MCPが"AI と外部システムの接続"の標準になりつつある、** と理解するのが今の業界の総意です。

### 3. 具体例・ユースケース

#### 3-1. 実際のMCPサーバの例(公式提供)

ベンダーやサービス提供者が自社のサービスにアクセスするためのMCPサーバを出しているケースです。これがエコシステムの中核です。

| サービス | できること | 提供形態 |
| --- | --- | --- |
| **GitHub** | リポジトリの読み書き Issue/PR操作 コード検索 | リモート(公式) ローカル |
| **Slack** | メッセージ送受信 チャンネル操作 | リモート(公式) |
| **Notion** | ページ作成・更新 データベース操作 | リモート(公式) |
| **Google Drive** | ファイル検索・取得 | リモート(公式) |
| **Stripe** | 決済データ参照 サブスクリプション操作 | リモート(公式) |
| **Atlassian (Jira/Confluence)** | チケット操作 ドキュメント検索 | リモート(公式) |
| **Salesforce** | レコード検索・作成・更新 | リモート(公式) |
| **HubSpot** | コンタクト・取引管理 | リモート(公式) |
| **Tableau** | データソース・ワークブック操作 Pulse連携など | リモート ローカル |
| **Snowflake** | データウェアハウスへの 問い合わせ・分析 | リモート ローカル |

これだけでも「AIアシスタントに普段の業務システムを直接触らせる」絵が浮かびます。

#### 3-2. クライアント側の具体例

逆に「MCPサーバを呼び出す側」の代表例は以下の通り。

* **Claude Desktop / Claude.ai**：
  + Anthropicが提供するチャットアプリ。設定で複数のMCPサーバを束ねて使える
* **Cursor / Windsurf**：
  + AIコーディングエディタ。GitHubやLinearなどのMCPサーバを直接呼び出す
* **VS Code(GitHub Copilot Chat)**：
* **ChatGPT(Desktop / Custom Connectors)**：
* **Microsoft Copilot Studio**：

「同じMCPサーバが、Claude DesktopでもCursorでもChatGPTでも使える」というのが、まさにMCPが標準であることの恩恵です。

#### 3-3. データ分析・BI文脈での例

データ分析やBIの世界もMCPの恩恵を大きく受けている領域です。

* **Tableau MCP**：
  + Tableau上のデータソース・ワークブック・メトリクスにAIから直接アクセス。「先月の売上を地域別に分解してほしい」とClaudeに頼むと、Tableauに問い合わせて結果を返す
* **Snowflake MCP**：
* **PostgreSQL / MySQL MCP**：

「BIツールの画面を開いて手動で操作する」という従来のスタイルが、「自然言語でAIに分析を依頼すると、AIがBIに問い合わせて答えを持ってくる」という体験に置き換わりつつあります。

#### 3-4. 業務自動化・社内ツール連携の例

* **「毎週月曜の朝、先週のGitHub PR一覧をまとめてSlackに投稿」**：
  + GitHub MCP + Slack MCP を Claude で束ねる
* **「問い合わせメールの内容からJiraチケットを自動起票」**：
  + Gmail MCP + Atlassian MCP
* **「Confluenceの議事録を参照して関連タスクを洗い出し、Notionにまとめ直す」**：
  + Confluence MCP + Notion MCP

事例として公開されているものでは、**Microsoftの社内Sales Development Agent**(Dynamics 365に MCP で接続するAIエージェント)が、2025年1〜11月の61,734件のリードに対して **「リード→案件化のコンバージョン率を15.1%改善」** した、という数字が出ています。複数のMCPサーバを束ねた「エージェント」が業務効率を実数値で押し上げ始めている、という段階にあります。

## Part2: MCPの仕組みを理解する

ここから先は「もう少し技術的に踏み込みたい人」向けの内容です。Part1の理解で「MCPって何？」には答えられるようになりますが、自分で動かす段になるとPart 2以降の理解が必要になります。

### 4. MCP仕様の中身

#### プロトコルの基本構造

MCPは **「JSON-RPC 2.0」** というシンプルなメッセージ形式の上に作られています。クライアントとサーバが構造化されたメッセージをやり取りする、という素直な作りです。

通信は**2つの層**に分かれています。

* **データ層(Data Layer)**：
  + 何をやり取りするかを決める層。ライフサイクル管理、ツール、リソース、プロンプト、通知などの定義
* **トランスポート層(Transport Layer)**：
  + どうやり取りするかを決める層。接続確立、メッセージのフレーミング、認証など

データ層は共通で、トランスポート層が「ローカルか／リモートか」で切り替わります。これはPart3の6章で詳しく扱います。

#### 三者構造の詳細

Part1で名前だけ出した3つの登場人物を、もう少し精密に定義します。

* **MCPホスト**:
  + ユーザが直接触るAIアプリ。複数のMCPサーバを束ねる役割
* **MCPクライアント**：
  + ホストの中に、「接続するMCPサーバ1台につき1つ」生成される。サーバとの会話を維持する
* **MCPサーバ**：
  + 「使える機能（ツール）」「参照できるデータ（リソース）」「使えるテンプレート（プロンプト）」を提供する独立したプログラム

#### MCPサーバが提供する3つの"プリミティブ"

サーバが提供できるものは、仕様上3種類に分類されます。

| プリミティブ | 内容 | 例 |
| --- | --- | --- |
| **Tools (ツール)** | AIが実行できる関数。 引数を渡すと結果が返る | `search_github_issues(query)`, `send_slack_message(channel, text)` |
| **Resources (リソース)** | AIが参照できるデータ。 ファイルやDBレコードなど | `file://project/README.md`,  `db://customers/12345` |
| **Prompts (プロンプト)** | 再利用可能なプロンプトテンプレート | `code_review_prompt`,  `weekly_report_prompt` |

実運用では**Tools**が圧倒的に多く使われています。

### 5. MCPを使うために必要なもの

「MCPを試してみたい」と思った時に、何を揃えれば動くのか、を整理します。

#### 利用者(消費する側)として使う場合

これが大多数のケースです。「ClaudeでGitHub操作したい」のような利用シーン。

必要なのは以下の3つ。

* **MCP対応のクライアント(ホスト)**：
  + Claude Desktop、Cursor、ChatGPTなど
* **使いたいMCPサーバの接続情報**：
* **認証情報**：
  + そのサーバが外部サービスにアクセスする際に必要なAPIキーやOAuthトークン

たとえばClaude DesktopでGitHub MCPを使う場合は、設定ファイル(`claude_desktop_config.json`) にGitHub MCPサーバの起動コマンドと GitHub Personal Access Tokenを書くだけで動きます。

#### 提供者(自前で MCP サーバを作る側)として使う場合

ここはエンジニア向けの話として展開。

* **対応言語のSDK**：
  + Python・TypeScript・Java・Kotlin・C#・PHP・Goなど、主要言語にSDKがあります
* **サーバを動かす場所**：
  + 利用者と同じマシン(ローカル)か、ネット越しのサーバ（リモート）か
* **認証認可の設計**：
  + リモートで配るなら OAuth 2.1 の実装が事実上必須

## Part3: MCPを自分で動かす

ここから先は「自分でセットアップする」「自分でサーバを作る」段階で必ず引っかかる論点です。実際に手を動かす場面で立ち返って読む形を想定しています。

### 6. MCPサーバの種類 - ローカルサーバ vs リモートサーバ

#### 2つのトランスポート

MCPの仕様には、サーバとの通信方法が2種類あります。

| トランスポート | 通信方式 | 動く場所 |
| --- | --- | --- |
| **stdio** | 標準入出力(プロセス間通信) | 利用者と同じマシン上 (ローカル) |
| **Streamable HTTP** | HTTP POST +  必要に応じてServer-Sent Event | ネット越し (リモート) |

#### ローカルMCPサーバとは

**stdioトランスポート**を使うMCPサーバを指します。挙動は以下の通り。

* 利用者のPC上で、クライアント（例：Claude Desktop）がサーバプログラムを 子プロセスとして起動
* 標準入力・標準出力を使ってJSON-RPCメッセージをやり取り
* クライアントが終了するとサーバプロセスも終了

特徴は以下の通り。

* **設置が簡単**: 設定ファイルにコマンドを書くだけで動く
* **認証がシンプル**: ローカルマシンの環境変数や認証情報をそのまま使える
* **ネットワーク非依存**: 速い、外に出ない
* **デメリット**: 1人ずつ自分のマシンに入れる必要がある。チームで共有しにくい

#### リモートMCPサーバとは

**Streamable HTTPトランスポート**を使うMCPサーバ。Webサービスとして公開されており、クライアントはHTTPで接続します。

特徴は以下の通り。

* **どこからでも使える**: ブラウザベースのAIアプリ（Web版Claude、ChatGPTなど）からも接続可能
* **複数ユーザで共有**: 1つのサーバを多人数で利用
* **OAuth 2.1 による認証**: ブラウザ経由のログインフローでセキュアに接続
* **デメリット**: ホスティング・認証・運用の手間が発生する

#### どちらを選ぶか

業界で言われているシンプルな指針はこれです。

> **「サーバの動くマシンを、AIクライアントの利用者本人が管理しているなら stdio（ローカル）。そうでなければ Streamable HTTP（リモート）。」**

ローカルファイルやローカルDBを触る道具なら stdio、SaaS や社内サーバの中身を触る道具ならリモート、という分類とほぼ重なります。

#### できること・できないことの比較

| 観点 | ローカル (stdio) | リモート (Streamable HTTP) |
| --- | --- | --- |
| 設置・配布 | 利用者ごとにインストールが必要 | URLを共有するだけ |
| 利用できるクライアント | デスクトップアプリ中心 | デスクトップ・Web・モバイル全部 |
| 認証 | ローカル環境変数・APIキー | OAuth 2.1 が標準 |
| 共有・スケール | 個人利用向け | チーム・全社・社外提供向け |
| ローカルリソース | ファイル・ローカルDB・ローカルコマンドにアクセス可 | 原則不可 (サーバ側のリソースのみ) |
| 構築コスト | 低い | 認証・ホスティングの実装で中〜高 |
| 通信パフォーマンス | ネットワークなしで最速 | ネットワーク越し |

#### Tableau MCPは現状、どちらに対応している？

これらを踏まえるとTableau MCPは現状、どちらに対応しているのでしょうか？

公式Tableau MCPの公開ドキュメントでは、AIクライアントが `node` あるいは `docker run -i` でサーバープロセスを起動する構成のみが案内されており、`config.stdio.json` という名称も使われているため、少なくとも**現行の公式情報からは stdio transport 前提のローカル実行型 MCP サーバーと解釈するのが妥当**です。

ただし**既定がstdioというだけで、`TRANSPORT=http` を指定すれば Streamable HTTP サーバとして起動でき、公式も `config.http.json` テンプレートを用意しています。** (Tableau Cloud向けのクラウドホスト型は2026.2提供予定とされており、現状は自前ホストが前提)

### 7. ローカルしか提供されていない場合の選択肢

「使いたいMCPサーバがローカル版しか出ていないが、チームで共有したい」という状況はよく発生します。この場合に取れる選択肢を整理します。

#### 選択肢A: ベンダーがリモート版を出すのを待つ

最も安全で楽な道。主要ベンダーは順次リモート版を提供しているので、急がないなら待つのも手。

#### 選択肢B: 自前でリモート化する

待てない場合の選択肢で、いくつかパターンがあります。

##### B-1. Cloudflare Tunnel で公開する

最も手軽な方法のひとつ。ローカルで起動しているMCPサーバを、Cloudflare の Tunnel 経由でインターネットからアクセス可能なURLに変換します。

* メリット:
  + **インバウンドポートを開けなくていい**: Tunnelは内側から外向きに接続する仕組みなので、社内ファイアウォールに穴を開けずに済む
  + **Cloudflare Accessと組み合わせれば認証も追加可能**: 特定のユーザだけアクセス可、というポリシーを後付けできる
  + **無料枠で試せる**
* デメリット:
  + 元のMCPサーバ自体は1台のマシン上で動いているので、そのマシンが落ちれば全員使えなくなる
  + スケーラビリティは限定的

##### B-2. プロキシ/ゲートウェイで stdio を HTTP 公開する

`mcp-proxy`(SSE to stdioモード) や `supergateway` で、ローカルstdioサーバを  
HTTPエンドポイント化でき、リモート専用クライアントから到達可能になる。

##### B-3. Cloudflare Workers などのサーバレス基盤で再実装する

ローカル MCP サーバの実装を参考に、Cloudflare Workers / AWS Lambda / Vercel などのサーバレス環境上に**リモートMCPサーバとして自前で立て直す**やり方です。

Cloudflare の場合、Agents SDK という公式ライブラリがあり、認証認可（OAuth 2.1）を含めたリモートMCPサーバを比較的少ない労力で構築できます。

* メリット:
  + スケールに強い
  + 認証フローを正しく実装できる
  + 複数ユーザでの利用が前提
* デメリット:
  + 開発工数が発生する
  + 元のMCPサーバが依存するローカルリソース(ファイル、ローカルDB)を使う場合、設計の作り直しが必要

##### B-4. MCP Gateway / MCP Portal を使う

新しいパターンとして、複数のMCPサーバを束ねてリモート化する「ゲートウェイ」型のサービスが出てきています。Cloudflare の MCP Server Portals、Apigene などが代表例です。

複数のローカルMCPサーバを1つのリモートエンドポイントに集約し、認証も一元化できます。エンタープライズ用途では今後この形が主流になりそうです。

##### 推奨ルート(暫定)

現時点では以下が妥当な選択肢になりそう。

* 個人検証・小規模PoC段階 → **B-1（Cloudflare Tunnel）**
* 本番運用や社外提供を見据える → **B-3(Workers等での再実装)** or **B-4(Gateway利用)**

## Part4: MCPクライアントについて

### 8. 「クライアント」という言葉の整理

ここではMCPクライアント、その中で今回扱うテーマである「Tableau MCP」に対応している、またはしてそうなものを取り上げてみます。

「クライアント」という言葉は仕様上の意味と通称が少しズレるので、まずそこを整理します。

#### 仕様上の「クライアント」と、世間で言う「クライアント」

* **仕様上のクライアント**: ホストの中で、サーバ1つにつき1つ生成される接続管理コンポーネント。ユーザが直接触るものではない
* **世間で言うクライアント**: ホスト全体を指して言うことが多い。Claude Desktopなど

このドキュメントでは混乱を避けるため、ユーザが直接使うアプリ全体を MCPホスト（≒一般的にいうMCPクライアント） と呼びます。

### 9. Tableau MCPクライアント(候補)の一覧

以下に、エントリ執筆・投稿時点(2026年05月)での"Tableau MCPクライアント候補"の一覧を列挙します。

結論としては、大きく2点。

* **Tableau公式MCPサーバーは標準でstdio(ローカル子プロセス)型なので、以下stdio対応しているクライアントはそのまま直結出来る。**
  + Claude Desktop
  + Claude Code
  + Cursor
  + VS Code
  + Cline
  + Windsurf
  + LM Studio
  + Gemini CLI
  + Goose
  + Warp など
* **一方、以下のような各種クライアントについては、現状stdioを起動できない(リモート専用クライアント)。そのため、Tableau MCP を Streamable HTTP（TRANSPORT=http）で自前ホストして公開URL化するのが基本。どうしてもstdioで動かす制約がある場合は、`mcp-proxy`(SSE to stdioモード)や `supergateway` などで「ローカルstdioサーバをHTTPエンドポイントとして公開」するブリッジを噛ませる。**
  + Slack
  + ChatGPT
  + Claude.ai Web
  + Le Chat
  + Agentforce
  + Copilot Studio
  + Zapier
  + n8n
  + Notion
  + Perplexityなど

というのを踏まえて、下記に対応状況やその他詳細事項に関する情報を一挙表としてまとめます。

#### Tableau MCPクライアント候補 - AIチャット / デスクトップ系

| クライアント | stdio | Streamable HTTP | HTTP+SSE | 備考・参考URL |
| --- | --- | --- | --- | --- |
| Claude Desktop | ○ | ○ | ○ | ローカルは `claude_desktop_config.json` のstdio、リモートは「カスタムコネクタ」（Anthropicクラウド経由）。[support.claude.com](https://support.claude.com/) |
| Claude Code | ○ | ○ | ○ | `claude mcp add --transport stdio/http/sse`。HTTP推奨。[docs.claude.com](https://docs.claude.com/en/docs/claude-code/mcp) |
| Claude.ai（Web） | × | ○ | ○ | ブラウザ版はリモート専用（カスタムコネクタ）。ローカルstdio不可。[support.claude.com](https://support.claude.com/) |
| ChatGPT（Connectors/Apps, Developer Mode） | × | ○ | ○ | リモート専用。OpenAI公式は「SSE and streaming HTTP」対応と明記。ローカルstdio不可。[platform.openai.com](https://platform.openai.com/docs/guides/developer-mode) |
| Cursor | ○ | ○ | ○ | `.cursor/mcp.json`。stdio/HTTP/SSE対応。[docs.cursor.com](https://docs.cursor.com/context/model-context-protocol) |
| VS Code（GitHub Copilot Agent mode） | ○ | ○ | ○ | `.vscode/mcp.json`（ルートキーは `servers`）。HTTP優先・SSEフォールバック。[code.visualstudio.com](https://code.visualstudio.com/docs/copilot/reference/mcp-configuration) |
| Le Chat（Mistral） | × | ○ | ? | カスタムMCPコネクタはリモートURLのみ。Streamable HTTPが標準。[docs.mistral.ai](https://docs.mistral.ai/) |
| LibreChat | ○ | ○ | ○ | stdio/Streamable HTTP/SSE対応（OSS）。[librechat.ai](https://www.librechat.ai/docs/features/mcp) |
| 5ire | ○ | ○ | ? | ローカルstdio中心、HTTP対応。[5ire.app](https://5ire.app/) |
| Cherry Studio | ○ | ○ | ○ | STDIO/SSE/Streamable HTTP対応。[cherry-ai.com](https://cherry-ai.com/) |
| LM Studio | ○ | ○ | ○ | v0.3.17以降MCPホスト。Cursor形式の `mcp.json`、OAuth対応（v0.4.11）。[lmstudio.ai](https://lmstudio.ai/docs/app/mcp) |
| Jan | ○ | ○ | ? | ローカルstdio中心。[jan.ai](https://jan.ai/) |
| Witsy | ○ | ○ | ? | stdio・HTTP対応のデスクトップクライアント。[witsyapp.com](https://witsyapp.com/) |
| HyperChat | ○ | ? | ? | stdioベースのデスクトップクライアント。[GitHub](https://github.com/BigSweetPotatoStudio/HyperChat) |

#### Tableau MCPクライアント候補 - コラボ / コミュニケーション

| クライアント | stdio | Streamable HTTP | HTTP+SSE | 備考・参考URL |
| --- | --- | --- | --- | --- |
| Slack（Slackbot MCPクライアント / Salesforce） | × | ○ | × | リモート専用。Streamable HTTPのみ対応、SSE・DCR非対応。stdioサーバーには直接繋げない。[解説記事](https://chatforest.com/guides/salesforce-slack-mcp-ai-platform/) |
| Microsoft Teams（Tableau App / Microsoft 365） | × | ? | ? | Teams単体はMCPクライアント機能を直接公開しておらず、Copilot Studio経由が現実的。[appsource.microsoft.com](https://appsource.microsoft.com/product/office/WA200007445) |

#### Tableau MCPクライアント候補 - Salesforce エコシステム

#### Tableau MCPクライアント候補 - AIコードエディタ / IDE

| クライアント | stdio | Streamable HTTP | HTTP+SSE | 備考・参考URL |
| --- | --- | --- | --- | --- |
| Windsurf IDE（Codeium） | ○ | ○ | ○ | stdio / Streamable HTTP / SSEの3種＋各OAuth対応。[docs.windsurf.com](https://docs.windsurf.com/windsurf/cascade/mcp) |
| Cline | ○ | ○ | ○ | ローカルstdio、リモートはStreamable HTTP（推奨）/SSE（レガシー）。[docs.cline.bot](https://docs.cline.bot/mcp/mcp-transport-mechanisms) |
| Roo Code | ○ | ○ | ○ | STDIO / Streamable HTTP（推奨）/ SSE（レガシー）。[docs.roocode.com](https://docs.roocode.com/features/mcp/using-mcp-in-roo) |
| Continue | ○ | ○ | ○ | `type: stdio / streamable-http / sse`。[docs.continue.dev](https://docs.continue.dev/customize/deep-dives/mcp) |
| Sourcegraph Cody | ○ | × | × | OpenCtx経由。stdioのみ（HTTP未対応）。[openctx.org](https://openctx.org/docs/providers/modelcontextprotocol) |
| Refact.ai | ○ | ? | ? | ローカルstdio中心。[refact.ai](https://refact.ai/) |
| Replit（Agent） | × | ○ | ? | リモートURL接続（OAuth DCR）。ローカルstdioは非対応とみられる。[docs.replit.com](https://docs.replit.com/) |
| Zed | ○ | ○ | ? | 「context servers」としてMCP対応。`command` でstdio、リモートURL可。[zed.dev/docs](https://zed.dev/docs/ai/mcp) |

#### Tableau MCPクライアント候補 - CLIエージェント / ターミナル

| クライアント | stdio | Streamable HTTP | HTTP+SSE | 備考・参考URL |
| --- | --- | --- | --- | --- |
| Gemini CLI（Google） | ○ | ○ | ○ | `command`→stdio、`httpUrl`→Streamable HTTP、`url`→SSE。OAuth対応。[GitHub](https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/mcp-server.md) |
| Goose（Block） | ○ | ○ | ○ | stdio（command-line extension）、Streamable HTTP（Remote Extension）、SSE対応。[block.github.io/goose](https://block.github.io/goose/docs/getting-started/using-extensions) |
| GitHub Copilot CLI | ○ | ○ | ? | `/mcp add` でLocal/STDIOとRemote HTTPを選択。[docs.github.com](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli) |
| Amazon Q Developer CLI | ○ | ○ | ? | stdio対応に加えリモートHTTP（OAuth）対応も追加済み。[docs.aws.amazon.com](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/qdev-mcp.html) |
| Warp Terminal | ○ | ○ | ○ | `command`（stdio）とURL（Streamable HTTP/SSE）対応。[docs.warp.dev](https://docs.warp.dev/agent-platform/capabilities/mcp/) |
| OpenCode（SST） | ○ | ○ | ? | ローカル/リモート両対応のターミナルエージェント。[opencode.ai](https://opencode.ai/docs/mcp-servers/) |
| Devin（Cognition） | ○ | ○ | ○ | stdio / SSE / HTTPの3方式対応。[docs.devin.ai](https://docs.devin.ai/work-with-devin/mcp) |

#### Tableau MCPクライアント候補 - ノーコード / ワークフロー自動化

| クライアント | stdio | Streamable HTTP | HTTP+SSE | 備考・参考URL |
| --- | --- | --- | --- | --- |
| Zapier MCP（MCP Client） | × | ○ | ○ | リモート専用。Streamable HTTPとSSE対応。stdioサーバー非対応。[zapier.com/mcp](https://zapier.com/mcp) |
| n8n（MCP Client Tool） | × | ○ | ○ | SSE / Streamable HTTP対応。stdioはノード自体では非対応（Claude Desktop等とはmcp-remote経由）。[docs.n8n.io](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcpclienttool/) |
| Dify | × | ○ | ○ | リモートMCP（HTTP/SSE）中心。[docs.dify.ai](https://docs.dify.ai/en/guides/tools/mcp) |
| MindPal | × | ○ | ? | リモートMCP接続。[mindpal.io](https://mindpal.io/) |
| Lutra AI | × | ○ | ? | リモートMCP接続。[lutra.ai](https://lutra.ai/) |

#### Tableau MCPクライアント候補 - AIエージェントフレームワーク

| クライアント | stdio | Streamable HTTP | HTTP+SSE | 備考・参考URL |
| --- | --- | --- | --- | --- |
| LangChain / LangGraph（langchain-mcp-adapters） | ○ | ○ | ○ | `transport: stdio / streamable_http / sse`。[GitHub](https://github.com/langchain-ai/langchain-mcp-adapters) |
| OpenAI AgentKit / Agents SDK | ○ | ○ | ○ | stdio・Streamable HTTP・HTTP/SSE対応。[openai.github.io](https://openai.github.io/openai-agents-python/mcp/) |
| Smolagents（Hugging Face） | ○ | ○ | ? | stdio・HTTP対応。[huggingface.co](https://huggingface.co/docs/smolagents) |
| Hermes Agent（Nous Research） | ○ | ? | ? | ローカルstdio中心とみられる。[nousresearch.com](https://nousresearch.com/) |
| Microsoft Copilot Studio | × | ○ | （△） | クラウド型でリモート専用。Streamable HTTP推奨。SSEは2025年8月以降サポート終了。[learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp) |

#### Tableau MCPクライアント候補 - その他

## まとめ

という訳で、今回はTableau(Tableau MCP)をピックアップする形でしたが、任意のMCPを正しく理解し、深く実践するための「MCPの基本的な部分を理解するための情報」を整理したまとめエントリの紹介でした。ローカルMCPとリモートMCP、及びトランスポートの違いについては今回の調査・執筆作業を通じて非常に勉強になりました。現状、「方式」と「対応状況」に応じて出来ることと出来ない事の差分が発生し、場合によっては対応に手間が掛かることが判明しましたが、これらの切り分けが出来るということ自体、とても助かるように出来ているなぁとも思いました。

これらの情報を踏まえ、今後はより実践的なアプローチでTableau MCPの世界を探索していこうと思います。

---

## この記事を読んだ方へ

感想・フィードバックは X（[@shinyaa31](https://x.com/shinyaa31)）までお気軽にどうぞ。
