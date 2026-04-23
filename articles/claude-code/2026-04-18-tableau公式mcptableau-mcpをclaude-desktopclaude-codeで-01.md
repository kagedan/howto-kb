---
id: "2026-04-18-tableau公式mcptableau-mcpをclaude-desktopclaude-codeで-01"
title: "Tableau公式MCP(Tableau MCP)をClaude Desktop／Claude Codeで試す：セットアップから実演デモまで"
url: "https://zenn.dev/truestar/articles/eaaf19733af78c"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-18"
date_collected: "2026-04-19"
summary_by: "auto-rss"
query: ""
---

![](https://static.zenn.studio/user-upload/1fdfdae50784-20260418.png)

先日投稿した下記のnote、Tableauワークブック(TWB)形式の定義が公式にアナウンス、展開されたことで今後展開が期待出来そうなことを幾つかのトピックにまとめたものでした。エントリの中では『Tableau × MCPエコシステム連携』という項目を設け、

更には下記ZennエントリではTableau界隈におけるMCPサーバの世界にはどのようなものがあるか、その概要をまとめました。

その中でまず検証すべきものとして、公式が展開している『**Tableau MCP**』が筆頭に挙げられるでしょう。

当エントリでは、このTableau MCPに関してClaude Desktop及びClaude Codeからの接続を試み、実際にどういうデータが得られるか、どういうことが出来るのかについて実際に試してみた結果を紹介します。(※Claude上でのやり取りキャプチャが多いのでスクロールバー長めです。ご容赦ください...🙇)

## Tableau MCPとは

Tableau MCPは、エージェントとTableau間の通信を簡素化するためにMCP(Model Context Protocol)を使用するオープンソースのGitHubプロジェクトであり、ユーザーがVizQLデータサービス、メタデータAPI、およびその他のTableau APIを活用することで、TableauデータをAIツールに取り込むことを可能にするプロダクトです。**超ざっくり要約すると『Tableau MCPは、Tableau CloudやTableau Serverで作成したワークブック含め各種要素の内容や情報を取得することができる』(取得したデータをあれこれするのは取得してからのツールやサービスの話)**、という見方になるでしょうか。

Tableau MCPの基本アーキテクチャは以下の通り。Tableau MCPはローカルコンピュータ上で別のプロセスとして実行され、Claude Desktopは標準の入出力ストリームを使用してTableau MCPと直接通信します。

![](https://static.zenn.studio/user-upload/4a66f2e50777-20260418.png)  
*公式ドキュメント「Getting Started」より、Tableau MCPのアーキテクチャ構成図*

Tableau MCPは、Tableau ServerまたはTableau Cloudのサイト上で公開されているデータソースと連携して動作します。そして、データに接続するためにはMCPで使用するためのパーソナルアクセストークン(PAT)を作成する必要があります。

!

以降の手順はTableau Cloud,或いはTableau Serverの環境があるという前提で進めます。  
(そして当エントリではTableau Cloud環境が用意済という状況から始めます)

Tableau Cloudでは『Tableau開発者プログラム』というのを提供しており、これを使う事で  
テスト用のTableau Cloud環境(無料)を使う事が出来ます。もし必要であればこちらのサービス利用での検証をご検討ください。

## Tableau Cloud環境設定

まず初めに、上述の通り「MCPアクセスに必要なパーソナルアクセストークン(PAT)」の準備から。

サイトにログイン後、右上のプロフィールから[マイアカウント設定]を開きます。

![](https://static.zenn.studio/user-upload/ae320ec8a49e-20260418.png)

個人設定画面内に『個人用アクセストークン』を作成してください。権限が足りない場合、また許可されていない場合は以下のような表示となっていると思います。その場合は管理者に依頼して許可してもらう、管理者権限ユーザーで検証する等の対応を行ってください。

![](https://static.zenn.studio/user-upload/4ed0cdb10b58-20260418.png)

Tableau MCP利用に際しては、利用出来るユーザーの範囲や期間等を定める事が出来ます。詳細は後述しますが、一旦ここでは「任意のグループに属するユーザーのみ許可する」形を取ることにしました。任意のグループを作成し、ユーザーを追加(ここではひとまず私だけ)。ユーザー権限には既存Creatorライセンスを付与された状態でしたが、今回用に「サイト管理者」を追加で付与してもらいました。

![](https://static.zenn.studio/user-upload/ea538ca13b5d-20260418.png)

権限がある状態だと、以下のようにトークン作成のメニューが表示されるようになります。任意の名前を入力し[トークンを作成する]を押下。

![](https://static.zenn.studio/user-upload/e71a9899b6b0-20260418.png)

作成の際の詳細情報を選択・入力。先程上記手順で作成したグループをPAT利用可能なユーザー対象として指定、その他は初期値のまま画面右上の[保存]を押下。

![](https://static.zenn.studio/user-upload/d628fce960e8-20260418.png)

PAT作成。出来上がった内容・ファイルは大切に保管しておいてください。後述手順でも用います。

![](https://static.zenn.studio/user-upload/dda9c2fbfdb9-20260418.png)

PAT作成後は以下のように一覧表示されます。

![](https://static.zenn.studio/user-upload/b7bb61c8cc1b-20260418.png)

## Tableau MCP利用の際の前提条件

Tableau MCPは、以下の条件を満たす事でTableau CloudまたはTableau Serverの両方のデータソースに対応します。

* 公開されているデータソースのみがサポート対象
* Tableau Serverユーザーは
  + VDS(VizQLデータサービス)を有効にする必要がある
  + メタデータAPIを有効にする必要がある
* ユーザーはデータソースにおいてAPIアクセスを有効にする必要がある
* Tableau CloudユーザーはPulse APIを利用する場合、サイトでTableau Pulseを有効にする必要がある

公開済みのデータソースがない場合は、Superstoreのようなサービスを利用して作成するか、  
CSV/Excelファイルをアップロードして公開版を作成することができます。

## Tableau MCP実践：Claude Desktopからの接続

ここからはClaude Desktop経由でTableau MCPに接続する手順を進めていきます。公式サイトからDesktopインストーラを入手、導入まで済ませておいてください。

Claude Desktop起動後、画面左下[設定]→[拡張機能]→[拡張機能を参照]を選択。

![](https://static.zenn.studio/user-upload/0bf617cc5082-20260418.png)

一覧から該当するものを"Tableau"で絞り込み、該当したものを選択。

![](https://static.zenn.studio/user-upload/9c6b97814ff4-20260418.png)

[インストール]を選択。

![](https://static.zenn.studio/user-upload/39f8a4395dc5-20260418.png)

Tableau MCP Serverの認証に必要な情報の入力を求められます。先程控えておいた諸々の値を設定し[保存]押下。

![](https://static.zenn.studio/user-upload/84ddb778d4f8-20260418.png)

保存された結果は以下のようになっています。その1(概要)：

![](https://static.zenn.studio/user-upload/7f76b967fe65-20260418.png)

その2(MCP連携設定値)：

![](https://static.zenn.studio/user-upload/ecd5b7f7034a-20260418.png)

その3(ツールの一覧、及び権限対応) ※現時点では都度「承認が必要」なオペレーション設定になっています。この辺りは色々試してもらい、承認不要なものはここで設定を切り替えてください。

![](https://static.zenn.studio/user-upload/13342304c1ab-20260418.png)

## Tableau MCP実践：Claude Desktop上でデモ実演、できることを確認

さぁ！これで準備は整いました。実際にTableau MCPとやり取りしてみましょう。新規チャットで問い掛けてみます。

### 接続確認

Tableau MCPの設定があること、繋がっていることは認識出来ている模様。

![](https://static.zenn.studio/user-upload/16b23af5d192-20260418.png)

> Tableau MCPでできることの一覧を教えて欲しい。そして、「できること」を確認できるようなデータの見せ方を、デモ的に見せて欲しい。

というリクエストを投げたら以下のようなウィジェットを作ってきました。この内容を順に見ていきます。

![](https://static.zenn.studio/user-upload/98661de19b41-20260418.png)

### Tableau MCP実演デモ1：ワークブック・ビューの一覧

最初のデモは「ワークブック・ビューの一覧」。シンプルに守備範囲となるワークブック・ビューの一覧を表示してとお願いし、以下のような形で一覧を取得、表示までやってくれました。一覧と合わせて概要の説明までやってくれています。

![](https://static.zenn.studio/user-upload/de9434441f96-20260418.png)

ワークブックをクリックすると、配下のビュー一覧を表示。画像表示が可能なもの？については丁寧に[画像表示]のアイコンが表示されています。

![](https://static.zenn.studio/user-upload/82ce4ab488df-20260418.png)

クリックすると画像表示までやってくれ...あれ、途中経過では作成しているように見えるんですが、依頼結果の「応答」タイミングでは画像が表示されていません。

![](https://static.zenn.studio/user-upload/83f8fa87952a-20260418.png)

何度か試してみましたがどうも具合が悪いようです。

![](https://static.zenn.studio/user-upload/71ee32052a17-20260418.png)

結果的に、若干の不具合気味な回答が返ってきました。(推測ですが、Claude Desktop拡張側での画像コンテンツの扱いに起因する挙動に見えます。2026年04月時点) ワークアラウンドも提示されていますし、「現状こういう感じなんだな」ということで次に進みます。

![](https://static.zenn.studio/user-upload/55caacb98cbd-20260418.png)

### Tableau MCP実演デモ2：ビューを画像で取得

こちらのデモ、要素としてはClaude Desktopが提示してくれてましたが、流れで上記ケースにて消化していましたので割愛します。

![](https://static.zenn.studio/user-upload/2bd7239f6730-20260418.png)

### Tableau MCP実演デモ3：集計クエリ

「実データを集計、クエリして欲しい」というリクエストに対する結果です。クエリ実行が為され、結果を複数可視化表示してくれました。表示しているのはSuperstoreデータにおけるTOP10顧客。

![](https://static.zenn.studio/user-upload/f70805fe21c2-20260418.png)

ボタン押下でそれぞれタブ切り替えの形で別途グラフが表示されています。(サブカテゴリ分析)

![](https://static.zenn.studio/user-upload/8f940127ed86-20260418.png)

地域xセグメント分析：

![](https://static.zenn.studio/user-upload/276b55dcfa4c-20260418.png)

売上ビン分析：

![](https://static.zenn.studio/user-upload/37b225d4f45d-20260418.png)

上記は雑な感じの依頼でしたが、見たいものや切り口が明確になっていればその指示を投げることでリクエストに沿った情報を見せてくれたりもします。

> 地域とサブカテゴリにおける売上のヒートマップが見たい。年で表示データを切り替えられるようなインタラクティブなダッシュボードにしてくれると嬉しいです

![](https://static.zenn.studio/user-upload/99e46359a832-20260418.png)

### Tableau MCP実演デモ4：Pulseメトリクスの表示

Tableau MCPではPulseに関する情報も取得できます。

個人的にはTableau Pulse、あんまり馴染みが無かったので「そもそも何これ？」ってな感じでしたが、Tableau PulseもClaude Codeも共にAI、使い方次第で何か面白そうな事もできそうですね。

![](https://static.zenn.studio/user-upload/8f9063febc8b-20260418.png)

> 使い方次第で何か面白そうな事もできそうですね。

「なお、」で始まる部分、まさにこの範囲なのかも。

![](https://static.zenn.studio/user-upload/e776c7b64189-20260418.png)

### Tableau MCP実演デモ5：コンテンツ検索

Claude Desktopが提示してきたデモは上記4つでしたが、更に聞いてみるとまだやってないツールがあるようでした。

![](https://static.zenn.studio/user-upload/5e9815f02ba2-20260418.png)

ということでやってもらいました。1つめはコンテンツ検索(search-content)。Tableauサイト内のサポートされているすべてのコンテンツタイプを対象に、検索クエリに関連するオブジェクトを検索します。

![](https://static.zenn.studio/user-upload/4920614a265f-20260418.png)

[タイプ絞込(datasourceのみ)]を選択すると別のデータを表示してきました。

![](https://static.zenn.studio/user-upload/20609f2ce2fa-20260418.png)

ポイント：

![](https://static.zenn.studio/user-upload/460300eaf9fa-20260418.png)

### Tableau MCP実演デモ6：ID指定でメトリクスを直接取得

未実施デモ2つめはID指定でメトリクスを直接取得するというもの。

![](https://static.zenn.studio/user-upload/e405fa2ab4a6-20260418.png)

![](https://static.zenn.studio/user-upload/08fa67c8a398-20260418.png)

## 「Tableau MCPでできること」と確認した内容のまとめ

上記「デモ実演」で可能な限り見れるものを見てきました。公式ドキュメントの『Tools』一覧との対比は以下の通り。幾つか準備や状況が整わず確認できなかったものがありましたが、大枠どういう挙動をするものが利用できるのかはカバーできたかと思います。

| ツール | 説明 | 当エントリでのデモ状況 | API Doc |
| --- | --- | --- | --- |
| `list-workbooks` | ワークブック一覧取得 | ✅ デモ済 | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/workbooks/list-workbooks) |
| `list-views` | ビュー一覧取得 | ✅ デモ済 | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/views/list-views) |
| `get-workbook` | ワークブック詳細取得 | ✅ デモ済 | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/workbooks/get-workbook) |
| `get-view-image` | ビューを画像取得 | ✅ デモ済 (※Claude.ai 画面では非表示 の制約あり) | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/views/get-view-image) |
| `get-view-data` | ビューデータをCSV取得 | ✅ デモ済 | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/views/get-view-data) |
| `list-datasources` | データソース一覧取得 | ✅ デモ済 | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/data-qna/list-datasources) |
| `get-datasource-metadata` | データソースのフィールド・メタ情報取得 | ✅ デモ済 | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/data-qna/get-datasource-metadata) |
| `query-datasource` | VizQLカスタムクエリ実行 | ✅ デモ済 | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/data-qna/query-datasource) |
| `search-content` | サイト横断コンテンツ検索 | ✅ デモ済 | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/content-exploration/search-content) |
| `list-all-pulse-metric-definitions` | Pulseメトリック定義一覧 | ✅ デモ済 | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/pulse/list-all-pulse-metric-definitions) |
| `list-pulse-metrics-from-metric-definition-id` | 定義IDからメトリクス取得 | ✅ デモ済 | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/pulse/list-pulse-metrics-from-metric-definition-id) |
| `list-pulse-metrics-from-metric-ids` | メトリクスID指定で取得 | ✅ デモ済 | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/pulse/list-pulse-metrics-from-metric-ids) |
| `generate-pulse-metric-value-insight-bundle` | Pulseインサイトバンドル生成 | ✅ デモ済 | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/pulse/generate-pulse-metric-value-insight-bundle) |
| `list-pulse-metric-subscriptions` | Pulseサブスクリプション一覧 | 🔲動作確認済 (サイトに0件) | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/pulse/list-pulse-metric-subscriptions) |
| `generate-pulse-insight-brief` | AI会話型インサイトブリーフ | ❌ 403エラー (プラン・権限依存) | [Doc](https://tableau.github.io/tableau-mcp/docs/tools/pulse/generate-pulse-insight-brief) |

※以下、ドキュメントには存在するが今回のデモでは紹介されていなかったものを列挙しておきます。(どこかで検証したい)

## Tableau MCP実践：Claude Codeからの接続

さて、ここまでだいぶスクロールバーをスクロールして頂きました。ここからはClaude Codeによる接続を試してみたいと思います。Claude Desktopでの接続情報を流用する形で設定を行います。

私自身ここまでの経緯を辿ると、対象となる設定ファイルのmcpServers項目配下に値を追加、追記する形で設定を進めていたのですが(そしてその場合、mcpServers配下にある内容をコピペするくらいの感覚で他環境への設定移行が済んでいたのですが)、今回Claude Desktopでは『拡張機能』による導入を行いました。なのでmcpServersには設定されておらず。なので今回はClaude Desktop設定の際に控えていた値を転記する形で設定を行います。

とは言っても、設定自体はコマンド一発で完了するのですが...(下記内容に倣って`claude mcp add`コマンドを実行してください)

```
% claude mcp add --scope user tableau-mcp \
  -e SERVER=サーバ名 \
  -e SITE_NAME=サイト名 \
  -e PAT_NAME=PATキーの名前 \
  -e PAT_VALUE=PATファイルに含まれる値 \
  -e TRANSPORT=stdio \
  -- node "(Tableau MCP サーバー本体のファイルパス。Node.js)"
```

最後の `-- node` に対応する引数については、導入する環境はOSに依って内容が異なってくるかと思います。私の環境(Mac/Apple M4)では以下コマンドで見つかる実行パスを設定しました。

```
## #1.まずはTableau MCPの実行フォルダがあるかどうかを確認、
##    ant.dir.gh.tableau.tableau-mcp/ の存在を把握.
% find ~/Library/Application\ Support/Claude -name "*tableau*" 2>/dev/null
/Users/xxxxxxxxxxxxxxx/Library/Application Support/Claude/Claude Extensions Settings/ant.dir.gh.tableau.tableau-mcp.json
/Users/xxxxxxxxxxxxxxx/Library/Application Support/Claude/Claude Extensions/ant.dir.gh.tableau.tableau-mcp
/Users/xxxxxxxxxxxxxxx/Library/Application Support/Claude/Claude Extensions/ant.dir.gh.tableau.tableau-mcp/.cursor/rules/tableau-mcp.mdc

## #2. ant.dir.gh.tableau.tableau-mcpの配下を確認。buildフォルダを把握.
% ls ~/Library/Application\ Support/Claude/Claude\ Extensions/ant.dir.gh.tableau.tableau-mcp/
app.json                CODEOWNERS              LICENSE.txt             package.json            README.md               SECURITY.md
build                   CONTRIBUTING.md         manifest.json           playwright.config.ts    scripts
CODE_OF_CONDUCT.md      icon.png                node_modules            Procfile                sea-config.json

## #3. build/フォルダの中身を確認。index.jsの存在を把握.
% ls ~/Library/Application\ Support/Claude/Claude\ Extensions/ant.dir.gh.tableau.tableau-mcp/build/
index.js        telemetry

↓
## 上記経緯を踏まえ、『実行フォルダ』＋ build/ + index.js を繋げた文字列を実行パスとして設定.
/Users/xxxxxxxxxxxxxxx/Library/Application Support/Claude/Claude Extensions/ant.dir.gh.tableau.tableau-mcp/build/index.js
```

`claude mcp list`コマンドを実行し、接続が確認できていればOKです。

```
% claude mcp list
:
tableau-mcp: node /Users/xxxxxxxxxxxxxxx/Library/Application Support/Claude/Claude Extensions/ant.dir.gh.tableau.tableau-mcp/build/index.js - ✓
Connected
```

### 接続確認

Claude Desktop同様、念のための接続確認をエージェント経由で実施。問題無さそうです。

![](https://static.zenn.studio/user-upload/f20247cc96c6-20260418.png)

### できることの確認(整理)

基本的に『Claude DesktopでできることはClaude Codeでもできる』とは思うのですが、一応聞いてみました。

> ・Claude Desktopでも、Claude Codeでもできること  
> ・Claude Desktopではできるが、Claude Codeではできないこと  
> ・Claude Desktopではできないが、Claude Codeでしかできないこと  
> それぞれ分けて整理し直してもらえますか？結果は表形式にして欲しいです。

結果は以下。

![](https://static.zenn.studio/user-upload/ffb4aaf295b0-20260418.png)

人に優しくテーブル表記でも再掲。エントリのボリュームがだいぶ長くなってきたので(Claude Codeでの)実践自体は当エントリでは見送りますが、Claude Codeでの利用はより広範な処理や連携が期待できそうなものが多いですね。

| 機能 | Claude Desktop | Claude Code | Claude Codeでしかできないこと、 どんな展開が期待できる？ |
| --- | --- | --- | --- |
| 全Tableau MCP ツール呼び出し | ✅️ | ✅️ | --- |
| データのテキスト解釈 ・インサイト生成 | ✅️ | ✅️ | --- |
| ワークブック・ビュー・ データソース探索 | ✅️ | ✅️ | --- |
| 画像のチャットUI インライン表示 | ✅️ | ❌️ | --- |
| 取得データ・画像の ローカルファイル保存 | ❌️ | ✅️ | Tableauから取得したデータ(CSV等)や ビュー画像をローカルに書き出せる。 後続の分析や他ツールへの受け渡しに使える。 |
| コード生成＋即実行 (Python等) | ❌️ | ✅️ | 取得したTableauデータを元にPython スクリプトを生成し、そのままターミナルで 実行できる。集計・可視化・加工まで 一気通貫で行える。 |
| Git操作 | ❌️ | ✅️ | 作成した分析スクリプトやクエリをGitで バージョン管理できる。 変更履歴の追跡やチームへの共有が可能。 |
| Hooks/Cronによる 自動化 | ❌️ | ✅️ | ・Hooks: ツール実行前後にスクリプトを自動実行(例: ログ記録・コマンド検証) ・外部Cron: スクリプト化したClaudeタスクを定期実行 (例: 毎朝9時にTableauのメトリクスを取得してSlackに通知) |
| サブエージェントでの 並列処理 | ❌️ | ✅️ | 複数のビューやダッシュボードを同時に 別エージェントに分析させることで、 処理時間を大幅に短縮できる。 |
| 他システム・開発 パイプラインへの統合 | ❌️ | ✅️ | TableauデータをAPI、DB、ETLパイプライン、 CI/CDなど他システムと組み合わせた処理フローに 組み込める。 |

## まとめ

という訳で、Tableau公式が提供しているMCP『Tableau MCP』の紹介と実践内容をお届けしました。Tableau CloudなりServerの時点で大枠データは集められている、整っているとは思いますがこうやってClaudeを介してデータを探索する、またはTableau MCPと同じ粒度で他のMCPサーバーと連携し、それらを合わせて見る、分析するというサービス間連携も比較的ハードル低く体験できるのでは...と今回の実践を経て思いました。

[冒頭紹介したZennエントリ](https://zenn.dev/truestar/articles/37f418a0bcace9)にあるように、Tableau関連のMCPは他にも存在します。引き続き他のMCP連携についても実践していきたいと思います！
