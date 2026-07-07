---
id: "2026-07-07-amazon-bedrockでclaude-35-sonnetが突然利用できなくなったのでcloud-01"
title: "Amazon BedrockでClaude 3.5 Sonnetが突然利用できなくなったのでCloudTrailから原因を調査してみた"
url: "https://qiita.com/ss_IT_study/items/e9a13fb9d6695b4c76ae"
source: "qiita"
category: "ai-workflow"
tags: ["API", "Python", "qiita"]
date_published: "2026-07-07"
date_collected: "2026-07-08"
summary_by: "auto-rss"
query: ""
---

# 目次
[#1.はじめに](#1はじめに)
[#2.環境](#2環境)
[#3.発生した事象](#3発生した事象)
[#4.CloudTrailで調査してみる](#4cloudtrailで調査してみる)
[#5.公式ドキュメントと照らし合わせる](#5公式ドキュメントと照らし合わせる)
[#6.あとがき](#6あとがき)



# 1.はじめに

Amazon Bedrockで提供されている **Claude 3.5 Sonnet** は、東京リージョンでは2026年7月31日に提供終了予定となっています。

私は「提供終了日までは利用できる」と考え、しばらく利用していなかった検証環境から久しぶりにAPIを実行したところ、突然リクエストが失敗するようになりました。

CloudTrailのログと公式ドキュメントを確認したところ、Legacyモデルのライフサイクルによるアクセス制御であることが読み取れました。

この記事では、実際に行った調査結果を紹介します。

::: note warn
今さらClaude 3.5 Sonnetの記事となりますが、今月末ギリギリまでモデルを変更しない方は注意です。
:::

# 2.環境

今回確認した環境は次のとおりです。

|項目|内容|
|---|---|
|リージョン|ap-northeast-1（東京）|
|モデル|anthropic.claude-3-5-sonnet-20240620-v1:0|
|API|Converse|
|SDK|boto3|
|実行環境|AWS Lambda（Python 3.14）|

# 3.発生した事象

元々検証用に作成していたLambdaからClaude 3.5 SonnetへConverse APIを実行したところ、リクエストが失敗しました。

コードは特に修正していませんし、IAMポリシーも変更していません。
「提供終了日はまだ先なのになぜ利用できないのだろう？」と考え、原因調査を行いました。


# 4.CloudTrailで調査してみる

CloudTrailではConverse APIのイベントに次の内容が記録されていました。

```json
{
  "eventSource": "bedrock.amazonaws.com",
  "eventName": "Converse",
  "awsRegion": "ap-northeast-1",
  "errorCode": "ResourceNotFoundException",
  "errorMessage": "Access denied. This Model is marked by provider as Legacy and you have not been actively using the model in the last 30 days. Please upgrade to an active model on Amazon Bedrock",
  "requestParameters": {
    "modelId": "anthropic.claude-3-5-sonnet-20240620-v1:0"
  }
}
```

`errorMessage`を見ると、原因がかなり具体的に記録されていました。

```text
Access denied.
This Model is marked by provider as Legacy
and you have not been actively using the model in the last 30 days.
Please upgrade to an active model on Amazon Bedrock
```

ここから読み取れる情報は次のとおりです。

- モデルはLegacy状態
- 直近30日間利用していない
- 後継モデルへの移行を推奨

# 5.公式ドキュメントと照らし合わせる

Amazon BedrockのModel Lifecycleでは、Legacyモデルについて次のように説明されています。

公式ドキュメントはこちらです。

https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle.html

>新規のお客様はレガシーモデルをご利用いただけません。また、既存のお客様も15日間利用がない場合、レガシーモデルへのアクセス権を失う可能性があります。


今回確認したログの内容では30日となっていたので、ドキュメントの記載と微妙に異なりますが、
レガシー状態ではしばらくモデルを使わないと利用できなくなるようです。

::: note warn
私の環境では30 daysのキーワードがログに出ていましたが、他の方の環境やモデルによってはドキュメント通り15日が基準となる可能性もあるのでご注意ください。
:::

# 今回の調査結果

今回調査した内容を整理すると次のようになります。

|項目|結果|
|---|---|
|対象モデル|Claude 3.5 Sonnet|
|リージョン|東京|
|API|Converse|
|CloudTrail errorCode|ResourceNotFoundException|
|CloudTrail errorMessage|Access denied... Legacy... not actively using...|
|原因|Legacyモデルに対するアクセス制御|
|対応|後継モデルへ移行|

# 6.あとがき

今回の調査では、CloudTrailのログを確認したことで、IAMやSDKではなく、Model Lifecycleによるアクセス制御が関係していることが読み取れました。

結論としてはサービス終了ギリギリまで粘るのではなく、早めにモデルの更新対応をしましょうということですね。

同じ事象に遭遇した方の切り分けの参考になれば幸いです。

# 参考資料

- Amazon Bedrock User Guide - Model lifecycle
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle.html
