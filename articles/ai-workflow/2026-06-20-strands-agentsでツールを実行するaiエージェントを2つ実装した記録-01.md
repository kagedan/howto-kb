---
id: "2026-06-20-strands-agentsでツールを実行するaiエージェントを2つ実装した記録-01"
title: "Strands Agentsでツールを実行するAIエージェントを2つ実装した記録"
url: "https://zenn.dev/satoru_o/articles/efaa935d1e4cdd"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "prompt-engineering", "API", "AI-agent", "Python", "TypeScript"]
date_published: "2026-06-20"
date_collected: "2026-06-21"
summary_by: "auto-rss"
query: ""
---

## はじめに

ローカルのDev Container環境で、Strands Agentsを使ってツールを実行できるAIエージェントを2種類実装しました。1つはMCP(Model Context Protocol)サーバー経由でファイル操作を行うエージェント、もう1つは自作ツールでgit diffを取得し、コミットメッセージを提案するエージェントです。

公式ドキュメントのサンプルコード自体は数十行程度で動くようになっていますが、実際にAmazon Bedrock経由でツールを呼び出すと、モデルIDの指定方法やモデルアクセスの権限設定でいくつかのエラーに遭遇しました。特にBedrockの推論プロファイル(モデルIDの先頭に付くプレフィックス)は、リージョンとモデルの世代によって必要・不要が変わるため、ドキュメントを一度読むだけでは気づきにくい部分です。

この記事では、次の内容を扱います。

* Strands Agentsの最小構成(Hello World)の実行
* MCPサーバーをツールとして使うエージェントの実装と、そこで発生したBedrockのモデルアクセス・推論プロファイル関連のエラー
* 自作の`@tool`でgit diffを取得し、コミットメッセージを提案するエージェントの実装と、git diffの仕様に関連するエラー
* Strands Agentsというフレームワーク自体の概要

## 実行環境

VS CodeのDev Container上で作業しました。Pythonの依存関係管理には`uv`を使い、AWSへの認証はIAM Identity Center(SSO)経由のプロファイルで行っています。Bedrockの呼び出しリージョンは東京(ap-northeast-1)です。AgentCore Runtimeなどへのデプロイは今回は行わず、すべてローカル実行の範囲で確認しています。

使用したSSO権限セットの権限は、AWSマネージドポリシーの`ReadOnlyAccess`に、以下のインラインポリシーを追加した構成です。Bedrockのモデル呼び出し(`bedrock:InvokeModel`、`bedrock:InvokeModelWithResponseStream`)のみを許可し、それ以外は読み取り専用に絞っています。

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Statement1",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```

## Hello World

Strands Agentsは、`Agent()`を呼ぶだけでBedrock経由のモデルとやり取りできます。

```
uv run --with strands-agents python -c "from strands import Agent; print(Agent()('Hello, world! 自己紹介して'))"
```

ツールを何も渡さない状態であれば、この1行だけでモデルからの応答が返ってきました。

## MCPサーバーをツールとして使うエージェント

### 実装

ローカルのファイルシステムに対してファイルの読み書きやディレクトリ一覧の取得を行う、`mcp-server-filesystem`というMCPサーバーをツールとしてエージェントに渡しました。エージェントが操作できる範囲を限定するため、操作対象は専用の`sandbox`ディレクトリだけに絞っています。

```
from pathlib import Path

from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

# このエージェントがファイル操作していい範囲をここだけに絞る
SANDBOX_DIR = Path(__file__).parent / "sandbox"
SANDBOX_DIR.mkdir(exist_ok=True)

filesystem_mcp = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="mcp-server-filesystem",
        args=[str(SANDBOX_DIR)],
    )
))

with filesystem_mcp:
    tools = filesystem_mcp.list_tools_sync()
    agent = Agent(
        tools=tools,
        model="jp.anthropic.claude-haiku-4-5-20251001-v1:0",
        system_prompt="あなたはファイル操作ができるアシスタントです。指定されたディレクトリの中でのみファイルを読み書きできます。",
    )
    agent(
        "sandboxフォルダに memo.txt というファイルを作って、"
        "「AgentCoreとMCPのテスト成功」と書き込んで。"
        "書き終わったら、フォルダの中身一覧も確認して教えて。"
    )
```

MCPサーバーとの接続にはStrands Agentsが提供する`MCPClient`を使います。サーバー起動時に`list_tools_sync()`でツールの一覧を取得し、そのまま`Agent`の`tools`引数に渡すだけで、エージェントはMCP経由のファイル操作ツールを使えるようになります。

### モデルアクセス権限でのエラー

`model`を指定せずに実行したところ、以下のエラーが発生しました。

```
botocore.errorfactory.AccessDeniedException: An error occurred (AccessDeniedException) when
calling the ConverseStream operation: Model access is denied due to IAM user or service role
is not authorized to perform the required AWS Marketplace actions (aws-marketplace:ViewSubscriptions,
aws-marketplace:Subscribe) to enable access to this model.
```

**原因**: Anthropicのモデルなど、Bedrockでサードパーティから提供されているモデルは、アカウント内で初めて呼び出す際にAWS Marketplace経由のサブスクリプションが自動的に開始される仕様になっています。このとき呼び出し元のIAMロールに`aws-marketplace:Subscribe`などの権限がないと、自動サブスクリプションが失敗してこのエラーになります。

**対策**: Bedrockコンソールの「Model access」画面で対象モデルへのアクセスを一度有効化すると、以降はアカウント内のどのIAMロールも、Marketplace権限を個別に持たなくてもそのモデルを呼び出せるようになります。

### 推論プロファイルIDの指定でのエラー

モデルアクセスを有効化した後、モデルIDをベースモデルID(`anthropic.claude-haiku-4-5-20251001-v1:0`)のまま指定して実行すると、別のエラーになりました。

```
botocore.errorfactory.ValidationException: An error occurred (ValidationException) when calling
the ConverseStream operation: Invocation of model ID anthropic.claude-haiku-4-5-20251001-v1:0
with on-demand throughput isn't supported. Retry your request with the ID or ARN of an
inference profile that contains this model.
```

メッセージに従って米国向けの推論プロファイルID(`us.anthropic.claude-haiku-4-5-20251001-v1:0`)に変更したところ、今度はモデルIDが無効というエラーになりました。

```
botocore.errorfactory.ValidationException: An error occurred (ValidationException) when calling
the ConverseStream operation: The provided model identifier is invalid.
```

**原因**: Claude Haiku 4.5やSonnet 4.6のような比較的新しい世代のモデルは、Bedrockのオンデマンド呼び出しにおいてベースモデルIDではなく推論プロファイルID(クロスリージョン推論プロファイル)を指定する必要があります。推論プロファイルIDには対応する地理的リージョン群を示すプレフィックスが付いており、東京リージョン(ap-northeast-1)から呼び出す場合、米国向けの`us.`プレフィックスは無効なIDとして扱われます。東京・大阪間でリクエストを処理する日本向けのプレフィックスは`jp.`です。

**対策**: モデルIDを`jp.anthropic.claude-haiku-4-5-20251001-v1:0`に変更したところ、エラーは解消しました。実行すると、エージェントは`write_file`と`list_directory`の2つのツールを自律的に呼び出し、`sandbox/memo.txt`の作成とフォルダ内容の確認を完了しました。

## 自作ツールでgit diffからコミットメッセージを作るエージェント

### 実装

`@tool`デコレータを使うと、Python関数をそのままエージェントのツールとして登録できます。git の差分を取得する関数をツール化し、その結果をもとにコミットメッセージを提案させるエージェントを作りました。最終的なコードは以下の通りです。

```
import subprocess
from strands import Agent, tool

@tool
def get_repository_diff() -> str:
    """
    Gitリポジトリ全体の変更(diffや新規ファイル)を取得します。
    カレントディレクトリに関わらず、リポジトリ全域の変更を網羅します。
    """
    # 1. Gitリポジトリのルートディレクトリを取得
    res_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if res_root.returncode != 0:
        return "エラー: ここはGitリポジトリ内ではないか、Gitがインストールされていません。"
    git_root = res_root.stdout.strip()

    # 2. ステージング済みの差分を確認
    res_staged = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, cwd=git_root)
    if res_staged.stdout.strip():
        return f"--- ステージング済みの差分 ---\n{res_staged.stdout}"

    # 3. 通常の差分を確認
    res_workdir = subprocess.run(["git", "diff"], capture_output=True, text=True, cwd=git_root)
    if res_workdir.stdout.strip():
        return f"--- 未ステージングの差分 ---\n{res_workdir.stdout}"

    # 4. diffには映らない「新規作成ファイル(未追跡)」がないか確認
    res_status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=git_root)
    if res_status.stdout.strip():
        return (
            "具体的なコード差分(diff)はありませんが、以下のファイルに変更または新規作成があります:\n"
            f"{res_status.stdout}\n"
            "※新規ファイルの場合は中身のdiffが見えないため、ファイル名から推測してコミットメッセージを提案してください。"
        )

    return "変更の差分(diff)も、新規作成されたファイルもありませんでした。"

agent = Agent(
    tools=[get_repository_diff],
    model="jp.anthropic.claude-haiku-4-5-20251001-v1:0",
    system_prompt=(
        "あなたはGitのコミットメッセージを生成する優秀なエンジニアです。\n"
        "必ず最初にツールを使ってリポジトリのdiffやステータスを取得してください。\n"
        "得られた情報を分析し、複数のコミットメッセージの候補(Conventional Commitsに準拠したもの、シンプルなものなど)を日本語で提案してください。"
    )
)

print("エージェントがGitの差分を調査中...")
response = agent("リポジトリの変更を確認して、適切なコミットメッセージをいくつか考えて！")
```

ここまでの構成に至るまで、3つのエラーに遭遇しました。

### モデルのアクセス権限でのエラー(別モデルでも発生)

最初は、低コストで動作が安定しているモデルとして`anthropic.claude-3-haiku-20240307-v1:0`を指定しました。実行すると、ファイル操作エージェントで遭遇したものと同種の`AccessDeniedException`(AWS Marketplaceのサブスクリプション関連)が発生しました。

**原因**: モデルアクセスの有効化はモデルごとに個別に行われます。Claude Haiku 4.5へのアクセスは既に有効化されていましたが、Claude 3 Haikuについては別途有効化が必要だったと考えられます。

**対策**: コンソールでの再有効化を待つ代わりに、既に動作確認済みの`jp.anthropic.claude-haiku-4-5-20251001-v1:0`に変更しました。これによりエラーは解消しました。

### git diffがカレントディレクトリに依存する問題

モデルのエラーを解消した後にエージェントを実行すると、「変更がない」という応答が返ってきました。実際にはリポジトリ内に変更が存在していたため、検出漏れが起きていました。

```
# 修正前: subprocess.run はカレントディレクトリを基準に実行される
res_workdir = subprocess.run(["git", "diff"], capture_output=True, text=True)
```

**原因**: `subprocess.run(["git", "diff"], ...)`はカレントディレクトリを基準に実行されます。スクリプトをリポジトリのサブディレクトリで実行していたため、そのディレクトリ以下の変更しか確認できていませんでした。

**対策**: `git rev-parse --show-toplevel`でリポジトリのルートパスを取得し、`subprocess.run`の`cwd`引数にそのパスを渡すようにしました。これにより、スクリプトをどの階層で実行してもリポジトリ全体の差分を取得できるようになりました。

### 新規作成ファイルがdiffに表示されない問題

ルートディレクトリを基準にした後も、新しく作成したばかりのファイルについては「変更がない」という応答が返ってくることがありました。

**原因**: `git diff`は、一度もコミットやステージングをされていない新規ファイル(未追跡ファイル)を対象に含めません。これはgit diffコマンド自体の仕様であり、新規ファイルの内容を確認するには別の手段が必要です。

**対策**: `git status --porcelain`の結果も取得し、`git diff`で差分が見つからない場合のフォールバックとして使うようにしました。これにより、未追跡ファイルが存在する場合もエージェントがその情報を認識できるようになりました。

### 実行結果

`experiments/`ディレクトリを新規追加した状態で実行したところ、エージェントは新しいディレクトリの存在を検出し、Conventional Commits形式を含む複数のコミットメッセージ案を提示しました。この時点では`git status`から得られるファイル名の情報しかないため、提案内容は「実験用ディレクトリの追加」といった推測に基づくものでした。

対象のファイルを`git add`してから再度実行すると、`git diff --cached`によってステージング済みの差分(実際のコード内容)が取得できるようになり、「MCPクライアントを使用したファイル操作エージェントの実装」のように、変更内容を反映したより具体的な提案が返ってきました。これは観察であり、エージェントが受け取れる情報の解像度がdiffの有無によって変わることを示しています。

## Strands Agentsとは

Strands Agentsは、AWSが2025年5月に公開したオープンソースのAIエージェント構築用SDKです。Python版に加えてTypeScript版も提供されています。

特徴的なのは、エージェントの振る舞いを事前にワークフローとしてコード化するのではなく、モデル自身に次の行動を判断させる「モデル駆動」のアプローチを採用している点です。エージェントは「モデル」「ツール」「プロンプト」の3要素の組み合わせとして定義され、与えられたツールをいつ・どのように使うかはモデル自身が判断します。AWS社内でもAmazon Q DeveloperやAWS Glueなどのプロダクトで、エージェント機能の実装にStrands Agentsが使われています。

ツールの追加方法は大きく2つあります。1つは今回のgit diffエージェントのように、Python関数に`@tool`デコレータを付けてそのままツール化する方法です。もう1つは今回のファイル操作エージェントのように、MCP(Model Context Protocol)サーバーに接続し、サーバー側が提供するツール群を`MCPClient`経由で取り込む方法です。MCPはAIエージェントとツール提供サーバーの間の通信を標準化するプロトコルで、Strands Agentsはこれをネイティブにサポートしています。

モデルプロバイダーについては、Amazon Bedrock以外にもAnthropicのAPIなど複数のプロバイダーに対応しており、特定のモデルやクラウドに縛られない設計になっています。今回のようにAmazon Bedrockをモデルプロバイダーとして使う場合、Strands Agents自体のAPIはシンプルですが、Bedrock側のモデルアクセス設定や推論プロファイルの仕様がエージェントの動作にそのまま影響します。今回遭遇したエラーの大半は、Strands Agentsそのものの問題ではなく、Bedrockでモデルを呼び出す際に共通して発生し得るものでした。

## まとめ

Strands Agentsを使うと、MCPサーバー連携・自作ツールのいずれの方法でも、数十行程度のコードでツールを実行するエージェントを構築できました。一方で、Amazon Bedrockをモデルプロバイダーとして使う場合は、モデルアクセスの有効化(Marketplaceサブスクリプション)と、モデルの世代・呼び出しリージョンに応じた推論プロファイルIDの指定という、Bedrock側の事情に起因するエラーに複数回遭遇しました。これらは他のフレームワークでBedrockを使う場合にも当てはまる点だと考えられます。

今回はローカル実行の範囲にとどめたため、AgentCore Runtimeなどを使ったAWS上へのホスティングは今後の課題です。

## 参考資料
