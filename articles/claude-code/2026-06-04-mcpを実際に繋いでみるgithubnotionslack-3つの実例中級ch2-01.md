---
id: "2026-06-04-mcpを実際に繋いでみるgithubnotionslack-3つの実例中級ch2-01"
title: "# MCPを実際に繋いでみる——GitHub・Notion・Slack 3つの実例【中級Ch2】"
url: "https://zenn.dev/shun_producer/articles/fc424bd460dd2f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "zenn"]
date_published: "2026-06-04"
date_collected: "2026-06-05"
summary_by: "auto-rss"
query: ""
---

前章でMCPの正体——「Claudeを外部サービスに繋ぐ規格」——は理解できた。この章では実際の接続手順を、よく使うサービス別に解説する。

やることはシンプルだ。**設定ファイルに数行書いて、Claude Codeを再起動するだけ**。一緒にやってみよう。

## 設定ファイルはどこにあるのか

Claude CodeのMCP設定は、ホームディレクトリの中にあるJSONファイルに書く。

このファイルがない場合は、自分で作っていい。すでにある場合は、開いて中身を確認する。

参考までに、Claude Desktop（デスクトップアプリ版）の場合は別のパスになる：

```
~/Library/Application Support/Claude/claude_desktop_config.json  （Mac）
%APPDATA%\Claude\claude_desktop_config.json  （Windows）
```

CLI版（ターミナルで `claude` と打って使うやつ）とDesktop版は設定ファイルが別物だ。この記事はCLI版を前提に進める。

## 設定の基本構造

`settings.json` にMCPを足すときは、`mcpServers` というキーの中に各サービスを並べる。例で見てもらうのが早い。

```
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

各パーツの意味はこうだ。

* `mcpServers`：全MCPの親キー
* `github`：MCPの呼び名（自分でつけてOK）
* `command`：実行コマンド（だいたい `npx`）
* `args`：実行する具体的なパッケージと引数
* `env`：APIキーなど、そのMCPが必要とする秘密情報

複数のMCPを繋ぎたいときは、`mcpServers` の中に並べて書く。

```
{
  "mcpServers": {
    "github": { ... },
    "notion": { ... },
    "slack": { ... }
  }
}
```

## ケース1：GitHub MCP

リポジトリの一覧取得、Issue作成、PRレビューなどができるようになる。

**APIキー（Personal Access Token）の取り方**

1. GitHubにログイン
2. 右上のアイコン → Settings → Developer settings → Personal access tokens → Tokens (classic)
3. 「Generate new token」をクリック
4. スコープは最小限に。`repo` と `read:org` だけで多くの操作はカバーできる
5. 発行されたトークン（`ghp_...`）をコピー

トークンは**発行された瞬間しか表示されない**。コピーし忘れたら作り直し。

**settings.jsonに追加**

```
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

## ケース2：Notion MCP

NotionのページやDB操作ができるようになる。「議事録ページを読んで要点まとめて」「タスクDBに追加して」が一言で動く。

**APIキー（Integration Token）の取り方**

1. [Notion My integrations](https://www.notion.so/my-integrations) を開く
2. 「+ New integration」をクリック
3. 名前を付けて作成（例：`Claude Code`）
4. 発行された Internal Integration Token（`secret_...`）をコピー
5. **重要**：使いたいNotionページを開き、右上「・・・」→「Connections」から、いま作ったintegrationを追加する。これをしないとClaudeはページを読めない

**settings.jsonに追加**

```
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "NOTION_API_KEY": "secret_xxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

## ケース3：Slack MCP

Slackへのメッセージ送信や、チャンネルの履歴取得ができるようになる。

**Bot Tokenの取り方**

1. [Slack API: Your Apps](https://api.slack.com/apps) を開く
2. 「Create New App」→「From scratch」
3. App名とWorkspaceを設定
4. 左メニュー「OAuth & Permissions」を開く
5. **Bot Token Scopes** に以下を追加：
   * `chat:write`（メッセージ送信）
   * `channels:read`（チャンネル一覧）
   * `users:read`（ユーザー情報）
6. ページ上部の「Install to Workspace」をクリック
7. 発行された Bot User OAuth Token（`xoxb-...`）をコピー

**settings.jsonに追加**

```
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-xxxxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

## 接続確認

設定を書き終えたら、**Claude Codeを完全に再起動する**。`Ctrl+C` で抜けてから、もう一度 `claude` で立ち上げ直す。再読み込みされていなければ何も動かない。

起動したら、それぞれ試してみる。

* GitHub：「自分のリポジトリ一覧を見せて」
* Notion：「Notionのページ一覧を取得して」
* Slack：「Slackの #general に『テスト』と投稿して」

繋がっていれば、Claudeが実際に動いて結果を返してくれる。

## よくある失敗パターン3つ

**1. Claude Codeを再起動していない**

これが一番多い。設定ファイルは起動時にしか読まれない。書き換えたら必ず再起動する。

**2. APIキーの前後にスペースが混ざっている**

コピー＆ペーストで先頭や末尾に不要な空白が入ることがある。エディタの「不可視文字を表示」で確認するか、もう一度貼り直す。キー自体が無効になるわけではないので、何度でも貼り直していい。

**3. `npx` が使えない**

MCPの多くはNode.jsの `npx` コマンドで動く。ターミナルで `npx --version` と打ってバージョンが出るか確認。出なければ [Node.js公式](https://nodejs.org/) からインストールする。

## 最初は1つだけにしよう

「全部繋ぎたい」気持ちは抑えて、**最初は1つだけ**にする。理由は3つ。

1. **トラブルが起きたとき原因を絞れる**——どのMCPが悪さしているか一目でわかる
2. **設定ミスに気づきやすい**——確認するのは1ブロックだけで済む
3. **手応えが出やすい**——「これ本当に便利だ」と実感してから次に進める

一番よく使うサービス（毎日触っているもの）から入れて、安定運用できたら2つ目に進む。このペースが結局一番早い。

## 次のステップ

MCPで「外の世界」と繋がったら、次は「Claudeの中の機能」をもっと引き出す方法だ。次章では **Skills（スキル）** を扱う。`/seo-audit` みたいなスラッシュコマンド、見たことないだろうか。あれの正体と使い方を解説する。

---

*Claude Code初心者〜中級者向け教科書シリーズ / 中級編 Chapter 2*
