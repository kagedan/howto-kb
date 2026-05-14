---
id: "2026-05-13-horomojisan-codexにchatwork連携を入れてみた-最初はchatwork-mcp-01"
title: "@horomojisan: CodexにChatwork連携を入れてみた。 最初はChatwork MCP ServerをCodexのマーケットプ"
url: "https://x.com/horomojisan/status/2054458805099114902"
source: "x"
category: "claude-code"
tags: ["MCP", "API", "x"]
date_published: "2026-05-13"
date_collected: "2026-05-14"
summary_by: "auto-x"
query: "MCP server 設定 OR MCP 活用事例 OR MCP 連携"
---

CodexにChatwork連携を入れてみた。

最初はChatwork MCP ServerをCodexのマーケットプレイスに追加しようとして失敗。
原因は、Chatwork公式のものが「Codex Plugin」ではなく、純粋なMCPサーバーだったこと。

そこで方針変更。

Codex CLIからMCPサーバーとして直接登録し、設定ファイルにChatwork APIトークンを渡す形にしたら動いた。

できたこと：
・Chatworkのルーム一覧取得
・直近メッセージの取得
・指定した相手へのテスト投稿

最後は、知り合い宛に
「これはCodexからChatwork MCP/API経由で投稿できるかの疎通確認です」
という説明付きメッセージを実際に送信。

つまり、CodexからChatworkを自然言語で操作する入口が作れた。

細かい手順はnoteにまとめます。
ポイントは「マーケットプレイス追加」ではなく「MCPサーバー直接登録」です。
