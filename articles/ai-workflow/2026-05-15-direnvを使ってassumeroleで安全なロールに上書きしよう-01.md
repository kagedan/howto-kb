---
id: "2026-05-15-direnvを使ってassumeroleで安全なロールに上書きしよう-01"
title: "direnvを使って、AssumeRoleで安全なロールに上書きしよう"
url: "https://zenn.dev/avot/articles/a802d403c02340"
source: "zenn"
category: "ai-workflow"
tags: ["zenn"]
date_published: "2026-05-15"
date_collected: "2026-05-16"
summary_by: "auto-rss"
query: ""
---

# 概要

direnvは便利ですよね。アクセスキーを前提としたアカウントの切り替えについては、  
<http://zenn.dev/harashun11/articles/93c05cdd6dec0e>  
とかを見てていただくとして、claudeで使うときのガードレールとして  
普段は書き込めないようにしたいので.envrcでそこまでやっちゃえばいいなと思い設定したのでメモを残します。

## 1. 前提条件

### IAMロールの作成

読み込み専用の化け先ロールを作っておきましょう。（例: `ClaudeAuditRole`）

この環境では、”ReadOnlyAccess”、”SecurityAudit”としてますがよしなに。  
「信頼関係」も以下のような感じで設定しておきます。

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:root"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

### IAMユーザへのポリシー付与

化けさせたいIAMユーザがAssumeRoleできるようにポリシーを追加します。  
（インラインポリシーをその場で作ってますがやり方はなんでもいいと思います。）

```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": "sts:AssumeRole",
			"Resource": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ClaudeAuditRole"
		}
	]
}
```

## 2. 実装方法

実施したいディレクトリの.envrcを以下のような内容にしておきます。

AWS\_PROFILEで指定したプロファイルの権限を使って、AssumeRoleを実行、得られたRead用ロールの一時キーを環境変数に上書きしてる感じです。

.envrc

```
# .envrc
export AWS_PROFILE="YOUR_IAM_PROFILE"
export AWS_DEFAULT_REGION="ap-northeast-1"
TARGET_ROLE_ARN="arn:aws:iam::YOUR_ACCOUNT_ID:role/ClaudeAuditRole"

# スイッチの切り替え（falseにすると元のプロファイル権限で動作）
USE_READONLY=true

if [ "$USE_READONLY" = true ]; then
  # 既存をクリア
  unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
  
  # AssumeRoleを実行し結果をevalで環境変数に展開
  eval "$(aws sts assume-role \
    --role-arn "$TARGET_ROLE_ARN" \
    --role-session-name "audit-session" \
    --query 'Credentials.[
      join(`=`, [`export AWS_ACCESS_KEY_ID`, AccessKeyId]),
      join(`=`, [`export AWS_SECRET_ACCESS_KEY`, SecretAccessKey]),
      join(`=`, [`export AWS_SESSION_TOKEN`, SessionToken])
    ]' \
    --output text)"
# この辺はわかりやすさのためなので要らないかもしれないです。    
  echo "MODE: READONLY (STS)"　
else
  echo "MODE: PROD (Full Admin)"
fi

# 現在の有効な権限を表示
aws sts get-caller-identity --query "Arn" --output text
```

## 3. トラブルシューティング

Role cannot be found  
同じミスする人は居ないと思いますが、  
別のディレクトリで間違ってaws sts assume-role しようとしてコマンドが通らなかったので気を付けてください。

権限が反映されない  
aws sts assume-roleの話ですが、コマンド単体の実行では現在のシェルの環境変数は更新されませんので、evalを用いるか、出力された値を個別にexportする必要があります。

sts:AssumeRole is not authorized  
作ったロールへのsts:AssumeRole実行権限が実行したいIAMロールに付与されているか確認してください。

## 4. 運用

対象ディレクトリへ移動し、direnv allowを実行した後はディレクトリに入るだけで、

```
export AWS_PROFILE="YOUR_IAM_PROFILE"
```

を通り越して、今回作ったロールのプロファイルになります。  
あとは普通にClaude呼び出すだけですね。  
env | grep AWS\_ なり、aws sts get-caller-identityなり切り替わってること確認できると思います。  
元のプロファイル権限が必要な場合は、USE\_READONLY=trueを単にコメントアウトです。  
(いろいろ考えたのですが、デフォルトではRead、必要なときに書き換えればいいなと思ったのでこの実装です。)
