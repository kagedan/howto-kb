---
id: "2026-03-31-mcpサーバーを自分で作ってみる-hotpepper-api-01"
title: "MCPサーバーを自分で作ってみる / HOTPEPPER API"
url: "https://qiita.com/cecil_/items/c2a1fe09c47e9bc9700e"
source: "qiita"
category: "ai-workflow"
tags: ["MCP", "API", "LLM", "qiita"]
date_published: "2026-03-31"
date_collected: "2026-03-31"
summary_by: "auto-rss"
---

## はじめに

何かと話題のLLM（大規模言語モデル）。時代に置いていかれないよう、自分でも何か作ってみようと思い立ち、簡単にですがMCPサーバーを実装してみました。

## この記事でわかること

# MCPの概要

## MCPとは

MCPとは **Model Context Protocol** の略称で、AIモデルと外部システムを接続するための共通プロトコルです。

従来、AIに外部の情報や機能を使わせるためには、連携先ごとに個別のAPI設計と実装が必要でしたが、MCPの登場によりそんなめんどくさいことをする必要が無くなりました。

よく見かけるわかりやすい図↓  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3951996%2Fb0fc7174-8ed4-4858-b659-28525f1989c8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=888c294cfe6bc54b0327463c1940f8d1)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3951996%2Fb0fc7174-8ed4-4858-b659-28525f1989c8.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=888c294cfe6bc54b0327463c1940f8d1)  
（引用：<https://norahsakal.com/blog/mcp-vs-api-model-context-protocol-explained/> ）

## MCPサーバーとは

図でいうところのケーブルがMCPサーバーです。  
ホストを介してAIからの要求を受け取り、対応する処理を実行して結果を返す役割を担います。

MCPサーバーが外部に公開できる機能は、主に以下の3種類です。

* Tools ... APIの実行、コードの自動作成、ブラウザ操作（Puppeteer）、Git操作など、AIがアクションを起こす機能
* Resources ... ファイル内容やデータベースなど、AIが参照できる構造化データを提供
* Prompts ... 定型作業や特定のタスクに適した、AI向けの指示テンプレート

最近では、様々なサービスが公式のMCPサーバーを公開していますが、今回はこちらを自作してみよう。ということです。

# 実装したもの

MCPについてざっくり理解できたところで、実装したものの説明です。  
今回はアカウント登録をすれば無料で利用できるホットペッパーグルメAPIを利用した、ホットペッパーMCPを実装しました。

Claude DesktopやCursorなどのMCPクライアントから「渋谷で個室のある居酒屋を探して」と話しかけるだけでお店が検索できるようになる、とイメージしていただければよいです。

## 事前準備

前述したとおり、今回はホットペッパーAPIを利用しますので、アカウント登録しAPIキーを取得しましょう。  
<https://webservice.recruit.co.jp/register>

## 実装

必要なもの

```
Python 3.12.10
FastMCP
uv（またはpip）
Claude Desktop
```

プロジェクト作成

```
mkdir hotpepper-mcp
cd hotpepper-mcp
```

pyproject.toml を作成します。

pyproject.toml

```
[project]
name = "hotpepper-mcp"
version = "0.1.0"
description = "ホットペッパーグルメAPI MCP Server"
requires-python = ">=3.12"
dependencies = [
    "fastmcp",
    "httpx",
    "python-dotenv",
]
```

### 依存関係をインストール

### APIキーの設定

.env ファイルを作成して APIキーを書き込みます。

.env

```
HOTPEPPER_API_KEY="事前準備で取得しておいたAPIキー"
```

（Gitに上げない場合は不要ですが）

```
echo ".env" >> .gitignore
```

### MCPサーバー実装

ホットペッパーAPIが公開している 全11種類のAPI をツールとして実装します。  
まずは動作するかを確認したいのでミニマムに1つだけ実装してみます。

server.py

```
import os
import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

API_KEY = os.getenv("HOTPEPPER_API_KEY")
BASE_URL = "https://webservice.recruit.co.jp/hotpepper"

mcp = FastMCP("hotpepper-mcp")

def _build_params(extra: dict = {}) -> dict:
    params = {"key": API_KEY, "format": "json"}
    params.update({k: v for k, v in extra.items() if v is not None})
    return params

async def _get(path: str, params: dict) -> dict:
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BASE_URL}{path}", params=params)
        res.raise_for_status()
        return res.json()

@mcp.tool
async def get_large_service_areas() -> dict:
    """
    ホットペッパーの大サービスエリアマスタを取得します。
    関東・関西など大きなエリア区分のコードと名称の一覧が返ります。
    エリアコードはグルメサーチAPIのlarge_service_areaパラメータで使用できます。
    """
    params = _build_params()
    return await _get("/large_service_area/v1/", params)

if __name__ == "__main__":
    mcp.run()
```

### Claude Desktopへの登録

今回はホストにClaude Desktopを利用するのでClaude Desktopでの設定例です。  
設定ファイル（claude\_desktop\_config.json）を編集し、ホストがMCPサーバーを読み込めるようにします。  
パスはユーザー配下の %APPDATA%\Claude\claude\_desktop\_config.json  
※一度もClaude Desktopを起動していないと作られていない可能性があります。

claude\_desktop\_config.json

```
{
  "mcpServers": {
    "hotpepper": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "自身のプロジェクトのパス",
        "python",
        "server.py"
      ]
    }
  }
}
```

## 動作確認

### 読み込み確認

Claude Desktopを再起動後、MCPサーバーが正常に読み込まれているかまずは確認します。  
※修正後はタスクマネージャーから一度完全に落としてくださいね。

設定>開発者>ローカルMCPサーバーから確認できます。下記のように"running"となっていればOK。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3951996%2F3e235bc7-0032-48eb-a5db-325f6e90056c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=09d719154afa4498cd04c79368c9e02c)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3951996%2F3e235bc7-0032-48eb-a5db-325f6e90056c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=09d719154afa4498cd04c79368c9e02c)

### 動作確認

正常に読み込めていることが確認出来たら、適当に話しかけてみましょう。  
飲食店調べてくらいの問いかけであれば、今回実装するツールなしでも返答が来てしまうので、今回は明示的にツールを用いて検索するように問いかけます。

[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3951996%2Fd2ffa673-8d31-445c-b638-fe10ed71bf9d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=18a7375c8aaefa2bed6bfa75ae98262f)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3951996%2Fd2ffa673-8d31-445c-b638-fe10ed71bf9d.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=18a7375c8aaefa2bed6bfa75ae98262f)

新規追加後は、下記のようにツールの利用許可画面がでますので許可してあげましょう。  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3951996%2Fcdce0886-e570-4905-98a2-614d5f24b44c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cbd18248b6712b81c5f83d99349d48c7)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3951996%2Fcdce0886-e570-4905-98a2-614d5f24b44c.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=cbd18248b6712b81c5f83d99349d48c7)

正常に動作しました。  
"Get large service areas"から、先ほど追加したツールを用いて返答されたことがわかります。  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3951996%2F304783a4-ee43-479a-8897-a21dbb2c5eb7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7369abfaf75feda1385b4d479cda13ab)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3951996%2F304783a4-ee43-479a-8897-a21dbb2c5eb7.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=7369abfaf75feda1385b4d479cda13ab)

ひとまずツールを実装し、ホストに読み込ませることには成功しましたが、現段階では"大サービスエリア"を取得してくることしかできません。なぜならそのようにしか実装していないから。  
AIは優秀なので、与えられたツール以外を使うなと言わなければ、いいようにこちらに情報を返してくれちゃいます。  
ですが、APIで取得した値ではないので確実性が無かったり、そもそも今回はツールを使ってもらって返答してもらうのが目的なので、同様に他のAPIのツールも実装しましょう。

基本的にはシンプルに実装していけばよいのですが、グルメサーチAPIや店名サーチAPIなどが持っているkeywordパラメータの影響が大きく、これと推測である程度返答ができてしまうので"推測するな、マスタAPIを先に叩け keywordはあくまで補助、最後の切り札に使え"とか、"検索はこの手順でやれ"と、Docstringに明示的に書いておくのが良いかと思います。  
ここを厳しく記載し過ぎると次はツールを使おうとしてくれない。という問題もあるので塩梅が難しいです。

### 諸々実装した後

無事、期待通り動作するようになりました。  
[![image.png](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3951996%2F1a7f21fa-8c2f-49d2-8f5e-4189e49f001b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f93930167ecebd883ec98826f1e81132)](https://qiita-user-contents.imgix.net/https%3A%2F%2Fqiita-image-store.s3.ap-northeast-1.amazonaws.com%2F0%2F3951996%2F1a7f21fa-8c2f-49d2-8f5e-4189e49f001b.png?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=f93930167ecebd883ec98826f1e81132)

# まとめ

この記事では、ホットペッパーグルメAPIをFastMCPでMCPサーバー化する手順を紹介しました。

とりあえず実用レベルまでは持っていけました。ただ、Docstring を工夫して記載しないと挙動が安定しなかったり、"ホットペッパーで"のように付けてあげないとツールを使ってくれないことがあったりで、まだまだ改善ポイントは多そうです。引き続き試行錯誤中です。

上記をはじめとし改善できる点は他にも多々あるかと思いますが、筆者はひよっこなので大目に見てください。
