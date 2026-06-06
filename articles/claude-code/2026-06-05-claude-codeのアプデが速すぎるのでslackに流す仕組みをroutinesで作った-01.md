---
id: "2026-06-05-claude-codeのアプデが速すぎるのでslackに流す仕組みをroutinesで作った-01"
title: "Claude Codeのアプデが速すぎるのでSlackに流す仕組みをRoutinesで作った"
url: "https://zenn.dev/uchunanora/articles/routines-claude-update"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "API", "zenn"]
date_published: "2026-06-05"
date_collected: "2026-06-06"
summary_by: "auto-rss"
query: ""
---

Claude Codeのアップデート追えてますか？  
私は追えてません！（アプデ速すぎだろ...）

そこで、**Claude Code Routines**を使ってClaude Codeのアップデート情報を良い感じに翻訳・要約してSlackに流す仕組みを作りました。

* 毎日1回定期実行
* GithubのReleases APIから直近24時間のリリースを取得
* アップデート内容を要約してSlackに通知

本当はアップデートを検知したら即座に通知したいですが、今回はとりあえず定期実行でやってみました。

## Claude Code Routines

ざっくり言うと、Claude Codeの設定をAnthropicのクラウド上で自動実行する仕組みです。  
トリガーは3種類あります。

* Schedule: 定期実行（hourly / daily / weekly）
* API: 専用エンドポイントにリクエストして起動
* Github: リポジトリのイベントに反応

今回はScheduleトリガーを使って、毎日1回実行するように設定します。

<https://code.claude.com/docs/en/routines>

## 全体の流れ

1. リリースを取得するコマンドを固める
2. Routineを作成し、クラウド環境の設定
3. プロンプトを作成
4. dailyトリガーを設定して、動作確認

### 1. リリースの取得

GithubのReleases APIを素直に叩きました。  
Githubの未認証リクエストの上限はIPあたり60回/時なのですが、RoutinesはAnthropicのクラウド上で動くので、IPが共有されているからなのか、認証なしだと403を引くことが多々ありました。  
なので、認証トークンを環境変数で渡す形にしました。Publicリポジトリを読むだけなので、スコープなしのトークンで十分です。

```
curl -s -H "Authorization: Bearer $GH_TOKEN" \
"https://api.github.com/repos/anthropics/claude-code/releases?per_page=10"
```

レスポンスが巨大なので、これをそのままモデルに渡すのはコンテキストの無駄なので、必要な項目だけ・条件を絞ったうえで取り出します。

```
curl -s -H "Authorization: Bearer $GH_TOKEN" \
"https://api.github.com/repos/anthropics/claude-code/releases?per_page=10" \
| jq '[ .[]
| select(.draft == false and .prerelease == false)
| select((.published_at | fromdateiso8601) >= (now - 86400))
| {tag: .tag_name, published_at, url: .html_url, body} ]
| sort_by(.published_at)'
```

* `jq`で、ドラフト・プレリリースを除外して、直近24時間のリリースだけに絞っています。
* 残すのは tag / published\_at / url / body の4つだけ

結果はこんな最小限の配列になります。

```
[
  {
    "tag": "v2.1.162",
    "published_at": "2026-06-03T21:31:35Z",
    "url": "https://github.com/anthropics/claude-code/releases/tag/v2.1.162",
    "body": "## What's changed\n- ..."
  }
]
```

### 2. Routineの作成と環境変数の設定

[Routinesのダッシュボード](https://claude.ai/code/routines)から新しいRoutineを作成します。

![Routinesダッシュボード](https://static.zenn.studio/user-upload/a6775b309653-20260605.png)

作成したら「指示」の右下から環境を選択できるので、設定ボタンを押下するとクラウド環境を設定することができます。

![新しいRoutine](https://static.zenn.studio/user-upload/a910e3e5f524-20260605.png)

![クラウド環境の設定](https://static.zenn.studio/user-upload/f3e22e1e2eee-20260605.png)

ネットワークアクセスは、GithubのAPIとSlackのWebhookに対して許可を出しておきます。

```
api.github.com
hooks.slack.com
```

また、環境変数も設定しておきます。

```
GH_TOKEN=github_pat_xxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
```

### 3. プロンプトの作成

モデルはHaiku4.5を指定しました。

プロンプトは、先ほどのコマンドで取得したリリース情報を要約してSlackに送る内容を書きます。

いまのところこんな感じで様子見です。

```
Claude Code リリース通知ジョブ（定期実行）

このルーティンは、anthropics/claude-code の新しいリリースを毎日チェックし、
あれば Slack に通知する定期ジョブです。GH_TOKEN と SLACK_WEBHOOK_URL は
このルーティンの環境変数として設定済みで、下記コマンドがそのまま参照します。
判断に必要な情報はすべて以下に含まれているので、上から順に実行してください。

手順：
1. 以下を実行して、直近24時間の正式リリースだけを取得：
curl -s -H "Authorization: Bearer $GH_TOKEN" \
"https://api.github.com/repos/anthropics/claude-code/releases?per_page=5" \
| jq '[ .[]
| select(.draft == false and .prerelease == false)
| select((.published_at | fromdateiso8601) >= (now - 86400))
| {tag: .tag_name, published_at, url: .html_url, body} ]
| sort_by(.published_at)'

2. curl失敗などエラーが出た場合、「取得失敗のためスキップ」とだけ記録して終了。

3. 配列が空の場合、「直近24時間に新規リリースなし」と記録して終了。

4. 配列が1件以上なら、配列の順（古い→新しい）に、bodyを箇条書きで要約（特に新機能）してメッセージ本文（日本語）を作成してSlackに送信。
メッセージ：
Claude Code <tag1> 🚀
<bodyの要約1>
Claude Code <tag2> 🚀
<bodyの要約2>

送信は jq で JSON を組み立ててエスケープを安全にすること:

jq -n --arg text "$MSG" '{text: $text}' \
| curl -s -X POST -H 'Content-Type: application/json' \
-d @- "$SLACK_WEBHOOK_URL"

完了条件: 上記を実行し終えること。途中で人間に問い合わせないこと。
```

プロンプトを作成しているとき、何度か実行すると、手順通り最後まで実行されず、質問をしてきて止まっていることが多々ありました。  
なので、これは定期ジョブであり、途中で人間に問い合わせることがないように設計することがポイントです。

### 4. トリガーの設定と動作確認

最後にScheduleトリガーを設定して、作成しましょう。

![Scheduleトリガー](https://static.zenn.studio/user-upload/46709b2aa5c6-20260605.png)

Routineができあがるので選択して、右上の「今すぐ実行」をクリックして動作確認を行います。

正常に動けば、Slackに要約されたリリース情報が流れてくるはずです。

途中でエラーが起きたら、プロンプトを修正してみてください。

![](https://static.zenn.studio/user-upload/3d6fcd22b1f5-20260605.png)

これで、Claude Codeのアップデートを追うのがちょっぴり楽になりました。

![](https://static.zenn.studio/user-upload/f6c6eff2c360-20260605.png)
