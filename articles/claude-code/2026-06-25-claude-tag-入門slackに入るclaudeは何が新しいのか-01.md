---
id: "2026-06-25-claude-tag-入門slackに入るclaudeは何が新しいのか-01"
title: "Claude Tag 入門：Slackに入るClaudeは何が新しいのか"
url: "https://zenn.dev/arufian/articles/ded5c05a77a5d1"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "LLM", "cowork", "zenn"]
date_published: "2026-06-25"
date_collected: "2026-06-26"
summary_by: "auto-rss"
query: ""
---

## はじめに

2026年6月、Anthropicは **Claude Tag** を公開ベータとして案内しました。Claude Tagは、Slackチャンネルで `@Claude` とメンションすると、Claudeがそのスレッド内で作業し、結果を返す仕組みです。

出典：[Work with Claude Tag](https://claude.com/docs/claude-tag/overview)

重要なのは、これは単なる「SlackからClaudeに質問できる機能」ではないという点です。Claude Tagでは、管理者がチャンネルやワークスペース単位でアクセス権を設定し、Claudeがチーム用のサービスアカウントとして、リポジトリ、チケット、データウェアハウス、監視ツールなどにアクセスできます。作業はSlackスレッドに見える形で進み、結果も同じ場所に残ります。

Andrej Karpathyもこの発表に対して、Claude Tagを「LLM UI/UXの3つ目の大きな再設計」と表現しています。彼の整理では、1つ目は「Webサイトへ行くLLM」、2つ目は「PCにダウンロードするアプリとしてのLLM」、3つ目が「組織全体のツールとコンテキストを持ち、人間チームと並んで動く、自己完結した永続的・非同期の存在」です。

出典：[Andrej Karpathyの投稿](https://x.com/karpathy/status/2069547676849557725)

この記事では、公式ドキュメントとKarpathyの投稿をもとに、Claude Tagの仕組み、権限モデル、セキュリティ、使いどころ、導入時の注意点を整理します。

---

## Claude Tagとは

Claude Tagは、Slackチャンネルに参加するClaudeです。ユーザーはSlack上で `@Claude` とメンションし、調査、要約、チケット化、PR作成、データ分析、監視確認などの作業を依頼できます。

公式ドキュメントでは、Claude Tagの基本形を次のように説明しています。

* Slackチャンネル、スレッド、DMで `@Claude` に話しかける
* チャンネルでは管理者が設定した接続と権限を使う
* 作業はAnthropicがホストする一時的なサンドボックスで実行される
* 進行状況はSlackスレッド内のチェックリストとして更新される
* 結果は同じSlackスレッドに投稿される
* 長い作業では、ドキュメント、チャート、ファイル、Pull Requestなどの成果物を作れる

出典：[How Claude Tag works](https://claude.com/docs/claude-tag/concepts/how-it-works)

利用者から見ると、チームメンバーに依頼する感覚に近いです。

```
@Claude checkoutが今朝から遅い。今朝のデプロイ前後でレイテンシを比較して、原因を調べて。
```

Claudeはスレッドで受け取り、DatadogやGitHubなどチャンネルに許可された接続を使い、調査し、必要なら修正PRを開きます。

---

## 何が新しいのか

Claude Tagの新しさは、LLMの入口が「個人の画面」から「チームの作業場所」へ移ることです。

従来のチャットUIでは、利用者がClaudeの画面へ移動し、必要な文脈を貼り、出力をSlackやGitHubへ戻す必要がありました。Claude Codeのようなローカル/IDE型のエージェントでは、作業は強力ですが、基本的には個人の環境と権限に紐づきます。

Claude Tagでは、Slackチャンネルそのものが作業依頼の入口になります。議論、依頼、進捗、成果物へのリンクが同じスレッドに残るため、チーム全体が作業を見て、途中で軌道修正できます。

Karpathyの投稿が示しているポイントもここです。Claude Tagは、Claudeが「どこかに呼び出すツール」ではなく、組織内の人間活動にかなりインラインに入ってくる形です。ツール連携、実行環境、メモリ、セキュリティを裏側で整えることで、Claudeがチームの中に参加しているように扱える、という見方です。

個人的には、Claude Tagは「チャットボット」よりも「Slack常駐のチームエージェント」と捉える方が近いと思います。

---

## 実行の流れ

Claude Tagの1回の依頼は、公式ドキュメント上では次の5ステップで説明されています。

出典：[Lifecycle of a request](https://claude.com/docs/claude-tag/concepts/how-it-works#lifecycle-of-a-request)

```
1. Slackで誰かが @Claude にタスクを依頼する
2. Anthropic側で、そのスレッド専用のサンドボックスが作られる
3. Claudeがチャンネルの権限を使って作業する
4. 結果をSlackスレッドへ返す
5. スレッドが静かになるとサンドボックスは破棄される
```

![セッションの5ステップループ](https://res.cloudinary.com/zenn/image/fetch/s--QOJdNlm6--/https://mintcdn.com/claude-ai/5JFKyLlO7sHMMf5J/images/claude-tag/diagrams/session-loop.svg%3Ffit%3Dmax%26auto%3Dformat%26n%3D5JFKyLlO7sHMMf5J%26q%3D85%26s%3D436dd451c4ab3ab0f0b072f85051e844)  
*出典：[Lifecycle of a request](https://claude.com/docs/claude-tag/concepts/how-it-works#lifecycle-of-a-request)*

ポイントは、スレッドとサンドボックスの寿命が違うことです。Slackスレッド、投稿された結果、開かれたPR、外部システムに保存された成果物は残ります。一方、サンドボックス内だけに存在するファイルは残りません。長い作業では、途中成果をブランチ、PR、Slack添付、ドキュメントなど永続的な場所へ保存するよう依頼するのが実用的です。

また、1つのスレッドが1つの作業セッションになります。同じチャンネル内でも別スレッドなら別セッションです。途中で誰かがスレッドに返信すると、Claudeはその指示を読み、同じ作業の文脈で進めます。再度 `@Claude` とメンションする必要はありません。

![スレッドは残るが、サンドボックスは静かになると解放され、返信で作り直される](https://res.cloudinary.com/zenn/image/fetch/s--ZXbJ6xuD--/https://mintcdn.com/claude-ai/5JFKyLlO7sHMMf5J/images/claude-tag/diagrams/session-lifecycle.svg%3Ffit%3Dmax%26auto%3Dformat%26n%3D5JFKyLlO7sHMMf5J%26q%3D85%26s%3D9a56231787b03f179e8d552d887778fc)  
*出典：[Session context and memory](https://claude.com/docs/claude-tag/concepts/how-it-works#session-context-and-memory)*

---

## チャンネルとDMの違い

Claude Tagでは、どこでClaudeに話しかけるかによって、使われる権限と責任範囲が変わります。

出典：[Team channels and personal DMs](https://claude.com/docs/claude-tag/concepts/how-it-works#team-channels-and-personal-dms)、[How agent identity works](https://claude.com/docs/claude-tag/concepts/agent-identity)

| 場所 | 使う権限 | 作業の見え方 | 主な用途 |
| --- | --- | --- | --- |
| Slackチャンネル | 管理者がチャンネルに設定した接続 | チャンネルメンバー全員が見える | 共有作業、調査、PR、チケット、プロジェクト進行 |
| DM | 個人のclaude.aiアカウントと個人コネクタ | 本人だけ | 個人タスク、自分の予定やファイルを使う作業 |

チャンネルでは、Claudeは依頼者本人として動くのではなく、Claude用にプロビジョニングされたサービスアカウントとして動きます。GitHubならClaude GitHub App、その他のツールなら管理者が用意した専用アカウントです。

![チャンネルとDMでのエージェントの身元](https://res.cloudinary.com/zenn/image/fetch/s--B721mKaJ--/https://mintcdn.com/claude-ai/5JFKyLlO7sHMMf5J/images/claude-tag/diagrams/dm-identity.svg%3Ffit%3Dmax%26auto%3Dformat%26n%3D5JFKyLlO7sHMMf5J%26q%3D85%26s%3Dd4089034f46e4a760f9fac9d36a689cc)  
*出典：[How agent identity works](https://claude.com/docs/claude-tag/concepts/agent-identity)*

この設計により、作業ログを個人アカウントではなくClaudeのサービスアカウントとして追跡できます。一方で、チャンネルにいる人は全員そのチャンネルに紐づくClaudeの権限を使えるため、接続するサービスアカウントには最小権限を与えるべきです。

---

## アクセス権は「人」ではなく「場所」に付く

Claude Tagで最も重要な設計は、アクセス権がユーザーではなくチャンネルやワークスペースのスコープに付くことです。

出典：[Channel access](https://claude.com/docs/claude-tag/concepts/how-it-works#channel-access)

たとえば、`#platform-eng` にはGitHub、Datadog、Sentryを接続し、`#sales` にはSalesforce、HubSpot、Gongを接続する、といった運用ができます。同じ人が両方のチャンネルにいても、Claudeが使える外部システムはそのチャンネルに設定されたものに従います。

この「スコープ → チャンネル → スレッド」の入れ子構造を図にすると、こんな感じです。アクセス権はスコープに、メモリはチャンネル（公開チャンネルはワークスペース共有）に、作業中の状態はスレッドに紐づき、DMはこの構造の外側で個人アカウントとして動きます。

![スコープ・チャンネル・スレッドの3層構造とDM](https://res.cloudinary.com/zenn/image/fetch/s--bjXySugP--/https://mintcdn.com/claude-ai/5JFKyLlO7sHMMf5J/images/claude-tag/diagrams/three-levels.svg%3Ffit%3Dmax%26auto%3Dformat%26n%3D5JFKyLlO7sHMMf5J%26q%3D85%26s%3D511231c5561da4ade26f91cd395488fa)  
*出典：[Session context and memory](https://claude.com/docs/claude-tag/concepts/how-it-works#session-context-and-memory)*

今いるチャンネルでClaudeが何にアクセスできるかは、推測せずに次のように聞くのが推奨されています。

```
@Claude what can you access from this channel?
```

これは導入後の運用でも重要です。人間のSlack権限、個人のGoogle Drive連携、Claude Tagのチャンネル接続は別物です。チャンネルで使えるのは、管理者がそのスコープへ付けた接続です。

---

## セキュリティモデル

Claude Tagは、チャンネルごとに一時的なサンドボックスを作り、外部通信をAgent Proxy経由に限定します。

出典：[Security and data handling](https://claude.com/docs/claude-tag/concepts/security-and-data)

公式ドキュメントで確認できる主な設計は次の通りです。

* サンドボックスはAnthropicのインフラ上で動く
* サンドボックス自体には認証情報を置かない
* 認証情報は別のcredential storeに保存される
* 外部通信はAgent Proxyを通る
* Agent Proxyが宛先ルールを確認し、必要な認証情報を境界で注入する
* 許可されていないホストへの通信はデフォルトでブロックされる
* 接続先ツール側では、Claude用サービスアカウントの操作として記録される

![外部通信のリクエストパス](https://res.cloudinary.com/zenn/image/fetch/s--vwTp5B7p--/https://mintcdn.com/claude-ai/5JFKyLlO7sHMMf5J/images/claude-tag/diagrams/request-path.svg%3Ffit%3Dmax%26auto%3Dformat%26n%3D5JFKyLlO7sHMMf5J%26q%3D85%26s%3De8776cf0edd1f3ec912b9b044c9cc838)  
*出典：[Security and data handling](https://claude.com/docs/claude-tag/concepts/security-and-data)*

つまり、モデルやサンドボックスにAPIキーを直接渡すのではなく、境界にあるプロキシが通信先ごとに資格情報を付ける構造です。

![Agent Proxyの宛先判定](https://res.cloudinary.com/zenn/image/fetch/s--9YcqLI_i--/https://mintcdn.com/claude-ai/5JFKyLlO7sHMMf5J/images/claude-tag/diagrams/proxy-decision.svg%3Ffit%3Dmax%26auto%3Dformat%26n%3D5JFKyLlO7sHMMf5J%26q%3D85%26s%3D9e578cca43452a4feaf952acbf1d597b)  
*出典：[Security and data handling](https://claude.com/docs/claude-tag/concepts/security-and-data)*

ただし、これは「何でも安全に接続してよい」という意味ではありません。チャンネルメンバー全員が、そのチャンネルに紐づくClaudeの接続を使えます。したがって、導入時は次のような設計が必要です。

* 個人アカウントではなく専用サービスアカウントを作る
* 接続先ごとに読み取り専用、書き込み可否、対象リポジトリなどを絞る
* 高権限の接続はプライベートチャンネルや限定スコープに閉じる
* 監査ログでClaudeの操作を追跡できる状態にする
* 外部通信の許可ホストを必要最小限にする

---

## メモリの扱い

Claude Tagのメモリも個人ではなく場所に紐づきます。

出典：[What Claude Tag remembers](https://claude.com/docs/claude-tag/users/memory)

公式ドキュメントによると、公開チャンネルで得たメモリはワークスペース内で共有されます。たとえば `#data-eng` で決まった運用ルールを、別の公開チャンネルから参照できる場合があります。一方、プライベートチャンネルで得たメモリは、そのチャンネル専用のストアに保存されます。

メモリは次のように管理できます。

```
@Claude remember for this channel: PRを開く前に必ずlintを実行して。
```

確認もできます。

```
@Claude what do you remember about this channel?
```

チャンネルメンバーはメモリを確認・修正できます。長い手順や細かい規約をメモリに詰め込むより、リポジトリやドキュメントに置いてClaudeが読めるようにする方が安定します。

---

## ルーチン：依頼しなくても動く作業

Claude Tagは、単発依頼だけでなく、ルーチンも設定できます。

出典：[Set up routines](https://claude.com/docs/claude-tag/users/proactivity)

ルーチンは、スケジュール実行、チャンネル監視、Pull Requestの購読など、チャンネルに紐づく定常作業です。例としては次のような依頼です。

```
@Claude every weekday at 9am JST, read the open threads in this channel,
check linked tickets and pull requests, and post a one-line status per item.
```

ルーチンも通常の依頼と同じく、チャンネルに設定された接続と権限を使います。設定後はチャンネルに可視化され、誰でも一覧確認、編集、停止を依頼できます。

注意点として、スケジュールのタイムゾーンは明示した方が安全です。公式ドキュメントでは、明示しない場合はUTCがデフォルトになり、Claudeが推測する可能性があると説明されています。

---

## 使いどころ

公式のUse case libraryでは、Claude Tagの用途として次のようなものが挙げられています。

出典：[Use case library](https://claude.com/docs/claude-tag/users/use-cases)

| 用途 | 何をするか | 必要な接続例 |
| --- | --- | --- |
| キャッチアップ | スレッド、チャンネル、未対応事項を要約 | なし |
| 依頼のトリアージ | 重複検出、回答、担当者振り分け | 任意でIssue Tracker |
| ドキュメント化 | 議論から決定メモ、チケット、返信文を作る | 任意でDriveやIssue Tracker |
| プロジェクト追跡 | ステータス更新、承認待ちの追跡 | 任意でIssue Tracker |
| ナレッジ検索 | ポリシー、Runbook、過去決定を探す | Google Drive、Notion、Confluence |
| データ質問 | SQL実行、チャート作成 | BigQuery、Snowflake、Redshift |
| バグ修正 | 再現、原因調査、draft PR作成、CI追跡 | GitHub、任意でDatadog/Sentry |
| 監視・アラート | ダッシュボード確認、アラート調査 | Datadog、Sentry、PagerDuty |
| 営業・CS | 商談状況、事前準備、週次パイプライン要約 | Salesforce、HubSpot、Gong |

個人的に最初に試すなら、次の3つが現実的です。

1. 既存スレッドの要約と未決事項の抽出
2. バグ報告チャンネルでの再現手順整理とIssue化
3. 毎朝のプロジェクトステータス更新

これらはSlack内の文脈だけでも始めやすく、接続を増やしたときの効果も分かりやすいです。

---

## 実際の使用例（Slackでの動き）

表だけだとイメージしづらいので、公式プロダクトページに載っている実際のSlackスクリーンショットを使って、Claude Tagが各シーンでどう動くかを見ていきます。

出典：[Claude Tag プロダクトページ](https://claude.com/product/tag)

### 長いスレッドのキャッチアップ

長くなったスレッドに `@Claude` をメンションすると、決定事項、未解決の論点、関係者、そして自分待ちになっている項目を数秒で整理してくれます。会議に出られなかったときや、放置されたチャンネルに合流するときに効きます。

![長いスレッドを要約し、決定事項・未決事項・自分待ちの項目を返すClaude Tag](https://res.cloudinary.com/zenn/image/fetch/s--NmOCGfZc--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://cdn.prod.website-files.com/6889473510b50328dbb70ae6/6a3a9a489e1797f1e0665bbe_d5622abab0729b05479a1127780e0fc2_tag_img_catch-up.png?_a=BACMTiAE)  
*出典：[Claude Tag プロダクトページ](https://claude.com/product/tag)*

### バグ修正とdraft PR作成

バグ報告のスレッドで依頼すると、再現・原因調査をしたうえで、Claude GitHub App経由でdraft PRを開き、そのリンクをスレッドに貼ってくれます。CIがグリーンになるまで追いかける、という使い方もできます。

![バグを調査してdraft PRを開き、スレッドにリンクを返すClaude Tag](https://res.cloudinary.com/zenn/image/fetch/s--aI8mpGec--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://cdn.prod.website-files.com/6889473510b50328dbb70ae6/6a3a9a4d1d6688235b6da910_59b3eb2c3ea8efd3531293b45ff1c524_tag_img_draft-prs.png?_a=BACMTiAE)  
*出典：[Claude Tag プロダクトページ](https://claude.com/product/tag)*

### データを聞いてその場で数字を出す

データウェアハウスを接続したチャンネルなら、自然文で質問するだけでSQLを実行し、数字やチャートをスレッドに返してくれます。アナリストに依頼を投げて待つ、という往復が消えます。

![質問を受けてウェアハウスに問い合わせ、数字を返すClaude Tag](https://res.cloudinary.com/zenn/image/fetch/s--7a7AgPCA--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://cdn.prod.website-files.com/6889473510b50328dbb70ae6/6a3a9a483452abcaa293aa7a_e4851576863e95688132488f21e5a9b4_tag_img_pull-numbers.png?_a=BACMTiAE)  
*出典：[Claude Tag プロダクトページ](https://claude.com/product/tag)*

### チャンネル監視とアラート

ルーチンとして設定しておくと、`@Claude` は依頼を待たずに動きます。静かになったスレッドを掘り起こしたり、デプロイが反映されたら投稿したり、判断が必要な項目を担当者にタグ付けして知らせたりします。

![チャンネルを監視し、必要な相手をタグ付けして知らせるClaude Tag](https://res.cloudinary.com/zenn/image/fetch/s--zd6gnqyJ--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_1200/https://cdn.prod.website-files.com/6889473510b50328dbb70ae6/6a3a9a4dfa9608d0d72727df_2e8c5c719077802290648adb0ff0bbc7_tag_img_monitor-channels.png?_a=BACMTiAE)  
*出典：[Claude Tag プロダクトページ](https://claude.com/product/tag)*

どのスクリーンショットでも共通してるのは、依頼・作業・結果が全部同じSlackスレッドに残ってることです。これがClaude Tagの一番の特徴で、チーム全員が同じ場所で経過を追えます。

---

## 管理者のセットアップ

Claude Tagの初期セットアップは、Claude組織のOwnerが `claude.ai/admin-settings/claude-tag` から行います。

出典：[Set up Claude Tag](https://claude.com/docs/claude-tag/admins/setup-overview)

公式ドキュメント上の流れは次の4ステップです。

```
1. SlackワークスペースをClaude組織にペアリングする
2. Access bundleを作り、必要なツール接続を追加する
3. 月次の支出上限を設定する
4. 内容を確認してClaude Tagを有効化する
```

セットアップ前に必要なものは、Claude組織のOwner権限、Slackワークスペース管理者、Teamプランの場合は利用クレジット、テスト用チャンネルです。Slack側では `@Claude connect` を実行し、15分有効なペアリングコードをClaude管理画面に貼ります。

Access bundleは、Claude Tagが使う認証情報、リポジトリ許可、プラグイン、指示をまとめた単位です。GitHubは初期ダイアログ内の一般アプリ接続とは別にClaude GitHub App経由で設定します。

セットアップ後の検証として、公式ドキュメントではパイロットチャンネルで次を実行することが案内されています。

```
/invite @Claude
@Claude summarize this channel
```

このテストは外部接続を使わないため、Slackアプリのインストール、ワークスペースのペアリング、チャンネルでの有効化を切り分けて確認できます。

---

## 課金と制限

Claude Tagは消費量ベースです。チャンネルやスレッドでの利用は、個人席やAPIクレジットではなく、組織のusage balanceから消費されます。DMではユーザー個人のClaudeアカウントで動くため、組織の支出上限の対象外です。

出典：[Billing and spend limits](https://claude.com/docs/claude-tag/overview#billing-and-spend-limits)

管理者は利用状況をClaude Consoleで確認でき、チャンネル別の内訳も見られます。支出上限はOwnerが設定します。Teamプランではusage creditsを購入し、Enterpriseプランでは請求書ベースになります。

導入時は、最初から全チャンネルへ広げるより、パイロットチャンネルで実際の作業量と消費を見てから広げる方がよさそうです。

---

## Claude CodeやCoworkとの違い

公式ドキュメントでは、Claude Tag、Cowork、Claude Codeの違いを次のように整理しています。

出典：[How Claude Tag differs from Cowork and Claude Code](https://claude.com/docs/claude-tag/concepts/how-it-works#how-claude-tag-differs-from-cowork-and-claude-code)

|  | Claude Tag | Cowork | Claude Code |
| --- | --- | --- | --- |
| 場所 | Slackチャンネル | claude.aiのチャット | ターミナルやIDE |
| 権限 | 管理者がチャンネルに設定したチーム権限 | 個人のコネクタ | 個人のローカル環境と認証情報 |
| 可視性 | チャンネル全員 | 自分だけ | 自分だけ |
| 向いている作業 | チームで見たい共有作業 | 個人の調査・文章作成 | 自分のcheckoutでの実装 |

Claude Tagは、個人が強いエージェントを使うためのものではなく、チームが同じ文脈を見ながらエージェントへ作業を委任するためのものです。

---

## 導入時の注意点

Claude Tagを導入するときは、次の観点を最初に決めると混乱が少ないです。

### 1. どのチャンネルに何を許すか

アクセス権はチャンネルに付きます。最初は「全社デフォルトで広く許可」よりも、用途ごとに小さく切った方が監査しやすいです。

例：

* `#eng-bugs`：GitHub、Sentry、Datadog
* `#data-questions`：SnowflakeまたはBigQuery
* `#sales-ops`：Salesforce、HubSpot
* `#project-status`：Issue Tracker、Drive

### 2. サービスアカウントを人間から分ける

Claude Tagの操作はClaude用アカウントに帰属します。個人アカウントを流用すると、監査、退職者対応、権限剥奪が難しくなります。

### 3. 最初の成功パターンを固定する

いきなり「何でもやって」ではなく、繰り返し使える依頼をチャンネルごとに作る方が効果が見えます。

```
@Claude このスレッドを決定事項、未決事項、担当者、期限に分けて要約して。
```

```
@Claude このバグ報告を再現手順、期待結果、実際結果、必要ログに整理して、Linearチケット案を作って。
```

```
@Claude 毎週月曜9時JSTに、このチャンネルの未完了スレッドとリンクされたPRを確認し、ブロッカーだけ表で出して。
```

### 4. メモリを定期的に棚卸しする

チャンネルメモリは便利ですが、古いリポジトリ名、古い担当者、古い運用が残ると誤動作の原因になります。`@Claude what do you remember about this channel?` を定期的に実行し、古い内容を削除・更新する運用が必要です。

---

## まとめ

Claude Tagは、ClaudeをSlackに置くだけの機能ではありません。チャンネル単位の権限、サービスアカウント、Agent Proxy、一時サンドボックス、チャンネルメモリ、ルーチンを組み合わせ、Claudeをチームの作業場所に参加させる仕組みです。

Karpathyが言うように、これはLLM UI/UXの重要な転換に見えます。WebサイトやローカルアプリとしてのLLMから、組織の会話、ツール、実行環境、メモリを持つ非同期のチームメンバー型エージェントへ移る流れです。

ただし、価値が出るほど権限設計も重要になります。最初は小さなチャンネル、小さなAccess bundle、低リスクな定型作業から始め、監査ログと支出を見ながら広げるのが現実的です。

Claude Tagを理解するうえでの一文は、これだと思います。

> Claude Tagは、Slackに入ったチャットボットではなく、Slackを入口にして動くチームスコープのエージェントである。
