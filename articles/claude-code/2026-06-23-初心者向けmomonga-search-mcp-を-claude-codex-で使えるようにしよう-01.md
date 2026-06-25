---
id: "2026-06-23-初心者向けmomonga-search-mcp-を-claude-codex-で使えるようにしよう-01"
title: "【初心者向け】Momonga Search MCP を Claude / Codex で使えるようにしよう！"
url: "https://zenn.dev/ray000/articles/momonga-search-mcp-setup"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "LLM", "OpenAI", "GPT"]
date_published: "2026-06-23"
date_collected: "2026-06-25"
summary_by: "auto-rss"
query: ""
---

## About

[Momonga Search MCP](https://github.com/ReiMinamoto/momonga_search_mcp) を、手元の AI クライアントから使えるようにするセットアップ手順をまとめた記事です。

対象クライアントは次の3つです。

* **Claude Desktop**
* **Claude Code**
* **Codex**

いずれも「自分のPC上で MCP サーバーを起動して使う（stdio / ローカル実行）」スタイルです。`uv` のインストールから順番に説明するので、初心者の方でも大丈夫です！

> ChatGPT について：本サーバーは ChatGPT には対応していません（設計上の理由は記事後半の[「ChatGPT で使いたい人へ」](#chatgpt-%E3%81%A7%E4%BD%BF%E3%81%84%E3%81%9F%E3%81%84%E4%BA%BA%E3%81%B8)を参照）。代わりに上の3つのどれかを使ってください。

---

## Momonga Search MCP とは

**企業の公表資料・経済ニュースを、LLM / エージェントが安全に検索・取得・根拠提示するための MCP サーバー**です。

このMCPサーバーは以下の設計になっています。

* 文書の全文をそのままエージェントに渡すのではなく、**取得した内容を手元のキャッシュに保存**しておき、`search_section_contents` / `get_section_window` などで**必要な箇所だけを切り出して**返す
* これにより、エージェントの限られたコンテキスト（読み込める文章量）を無駄遣いせずに調査を進められる

コンテキストを削減することは、モデルの使用量を減らすだけではなく、出力の性能にも影響するため非常に重要です。

この「**取得物を手元に保存し、そこから必要な断片だけを再利用する**」仕組みは、**サーバーとエージェントが同じマシンに存在する stdio / ローカル実行**と相性が良いです。本記事が上の3クライアントを対象にしているのも、この設計が活きるためです。

---

## 全体の流れ

セットアップは大きく2段階です。

1. **共通準備**（全クライアント共通） … `uv` → リポジトリ取得 → APIキー設定（→ 任意で動作確認）
2. **クライアント別の登録** … Claude Desktop / Claude Code / Codex のいずれか

まずは共通準備を一度やってしまえば、あとは使いたいクライアントの登録手順を見るだけで大丈夫です。

---

## 1. 共通準備

### 1-1. `uv` をインストールする

`uv` は Python 環境とパッケージをまとめて高速に入れられるツールです。本サーバーは `uv` を前提にしているので、これをインストールする必要があります。  
使っているOSに合わせて、ターミナル（Windowsの場合はPowerShell）で次のコマンドを実行しましょう。

**macOS / Linux:**

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows（PowerShell）:**

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

インストール後、ターミナル（Windows は PowerShell）を開き直してから確認します。

バージョンが表示されればOKです。表示されない場合は、ターミナルを一度閉じて開き直してみてください。

### 1-2. リポジトリを取得する

GitHub 上の [momonga\_search\_mcp](https://github.com/ReiMinamoto/momonga_search_mcp) を、手元のPCにコピー（`git clone`）します。

> **Git について：**  
> この手順では `git clone` コマンドを使います。`git` が入っていない場合は、OS ごとに次のとおりインストールしてください。
>
> * **macOS**：`git clone` を実行したときに Command Line Tools のインストールを求めるポップアップが出ることがあります。そのまま「インストール」を選べば OK です（Git も一緒に入ります）。
> * **Windows**：[Git for Windows](https://git-scm.com/download/win) をインストールしてください。
> * **Linux**：Ubuntu / Debian 系では `sudo apt update && sudo apt install git` でインストールできます。Fedora 系では `sudo dnf install git`、Arch 系では `sudo pacman -S git` を使ってください。

```
git clone https://github.com/ReiMinamoto/momonga_search_mcp.git
cd momonga_search_mcp
uv sync
```

`uv sync` で、サーバーの実行に必要なパッケージが自動的にそろいます。

!

この後のクライアント登録で**このリポジトリの絶対パス**を何度も使います。`cd momonga_search_mcp` のあと、リポジトリ直下で次を実行してパスを控えておくと後が楽です。

* **macOS / Linux:** `pwd`
* **Windows（PowerShell）:** `(Get-Location).Path`

表示されたパス（例：`/Users/yourname/momonga_search_mcp` や `C:\Users\<ユーザー名>\momonga_search_mcp`）をメモしておき、以降の設定で**パスを書く箇所**（`"/absolute/path/to/momonga_search_mcp"` などのプレースホルダ部分）に貼り付けてください。なお、Windows では `\` を `/` に置き換えてください。

> 補足：`uv` がデフォルトのキャッシュ場所に書き込めない環境では、`export UV_CACHE_DIR=.uv-cache` のようにワークスペース内へ向けると安定します。

### 1-3. APIキーを設定する

<https://momongasearch.com/> で Momonga Search API キーを発行します。

1-2 で `cd` した**リポジトリ直下**（`momonga_search_mcp` の中）で、設定ファイルの雛形をコピーします。

これでリポジトリ直下に `.env` ファイルができます。この `.env` をエディタで開き、`MOMONGA_SEARCH_API_KEY` を発行した実際のキーに置き換えます。

.env

```
MOMONGA_SEARCH_API_KEY=ms_live_xxxxxxxxxxxxxxxx
```

主な環境変数は次のとおりです。最初は `MOMONGA_SEARCH_API_KEY` だけ設定すれば動きます。他の変数は基本的にいじらなくて大丈夫です。

| 環境変数 | 必須 | デフォルト | 意味 |
| --- | --- | --- | --- |
| `MOMONGA_SEARCH_API_KEY` | API利用時 | なし | Momonga Search の APIキー |
| `MOMONGA_BASE_URL` | いいえ | `https://api.momongasearch.com/v1` | APIのベースURL |
| `MOMONGA_SEARCH_MCP_CACHE_DIR` | いいえ | OS標準のキャッシュ場所 | 取得物の保存先 |
| `MOMONGA_SEARCH_MCP_CACHE_MAX_GB` | いいえ | `1` | キャッシュ容量の上限（GB） |
| `MOMONGA_MCP_LOG_LEVEL` | いいえ | `INFO` | ログレベル |

### 1-4.（任意）動作確認

ここまでで準備は完了です。**この節はスキップしても構いません**。次の「クライアント別セットアップ」に進んで、登録後にツールが使えればOKです。

もしクライアント登録前にサーバー単体で起動するか確かめたい場合は、リポジトリ直下で次を実行します（macOS / Linux / Windows 共通）。

```
uv run momonga-search-mcp
```

stdio サーバーとして起動し、**待機状態**になります。次のようなログが1行出て、プロンプトに戻らなければ成功です。

```
2026-05-30 21:00:00,614 INFO momonga_search_mcp.server: starting momonga-search-mcp over stdio base_url=https://api.momongasearch.com/v1 cache_dir=...
```

確認できたら `Ctrl-C` で停止してください。  
うまく起動しないときは、後述の[トラブルシュート](#3-%E3%81%86%E3%81%BE%E3%81%8F%E3%81%84%E3%81%8B%E3%81%AA%E3%81%84%E3%81%A8%E3%81%8D%E3%81%AF%E3%83%88%E3%83%A9%E3%83%96%E3%83%AB%E3%82%B7%E3%83%A5%E3%83%BC%E3%83%88)を参照してください。

---

## 2. クライアント別セットアップ

使いたいクライアントの節だけ読めばOKです。

### 2-1. Claude Desktop

Claude Desktop は設定ファイル `claude_desktop_config.json` に MCP サーバーを登録します。

**Claude Desktop の `設定（Settings） → 開発者（Developer） → 設定を編集（Edit Config）` から開く**のが一番簡単です（macOS / Windows 共通）。このボタンで設定ファイルが直接開き、ファイルが無ければ自動で作られるので、パスを自分で探す必要はありません。

開いたファイルに次のように追記します。下の `"/absolute/path/to/momonga_search_mcp"` の部分を、**1-2 で控えたこのリポジトリの絶対パスに書き換えて**ください。

claude\_desktop\_config.json

```
{
  "mcpServers": {
    "momonga-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/momonga_search_mcp",
        "run",
        "momonga-search-mcp"
      ]
    }
  }
}
```

**すでにファイルに中身がある場合**（`preferences` など別の設定が入っているとき）は、上書きせず、`mcpServers` を**トップレベルのキーとして追加**します。既存のキーとはカンマ `,` で区切ってください。たとえば次のような既存ファイルなら、

claude\_desktop\_config.json

```
{
  "preferences": { "...": "..." },
  "coworkUserFilesPath": "C:/Users/<ユーザー名>/Claude"
}
```

こう追記します（`coworkUserFilesPath` の後ろにカンマを足して `mcpServers` を追加）。

claude\_desktop\_config.json

```
{
  "preferences": { "...": "..." },
  "coworkUserFilesPath": "C:/Users/<ユーザー名>/Claude",
  "mcpServers": {
    "momonga-search": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/<ユーザー名>/momonga_search_mcp",
        "run",
        "momonga-search-mcp"
      ]
    }
  }
}
```

保存したら **Claude Desktop を完全に再起動**します。ウィンドウ右上の `×` で閉じるだけではバックグラウンドで動き続けることがあるため、必ずアプリ自体を終了してから開き直してください。

* **Windows**：タスクバー右下の通知領域（隠れているインジケーターを含む）にある Claude アイコンを右クリックし、`Quit` / `終了` を選びます。見つからない場合は `Ctrl + Shift + Esc` でタスクマネージャーを開き、Claude 関連プロセスを終了します。
* **macOS**：メニューバーまたは Dock の Claude アイコンから `Quit Claude` / `Claude を終了` を選びます。ショートカットは、Claude を前面にした状態で `Cmd + Q` です。

その後、Claude Desktop をもう一度起動します。

再起動後、うまく繋がっているかは次の順で確認します。

1. **接続状態** … `設定（Settings） → 開発者（Developer）` で、`momonga-search` が接続済みか確認します。
2. **実際に使う** … 新しいチャットで「モモンガサーチMCPを使って、トヨタ自動車の開示資料を探して」のように頼み、エラーなく応答が返れば成功です。

うまくいかない場合は、JSON の書式ミスやリポジトリのパス誤りが多いので、後述の[トラブルシュート](#3-%E3%81%86%E3%81%BE%E3%81%8F%E3%81%84%E3%81%8B%E3%81%AA%E3%81%84%E3%81%A8%E3%81%8D%E3%81%AF%E3%83%88%E3%83%A9%E3%83%96%E3%83%AB%E3%82%B7%E3%83%A5%E3%83%BC%E3%83%88)を確認してください。

### 2-2. Claude Code

Claude Code では、`claude mcp add` コマンドで登録するのが一番簡単です。`--scope user` を付けると**自分のすべてのプロジェクトから使える**ようになるので、調査用のプロジェクトなどどこからでも呼び出せます。下の `/absolute/path/to/momonga_search_mcp` を、**1-2 で控えたこのリポジトリの絶対パスに書き換えて**から実行してください。

```
claude mcp add momonga-search --scope user -- uv --directory /absolute/path/to/momonga_search_mcp run momonga-search-mcp
```

登録後、Claude Code を開き直します。すでに Claude Code を起動している場合は、一度終了してから起動し直してください。

起動後、Claude Code 内で `/mcp` を実行し、`momonga-search` が接続されているか確認できます。続けてチャットで「モモンガサーチMCPを使って、トヨタの開示資料を検索して」などと頼み、応答が返ればOKです。

### 2-3. Codex

Codex も `codex mcp add` コマンドで登録するのが簡単です。設定ファイルの場所を自分で探す必要がなく、`~/.codex/config.toml` に自動で書き込まれて**どこからでも使える**ようになります。下の `/absolute/path/to/momonga_search_mcp` を、**1-2 で控えたこのリポジトリの絶対パスに書き換えて**から実行してください。

```
codex mcp add momonga-search -- uv --directory /absolute/path/to/momonga_search_mcp run momonga-search-mcp
```

登録後、Codex を開き直します。すでに Codex を起動している場合は、一度終了してから起動し直してください。

起動後、Codex 内で `/mcp` を実行し、`momonga-search` が登録されているか確認できます。続けてチャットで「モモンガサーチMCPを使って、トヨタの開示資料を検索して」などと頼み、応答が返ればOKです。

---

## 3. うまくいかないときは（トラブルシュート）

### 切り分けの順番

1. **[1-4（任意）](#1-4%E4%BB%BB%E6%84%8F%E5%8B%95%E4%BD%9C%E7%A2%BA%E8%AA%8D)** … リポジトリ直下で `uv run momonga-search-mcp` が待機できるか（サーバー単体の起動確認）
2. **クライアントの再起動と設定** … 下の「よくあるつまずき」を確認
3. **MCP が接続できたあと** … チャットで「モモンガサーチMCPの `diagnose_setup` を実行して」と頼む。APIキーの有無やキャッシュ場所などを返す補助用で、**接続前は使えません**

### よくあるつまずき

* **`uv` が見つからない**：ターミナルを開き直す。`uv --version` で確認。
* **MCP が接続されない・サーバーが起動しない**：クライアントを**完全に再起動**したか確認（ウィンドウを閉じるだけでは足りないことがあります）。**手順 2 で登録した設定**に書いたリポジトリの絶対パスが、1-2 で控えた実際の場所と一致しているか確認（`/absolute/path/to/...` のままになっていないか）。Claude Desktop なら「設定を編集」で開く JSON、Claude Code / Codex なら `mcp add` コマンドの `--directory` に渡したパスを見直す（`codex mcp list` / `claude mcp list` で登録内容を確認できます）。
* **`server_setup_error` が返る**（チャットで調査を頼んだときなど）：APIキー未設定の可能性。リポジトリ直下の `.env` の `MOMONGA_SEARCH_API_KEY` を確認。
* **JSON の書式エラー**：カンマや括弧の閉じ忘れに注意。
* **Claude Desktop の設定でパスがうまくいかない**：`"--directory"` に書く絶対パスは **`C:/Users/...` のように `/` 区切りにしてください**（`C:\Users\...` の `\` は環境によって解釈がブレることがあります。[1-2](#1-2.-%E3%83%AA%E3%83%9D%E3%82%B8%E3%83%88%E3%83%AA%E3%82%92%E5%8F%96%E5%BE%97%E3%81%99%E3%82%8B)の注意と同じ）。

### WSL を使っている場合の注意

Windows 版 Claude Desktop / Codex は **Windows 側のコマンドしか直接実行できません**。リポジトリや `uv` を WSL 側（`/home/...`）に置くと、Windows アプリからは見えず起動に失敗します。対処は2択です。

* **Windows 側で完結させる**（本記事どおり Windows に clone & `uv` インストール）← 初心者はこちら推奨
* WSL 側で動かしたい場合は、`command` を `wsl` にして WSL 内の `uv run` を呼ぶ（WSL を使う方なら調整できるはずなので詳細は割愛します）

---

## ChatGPT で使いたい人へ

「ChatGPT も MCP に対応したのでは？」と思った方へ。結論から言うと **対応はしていますが、本サーバーは ChatGPT では動かせません**。理由は設計思想にあります。

### ChatGPT の MCP 対応の現状

ChatGPT / OpenAI 側でも MCP 対応は進んでいますが、基本的には **HTTPS で公開された Remote MCP サーバー（Streamable HTTP / SSE）** を接続する形です。本サーバーのような **ローカル stdio サーバーを ChatGPT から直接起動して使う構成ではありません**。

### 設計思想とのトレードオフ

本サーバーは前述のとおり、**取得物をローカルキャッシュ（SQLite インデックス付き）に永続化し、そこから必要な断片だけを返してコンテキストを節約する**設計です。これは「サーバーとエージェントが同じマシンに1対1」という stdio / ローカル実行と非常に相性が良い一方で、**複数ユーザーが1つのエンドポイントを共有する Remote MCP（ChatGPT のコネクタ方式）とは構造的に噛み合いません**。

共有サーバー上の単一キャッシュを全ユーザーで共有することになり、コンテキスト削減のために設けた永続キャッシュが、かえってユーザー間の分離やキャッシュ管理を複雑にしてしまうからです。

そのため、本サーバーを使うなら **Claude Desktop / Claude Code / Codex（いずれも stdio・ローカル実行）** を使ってください。よろしくお願いします。

---

## まとめ

* 本サーバーは「**手元で1人で使う（stdio・ローカル実行）**」設計。`uv` を入れるところから始めるのが近道。
* 共通準備（`uv` → clone → APIキー → 動作確認）を一度やれば、あとはクライアント登録だけ。
* Claude Code / Codex は `mcp add` コマンド一発、Claude Desktop は JSON に追記するだけ。
* ChatGPTは設計思想とのトレードオフがあるため、未対応。

ワークフローのskill化などコンテキスト削減にこだわって作ったので、ぜひ使ってみてください！  
最後まで読んでいただきありがとうございました！
