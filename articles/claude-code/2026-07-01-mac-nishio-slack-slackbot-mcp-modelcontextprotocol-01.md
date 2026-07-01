---
id: "2026-07-01-mac-nishio-slack-slackbot-mcp-modelcontextprotocol-01"
title: "@Mac_nishio: #Slack #Slackbot #MCP #ModelContextProtocol #AI #初心者向け #Slac"
url: "https://x.com/Mac_nishio/status/2072249394800509254"
source: "x"
category: "claude-code"
tags: ["MCP", "API", "x"]
date_published: "2026-07-01"
date_collected: "2026-07-02"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

#Slack #Slackbot #MCP #ModelContextProtocol #AI #初心者向け #SlackAPI
Slackbot に MCP を入れる方法——公式マニュアルに書いてない「3つの登場人物」
Slack の公式ドキュメント「Connecting an MCP server to the Slackbot MCP Client」を読んで、MCP を Slackbot から使おうとした。

手順は書いてある。でも 初心者向けに一番大事なことが書いてない と感じた。

公式マニュアルで足りないこと
マニュアルはだいたい次の流れ：

Slack App を作る
MCP Servers に URL を登録
ワークスペースにインストール
Slackbot から使う
ここまで。でも多くの人がこう思う：

「App を作ったから、その App に DM すればいいの？」

違います。

作った App は、多くの場合 会話相手ではない。
MCP サーバーの住所を Slack に教えるための「登録用の箱」 に近い。
実際に話すのは Slackbot（Slack 純正の AI）です。

この一点を理解しないと、設定画面を行き来しても「つながった気がしない」まま終わりやすい。

3つの登場人物（ここだけ覚えれば半分は解ける）

名前何か例えるなら
Slackbot
ユーザーが話す AI
フロントの受付
あなたの Slack App
MCP URL と権限を登録する単位
配線盤・名札
MCP サーバー
ツールを提供する HTTPS サーバー
実際の作業場
データの流れ：
あなた → Slackbot（会話）

↓
Slack が MCP を呼ぶ
↓
あなたの MCP サーバー（ツール実行）
App はこの図の 「Slack に URL を教える」 部分。App 自身が Slackbot の代わりに返事するわけではない。
手順（一般名で）

前提
MCP サーバーが HTTPS で公開されている

初回は動作確認用に no_auth でも可（本番は後で slack_identity_auth 等を検討）
Step 1: 開発者コンソールを開く
❌ ワークスペースの「インストールされたアプリ」管理画面
✅ https://t.co/jGG1Za666L

ここを間違える人が多い。
Step 2: Slack App を新規作成

Create New App → From scratch

名前例: My MCP Connector

使うワークスペースを選択
※ 既存の通知用 bot App に載せても動くが、MCP 専用の新規 App の方が分かりやすい。
Step 3: MCP サーバーを登録
左メニュー Features → MCP Servers（無い場合は機能未提供のワークスペース）

Get Started

入力例:
項目例
Name
acme-tools（Slackbot のトグルに出る名前）
URL
https://t.co/jmT5ttFcbR
Auth Type
最初は No Auth
Save
mcp:connect スコープは自動で付く。
Step 4: ワークスペースにインストール
OAuth & Permissions

Install to Workspace（変更後は Reinstall）

権限を許可
Step 5: Slackbot に接続（ここが本番）
Slack で Slackbot の DM を開く（笑顔アイコン。自作 App の DM ではない）
入力欄上の Apps をクリック

一覧の acme-tools（Step 3 の Name）のトグルを ON
初回は許可ダイアログが出ることがある
Step 6: 動作確認
Slackbot に送る：
acme-tools で使えるツールを教えて

英語なら：

What tools are available from acme-tools?
ツール一覧が返れば成功。

Step 7: 失敗したら Logs
https://t.co/c8Gds1u6o6 → 対象 App → MCP Servers → Logs

initialize や tools/list の HTTP ステータスを確認。ここに原因が出ることが多い。

よくあるつまずき

1. /mcp が 400 missing_user_context

MCP サーバーが tenant/user 認証を要求していると、Slackbot からはそのまま繋がらない。
対処の例：

サーバーが用意している セッション付き URL を使う

またはサーバー側で Slack 向
