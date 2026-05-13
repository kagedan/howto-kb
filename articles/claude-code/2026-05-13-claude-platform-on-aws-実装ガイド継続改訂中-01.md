---
id: "2026-05-13-claude-platform-on-aws-実装ガイド継続改訂中-01"
title: "Claude Platform on AWS 実装ガイド(継続改訂中)"
url: "https://qiita.com/j-dai/items/d228234f043972e80103"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "prompt-engineering", "API", "AI-agent", "Python", "qiita"]
date_published: "2026-05-13"
date_collected: "2026-05-13"
summary_by: "auto-rss"
query: ""
---

# Claude Platform on AWS 実装ガイド（運用・セキュリティ視点）

**想定読者：** クラウド／インフラ管理者、IT セキュリティ担当、AI 導入プロジェクトリーダー  
**スコープ：** Claude Platform on AWS  
**文書バージョン：** v0.3（2026 年 5 月時点。運用前に必ず公式ドキュメントで最終確認してください）

---

## はじめに

Claude Platform on AWS は、Anthropic の Claude API と同等の体験を、**AWS アカウントと IAM を入口**に利用する統合です。課金や契約の入口が AWS 側に寄る一方、**推論そのものは Anthropic が運用するインフラ上で実行**されます。データレジデンシーや監査要件が厳しい場合は、要件に合わせて Amazon Bedrock 等も比較検討してください。

**参照ドキュメント**

- [Claude Platform on AWS ユーザーガイド（AWS）](https://docs.aws.amazon.com/claude-platform/latest/userguide/welcome.html)
- [IAM アクションとルート対応（AWS）](https://docs.aws.amazon.com/claude-platform/latest/userguide/iam-actions.html)
- [監視・ログ（AWS）](https://docs.aws.amazon.com/claude-platform/latest/userguide/monitoring.html)
- [Prerequisites（AWS）](https://docs.aws.amazon.com/claude-platform/latest/userguide/prerequisites.html)
- [Claude API ドキュメント（Anthropic）](https://platform.claude.com/docs)

---

## 目次

1. [Claude Platform on AWS とは](#what)
2. [前提条件](#prereq)
3. [有効化と初期セットアップ](#setup)
4. [管理者設定（IAM・キー・コンソール）](#admin)
5. [テストユーザーと機能検証](#test)
6. [IAM とアクセスの扱い（Identity Center は任意）](#iam-access)
7. [Appendix A：料金・コスト](#appendix-a)
8. [Appendix B：監査ログ・監視](#appendix-b)
9. [Appendix C：トラブルシューティング](#appendix-c)
10. [改訂履歴](#changelog)

---

## Claude Platform on AWS とは {#what}

Claude Platform on AWS は、AWS アカウント経由で Anthropic の Claude プラットフォーム（Messages API 等）を利用する形態です。Bedrock 上のマネージドモデル提供とは**別ライン**です。

| 比較項目 | Claude Platform on AWS | Amazon Bedrock |
| --- | --- | --- |
| 推論スタックの運用 | Anthropic | AWS |
| API 形式 | Anthropic Messages API（`/v1/messages` 等） | Converse / InvokeModel 等 |
| 新機能・新モデルの追従 | 一次 API と同日リリースを狙う設計 | AWS 側の提供タイミングに依存 |
| Agent Skills 等のプラットフォーム機能 | 利用可能なものがある（ベータ含む） | Bedrock の機能セットに依存 |
| `anthropic-beta` ヘッダー | 一次 API と同様のベータ運用が可能 | モデル／機能により異なる |
| 認証 | AWS IAM（SigV4）とワークスペース API キー | 主に IAM（SigV4）等 |
| 課金の入口 | AWS 請求（表示粒度は公式の最新情報を参照） | AWS ネイティブ課金 |
| データ処理の分担 | AWS と Anthropic がそれぞれデータ処理者として関与（契約書に従う） | AWS 側の枠組みに寄せやすい |
| コンソール | Claude Console（`platform.claude.com`） | Bedrock コンソール |

**重要：** PrivateLink は「VPC から AWS ゲートウェイまで」をプライベートにしやすくしますが、**推論は Anthropic 側インフラへ到達**します。FedRAMP High / IL4 / IL5 / HIPAA 等の要件がある場合は、Bedrock を検討してください。

---

## 前提条件 {#prereq}

### AWS アカウント要件

| 要件 | 内容 |
| --- | --- |
| AWS アカウント | 有効なアカウント。初期セットアップは管理者相当の権限を推奨 |
| Marketplace | サブスクリプション承認など、契約手続きに必要な権限 |
| 支払い方法 | 請求が有効な支払設定 |
| リージョン | **利用可能リージョンは拡張され得ます**。[Prerequisites](https://docs.aws.amazon.com/claude-platform/latest/userguide/prerequisites.html) およびコンソール表示を正とし、**オプトインリージョン**はアカウントのオプトイン設定が前提です |
| **IAM Identity Center** | **必須ではありません**。単一の AWS アカウント（Organizations のメンバーアカウントでも可）で、**IAM ユーザー／IAM ロールのみ**の構成で運用できます |

### IAM 権限（セットアップ担当者向けの例）

サブスク操作と OWIF 有効化、サービス API への道を開く、という観点での**例示**です。実際の最小権限は組織方針に合わせて絞り込んでください。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "aws-marketplace:Subscribe",
        "aws-marketplace:Unsubscribe",
        "aws-marketplace:ViewSubscriptions",
        "iam:EnableOutboundWebIdentityFederation",
        "iam:GetOutboundWebIdentityFederationInfo",
        "aws-external-anthropic:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### AWS マネージドポリシー（代表）

| マネージドポリシー | 用途の目安 |
| --- | --- |
| `AnthropicFullAccess` | 管理用途（広い権限。運用ポリシーに合わせて限定推奨） |
| `AnthropicReadOnlyAccess` | 監査・閲覧中心 |
| `AnthropicInferenceAccess(現時点確認できない)` | 推論・バッチ等のデータ面 |
| `AnthropicLimitedAccess` | 推論に加え Files / Skills / Managed Agents 周辺のデータ面操作を広く許可。`AssumeConsole` は developer 能力に限定される等、Limited でも広いので用途を確認の上で付与 |

### ソフトウェア要件

| ソフトウェア | バージョン目安 | 用途 |
| --- | --- | --- |
| AWS CLI | v2 系 | OWIF 確認、自動化 |
| Python / Node 等 | 各 SDK の推奨版 | クライアント実装 |
| Git | 任意 | サンプル取得 |

```bash
aws --version
```

### ネットワーク

| 項目 | 要件 |
| --- | --- |
| エンドポイント | `https://aws-external-anthropic.{region}.api.aws` への **HTTPS（443）** |
| PrivateLink | 利用する場合は VPC エンドポイント設計。ただし**推論パス全体のデータ境界**とは別問題 |
| TLS | TLS 1.2 以上 |

### Anthropic 側の契約・ポリシー

商用利用規約、Usage Policy、データ取り扱い（DPA 等）への同意が必要です。エンタープライズ契約やプライベートオファーがある場合は、**割引の遡及が効かない**ケースがあるため、サインアップ前に営業／法務と整合させてください。

### 前提条件チェックリスト

```
□ 有効な AWS アカウント（単体または Organizations メンバーいずれも可）
□ Marketplace 手続きに必要な IAM 権限
□ 請求設定が有効
□ 利用リージョン方針の決定（DR / レイテンシ / データレジデンシ）
□ AWS CLI v2 の利用準備
□ Anthropic のデータ関連ポリシーの確認
□ プライベートオファーの有無確認
□ ネットワーク（インターネット／PrivateLink）方針
□ OWIF（Outbound Web Identity Federation）有効化方針
□ （任意）IAM Identity Center を使う場合は、利用方針と Permission Set を決定済み
```

---

## 有効化と初期セットアップ {#setup}

### 全体フロー

```
1. AWS コンソールでサインアップ（Marketplace 連携）
2. メール経由で Anthropic 組織の初期設定
3. ワークスペース ID の確認（リージョンにバインド）
4. Outbound Web Identity Federation（OWIF）をアカウントで有効化
5. Claude Console にサインインできることを確認
6. 環境変数と SDK を用意
7. 最初の Messages API 疎通
```

### Step 1：AWS コンソールでサインアップ

1. [AWS マネジメントコンソール](https://console.aws.amazon.com) にサインインする。  
2. 検索から **Claude Platform on AWS** を開く。  
3. **Sign up** を進め、表示される利用規約（Anthropic / AWS）に同意する。  
4. **Continue** 後、Marketplace 処理で**数分待つ**（バナー表示は正常なことが多い）。  
5. プライベートオファーがある場合は、指示に従い **Marketplace で承認**する。  
6. 完了後、`platform.claude.com/partner-signup` などへ誘導されることがあります。

### Step 2：Anthropic 組織のセットアップ

1. 画面案内に従い、組織オーナーのメールを入力して **Get started**。  
2. メールのセットアップリンクから続行。  
3. 「Signed in as a different account」と出た場合は **Log out and continue** 等の指示に従う。  
4. 組織情報を入力し **Complete setup**。  
5. 完了後以下画面を確認できる。
 ![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1348505/3e3912b1-790b-4b5b-aee8-5a4fc087bcec.png)


### Step 3：ワークスペース ID の確認

**各リージョンで、サインアップ時にデフォルトのワークスペースが作成されます**（[Prerequisites](https://docs.aws.amazon.com/claude-platform/latest/userguide/prerequisites.html)）。追加のワークスペース作成や改名・アーカイブは、ワークスペース API と IAM アクションで管理します（[Workspaces](https://docs.aws.amazon.com/claude-platform/latest/userguide/workspaces.html)）。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1348505/0095a30f-d936-45b6-8e7d-4de7935e7bed.png)
※ap-northeast-1含むいろいろリージョンに作れますが、現時点データレジデンシーがglobal(確認中)とusのみ。

AWS コンソールの **Workspaces**、または Claude Console、List/Get API で確認し、**安全な秘密管理**に保存してください。

### Step 4：Outbound Web Identity Federation（OWIF）

**アカウント単位で一度だけ**有効化します（[Prerequisites](https://docs.aws.amazon.com/claude-platform/latest/userguide/prerequisites.html)）。

```bash
aws iam enable-outbound-web-identity-federation

# 既に有効な場合のエラーは無視してよいことが多い
# [ERROR] (FeatureEnabled) ... already enabled

aws iam get-outbound-web-identity-federation-info
```

無効のままだと、典型的には次のメッセージで失敗します。

> `"Outbound web identity federation is disabled for your account"`

### Step 5：Claude Console のサインイン確認

1. `aws-external-anthropic:AssumeConsole` を許可した IAM プリンシパルで AWS に入る。  
2. サービスページの **Open Claude Console** を押す。  
3. AWS 側が JWT を発行し、`platform.claude.com` にフェデレーションされる。  
4. 初回は業務メールの入力など JIT ユーザー作成フローがあることがあります。  
5. 左下に **Account managed by AWS** と出ることを確認（表示文言は変更され得ます）。

`AssumeConsole` で得られる Claude Console セッションは**最長 12 時間**などの特性があります（[IAM actions](https://docs.aws.amazon.com/claude-platform/latest/userguide/iam-actions.html) の注意書き参照）。

### Step 6：環境変数

```bash
export ANTHROPIC_AWS_WORKSPACE_ID='wrkspc_01AbCdEf23GhIj'
export AWS_REGION='ap-northeast-1'

# API キー利用時（AWS コンソールで発行したワークスペースキー）
export ANTHROPIC_AWS_API_KEY='<your-workspace-api-key>'

# エンドポイントを上書きする場合のみ
# export ANTHROPIC_AWS_BASE_URL='https://aws-external-anthropic.ap-northeast-1.api.aws'
```

SigV4 利用時は、通常どおり `AWS_ACCESS_KEY_ID` / ロールチェーン / SSO プロファイルを構成します。

### Step 7：SDK と疎通テスト

```bash
pip install "anthropic[aws]"
```

```python
# test_connection.py
from anthropic import AnthropicAWS

client = AnthropicAWS()

raw = client.messages.with_raw_response.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    messages=[
        {"role": "user", "content": "Claude Platform on AWS の疎通テストです。"},
    ],
)

message = raw.parse()
print("OK:", message.content[0].text)
print("AWS Request ID:", raw.headers.get("x-amzn-requestid"))
print("Anthropic Request ID:", raw.headers.get("request-id"))
```

```bash
python test_connection.py
```

**モデル ID**（`claude-sonnet-4-6` 等）は、ListModels または Console で**利用可能な ID を都度確認**してください。

---

## 管理者設定（IAM・キー・コンソール） {#admin}

### IAM ロール設計の例

#### 管理者（例：広い権限。本番では分割推奨）

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ClaudePlatformAdmin",
      "Effect": "Allow",
      "Action": "aws-external-anthropic:*",
      "Resource": "*"
    }
  ]
}
```

#### 推論中心（ワークスペース ARN でスコープ）

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ClaudeInference",
      "Effect": "Allow",
      "Action": [
        "aws-external-anthropic:CreateInference",
        "aws-external-anthropic:CountTokens",
        "aws-external-anthropic:GetModel",
        "aws-external-anthropic:ListModels",
        "aws-external-anthropic:GetWorkspace"
      ],
      "Resource": "arn:aws:aws-external-anthropic:*:*:workspace/*"
    },
    {
      "Sid": "ListWorkspaces",
      "Effect": "Allow",
      "Action": "aws-external-anthropic:ListWorkspaces",
      "Resource": "*"
    }
  ]
}
```

#### 特定ワークスペースのみ許可

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "aws-external-anthropic:CreateInference",
        "aws-external-anthropic:GetWorkspace"
      ],
      "Resource": "arn:aws:aws-external-anthropic:ap-northeast-1:123456789012:workspace/wrkspc_01AbCdEf23GhIj"
    }
  ]
}
```

ARN 形式：

```
arn:aws:aws-external-anthropic:{region}:{account-id}:workspace/{workspace-id}
```

#### バッチ推論を拒否する例

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "aws-external-anthropic:CreateInference",
        "aws-external-anthropic:CountTokens",
        "aws-external-anthropic:GetModel",
        "aws-external-anthropic:ListModels",
        "aws-external-anthropic:GetWorkspace"
      ],
      "Resource": "arn:aws:aws-external-anthropic:*:*:workspace/*"
    },
    {
      "Effect": "Allow",
      "Action": "aws-external-anthropic:ListWorkspaces",
      "Resource": "*"
    },
    {
      "Effect": "Deny",
      "Action": [
        "aws-external-anthropic:CreateBatchInference",
        "aws-external-anthropic:GetBatchInference",
        "aws-external-anthropic:ListBatchInferences"
      ],
      "Resource": "*"
    }
  ]
}
```

### API キー管理

1. AWS コンソールの Claude Platform on AWS → **API keys**。  
2. **Generate a key**。名前は `{環境}-{チーム}-{用途}-{日付}` などで統一。  
3. **一度しか表示されない**ため、Secrets Manager 等へ即保管。

**注意：**

- リポジトリに直書きしない。  
- Claude Console 上で作った通常の API キーと、**ワークスペース API キーは別物**です。

#### 短期トークン（任意）

長寿命キーを配らずに済ませたい場合のパターンです。パッケージ名・手順は [AWS のユーザーガイド](https://docs.aws.amazon.com/claude-platform/latest/userguide/welcome.html) および関連リリース情報を参照してください。

### Claude Console の管理機能（整理）

| 領域 | 内容 | 備考 |
| --- | --- | --- |
| Usage / Cost / Limits | 利用量・コスト・レート上限の可視化 | フェデレーション後の Console |
| Workspaces / Files / Skills / Batches / Agents | 各機能の操作 | データ面は多くが **Data イベント**（Appendix B） |
| API keys | ワークスペース API キー | **AWS コンソール** |
| メンバー／ユーザープロフィール | 人の単位の管理 | Claude 側のユーザープロフィール API／Console。AWS IAM とは別レイヤー |
| 課金の全体像 | AWS 請求・CUR | AWS 側のビューで補完 |

Console ロール（Admin / Developer）は、契約形態に応じて Anthropic 側で割り当てられることがあります。

### データレジデンシー（`inference_geo`）

`inference_geo` は **`us`（米国内）** と **`global`（省略時のデフォルト）** などをリクエスト単位で指定します。**1.1 倍の価格倍率が US に適用**される旨が公式に記載されています（[Data residency](https://docs.aws.amazon.com/claude-platform/latest/userguide/data-residency.html)）。

**対応モデル範囲**も公式に制限があります（例：**Claude Opus 4.6 / Sonnet 4.6 以降**でサポート、4.5 系に付けると 400 等）。利用前にモデル一覧を確認してください。

### レートリミット

Tier 1 から開始される説明は参考情報として残しつつ、**実数値と引き上げ手続きは Console の Limits と Anthropic／AWS の案内を正**としてください。Bedrock とは別プロダクトのため、**自動ティア昇格の有無も別**です。

### ゼロデータリテンション（ZDR）

デフォルト無効でオプトイン、有効化は Anthropic 側の手続き、という整理で問題ありません。契約書と突合してください。

### AWS PrivateLink（任意）

```bash
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxxxxxxx \
  --service-name com.amazonaws.ap-northeast-1.aws-external-anthropic \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-xxxxxxxx \
  --security-group-ids sg-xxxxxxxx \
  --private-dns-enabled
```

`service-name` と **利用リージョン**は公式の最新表記に合わせてください。

---

## テストユーザーと機能検証 {#test}

### テスト構成の例

```
対象 AWS アカウント 1 つ（スタンドアロンまたは Organizations メンバー）
  └ テスト用 IAM ユーザー または IAM ロール
       └ AnthropicInferenceAccess 等

テスト用ワークスペース API キー（任意）
  └ 命名: test-{チーム}-{日付}

ワークスペース ID / リージョン
```

### IAM ユーザー作成の例（Identity Center なし）

```bash
aws iam create-user --user-name test-claude-user

aws iam attach-user-policy \
  --user-name test-claude-user \
  --policy-arn arn:aws:iam::aws:policy/AnthropicInferenceAccess

aws iam create-access-key --user-name test-claude-user
```

発行したアクセスキーは `aws configure --profile test-claude` 等に保存し、**ローテーションと漏えい対策**を必須化してください。

### 機能テストの要点

- **基本メッセージ**、**マルチターン**、**system**、**stream**、**prompt cache**、**Files**、**tool use**、**inference_geo** など、段階的に切り分けます。  
- Files API や beta ヘッダは**日付付き beta 名**が変わり得るため、[Anthropic のドキュメント](https://platform.claude.com/docs) を確認してください。

#### マルチターン（推奨パターン）

```python
from anthropic import AnthropicAWS

client = AnthropicAWS()
model = "claude-sonnet-4-6"

m1 = client.messages.create(
    model=model,
    max_tokens=256,
    messages=[{"role": "user", "content": "私のニックネームは「テスト太郎」です。覚えてください。"}],
)
a1 = m1.content[0].text

m2 = client.messages.create(
    model=model,
    max_tokens=256,
    messages=[
        {"role": "user", "content": "私のニックネームは「テスト太郎」です。覚えてください。"},
        {"role": "assistant", "content": a1},
        {"role": "user", "content": "私のニックネームは何でしたか？"},
    ],
)
print(m2.content[0].text)
```

### テスト記録テンプレート

| ID | 内容 | 日時 | 結果 | 備考 |
| --- | --- | --- | --- | --- |
| T1 | 基本メッセージ | | Pass / Fail | |
| T2 | マルチターン | | | |
| T3 | system | | | |
| T4 | stream | | | |
| T5 | prompt cache | | | |
| T6 | Files API | | | beta 名要確認 |
| T7 | tool use | | | |
| T8 | inference_geo=us | | | 対応モデルのみ |

---

## IAM とアクセスの扱い（Identity Center は任意） {#iam-access}

### 階層イメージ

```
AWS アカウント（1 つで完結してよい）
 └ Claude Platform on AWS（Anthropic 組織）
    └ ワークスペース（リージョン単位でバインド）
       └ IAM ユーザー／IAM ロール（API アクセス境界）
          └ （任意）IAM Identity Center 経由の Permission Set 割当
          └ アプリごとのシークレット（API キーまたは短期トークン）
```

**IAM Identity Center は必須ではありません。** 単一アカウント運用では、**IAM ユーザー＋アクセスキー**、または **IAM ロール＋`sts:AssumeRole`** だけで十分なことが多いです。Identity Center は、複数アカウントや大規模な人員プロビジョニングを一元化したい場合の **オプション**です。

### ロール／ポリシーの割り当ての考え方

| 名前の例 | 目的 | メモ |
| --- | --- | --- |
| `ClaudeAdminRole` | 設定・購読・広い操作 | `AnthropicFullAccess` は必要最小限の主体にのみ |
| `ClaudeDevRole` | 推論＋周辺機能 | インラインポリシーで `CreateSkill` 等を明示 |
| `ClaudeUserRole` | 推論のみ | `AnthropicInferenceAccess` 起点で調整 |
| `ClaudeReadOnlyRole` | 監査 | `AnthropicReadOnlyAccess` |

**単一アカウントでは**、ロールを少数で共有せず、人／アプリごとに IAM プリンシパルを分け、CloudTrail の `userIdentity` で追跡できるようにすることを推奨します。

### 単一 AWS アカウントのみ（Identity Center なし）

Organizations の**メンバーアカウント 1 つ**でも、**スタンドアロンのアカウント 1 つ**でも構いません。

1. **IAM ユーザー + アクセスキー**  
   - ユーザーを作成し、`AnthropicInferenceAccess` 等をアタッチ。  
   - `aws iam create-access-key` でキーを発行し、`aws configure` のプロファイルに設定。  
   - **長期キーは漏えいリスクが高い**ため、ローテーションと Secrets Manager 保管、可能なら短期トークンやロールへの移行を推奨。

2. **IAM ロール + `sts:AssumeRole`**  
   - 同一アカウント内：主体ごとにロールを作り、信頼ポリシーで引き受けを限定。  
   - クロスアカウント：信頼ポリシーで `AssumeRole` を許可。

3. **IAM ユーザー + コンソールパスワード**  
   - API キー発行やサブスク確認など、コンソール作業のみの担当者向け。

環境変数の例（単一アカウント・IAM ユーザー鍵の場合）:

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=ap-northeast-1
export ANTHROPIC_AWS_WORKSPACE_ID='wrkspc_...'
# export ANTHROPIC_AWS_API_KEY='...'
```

OWIF 有効化やワークスペースの既定プロビジョニングは **アカウント単位**のため、**そのアカウント内で 1 回**実施すれば足ります。

### IAM Identity Center を使う場合（任意）

複数アカウント・大量ユーザーを SSO で統制する場合に、Permission Set をロールやポリシーにバインドします。

```bash
aws sso-admin create-account-assignment \
  --instance-arn arn:aws:sso:::instance/ssoins-XXXXXXXX \
  --target-id 123456789012 \
  --target-type AWS_ACCOUNT \
  --permission-set-arn arn:aws:sso:::permissionSet/ssoins-XXXXXXXX/ps-XXXXXXXX \
  --principal-type USER \
  --principal-id user-XXXXXXXX
```

### 開発者向け設定例（Identity Center なし）

```bash
export AWS_PROFILE=test-claude
export ANTHROPIC_AWS_WORKSPACE_ID='wrkspc_01AbCdEf23GhIj'
export AWS_REGION='ap-northeast-1'

pip install "anthropic[aws]"
python -c "from anthropic import AnthropicAWS as C; c=C(); print(c.messages.create(model='claude-sonnet-4-6', max_tokens=32, messages=[{'role':'user','content':'ping'}]).content[0].text)"
```

### Claude Console へのアクセス（`AssumeConsole`）

```json
{
  "Effect": "Allow",
  "Action": "aws-external-anthropic:AssumeConsole",
  "Resource": "*"
}
```

能力（Admin / Developer）は `aws-external-anthropic:Capability` 条件キーで制御します（[IAM policies](https://docs.aws.amazon.com/claude-platform/latest/userguide/iam-policies.html) 参照）。

### API キー命名と保管（参考）

| 用途 | 命名例 | 保管場所 |
| --- | --- | --- |
| 共有バックエンド | `prod-backend-inference-20250501` | AWS Secrets Manager |
| ステージング | `stg-all-team-YYYYMM` | AWS Secrets Manager |
| 個人検証 | `dev-{username}-YYYYMM` | 個人 `.env`（非共有） |

### Claude Code（CLI）

[Claude Code の環境変数](https://code.claude.com/docs/en/env-vars.md) に合わせます。

```bash
npm install -g @anthropic-ai/claude-code

export ANTHROPIC_AWS_API_KEY='<AWS コンソールで発行したワークスペース API キー>'
export ANTHROPIC_AWS_WORKSPACE_ID='wrkspc_01AbCdEf23GhIj'
export AWS_REGION='ap-northeast-1'

# export ANTHROPIC_AWS_BASE_URL='https://aws-external-anthropic.ap-northeast-1.api.aws'

claude
```

### 運用チェックリスト（参考）

```
□ IAM ロール／ユーザーとポリシーのレビューが完了している
□ API キー／短期トークンの保管とローテーション手順がある
□ （任意）IAM Identity Center を使う場合は Permission Set と割当が完了している
□ CloudTrail（Management + 必要な Data）の方針が決まっている
□ コスト可視化（Budgets / CUR）の担当が決まっている
□ レートリミットとクライアント側リトライ方針がある
□ ZDR の要否が契約と整合している
□ インシデント連絡先（AWS / Anthropic）が文書化されている
```

---

## Appendix A：料金・コスト {#appendix-a}

- **換算・単位**（CCU 等）は [Anthropic の Pricing ページ](https://platform.claude.com/docs/en/about-claude/pricing#claude-platform-on-aws-pricing) を正としてください。  
- AWS 側の請求書・**Cost and Usage Report（CUR）**での見え方は進化し得ます。[Monitoring and logging](https://docs.aws.amazon.com/claude-platform/latest/userguide/monitoring.html) の「Cost allocation and monitoring」に従い、**タグをコスト配分キーとして有効化**するのが実務的です。

### ワークスペースへのタグ付け

タグはワークスペースに付与し、IAM 条件や CUR に流します。実装は **`aws-external-anthropic:TagResource` / `UntagResource`** を参照してください（[Workspaces](https://docs.aws.amazon.com/claude-platform/latest/userguide/workspaces.html)）。

### Claude Console の Usage / Cost

Console 上のビューは利便性が高い一方、**請求の最終的な内訳は AWS 側のレポートと突合**してください。

---

## Appendix B：監査ログ・監視 {#appendix-b}

### CloudTrail

[Monitoring and logging](https://docs.aws.amazon.com/claude-platform/latest/userguide/monitoring.html) の分類に従います。

- **Management イベント**：ワークスペース作成や Vault 操作など  
- **Data イベント**：`/v1/messages` などのデータ面（**明示的に有効化が必要**。課金が増える）

#### Data イベントの例

**リソース型：** `AWS::AWSExternalAnthropic::Workspace`（[Monitoring and logging](https://docs.aws.amazon.com/claude-platform/latest/userguide/monitoring.html)）

```bash
aws cloudtrail create-trail \
  --name claude-platform-trail \
  --s3-bucket-name your-cloudtrail-bucket \
  --include-global-service-events \
  --is-multi-region-trail

aws cloudtrail put-event-selectors \
  --trail-name claude-platform-trail \
  --event-selectors '[
    {
      "ReadWriteType": "All",
      "IncludeManagementEvents": true,
      "DataResources": [
        {
          "Type": "AWS::AWSExternalAnthropic::Workspace",
          "Values": ["arn:aws:aws-external-anthropic:*:*:workspace/*"]
        }
      ]
    }
  ]'
```

トレイルの種類や高度なセレクタ併用可否は [CloudTrail ユーザーガイド](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/) で確認してください。

### リクエスト ID

- `x-amzn-requestid`：AWS サポート／CloudTrail 調査向け  
- `request-id`：Anthropic サポート向け  

取得は **`with_raw_response`** パターンが確実です（[Monitoring and logging](https://docs.aws.amazon.com/claude-platform/latest/userguide/monitoring.html) のコード例参照）。

### CloudWatch メトリクスについて

Claude Platform on AWS は、**ワークスペース単位の利用量メトリクスを CloudWatch に自動公開しない**旨が公式に述べられています（同上）。エラーレートやレイテンシは、アプリ側ログや CloudTrail 由来のメトリクスフィルターなどで補完するのが現実的です。

---

## Appendix C：トラブルシューティング {#appendix-c}

| 症状 | 典型原因 | 次のアクション |
| --- | --- | --- |
| `Outbound web identity federation is disabled for your acco
