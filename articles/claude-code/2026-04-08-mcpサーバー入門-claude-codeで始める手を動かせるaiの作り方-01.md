---
id: "2026-04-08-mcpサーバー入門-claude-codeで始める手を動かせるaiの作り方-01"
title: "MCPサーバー入門 — Claude Codeで始める「手を動かせるAI」の作り方"
url: "https://qiita.com/taiki_i/items/fbaf8c5e284ac3c92938"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "LLM", "qiita"]
date_published: "2026-04-08"
date_collected: "2026-04-08"
summary_by: "auto-rss"
---

## はじめに

最近 AI 界隈で「MCP」「MCP サーバー」という言葉を目にする機会が一気に増えました。  
Claude Desktop や Cursor、各種 AI エージェントの紹介記事を読んでいると、当たり前のように「MCP サーバーを入れておくと便利」と書かれているけれど、

> 「そもそも MCP って何…？」  
> 「サーバーって自分で立てるの？難しそう…」

と感じている方も多いのではないでしょうか。

この記事では、**プログラミング初心者の方でも MCP サーバーを理解して、実際に自分の環境に導入できる**ことをゴールに、基礎から設定例までまとめて解説します。

最後には、実際に使える代表的な MCP サーバーを 5 つ紹介して、それぞれの設定方法・使い方も具体的に書いていきます。

## MCP サーバーとは？

### MCP（Model Context Protocol）とは

Anthropic が 2024 年 11 月に公開したオープンな規格で、ひとことで言うと  
**AI（LLM）と外部のツール・データソースをつなぐための共通プロトコル」** です。

これまで、AI に「自分の PC のファイルを読ませたい」「GitHub のリポジトリを操作させたい」「DB に問い合わせさせたい」といったことをやらせようとすると、ツールごとに独自の連携コードを書く必要がありました。

MCP は、この「AI ↔ ツール」の接続部分を**共通の規格**にしてしまおう！！ というものです。USB-C のように、規格さえ合っていればどんなツールでも差し込んで使える、と考えるとイメージしやすいです。

### MCP サーバーとは

MCP サーバーは、その規格に従って **「AI に提供する機能（ツール・データ）」を実装したプログラム** のことです。

例えば、

* ファイルを読み書きするための MCP サーバー
* GitHub を操作するための MCP サーバー
* PostgreSQL に SQL を投げるための MCP サーバー
* Web ページを取得・スクレイピングするための MCP サーバー

など、用途別にたくさんの MCP サーバーが公開されています。

### クライアントとサーバーの関係

MCP は「クライアント ↔ サーバー」の構成になっています。

| 役割 | 具体例 |
| --- | --- |
| MCP クライアント | Claude Desktop、Cursor、Cline、Zed など |
| MCP サーバー | filesystem、github、postgres、fetch、playwright など |

クライアント側（Claude Desktop など）に「この MCP サーバーを使うよ」と設定ファイルで教えてあげると、AI がその機能を使えるようになります。

## なぜ MCP サーバーを使うと便利なのか

ただのチャット AI と比べて、MCP サーバーを組み合わせると以下のようなことができるようになります。

* ローカルファイルを読んで要約してもらう
* GitHub の Issue を一覧化して優先順位を付けてもらう
* DB に SQL を投げて結果を分析してもらう
* Web サイトを実際に開いてスクリーンショットを撮らせる
* API のドキュメントを取得して、その場でサンプルコードを書かせる

つまり、AI が「**会話するだけの存在**」から「**手を動かせるアシスタント**」に進化するわけです。

## MCP サーバーの導入方法（Claude Code 編）

ここでは **Claude Code**（ターミナルで動く Anthropic 公式の AI コーディングツール）を例に、MCP サーバーを追加する方法を説明します。

Claude Code は Claude Desktop と違い、**設定ファイルを手で書かなくても `claude mcp add` コマンドで追加できる**のが特徴です。

### 1. 事前準備

多くの MCP サーバーは以下のいずれかのランタイムで動きます。使いたいサーバーに合わせて入れておきましょう。

* **Node.js**(`npx` コマンドを使うサーバー用)
* **Python / uv**(`uvx` コマンドを使うサーバー用)
* **Docker**(コンテナで動かしたい場合)

それぞれ以下で動作確認できます。

```
node -v
npx -v
uvx --version
docker -v
```

### 2. スコープを理解する

Claude Code の MCP サーバー設定には **3 つのスコープ**があります(スコープとは、設定を誰がどこで使えるようにするか決めるラベルのこと)。これが Claude Desktop と大きく違うポイントです。

| スコープ | 保存場所 | 用途 |
| --- | --- | --- |
| `local`（デフォルト） | プロジェクト単位・自分だけ | 個人的な試験導入、認証情報を含むもの |
| `project` | プロジェクト直下の `.mcp.json` | チーム全員で共有したい設定（Git にコミット可能) |
| `user` | ユーザーのホーム設定 | 全プロジェクトで使い回したい設定 |

コマンドで指定する場合は `-s local` / `-s project` / `-s user` のように書きます。迷ったら、

* 自分専用 → `local`
* チームで共有 → `project`
* 全プロジェクトで使う → `user`

と覚えておけば OK です。

### 3. MCP サーバーを追加する基本コマンド

```
claude mcp add <サーバー名> -- <実行コマンド> [引数...]
```

`--` 以降が「実際に起動するコマンド」になります。環境変数を渡したい場合は `-e KEY=VALUE` を使います。

```
claude mcp add <サーバー名> -e TOKEN=xxxx -- <実行コマンド> [引数...]
```

### 4. 確認・削除コマンド

追加したサーバーは以下で確認できます。

```
# 一覧表示
claude mcp list

# 詳細確認
claude mcp get <サーバー名>

# 削除
claude mcp remove <サーバー名>
```

Claude Code を起動した状態で `/mcp` と打てば、現在接続されている MCP サーバーの状態も確認できます。

## おすすめ MCP サーバー 5 選と導入手順

ここからは、初心者の方がまず入れておくと「MCP の便利さ」を実感しやすい 5 つのサーバーを、**Claude Code での追加コマンド付き**で紹介します。

### ① Filesystem — ローカルファイルを操作する

#### できること

* 指定フォルダ配下のファイル一覧取得
* ファイルの読み込み・作成・編集
* ディレクトリ作成、ファイル検索 など

> 💡 ちなみに Claude Code は標準でカレントディレクトリのファイル操作ができるので、「別のディレクトリも触らせたい」ときに真価を発揮します。

#### 追加コマンド

```
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem 許可するフォルダパス
```

`許可するフォルダパス`には許可したいフォルダのパスを並べて書きます。**ここに指定していないフォルダには AI もアクセスできません**。安全のため、いきなりホーム全体を許可するのは避けましょう。

#### 使い方の例

Claude Code の対話中に、こんな感じで頼めます。

```
~/Documents の中にある .md ファイルを一覧して、
それぞれ何について書かれているか 1 行で要約して。
```

### ② mcp-server-fetch — Web ページの内容を取得する

#### できること

* 指定 URL の HTML を取得して Markdown 化
* ニュース記事やブログを AI に読ませて要約・分析

#### 追加コマンド

```
claude mcp add fetch -- uvx mcp-server-fetch
```

`uvx` は Python 製ツールランナー [uv](https://github.com/astral-sh/uv) に含まれるコマンドです。事前に `uv` をインストールしておきましょう。

#### 使い方の例

```
https://example.com/news/123 の記事を取得して、
3 行で要約してから感想を述べて。
```

URL を投げるだけでサクッと記事の内容を読んでくれるので、リサーチ用途で重宝します。

### ③ server-github — GitHub を操作する

#### できること

* リポジトリ・Issue・PR の検索や取得
* Issue・PR の作成、コメントの追加
* ファイルの取得や更新

#### 事前準備

GitHub の [Personal Access Token](https://github.com/settings/personal-access-tokens) を発行しておきます。最低限 `repo` スコープがあれば OK です。

#### 追加コマンド

```
claude mcp add github \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxx \
  -- npx -y @modelcontextprotocol/server-github
```

`-e` オプションで環境変数としてトークンを渡します。

> ⚠️ トークンは秘密情報です。`project` スコープで追加すると `.mcp.json` に書き込まれて Git にコミットされてしまうリスクがあるので、**トークン付きの設定は `local` スコープ（デフォルト）** を推奨します。

#### 使い方の例

```
my-org/my-repo の Open な Issue を一覧して、
ラベルごとにグルーピングして優先度を提案して。
```

```
さっきの修正内容で feature/login ブランチに PR を作成して。
タイトルとボディは内容に合わせて考えて。
```

### ④ mcp-server-postgres — PostgreSQL を読む

#### できること

* データベースのスキーマ取得
* 任意の SELECT 文を実行して結果を取得
* データ分析・集計を AI と対話的に実施

> 注意：公式の `postgres` MCP サーバーは**読み取り専用**です。`UPDATE` や `DELETE` を実行することはできません。本番 DB でも比較的安心して試せます。

#### 追加コマンド

```
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres \
  "postgresql://user:password@localhost:5432/mydb"
```

接続文字列は環境に合わせて書き換えてください。パスワードを含むので、こちらも `local` スコープで追加するのがおすすめです。

#### 使い方の例

```
この DB にある users テーブルと orders テーブルの構造を教えて。
そのうえで、直近 30 日で最も注文金額が大きかったユーザー TOP10 を出して。
```

「DB の構造を把握 → SQL を組み立てる → 結果を解釈する」を AI が一気にやってくれるので、データ分析の初手として非常に強力です。

### ⑤ Playwright MCP — ブラウザを操作する

#### できること

* 実際にブラウザを起動してページを開く
* スクリーンショット取得
* フォーム入力・クリック操作の自動化
* E2E テストっぽい一連の操作を AI に指示

`fetch` が「HTML を取ってくるだけ」なのに対し、こちらは**本物のブラウザを動かす**ので、JavaScript で動的に描画されるサイトもちゃんと扱えます。

#### 追加コマンド

```
claude mcp add playwright -- npx -y @playwright/mcp@latest
```

初回起動時にブラウザのバイナリがダウンロードされるため、少し時間がかかることがあります。

#### 使い方の例

```
https://example.com を開いて、トップページのスクリーンショットを撮って。
```

```
Qiita のトップを開いて、トレンドの記事タイトルを上から 10 件取得して。
```

## 5 つを全部追加するコマンドまとめ

ここまで紹介した 5 つを一気に追加したい場合は、以下を順に実行すれば OK です。

```
# Filesystem
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem \
  /Users/yourname/Documents

# fetch
claude mcp add fetch -- uvx mcp-server-fetch

# GitHub
claude mcp add github \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxx \
  -- npx -y @modelcontextprotocol/server-github

# PostgreSQL
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres \
  "postgresql://user:password@localhost:5432/mydb"

# Playwright
claude mcp add playwright -- npx -y @playwright/mcp@latest
```

追加後は以下で確認しましょう。

5 つのサーバーが表示されていれば OK です。Claude Code を起動して `/mcp` と打てば、接続状態もチェックできます。

---

## `.mcp.json` を直接書く方法（チーム共有向け）

チームで設定を共有したい場合は、プロジェクト直下に `.mcp.json` を置く方法もあります。`claude mcp add -s project ...` で追加しても自動生成されますが、手書きしたい人向けにフォーマットも載せておきます。

```
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "./"
      ]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

このファイルを Git にコミットしておけば、チームメンバーが同じリポジトリで Claude Code を起動した際に同じ MCP サーバー構成を再現できます。

> ⚠️ 繰り返しになりますが、**トークンやパスワードを含むサーバーは `.mcp.json` に書かないでください**。個人の `local` スコープで追加しましょう。

## つまづきやすいポイント

最後に、初心者がハマりがちなポイントをまとめておきます。

1. **`claude mcp add` の `--` を忘れる**  
   `--` より前は Claude Code 側のオプション、後ろが「実行するコマンド」です。ここを区切らないとうまく解釈されません。
2. **`npx` / `uvx` が見つからない**  
   Node.js / uv のインストールが必要です。`npx -v` `uvx --version` がそれぞれ通るか確認しましょう。
3. **追加後にサーバーが起動しない**  
   `claude mcp list` で状態を確認し、エラーが出ているようなら `claude mcp get <サーバー名>` で詳細を見ます。Claude Code 起動中なら `/mcp` コマンドでも状況確認できます。
4. **権限エラー（Filesystem）**  
   コマンドで許可していないフォルダにはアクセスできません。読みたいフォルダがあるなら明示的に追加してください。
5. **トークンの取り扱い**  
   GitHub のトークンや DB パスワードは `project` スコープ（`.mcp.json`）には書かず、`local` スコープで追加するのが鉄則です。うっかり Git にコミットしないよう注意しましょう。

## まとめ

* **MCP** は AI と外部ツールをつなぐための共通プロトコル
* **MCP サーバー**はその規格に従って機能を提供するプログラム
* **Claude Code** なら `claude mcp add` コマンド一発で導入できる
* スコープ（`local` / `project` / `user`）を理解すると、個人利用・チーム共有を安全に使い分けられる
* 今回紹介した 5 つを入れるだけでも、AI が「ファイル操作・Web 取得・GitHub・DB・ブラウザ操作」までこなせる強力なアシスタントに変わる

MCP サーバーは日々新しいものが公開されています。慣れてきたら [公式リポジトリ](https://github.com/modelcontextprotocol/servers) を眺めて、自分の業務に合いそうなものをどんどん追加してみてください。

「AI に手を動かしてもらう」体験をぜひ味わってみてください 🙌

それでは、よい MCP ライフを！
