---
id: "2026-05-18-macos版claude-desktopでローカルファイルを直接操作filesystem-mcpの設-01"
title: "【macOS版】Claude Desktopでローカルファイルを直接操作！filesystem MCPの設定手順"
url: "https://qiita.com/kooohei/items/3c7291036d9a9e68fcad"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "LLM", "qiita"]
date_published: "2026-05-18"
date_collected: "2026-05-18"
summary_by: "auto-rss"
query: ""
---

# はじめに
最近話題の**MCP（Model Context Protocol）**。その中でも、ローカルPCのファイルを直接AIに操作させることができる `filesystem` サーバーは、開発体験を劇的に向上させる強力なツールです。

先日、Claude DesktopアプリがMCPに対応し、この `filesystem` サーバーを簡単に組み込めるようになりました。
本記事では、macOS環境のClaude Desktopに `@modelcontextprotocol/server-filesystem` を導入し、ローカルの特定のディレクトリ（今回は `Desktop`）へアクセスしてファイル操作を行うまでの具体的な設定手順と、つまづきやすい注意点を解説します。

## 対象環境
* macOS (Apple Silicon 環境を想定)
* Claude Desktop アプリ
* Homebrew + Node.js 環境

# そもそも `@modelcontextprotocol/server-filesystem` とは？
今回利用する `@modelcontextprotocol/server-filesystem` は、MCPの公式リファレンス実装として提供されているNode.js製のMCPサーバー（npmパッケージ）です。

単なるプログラムではなく、Claude（LLM）とあなたのローカルPCのファイルシステムを繋ぐ「安全な仲介役（ブリッジ）」として機能します。

具体的には、Claudeに対して以下のような「ツール（機能）」を標準化されたAPIとして提供します。

* **ファイルの読み書き** (`read_file`, `write_file`)
* **ディレクトリの探索** (`list_directory`, `list_allowed_directories`)
* **ファイルの検索** (`search_files`)
* **ファイル情報の取得** (`get_file_info`)

**【セキュリティ面での強力な特徴】**
最も重要な点として、このサーバーは「起動時に引数で明示的に指定したディレクトリ（およびそのサブディレクトリ）」にのみアクセスを許可します。
今回のように `/Users/kooohei/Desktop` と指定すれば、システムファイルや別プロジェクトのフォルダにはClaude側から絶対に変更・アクセスできないよう、パストラバーサル（ディレクトリトラバーサル）攻撃などを防ぐ堅牢な設計になっています。


# 1. Node.js / npx の確認
まずはターミナルを開き、`npx` コマンドが利用できることと、そのパスを確認します。

```bash:パスの確認
which npx
which node
node -v
```

私の環境（Apple Silicon Mac）では以下のようになりました。Homebrewでインストールしている場合、`/opt/homebrew/bin/` 配下になるケースが多いです。

```text:例）出力結果
/opt/homebrew/bin/npx
/opt/homebrew/bin/node
v25.4.0
```

# 2. Claude Desktop の設定ファイルを編集
Claude Desktop の MCP 設定ファイルを作成・編集します。macOS の場合は以下のパスになります。

```bash:設定ファイル
~/Library/Application Support/Claude/claude_desktop_config.json
```
※ファイルが存在しない場合は、新規作成してください。


# 3. filesystem MCP を追加
設定ファイルに以下のJSONを記述します。

```json:追記設定
{
  "mcpServers": {
    "filesystem": {
      "command": "/opt/homebrew/bin/npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/kooohei/Desktop"
      ]
    }
  }
}
```

**【設定項目の解説】**

* **`mcpServers`**: 連携するMCPサーバーを定義する大枠の項目です。ここに複数のサーバーを追加していくことができます。
* **`filesystem`**: 今回追加するサーバーの識別名です。Claude DesktopのUI（コネクタ画面）にはこの名前が表示されます。任意の名前で構いません。
* **`command`**: 実行するコマンドです。環境変数（パス）の読み込みエラーを防ぐため、手順1で確認した `npx` の**絶対パス**を指定することを強く推奨します。
* **`args`**: コマンドに渡す引数を配列で指定します（※ `arg` ではなく `args` であることに注意）。
* `"-y"`: `npx` 実行時に「パッケージをインストールしますか？」という確認プロンプトが出た際、自動的に `yes` と応答してスキップするためのオプションです。
* `"@modelcontextprotocol/server-filesystem"`: 実際に実行するMCPサーバーのnpmパッケージ名です。
* `"/Users/kooohei/Desktop"`: **Claudeにアクセスを許可するディレクトリ**の絶対パスです。ここを書き換えることで、Claudeが触れる範囲を制御できます。複数指定したい場合は、`"/Users/kooohei/Desktop", "/Users/kooohei/Downloads"` のように配列の要素として続けて記述します。


# 4. Claude Desktop を再起動
設定を反映させるため、Claude Desktopを再起動します。Dockから閉じるだけではバックグラウンドでプロセスが残る場合があるため、コマンドで完全終了させるのが確実です。

```bash:再起動
killall Claude
open -a Claude
```

# 5. ログの確認（重要）
うまく連携できない場合は、まずログを確認しましょう。

```bash:確認
cat ~/Library/Logs/Claude/mcp-server-filesystem.log
```

正常に起動している場合は、`Server started and connected successfully` といったログが記録されます。また、ログ内に `tools/list` のような表記があれば、Claude Desktop 側が正しく filesystem MCP を認識しています。


# 6. Claude Desktop 側でツールを確認
Claude Desktop のチャット入力欄左下にある **「＋」アイコン** をクリックし、**「コネクタ」**（またはツールアクセス）を開きます。
ここで `filesystem` が表示されていれば連携成功です。

![claude-filesystem_03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/82090/5697bf00-8ea9-4c77-8382-d3acb8d46c0b.png)
*▲ filesystem コネクタが表示されていない状態*

![claude-filesystem_06.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/82090/407fbc88-2f89-47dc-9858-efb0e01c7db0.png)
*▲ filesystem コネクタが表示された状態*


# 7. 最初はアクセスできない場合がある？（注意点）
連携が完了していても、いきなり以下のように質問すると……

> Desktop配下のファイル一覧を表示してください

![claude-filesystem_07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/82090/7644418d-d4ac-443c-940c-271ad4bc26b3.png)

画像のように「私が使えるのはクラウド上のコンテナ環境のみで…」と、filesystemツールを利用せず通常の回答（エラー）になってしまう場合があります。これはツールがうまく呼び出されていない状態です。

![claude-filesystem_05.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/82090/0a34d4cf-1b33-4082-a1aa-fc3310cf0f7b.png)


# 8. コネクタをONにした状態で再実行
入力欄の「＋」から **`filesystem` のトグルスイッチを明示的にON** にした状態で、再度同じプロンプトを実行してみてください。

すると、今度は「filesystem連携を使用しました」という表示とともに、ローカルの Desktop 配下のファイル一覧を見事に取得してくれます。

![claude-filesystem_08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/82090/535107a8-3de7-4173-bc91-bea59e45047b.png)
*▲ filesystem が実際に利用され、ローカルファイルの一覧が取得できた状態*



# おわりに
本記事では、Claude Desktopでローカルファイルを直接操作するための `filesystem` MCPの設定手順をご紹介しました。

導入することで、以下のような操作をClaudeと対話しながら直接行えるようになります。
* ローカルファイルの一覧取得
* ファイル内容の読み込み
* ファイルの編集やコードの自動修正

ブラウザ版で毎回ファイルをアップロードしたり、コードをコピペしたりする手間が省けるため、一度設定してしまえば日々の作業効率が格段に上がります。また、今回の設定のように**アクセス許可を特定のフォルダのみに限定する**ことで、安全面をコントロールしながら利用できるのも嬉しいポイントです。

MCPには `filesystem` 以外にも、GitHubやNotion、データベースなどと連携できる多様なサーバーが用意されています。まずは導入がシンプルで効果を実感しやすい `filesystem` から、ぜひMCPの圧倒的な便利さを体感してみてください！
