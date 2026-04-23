---
id: "2026-04-13-claude-managed-agentsで家庭内パーソナルアシスタントを作った-01"
title: "Claude Managed Agentsで家庭内パーソナルアシスタントを作った"
url: "https://zenn.dev/trknhr/articles/b6170f4284789e"
source: "zenn"
category: "ai-workflow"
tags: ["AI-agent", "zenn"]
date_published: "2026-04-13"
date_collected: "2026-04-14"
summary_by: "auto-rss"
---

# はじめに

Claude Managed Agentsが出たので、家庭内の雑務を受けるパーソナルアシスタントを試しに作ってみました。まだまだ運用に乗ってないPoCレベルのアプリですが。

やりたかったのは、ざっくり言うと「Slackで呼べて、家庭のメモやタスクや予定をそこそこ賢く扱ってくれるAI」です。家族や親戚の誕生日、何を贈ったか、学校や保育園のプリント、生協の注文、日々の細かい家事タスクあたりを雑に投げても、それなりに覚えて整理してくれるものを目指しました。

最初の印象を先に書くと、Claude Managed Agentsはかなり良かったです。特に、

* 実行環境を自前でホスティングしなくてよい
* Vaultやsandboxが最初からManagedで用意されている
* MCPやcustom toolを軸に安全な構成を組みやすい

一方で、Slack Events APIの受け口や、タスク状態の保存、定期実行の制御まで全部をManaged Agentだけで完結させるのは難しかったです。最終的には `Lambda + DynamoDB + EventBridge Scheduler` を周辺に置いて、Managed Agentを中核にする構成に落ち着きました。

実際こんな感じで機能します。  
![](https://static.zenn.studio/user-upload/a37e72941355-20260413.png)

# 作りたかったもの

要件はこんな感じです。

1. 家庭タスクをSlackからメンションで呼び出せる
2. AIがメモしたり文字起こししたりできる
3. Google CalendarやDriveと連携して大事なことを見逃さない
4. AIが一日一回、家庭のタスクをリマインドしてくれる
5. 終わったタスクや定期イベントを雑に投げても、それっぽく覚えてくれる

このうち、今回ちゃんと動いたのは主に `1 / 2 / 4 / 5` です。`3` の Calendar / Drive 連携は次の段階です。というのもClaude Managed Agents側で連携があらかじめ用意されていなかったので今回は後回しにすることにしました

# Quickstartはかなりよかった

まずは Claude Console の Quickstart から始めました。

対話しながら Agent の設定が固まっていくので、叩き台を作るにはかなり便利です。日本語IMEまわりは少し怪しくて、Enterで送信されがちな場面はありましたが、初期セットアップとしては十分に速い印象でした

## Slack MCP

Slack側ではBotアカウントを作り、必要な権限を付けました。最終的に必要だったのは主にこのあたりでした。

* `app_mentions:read`
* `chat:write`
* `files:read`

Slack MCP自体はManaged Agent側に持たせています。ただ、実際のイベント受信や添付ファイルの回収はLambda側に寄せています。Slackとの接続を全部MCPだけで処理するというより、役割を分けた形です。

## Sandbox

Claude Managed Agentsでは実行環境もManagedで用意されます。今回は Slack MCP と custom tool の呼び出しを前提にした sandbox を使いました。

DynamoDBをAgentに直接触らせる構成にはしていません。ここは custom tool 経由にして、実際の読み書きは Lambda 側で実行しています。この方が権限境界がはっきりしますし、更新ルールもアプリ側で制御できます。

Anthropicの公式ドキュメントでは、この実行環境は `Environment` として扱われています。Environment は「Agent が動くコンテナ設定」で、1回作ってID参照する形です。複数セッションで同じ Environment を共有できますが、各セッションは独立したコンテナインスタンスを持ち、ファイルシステム状態は共有されません。つまり、「設定は共通化できるが、実行時の状態はセッションごとに隔離される」というのがポイントです。

参照:

今回のように個人用・家庭用のエージェントでも、毎回まっさらな隔離環境で走るので、前回実行のゴミや偶発的な状態に引きずられにくいです。さらに、ネットワーク設定も Environment 側で制御でき、Anthropic の docs でも本番運用では `limited` ネットワークと明示的な `allowed_hosts` を使うことが推奨されています。つまり、sandbox の意義は「Claude を安全に動かすための箱」であるだけでなく、「依存パッケージ・ネットワーク権限・隔離性をまとめて管理するための単位」だと理解するとしっくりきます。

## Vault

Slack MCP用の認証情報は Vault に保存しました。credential をAgentに直接持たせなくてよいのはかなり安心感があります。認証周りで問題が起きた時も、どこを見ればよいかが明確でした。

Vault の意義もかなり明快です。Anthropic の docs では、Vault と credential は「一度登録してIDで参照する認証プリミティブ」として説明されています。これにより、自前で secret store を運用したり、毎回のAPI callでトークンを送ったり、どのユーザー権限でAgentが動いたかを見失ったりせずに済みます。

参照:

もう1つ重要なのは、MCPサーバー定義と認証情報が分離されていることです。Agent 作成時には「どの MCP サーバーに接続するか」だけを定義し、セッション作成時に `vault_ids` を渡して認証を解決します。公式ドキュメントでも、この分離によって「再利用可能なAgent定義から secret を切り離しつつ、セッションごとに別の認証を使える」とされています。今回のように、Slack MCP を使いつつアプリ側からSlackイベントを受ける構成では、この責務分離はかなりありがたかったです。

参照:

# でも周辺アプリは普通に必要

最初は「Managed Agentだけでかなりいけるのでは」と思っていたのですが、実際には周辺アプリは必要でした。

理由は単純で、今回必要だったのが次の3つだったからです。

* Slack Events APIを受けるHTTP endpoint
* Slackの3秒制限に耐える非同期化
* memory / task / session / idempotency のようなアプリ状態

なので構成はこうなりました。

```
Slack mention
  -> API Gateway
  -> Lambda (ingress)
  -> SQS
  -> Lambda (worker)
  -> Claude Managed Agent
  -> Slack reply

Daily reminder
  -> EventBridge Scheduler
  -> Lambda (scheduled runner)
  -> Claude Managed Agent
  -> Slack post

State
  -> DynamoDB
```

Slackのメンションは `ingress Lambda -> SQS -> worker Lambda` に流しています。Slackには即時ACKを返して、Claudeの処理は裏で進める形です。

毎日のリマインダーは EventBridge Scheduler から起動しています。今は毎朝 `09:00 JST` に `daily-summary` タスクを起動し、未完了タスクのリマインダーを Slack に投稿するようにしています。

# どこに何を保存しているか

今回使っている DynamoDB テーブルは7つです。

* `SlackThreadSessionsTable`: Slack thread と Claude session の対応
* `ProcessedEventsTable`: Slackイベントの重複排除
* `ScheduledTasksTable`: 定期実行タスク定義
* `UserMemoriesTable`: Claude memory store との対応
* `MemoryItemsTable`: custom tool経由で保存する半構造化memory
* `TasksTable`: タスクの現在状態
* `TaskEventsTable`: タスク履歴

`MemoryItemsTable` と `TasksTable` / `TaskEventsTable` は今回の肝でした。

家庭用途で本当に欲しいのは、

* 誰かの誕生日で去年何を贈ったか
* 学校や保育園にはどんなタスクや伝言事項があったか
* いま未完了のタスクは何か
* そのタスクは done になったか

みたいな情報です。

これを毎回全部プロンプトに流し込むより、必要な時だけ検索して取り出した方が扱いやすいです。なので正本はDynamoDBに置いて、Claudeには custom tool 経由で読ませる形にしました。

最終的に定義した tool はこの5つです。

* `search_memories`
* `save_memory`
* `list_tasks`
* `upsert_task`
* `mark_task_done`

Managed Agent がこれらを呼ぶと `agent.custom_tool_use` が発生し、Lambda 側がその要求を受けて DynamoDB を更新し、`user.custom_tool_result` を返します。

ここはかなり気に入っています。Agent に DynamoDB の IAM 権限を直接渡さずに済むので、安全ですし、アプリ側のルールも守らせやすいです。

実際、以下は end-to-end で確認できました。

* `save_memory` で「Hanakoの誕生日は8/12」を保存
* `upsert_task` で「誕生日プレゼントを買う」タスクを作成
* `mark_task_done` で done に更新
* `TaskEventsTable` に `created` / `marked_done` が残る

# Slackメンションは普通に使える

Slackから `@AI` と呼ぶと、同じスレッド内で会話が続きます。

ここで効いたのは「Slack thread = Claude session」にしたことでした。Slackの使い方と会話文脈が揃うので、運用上かなり自然です。

また、添付ファイルも Lambda 側で回収するようにしました。`files:read` を付けておけば、Slack の `url_private` から PDF や画像を取り、Claude に `document` / `image` ブロックとして渡せます。

これで、

* 学校や保育園の配布PDFを投げる
* AIが内容を読む
* 必要ならタスク化する
* 重要事項は memory に保存する

という流れがかなり取りやすくなりました。

# 毎日のリマインダーも作れた

定期実行は EventBridge Scheduler を使いました。

今は `daily-summary` という task 定義を DynamoDB に持たせていて、毎朝9時に scheduled runner がその task を読んで Claude を起動します。

中身は単純で、まず `list_tasks` を呼んで `open` / `in_progress` の未完了タスクを取ります。その上で、その日のリマインダー文面を Claude に作らせて Slack に投稿しています。

固定文ではなく、DynamoDB上の未完了タスクを見てその日の文面を作れるので、この構成は運用的にも相性が良さそうです。

# PDFを読んで勝手に覚えさせるのはかなり良い

これは家庭用途と相性がよかったです。

SlackにPDFを投げて `@AI これ見ておいて` と言えるだけで、だいぶ使い勝手が変わります。プリントを見て、

* 日付を拾う
* やることをタスク化する
* 名前やイベントを memory に保存する

まで繋がると、家庭内の「忘れやすいけど重要なもの」をかなり吸収できます。

厳密なデータベースというより、「あとでそれっぽく思い出せること」が重要な場面は多いので、`save_memory` と `search_memories` に分けていますが、この辺は運用していくと意外と辛いかもなので最悪作り直すかもです。。。

# Pricing

料金はやはり気になります。

公式Pricingページを見ると、今回使っている `Claude Sonnet 4.6` は次の料金でした。

* Input: `$3 / MTok`
* Output: `$15 / MTok`
* Session runtime: `$0.08 / session-hour`

参照:

家庭用途なら、雑な試算で月 `$10 前後` には収まりそうです。

前提はこう置きました。

* Slack mention: 1日5回
* Daily reminder: 1日1回
* mention 1回あたり: 入力12k tokens / 出力1.2k tokens / runtime 20秒
* reminder 1回あたり: 入力15k tokens / 出力1.5k tokens / runtime 15秒

この前提だと、

* mention 側: `約 $8.4 / month`
* reminder 側: `約 $2.1 / month`
* 合計: `約 $10.5 / month`

くらいです。

もちろん、以下が増えるとすぐ上がります。

* 長文PDFをたくさん読む
* web search や追加toolを多用する
* 会話が長くなってコンテキストが膨らむ

ただ、家庭用途のように1日の起動回数が限られているなら、AWS側のコストはかなり小さく、支配的なのはClaudeの token cost になりそうでした。

# ハマりどころ

## Slack Eventsの設定

最初は `Request URL` は通るのにイベントが来ない、みたいな状態で少し詰まりました。最終的には、

* Event Subscriptions を有効化
* `app_mention` を追加
* `files:read` を追加
* scope 変更後に app を再インストール

このあたりをちゃんとやる必要がありました。コード自体はAIに任せられるけど設定はAIに聞きながらとはいえ自分でやらなきゃならず最大のボトルネックでした。

## Slack MCPとLambda側の責務分離

Slack MCP は便利なのですが、今回のように外部イベント起点、添付解析、スレッド返信、冪等制御、DBへの保存までやると、Slackの入出力はアプリ側で握ることになりました。

* 入力と配信は Lambda 側
* 推論と必要な tool 呼び出しは Managed Agent 側
* DynamoDBの制御はLambda側、実行はManaged Agent

## Memoryは最初から何でも自動保存しない方がよい

これは今後の運用ですが、メモリは放っておくとすぐ汚れます。誕生日や贈り物履歴のような durable なものはよいのですが、一時的な依頼まで全部保存すると破綻します。

今回は `save_memory` という明示的な入口を作り、どの情報を残すかをAgentに判断させつつ、最終的な保存はアプリ側が制御する形にしました。

# 今後やりたいこと

次はこのあたりをやりたいです。

* Google Calendar への登録と、返ってきた event id を task に紐付ける
* Google Drive 上の資料を読んで task / memory に落とす
* `done` になったタスクを週次で振り返る
* 「誕生日が近い」「生協の締切が近い」のような reminder を増やす
* memory の自動保存ポリシーを整える
* memoryの自動クリーンアップ
* 運用運用運用

特に Calendar 連携は重要で、Claude が予定を登録し、その結果を structured JSON で受け取り、DynamoDB の task state と同期する形がよさそうだと見ています。  
あとこういうアプリは運用が肝なので長期で家庭内で運用していくというのが非常に大事な気がします。

# まとめ

まとめるとClaude Managed Agents かなり良かったです。

Managed であることの価値が大きいです。可用性、実行環境、credential の扱い、権限制御を全部自前でやるのはやはり重いので、Claude Managed Agents に寄せることでかなりコントロールしやすくなります。

全部をManaged Agentだけで完結させるのではなく、

* 推論と sandbox は Managed
* webhook / state / integration glue は Lambda

に切るのが、今のところかなりしっくり来ています。

家庭内パーソナルアシスタントとしても十分手応えがありました。少なくとも、雑に Slack へメモを投げるだけで「覚える」「思い出す」「朝リマインドする」まで繋がるところまでは見えたので、次は Calendar と Drive を繋いで実運用に寄せていきたいです。

# 参考
