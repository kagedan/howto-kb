---
id: "2026-05-04-minervacosmetic-mcpサーバーを自分で立てるのにコードを1行も書かなかった設定ファイ-01"
title: "@minervacosmetic: MCPサーバーを自分で立てるのに、コードを1行も書かなかった。設定ファイルにコピペするだけで動いた。 これを知っている"
url: "https://x.com/minervacosmetic/status/2051135372516896824"
source: "x"
category: "ai-workflow"
tags: ["MCP", "GPT", "x"]
date_published: "2026-05-04"
date_collected: "2026-05-05"
summary_by: "auto-x"
---

MCPサーバーを自分で立てるのに、コードを1行も書かなかった。設定ファイルにコピペするだけで動いた。

これを知っているかどうかで、Claude・Cursor・Windsurf などのAIツールから引き出せる作業量が文字通り変わる。

---

MCPとは何かを一言で言うと、「AIに外部ツールを操作させるための接続口」だ。

通常のChatGPTやClaudeは、会話の中だけで完結する。しかしMCPサーバーを通じると、ファイルの読み書き・ブラウザ操作・データベースへのアクセスをAIが直接実行できる。

コピペで動くMCPサーバーは、GitHubに300以上すでに公開されている。

---

【実際の手順】

1. `npx` が使える環境を確認（Node.js が入っていれば即OK）

2. Claude Desktop の設定ファイル（`claude_desktop_config.json`）を開く

3. 以下をコピペして保存する

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/自分のユーザー名/Desktop"
      ]
    }
  }
}
```

4. Claude Desktop を再起動する

これだけで、ClaudeがデスクトップのファイルをAIが直接読み書きできる状態になる。所要時間は10分かからない。

---

これができると何が変わるか。

毎日30分かけていたファイル整理・命名・仕分けをClaudeに丸投げできる。週5日換算で月10時間以上の削減になる計算だ。

さらに応用すれば、Slack・Notion・Google Drive・GitHubへの接続も同じ構造で追加できる。設定ファイルに1ブロック足すだけで、AIの操作範囲が1つずつ広がっていく。

---

MCPサーバーの一覧は「awesome-mcp-servers」でGitHub検索すると出てくる。スター数順に並べれば、実用度の高いものから確認できる。

AIをチャットで使い続けている間は、この差は見えない。ファイル・ブラウザ・DBを動かせるAIと、会話だけのAIとでは、自動化できる工程数がそもそも違う。

ファイルシステム以外でよく使われるのは、`@modelcontextprotocol/server-brave-search`（Web検索）と`@modelcontextprotocol/server-github`（リポジトリ操作）の2つだ。どちらも設定ファイルに同じ形式でブロックを追加するだけで動く。複数のMCPサーバーを同時に有効化できるので、接続先を増やすほど自動化できる範囲が広がる。

「Node.jsが入っていない」という場合の詰まりポイントは一点だけだった。公式サイト（https://t.co/KEitSNvROB）からLTS版をインストールしてターミナルで`node -v`が返れば、npxも同時に使える状態になっている。Windowsの場合は設定ファイルのパス区切りを`\\`にする必要があるが、それ以外の手順は同一だ。

まず試すなら、filesystemサーバーをデスクトップに向けてClaudeに「フォルダ内のファイル名を一覧にして日付順に並べ直して」と指示するだけでいい。コードゼロで自動整理が動く状態を確認できる。これを起点に接続先を1ブロックずつ足していくのが、最短で自動化範囲を広げる順序だと思う。
