---
id: "2026-03-20-元オンプレ屋が疑似aws環境のログをgemiclawに確認してもらうまで備忘録-01"
title: "元オンプレ屋が疑似AWS環境のログをGemiclawに確認してもらうまで(備忘録)"
url: "https://zenn.dev/aa_taka/articles/c5e67c212e4a40"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-03-20"
date_collected: "2026-03-22"
summary_by: "auto-rss"
---

## 1. はじめに：プロジェクトの背景

OpenClawなどAIエージェントを一度は触ってみたいなと考えていた時に、コンテナで動くAIエージェント(Gemiclaw)についてのNishinaさんの記事を読み、Gemiclawでシステムの管理とかできたら面白そうだと考えました。よく分からないけど、権限周りをクリアしてシステムのログをDiscordとかで見れたら、外出時でも確認できてよさそう。

<https://zenn.dev/nishina__n/articles/69587684b36113>

<https://github.com/Nishina-N/gemiclaw>

Gemiclawの検証のために、LocalStack上でシステムを作る必要ができました。ネット上にある構築手順付きのAWSハンズオンなどをGeminiに読み込ませたら簡単に構築できそうだけど、技術記事にするのだから自分でGeminiと話して何か作りたい。とりあえず、SAAの試験勉強でおなじみの「S3に写真をアップロードすると、通知を受けてLambdaが動く」という構成をベースにすることにしました。せっかくなので、ログインするアカウントによってWeb画面が切り替わる仕組みも取り入れます。一般社員は「ファイルのアップロード」ができ、管理者は「誰が何を上げたかの一覧確認」と「対応ステータス（未対応・対応済み）の更新」ができる。そんな、実用的な運用管理システムを目指して作ってみます。

## 2. 技術スタック

大まかな方針が決まったので、次にGeminiのGemでレビュアー役を作りました(Gemは作成時の初期設定が維持されるため、「あなたはプロの宇宙飛行士です」といった設定を忘れにくいです)。  
作成したGemとの打ち合わせを通してterraformやLambdaの設定ファイルとリポジトリ構成を固めます。LocalStackだけでの利用を想定しているため、variables.tfなどを作成せずにシンプルにmain.tfに全部詰め込む設定にしました。

・なぜ main.tf 1枚なのか  
通常の本番環境では保守性のためにファイルを分割しますが、今回は「検証環境の迅速な立ち上げと破棄」に特化するため、あえて1ファイルに集約しています。これにより、AIエージェントがインフラの全容を一度のコンテキスト読み込みで把握できるというメリットも生まれています。

---

### 2.1. リポジトリ構成と論理構成図

私の管理のしやすさとGemiclawが確認しやすいために、AIエージェントとシステムを同じディレクトリに入れて構築しました。

```
projects/gemiclaw/
├── main.tf             # Terraform (LocalStack用)
├── src/                # ソースコードルート
│   └── lambda/         # Go言語によるLambda関数群
│       ├── admin_list/   # 管理者用：提出写真一覧取得
│       ├── admin_update/ # 管理者用：写真ステータス更新
│       ├── auth/         # 認証・ログイン処理
│       └── photo/        # 写真投稿・メタデータ管理
├── gemiclaw/           # AIエージェント本体
│   └── config/skills/  # AIに付与するスキル（今回のデバッグの舞台）
└── terraform.tfstate   # 状態管理ファイル
```

### 2.2. 論理構成図

今回のシステムは、\*\*「フロントエンド（HTML/JS）」「AWSモック（LocalStack）」「AIエージェント（Gemiclaw）」\*\*の3者が複雑に連携します。

```
AWS Environment (LocalStack / ap-northeast-1)
│
├── [ 入口 1 ] API Gateway (AuthAPI)
│   ├── /login (POST) ──────────> auth-handler (認証・トークン発行)
│   │   │
│   │   ├── /admin (管理者用)
│   │   │   ├── /list (GET) ────> admin-list-handler
│   │   │   └── /update (POST) ──> admin-update-handler
│   │   │
│   │   └── /stuff (一般社員用)
│   │       └── (S3へのUpload) ─┐
│                             　│
├── [ 入口 2 ] Storage Layer    │
│   └── S3: my-photo-storage <──┘ (ファイルが置かれる)
│       └── s3:ObjectCreated:* ───> photo-handler (自動起動・DB登録)    　  　
│
├── Compute Layer (Lambda Functions)
│   ├── auth-handler         # ユーザー認証 / AuthUserテーブル参照
│   ├── admin-list-handler   # メタデータ一覧取得 / PhotoMetadata参照
│   ├── admin-update-handler # メタデータ更新 / PhotoMetadata参照
│   └── photo-handler        # 【非同期】S3保存をトリガーにメタデータをDB登録
│
├── Storage & Database Layer
│   ├── S3: my-photo-storage     # 写真データ本体の保存 (CORS設定済)
│   ├── DynamoDB: AuthUser       # 認証用 (UserID / Password / Role)
│   └── DynamoDB: PhotoMetadata  # 写真管理用 (PhotoID / UserID [GSI])
│
└── AI Agent & Development (Local)
    ├── Gemiclaw (Docker)        # エージェント本体。API経由でシステムを操作
    └── Terraform (main.tf)      # インフラ全体のコード化 (IaC)
```

技術的な肝となるのが、\*\*「どこから、どうやってLocalStackに接続するか」\*\*というエンドポイントの設定です。

**Terraformからの接続:**  
main.tf 内で全てのAWSサービスの宛先を <http://localhost:4566> に向けています。

**AIエージェント（Docker）からの接続:**  
エージェントはコンテナ内で動いているため、localhost を指定すると自分自身を見に行ってしまいます。そのため、スキル（run.sh）内では宛先を <http://host.docker.internal:4566> に書き換える必要があります。

**CORS（Cross-Origin Resource Sharing）:**  
フロントエンド（ブラウザ）からLocalStackのS3やAPI Gatewayに直接アクセスするため、S3バケットとAPI Gatewayの両方に、適切なCORS許可設定をTerraformで記述しています。これがないとブラウザで画像が表示されません。

## ３. Gemiclaw導入とシステムとの連携設定内容

### 3.1 Gemiclawとは

**1.ローカル完結の安全な検証環境**  
フルローカル構成: 本物のクラウドを使わず、Docker上のLocalStackと通信するため、機密漏洩リスクを抑えて自由にAWS操作を試行錯誤できます。  
システムの自己保護: エージェントの根幹ロジックはコンテナイメージとして保護（読み取り専用）されており、エージェントが誤操作をしても自身のシステムを破壊することはありません。

**2.柔軟な機能拡張と運用手順の定型化**  
即時スキル獲得: 必要に応じて、会話を通じて新しいAWS操作用のスクリプト（スキル）をその場で追加し、機能を拡張できます。  
マニュアルによる安定運用: config/manuals/ に手順書を置くことで、複雑なAWSリソースの操作順序をエージェントに正確かつ再現性高く実行させることができます。

---

### 3.2 Gemiclawのセットアップ

公式リポジトリに書いてあるセットアップ/Discord Bot作成手順の通りに進めます。  
リポジトリ　<https://github.com/Nishina-N/gemiclaw>

**1. セットアップ項目**

* **前提条件の確認**: Docker環境、Gemini APIキー、Discord Botトークンの準備
* **リポジトリのクローン**: GitHubからのソースコード取得
* **環境変数の設定**: `.env` ファイルへのAPIキーとトークンの記述
* **Key BinderのAPIキー設定**: `secrets_for_skills.json` への外部サービス（Brave, Mapbox等）のキー設定
* **Google APIの設定（任意）**: 連携用ライブラリのインストールと認証実行
* **システムの起動**: Dockerコンテナのビルドとバックグラウンド実行
* **ログの確認**: 動作状況のモニタリング

**2. Discord Bot の作成とトークン取得項目**

* **アプリケーションの新規作成**: Discord Developer Portalでの登録
* **Botの追加とトークン取得**: Botユーザーの生成と認証トークンのコピー
* **Privileged Gateway Intentsの有効化**: 「SERVER MEMBERS」および「MESSAGE CONTENT」の権限許可
* **サーバーへの招待URL生成**: スコープ（bot）と権限（メッセージ送受信、履歴参照、ファイル添付等）の選択
* **Botの認証とサーバー参加**: 生成されたURLによる招待の実行
* **チャンネルIDの取得**: 開発者モードを使用した設定用IDのコピー  
  **注意：私は上記「チャンネルID」を「サーバーID」と勘違いして、はまりました。**  
  ![](https://static.zenn.studio/user-upload/a5955007fb35-20260320.png)

## ４. 写真管理システムの構成(設定ファイルとトラブルシューティング)

システムには「認証(ログイン/ログアウト)」、「写真のアップロード」「アップロード写真の一覧表を表示」「一覧表の1つの項目を変更/保存」という4つの機能があるのですが、同時にすべての機能を構築せず、次の順番で構築しました。  
①「認証(ログイン/ログアウト)」、「写真のアップロード」  
↓  
②「アップロード写真の一覧表を表示」  
↓  
③「一覧表の1つの項目を変更/保存」

### 4.1. システム概要と環境

目的: 社員がS3へ写真をアップロードし、管理者がその写真のステータス（未対応/対応済み）を管理できるWebアプリケーションの検証環境構築。

インフラ環境: LocalStack (ローカル上のAWSモック環境)  
IaC (Infrastructure as Code): Terraform  
バックエンド: AWS Lambda (Go言語 - provided.al2023 カスタムランタイム)  
フロントエンド: HTML / JavaScript (シングルページアプリケーション)  
使用サービス: API Gateway, Lambda, DynamoDB, S3, IAM, CloudWatch Logs

### 4.2. アーキテクチャとシステムフロー

システムは「ログイン時のロール（権限）」によって、フロントエンドの表示とバックエンドの通信先が動的に切り替わります。

**認証フロー (/login エンドポイント)**  
ユーザーがIDとパスワードを入力し、API Gateway経由で auth\_lambda を呼び出す。  
DynamoDB (AuthUser テーブル) を検索し、パスワード検証とロール（Admin または User）を取得。  
User の場合は、S3へ直接アップロードするための「署名付きURL (Presigned URL)」を発行して返す。

**社員フロー (Role: User)**  
フロントエンドは「アップロード画面」を表示。  
返却された署名付きURLを用いて、ブラウザから直接 S3 (my-photo-storage) へ画像を PUT 送信。  
(※S3への配置をトリガーに photo\_lambda が起動し、DynamoDBの PhotoMetadata テーブルへレコードを登録)

**管理者フロー (Role: Admin)**  
フロントエンドは「ステータス一覧画面」を表示し、自動的に /admin/list エンドポイントを呼び出す。  
admin\_list\_lambda が DynamoDB (PhotoMetadata) をスキャンし、全写真のリストを返す（Statusがない場合は「未対応」をデフォルトとする）。  
管理者が画面上の「ステータス変更ボタン」を押すと、/admin/update エンドポイント (admin\_update\_lambda) が呼ばれ、DynamoDBの対象レコードの Status を書き換える。

### 4.3. システム構造(論理構成図2回目)

```
AWS Environment (LocalStack / ap-northeast-1)
│
├── [ 入口 1 ] API Gateway (AuthAPI)
│   ├── /login (POST) ──────────> auth-handler (認証・トークン発行)
│   │   │
│   │   ├── /admin (管理者用)
│   │   │   ├── /list (GET) ────> admin-list-handler
│   │   │   └── /update (POST) ──> admin-update-handler
│   │   │
│   │   └── /stuff (一般社員用)
│   │       └── (S3へのUpload) ─┐
│                             　│
├── [ 入口 2 ] Storage Layer    │
│   └── S3: my-photo-storage <──┘ (ファイルが置かれる)
│       └── s3:ObjectCreated:* ───> photo-handler (自動起動・DB登録)    　  　
│
├── Compute Layer (Lambda Functions)
│   ├── auth-handler         # ユーザー認証 / AuthUserテーブル参照
│   ├── admin-list-handler   # メタデータ一覧取得 / PhotoMetadata参照
│   ├── admin-update-handler # メタデータ更新 / PhotoMetadata参照
│   └── photo-handler        # 【非同期】S3保存をトリガーにメタデータをDB登録
│
├── Storage & Database Layer
│   ├── S3: my-photo-storage     # 写真データ本体の保存 (CORS設定済)
│   ├── DynamoDB: AuthUser       # 認証用 (UserID / Password / Role)
│   └── DynamoDB: PhotoMetadata  # 写真管理用 (PhotoID / UserID [GSI])
│
└── AI Agent & Development (Local)
    ├── Gemiclaw (Docker)        # エージェント本体。API経由でシステムを操作
    └── Terraform (main.tf)      # インフラ全体のコード化 (IaC)
```

### 4.4. 以下設定ファイルの内容

main.tfの設定

```
# ==========================================
# 1. プロバイダー設定
# ==========================================
# 本番のAWSではなく、LocalStack（ローカルの疑似AWS環境）に接続するための設定です。
# 変数 use_LocalStack を切り替えるだけで、将来的にクラウド本番環境へデプロイ可能な構成にしています。

variable "use_LocalStack" {
  description = "LocalStackを使用するかどうか。trueでローカル、falseで本番AWS"
  type        = bool
  default     = true
}

provider "aws" {
  access_key                  = "test" # LocalStackでは任意の文字列でOK
  secret_key                  = "test"
  region                      = "ap-northeast-1"
  
  s3_use_path_style           = true   # LocalStack特有のバケット参照方式を有効化
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  # ローカル実行時のみ、エンドポイントをlocalhost:4566（LocalStack）に向ける動的設定
  dynamic "endpoints" {
    for_each = var.use_LocalStack ? [1] : []
    content {
      apigateway = "http://localhost:4566"
      lambda     = "http://localhost:4566"
      dynamodb   = "http://localhost:4566"
      s3         = "http://localhost:4566"
      iam        = "http://localhost:4566"
    }
  }
}

# ==========================================
# 2. DynamoDB: データの永続化
# ==========================================
# NoSQLデータベースです。ユーザー認証情報と写真のメタデータの2つのテーブルを定義しています。

# 認証用テーブル：UserIDを主キーとしてログイン情報を管理
resource "aws_dynamodb_table" "auth_table" {
  name         = "AuthUser"
  billing_mode = "PAY_PER_REQUEST" # 従量課金設定
  hash_key     = "UserID"

  attribute {
    name = "UserID"
    type = "S"
  }
}

# 写真メタデータ用テーブル：写真ごとの情報（所有者やアップロード日など）を管理
resource "aws_dynamodb_table" "photo_metadata_table" {
  name         = "PhotoMetadata"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "PhotoID"

  attribute {
    name = "PhotoID"
    type = "S"
  }

  attribute {
    name = "UserID"
    type = "S"
  }

  # インデックス設定：UserIDからその人の写真を高速に検索（Query）できるようにする
  global_secondary_index {
    name            = "UserIndex"
    hash_key        = "UserID"
    projection_type = "ALL"
  }
}

# 初期データ投入：検証用の「管理者(aataka)」と「社員(tanaka)」のアカウントを作成
resource "aws_dynamodb_table_item" "admin_user" {
  table_name = aws_dynamodb_table.auth_table.name
  hash_key   = aws_dynamodb_table.auth_table.hash_key
  item = jsonencode({
    "UserID":   {"S": "aataka"},
    "Password": {"S": "pass123"},
    "Role":     {"S": "Admin"}
  })
}

resource "aws_dynamodb_table_item" "staff_user" {
  table_name = aws_dynamodb_table.auth_table.name
  hash_key   = aws_dynamodb_table.auth_table.hash_key
  item = jsonencode({
    "UserID":   {"S": "tanaka"},
    "Password": {"S": "pass456"},
    "Role":     {"S": "User"}
  })
}

# ==========================================
# 3. S3: 写真保存用バケット & CORS設定
# ==========================================
# オブジェクトストレージ。実体となる写真ファイルを保存します。

resource "aws_s3_bucket" "photo_bucket" {
  bucket = "my-photo-storage"
}

# ブラウザからの直接アップロードを許可するためのセキュリティ設定（CORS）
resource "aws_s3_bucket_cors_configuration" "photo_cors" {
  bucket = aws_s3_bucket.photo_bucket.id
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "POST"]
    allowed_origins = ["*"] # 本番では特定のドメインに絞る必要があるポイント
    expose_headers  = ["ETag"]
  }
}

# ==========================================
# 4. IAM Roles & Policies（権限管理）
# ==========================================
# 「最小権限の原則」に基づき、LambdaがDynamoDBとS3にのみアクセスできるよう設定しています。

resource "aws_iam_role" "lambda_common_role" {
  name = "lambda_common_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" } }]
  })
}

# 基本的な実行ログ出力権限を付与
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_common_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# DynamoDBの読み書きと、S3バケット内のオブジェクト操作権限をまとめたポリシー
resource "aws_iam_role_policy" "lambda_combined_policy" {
  name = "lambda_combined_policy"
  role = aws_iam_role.lambda_common_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Action = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:Scan", "dynamodb:UpdateItem"], Effect = "Allow", Resource = "*" },
      { Action = ["s3:PutObject", "s3:GetObject"], Effect = "Allow", Resource = "${aws_s3_bucket.photo_bucket.arn}/*" }
    ]
  })
}

# ==========================================
# 5. Lambda Functions（サーバーレス処理）
# ==========================================
# Go言語で記述された「ビジネスロジック」の実行環境です。

# 認証処理用：ログイン要求を処理し、S3アップロード用の署名付きURLなどを生成
resource "aws_lambda_function" "auth_lambda" {
  function_name = "auth-handler"
  handler       = "bootstrap"
  runtime       = "provided.al2023" # Go/Rust用のカスタムランタイム
  role          = aws_iam_role.lambda_common_role.arn
  filename      = "auth_lambda.zip"
  environment {
    variables = {
      DYNAMO_TABLE = aws_dynamodb_table.auth_table.name
      PHOTO_BUCKET = aws_s3_bucket.photo_bucket.id
      S3_HOSTNAME  = "localhost"
    }
  }
}

# 写真登録用：S3にファイルが置かれたことを検知して、メタデータをDynamoDBに自動登録
resource "aws_lambda_function" "photo_lambda" {
  function_name = "photo-handler"
  handler       = "bootstrap"
  runtime       = "provided.al2023"
  role          = aws_iam_role.lambda_common_role.arn
  filename      = "photo_lambda.zip"
  environment {
    variables = { METADATA_TABLE = aws_dynamodb_table.photo_metadata_table.name }
  }
}

# 管理者機能（一覧取得）
resource "aws_lambda_function" "admin_list_lambda" {
  function_name = "admin-list-handler"
  handler       = "bootstrap"
  runtime       = "provided.al2023"
  role          = aws_iam_role.lambda_common_role.arn
  filename      = "admin_list.zip"
  source_code_hash = filebase64sha256("admin_list.zip") # コード変更時に自動検知して再デプロイ
  environment {
    variables = { METADATA_TABLE = aws_dynamodb_table.photo_metadata_table.name }
  }
}

# 管理者機能（ステータス更新）
resource "aws_lambda_function" "admin_update_lambda" {
  function_name    = "admin-update-handler"
  handler          = "bootstrap"
  runtime          = "provided.al2023"
  role             = aws_iam_role.lambda_common_role.arn
  filename         = "admin_update.zip"
  source_code_hash = filebase64sha256("admin_update.zip")
  environment {
    variables = { METADATA_TABLE = aws_dynamodb_table.photo_metadata_table.name }
  }
}

# ==========================================
# 6. S3イベント通知設定（自動化の要）
# ==========================================
# 「S3に写真が保存された」というイベントをきっかけにLambdaを動かす設定です。
# 運用エンジニアとしては、この「非同期処理」の流れを把握しておくことが重要です。

resource "aws_lambda_permission" "allow_s3" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.photo_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.photo_bucket.arn
}

resource "aws_s3_bucket_notification" "photo_notification" {
  bucket = aws_s3_bucket.photo_bucket.id
  lambda_function {
    lambda_function_arn = aws_lambda_function.photo_lambda.arn
    events              = ["s3:ObjectCreated:*"] # 新規作成時に発火
  }
  depends_on = [aws_lambda_permission.allow_s3]
}

# ==========================================
# 7. API Gateway（外部接続窓口）
# ==========================================
# HTTPリクエストを受け取り、各Lambdaへ橋渡しする司令塔です。

resource "aws_api_gateway_rest_api" "auth_api" { name = "AuthAPI" }

# 各エンドポイント（/login, /admin/list, /admin/update）のルーティング定義
# ここでは「AWS_PROXY」を使用し、リクエスト情報を丸ごとLambdaに渡しています。

# --- login ---
resource "aws_api_gateway_resource" "login" {
  rest_api_id = aws_api_gateway_rest_api.auth_api.id
  parent_id   = aws_api_gateway_rest_api.auth_api.root_resource_id
  path_part   = "login"
}

resource "aws_api_gateway_method" "login_post" {
  rest_api_id   = aws_api_gateway_rest_api.auth_api.id
  resource_id   = aws_api_gateway_resource.login.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "login_int" {
  rest_api_id             = aws_api_gateway_rest_api.auth_api.id
  resource_id             = aws_api_gateway_resource.login.id
  http_method             = aws_api_gateway_method.login_post.http_method
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.auth_lambda.invoke_arn
  integration_http_method = "POST"
}

# (中略: admin関連のエンドポイント設定)

# --- CORS (OPTIONS) Settings ---
# フロントエンド（React等）からAPIを呼ぶために必要な「おまじない」の設定です。
# 実際にはこれが正しく設定されていないと通信エラーになる、トラブルシューティングの頻出箇所です。

resource "aws_api_gateway_method" "options" {
  rest_api_id   = aws_api_gateway_rest_api.auth_api.id
  resource_id   = aws_api_gateway_resource.login.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# ... (中略: OPTIONSメソッドの詳細レスポンス定義) ...

# ==========================================
# 8. アウトプット（構築後の確認用）
# ==========================================
# デプロイ完了後、接続先となるURLを表示します。

output "api_url" {
  value = "http://localhost:4566/restapis/${aws_api_gateway_rest_api.auth_api.id}/${aws_api_gateway_stage.dev.stage_name}/_user_request_/login"
}

output "admin_api_url" {
  value = "http://localhost:4566/restapis/${aws_api_gateway_rest_api.auth_api.id}/${aws_api_gateway_stage.dev.stage_name}/_user_request_/admin/list"
}
```

index.htmlの設定

```
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Engineer Portfolio</title>
    <style>
        /* スタイル定義：直感的なUIにするため、ログイン状態に応じて表示/非表示を切り替えます */
        body { font-family: sans-serif; padding: 20px; line-height: 1.6; }
        .container { max-width: 600px; margin: auto; border: 1px solid #ccc; padding: 20px; border-radius: 8px; position: relative; }
        input { width: 100%; margin-bottom: 10px; padding: 8px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; cursor: pointer; border-radius: 4px; }
        .logout-btn { position: absolute; top: 10px; right: 10px; width: auto; background: #dc3545; padding: 5px 10px; font-size: 0.8em; }
        .status { margin-top: 20px; padding: 10px; background: #f4f4f4; font-size: 0.9em; word-break: break-all; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>

<div class="container">
    <button id="logoutBtn" class="logout-btn" onclick="handleLogout()" style="display:none;">ログアウト</button>

    <div id="loginSection">
        <h2>Login</h2>
        <input type="text" id="userId" placeholder="User ID">
        <input type="password" id="password" placeholder="Password">
        <button onclick="handleLogin()">Login</button>
    </div>

    <div id="uploadSection" style="display:none; margin-top:20px;">
        <h3>Upload Photo</h3>
        <input type="file" id="photoFile" accept="image/*">
        <button onclick="handleUpload()" style="background: #28a745;">Upload to S3</button>
    </div>

    <div id="adminSection" style="display:none; margin-top:20px;">
        <h3>【管理者】提出写真ステータス一覧</h3>
        <table id="adminTable">
            <thead>
                <tr>
                    <th>アップロード者</th>
                    <th>ファイル名</th>
                    <th>ステータス</th>
                </tr>
            </thead>
            <tbody id="photoTableBody"></tbody>
        </table>
    </div>

    <div id="status" class="status">ステータス: 待機中</div>
</div>

<script>
    /* ============================================================
     * バックエンド接続設定
     * ============================================================
     * Terraformで作成された API Gateway のエンドポイントURLを指定します。
     * LocalStack環境のため、localhost:4566 を経由してアクセスします。
     */
    const BASE_URL = "http://localhost:4566/restapis/vc4skgpwm1/dev/_user_request_";

    // S3へ直接アップロードするための「署名付きURL」を一時保存する変数
    let presignedUrl = ""; 

    /**
     * handleLogin: ユーザー認証処理
     * 1. API Gateway(/login)へID/PASSを送信
     * 2. LambdaがDynamoDBを参照し、認証結果と「ロール(権限)」を返却
     * 3. 一般ユーザーには「S3アップロード用のURL」も同時に発行
     */
    async function handleLogin() {
        const id = document.getElementById('userId').value;
        const pass = document.getElementById('password').value;
        const statusDiv = document.getElementById('status');
        statusDiv.innerText = "認証中...";

        try {
            const response = await fetch(`${BASE_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: id, pass: pass })
            });

            const data = await response.json();

            if (response.ok) {
                statusDiv.innerText = "ログイン成功！";
                document.getElementById('loginSection').style.display = 'none';
                document.getElementById('logoutBtn').style.display = 'block';

                // ロールに基づいた画面の出し分け（認可制御のフロントエンド実装）
                if (data.role === "Admin") {
                    document.getElementById('adminSection').style.display = 'block';
                    loadAdminData(); // 管理者画面のデータをロード
                } else {
                    document.getElementById('uploadSection').style.display = 'block';
                    // サーバーから取得した「署名付きURL」を保持（有効期限があるため一時的に保持）
                    presignedUrl = data.uploadUrl;
                }
            } else {
                statusDiv.innerText = "エラー: " + (data.message || "認証失敗");
            }
        } catch (err) {
            statusDiv.innerText = "通信エラー: " + err.message;
        }
    }

    /**
     * handleLogout: セッションのリセット
     * クライアント側の状態を初期化し、認証情報の漏洩を防ぎます。
     */
    function handleLogout() {
        document.getElementById('loginSection').style.display = 'block';
        document.getElementById('uploadSection').style.display = 'none';
        document.getElementById('adminSection').style.display = 'none';
        document.getElementById('logoutBtn').style.display = 'none';
        document.getElementById('userId').value = "";
        document.getElementById('password').value = "";
        document.getElementById('status').innerText = "ステータス: ログアウトしました";
        presignedUrl = "";
    }

    /**
     * loadAdminData: 管理者用データの一覧取得
     * API Gateway(/admin/list)を経由して、DynamoDBに保存された全写真のメタデータを取得します。
     */
    async function loadAdminData() {
        try {
            const res = await fetch(`${BASE_URL}/admin/list`);
            const photos = await res.json();
            const tbody = document.getElementById('photoTableBody');
            
            // 取得したJSONデータをHTMLのテーブル行へ変換
            tbody.innerHTML = photos.map(p => {
                const currentStatus = p.status || "未対応";
                const nextStatus = currentStatus === '対応済み' ? '未対応' : '対応済み';
                return `
                    <tr>
                        <td>${p.userId}</td>
                        <td>${p.photoId.split('/').pop()}</td>
                        <td>
                            <b style="color: ${currentStatus === '対応済み' ? 'green' : 'red'};">${currentStatus}</b>
                            <button onclick="toggleStatus('${p.photoId}', '${nextStatus}')" style="width: auto; margin-left:10px; padding:2px 5px; font-size:0.8em; background:#6c757d;">
                                ${nextStatus}にする
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
        } catch (e) { console.error(e); }
    }

    /**
     * toggleStatus: ステータスの更新処理
     * API Gateway(/admin/update)へ、対象の写真IDと新しいステータスを送信し、DynamoDBを更新します。
     */
    async function toggleStatus(photoId, newStatus) {
        document.getElementById('status').innerText = "ステータス更新中...";
        try {
            const response = await fetch(`${BASE_URL}/admin/update`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ photoId: photoId, status: newStatus })
            });
            if (response.ok) {
                document.getElementById('status').innerText = "DBを更新しました。";
                loadAdminData(); // 最新の状態を再描画
            }
        } catch (e) { document.getElementById('status').innerText = "エラー: " + e.message; }
    }

    /**
     * handleUpload: S3への直接アップロード
     * 【重要】APIサーバーを経由せず、AWS S3が発行した「署名付きURL」に対して
     * PUTメソッドでファイルを直接送信します。これによりAPIサーバーの負荷を軽減できます。
     */
    async function handleUpload() {
        const fileInput = document.getElementById('photoFile');
        if (!fileInput.files[0] || !presignedUrl) return;
        document.getElementById('status').innerText = "アップロード中...";
        try {
            // S3の署名付きURLへバイナリデータを送信
            const response = await fetch(presignedUrl, { method: 'PUT', body: fileInput.files[0] });
            if (response.ok) {
                document.getElementById('status').innerText = "完了！ S3へのアップロードに成功しました。";
                // この後、S3のイベント通知機能により自動的にLambdaが起動し、DBに登録されます。
            }
        } catch (err) { document.getElementById('status').innerText = "エラー: " + err.message; }
    }
</script>
</body>
</html>
```

auth/main.goの設定

```
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

/**
 * CORS解除用共通ヘッダー
 * ブラウザ（フロントエンド）からのリクエストを許可するために必須の設定です。
 * 運用フェーズでは、セキュリティ向上のため "*" ではなく特定のドメインに制限する検討が必要です。
 */
var corsHeaders = map[string]string{
	"Access-Control-Allow-Origin":  "*",
	"Access-Control-Allow-Methods": "POST,OPTIONS",
	"Access-Control-Allow-Headers": "Content-Type",
}

/**
 * handler: Lambdaのメインロジック
 * 役割：ユーザー認証、ロール（権限）の判定、S3署名付きURLの発行
 */
func handler(ctx context.Context, request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	// 1. リクエストボディのパース
	// フロントエンドから送られてきた JSON（ID/Pass）を構造体にマッピングします。
	var req struct {
		ID   string `json:"id"`
		Pass string `json:"pass"`
	}
	json.Unmarshal([]byte(request.Body), &req)

	if req.ID == "" {
		return events.APIGatewayProxyResponse{StatusCode: 401, Headers: corsHeaders}, nil
	}

	// 2. AWS SDK の接続設定 (LocalStack 用の特殊設定)
	// 本番AWSでは config.LoadDefaultConfig(ctx) だけで済みますが、
	// ローカル検証環境（Docker/LocalStack）ではエンドポイントの手動書き換えが必要です。
	cfg, _ := config.LoadDefaultConfig(ctx,
		config.WithRegion("ap-northeast-1"),
		config.WithEndpointResolverWithOptions(aws.EndpointResolverWithOptionsFunc(
			func(service, region string, options ...interface{}) (aws.Endpoint, error) {
				// ネットワーク構成のポイント：
				// LambdaコンテナからLocalStackコンテナへ通信するため "host.docker.internal" を使用。
				return aws.Endpoint{
					URL:               "http://host.docker.internal:4566",
					SigningRegion:     "ap-northeast-1",
					HostnameImmutable: true,
				}, nil
			})),
	)

	// DynamoDBクライアントの初期化
	dbClient := dynamodb.NewFromConfig(cfg)

	// S3クライアントの初期化
	s3Client := s3.NewFromConfig(cfg, func(o *s3.Options) {
		// 重要：署名URLのホスト名書き換え
		// 署名URLは「ブラウザ（Windows）」が解釈するため、コンテナ内名称ではなく
		// Windowsから見える "localhost" をベースに発行する必要があります。
		o.BaseEndpoint = aws.String("http://localhost:4566")
	})
	presignClient := s3.NewPresignClient(s3Client)

	// 3. DynamoDB からユーザー情報を取得
	// 環境変数 DYNAMO_TABLE を使用することで、テーブル名の変更に柔軟に対応できる運用設計にしています。
	tableName := os.Getenv("DYNAMO_TABLE")
	out, err := dbClient.GetItem(ctx, &dynamodb.GetItemInput{
		TableName: aws.String(tableName),
		Key: map[string]types.AttributeValue{
			"UserID": &types.AttributeValueMemberS{Value: req.ID},
		},
	})

	// ユーザーが存在しない、または取得エラー時のハンドリング
	if err != nil || out.Item == nil {
		return events.APIGatewayProxyResponse{
			StatusCode: 401,
			Headers:    corsHeaders,
			Body:       `{"message":"User not found"}`,
		}, nil
	}

	// パスワードチェック (検証用のため簡易比較)
	// 実運用では bcrypt 等でのハッシュ化比較が必須となるポイントです。
	dbPass := out.Item["Password"].(*types.AttributeValueMemberS).Value
	if dbPass != req.Pass {
		return events.APIGatewayProxyResponse{
			StatusCode: 401,
			Headers:    corsHeaders,
			Body:       `{"message":"Invalid password"}`,
		}, nil
	}

	// 権限（Role）の取得：Admin か User かを判定し、フロントエンドの挙動を制御します。
	role := "User"
	if r, ok := out.Item["Role"].(*types.AttributeValueMemberS); ok {
		role = r.Value
	}

	// 4. S3 署名付きURLの生成 (セキュアなアップロード)
	// メリット：S3バケットを公開（Public）にすることなく、特定のユーザーに
	// 期間限定（15分間）でアップロード権限を安全に委譲できます。
	bucketName := os.Getenv("PHOTO_BUCKET")
	// ファイル名にタイムスタンプを付与し、上書きを防止
	objectKey := fmt.Sprintf("uploads/%s/%d.jpg", req.ID, time.Now().Unix())

	presignedReq, err := presignClient.PresignPutObject(ctx, &s3.PutObjectInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(objectKey),
	}, s3.WithPresignExpires(15*time.Minute))

	if err != nil {
		return events.APIGatewayProxyResponse{StatusCode: 500, Headers: corsHeaders}, nil
	}

	// 5. レスポンスの生成
	// 生成したURL、ロール、メッセージを JSON 形式でフロントエンドへ返却。
	resBody, _ := json.Marshal(map[string]string{
		"uploadUrl": presignedReq.URL,
		"role":      role,
		"message":   "success",
	})

	return events.APIGatewayProxyResponse{
		StatusCode: 200,
		Headers:    corsHeaders,
		Body:       string(resBody),
	}, nil
}

func main() {
	// Lambda 実行開始
	lambda.Start(handler)
}
```

photo/main.goの設定

```
package main

import (
	"context"
	"net/url" // S3のオブジェクトキーに含まれる特殊文字（スペースが+になる等）を正しく扱うためのデコード用
	"os"
	"strings"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
)

/**
 * handler: S3イベント通知を受け取るメインロジック
 * 役割：S3に保存されたファイルパスを解析し、DynamoDBにメタデータとして登録する
 */
func handler(ctx context.Context, s3Event events.S3Event) error {
	// --- 1. AWS SDK / LocalStack 接続設定 ---
	// 本番AWSではなく、ローカルの疑似環境(LocalStack)へ接続を誘導します。
	cfg, err := config.LoadDefaultConfig(ctx,
		config.WithRegion("ap-northeast-1"),
		config.WithEndpointResolverWithOptions(aws.EndpointResolverWithOptionsFunc(
			func(service, region string, options ...interface{}) (aws.Endpoint, error) {
				// コンテナ間通信のためのエンドポイント指定
				// host.docker.internal を使用して Docker ホスト側の LocalStack へアクセス
				return aws.Endpoint{
					URL:           "http://host.docker.internal:4566",
					SigningRegion: "ap-northeast-1",
				}, nil
			})),
	)
	if err != nil {
		return err // 初期化失敗時は即座にエラーを返し、Lambdaをリトライまたは失敗させる
	}

	// DynamoDB操作用のクライアントを作成
	dbClient := dynamodb.NewFromConfig(cfg)

	// --- 2. イベントレコードのループ処理 ---
	// S3は一度に複数のファイルを通知する場合があるため、1件ずつ確実に処理します。
	for _, record := range s3Event.Records {
		
		// --- ファイル名のデコード処理（運用上の重要ポイント） ---
		// S3の通知に含まれるKeyは URLエンコード（例: 空白が"+"になる）されています。
		// これをそのままDBに入れると検索に失敗するため、元の名前に復元します。
		rawKey := record.S3.Object.Key
		key, err := url.QueryUnescape(rawKey)
		if err != nil {
			key = rawKey // デコード失敗時はフォールバックとして元の値を使用
		}
		
		// --- 3. ユーザーIDの抽出ロジック（パス設計への依存） ---
		// パスが "uploads/{UserID}/{filename}" であるという設計に基づき、UserIDを切り出します。
		// 運用エンジニアとしては、このパス構造が崩れるとデータ登録に失敗することを把握しておく必要があります。
		parts := strings.Split(key, "/")
		if len(parts) < 3 {
			// ディレクトリ階層が足りない不正なファイル配置は無視（エラーログとして残すのが実務的）
			continue 
		}
		userID := parts[1] // "uploads" の次の要素が UserID

		// --- 4. DynamoDBへの書き
```

admin\_list/main.goの設定

```
package main

import (
	"context"
	"encoding/json"
	"os"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
)

/**
 * CORS対応ヘッダー
 * 管理画面（フロントエンド）から一覧取得APIを呼び出すために設定しています。
 */
var corsHeaders = map[string]string{
	"Access-Control-Allow-Origin":  "*",
	"Access-Control-Allow-Methods": "GET,OPTIONS",
	"Access-Control-Allow-Headers": "Content-Type",
}

/**
 * handler: 写真メタデータ一覧取得ロジック
 * 役割：DynamoDBからすべての写真情報を取得し、管理画面用のフォーマットで返却する
 */
func handler(ctx context.Context, request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	// --- 1. AWS SDK / LocalStack 接続設定 ---
	// 他のLambdaと同様に、コンテナ間通信（host.docker.internal）を介してLocalStackへ接続します。
	cfg, _ := config.LoadDefaultConfig(ctx,
		config.WithRegion("ap-northeast-1"),
		config.WithEndpointResolverWithOptions(aws.EndpointResolverWithOptionsFunc(
			func(service, region string, options ...interface{}) (aws.Endpoint, error) {
				return aws.Endpoint{
					URL: "http://host.docker.internal:4566",
					SigningRegion: "ap-northeast-1",
				}, nil
			})),
	)

	dbClient := dynamodb.NewFromConfig(cfg)

	// --- 2. DynamoDB Scan 操作 ---
	// 【運用上の注意点】
	// Scanはテーブルの全データを読み取るため、データ量が増えるとパフォーマンスが低下し、コストも増大します。
	// 今回はポートフォリオ規模のためScanを採用していますが、実運用では
	// クエリ（Query）やページネーションの実装を検討すべき箇所です。
	result, err := dbClient.Scan(ctx, &dynamodb.ScanInput{
		TableName: aws.String(os.Getenv("METADATA_TABLE")),
	})
	if err != nil {
		// データベース接続エラー等の場合、500エラーを返して異常を通知します。
		return events.APIGatewayProxyResponse{StatusCode: 500, Headers: corsHeaders, Body: err.Error()}, nil
	}

	// --- 3. レスポンス用構造体の定義 ---
	// DynamoDBの型（AttributeValue）を、フロントエンドが扱いやすい単純なJSON構造に変換します。
	type PhotoRecord struct {
		PhotoID string `json:"photoId"`
		UserID  string `json:"userId"`
		Status  string `json:"status"`
	}

	records := []PhotoRecord{}
	for _, item := range result.Items {
		// --- データ整合性の担保 ---
		// Status属性は、後から追加された仕様や未対応のデータでは存在しない可能性があります。
		// その場合でもシステムがクラッシュしないよう、「未対応」という初期値を設定する「防御的プログラミング」を行っています。
		status := "未対応"
		if s, ok := item["Status"].(*types.AttributeValueMemberS); ok {
			status = s.Value
		}

		// 取得した各項目を構造体に格納
		records = append(records, PhotoRecord{
			PhotoID: item["PhotoID"].(*types.AttributeValueMemberS).Value,
			UserID:  item["UserID"].(*types.AttributeValueMemberS).Value,
			Status:  status,
		})
	}

	// --- 4. JSONレスポンスの返却 ---
	resBody, _ := json.Marshal(records)
	return events.APIGatewayProxyResponse{
		StatusCode: 200,
		Headers:    corsHeaders,
		Body:       string(resBody),
	}, nil
}

func main() {
	// Lambdaランタイムの開始
	lambda.Start(handler)
}
```

admin\_update/main.goの設定

```
package main

import (
	"context"
	"encoding/json"
	"log"
	"os"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
)

/**
 * UpdateRequest: フロントエンドから送られてくる更新データ
 * どの写真(PhotoID)を、どの状態(Status)に変えるかを定義します。
 */
type UpdateRequest struct {
	PhotoID string `json:"photoId"`
	Status  string `json:"status"`
}

/**
 * handler: ステータス更新ロジック
 * 役割：特定の写真レコードの「Status」属性を、指定された値（対応済み等）に書き換えます。
 */
func handler(ctx context.Context, request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	// --- 1. CORS対応ヘッダー ---
	// 管理画面からのPOSTリクエストを許可するために設定。
	corsHeaders := map[string]string{
		"Access-Control-Allow-Origin":  "*",
		"Access-Control-Allow-Methods": "POST,OPTIONS",
		"Access-Control-Allow-Headers": "Content-Type",
	}

	// --- 2. リクエストのバリデーション ---
	var req UpdateRequest
	if err := json.Unmarshal([]byte(request.Body), &req); err != nil {
		// 不正なJSON形式が送られてきた場合、400 Bad Request を返して即座に終了。
		return events.APIGatewayProxyResponse{StatusCode: 400, Headers: corsHeaders, Body: "Invalid JSON"}, nil
	}

	// --- 3. AWS SDK / LocalStack 接続設定 ---
	// 他のLambdaと一貫性を持たせ、host.docker.internal経由でLocalStackへ接続します。
	cfg, _ := config.LoadDefaultConfig(ctx,
		config.WithRegion("ap-northeast-1"),
		config.WithEndpointResolverWithOptions(aws.EndpointResolverWithOptionsFunc(
			func(service, region string, options ...interface{}) (aws.Endpoint, error) {
				return aws.Endpoint{URL: "http://host.docker.internal:4566", SigningRegion: "ap-northeast-1"}, nil
			})),
	)

	dbClient := dynamodb.NewFromConfig(cfg)

	// --- 4. DynamoDBのデータ更新 (UpdateItem) ---
	// 【技術的ポイント：予約語の回避】
	// 「Status」という単語はDynamoDBの予約語であるため、直接記述するとエラーになります。
	// そのため、#s というプレースホルダー（ExpressionAttributeNames）を使用して安全に更新します。
	_, err := dbClient.UpdateItem(ctx, &dynamodb.UpdateItemInput{
		TableName: aws.String(os.Getenv("METADATA_TABLE")),
		Key: map[string]types.AttributeValue{
			"PhotoID": &types.AttributeValueMemberS{Value: req.PhotoID},
		},
		// 「Status属性を、変数 :val の値でセットする」という命令
		UpdateExpression:          aws.String("SET #s = :val"),
		ExpressionAttributeNames:  map[string]string{"#s": "Status"},
		ExpressionAttributeValues: map[string]types.AttributeValue{
			":val": &types.AttributeValueMemberS{Value: req.Status},
		},
	})

	if err != nil {
		// --- 運用上のエラー追跡 ---
		// エラーログを標準出力に出すことで、CloudWatch Logs（LocalStackログ）から
		// 障害原因を特定しやすくしています。
		log.Printf("Update Error: %v", err)
		return events.APIGatewayProxyResponse{StatusCode: 500, Headers: corsHeaders, Body: err.Error()}, nil
	}

	// --- 5. 成功レスポンス ---
	return events.APIGatewayProxyResponse{
		StatusCode: 200,
		Headers:    corsHeaders,
		Body:       `{"result":"Updated Successfully", "updated": true}`,
	}, nil
}

func main() {
	// Lambdaランタイムの開始
	lambda.Start(handler)
}
```

---

### 4.5. トラブルシューティング

#### 【フェーズA：インフラ基盤の構築エラー】

**エラー①：Lambda 作成時の "Docker not available"**

* **現象**: Terraform で Lambda をデプロイしようとすると、`ResourceNotReady` でタイムアウトする。
* **原因**: LocalStack は Lambda の実行に Docker コンテナを使用するが、LocalStack コンテナ自体がホスト側の Docker デーモンにアクセスできていなかった。
* **解決策**: Docker 起動時にホストのソケットをマウントし、コンテナ内から Docker 操作を可能にした。

  ```
  docker run -d -v /var/run/docker.sock:/var/run/docker.sock ... LocalStack/LocalStack
  ```

**エラー②：DynamoDB の `ConditionalCheckFailedException`**

* **現象**: `terraform apply` 時に初期データの投入（`aws_dynamodb_table_item`）が失敗する。
* **原因**: LocalStack を再起動せずに Terraform を再実行したため、既に存在する ID と衝突した。
* **解決策**: AWS CLI で対象アイテムを手動削除、または `terraform destroy` を挟むことで状態の整合性を確保。

---

#### 【フェーズB：バックエンド（Go/Lambda）の実行エラー】

**エラー③：謎の "bootstrap: no such file or directory"**

* **現象**: API を叩くと `502 Bad Gateway` が発生し、Lambda の実行自体が失敗する。
* **原因**: Go のバイナリ名が `main` のままだった。Amazon Linux 2023 (al2023) ランタイムでは、実行ファイル名を必ず `bootstrap` にする必要がある。
* **解決策**: ビルド時の出力ファイル名を指定し、ZIP 化する。

  ```
  GOOS=linux GOARCH=amd64 go build -o bootstrap main.go
  ```

**エラー④：Lambda ログの沈黙（カスタムログが表示されない）**

* **現象**: `logs tail --follow` で監視しても、`START/END` ログしか出ず、自分の書いた `log.Printf` が出ない。
* **原因**: バイナリの更新が反映されていない、あるいはハンドラーの引数（JSON構造体）の定義ミスによる即時エラー。
* **解決策**: 一旦ビルド済みファイルを全削除し、関数の入り口に「強制的な生存確認ログ」を仕込んでデプロイ。

---

#### 【フェーズC：フロントエンド & 開発環境の不具合】

**エラー⑤：VS Code ターミナルの「二重丸（◎）」と描画フリーズ**

* **現象**: プロンプトの表示が崩れ、入力した文字やペーストしたコマンドが見えなくなる。
* **原因**: WSL2 の Ubuntu 側が想定するプロンプトアイコンと、VS Code の GPU レンダリングエンジンとの競合。
* **解決策**: `Integrated: GPU Acceleration` を `off` にし、`stty echo` でシリアル通信のような「エコー」設定を強制復帰。

**エラー⑥：API Gateway の CORS ポリシー違反**

* **現象**: ブラウザからログインしようとすると、コンソールに赤い CORS エラーが出る。
* **原因**: セキュリティ上の理由で、API Gateway が `Access-Control-Allow-Origin` ヘッダーを返していない。
* **解決策**: Terraform で `OPTIONS` メソッド（Preflight リクエスト）に対するレスポンスを定義し、LocalStack がヘッダーを返すように構成。

---

#### 【フェーズD：Git & GitHub によるバックアップの失敗】

**エラー⑦：GitHub の 100MB 制限（巨大な AWS プロバイダー）**

* **現象**: `git push` が `remote rejected` で拒否される。
* **原因**: `.terraform/` フォルダ内の巨大な実行ファイル（800MB超）をコミットに含めてしまった。
* **解決策**: `.gitignore` を作成し、`git rm -r --cached .` でキャッシュを抹消。`git commit --amend` で過去の巨大ファイルを「なかったこと」にしてから、`--force` でプッシュ。

**エラー⑧：恐怖の「入れ子リポジトリ（Nested Git）」**

* **現象**: フォルダ内にフォルダがある構成で、GitHub 上で中身が空っぽ（グレーアウト）になる。
* **原因**: `gemiclaw/gemiclaw/` のように深い階層に別の `.git` フォルダが残っており、サブモジュールとして誤認された。
* **解決策**: 内側の `.git` を `rm -rf` で完全削除。外側のリポジトリのキャッシュをクリアして再登録。

---

## 5. AIエージェントでシステムのログが確認できるか検証

GemiclawとDiscordですぐやりとりできたので、LocalStack上のログを確認するためのスキルもすぐ作成できるだろうと思いましたが、簡単ではありませんでした。

#### 1：AIが新しいスキル（ツール）を認識しない

* **発生した事象**: ホスト側でスキルディレクトリ（`check_aws_logs`）を作成したが、AIエージェントに「見当たらない」と返された。
* **原因**: AIエージェントはコンテナ起動時にスキル一覧をスキャンしてメモリにロードするため、起動後にホスト側で追加されたファイルをリアルタイムには認知できない。
* **対応策**: コンテナの再起動（`docker-compose restart`）、または再ビルドを行う。
* **なぜ有効なのか**: コンテナの再起動により初期化プロセスが再度走り、ホスト側で追加されたディレクトリがコンテナ内に正しくマウントされ、AIの「利用可能なツールリスト」に登録されるため。

#### 2：ログが存在しない（ResourceNotFoundException） - 仕様の壁

* **発生した事象**: AIがスキルを認識し実行したが、`ResourceNotFoundException` が発生し、ロググループが見つからないと報告された。
* **原因**: LocalStack（および実際のAWS）の仕様として、Lambda関数をデプロイしただけではCloudWatchのロググループは作成されない。関数が**最低1回実行されて初めてログストリームが生成される**ため。
* **対応策**: `aws lambda invoke` コマンドやフロントエンドの画面操作を通じて、対象のLambda（`admin-update-handler`）を一度実行させる。
* **なぜ有効なのか**: 実行エンジンが動くことで物理的にログが書き込まれる先（ロググループ）が生成され、AWS CLIからの取得リクエストが通るようになるため。

#### 3：見えているのに取れない（ResourceNotFoundException） - ロジックの壁

* **発生した事象**: 一覧取得スキル（`list_aws_logs`）でログの存在は確認できたのに、フルネームで取得を依頼すると依然としてエラーになる。
* **原因**: 取得用スクリプト（`run.sh`）内で親切心から自動付与していた `/aws/lambda/` プレフィックスと、AIが渡してきたフルパスが合体し、`/aws/lambda//aws/lambda/admin-update-handler` という二重パスになっていた。
* **対応策**: `run.sh` 内に、入力文字列が `/aws/lambda/` で始まっているかを判定するIF文を追加し、プレフィックスの二重付与を防ぐ。
* **なぜ有効なのか**: AIが「関数名」だけを渡しても「フルパス」を渡しても、スクリプト側でよしなに正規化して正しいAWSコマンドを組み立てられるようになるため。

#### 4：AIフレームワークの引数渡し仕様（空の変数を参照）

* **発生した事象**: 手動でスクリプトを実行すると成功するのに、AIがスキルを呼び出すとエラーになる。
* **原因**: 通常のシェルスクリプトのように `$1` で引数を受け取る設計にしていたが、エージェントの仕様上、AIからの引数は **環境変数 `SKILL_ARGS` にJSON文字列として格納されて渡される** ため、`$1` が空になっていた。
* **対応策**: `run.sh` 内でPythonのワンライナーを実行し、`SKILL_ARGS` のJSONをパースして引数（`function_name`）を抽出するように修正。

  ```
  INPUT_NAME=$(python3 -c "import sys,json,os; print(json.loads(os.environ['SKILL_ARGS'])['function_name'])")
  ```
* **なぜ有効なのか**: エージェントシステム固有の「JSONによるパラメータ渡し」の仕様にスクリプトが適合し、AIの意図した引数が正確にAWS CLIコマンドにマッピングされるため。

#### 5：Pythonライブラリの競合（urllib3 / ImportError）

* **発生した事象**: DynamoDBをスキャンする新しいスキルを実行した際、`ImportError: cannot import name 'DEFAULT_CIPHERS'` というエラーが発生し、AWS CLIが動かなくなった。
* **原因**: AIエージェントを動かすためのPython環境（`/app/config/pip_packages/` にある `urllib3` など）と、システムにインストールされた `awscli` が内部で依存しているPythonライブラリのバージョンが衝突（干渉）を起こした。
* **対応策**: スキルの `run.sh` において、`aws` コマンドを実行する直前（またはその行のみ）で、環境変数 `PYTHONPATH` を一時的にクリアする。

  ```
  # 実行例
  PYTHONPATH="" aws --endpoint-url=http://host.docker.internal:4566 dynamodb scan ...
  ```
* **なぜ有効なのか**: `PYTHONPATH` を空にすることで、AWS CLIはコンテナ内のAI用ライブラリ（pip\_packages）を見に行かず、システム標準のクリーンなライブラリだけを使用して実行されるため、依存関係のバッティングを完全に回避できる。

---

下記がGemiclawと話した内容になります。  
![](https://static.zenn.studio/user-upload/f6608e4a9994-20260320.png)  
![](https://static.zenn.studio/user-upload/086317ea2862-20260320.png)  
![](https://static.zenn.studio/user-upload/38b2ed1d3d47-20260320.png)  
![](https://static.zenn.studio/user-upload/02ab9218cd0a-20260320.png)  
![](https://static.zenn.studio/user-upload/e22e986b000c-20260320.png)  
![](https://static.zenn.studio/user-upload/09d95cec5131-20260320.png)  
![](https://static.zenn.studio/user-upload/6373ea611796-20260320.png)  
![](https://static.zenn.studio/user-upload/42b4b060e2da-20260320.png)  
![](https://static.zenn.studio/user-upload/e4e460ae45c2-20260320.png)  
![](https://static.zenn.studio/user-upload/dc1e3f0820ac-20260320.png)  
![](https://static.zenn.studio/user-upload/603e089ce2ef-20260320.png)  
![](https://static.zenn.studio/user-upload/fd4a2b4dd144-20260320.png)  
![](https://static.zenn.studio/user-upload/19df3f6e9d84-20260320.png)  
![](https://static.zenn.studio/user-upload/7592ae5775d8-20260320.png)

Gemiclawとのやりとり

```
aataka — 2026/03/17 19:06
スキルを更新したので確認して

gemiclaw
アプリ
 — 2026/03/17 19:06
承知しました。スキルの確認ですね。
/app/config/skills/ 配下に新しいスキルディレクトリが追加されているか確認します。

aataka — 2026/03/17 19:06
何が更新されている？

gemiclaw
アプリ
 — 2026/03/17 19:06
現在のディレクトリ構成を確認しましたが、直近で追加や変更されたと思われる新しいスキルディレクトリは見当たりませんでした。

念のため、もし何か特定のスキルが更新されたという認識であれば、どのディレクトリ名か教えていただけますか？それとも、既存スキルの内容（中身のスクリプトなど）を更新されたのでしょうか？

aataka — 2026/03/17 19:08
スキルを更新したので確認して

gemiclaw
アプリ
 — 2026/03/17 19:08
スキルのディレクトリ構成を確認しましたが、現在 /app/config/skills/ 配下にあるのは以下の通りです。

check_aws_logs
get_location
get_mapbox_map
memory_search
run_python
run_python_code
send_image_to_discord
web_search

もし今回新しく追加・更新されたスキルがある場合、上記とは別の場所に配置されているか、あるいはディレクトリ名が異なる可能性があります。どのディレクトリ（またはどのスキル）を確認すべきか、念のため教えていただけますか？🐾

aataka — 2026/03/17 19:09
check_aws_logs スキルが認識されているのを確認しました。では、そのスキルを使って admin-update-handler のAWSログを取得し、直近の動作状況を報告してください。

gemiclaw
アプリ
 — 2026/03/17 19:09
申し訳ありません、check_aws_logs を使用して admin-update-handler のログを取得しようとしましたが、エラーが発生しました。

エラー内容: ResourceNotFoundException
指定された名前のロググループ（/aws/lambda/admin-update-handler など）が見つかりません。

この関数名で正しいか、あるいはロググループ名が別の形式になっていないかご確認いただけますでしょうか？もし特定のロググループ名を指定する必要があれば、併せてお知らせください。🐾

aataka — 2026/03/17 19:10
Lambda を一度実行してログを生成させました。もう一度 check_aws_logs で admin-update-handler の状況を確認してください。

gemiclaw
アプリ
 — 2026/03/17 19:10
ご指示通り再度 admin-update-handler のログを確認いたしましたが、やはり同じ ResourceNotFoundException が発生し、ロググループが見つかりません。

Lambda の実行によってログは生成されたとのことですので、以下の可能性が考えられます。

ロググループ名の違い: Lambda 関数名 admin-update-handler と実際のロググループ名（例: /aws/lambda/関数名 以外の命名規則）が異なっている。
リージョンまたは設定の不一致: Lambda が実行された環境と、このツールが参照している LocalStack の環境が一致していない。

正確なロググループ名を特定するため、まずは現在システム上に存在するロググループの一覧を確認したいと思います。よろしいでしょうか？🐾

aataka — 2026/03/17 19:11
調査用の新スキル list_aws_logs を追加して再起動しました。まずはこのスキルを使って、今 LocalStack 上に存在するすべてのロググループを表示してください。その中から admin-update-handler に対応する正しいロググループ名を見つけ、再度内容の確認をお願いします。

gemiclaw
アプリ
 — 2026/03/17 19:12
申し訳ありません。list_aws_logs で確認したところ、ロググループの一覧には /aws/lambda/admin-update-handler が確かに存在していました。

しかし、その名前を指定して check_aws_logs を実行すると、依然として ResourceNotFoundException が発生します。

推測ですが、ツール側の実装で「/aws/lambda/」というプレフィックスが自動付与されているか、あるいはロググループ名が微妙に異なる（例えば、CloudWatch側で実際に作成されているリソース名が微妙に異なるなど）可能性があります。

念のため、他のロググループについても同様のエラーが出るか、あるいは他のロググループ名なら正しく取得できるかテストしてもよろしいでしょうか？あるいは、ログ取得の際の「関数名」の指定方法について、何か制約があるかご存知でしたら教えていただけますか。🐾

aataka — 2026/03/17 19:12
スキルの run.sh を修正し、ロググループ名の指定を柔軟にしました。今度は /aws/lambda/admin-update-handler というフルネームを直接 check_aws_logs スキルに渡して、もう一度ログの取得を試みてください。

gemiclaw
アプリ
 — 2026/03/17 19:12
申し訳ありません。ご指示通りフルネーム /aws/lambda/admin-update-handler を指定して実行しましたが、やはり ResourceNotFoundException が発生します。

しかし、list_aws_logs の結果には確かに /aws/lambda/admin-update-handler が存在しています。

これまでの状況を整理すると、以下の技術的な懸念があります：

ツールの呼び出し先: check_aws_logs ツール自体が、内部で別のプレフィックスを付与している、あるいは別環境を参照しにいっている可能性があります。
APIの差異: ロググループは存在しているのに「取得できない」という事象は、指定したロググループのストリームが存在しない、あるいはAPIが参照しているリージョンやアカウントIDが微妙に食い違っている可能性があります。

この問題の切り分けのため、他のロググループである /aws/lambda/auth-handler など、別の関数でも同様にエラーが出るか試してもよろしいでしょうか？あるいは、check_aws_logs ツールの run.sh の中身を一度拝見させていただき、どのようなコマンドが実行されているか確認させていただくことは可能でしょうか？🐾

aataka — 2026/03/17 19:15
君の推測は正しい。check_aws_logs の run.sh を確認したところ、以前は名前の頭に /aws/lambda/ を強制付与していたため、フルネームで渡すと二重になってエラーになっていた。

いま、スクリプトを修正して、フルネームでも関数名だけでも受け取れるようにしたよ。

現在の run.sh の中身：

Bash
if [[ $INPUT_NAME == /aws/lambda/* ]]; then
    LOG_GROUP_NAME=$INPUT_NAME
else
    LOG_GROUP_NAME="/aws/lambda/${INPUT_NAME}"
fi
aws --endpoint-url=http://host.docker.internal:4566/ logs tail ${LOG_GROUP_NAME}
これでもう一度、admin-update-handler（またはフルネーム）でログが取れるか試してみて。

gemiclaw
アプリ
 — 2026/03/17 19:15
ご指示いただいた内容を深く検証した結果、原因が判明しました。

まず、手動でテスト実行したところ、修正いただいた run.sh のロジックは正しく動作しており、ログの取得自体は成功しました。しかし、check_aws_logs ツールを介して実行するとエラーが出るのは、ツール定義における parameters の受け渡しと、シェルスクリプト側での $1 引数の参照がうまく噛み合っていないためです。

現状のツールの呼び出し方では、SKILL_ARGS 環境変数に {"function_name": "..."} という形式でJSONが渡されていますが、スクリプト側ではそれをパースせずに $1 をそのまま使おうとしており、結果として空の値を参照しているか、意図しない挙動になっているようです。

対処案
このツールを正常に動作させるため、check_aws_logs/run.sh を以下のように修正し、JSONから引数をパースするように変更することを提案します。

#!/bin/bash
# SKILL_ARGSからJSONをパースして function_name を取得
INPUT_NAME=$(python3 -c "import sys,json,os; print(json.loads(os.environ['SKILL_ARGS'])['function_name'])")

# (以下、プレフィックス判定とAWSコマンド実行ロジックはそのまま)

この修正で、Discordからの呼び出し時にも正しく引数が渡り、ログを取得できるようになります。この修正を行ってよろしいでしょうか？🐾

aataka — 2026/03/17 19:16
素晴らしいデバッグだ！君の提案通り SKILL_ARGS をパースするように run.sh を修正したよ。

君が提案してくれたパース処理：
INPUT_NAME=$(python3 -c "import sys,json,os; print(json.loads(os.environ['SKILL_ARGS'])['function_name'])")

これを組み込んだので、もう一度 admin-update-handler のログ取得に挑戦してみて。今度こそ成功するはずだ！

gemiclaw
アプリ
 — 2026/03/17 19:16
修正いただいたスクリプトのおかげで、ついに admin-update-handler のログを正常に取得できました！

取得したログの内容は以下の通りです：

2026-03-17T10:09:57 START RequestId: ccefc143-7e11-4371-8472-5e8eac510bbd Version: $LATEST
2026-03-17T10:09:57 END RequestId: ccefc143-7e11-4371-8472-5e8eac510bbd
2026-03-17T10:09:57 REPORT RequestId: ccefc143-7e11-4371-8472-5e8eac510bbd    Duration: 0.97 ms    Billed Duration: 1 ms    Memory Size: 128 MB    Max Memory Used: 128 MB

リクエストは正常に処理されているようです。デバッグにご協力いただきありがとうございました！他に何か確認することや、お手伝いできることはありますか？🐾

aataka — 2026/03/17 19:16
それ以外にどんなawsのログが確認できるかを試してその内容をここにリストで出して

gemiclaw
アプリ
 — 2026/03/17 19:17
ご指示ありがとうございます。確認したところ、LocalStack 上には現在以下の Lambda ロググループが存在しています。

/aws/lambda/admin-list-handler
/aws/lambda/admin-update-handler
/aws/lambda/auth-handler
/aws/lambda/photo-handler

各関数のログ取得を試みましたが、現在ログが記録されているのは先ほど確認した admin-update-handler のみで、その他の関数については直近の実行履歴（ログ）が空の状態でした。

もしこれらの関数を動作させる必要がある場合は、トリガーとなる処理を実行して再度状況を確認いたしますので、お気軽にお申し付けください。🐾

aataka — 2026/03/17 19:20
今新しくログが生成されたかも、確認して

gemiclaw
アプリ
 — 2026/03/17 19:20
LocalStack 上の AWS ロググループを改めて全件調査しました。現在、以下のロググループが存在し、直近で以下のログが生成されていました。

ログ生成状況
/aws/lambda/admin-list-handler
2026-03-17 10:18:56 に実行ログあり（正常終了）。
/aws/lambda/auth-handler
2026-03-17 10:18:49 および 10:18:55 に実行ログあり（正常終了）。
/aws/lambda/admin-update-handler
現在、直近の新しいログはありません（以前確認した内容が最後です）。
/aws/lambda/photo-handler
現在、ログはありません。

admin-update-handler に動きがないようです。もし特定の処理を実行してログを出したい場合は、トリガーをかけていただければすぐに確認します。🐾

aataka — 2026/03/17 19:20
dynamodbのテーブルを出して

gemiclaw
アプリ
 — 2026/03/17 19:21
LocalStack 上に存在する DynamoDB テーブルを確認しました。現在は以下の2つのテーブルが作成されています。

AuthUser
PhotoMetadata

これらについて詳細を確認したい場合や、中身のデータを操作する必要があればおっしゃってください。🐾

aataka — 2026/03/17 19:23
管理者がログインしたときに出力される表を出して

gemiclaw
アプリ
 — 2026/03/17 19:23
申し訳ありません。DynamoDB の調査において技術的な問題が発生しました。

直接ツールを使用してテーブル一覧を取得しようとしましたが、環境内のライブラリの依存関係（urllib3）で競合が発生し、DynamoDB へのクエリが正常に実行できない状態です。先ほどまでは Lambda のログ取得ツール (check_aws_logs) で正常に結果を得られていたため、おそらく今回の調査に使おうとした DynamoDB 操作用の Python コードが、ローカル環境のライブラリ設定と干渉しているようです。

原因を正確に特定し、別の方法で DynamoDB テーブルの内容を確認できるよう修正しますので、少々お時間をいただけますでしょうか。まずは環境の整合性を整えてから再調査いたします。🐾
aataka — 2026/03/17 19:25
Pythonのライブラリ競合で手間取っているようだね。代わりに AWS CLI を使った check_db_table スキルを追加したよ。

これを使って PhotoMetadata テーブルをスキャンし、管理者がログインした時に表示される『提出写真ステータス一覧』の内容をリスト形式で出力して。
gemiclaw
アプリ
 — 2026/03/17 19:25
ご指示いただいた check_db_table スキルを実行しましたが、依然としてライブラリの urllib3 に関する依存関係のエラー（ImportError: cannot import name 'DEFAULT_CIPHERS'）が発生してしまいました。

先ほど推測した通り、/app/config/pip_packages/ にインストールされている urllib3 が、システム標準の awscli が期待するものとバージョン不整合を起こしているようです。

この問題を根本的に解決するため、以下の手順を提案します：

ライブラリの隔離確認: 現在 /app/config/pip_packages/ にある urllib3 を一時的に退避させ、システム環境の awscli が標準ライブラリで動作できるか確認する。
代替手段の検討: もし awscli コマンドがこの環境でうまく使えない場合、Pythonの boto3 を用いたスクリプトを、環境パスをクリーンに保った状態で作成し、そちらでDynamoDBをスキャンする。

まずは、どのようなライブラリが pip_packages にあるかを確認し、状況を整理します。進めてもよろしいでしょうか？🐾

aataka — 2026/03/17 19:25
君の言う通り、pip_packages 内のライブラリが干渉していたよ。

そこで、check_db_table スキルの実行時に一時的に PYTHONPATH をクリアするように run.sh を修正した。

これで外部ライブラリの干渉を受けずにシステム標準の awscli が動くはずだ。もう一度 PhotoMetadata テーブルのスキャンを試してみて。

gemiclaw
アプリ
 — 2026/03/17 19:25
PYTHONPATH をクリアしたことで、ライブラリの干渉なく正常に PhotoMetadata テーブルの中身を取得できました！

現在の提出写真ステータス一覧は以下の通りです。

| PhotoID | UserID | Status |
| :--- | :--- | :--- |
| uploads/tanaka/1773733711.jpg | tanaka | 未対応 |
| uploads/tanaka/1773734225.jpg | tanaka | 対応済み |
| uploads/tanaka/1773735348.jpg | tanaka | 対応済み |

tanaka さんの提出した写真のうち、1件がまだ「未対応」の状態ですね。
他に確認したい項目や、お手伝いできることはありますか？🐾
```

---

## 6. オンプレ環境との違い

オンプレ環境とクラウド環境の違いについて  
今回LocalStackの疑似aws環境でシステムを構築しましたが、オンプレ環境とは**比べ物にならない**ほどに手順の簡略化と高可用性を感じました。

そこで、geminiに過去のインフラ基盤運用で直面してきた「目に見えない運用・テストのコスト」をどう解決するかを軸に、システム構成を以下の4つのフェーズに分けて比較してもらいました。

今回は、ロードバランサ等を用いない最小構成の「簡易写真管理システム（非同期でのDB登録機能付き）」を前提として、各アーキテクチャの**構築・機能試験・運用のコスト**を評価しています。  
（そりゃあ、オンプレじゃなくてクラウドにしたくなる気持ちがわかる）

#### アーキテクチャ別：構築・テスト・運用フェーズの工数詳細比較

| 比較項目 | ① オンプレミス (物理ベアメタル) | ② オンプレミス (仮想化/VMware等) | ③ AWS サーバ設計 (EC2) | ④ サーバレス設計 (本構成) |
| --- | --- | --- | --- | --- |
| **ハードウェア調達・設定** | **数ヶ月** (機器選定、発注、ラッキング、電源・結線、初期設定) | **ホスト単位で数ヶ月** (VM追加自体は数分〜数十分だが、物理リソースの上限に縛られる) | **不要** (数分でインスタンス起動) | **完全不要** |
| **OS・ネットワーク構築** | **数日** (OSインストール、物理スイッチのVLAN・ルーティング設計) | **数時間** (仮想スイッチ設定、OSクローン作成) | **数十分** (VPC、サブネット、SG設定等) | **不要** (IAMロールとAPI Gatewayのパス定義のみ) |
| **ミドルウェア・ランタイム導入** | **必須** (Webサーバ、言語ランタイム等の手動インストールと初期設定) | **必須** (テンプレート化は可能だが定期的なアップデート作業は残る) | **必須** (AMI化の手間や、起動スクリプトの管理が必要) | **不要** (Lambdaの `Runtime` 指定のみで環境が即座に用意される) |
| **非同期処理の実装** *(※画像保存時のDB更新)* | **高難度** (inotify等でディレクトリ監視デーモンを自作し、OSに常駐化) | **高難度** (物理と同等。OS依存のスクリプト管理・プロセス死活監視が発生) | **高難度** (オンプレと同等、もしくはS3のポーリング処理を自前実装し常駐化) | **超低難度** (S3の `ObjectCreated` イベント通知を設定するのみ。OS管理不要) |
| **テスト環境の用意（コスト）** | **莫大** (本番と同スペックの物理サーバをもう1セット購入・維持) | **大** (リソースを圧迫し、ハイパーバイザのライセンス費用等も影響) | **中** (EC2やRDSを複製できるが、**起動している間は常に時間課金が発生**) | **極小 (実質無料)** (LocalStackによりローカルで完全再現可能。本番AWSでも待機コストゼロ) |
| **インフラの冪等性・再構築** *(作り直しの容易さ)* | **困難** (一度OSを汚すとクリーンな状態に戻すのが極めて重労働) | **やや手間** (スナップショットで戻せるが、容量を食い、世代管理が煩雑) | **手間** (EC2の破棄・再作成に数分。Terraformを使ってもOS内の状態担保は別課題) | **一瞬・確実** (`terraform destroy & apply` で数秒〜数十秒で更地から完全復元) |
| **障害復旧・プロセス監視** | **泥臭い運用** (ハード故障対応、プロセスダウン時の再起動スクリプトや監視ツール必須) | **インフラ層はHA化** (vMotion等でハード障害は吸収できるが、ゲストOS内のプロセス監視は必須) | **インフラ層は自動化** (Auto Recovery等があるが、OS内のプロセス監視と復旧機構は自前で必須) | **完全マネージド** (プロセスの実行基盤はAWSが担保。落ちたとしてもリトライ機構が標準装備) |

## 7. 成果と今後の展望

今回の検証でIaCやAIエージェントなどのクラウドエンジニアとして必要な技術がどんなものかを経験しました。今後の展望として

**AIエージェントの自律化**  
現状のGemiclawは、リソースの確認やログ取得といった「Read（読み取り）」操作にとどまっています。次のステップとして、Terraformの実行権限やAWS CLIによる「Write（書き込み）」権限を安全な範囲で付与し、システム障害や設定のドリフト（ズレ）を検知したら、AI自らが terraform apply を実行してインフラをあるべき姿に自動修復する「自律型の運用エージェント」へと進化させたいと考えています。

**様々なAWSサービスに挑戦**  
今回のシステム（API Gateway + Lambda + S3 + DynamoDB）はサーバーレスの基本形ですが、今後はさらに実践的なアーキテクチャへと拡張していきます。例えば、S3へのアップロードイベントをAmazon SQSやSNSで受け取って非同期処理の堅牢性を高めたり、Amazon CloudFrontを前段に配置して配信を最適化するなど、スケーラビリティや可用性を意識した構成変更を検証環境のLocalStack、本番環境のaws上で迅速にスクラップ＆ビルドするような検証をしていきたいとお思います。

**マルチクラウド展開**  
インフラをTerraformでコード化（IaC）した最大のメリットを活かし、現在のAWS構成をGoogle Cloud環境へと移植する検証も行います。AWSの各種サービスに相当するGCPサービス（Cloud Functions、Cloud Storage、Firestoreなど）へコードを書き換え、Google Cloudのエミュレータ等で再現することで、特定のクラウドベンダーに依存しない柔軟で俯瞰的なインフラ設計の視点を養っていきます。(その前に他のクラウドがawsとどう違うのかの確認もしなきゃ)

最後までに読んでいただきありがとうございました!!!
