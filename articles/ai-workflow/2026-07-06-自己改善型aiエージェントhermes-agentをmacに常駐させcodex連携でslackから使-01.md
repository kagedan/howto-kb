---
id: "2026-07-06-自己改善型aiエージェントhermes-agentをmacに常駐させcodex連携でslackから使-01"
title: "自己改善型AIエージェント「Hermes Agent」をMacに常駐させ、Codex連携でSlackから使えるようにする"
url: "https://zenn.dev/nenene01/articles/hermes-agent-slack-codex-setup"
source: "zenn"
category: "ai-workflow"
tags: ["API", "AI-agent", "OpenAI", "GPT", "zenn"]
date_published: "2026-07-06"
date_collected: "2026-07-07"
summary_by: "auto-rss"
query: ""
---

## はじめに

AIエージェントは、モデル進化（いわば縦方向の強化）が盛んで「その瞬間の最適な回答」はどんどん賢くなっています。

ですが、横方向の発展も必要かと思います。プロジェクトに合わせて身近になったエージェントも最適化するべきだと思います。

最近、勢いのあるNous Researchが開発する [**Hermes Agent**](https://github.com/NousResearch/hermes-agent) をインストールし検証してみました。

簡単ですが、特徴は以下となります。

* セッションをまたいで記憶を永続化する
* 複雑なタスクを完了すると**スキルを自動生成**し、使いながら自己改善する
* 過去の会話を全文検索して想起する

という「ハーネス側の学習ループ」を売りにした、常駐型のパーソナルエージェントとなります。

![Hermes Agentとは](https://static.zenn.studio/user-upload/deployed-images/6c2c78c96da395a5fd2172b5.png?sha=176cc1edc965bb3fcc251d75e53b213db8e6b6e3)

まずはHermes AgentをMacにインストールし構築します。

1. **OpenAI Codex（ChatGPTサブスクリプション）とOAuth連携**
2. **Slackに接続してチャネルから起動**
3. **launchdでサービス化（常駐化）**

※途中でいくつか罠を踏みました。その回避方法も記載しました。

構築後、動作確認をしましたので**セッション・スキル・作業ログがどこに残るかの内部調査**を記載しました。

## 検証環境

* macOS (Apple Silicon)
* ChatGPT サブスクリプション（Codex CLI 認証済み）
* Slack ワークスペース（管理権限あり）

## 1. インストール

Github記載のワンライナーを実行し、zshに反映するだけ。

```
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.zshrc
hermes --version
# Hermes Agent v0.18.0 (2026.7.1)
```

## 2. Codex OAuth連携

### 罠①: デバイスコード認証がブロック

Hermesの標準手順では `hermes model` または以下でデバイスコードログインを行います。

```
hermes auth add openai-codex --type oauth
# → https://auth.openai.com/codex/device を開いてコードを入力
```

ところが私の環境では、ChatGPT側で次のエラーになりました。

> ChatGPT セキュリティ設定で Codex のデバイスコード認証を有効化したら、もう一度実行してください。

ChatGPTのセキュリティ設定でデバイスコード認証が無効化されているとこの方式は使えないです。

### 回避策: Codex CLIの認証情報をインポート

Hermesには **Codex CLIの** `~/.codex/auth.json` **を取り込む仕組み**が用意されているため、Codex CLIで `codex login` 済みなら、デバイスコード認証を有効化しなくても連携できました。

`hermes model` の対話フローで「Import these credentials?」に `y` と答えるだけです。

```
hermes auth status openai-codex
# openai-codex: logged in
```

デフォルトモデルを設定し確認します。

```
hermes config set model.default gpt-5.5
hermes -z "こんにちは。1+1の答えだけを一言で返して。"
# 2
```

## 3. Slack接続

HermesのSlack連携は **Socket Mode** で動きます。WebSocketの外向き接続のため、**ngrok等でポートを公開する必要はなかったです。**

### Slack Appの作成（マニフェスト一発）

必要なスコープ・イベント購読・スラッシュコマンドを全部入りにしたマニフェストをHermesが生成してくれます。

```
hermes slack manifest --write
# → ~/.hermes/slack-manifest.json
```

[api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From an app manifest** で、このJSONを貼り付けます。

### トークンを2つ取得

必要なトークンを回収します。

1. **App-Level Token（`xapp-`）**: Basic Information → App-Level Tokens → Generate。スコープに `connections:write` を付与

![App-Level Tokensセクション](https://static.zenn.studio/user-upload/deployed-images/15e7d096e5e35e9369961d1f.png?sha=d9c94081e032776c010512eda529aa750fa99c9b)

![connections:writeスコープを付けて生成](https://static.zenn.studio/user-upload/deployed-images/d6d6f521c165e70128770ffd.png?sha=ae791339eac4495e6d07f9e79bc3007a7f45c18a)

2. **Bot User OAuth Token（`xoxb-`）**: Install App → Install to Workspace 実行後に表示

取得したら `~/.hermes/.env` に設定します。

![.envへの設定](https://static.zenn.studio/user-upload/deployed-images/87aac3df1de40636ccc50dd6.png?sha=1f66e7a450bf13ea533091e64a0a1ea226409ba9)

```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_ALLOWED_USERS=UXXXXKKEJJD          # 自分のMember ID
SLACK_HOME_CHANNEL=C099C999END           # ホームチャネル
SLACK_ALLOWED_CHANNELS=C021C926EMD,C021Z683999
```

### ゲートウェイ起動

ログで接続を確認できます。

```
[Slack] Authenticated as @hermes in workspace my-workspace (team: T0XXXXXXXXX)
[Slack] Socket Mode connected (1 workspace(s))
✓ slack connected
```

### 罠②: 反応しない場合のチェックリスト

私が実際に踏んだ順に：

1. **ボットがチャネルに入っていない** — `/invite @hermes` したつもりが別チャネル（#general）でした。APIで確認すると良いです:

```
 curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
   "https://slack.com/api/conversations.info?channel=C021C926EMD" | jq '.channel.is_member'
```

2. **許可リスト未設定** — `SLACK_ALLOWED_USERS` / `SLACK_ALLOWED_CHANNELS` に含まれない送信者・チャネルは**サイレントに拒否**されます。エラーも返ってこないので気づきにくいです
3. **イベント未購読** — マニフェストを使わず手動作成した場合、`message.channels` / `app_mention` の購読漏れが定番の原因です

設定変更後は `.env` 再読み込みのためゲートウェイを再起動します。無事つながると：

```
[ねねね] こんにちは
→ こんにちは、ねねねさん！今日は何をお手伝いしましょうか？
```

## 4. launchdでサービス化

ここまでの起動はターミナル依存なので、Macを再起動すると止まります。サービス化コマンドが用意されています。

```
hermes gateway install
# Installing launchd service to: ~/Library/LaunchAgents/ai.hermes.gateway.plist
# ✓ Service installed and loaded!

hermes gateway status
# ✓ Gateway is supervised by launchd (PID 61658)
```

これで**ログイン時の自動起動＋クラッシュ時の自動再起動**が有効になり、Macが起きている限りSlackのHermesが応答し続けます。ログは `~/.hermes/logs/gateway.log` に出ます。

## A. セッション・スキル・作業ログはどこに残るのか

Slackで何往復かやり取りした後、`~/.hermes/` を調査しました。

### セッション: SQLite + 全文検索

* 会話の実体はSQLite(`~/.hermes/state.db`)。`messages`テーブルに role・本文・**ツール呼び出しのJSON**・reasoningがありました。
* 同DBに `messages_fts`（FTS5全文検索インデックス）がありました。「過去セッション横断検索」機能の実体だそうです。
* **Slackはスレッドごとに別セッション**になります（セッションキーに `thread_id` が含まれる）
* 一覧は `hermes sessions list`。セッションにはタイトルが自動で付いていました。

### スキル: 使用回数と自己改善回数がトラッキングされる

* スキル本体は `~/.hermes/skills/`（72個が同梱）
* `~/.hermes/skills/.usage.json` に各スキルの `use_count` / `view_count` / `**patch_count`（自己改善で書き換えた回数）\*\* が記録されます。「スキルが使いながら育つ」のを定量的に観察できる値がありました。スキルを使いつつ最適化するのは面白いですね。
* バックグラウンドのスキル整備は「curator」というプロセスが担い、`/curator` コマンドで操作できます。

### メモリ

`~/.hermes/memories/` は使い始めの時点では空でした。MEMORY.md / USER.md はエージェントが最初にメモリを書き込むタイミングで生成されるようです。人格定義の `SOUL.md` は雛形が最初から置かれます。

### 罠③: デフォルトの作業ディレクトリはホームそのもの

重要な発見として、**ゲートウェイ経由のHermesはホームディレクトリ（`~`）を作業スペースとして使います**。後述のインフォグラフィック生成では、成果物が `~/hermes_capabilities_infographic.html` と `~/infographic/` に直接作られていました。

つまりSlack経由のHermesはユーザー権限でファイル全域を読み書きできてしまうのです。危険コマンドは承認制（`/approve` / `/deny`）で守られていますが、閉じ込めたい場合は `config.yaml` の `terminal.cwd` 指定や、Dockerバックエンド（`terminal.backend: docker`）での隔離を検討すべきです。

## 6. 「生成 → 自分で見る → 直す」ループを観察する

まずSlackで「Hermesができることを教えて」と聞いてみると、スキル（`hermes-agent`）を自分で参照しながら回答してくれます。

![SlackでHermesに「できること」を質問](https://static.zenn.studio/user-upload/deployed-images/4cdcd12a3b4efd79e5b5014c.png?sha=5a9f47fdebde505ecc1e2c533dffe50938875ece)

続けて「できることをインフォグラフィックで回答して」と依頼したときの実行トレースを `state.db` の `tool_calls` から復元すると、こうなっていました。

```
skill_view: baoyu-infographic          # インフォグラフィック用スキルを読み込み
terminal:   PIL / matplotlib の有無を確認（→無し）
write_file: ~/hermes_capabilities_infographic.html
browser_navigate: file://~/hermes_capabilities_infographic.html
browser_vision: 「文字が見切れていないか確認して」   # 自分でスクショを撮って自己検証！
patch: ×13回                            # 見切れを修正
terminal:   qlmanage でプレビュー画像化
vision_analyze: レイアウト確認
write_file: SVG版に作り直し → rsvg-convert でPNG化
patch: ×3回
```

HTMLを書いたあと**ヘッドレスブラウザで自分の成果物を開き、visionで「文字が見切れていないか」を確認して13回パッチを当てる**という、人間のデザイナーのような自己修正ループが回っていました。数分後、Slackに完成品が投稿されました。

![Hermesが自律生成したインフォグラフィック](https://static.zenn.studio/user-upload/deployed-images/9eae8fc4b54439b3d967f977.png?sha=c1d7bdb18a24948e5d66e0040a3fe18a4dd954b4)

依頼はSlackの1メッセージだけです。スキル参照 → コード生成 → セルフレビュー → 修正 → 配信までが全自動でした。

## 運用メモ

* **コスト**: Codex連携ならChatGPTサブスクリプション内で動きます。常駐コストはPC1台の電気代のみ（アイドル時のHermesはほぼ無負荷）
* **セキュリティ**: `SLACK_ALLOWED_USERS` は必ず設定する。作業ディレクトリの隔離も検討（前述）
* **外部公開は不要**: Socket Modeのおかげで受信ポートを開ける必要なし。webhook型の連携が必要の場合は、Hermesに統合済みのCloudflare Tunnel検討。
* **常駐先の選択肢**: 中古Mac miniやVPSを検討しようと思います。安い中古のMac miniが欲しい。

## まとめ

* Hermes Agentは「モデルの賢さ」ではなく「**経験の蓄積と自己改善**」を軸にした常駐型エージェント
* Codex CLIの認証情報インポートでOAuth連携もできる
* Slack連携はSocket Modeなのでポート公開不要。
* `hermes gateway install` でlaunchd常駐化まで一発
* セッションはSQLite（FTS5付き）、スキルは使用回数・自己改善回数までトラッキングされ、学習ループの中身をファイルとして観察できる

「Slackに1行投げるとMac上のエージェントがツールを駆使して成果物を返してくる」体験は面白く、可能性を感じました。

Slackに常駐し共通のナレッジをメンバー間で利用でき、Slack上に証跡があり、追跡できるのも良いですね。
