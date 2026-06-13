---
id: "2026-06-12-claude-code-claude-desktopでgithub-mcp連携してみた-enterp-01"
title: "Claude Code + Claude DesktopでGitHub MCP連携してみた ─ enterprise policyエラーの解決まで"
url: "https://qiita.com/juyun2490/items/4698fe224f718c7e295f"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-06-12"
date_collected: "2026-06-13"
summary_by: "auto-rss"
query: ""
---

## はじめに

社内にClaude Codeを導入していく過程で、外部ツールとの連携を順番に試しています。

前回の記事はこちら：
👉 **[Claude Codeを社内導入する前に整理したこと ─ 外部ツール連携の安全性確認から実施記録テンプレートまで](https://qiita.com/juyun2490/items/2e481f659d897d7208c5)**

今回はGitHub MCP連携を実際にやってみた記録です。手順そのものはシンプルなんですが、社内特有の事情でいくつかハマりました。同じような環境の人の参考になれば。

### なぜGitHub MCPを使いたかったか

うちのチームはPRレビューがそこそこ多くて、MCP連携前はブラウザでdiffを開いてコピーしてClaudeに貼り付けて…という地味に面倒な流れがありました。

MCP連携後はこれが全部自然言語で済むようになります：

| 作業 | MCP前 | MCP後 |
|------|-------|-------|
| PRレビュー | ブラウザでdiffをコピー→貼り付け | 「PR #○○をレビューして」一言で完結 |
| レビューコメント対応 | コメントを読む→手動修正→コミット | コメント読む→修正→コミットまで一気通貫 |
| 複数PR横断確認 | ブラウザで1つずつ確認 | 「今週のPR一覧を確認して」で一括確認 |

---

## 環境

- OS：Mac・Windows（両対応）
- Claude Code CLI（ターミナル）
- Claude Desktop

---

## 事前確認

まずNode.jsのバージョンだけ確認しておきます。18未満だとMCPがうまく動かないケースが多いので。

```bash
# Node.js バージョン確認（18以上が必要）
node --version

# Claude Code バージョン確認
claude --version
```

---

## STEP 1 — Claude Desktop のインストール

Claude Code CLIは使っていたけどClaude Desktopはまだ入れていなかったので、まずここから。

### Mac

```
1. https://claude.ai/download をブラウザで開く
2.「Download for Mac」をクリック
3. ダウンロードされた .dmg ファイルを開く
4. Claude アイコンを Applications フォルダにドラッグ
5. Applications から Claude を起動
6. claude.ai アカウントでログイン
```

インストール後は**完全に終了**させてください。ウインドウを閉じるだけだとバックグラウンドで起動し続けます（Dockで右クリック → 終了）。

### Windows

```
1. https://claude.ai/download をブラウザで開く
2.「Download for Windows」をクリック
3. ダウンロードされた .exe インストーラーを実行する
4. インストーラーの指示に従いインストール完了
5. Claude を起動して claude.ai アカウントでログイン
```

こちらもインストール後は完全に終了（タスクバーのアイコンを右クリック → 終了）。

> 参考：[Claude公式ダウンロードページ](https://claude.ai/download)

---

## STEP 2 — Personal Access Token（PAT）の発行

### Classic token と Fine-grained token、どっちを使うか

GitHubのPATには2種類あります。最初どちらを使うか迷ったので、違いを整理しました。

GitHubはFine-grained tokenを推奨していますが、複数のOrganizationに一度にアクセスしたい場合など、Classic tokenでないと対応できないケースもあります。

| 比較項目 | Classic token | Fine-grained token |
|---------|--------------|-------------------|
| リポジトリ範囲 | 全リポジトリへのアクセス | 特定リポジトリのみに限定可能 |
| 権限の粒度 | スコープ単位（粗い） | 機能単位（細かく制御可能） |
| 有効期限 | 無期限設定が可能 | 設定が必要（最大366日） |
| 複数Organization | ✅ 対応 | ❌ 1つのユーザー/Orgのみ |
| GitHubの推奨 | ⚠️ セキュリティ上は非推奨 | ✅ 推奨 |
| 今回の使用 | **✅ 使用**（全リポジトリを対象にするため） | 特定リポジトリに絞る場合はこちら |

今回は全リポジトリを対象にしたかったのでClassic tokenを選びました。セキュリティ的には範囲が広いので、トークンの管理には気をつける必要があります。

:::note warn
**Classic tokenを使う場合の注意：**
全リポジトリへのアクセス権が付与されるため、漏洩時の影響範囲が大きい。
Gitにコミットしたり共有ストレージに平文で保存するのは絶対NG。
:::

> 参考：[GitHub公式ドキュメント「個人用アクセストークンを管理する」](https://docs.github.com/ja/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
> 該当箇所：「Personal access tokens (classic) は安全性が低くなります。ただし、現在、一部の機能はpersonal access tokens (classic) でしか機能しません」

### 発行手順

```
GitHub にログイン
→ 右上アイコン → Settings
→ Developer settings（左メニュー最下部）
→ Personal access tokens
→ Tokens (classic)
→「Generate new token (classic)」
```

### 今回設定したスコープ

| スコープ | 内容 |
|---------|------|
| `repo` | リポジトリ全般（Issues・PR・コード） |
| `read:org` | Organization情報の読み取り |
| `project` | GitHub Projects v2の操作 |

> 参考：[tomozumi-system.com「Claude GitHub MCP Serverの設定手順」](https://tomozumi-system.com/2026/02/claude-github-mcp-server-%E3%81%A7claude%E3%81%A8github%E3%82%92%E9%80%A3%E6%90%BA%E3%81%99%E3%82%8B/)

:::note warn
既存のトークンがあっても、用途ごとに分けて新しく作るのがおすすめ。Claude Code用だけを後で無効化できるので管理が楽になります。
あと、トークンはページを離れると二度と表示されないので必ずコピーして保管を。（一度やらかしました）
:::

---

## STEP 3 — Claude Desktop への設定

### HTTP方式とstdio方式、どっちを使うか

GitHub MCPの接続方式は2種類あります。

| 方式 | Claude Code CLI | Claude Desktop |
|------|----------------|----------------|
| **HTTP方式**（`api.githubcopilot.com/mcp/`） | ✅ 対応 | ❌ 非対応 |
| **stdio方式**（`@modelcontextprotocol/server-github`） | ✅ 対応 | ✅ 対応 |

Claude Code CLIとClaude Desktop両方で使いたかったのでstdio方式を選びました。HTTP方式はClaude Desktopで使えないので注意です。

> 参考：[LobeHub「GitHub MCP setup」](https://lobehub.com/mcp/pcantalupo-github-mcp-setup)
> 該当箇所：「Claude Desktop does not support HTTP transport for GitHub MCP」

### 設定ファイルの場所

OSによって違います。

- macOS：`~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows：`%APPDATA%\Claude\claude_desktop_config.json`

> 参考：[Qiita「MCP 導入・環境構築〜基本的な使い方の全手順」](https://qiita.com/to3izo/items/ca0e9596324610b195fc)
> 該当箇所：macOS・Windowsの設定ファイルパス記載箇所

### Mac での手順

ターミナルから直接開けます。

```bash
open -e ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

ファイルがない場合はこちら：

```bash
mkdir -p ~/Library/Application\ Support/Claude
touch ~/Library/Application\ Support/Claude/claude_desktop_config.json
open -e ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Windows での手順

パスを直接探すより、設定画面から開くのが確実です。最新のClaude Desktop（Windows Store版など）はファイルの場所が複雑なケースがあるので。

```
Claude Desktop を起動
→ 左上メニュー「Claude」→「設定（Settings）」
→「開発者（Developer）」タブ
→「設定を編集（Edit Config）」をクリック
→ 設定ファイルのあるフォルダが開く
→ claude_desktop_config.json をテキストエディタで開く
```

> 参考：[DevelopersIO「Claude DesktopでのMCP設定」](https://dev.classmethod.jp/articles/free-claude-desktop-filesystem-mcp-setup/)
> 該当箇所：「Claude Desktop の 設定 ＞ 開発者 ＞ 設定を編集 をクリックすると、設定ファイルのあるフォルダが開く」

### 設定ファイルに書く内容

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ここに発行したトークンを貼り付ける"
      }
    }
  }
}
```

:::note
他のMCPサーバーがすでに設定済みの場合は `mcpServers` の中に追記すればOKです。
:::

書いたら保存してClaude Desktopを**再起動**。

チャット画面下部の＋アイコンかツールアイコンをクリックして `github` が出てきたら接続成功です。

---

## STEP 4 — Claude Code CLIへの設定

ここで注意点が1つ。**`claude` セッションを起動する前**のターミナルで実行してください。`claude` を起動した後の `>` プロンプトの中では動きません。

```bash
claude mcp add github \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=発行したトークン \
  -- npx -y @modelcontextprotocol/server-github
```

うまくいくとこう表示されます：

```
Added stdio MCP server github with command: npx -y @modelcontextprotocol/server-github to local config
File modified:
```

---

## ハマったところと解決策

ここが今回一番しんどかった部分です。手順自体はシンプルなんですが、社内の設定ファイルが絡んでくると想定外のエラーが出ました。

### ① enterprise policy でブロックされた

STEP 4のコマンドを叩いたらこんなエラーが出ました：

```
Cannot add MCP server "github": not allowed by enterprise policy
```

最初は何のことかわからなくて焦りましたが、原因を調べてみたら以前チーム展開した `managed-settings.json` が犯人でした。Slackしか許可していなかったんです。

```json
{ "serverName": "slack" }
```

**解決策：** `managed-settings.json` に `github` を追加する。

```bash
sudo nano "/Library/Application Support/ClaudeCode/managed-settings.json"
```

```json
{
  "allowedMcpServers": [
    { "serverName": "slack" },
    { "serverName": "github" }
  ]
}
```

nanoの保存方法（慣れてないと戸惑う）：

```
Ctrl + O  → 保存
Enter     → ファイル名確認
Ctrl + X  → 編集終了
```

修正できたか確認：

```bash
cat "/Library/Application Support/ClaudeCode/managed-settings.json"
```

---

### ② managed-settings.json を編集しようとしたら権限エラー

さっそく `managed-settings.json` を編集しようとしたら今度はこれが出ました：

```
あなたはファイル"managed-settings.json"の所有者ではなく、そのファイルに書き込む権限がありません。
```

自分で作ったファイルなのに…と思いましたが、`sudo` で作ったせいで所有者が `root` になっていたのが原因でした。なので `sudo nano` で開けば解決します。

```bash
sudo nano "/Library/Application Support/ClaudeCode/managed-settings.json"
```

`managed-settings.json` を `sudo` で作成した方は同じ問題にぶつかる可能性があるので先に頭に入れておくといいかも。

---

## STEP 5 — 接続・動作確認

```bash
claude mcp list
# → github ✓ Connected と表示されれば成功
```

`claude` を起動してセッション内でも確認できます：

```bash
claude
```

```
/mcp
# → github ✓ connected を確認
```

動作確認はこのあたりから試してみました：

```
# PR一覧の取得
このリポジトリのオープンなPR一覧を教えてください

# PRレビュー
PR #[番号] のdiffを確認して、問題点と改善点を教えてください

# レビューコメントへの対応
PR #[番号] のレビューコメントを全部読んで、
対応できるものは修正してコミットしてください
```

---

## まとめ

設定自体は思ったよりシンプルでした。ただ `managed-settings.json` を使っているチームは enterprise policy のブロックと権限エラーの2段階でハマる可能性があるので、STEP 4の前に `managed-settings.json` の中身を確認しておくとスムーズです。

PRレビューの流れがだいぶ楽になったので、しばらく使いながら業務への効果を記録していきます。

---

## 参考リンク

| 内容 | URL |
|------|-----|
| Claude公式ダウンロードページ | https://claude.ai/download |
| GitHub公式：PATの種類と違い | https://docs.github.com/ja/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens |
| tomozumi-system.com：GitHub MCP Server 設定手順 | https://tomozumi-system.com/2026/02/claude-github-mcp-server-%E3%81%A7claude%E3%81%A8github%E3%82%92%E9%80%A3%E6%90%BA%E3%81%99%E3%82%8B/ |
| LobeHub：GitHub MCP setup | https://lobehub.com/mcp/pcantalupo-github-mcp-setup |
| Qiita：MCP 導入・環境構築（Claude Desktop編） | https://qiita.com/to3izo/items/ca0e9596324610b195fc |
| DevelopersIO：Claude DesktopでのMCP設定（Windows向け） | https://dev.classmethod.jp/articles/free-claude-desktop-filesystem-mcp-setup/ |
