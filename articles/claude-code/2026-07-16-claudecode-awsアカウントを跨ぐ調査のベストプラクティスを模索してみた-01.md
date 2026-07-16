---
id: "2026-07-16-claudecode-awsアカウントを跨ぐ調査のベストプラクティスを模索してみた-01"
title: "【ClaudeCode × AWS】アカウントを跨ぐ調査のベストプラクティスを模索してみた"
url: "https://qiita.com/kikuziro/items/6cbd5f7846cb1739f7ae"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "qiita"]
date_published: "2026-07-16"
date_collected: "2026-07-17"
summary_by: "auto-rss"
query: ""
---

## 📨 AIエージェント間の伝令役になってた

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2933489/5cbbff17-2e0d-4e4b-ac69-5490b4d185f7.png)

先日、AWSのクロスアカウントアクセスがうまくいかず、エラーの原因がアカウントAにあるのかアカウントBにあるのか切り分ける必要が出てきました。で、私が何をしていたかというと…完全に伝令役になってました。

>1. アカウントAにつないだClaude Codeに「なんでエラーになるの？」と聞く
>2. 「B側のバケットポリシーを確認してください」と言われる
>3. その文章をコピペして、アカウントBにつないだClaude Codeに投げる
>4. Bの回答をコピペして、Aに持ち帰る （自分で調べろよ...）

「もっと効果的な方法あるでしょ」ってことでClaude Codeでアカウントをまたいだ調査を自動化する方法を3パターン考えて実際に試してみました。

## 📋 今回の前提

- アカウントA → アカウントBへのクロスアカウントアクセスが失敗している
- 原因がA側（IAMポリシー、AssumeRoleの設定など）にあるのか、B側（リソースポリシー、信頼ポリシーなど）にあるのかを切り分けたい
- Claude Codeを使う

:::note warn
本記事の構成はあくまで検証・実験目的です。
:::

## 💡 考えた3つの方式

### 📌 共有ファイル＋ポーリング（掲示板方式）

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2933489/dac11daf-4c40-401d-9de0-deda95ae9029.png)

アカウントA、アカウントBそれぞれでエージェントを起動し、共通のファイルに「調査結果」と「相手アカウントへの質問」を書き合う方式です。各エージェントは1分ごとにファイルを見に行くループを回して、相手からの質問が書かれていたら調査して回答を追記します。

### 🕹️ MCP＋サブエージェント方式

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2933489/c6c932d4-2297-4058-9683-9f0b399ae777.png)

アカウントA用、アカウントB用のMCP（Model Context Protocol。エージェントに外部ツールを追加で持たせる仕組み）サーバーをそれぞれ作成し、さらにA担当・B担当のサブエージェントを定義します。メインエージェントが**司令塔**となって、サブエージェントに指示を出し報告を集めて推理する方式です。

### 🎭 AWSMCPServer＋マルチプロファイル（早着替え方式）

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2933489/3c1a3af5-3d73-424f-9115-b5d277e11555.png)

アカウントAを主体としつつ、Bを調べたくなったタイミングで同じエージェントが認証情報だけを着替えて、そのままアカウントBを直接調査する方式です。今回は2026年6月にクロスアカウント・クロスロールアクセス対応が発表された「AWS MCP Server」のマルチプロファイル機能を使います。

https://aws.amazon.com/jp/about-aws/whats-new/2026/06/aws-mcp-server/


ここからは1つずつ実際にやってみます。

## 🧪 方式1を試す（掲示板方式）

### 🏗️ 構成

- アカウントAのエージェント、アカウントBのエージェントをそれぞれ別のターミナルで起動
- 共有フォルダ `/blackboard` に置いた掲示板ファイル `research.txt` を介してやり取り
- 各エージェントはプロンプトの指示に従い、1分おきにファイルをポーリングして相手の追記を待つ

![スクリーンショット 2026-07-16 8.39.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2933489/c85f2563-9c84-41d9-9a68-4f58037b258a.png)

### ⚙️ セットアップ

各アカウントが参照できるエージェントをそれぞれ起動しておきます。
ここで重要な点は自分のアカウントのみ参照できる状態という点です。

### 📝 調査を依頼するプロンプト

アカウントA側のエージェントに状況を説明して調査を丸投げします。ポイントは「クロスアカウント側の確認が必要なら、掲示板ファイルに質問を書いて、1分おきにポーリングしろ」と指示しておくこと。

```プロンプト.txt
S3にファイルをputしました。eventbridge経由でクロスアカウントでSQSが起動されるはずなのですがSQSにデータメッセージが渡っておりません。調査をお願いします。
クロスアカウントの方で調査が必要であれば、以下のフォルダにテキストファイルを作成し、その中にあなたの調査内容及び質問事項を記載してください。また、該当のテキストはクロスアカウント先のエージェントが追記する可能性があるので、1分おきにポーリングして内容を確認してください。内容が追記されていたら、その内容に従って調査を継続してください。
`/blackboard/research.txt`
```

次に、別ターミナルのアカウントB側エージェントに「掲示板を見張って、更新されたら調べて」と指示します。

```プロンプト.txt
`/blackboard/research.txt` ここのファイル内容を1分おきにポーリングし、内容が更新されたら内容に従って調査をお願いします。調査結果はまたテキストに上書きしてください。
```

### 📋 実行結果

あとは放置しておくと、エージェント同士が掲示板越しに会話してくれます。最初のうち、Bは掲示板がまだ空なので健気に待ち続けます。

> ファイルはまだ作成されていません。今回も何もせず、次のポーリングを待ちます。
> ファイルはまだ作成されていません。今回も何もせず、次のポーリングを待ちます。

Aはまず自分のアカウント内を一通り調べ、「A側は全部正常。でもFailedInvocationsが記録されている＝配送そのものが失敗している。原因はB側っぽい」というところまで突き止めて、掲示板（`research.txt`）にB向けの確認事項を書き出しました。Aが書き込んだ確認事項にBがポーリングで気づき、

> 研究依頼ファイル(research.txt)が更新されていました。中身はクロスアカウントAWS障害調査(EventBridge→SQS配送失敗)の依頼です。アカウントB側からの確認事項が4つあるので、調査を開始します。

B側で読み取り専用APIを使って4つの確認事項を調べ、回答欄に追記。それをAが読み取って、最終的に根本原因を結論づけました。原因は、B側のSQSキューポリシーの許可ステートメントに `Principal` 句がまるごと欠落していたこと。

<details><summary>📋 実際の掲示板ファイル（research.txt）の中身を見る</summary>

```markdown
# クロスアカウント調査依頼: S3 -> EventBridge -> SQS メッセージ未達 (2026-07-14)

作成: アカウントA側エージェント
作成日時: 2026-07-14T05:10:00Z 頃

## 状況
アカウントA (111111111111) のS3バケットにファイルをPUTすると、EventBridge経由でアカウントB (222222222222)
のSQSキュー `sample-lambda-job-queue` にメッセージが送られるはずですが、届いていません。

## 構成
- S3バケット: cross-account-test-bucket-01 (アカウントA, ap-northeast-1)
- EventBridgeルール: sample-eventbridge-rule (デフォルトイベントバス, アカウントA)
  - EventPattern: source=aws.s3, detail-type=Object Created, detail.bucket.name=cross-account-test-bucket-01, detail.reason=PutObject
- ターゲット: SQSキュー arn:aws:sqs:ap-northeast-1:222222222222:sample-lambda-job-queue
- 実行ロール(アカウントA): arn:aws:iam::111111111111:role/sample-eventbridge-exec-role

## アカウントA側で確認済み(すべて正常でした)
1. S3バケットのEventBridge通知は有効化済み ( "EventBridgeConfiguration": {} )
2. EventBridgeルールは State=ENABLED、EventPatternも正しい
3. ターゲット設定 (Arn, RoleArn) は正しい。ただし DeadLetterConfig (DLQ) は未設定
4. 実行ロールの信頼ポリシー (AssumeRolePolicyDocument) は Condition句の aws:SourceArn が
   正しく `arn:aws:events:ap-northeast-1:111111111111:rule/sample-eventbridge-rule` になっている
   (ローカルのテンプレートJSONに残っていたプレースホルダー化けは、実デプロイでは発生していませんでした)
5. 実行ロールのインラインポリシー (sample-eventbridge-sqs-send-policy) は、正しいキューARNに対して
   sqs:SendMessage を許可している

## 【決定的な証拠】失敗ポイントの特定
本日 2026-07-14T04:52:18Z にユーザーがS3へファイルをPUTした直後の状態を確認したところ:
- IAMロールの RoleLastUsed.LastUsedDate が 2026-07-14T04:52:18Z に更新されていた
  → EventBridgeによる sts:AssumeRole は成功している
- にもかかわらず、同時間帯 (2026-07-14 13:00 JST台) の CloudWatchメトリクス
  AWS/Events "FailedInvocations" (RuleName=sample-eventbridge-rule) に 1件 記録されている
  → ターゲット(SQS)への配送そのものは失敗している
- 前日 2026-07-13 13:00 JST台にも同様に FailedInvocations=1 が記録されている一方、
  同日14:00〜16:00 JST台は Invocations=1 のみで FailedInvocations は記録なし(成功)

結論: AssumeRoleまでは毎回成功しているが、その後の sqs:SendMessage 実行がアカウントA側の設定不備
以外の理由で失敗している可能性が高いです。DLQ未設定のため詳細なエラー理由はアカウントA側からは
追跡できません。アカウントA側から `sqs:GetQueueAttributes` を試したところ想定通り AccessDenied
となり (クロスアカウントなので当然です)、キューポリシーの中身はこちらからは見えませんでした。

## お願いしたい確認事項 (アカウントB側)
以下、可能な範囲でご確認いただき、このファイルの一番下の「回答欄」に追記していただけますでしょうか。
こちらは1分おきにこのファイルをポーリングして確認します。

Q1. SQSキュー `sample-lambda-job-queue` (ap-northeast-1) のキューポリシー(リソースベースポリシー)
    の中身を教えてください。特に Principal / Condition の記述が下記の正しい値になっているか確認を
    お願いします:
    - Principal ARN (Condition aws:PrincipalArn 等) が
      `arn:aws:iam::111111111111:role/sample-eventbridge-exec-role` になっているか
    - よくある事故として「ロール名部分がプレースホルダー (例: XXXX-eventbridge-exec-role) のまま
      置換されていない」ケースがあるので、そこも確認してください

Q2. このキューはSSE(サーバーサイド暗号化, KMS)が有効になっていますか？ もし有効な場合、
    KMSキーのキーポリシーでアカウントA (111111111111) の上記ロールに対して
    kms:GenerateDataKey / kms:Decrypt 等が許可されているか確認をお願いします。

Q3. アカウントB側のCloudTrailで、以下の時間帯付近に
    `arn:aws:iam::111111111111:role/sample-eventbridge-exec-role` からの sqs:SendMessage に対する
    AccessDenied 等のエラーが記録されていないか確認をお願いします。
    - 2026-07-14T04:52:00Z 〜 04:53:00Z (UTC) 付近 (本日分)
    - 2026-07-13T04:00:00Z 〜 04:10:00Z (UTC) 付近 (前日分、こちらも同様の失敗が1件記録されているため)

Q4. キュー自体が正しく存在し、リージョン(ap-northeast-1)、キュー名(sample-lambda-job-queue)に
    相違がないかもご確認ください。

よろしくお願いいたします。

## 回答欄 (ここから下に追記してください)

回答: アカウントB側エージェント
回答日時: 2026-07-14T05:29:00Z 頃
調査方法: profile account-b (222222222222) で読み取り専用APIのみ使用

A1. SQSキューポリシーは2ステートメント構成でした。
    - `AllowEventBridgeSameAccount`: アカウントB自身のイベントルール専用(Condition句あり、こちらは正常)
    - `AllowCrossAccountEventsRole`: アカウントAのロールを許可する想定の箇所と思われますが、
      Principal要素が丸ごと欠落しています。生のポリシーJSONを直接確認しましたが、
      `arn:aws:iam::111111111111:role/sample-eventbridge-exec-role` やアカウントID 111111111111
      への言及は一切ありませんでした。プレースホルダー化けではなく、Principal句そのものが
      入っていない状態です。
    → Principalのない許可ステートメントは実質的に何も許可しないため、クロスアカウントからの
      sqs:SendMessageは暗黙denyになっていると考えられます。これが根本原因の最有力候補です。

A2. SSEは有効ですが `SqsManagedSseEnabled=true` (SSE-SQS、AWS管理キー) で、
    カスタマー管理KMSキー (`KmsMasterKeyId`) は未設定でした。
    → KMSキーポリシーによるクロスアカウント制限は存在しないため、Q2(KMS)は原因ではありません。

A3. アカウントB側にはCloudTrail Trail・Event Data Store のいずれも未設定でした
    (`describe-trails` / `list-event-data-stores` ともに空)。
    sqs:SendMessageはデータイベントのため、Trail未設定の状態では記録自体が存在せず、
    ご指定の時間帯のAccessDeniedログは確認できませんでした(記録なし、確認不可という結果です)。

A4. `get-queue-url` は成功し、ARNは
    `arn:aws:sqs:ap-northeast-1:222222222222:sample-lambda-job-queue` と完全一致しました。
    リージョン・キュー名の相違はありません。

## 結論・推奨対応
キュー自体・暗号化設定には問題なく、原因は SQSキューポリシーの`AllowCrossAccountEventsRole`
ステートメントにPrincipal句が欠落していることと推測されます。Terraform定義で
Principal(`arn:aws:iam::111111111111:role/sample-eventbridge-exec-role`)の設定が
抜け落ちている可能性が高いため、該当ステートメントにPrincipalを追加のうえ再適用することを
推奨します。あわせて、原因切り分けを容易にするため、EventBridgeターゲットへのDLQ設定と、
アカウントB側でのCloudTrail Trail(データイベント記録)有効化もご検討ください。
```

</details>

私がコピペで往復していたやり取りを、エージェント2体が掲示板越しに調査してくれました。

## 🔬 方式2を試す（サブエージェント方式）

### 🧩 構成

- アカウントA用MCPサーバー / アカウントB用MCPサーバー（それぞれ読み取り系のAWS APIだけを公開）
- A調査担当サブエージェント / B調査担当サブエージェント
- メインエージェントが両者に指示を出し、報告を突き合わせて調査

![スクリーンショット 2026-07-16 8.40.55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2933489/126b94cb-bc23-47c2-86f2-9d492cea4d56.png)

### 🛠️ セットアップ

セットアップは大きく2つ。読み取り専用のMCPサーバーを2アカウント分用意するのと、各アカウント専任のサブエージェントを定義することです。

まずMCPサーバー。

<details><summary>⚙️ .mcp.json（読み取り専用・2アカウント分）</summary>

```json
{
  "mcpServers": {
    "aws-api-account-a": {
      "command": "uvx",
      "args": ["awslabs.aws-api-mcp-server@latest"],
      "env": {
        "AWS_API_MCP_PROFILE_NAME": "default",
        "AWS_REGION": "ap-northeast-1",
        "READ_OPERATIONS_ONLY": "true",
        "REQUIRE_MUTATION_CONSENT": "true"
      }
    },
    "aws-cloudwatch-account-a": {
      "command": "uvx",
      "args": ["awslabs.cloudwatch-mcp-server@latest"],
      "env": {
        "AWS_PROFILE": "default",
        "AWS_REGION": "ap-northeast-1",
        "FASTMCP_LOG_LEVEL": "ERROR"
      }
    },
    "aws-api-account-b": {
      "command": "uvx",
      "args": ["awslabs.aws-api-mcp-server@latest"],
      "env": {
        "AWS_API_MCP_PROFILE_NAME": "account-b",
        "AWS_REGION": "ap-northeast-1",
        "READ_OPERATIONS_ONLY": "true",
        "REQUIRE_MUTATION_CONSENT": "true"
      }
    },
    "aws-cloudwatch-account-b": {
      "command": "uvx",
      "args": ["awslabs.cloudwatch-mcp-server@latest"],
      "env": {
        "AWS_PROFILE": "account-b",
        "AWS_REGION": "ap-northeast-1",
        "FASTMCP_LOG_LEVEL": "ERROR"
      }
    }
  }
}
```

</details>

次にサブエージェント。`.claude/agents/` に配置します。キモは **`tools` にそのアカウント専用のMCPツールだけを列挙する**こと。アカウントA担当エージェントには `aws-api-account-a` 系のツールしか渡さないので、間違ってもB側を触れません。ここで境界を担保しています。以下はA担当の例。

<details><summary>⚙️ .claude/agents/aws-account-a-investigator.md</summary>

```markdown
---
name: aws-account-a-investigator
description: "個人AWSアカウント(A: 111111111111 / プロファイルdefault)専任の調査エージェント。このアカウント側のAWSリソース調査、クロスアカウント連携設定の確認に使う。"
model: sonnet
color: cyan
tools:
  - mcp__aws-api-account-a__call_aws
  - mcp__aws-api-account-a__suggest_aws_commands
  - mcp__aws-cloudwatch-account-a__analyze_log_group
  - mcp__aws-cloudwatch-account-a__analyze_metric
  - mcp__aws-cloudwatch-account-a__cancel_logs_insight_query
  - mcp__aws-cloudwatch-account-a__describe_log_groups
  - mcp__aws-cloudwatch-account-a__execute_cwl_insights_batch
  - mcp__aws-cloudwatch-account-a__execute_log_insights_query
  - mcp__aws-cloudwatch-account-a__execute_promql_query
  - mcp__aws-cloudwatch-account-a__execute_promql_range_query
  - mcp__aws-cloudwatch-account-a__get_active_alarms
  - mcp__aws-cloudwatch-account-a__get_alarm_history
  - mcp__aws-cloudwatch-account-a__get_logs_insight_query_results
  - mcp__aws-cloudwatch-account-a__get_metric_data
  - mcp__aws-cloudwatch-account-a__get_metric_metadata
  - mcp__aws-cloudwatch-account-a__get_promql_label_values
  - mcp__aws-cloudwatch-account-a__get_promql_labels
  - mcp__aws-cloudwatch-account-a__get_promql_series
  - mcp__aws-cloudwatch-account-a__get_recommended_metric_alarms
  - mcp__aws-cloudwatch-account-a__recommend_indexes_account
  - mcp__aws-cloudwatch-account-a__recommend_indexes_loggroup
---
あなたは「アカウントA調査エージェント」です。担当はAWSアカウント(アカウントA: 111111111111 / ローカルプロファイル `default`)のみ。

## 役割
- アカウントAのAWSリソース(IAM・ネットワーク・各種サービスの設定など、対象は問わない)を読み取り調査する

## 報告ルール
- 取得した情報は推測で補わず、実際にツールで確認した事実のみを報告する
- 確認できなかった項目は「確認できなかった」と明記し、憶測で埋めない

## 出力フォーマット
​```markdown
## アカウントA調査結果：{調査テーマ}
### わかったこと
{ARN・リソース名・設定値を含めた事実ベースの箇条書き}
### クロスアカウント関連の設定(該当する場合)
{Principal / AssumeRole / 許可先アカウントIDなど}
### 確認できなかったこと
{権限不足・リソース不在などで確認できなかった項目}
​```

## 応答ルール
- 全ての応答は必ず日本語で行うこと
```

</details>


### 💬 調査を依頼するプロンプト

方式1と同じ事象をエージェントに投げます

```プロンプト.txt
アカウントAにS3オブジェクトをプットしました。イベントブリッジ経由でアカウントBのSQSが動くはずなんですけど、動いていません。原因を調査してください。
```

### 📋 実行結果

両アカウントに同時に調査依頼が走っています。

> aws-account-a-investigator (Account A側のEventBridge発火状況調査) · 26 tool uses · 52.8k tokens
> aws-account-b-investigator (Account B側のSQS受信状況調査) · 16 tool uses · 66.8k tokens

応答が来ました。

<details><summary>📋 エージェントからの回答を見る</summary>

> A担当・B担当の調査結果と司令塔自身の分析が同じ結論に収束しました。原因はコードの不具合ではなく、Account B側のリソースに対する手動操作によるドリフトです。
>
> 原因
> - Account A (111111111111) の検証用バケット cross-account-test-bucket-01 へのPUTは正常に検知され、EventBridgeルール sample-eventbridge-rule が発火 → IAMロール sample-eventbridge-exec-role のAssumeRoleも成功している(CloudTrailで確認)。
> - しかしAccount B (222222222222) のSQSキュー sample-lambda-job-queue のキューポリシーで、クロスアカウント許可用のステートメント AllowCrossAccountEventsRole から Principal 要素が丸ごと消えている。そのためAccount AからのSendMessageが暗黙Denyになっており、CloudWatchメトリクスも Invocations=1 / FailedInvocations=1 で一致。
> - CloudTrailで特定：今日 2026-07-14 13:47〜13:50(JST)に、AWSコンソールから SetQueueAttributes が7回連続で手動実行されており(Principal ARNの末尾を試行錯誤で書き換え)、最後の適用(13:50:23)でPrincipal自体を落とした状態が保存されてしまっていました。Terraform管理下の正しい状態(7/13 15:29 apply時点、条件キー削除後・Principalは正常)からズレています。

</details>

方式1と同じ結論に加えて、B側CloudTrailの操作履歴（管理イベント）から「いつ・どの操作でPrincipalが消えたか」まで特定してきたのは驚きでした。A担当・B担当が同じフォーマットで報告してくるおかげで突き合わせもスムーズで、「全証拠を1か所に集めて推理する」強みを実感できました。

## 🚀 方式3を試す（早着替え方式）

### 🔧 構成

- プロキシ起動時にA・B両方のプロファイルを許可リストとして登録。ツールに `aws_profile` パラメータが生え、エージェントがツール呼び出し1回ごとに使うアカウントを指定できる（省略時はA側）

![スクリーンショット 2026-07-16 8.42.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2933489/265570e7-a571-4746-8a35-6e26e6d7e83e.png)

### 🧰 セットアップ

前提は`~/.aws` にA・B両方のプロファイルがあること。`.mcp.json` に書くのはこれ1つだけです。
方式2ではMCPサーバー＋サブエージェント2つが必要でしたが今回は1つで両アカウントに届きます。

```json
{
  "mcpServers": {
    "aws-mcp": {
      "command": "uvx",
      "args": [
        "mcp-proxy-for-aws==1.6.3",
        "https://aws-mcp.us-east-1.api.aws/mcp",
        "--metadata", "AWS_REGION=ap-northeast-1"
      ],
      "env": {
        "AWS_MCP_PROXY_PROFILES": "default account-b"
      }
    }
  }
}
```

:::note info
AWS_MCP_PROXY_PROFILES ここに書いたプロファイル以外は使えず、エージェントが `~/.aws/config` にある他のプロファイルを勝手に発見して使うこともできません。
:::

### 🗣️ 調査を依頼するプロンプト

方式1と同じ事象を、今度も1つのエージェントに丸ごと任せます。変わるのは切り替えの指示だけ。

```プロンプト.txt
S3にファイルをputしました。EventBridge経由でクロスアカウントでSQSにメッセージが渡るはずなのですが、届いておりません。原因の調査をお願いします。
まずはこのアカウント（アカウントA）側から調査してください。クロスアカウント先（アカウントB側）の調査が必要になったら、ツールの `aws_profile` パラメータに `account-b` を指定して、あなた自身がそのままB側も直接調査してください。
原因がどちらのアカウントのどの設定にあるのか、根拠とあわせて報告してください。
```

### 📋 実行結果

「A側は正常、原因はB側」と当たりを付けたエージェントは、同じ会話の中で `aws_profile` に `account-b` を指定し、B側のキューポリシーを直接取得。最終報告がこちら（抜粋）。

<details><summary>📋 エージェントからの回答を見る</summary>

> 原因はアカウントB（222222222222）側の SQS キューポリシーです。クロスアカウント許可用ステートメント AllowCrossAccountEventsRole から Principal 要素が丸ごと欠落しており、A側実行ロールからの sqs:SendMessage がリソースポリシーで許可されず、配信が拒否されています。A側の設定はすべて正常でした。
>
> 現在B側に適用されているポリシー（該当部分）:
>
> ```json
> {
>   "Sid": "AllowCrossAccountEventsRole",
>   "Effect": "Allow",
>   "Action": "sqs:SendMessage",
>   "Resource": "arn:aws:sqs:ap-northeast-1:222222222222:sample-lambda-job-queue"
> }
> ```
>
> Principal がないため、このステートメントは誰にも権限を与えていません。クロスアカウントアクセスは「A側のIAMポリシー」と「B側のリソースポリシー」の両方の明示Allowが必要なので、これで配信が止まります。

</details>

掲示板のポーリング待ちも、サブエージェントの起動も挟まず、1つの会話の中で方式1・方式2と同じ結論にたどり着きました。

## ⚖️ 3つ試しての比較

3方式を並べて比べると、こうなりました。

| 軸 | 方式1 掲示板 | 方式2 司令塔 | 方式3 マルチプロファイル |
| --- | --- | --- | --- |
| スピード| △ ポーリング往復 | ◎ 並列調査で速い | ⚪︎ 単一エージェント |
| 構築の手間 | ⚪︎ 共有領域のみ | △ MCP＋サブエージェント | ⚪︎ mcp-proxy-for-aws |
| アカウント境界 | ◎ ハード分離 | ⚪︎ サブエージェントはハード、メインは両方保持 | ⚪︎AWS_MCP_PROXY_PROFILES |
| 拡張性(アカウント追加) | ⚪︎ セッション追加 | △ MCP＋サブエージェント | ◎ プロファイル名の追加 |


## 🏆 結局どのパターンがいいの？
全てのパターンでアカウントを跨いだ調査ができ原因特定までできました。
しかし正直どれが一番とは判断できませんでした。そのうえで今回の調査でバランスが取れていると感じたのは方式3です。ただし方式3はコンテキスト内に複数アカウントの情報が同居するため、調査が長引いてコンテキストが肥大化すると、混線や取り違えのリスクが顕在化してくるかもしれません。3方式とも選択肢として手元に置いておいて状況に応じて使い分けるのがいいかなと思いました。

::: note warn
どの方式でも調査エージェントに渡す権限は読み取り専用に絞るのが大前提です.
:::


## 🔗 おまけ：DevOpsAgentでもできるようです
セカンダリアカウントを登録することでアカウントを跨いだ調査をDevOpsAgent上でも行えるようです。ぜひチェックしてみてください。

https://dev.classmethod.jp/articles/aws-devops-agent-multi-account-access/
