---
id: "2026-04-05-claude-code-google-analyticsga4のmcpサーバ連携を色々試してみた-01"
title: "Claude Code & Google Analytics(GA4)のMCPサーバ連携を色々試してみた"
url: "https://zenn.dev/shinyaa31/articles/e3a1bdf4d99d80"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "zenn"]
date_published: "2026-04-05"
date_collected: "2026-04-06"
summary_by: "auto-rss"
---

![](https://static.zenn.studio/user-upload/8dccbb4d7e08-20260404.png)

直近Google Analytics(GA4)の情報について色々解析したい、アクセスしたいという要件があり、それならばClaude(Claude Code)で良い感じにやりたいね。ということで当エントリではClaude(Claude Code)からGoogle Analytics(GA4)のMCPサーバを介して諸々連携する手順について、幾つかの経路にそれぞれ言及する形でまとめたいと思います。

ベースで参考にする手順はこのあたり。  
<https://developers.google.com/analytics/devguides/MCP?hl=ja>

<https://www.youtube.com/watch?v=PT4wGPxWiRQ>

<https://github.com/googleanalytics/google-analytics-mcp>

連携を試みたのは以下の方式です。

* Pythonパッケージ管理ツール『uv』を用い、所定のClaude Codeプロジェクト単体でMCPサーバ連携
* pipxを用い、グローバルな形でClaude CodeからMCPサーバ連携
* Claude Desktop経由でMCPサーバ連携

## 前提条件&準備

いずれのケースに於いても共通で必要となるのは『GA4環境』『GA4にアクセス出来るGoogleアカウント』『Google Cloudプロジェクト』『Claude Code環境』。まずはここを準備していきます。

また、筆者の環境ではClaude CodeでのPython実行にuvを用いる設定にしているため、その辺の設定も含めてここで確認、準備しておきます。

### GA4環境

何は無くともアクセス対象となるGoogle Analytics(GA4)環境が無いと始まりません。今回は以前から運営・投稿しているZennに紐づけた環境があるのでそれを使うことにします。  
![](https://static.zenn.studio/user-upload/82c5d05c1acf-20260404.png)

次に行う操作はGA4の閲覧権限を有するアカウントで行ってください。

### Googleアカウント/gcloudプロジェクト

連携にはGoogle Cloudプロジェクトが必要となります。gcloudコマンドを実行環境に導入しておきます。

```
## 実行環境OSはローカルのMac. 対応するインストーラでgcloudを導入
% uname -m
arm64

% curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-darwin-arm.tar.gz
% tar -xf google-cloud-cli-darwin-arm.tar.gz
% ./google-cloud-sdk/install.sh
Welcome to the Google Cloud CLI!
:
Do you want to help improve the Google Cloud CLI (y/N)?  y
:
Do you want to continue (Y/n)?  y
:
Enter a path to an rc file to update, or leave blank to use [/Users/xxxxxxxxxx/.zshrc]:
Backing up [/Users/xxxxxxxxxx/.zshrc] to [/Users/xxxxxxxxxx/.zshrc.backup].
[/Users/xxxxxxxxxx/.zshrc] has been updated.
:
Successfully built crcmod
Installing collected packages: crcmod, typing-extensions, setuptools, pycparser, google_crc32c, certifi, grpcio, cffi, cryptography, pyopenssl
Successfully installed certifi-2026.2.25 cffi-2.0.0 crcmod-1.7 cryptography-42.0.7 google_crc32c-1.8.0 grpcio-1.80.0 pycparser-3.0 pyopenssl-24.2.1 setuptools-82.0.1 typing-extensions-4.15.0
Virtual env enabled.

For more information on how to get started, please visit:
  https://cloud.google.com/sdk/docs/quickstarts

## ターミナル再起動後バージョン確認.
% gcloud --version
Google Cloud SDK 563.0.0
bq 2.1.31
core 2026.03.27
gcloud-crc32c 1.0.0
gsutil 5.36
```

### uvのインストール

<https://docs.astral.sh/uv/getting-started/installation/>  
<https://speakerdeck.com/mickey_kubo/pythonpatukeziguan-li-uv-wan-quan-ru-men>

```
% uv --version
uv 0.9.5 (Homebrew 2025-10-21)
```

### Claude Codeのインストール

<https://code.claude.com/docs/ja/quickstart>

```
% claude --version
2.1.89 (Claude Code)
```

### gcloud経由でGoogleプロジェクトを作成

Google Analytics MCP を使う前に、Google Cloudプロジェクト側で Google Analytics Admin API と Google Analytics Data API を有効化していきます。

まずはgcloudでログイン。ブラウザが立ち上がり、それぞれ許可をしていくことで認証が完了となります。

以下コマンドで現存するプロジェクトの一覧が表示されます。今回は検証用にGoogle Cloudプロジェクトを作る形で進めます。

```
% gcloud projects list
PROJECT_ID       NAME             PROJECT_NUMBER  ENVIRONMENT
:
:
```

`gcloud projects create`コマンドでプロジェクトを作成。

```
% gcloud projects create shinyaa31-ga-mcp-zenn --name "shinyaa31-ga-mcp for Zenn" --set-as-default
Create in progress for [https://cloudresourcemanager.googleapis.com/v1/projects/shinyaa31-ga-mcp-zenn].
Waiting for [operations/create_project.global.9999999999999999999] to finish...done.
Enabling service [cloudapis.googleapis.com] on project [shinyaa31-ga-mcp-zenn]...
Operation "operations/acat.p2-9999999999-xxXxxXxx-xXXX-9999-9999-99xx99xx99xx" finished successfully.
Updated property [core/project] to [shinyaa31-ga-mcp-zenn].
```

上記で作成したプロジェクトが一覧に出てくることを確認します。

```
## 現在アクティブな Google Cloud プロジェクト ID を確認.
% gcloud config get-value project
shinyaa31-ga-mcp-zenn
## 一覧でも確認
% gcloud projects list
PROJECT_ID             NAME                       PROJECT_NUMBER  ENVIRONMENT
:
:
shinyaa31-ga-mcp-zenn  shinyaa31-ga-mcp for Zenn  99999999999

## 現在のプロジェクトを切り替えるコマンド実行(これは後から変えられる)
% gcloud config set project shinyaa31-ga-mcp-zenn
Updated property [core/project].
```

`gcloud services enable`コマンドで必要となるAPIの有効化設定を行います。

```
## 有効化実施.
% gcloud services enable analyticsadmin.googleapis.com analyticsdata.googleapis.com
Operation "operations/acat.p2-9999999999-xxXxxXxx-xXXX-9999-9999-99xx99xx99xx" finished successfully.

## 有効化内容を確認.
% gcloud services list --enabled | grep analytics
analyticsadmin.googleapis.com        Google Analytics Admin API
analyticsdata.googleapis.com         Google Analytics Data API
analyticshub.googleapis.com          Analytics Hub API
```

## 1. uv環境 + プロジェクトスコープでMCPサーバ連携

### サービスアカウントによる認証情報の作成

Google Analyticsとのアクセス部分、認証が必要なのですがここではサービスアカウントによる認証方式で対応する方向で進めます。

Google Cloudアカウント上で[IAMと管理]→[サービスアカウント]を選択。  
![](https://static.zenn.studio/user-upload/78a08ae87e51-20260404.png)

[サービスアカウントを作成]を選択。  
![](https://static.zenn.studio/user-upload/716682fbbe55-20260404.png)

任意の名称を設定し、アカウントを作成します。  
![](https://static.zenn.studio/user-upload/f114239f47d3-20260404.png)

作成したサービスアカウントのメニューから[鍵を管理]を選択。  
![](https://static.zenn.studio/user-upload/984aac0264bd-20260404.png)

[新しい鍵]を選択。  
![](https://static.zenn.studio/user-upload/50e32b57aa66-20260404.png)

キーのタイプ:JSONで秘密鍵ファイルを作成。  
![](https://static.zenn.studio/user-upload/28d5e07fc1fb-20260404.png)

作成したファイルは安全に保存しておいてください。  
![](https://static.zenn.studio/user-upload/126ad377d731-20260404.png)

サービスアカウント作成時に生成されたメールアドレスの値をコピーし、  
![](https://static.zenn.studio/user-upload/d8100f705d1d-20260404.png)

対象となるGoogle Analyticsアカウントの[プロパティ]→[プロパティのアクセス管理]でアクセス出来るようにメールアドレスを登録します。  
![](https://static.zenn.studio/user-upload/46447958b504-20260404.png)

### Claude Codeプロジェクト作成

任意のClaude Code作業を行うディレクトリを定めて、そこで各種連携設定を進めていきます。

```
## 個人的にClaude Codeプロジェクトを束ねる場所を設けているので今回もそこで作業を進める.
% pwd
/xxx/xxx/xxxxxxxx/shinyaa31-claude-code-workspace

## Google Analytics MCPのリポジトリをクローン。今回はここをキャンプ地とする.
% git --version
git version 2.50.1 (Apple Git-155)
% git clone https://github.com/googleanalytics/google-analytics-mcp.git

## ディレクトリ移動.
% cd google-analytics-mcp

## 初期化作業実施(uv).
% uv --version
uv 0.9.5 (Homebrew 2025-10-21)
% uv sync
Using CPython 3.14.0
Creating virtual environment at: .venv
```

### Google Analytics MCP実行確認(単体)

次に、Claude Code にまだ登録せず、まずは単体で起動確認します。`uv run analytics-mcp` は公開例でもstdioベースの起動コマンドとして使われています。

`Starting MCP Stdio Server: Google Analytics MCP Server` と出ているのは、stdio MCP サーバーとして立ち上がったことを示すメッセージで、その後はクライアントからの入出力待ちになるのが自然です。いまの段階では「uv 環境でローカル起動できる」ことが確認できたと見てよいです。

```
% pwd
/xxx/xxx/xxxxxxxx/shinyaa31-claude-code-workspace/google-analytics-mcp
% uv run analytics-mcp
Starting MCP Stdio Server: Google Analytics MCP Server
```

確認が出来たらサーバは停めて構いません。(Ctrl+CでOK)

### Google Analytics MCP実行確認(Claude Code連携)

`claude mcp add`コマンドでmcp設定を追加します。

```
## MCP連携の追加.
% claude mcp add \
  --transport stdio \
  --scope project \
  -e GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json" \
  -e GOOGLE_CLOUD_PROJECT="shinyaa31-ga-mcp-zenn" \
  ga4 \
  -- /bin/zsh -lc 'cd "(実際のパス)/google-analytics-mcp" && uv run analytics-mcp'

## 内容の確認(1).
% claude mcp list
Checking MCP server health...

:
ga4: /bin/zsh -lc cd "/xxx/xxx/xxxxxxxx/shinyaa31-claude-code-workspace/google-analytics-mcp" && uv run analytics-mcp - ✓ Connected
:

## 内容の確認(2).
% claude mcp get ga4
ga4:
  Scope: Project config (shared via .mcp.json)
  Status: ✓ Connected
  Type: stdio
  Command: /bin/zsh
  Args: -lc cd "/xxx/xxx/xxxxxxxx/shinyaa31-claude-code-workspace/google-analytics-mcp" && uv run analytics-mcp
  Environment:
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
    GOOGLE_CLOUD_PROJECT=shinyaa31-ga-mcp-zenn

To remove this server, run: claude mcp remove "ga4" -s project
```

そして対象プロジェクト配下の `.mcp.json` ファイルに連携設定を反映。`args`配下の実行パス、及び`GOOGLE_APPLICATION_CREDENTIALS`に記載されているサービスアカウントの秘密鍵ファイルの場所は適宜該当する値に読み替える、設定を合わせるようにしてください。

/xxx/xxx/xxxxxxxx/shinyaa31-claude-code-workspace/google-analytics-mcp/.mcp.json

```
{
  "mcpServers": {
    "ga4": {
      "type": "stdio",
      "command": "/bin/zsh",
      "args": [
        "-lc",
        "cd \"/xxx/xxx/xxxxxxxx/shinyaa31-claude-code-workspace/google-analytics-mcp\" && uv run analytics-mcp"
      ],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account-key.json",
        "GOOGLE_CLOUD_PROJECT": "shinyaa31-ga-mcp-zenn"
      }
    }
  }
}
```

これで連携設定は完了です。Claude Code経由で色々聞いてみましょう。特にこれと言った切り口、観点が思いつかなかった場合はそのこと自体をClaude Code(を介してMCPサーバに)聞いてみるのも良いでしょう。今回は後者のアプローチでMCPサーバに色々出してもらいました。連携成功です！✌️

![](https://static.zenn.studio/user-upload/a3a82322e995-20260404.png)

![](https://static.zenn.studio/user-upload/a4d36283468f-20260404.png)

![](https://static.zenn.studio/user-upload/c1e34f118270-20260404.png)

![](https://static.zenn.studio/user-upload/c90e9bb18182-20260404.png)

ここまでの流れを一旦整理します。最終的にはやりたいことが実現出来た形です。

```
前提：
- Googleアカウント、Google Cloudプロジェクト、Claude Codeが使えることを確認

Google側準備
- gcloudログイン
- 今回検証用のGoogle Cloudプロジェクトを用意
- API有効化
- 認証部分をサービスアカウントキー利用の方向で準備

環境準備
- uvで環境作成
- githubリポジトリ(google-analytics-mcp)をclone
- 単体動作確認(サーバ起動出来た)

MCP連携
- claude mcp addで追加
- 動作検証を実施
```

## 2. pipx + CLI + ユーザースコープでMCPサーバ連携

上記手順では任意のClaude Codeプロジェクト配下でのみ有効な形(Project Scope)で、uv環境下でGoogle Analytics MCP連携を行いました。続いては、プロジェクトに閉じない形でグローバル(User Scope)にGoogle Analytics MCP連携を行う手順を試してみたいと思います。pipx(Python製のCLIツールを仮想環境ごと安全にインストールして実行するためのツール)を介して対応するCLIを導入し、利用するという手順で進めます。

### pipxによるCLIインストール

まずはpipxの導入から。

```
# brewでpipxインストール.
% brew install pipx
% pipx ensurepath

# 今開いているシェルを、新しいログインシェルで置き換えて再起動.
% exec $SHELL -l
```

google-analytics-mcp をCLIとして導入。

```
## インストール.
%  pipx install git+https://github.com/googleanalytics/google-analytics-mcp.git
WARNING: Skipping setuptools as it is not installed.
  installed package analytics-mcp 0.2.0, installed using Python 3.14.3
  These apps are now available
    - analytics-mcp
    - google-analytics-mcp
done! ✨ 🌟 ✨

## インストール確認.
% pipx list
venvs are in /Users/xxxxxxxxxx/.local/pipx/venvs
apps are exposed on your $PATH at /Users/xxxxxxxxxx/.local/bin
manual pages are exposed at /Users/xxxxxxxxxx/.local/share/man
   package analytics-mcp 0.2.0, installed using Python 3.14.3
    - analytics-mcp
    - google-analytics-mcp

% command -v google-analytics-mcp
/Users/xxxxxxxxxx/.local/bin/google-analytics-mcp
```

### MCP連携設定

1つめの手順同様、Claudeのmcpコマンドでサービスとして登録します。前述のものと被らないように、今回は`ga4-global-pipx`という名前でサービス登録を行いました。サービスアカウントキーのJSONファイルを`GOOGLE_APPLICATION_CREDENTIALS`の項目に設定するところは一緒です。

```
## さっきとは違うClaude Codeプロジェクトで実行.
% pwd
/xxx/xxx/xxxxxxxx/shinyaa31-claude-code-workspace/shinyaa31-general

## サービス登録.
% claude mcp add -s user ga4-global-pipx \
      -e GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json" \
      -e GOOGLE_CLOUD_PROJECT="shinyaa31-ga-mcp-zenn" \
      -- google-analytics-mcp

## 内容確認(1).
% claude mcp list
Checking MCP server health...
:
ga4-global-pipx: /bin/zsh -lc GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json" GOOGLE_CLOUD_PROJECT="shinyaa31-ga-mcp-zenn" google-analytics-mcp - ✓ Connected
:

## 内容確認(2).
% claude mcp get ga4-global-pipx
ga4-global-pipx:
  Scope: User config (available in all your projects)
  Status: ✓ Connected
  Type: stdio
  Command: google-analytics-mcp
  Args:
  Environment:
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
    GOOGLE_CLOUD_PROJECT=shinyaa31-ga-mcp-zenn

To remove this server, run: claude mcp remove "ga4-global-pipx" -s user
```

pipx + CLI経由でもGoogle Analytics MCPサーバと連携し、欲しい結果が見えることを確認出来ました！

![](https://static.zenn.studio/user-upload/c25e25cdb74e-20260404.png)  
![](https://static.zenn.studio/user-upload/95e297727866-20260404.png)  
![](https://static.zenn.studio/user-upload/d194d8caa4cd-20260404.png)

## 3. Claude Desktop経由でMCPサーバ連携

最後3つめのMCPサーバ連携はClaude Desktopから。設定ファイルはpipx + CLIの時のものを参考にします。

Claude Desktopを起動、画面左下のメニューから[設定]を選択。  
![](https://static.zenn.studio/user-upload/72e00b56bed2-20260404.png)

[開発者]→[設定を編集]を選択。Claude Desktop用の設定JSONファイルが開きますので、今回のGA4用連携設定を追加します。  
![](https://static.zenn.studio/user-upload/1968a1a1809a-20260404.png)

追加する内容は以下の通り。

claude\_desktop\_config.json

```
{
  "mcpServers": {
  	:
    "ga4-global-pipx": {
      "command": "/Users/xxxxxxxxxx/.local/bin/google-analytics-mcp",
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account-key.json",
        "GOOGLE_CLOUD_PROJECT": "shinyaa31-ga-mcp-zenn"
      }
    }
    :
  },
  :
  :
}
```

設定追記完了。  
![](https://static.zenn.studio/user-upload/9993f9b9376d-20260404.png)

Claude Desktopを再起動し、会話してみます。良い感じで結果が返ってきました！  
![](https://static.zenn.studio/user-upload/de4fc27927d5-20260404.png)

![](https://static.zenn.studio/user-upload/f06ea6150934-20260404.png)

![](https://static.zenn.studio/user-upload/4508df540ee1-20260404.png)

## 4. Claude.ai(Web)経由でMCPサーバ連携

同じ流れで、Claude.ai(Web)のコネクタ経由でGoogle Analytics 4のデータ連携出来ないかな？と思い探してみましたが、現時点では特に対応してなさそうでした。

![](https://static.zenn.studio/user-upload/bc8c003d93af-20260423.png)

## まとめ

という訳で、Google Analytics(GA4)とClaude(Claude Code)とのMCPサーバ連携について、幾つかの経路手法で試してみた内容の紹介でした。いずれも設定さえしてしまえば自然言語の依頼でここまで柔軟に、かつ示唆に富んだ情報が収集出来るというのはとても嬉しい限りですね。実際のデータ、データ解析結果を受けての改善活動も気軽かつスピーディに出来そうな気がしてきましたし、今後は様々な環境に対してこの連携を行い、色々改善活動を進めていきたいです。
