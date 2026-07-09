---
id: "2026-07-09-claude-desktop-on-amazon-bedrock-から-amazon-redshif-01"
title: "Claude Desktop on Amazon Bedrock から Amazon Redshift に MCP 接続してみた"
url: "https://zenn.dev/aws_japan/articles/claude-desktop-bedrock-redshift-mcp"
source: "zenn"
category: "claude-code"
tags: ["MCP", "API", "cowork", "Python", "zenn"]
date_published: "2026-07-09"
date_collected: "2026-07-10"
summary_by: "auto-rss"
query: ""
---

## はじめに

こんにちは！AWS でソリューションアーキテクトをしている町田です。

今回は、Claude Desktop (Cowork) から Amazon Redshift のデータにアクセスするために、**Amazon Redshift MCP Server** をローカル MCP サーバーとして Windows 環境でセットアップしてみました。  
Redshift へアクセスするにあたって、IAMユーザーの認証情報を使っています。IAM Identity Center のユーザーではありません。

セットアップすることで、Claude Desktop の会話内から「利用可能な Redshift クラスターを一覧して」「analytics データベースのテーブル構成を教えて」「直近の売上トップ 10 を集計して」といった自然言語での指示が可能になります。

## Amazon Redshift MCP Serverとは

[awslabs/mcp](https://github.com/awslabs/mcp/tree/main/src/redshift-mcp-server) で公開されているオープンソース MCP サーバーです。Redshift のプロビジョニング済みクラスターと Redshift Serverless ワークグループの両方に対応しており、以下の特徴があります。

* **クラスター自動検出**: クラスター / サーバーレスワークグループを自動的に検出
* **メタデータ探索**: データベース、スキーマ、テーブル、カラムをブラウズ
* **安全なクエリ実行**: **読み取り専用**モードで SQL を実行（単一ステートメントのみ、書き込みは拒否）
* **マルチクラスター対応**: 複数のクラスター / ワークグループを同時に扱える

接続は JDBC/ODBC ドライバーではなく Redshift Data API を経由するため、VPC 内への直接のネットワーク到達性は不要で、AWS 認証情報（IAM）だけで接続できるのがポイントです。

## 前提条件

* Claude Desktop がインストール済みで、Amazon Bedrock 経由のサードパーティ推論が設定済み
* 接続先の Amazon Redshift クラスター（プロビジョニング済み）または Redshift Serverless ワークグループが存在すること
* AWS CLI がインストール済みで、認証情報（プロファイル）が設定済みであること
* 利用する IAM プリンシパルに後述の IAM 権限が付与されていること
* （サンプルデータ投入を行う場合）CSV を配置する S3 バケットと、Redshift にアタッチ済みで S3 読み取り可能な IAM ロール

## セットアップの全体像

セットアップは以下の 4 ステップで完了します。

M365 ローカルコネクタと異なり Entra のアプリ登録のような管理者作業は不要で、**IAM 権限さえあればユーザー単独でセットアップ可能**です。

## ステップ 1: uv をインストールする

Redshift MCP サーバーは Python 製のパッケージ `awslabs.redshift-mcp-server` として配布されており、uv で実行します。

1. PowerShell を開き、以下を実行します。

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. ターミナルを開き直し、インストールを確認します。

3. Python 3.10 以降をインストールします（未導入の場合）。

## ステップ 2: AWS 認証情報と IAM 権限を準備する

### 2.1 AWS 認証情報の設定

MCP サーバーは AWS CLI と同じ認証情報チェーンを使用します。プロファイルが未設定の場合は以下で設定します。

```
aws configure --profile redshift-mcp
```

### 2.2 必要な IAM 権限

利用する IAM ユーザー / ロールに以下の権限が必要です（README から抜粋）。

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "redshift:DescribeClusters",
        "redshift-serverless:ListWorkgroups",
        "redshift-serverless:GetWorkgroup",
        "redshift-data:ExecuteStatement",
        "redshift-data:DescribeStatement",
        "redshift-data:GetStatementResult",
        "redshift-serverless:GetCredentials",
        "redshift:GetClusterCredentialsWithIAM",
        "redshift:GetClusterCredentials"
      ],
      "Resource": "*"
    }
  ]
}
```

### 2.3 データベース権限

IAM 権限に加えて、データベースレベルの権限も必要です。

| 権限 | 用途 |
| --- | --- |
| `SELECT` | クエリ対象のテーブル / ビューの読み取り |
| `USAGE` | 探索対象のスキーマへのアクセス |
| 接続権限 | 対象データベースへの接続 |

## ステップ 3: Claude Desktop に MCP サーバーを追加する

1. Claude Desktop を開き、**開発** → **サードパーティ推論の設定** → **コネクタと拡張機能** を選択します。
2. **「+ 追加」** からローカル（stdio）サーバーを追加し、以下の値を入力します。

![](https://static.zenn.studio/user-upload/deployed-images/397eea1f0621f1af49540d24.png?sha=85b26b406ee3d9c91bd0830349830ff30bcc8c8d)

| フィールド | 値 |
| --- | --- |
| 名前 | `awslabs.redshift-mcp-server`（任意の名前で OK） |
| トランスポート | `stdio` |
| コマンド | `uv` |
| 引数 | `["tool", "run", "--from", "awslabs.redshift-mcp-server@latest", "awslabs.redshift-mcp-server.exe"]` |
| 環境変数 | `{"AWS_PROFILE": "redshift-mcp", "AWS_DEFAULT_REGION": "us-east-1", "FASTMCP_LOG_LEVEL": "ERROR"}` |

![](https://static.zenn.studio/user-upload/deployed-images/6556b0885d7d375cf6a48a95.png?sha=adbcf0ecf94f2e26155931aefcb3d06ffc737a64)

JSON 形式で表すと以下の構成に相当します。

```
{
  "mcpServers": {
    "awslabs.redshift-mcp-server": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "awslabs.redshift-mcp-server@latest",
        "awslabs.redshift-mcp-server.exe"
      ],
      "env": {
        "AWS_PROFILE": "redshift-mcp",
        "AWS_DEFAULT_REGION": "us-east-1",
        "FASTMCP_LOG_LEVEL": "ERROR"
      }
    }
  }
}
```

3. **「変更を適用」** をクリックします。
4. **「今すぐ再起動」** をクリックします。

## ステップ 4: 動作確認

### 4.1 クラスターの一覧取得

1. 以下を Claude Desktop cowork に入力します。

```
利用可能な Redshift クラスターを一覧して
```

2. ツール実行の許可を求められるので、**「一度だけ許可」** をクリックします。
3. クラスター / ワークグループの一覧（識別子、タイプ、ステータスなど）が表示されることを確認します。

![](https://static.zenn.studio/user-upload/deployed-images/4ec370e281704e3a0c6bc406.png?sha=5cabc0cc781edafc0ebd548a5dac2cb60c95162f)

### 4.2 メタデータの探索とクエリ実行

続けて、以下のようなプロンプトで段階的にデータへアクセスできます。

```
dev データベースのスキーマとテーブルの一覧を教えて
```

Claude は `list_databases` → `list_schemas` → `list_tables` → `list_columns` と自動的にメタデータを探索し、最終的に SELECT クエリを組み立てて `execute_query` で実行してくれます。

・データを投入していない状態  
![](https://static.zenn.studio/user-upload/deployed-images/661f36ea9e5184279881a834.png?sha=336d71ad18c247d2fa6d02c38984183de7030d10)

・データを投入した後  
![](https://static.zenn.studio/user-upload/deployed-images/3e993f1ff2982a1b0640c787.png?sha=cfa98faef3e568d073d4d8489365adfa6afc7e05)

### 4.3 サンプルデータの投入

架空の EC サイト「サンプル商店」の 2025 年 1 年分の販売データを用意しました。顧客 500 件・商品 40 件・注文約 12,000 件・注文明細約 20,000 件で、テーブル構成は以下の通りです。

### 4.4 テーブル作成と COPY での投入

Redshift クエリエディタ v2 を開き、以下を実行します。（そのまま実行してもエラーになりますが参考までにどのような手順で追加したのかを残しておきます）

```
CREATE SCHEMA IF NOT EXISTS ecshop;

CREATE TABLE IF NOT EXISTS ecshop.customers (
    customer_id   VARCHAR(10)  NOT NULL,
    customer_name VARCHAR(50)  NOT NULL,
    prefecture    VARCHAR(20)  NOT NULL,
    segment       VARCHAR(10)  NOT NULL,   -- standard / premium / vip
    signup_date   DATE         NOT NULL,
    PRIMARY KEY (customer_id)
) DISTSTYLE ALL;

CREATE TABLE IF NOT EXISTS ecshop.products (
    product_id   VARCHAR(10)  NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    category     VARCHAR(30)  NOT NULL,
    unit_price   INTEGER      NOT NULL,   -- 現在の定価 (円)
    unit_cost    INTEGER      NOT NULL,   -- 仕入原価 (円)
    PRIMARY KEY (product_id)
) DISTSTYLE ALL;

CREATE TABLE IF NOT EXISTS ecshop.orders (
    order_id     VARCHAR(10) NOT NULL,
    customer_id  VARCHAR(10) NOT NULL,
    order_ts     TIMESTAMP   NOT NULL,
    order_status VARCHAR(12) NOT NULL,   -- delivered / shipped / cancelled
    total_amount INTEGER     NOT NULL,
    PRIMARY KEY (order_id)
) DISTKEY (customer_id) SORTKEY (order_ts);

CREATE TABLE IF NOT EXISTS ecshop.order_items (
    order_item_id VARCHAR(12) NOT NULL,
    order_id      VARCHAR(10) NOT NULL,
    product_id    VARCHAR(10) NOT NULL,
    quantity      INTEGER     NOT NULL,
    unit_price    INTEGER     NOT NULL,   -- 販売時点の単価 (円)
    is_returned   BOOLEAN     NOT NULL,   -- 返品フラグ
    PRIMARY KEY (order_item_id)
) DISTKEY (order_id) SORTKEY (order_id);
```

```
COPY ecshop.customers
FROM 's3://<BUCKET>/redshift-sample/customers.csv'
IAM_ROLE '<IAM_ROLE_ARN>'
FORMAT AS CSV;

COPY ecshop.products
FROM 's3://<BUCKET>/redshift-sample/products.csv'
IAM_ROLE '<IAM_ROLE_ARN>'
FORMAT AS CSV;

COPY ecshop.orders
FROM 's3://<BUCKET>/redshift-sample/orders.csv'
IAM_ROLE '<IAM_ROLE_ARN>'
FORMAT AS CSV
TIMEFORMAT 'YYYY-MM-DD HH:MI:SS';

COPY ecshop.order_items
FROM 's3://<BUCKET>/redshift-sample/order_items.csv'
IAM_ROLE '<IAM_ROLE_ARN>'
FORMAT AS CSV;
```

投入結果を確認します。

```
SELECT 'customers' AS tbl, COUNT(*) FROM ecshop.customers
UNION ALL SELECT 'products', COUNT(*) FROM ecshop.products
UNION ALL SELECT 'orders', COUNT(*) FROM ecshop.orders
UNION ALL SELECT 'order_items', COUNT(*) FROM ecshop.order_items;
```

| tbl | count |
| --- | --- |
| customers | 500 |
| products | 40 |
| orders | 11,951 |
| order\_items | 20,125 |

私の検証環境では IAM ユーザーに対して、ecshop スキーマへのアクセス権限を付与します。

```
GRANT USAGE ON SCHEMA ecshop TO "IAM:redshift-user-mcp";
GRANT SELECT ON ALL TABLES IN SCHEMA ecshop TO "IAM:redshift-user-mcp";
```

## ステップ 5: AI エージェントならではの活用デモ

ここからが本題です。BI ダッシュボードとの違いは、**「何を見るべきか」を人間が事前に定義しなくても、エージェントが仮説を立てながら探索的にクエリを重ねてくれる**ことです。SQL を 1 行も書かずに、データ分析者に依頼するのと同じ粒度の依頼ができます。

### 5.1 オープンエンドな異常検知

あえて具体的な指標を指定せず、次のプロンプトだけを投げてみます。

```
ecshop スキーマは EC サイトの 2025 年の販売データです。
経営会議に報告すべき「気になる変化」がないか、データを探索して調べてください。
売上・商品・顧客・返品などの観点で自由に分析し、
発見した事象ごとに根拠となる数字を添えて報告してください。
```

・実際のアウトプット  
![](https://static.zenn.studio/user-upload/deployed-images/1ab64321b71f0877bec05356.png?sha=0a92578244231c2b6f8166d096b4966bcbdad83e)

![](https://static.zenn.studio/user-upload/deployed-images/c21103b232ad7df6a985d8fb.png?sha=719617e54db1e9ef094a24dea7eaec4d27833616)

Claude はテーブル構成を自動探索した後、月次売上、カテゴリ別トレンド、返品率、地域別動向…と自律的にクエリを重ねていきます。  
事前に指標を教えていなくても、返品率の急増や特定地域の顧客離脱といった「定型レポートからはこぼれ落ちる変化」をエージェントが自力で拾えるかが見どころです。

### 5.2 根本原因の深掘り（ドリルダウン）

デモ 1 で見つかった事象について、そのまま会話で深掘りできます。

```
ワイヤレスイヤホンの返品率急増について深掘りしてください。
1. 返品率の推移を月次で出す
2. 特定の顧客層・地域に偏っていないか確認する
3. 同じ家電カテゴリの他商品と比較する
4. 品質問題・物流問題・顧客層の変化のどれが濃厚か、仮説と根拠を示す
```

・実際のアウトプット

![](https://static.zenn.studio/user-upload/deployed-images/4de732754036c418d7771f12.png?sha=b388b2b8252c8060f536be0f0344e20b1f92eb40)

人間のアナリストが行う「仮説 → 検証クエリ → 次の仮説」のループを、エージェントが数分で回してくれます。他商品の返品率が平常値のまま P-0015 だけ 9 月を境に跳ね上がっていることから、「9 月出荷ロット以降の品質問題」という仮説に到達できました。

### 5.3 分析結果をそのままアウトプットに変換

Claude Desktop はローカルファイルの作成もできるため、分析とレポーティングを 1 つの会話で完結できます。

```
ここまでの分析結果を、経営会議向けの 1 枚サマリーとしてまとめてください。
- 重要な発見 3 つ（それぞれ根拠の数字つき）
- 推奨アクション（担当部門つき）
- 裏付けに使った SQL は付録に
Word ファイルとして保存してください。
```

・実際のアウトプット

![](https://static.zenn.studio/user-upload/deployed-images/172859d49c3bec41f6877ef9.png?sha=c3282ace5e613d0a1b88ea61d841e7bd086be487)

「Redshift への問い合わせ → 分析 → 資料化」までを担ってくれるのは、単なる Text-to-SQL ツールにはないエージェントならではの体験です。M365 コネクタも接続していれば、「この内容を Teams の営業チャネルの議論と突き合わせて」といったデータソース横断の依頼にも発展できます。

## 利用可能なツール

Redshift MCP サーバーを接続すると、以下のツールが Claude Desktop から利用可能になります。

| ツール | 機能 |
| --- | --- |
| list\_clusters | クラスター / サーバーレスワークグループの検出 |
| list\_databases | 指定クラスター内のデータベース一覧 |
| list\_schemas | 指定データベース内のスキーマ一覧 |
| list\_tables | 指定スキーマ内のテーブル / ビュー一覧 |
| list\_columns | 指定テーブルのカラム定義（型、NULL 許可、デフォルト値など） |
| execute\_query | SQL クエリの実行（読み取り専用・単一ステートメント、書き込みは拒否） |

## ネットワーク要件

ローカル MCP サーバーはユーザーのデバイス上のホストプロセスとして動作し、デバイスから直接 AWS API を呼び出します。以下のエンドポイントへの HTTPS アウトバウンドアクセスが必要です（リージョンは利用環境に読み替えてください）。

| ホスト | 目的 |
| --- | --- |
| redshift.＜リージョン＞.amazonaws.com | クラスターの検出・一時認証情報の取得 |
| redshift-serverless.＜リージョン＞.amazonaws.com | サーバーレスワークグループの検出・認証 |
| redshift-data.＜リージョン＞.amazonaws.com | Redshift Data API（クエリ実行） |

## 認証・認可に関する FAQ

認証・認可まわりの疑問をまとめます。

### Q1. Identity Center (SSO) を使っている場合、`aws sso login` を定期的に実行する必要がある？

あると考えられます。  
Redshift MCP サーバーは環境変数 `AWS_PROFILE` で指定されたプロファイルの標準的な認証情報をそのまま使うローカルプロセスです。プロファイルが Identity Center ベースの場合、セッションが切れるたびに `aws sso login --profile <プロファイル名>` の再実行が必要だと考えられます。

### Q2. Claude Desktop の GUI 上のログインをすれば Redshift にアクセスできる？

できません。  
Claude Desktop へのサインインと AWS の認証は完全に別物です。この構成には独立した 3 つの認証が存在します。

| 認証 | 設定場所 | 用途 |
| --- | --- | --- |
| Claude アカウント | GUI のサインイン | Claude Desktop 自体の利用 |
| Bedrock 推論用 AWS 認証 | 「接続」画面のプロファイル設定 | Claude モデルの呼び出し |
| MCP サーバー用 AWS 認証 | MCP サーバーの環境変数 `AWS_PROFILE` | Redshift への API アクセス |

### Q3. Identity Center + Entra ID 連携時、「誰にどのテーブルを見せるか」はどう制御する？

認可は「Permission Set（= IAM ロール）単位」であって「ユーザー単位」ではない、というのが設計上のポイントです。

MCP サーバーは IAM 認証で DB の一時認証情報を取得し、Redshift には `IAMR:<ロール名>` という DB ユーザーとして接続します。Entra ID の 100 人が同じ Permission Set を使っていれば、Redshift から見ると全員が同一 DB ユーザーです。したがって:

* テーブル単位の出し分けは、Permission Set を部門・職務ごとに分割し、それぞれの `IAMR:<ロール名>` に GRANT を設計することで実現します（Entra ID グループ → Identity Center グループ → Permission Set という既存 ID 基盤の構造をそのまま認可境界にできます）

```
-- 例: 分析チーム用ロールには ecshop スキーマの読み取りのみ許可
GRANT USAGE ON SCHEMA ecshop TO "IAMR:AnalystRole";
GRANT SELECT ON ALL TABLES IN SCHEMA ecshop TO "IAMR:AnalystRole";
```

* 逆に、1 つの Permission Set を全員に配る構成では「人によって見せるテーブルを変える」ことは**できません**

### Q4. Bedrock を提供する AWS アカウントと Redshift のアカウントが別でも大丈夫？

問題ありません（特別な設定も不要です）。  
Q2 の表の通り、Bedrock 推論用の認証と MCP サーバー用の認証は独立しているため、それぞれ別アカウントの認証情報を向けるだけです。2 つの認証フローが交差する場面はありません。実際に本記事を執筆するにあたって、Bedrock 認証用アカウントと Redshift のアカウントは別々のアカウントです。

Identity Center を使っているなら、Redshift 側アカウントに Permission Set を割り当てて、そのアカウント用のプロファイルを作るのが良いかもしれません。

```
# ~/.aws/config の例 (Identity Center 利用時)
[profile redshift-mcp]
sso_session = my-sso
sso_account_id = <RedshiftのあるアカウントID>
sso_role_name = RedshiftAnalystAccess
region = ap-northeast-1
```

## まとめ

Claude Desktop (Cowork) on Amazon Bedrock に awslabs の Amazon Redshift MCP Server をローカル MCP サーバーとして設定することで、会話の中から Redshift のデータにアクセスできるようになりました。

* Redshift Data API 経由なので VPC への直接接続が不要、IAM 認証情報だけで接続可能
* 読み取り専用設計で、分析用途に安心して使える

デモで確認した通り、単に SQL を代行するだけでなく、**指標を事前に定義しなくてもエージェント自身が仮説を立てて探索・深掘りし、レポートまで仕上げてくれる**のが AI エージェント × データウェアハウスの面白さです。M365 ローカルコネクタと組み合わせれば、「Redshift の分析結果を Teams の議論と突き合わせてブリーフィングを作成」といった複数データソース横断のワークフローにも発展できます。

## 参考リンク
