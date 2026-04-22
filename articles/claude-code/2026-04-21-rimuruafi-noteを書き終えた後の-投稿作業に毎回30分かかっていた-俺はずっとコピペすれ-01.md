---
id: "2026-04-21-rimuruafi-noteを書き終えた後の-投稿作業に毎回30分かかっていた-俺はずっとコピペすれ-01"
title: "@rimuruafi: noteを書き終えた後の 「投稿作業」に毎回30分かかっていた。 俺はずっとコピペすれば 早くなると思ってたが、 MC"
url: "https://x.com/rimuruafi/status/2046695491359121611"
source: "x"
category: "claude-code"
tags: ["MCP", "API", "Python", "x"]
date_published: "2026-04-21"
date_collected: "2026-04-22"
summary_by: "auto-x"
---

noteを書き終えた後の
「投稿作業」に毎回30分かかっていた。

俺はずっとコピペすれば
早くなると思ってたが、
MCPの設定を一度するだけで
投稿作業がゼロになった。

ちなみにこれ、
Claudeの裏技でもなんでもない。
ただの"外部ツール連携の正しい使い方"だ。

その設定がこれです。

====
【MCP×Hooks 自動投稿の設定】
↓コピーして自分の環境に合わせるだけ↓

【Step1：MCPサーバーの接続設定】
settings.jsonに追記：
{
  "mcpServers": {
    "googleDrive": {
      "command": "mcp-google-drive",
      "args": ["--auth", "oauth"]
    },
    "slack": {
      "command": "mcp-slack",
      "args": ["--token", "YOUR_TOKEN"]
    }
  }
}

【Step2：記事保存後の自動処理】
hooks.jsonに追記：
{
  "PostToolUse": {
    "trigger": "Write",
    "matcher": "article.md",
    "command": "python auto_publish.py"
  }
}

【Step3：自動投稿スクリプトの指示】
claude "auto_publish.pyを作って。
処理内容：
①article.mdをGoogle Driveに保存
②noteの下書きAPIに記事を送信
③Slackの#publishチャンネルに
　『記事の下書きが完成しました』と通知
④X投稿用テキストをtweet_draft.txtに保存"
====

これ、全員やるべきだ。

記事ファイルが保存された瞬間に
全部が自動で動き出す。

Google Drive保存→note下書き→Slack通知→
X投稿文保存まで、人間は何もしなくていい。

「記事を書いた後の投稿作業が面倒」
と言っ
