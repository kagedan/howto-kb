---
id: "2026-06-18-claude-code-からターミナルだけでfastapi-アプリをデプロイしてみた-01"
title: "Claude Code からターミナルだけで、FastAPI アプリをデプロイしてみた"
url: "https://zenn.dev/kamuidash/articles/6a673850634039"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "Python", "zenn"]
date_published: "2026-06-18"
date_collected: "2026-06-19"
summary_by: "auto-rss"
query: ""
---

## 要約

* AI エージェント（Claude Code）に「アプリを作って、GitHub に push して、デプロイして」と頼むだけで、ブラウザのダッシュボードを一度も触らずに FastAPI アプリを本番公開できた。
* PaaSのKamuiDash（ <https://kamui-platform.com/ja/> ）が提供する MCP サーバーを使いました。create\_project / create\_app / list\_deploy\_runs / get\_app\_logs といった操作を、Claude Code から自然言語で呼び出せる。
* 結果、東京リージョンの公開 URL から HTTP 200、定常レスポンスは約 0.13 秒。無料プランでもスリープしない（コールドスタートなし）。
* 「作る→上げる→確認する」ループは完全に CLI / Claude Code から完結する。ただし、GitHub repoとKamuiDashの連携時のみブラウザでワンタップ必要。

## なぜ「AI エージェント × PaaS」なのか

* 最近はコードを書くのも調べ物をするのも Claude Code に任せる時間が増えました。一方でデプロイ周りだけは、結局ブラウザでダッシュボードを開いて、ポチポチ設定して……という手作業が残りがちです。
* ここで効いてくるのが MCP（Model Context Protocol）。PaaS 側が MCP サーバーを用意していれば、AI エージェントは「プロジェクトを作る」「アプリをデプロイする」「ログを見る」といった操作をツールとして直接呼べます。KamuiDash はこの MCP/CLI に対応しているので、今回はそれを使ってみました。

## 準備：CLI と MCP 接続

使うもの: kamui CLI（KamuiDash） / Claude Code / gh（GitHub CLI）。バージョン確認の例:

```
$ kamui --version
kamui version 0.1.18
$ claude --version
2.1.x (Claude Code)
$ gh --version
gh version 2.88.x
```

KamuiDash の MCP を Claude Code に接続します。トークンを画面に出さず、ファイルに書き出して Claude Code へ自動登録する --register を使うのが安全です。

```
$ kamui login            # ブラウザで GitHub OAuth（一度きり）
$ kamui mcp setup --register --token-file ~/.kamui/mcp-pat --client claude-code
```

発行される Personal Access Token は不要になったら kamui tokens delete でいつでも失効できます。

接続確認:

```
$ claude mcp list
kamui: https://api.kamui-platform.com/mcp (HTTP) - Connected
```

![](https://static.zenn.studio/user-upload/11b031496c85-20260617.png)

念のため、Claude Code 経由で「今ログイン中のアカウントのプロジェクト一覧を見せて」と頼み、想定どおりのアカウント（＝デプロイ先）に繋がっているかを最初に確認しておくと安心です。

## ステップ 1：FastAPI サンプルを Claude Code に作らせて GitHub へ

Claude Code にこう頼みました。  
「最小の FastAPI アプリを作って。GET / は Hello メッセージと region: tokyo を返す。GET /health は status: ok を返す。末尾で os.environ.get(PORT, 8000) を読み uvicorn で起動。requirements は fastapi と uvicorn[standard]。git init して gh で新規パブリックリポジトリを作成して push して。」

ポイントは KamuiDash の Python アプリが python main.py で起動されること。なので Uvicorn は main.py の中から、環境変数 PORT を読んで起動するように書きます。

```
# main.py
import os
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from KamuiDash!", "region": "tokyo"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

requirements.txt は fastapi と uvicorn[standard] の2行だけ。Claude Code が git init からコミット、gh repo create、push まで実行し、kamuiplatform/kamuidash-fastapi-demo ができあがりました。

## ステップ 2：MCP で create\_project から create\_app

ここからが本番。

Claude Code に以下の様に指示しました。

```
「KamuiDash の MCP で kamuiplatform/kamuidash-fastapi-demo の main を本番デプロイして」
```

以下のことをどんどん進めてくれます。

* create\_project（名前 demo / Free / Tokyo）
* create\_app（Python / そのリポジトリ / setup: pip install -r requirements.txt / start: python main.py / レプリカ1 / Free）
* list\_deploy\_runs と公開 URL の確認

途中repoとKamuiDashの連携が必要になりますが、AIがどうすれば良いか教えてくれます。  
![](https://static.zenn.studio/user-upload/f88a4ba85384-20260617.png)

## ステップ 3：デプロイ状況を AI に確認させる

ビルド中は Claude Code に状況を見させます。list\_deploy\_runs で deploying から success を追跡し、転けたら get\_deploy\_run\_logs、起動後は get\_app\_logs でアプリログを確認、という流れ。  
すべて MCP 経由なので、やはりブラウザは不要です。  
数分後、deploy: success / pod: running になり、公開 URL が発行されました。

![](https://static.zenn.studio/user-upload/5d5a78986817-20260617.png)

## 結果：公開 URL の疎通とレスポンス実測

東京リージョンの公開 URL に対して、ルート / を 3 回叩いて応答時間を実測しました。

```
$ for i in 1 2 3; do curl -s -o /dev/null -w "HTTP %{http_code} total=%{time_total}s\n" https://<app>.kamui-platform.com/ ; done
HTTP 200 total=1.127280s
HTTP 200 total=0.139520s
HTTP 200 total=0.127239s
```

3 回とも HTTP 200。初回は TLS / 接続確立込みで約 1.1 秒、以降は約 0.13 秒で安定。KamuiDash は無料プランでもアプリをスリープさせない設計なので、「最初のアクセスだけ数十秒待たされる」タイプのコールドスタートはありません。レスポンス本体は GET / が Hello メッセージ + region: tokyo、GET /health が status: ok を返します。

![](https://static.zenn.studio/user-upload/91456f77a70c-20260617.png)

## まとめ

「アプリを作って」「デプロイして」「ログ見せて」を会話で投げるだけで、FastAPI アプリが東京リージョンで本番稼働しました。Dockerfile も CI 設定も書いていません。AI コーディングの流れを止めずに、そのまま本番まで持っていける体験はかなり良いです。KamuiDash は無料プランから試せて、コールドスタートもありません。手元Vibe Codingしつつアプリをサクッとホストしたい人は是非触ってみてください。

KamuiDash: <https://kamui-platform.com/ja/>  
ドキュメント（MCP セットアップ）: <https://docs.kamui-platform.com/ja/mcp.html>
