---
id: "2026-05-07-claudeをai秘書化したくてmcpでgoogle-calendarを繋いだら思ったよりハマった話-01"
title: "ClaudeをAI秘書化したくてMCPでGoogle Calendarを繋いだら、思ったよりハマった話"
url: "https://qiita.com/chara-gida/items/c6d98ffcbb7ae246ed2c"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-05-07"
date_collected: "2026-05-08"
summary_by: "auto-rss"
---

![ChatGPT Image 2026年5月7日 12_40_31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2748416/677f8a66-7dbd-46a6-a94c-5d39620728b0.png)

## はじめに

Claude Codeを開発用途で使う記事はかなり増えてきましたが、

「予定確認」
「空き時間確認」
「予定追加」

あたりまでできたら、かなり秘書っぽいのでは？

と思い、ClaudeのMCP連携を試しました。

最終的には以下を目指しています。

- Google Calendar → 予定確認 / 予定追加
- Slack → 通知確認
- 必要に応じて他ツール連携

今回はまず Google Calendar 連携まで実施しました。

---

# Claude単体でできること / MCPが必要なこと

Claude単体でも以下はかなり強いです。

- タスク整理
- 優先順位整理
- 今日やることの壁打ち

一方で、以下は外部連携が必要でした。

- 実際の予定確認
- 空き時間確認
- 予定追加

つまり、

**Claudeが知らない外部情報を取りに行く時にMCPが強い**

という学びがありました。

---

# 環境

- Mac
- Node.js

---

# 手順① Claude Desktopインストール

公式サイトからインストール
https://claude.com/download

Mac版をインストール
起動確認まで実施

---

# 手順② configファイル確認

Macの場合

````
open ~/Library/Application\ Support/Claude/
````

`claude_desktop_config.json`

が存在するか確認

---

# 手順③ Node確認

````
node -v
npm -v
````

---

# 手順④ Google Cloud設定

## Google Calendar API有効化

API を有効化

---

## OAuth設定

- アプリ作成
- OAuth設定
- credentials JSON取得

ここ、Google UIが少し変わっていて迷いました。

---

# 最初に試したMCPサーバー（失敗）

試したもの：

````
mcp-google-calendar
````

リポジトリ：
[mcp-google-calendar GitHub](https://qiita.com/?utm_source=chatgpt.com)

問題：

- schema error
- Claude側でtools認識されない

MCP Inspectorで確認したところ
tool schema validation errorが発生していました。

---

# 採用したMCPサーバー

最終的にこちらを利用。

````
@cocal/google-calendar-mcp
````

リポジトリ：
https://github.com/cocal/google-calendar-mcp
（※実際のURLに差し替え）

---

# 手順⑤ OAuth認証

````
npx @cocal/google-calendar-mcp auth
````

Google認証実施

token生成確認

````
ls ~/.config/google-calendar-mcp/
````

---

# 手順⑥ credentials配置

````
mkdir -p ~/mcp-secrets
mv ~/Downloads/client_secret*.json ~/mcp-secrets/credentials.json
````

---

# 手順⑦ Claude config設定

````
{
  "mcpServers": {
    "google-calendar": {
      "command": "npx",
      "args": [
        "-y",
        "@cocal/google-calendar-mcp"
      ],
      "env": {
        "GOOGLE_OAUTH_CREDENTIALS": "/Users/ユーザー名/mcp-secrets/credentials.json"
      }
    }
  }
}
````

ここで最初

`CREDENTIALS_PATH`

を使っていてハマりました。

正しくは

`GOOGLE_OAUTH_CREDENTIALS`

でした。

---

# Claude再起動

config変更後は

**Claude完全終了**

（Cmd + Q）

↓

再起動

が必要です。

---

# 実際にできたこと

Claudeに以下を依頼。

- 今日の予定を教えて
- 明日の予定を教えて
- 来週の予定を確認して
- 明日14時にMTG追加して

無事動作しました。

---

# MCP運用時の注意点

## Claudeを閉じるとMCPも停止する

基本的に

Claude起動
↓
MCP起動

Claude終了
↓
MCP終了

なので、毎回手動起動は不要です。

---

## token切れ時は再認証

````
npx @cocal/google-calendar-mcp auth
````

---

## MCP増やしすぎ注意

一気に増やすと切り分けが大変。

まずは1つずつがおすすめ。

---

# まとめ

最初は

「Google Tasksも必要か？」

と思っていましたが、

Claude単体でもタスク整理はかなり強い。

MCPの本当の価値は

**Claudeが知らない外部情報へのアクセス**

でした。
