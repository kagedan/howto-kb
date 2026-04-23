---
id: "2026-04-07-claushに長時間タスクを任せてslack通知を受け取る方法-01"
title: "Claushに長時間タスクを任せてSlack通知を受け取る方法"
url: "https://qiita.com/claush/items/94ff55bcf93e69000ed6"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "qiita"]
date_published: "2026-04-07"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

## Claushとは

**Claush**は、iPhoneからVPS上のClaude CodeをSSH経由で操作するiOSアプリです。チャット感覚でClaude Codeに指示を出せるほか、アプリを閉じてもVPS上で処理が継続するバックグラウンド実行に対応しています。

## はじめに

`docker compose build` を実行して、ターミナルの前でぼーっと待った経験はないだろうか。

ビルドが終わるまで5分、10分、あるいはそれ以上。その間、スマホでニュースを眺めたり、コーヒーを飲んだり——「終わったかな」と何度も画面を確認する、あの無駄な時間。

この記事では、その待ち時間を完全になくす方法を紹介する。

Claude Codeに「docker compose buildして、終わったらSlackに通知して」と一言伝えるだけで、あとはiPhoneをポケットに入れて別のことができる。通知が来た瞬間に作業を再開すればいい。

### 完成するとこうなる

```
ユーザー: docker compose build して、終わったらSlackに通知して

Claude: 了解しました。docker compose build を開始します。完了後にSlackへ通知します。
        （VPS上でビルドが実行される）

↓ 数分〜数十分後、Slackに通知が届く ↓

[Slack通知]
✅ docker compose build 完了しました
ビルド時間: 8分23秒
```

iPhoneをポケットにしまって、美容室でカラー剤を塗ってもらっている間でも——通知が来るまで完全に手を離せる。

---

## 前提

この記事は以下の環境が設定済みであることを前提とする。

* VPS（Ubuntu/Debian推奨）
* Claude Code（VPS上にインストール済み）
* Claushアプリ（iPhoneにインストール済み）

未設定の場合は先にこちらを参照してほしい。

---

## Slack通知の設定

### 1. Slack Incoming Webhookを作成する

まず、SlackのWebhook URLを取得する。

**手順:**

1. [Slack API: Your Apps](https://api.slack.com/apps) にアクセスする
2. 「Create New App」→「From scratch」を選択する
3. App Nameを入力し（例: `claude-code-notify`）、ワークスペースを選択する
4. 左メニューの「Incoming Webhooks」をクリックする
5. 「Activate Incoming Webhooks」をオンにする
6. 「Add New Webhook to Workspace」をクリックする
7. 通知を送りたいチャンネルを選択して「許可する」をクリックする
8. 表示されたWebhook URL（`https://hooks.slack.com/services/...`）をコピーする

### 2. 動作確認

curlコマンドでWebhookが正しく動作するか確認する。

```
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"テスト通知です"}' \
  "https://hooks.slack.com/services/YOUR_TEAM_ID/YOUR_CHANNEL_ID/YOUR_WEBHOOK_TOKEN"
```

Slackに「テスト通知です」が届けば設定成功だ。

### 3. Claude CodeのMCPに通知プラグインを設定する

Claude CodeはMCP（Model Context Protocol）という仕組みでツールを拡張できる。Slack通知もMCPサーバーとして設定できる。

**方法A: MCPのnotifyサーバーを使う（推奨）**

`~/.claush/notify-config.json` に以下の形式でWebhook URLを保存しておくと、Claushがネイティブに通知機能を使える。

```
mkdir -p ~/.claush
cat > ~/.claush/notify-config.json << 'EOF'
{
  "default_platform": "slack",
  "slack": {
    "webhookUrl": "https://hooks.slack.com/services/YOUR_TEAM_ID/YOUR_CHANNEL_ID/YOUR_WEBHOOK_TOKEN"
  }
}
EOF
```

**方法B: 環境変数にWebhook URLを保存する**

シンプルに環境変数で管理する方法もある。

```
# .bashrc または .zshrc に追記
echo 'export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."' >> ~/.bashrc
source ~/.bashrc
```

Claude Codeへの指示内でこの環境変数を参照させることができる。

```
ユーザー: npm install して全テスト走らせて、結果を $SLACK_WEBHOOK_URL に通知して
```

**方法C: Claude Code内でcurlを直接実行させる**

最もシンプルな方法。Webhook URLをClaude Codeのプロンプトに含めるか、「Webhookのファイルから読んで通知して」と伝えるだけでも動作する。

```
# Webhook URLをファイルに保存
echo "https://hooks.slack.com/services/..." > ~/.slack-webhook
chmod 600 ~/.slack-webhook
```

```
ユーザー: docker compose build して、終わったら ~/.slack-webhook のURLにSlack通知して
```

---

## 実際の使い方

設定が完了したら、あとはClaushから自然言語で指示を出すだけだ。

### ケース1: Dockerビルドの完了通知

```
docker compose build して、終わったらSlackに「ビルド完了」と通知して
```

Claude Codeは以下を自動で実行する。

1. `docker compose build` を実行する
2. ビルドの成功・失敗を確認する
3. 結果をSlackに送信する

ビルド中はiPhoneをポケットにしまって、別の作業ができる。

---

### ケース2: npm installとテスト実行

```
npm install して全テスト走らせて、テストの結果（何件通過・何件失敗）をSlackに通知して
```

```
→ Slack通知:
✅ テスト完了
テスト結果: 142 passed, 0 failed
所要時間: 2分15秒
```

---

### ケース3: デプロイの成功・失敗通知

```
git pull して docker compose build して compose up -d して、
成功したら「デプロイ完了」、失敗したらエラー内容と一緒に「デプロイ失敗」をSlackに通知して
```

デプロイが成功した場合:

```
→ Slack通知:
✅ デプロイ完了
ブランチ: main (a3f8c12)
コンテナ起動: 3/3
```

デプロイが失敗した場合:

```
→ Slack通知:
❌ デプロイ失敗
エラー: "Cannot find module './config'"
ステップ: docker compose build (app)
```

---

### ケース4: 依存パッケージの更新チェック

```
npm outdated を実行して、メジャーバージョンアップが必要なパッケージがあれば一覧をSlackに送って
```

---

### ケース5: バックアップと通知

```
MySQLのデータをダンプして、~/backups/に日付付きで保存して、完了したらSlackに通知して
```

---

### 通知内容をカスタマイズする

指示の仕方で通知の内容を細かく制御できる。

```
# シンプルに完了だけ通知
docker compose build して終わったら通知して

# 詳細情報を含める
docker compose build して、ビルド時間・イメージサイズ・エラーがあればエラー内容もSlackに通知して

# 失敗時のみ通知
テストを走らせて、失敗したときだけSlackに通知して（成功時は不要）

# 複数ステップを一括実行
git pull && npm install && npm test して、各ステップの結果をまとめてSlackに通知して
```

---

## バックグラウンド処理の仕組み

「iPhoneのアプリを閉じても処理が続く」という動作を疑問に思う人もいるかもしれない。仕組みを説明する。

### 処理はVPS上で動いている

Claushはあくまで「VPSへの操作インターフェース」だ。`docker compose build` などのコマンドは、すべてVPS（サーバー）上で実行されている。

```
[iPhone / Claushアプリ]
    ↓ 指示を送信
[VPS上のClaude Code]
    ↓ コマンドを実行
[VPS上のプロセス: docker build]
    ↓ 完了後
[Slack API]
    ↓ 通知
[iPhoneのSlack]
```

iPhoneはあくまで「指示を送る端末」であり、「処理を実行する環境」ではない。そのため、iPhoneをスリープしてもアプリを閉じても、VPS上の処理は継続する。

### iPhoneのスリープ・アプリ切り替えの影響がない理由

| よくある誤解 | 実際の動作 |
| --- | --- |
| アプリを閉じると処理が止まる | VPS上の処理は継続する |
| iPhoneがスリープすると切断される | VPSとの接続はサーバー側で管理されている |
| バックグラウンドで通信できない | 通知はSlack経由なのでiOS通知として届く |

Claushアプリはセッション管理をサーバー側で行う設計になっている。これにより、iOSのバックグラウンド制限の影響を受けない。

### tmuxとの組み合わせ（より確実な方法）

さらに確実にしたい場合は、VPS側でtmuxセッション内でClaude Codeを動かすことができる。

```
# tmuxを使ってClaude Codeを起動
tmux new -s claude-session
claude

# セッションをデタッチ: Ctrl+B → D
# SSHが切断されてもClaude Codeは動き続ける
```

ただし、Claushを通常通り使っている場合はtmuxは必須ではない。

---

## 活用シーン

### 美容室でカラー中にデプロイ

美容室でカラー剤を塗ってもらう前に指示を出す。

```
今日のコミット全部レビューして問題なければmainにマージして、
ステージング環境にデプロイして、完了したらSlackに通知して
```

カラーが仕上がる1〜2時間後、通知が届いている。椅子から立ち上がる頃にはデプロイが完了している。

---

### 外出先でDockerビルド

電車に乗る前に指示を出す。

```
docker compose build -no-cache して、
成功したらDockerHub(myaccount/myapp:latest)にpushして、
終わったらSlackに通知して
```

目的地に着く頃には、ビルドとpushが終わっている。

---

### 就寝中にCI/CDを走らせて朝に結果確認

寝る前にCI/CDパイプラインを起動する。

```
全テスト走らせて、カバレッジレポートを生成して、
カバレッジが80%を下回っているファイルがあればリストアップして、
結果全部をSlackに通知して
```

翌朝、スマホを見るとSlackに詳細なテスト結果が届いている。コーヒーを飲みながらレポートを確認できる。

---

### 「任せながら別のことをする」開発スタイル

従来の開発では、長時間タスクの間は「待ち」が発生していた。

```
従来のワークフロー:
[コマンド実行] → [待つ] → [結果確認] → [次のコマンド] → [待つ] ...
```

Claushと通知を組み合わせると、待ちがなくなる。

```
新しいワークフロー:
[指示を出す] → [別のことをする] → [通知を受け取る] → [次の指示を出す] ...
```

並列で動かすこともできる。

```
# 複数のプロジェクトを同時に進める
プロジェクトAのビルドを開始して通知して（Claushでプロジェクトタブ1から）
プロジェクトBのテストを開始して通知して（Claushでプロジェクトタブ2から）
```

時間の使い方が根本的に変わる。

---

## まとめ

| 設定内容 | 詳細 |
| --- | --- |
| Slack Incoming Webhook | Slackのアプリページで数分で作成できる |
| Claude CodeへのWebhook設定 | `~/.claush/notify-config.json` に保存するか環境変数に設定 |
| 指示の出し方 | 「〜して、終わったらSlackに通知して」の一言でOK |
| バックグラウンド動作 | VPS上で処理が実行されるため、iPhone側の状態に影響されない |

「docker compose buildの間ずっと待っていた」時代は終わった。長時間タスクはClaude Codeに任せて、自分は別のことをする——この開発スタイルが、スキマ時間を開発時間に変える。

---

## 関連記事

**Claushアプリ**
