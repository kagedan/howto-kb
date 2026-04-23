---
id: "2026-03-30-awsリセールアカウントでbedrockのanthropicモデルが使えなくなったときの対処法-01"
title: "AWSリセールアカウントでBedrockのAnthropicモデルが使えなくなったときの対処法"
url: "https://qiita.com/nishikawa/items/4abd518c0def925f735a"
source: "qiita"
category: "ai-workflow"
tags: ["qiita"]
date_published: "2026-03-30"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

## はじめに

AWS のリセール（請求代行）アカウントで Amazon Bedrock の Anthropic モデルを使用していたところ、モデルの更新をきっかけに2つの問題が立て続けに発生しました。

* **問題① リセールアカウントで新しい Anthropic モデルが使えない**
* **問題② 別アカウントの Bedrock を使うようにしたら、今度は認証情報が1時間で切れる**

この記事では、その原因と対処法をまとめます。

**構成のイメージ**

某スポーツの試合情報を基にハイライトテキストを生成する用途で使っていました。

---

## 問題① リセールアカウントで Anthropic モデルが制限される

### 何が起きたか

使用していた `Claude 3.7 Sonnet` が廃止予定となったため、`Claude Sonnet 4.5` に変更しようとしたところ、以下のエラーが発生しました。

```
ValidationException
Access to this model is not available for channel program accounts.
Reach out to your AWS Solution Provider or AWS Distributor for more information.
```

### 原因

2025年10月に発表された、Bedrock パートナーリセールにおける Anthropic モデルの制限によるものです。

> Resale of Anthropic models subject to certain limitations.

参考: <https://aws.amazon.com/jp/blogs/apn/amazon-bedrock-now-available-for-partner-resale/>

リセール（請求代行）アカウントでは、**新規で Anthropic モデルを追加利用することができません。**

### 対処法

別モデルへの切り替えも試みましたが精度が要件を満たさなかったため、**新規 AWS アカウントを作成して Bedrock を利用する**構成に変更しました。

**変更後**

対応した内容は以下のとおりです。

| 対応内容 | アカウント |
| --- | --- |
| `Claude Sonnet 4.5` の使用申請 | 新規アカウント |
| Bedrock 用 IAM ロール作成（Bedrock 使用権限 ＋ 元アカウントからのアクセス許可） | 新規アカウント |
| Lambda の IAM ロールに新規アカウントの Bedrock 使用権限を追加 | 元アカウント |
| Lambda の認証処理・接続先を新規アカウントの Bedrock に変更 | 元アカウント |

---

## 問題② クロスアカウント構成で認証情報が1時間で切れる

### 何が起きたか

新規アカウントの Bedrock を使う構成に変更後、しばらくは正常に動作していましたが、**試合数の多い日に途中からエラーが発生**するようになりました。

### 原因の特定

状況を整理すると、以下の条件が重なっていました。

* Lambda から別アカウントの Bedrock に接続するため、**AssumeRole で認証情報を取得**していた
* 認証処理を**コンテナ起動時**に1回だけ実行していた
* 品質チェック機能の追加で Lambda の**処理時間が増加**していた
* 試合数が多く、**5分間隔の Scheduler が同じコンテナを使い回す**状態になっていた
* AssumeRole で取得した認証情報の**有効期限は1時間**

つまり、コンテナが1時間以上使い回され続けると、起動時に取得した認証情報が期限切れになりエラーになる、という流れでした。

```
コンテナ起動（認証情報取得）
  ↓
5分後: 同じコンテナを再利用（認証情報はそのまま）
  ↓
  …（繰り返し）
  ↓
1時間後: 認証情報の有効期限切れ → エラー 💥
```

### 対処法

**コンテナ起動時ではなく、Scheduler の実行タイミング（Lambda ハンドラーの中）で毎回認証し直す**ように変更しました。

```
# 変更前：コンテナ起動時に1回だけ認証
credentials = assume_role()  # モジュールレベルで実行

def handler(event, context):
    client = boto3.client('bedrock-runtime', **credentials)
    ...

# 変更後：ハンドラー実行のたびに認証
def handler(event, context):
    credentials = assume_role()  # ハンドラー内で毎回実行
    client = boto3.client('bedrock-runtime', **credentials)
    ...
```

これ以降、認証エラーは発生していません。

Lambda のコンテナは一度起動すると**しばらく使い回されます**。モジュールレベルで認証情報を取得していると、長時間稼働時に期限切れになるので注意が必要です。

---

## まとめ

| 問題 | 原因 | 対処法 |
| --- | --- | --- |
| リセールアカウントで Anthropic モデルが使えない | パートナーリセール制限（2025年10月〜） | 別 AWS アカウントで Bedrock を利用 |
| クロスアカウント認証が1時間で切れる | コンテナ起動時の認証情報をそのまま使い続けていた | Lambda ハンドラー内で毎回認証し直す |

リセールアカウントで Bedrock を使っている方、Lambda のコンテナ使い回しを意識していなかった方の参考になれば幸いです。

---

弊社ウェブサイトでは、技術記事の他にもデザインナレッジや日々の気づき等を配信しています。  
<https://www.jbgoode.jp/>

カジュアル面談も実施中です。お気軽にお問い合わせください。  
<https://www.jbgoode.jp/recruit/>
