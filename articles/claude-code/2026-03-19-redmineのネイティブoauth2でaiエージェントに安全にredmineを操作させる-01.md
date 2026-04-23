---
id: "2026-03-19-redmineのネイティブoauth2でaiエージェントに安全にredmineを操作させる-01"
title: "RedmineのネイティブOAuth2でAIエージェントに安全にRedmineを操作させる"
url: "https://qiita.com/ssc-ksaitou/items/b7a4d51ed78fa6e45521"
source: "qiita"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "qiita"]
date_published: "2026-03-19"
date_collected: "2026-03-23"
summary_by: "auto-rss"
---

## TL; DR

Redmine 6.1 のネイティブ OAuth2 + ゲートウェイで client\_secret を集約し、CLI ツールがトークンを隠蔽することで、API キー不要・スコープ制限付き・AI コンテキストへのトークン漏洩なしで Redmine を操作させる構成について述べた記事です。

## はじめに

チームで Redmine と Claude Code を併用していると、**チケットの内容をブラウザからコピーして AI に貼り付け、作業結果をまたコピーしてチケットに書き戻す場面によく遭遇します。** 自分もチームメンバーもこの手作業を繰り返していました。

AI にチケットを直接読み書きさせれば済む話ですが、既存の MCP サーバや CLI ツールは利用者の全操作権限を永続的に付与する Redmine API キーを要求するため、**権限が広すぎる・漏洩すると大変（全員にAPIキーを発行させたくない）** という問題があります。

そんな折、 **[Redmine 6.1](https://www.redmine.org/news/156)（[2025年9月リリース](https://www.redmine.org/projects/redmine/wiki/Changelog_6_1)）で OAuth2 プロバイダ機能が[ネイティブサポート](https://www.redmine.org/issues/24808)されました。** OAuth2 を使えば **API キーの事前発行・保管が不要になり、スコープで権限を絞った期限付きの一時トークンを発行できます。** 本記事では、この機能を使って AI エージェントに安全に Redmine を操作させる構成を紹介します。

なお、既存の Redmine MCP 実装も調べましたが、多くは認証方式が API キーのみでした。案件ごとに分かれる複数の Redmine インスタンスを扱いたかったこともあり、今回は MCP ではなく CLI ツール＋スキルという構成を選びました。Redmine 自体は REST API を備えているので、OAuth トークンさえ渡せばエージェント自身の Redmine REST API の知識で操作してくれます。[1](#fn-1)

……と思っていたら、[redmine-mcp-server](https://github.com/jztan/redmine-mcp-server)（2026年2月の v0.5.0 以降）が OAuth2 に対応していました。ただし、MCP サーバはローカルで起動する形態が一般的なため、各ユーザの MCP 設定に `client_secret` を配布する必要があります。本記事のゲートウェイ構成であれば `client_secret` をゲートウェイに集約でき、ユーザには `client_id` とゲートウェイ URL のみ共有すれば済みます。

## 構成概要

今回の構成は 3 つのコンポーネントで成り立っています。

1. **Redmine 6.1** — OAuth2 プロバイダ（認可サーバ兼リソースサーバ）
2. **OAuth ゲートウェイ** — `client_secret` を安全に保持し、トークン交換を仲介するサーバ（Cloudflare Workers + KV 等で構築可能）
3. **CLI ツール**（Python）— PKCE 付き OAuth2 クライアント + REST API クライアント

また、3 の利用方法と Redmine REST API の叩き方や必要になる OAuth2 スコープについて、Claude Code 向けにスキルを構築します。

CLI ツールは OAuth で発行されたトークンをツール内に隠蔽し、AI エージェントがトークンの値を直接見ることはありません（詳しくは後述）。

## Redmine 側のセットアップ

Redmine 6.1 で OAuth2 を有効にする手順です。

1. **REST API の有効化**: 管理 → 設定 → API → 「REST による Web サービスを有効にする」にチェック
2. **OAuth2 アプリケーションの登録**: 管理 → アプリケーション → 「新しいアプリケーション」
   * **名前**: 任意（例: `ai-agent`）
   * **リダイレクトURI**: ゲートウェイの URL（例: `https://oauth-gw.example.com/callback`）。ゲートウェイが認可コードを受け取り、CLI のローカルサーバへ中継します。
   * **Scopes**: AI に操作を認めるスコープを**すべて選択**します。ここで選択したスコープが上限となり、実際の認可時にはユーザがブラウザ上で AI がリクエストしたスコープを確認・承認します
3. 作成後に表示される**アプリケーションID**と**シークレット**を控えておく

シークレットは作成直後の画面でしか表示されません。この画面を閉じると二度と確認できないので、必ずこのタイミングで控えてください。

スコープの例（`value` 属性の物理名）:

| カテゴリ | スコープ |
| --- | --- |
| プロジェクト | `view_project`, `search_project`, `add_project`, `edit_project`, `close_project`, `delete_project`, `view_members`, `manage_members`, `manage_versions` |
| チケットトラッキング | `view_issues`, `add_issues`, `edit_issues`, `edit_own_issues`, `copy_issues`, `add_issue_notes`, `edit_issue_notes`, `edit_own_issue_notes`, `delete_issues`, `manage_subtasks`, `manage_issue_relations`, `manage_categories` |
| Wiki | `view_wiki_pages`, `view_wiki_edits`, `edit_wiki_pages`, `rename_wiki_pages`, `delete_wiki_pages`, `export_wiki_pages`, `manage_wiki` |
| 時間管理 | `view_time_entries`, `log_time`, `edit_time_entries`, `edit_own_time_entries` |
| ニュース | `view_news`, `manage_news`, `comment_news` |
| フォーラム | `view_messages`, `add_messages`, `edit_messages`, `delete_messages` |
| リポジトリ | `view_changesets`, `browse_repository`, `commit_access`, `manage_repository` |
| 文書 | `view_documents`, `add_documents`, `edit_documents`, `delete_documents` |
| ファイル | `view_files`, `manage_files` |
| Administration | `admin`（全権限） |

上記は代表的なものの抜粋で、実際にはさらに細かいスコープ（ウォッチャー操作、プライベート設定等）が存在します。また、導入しているプラグインによっても新しいスコープが追加される場合があります（ただし対応する REST API が無いこともあります）。

AI はスコープ選択を失敗しがちなので、後述するAI用のスキルにユースケースごとどのスコープが必要なのかきちんと書いておくとよいでしょう。

## OAuth ゲートウェイ

OAuth2 の仕組み上、トークン交換時に `client_secret` が必要です。しかし CLI ツール（パブリッククライアント）に `client_secret` を埋め込むのは安全ではありませんし、利用者ごとにアプリケーションとシークレットを作る必要が出てきます。

そこでゲートウェイサーバを配置し、以下の役割を持たせます。今回は Cloudflare Workers + KV で実装しました。

* `client_id` `client_secret` をシークレットストアや環境変数に保管
* CLI からのトークン交換リクエストを受け取り、`client_secret` を付与して Redmine に中継
* Redmine からの認可レスポンスを受け取り、CLI（`http://localhost:*` でリッスン中）へリダイレクト
  + ゲートウェイは Redmine から取得した access\_token を保持せず、CLI へただちに中継する設計とします

CLI は `client_secret` を一切知らないため、CLI のコードが漏洩しても `client_secret` は安全です。各ユーザの CLI に `client_secret` を配布する必要がなく、ゲートウェイの URL だけを共有すれば済みます。

## OAuth クライアント（CLI）

ゲートウェイサーバとのやり取り、Redmineから発行されゲートウェイサーバを通じて入手した一時認可トークンの隠蔽を提供しRedmine APIの操作を提供するPythonスクリプトです。OS標準インストール済みの純粋なPythonだけで動くように構成したほうがいいでしょう。

### `oauth_cli.py` - トークン取得

PKCE 付き OAuth2 フローを実行し、ブラウザで認可を取得してアクセストークンを返します。以下は簡易なコードイメージです。

oauth\_cli.py（主要部分を抜粋・汎用化）

```
import base64, hashlib, http.server, json, secrets, socketserver
import sys, threading, time, urllib.parse, urllib.request, webbrowser

GATEWAY_URL = "https://oauth-gw.example.com"
CLIENT_ID = "your_client_id"
REDMINE_INSTANCE = "redmine.example.com"

def generate_pkce():
    """PKCE code_verifier / code_challenge を生成"""
    verifier_bytes = secrets.token_bytes(32)
    verifier = base64.urlsafe_b64encode(verifier_bytes).rstrip(b"=").decode("ascii")
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    return verifier, challenge

def generate_state():
    """CSRF 防止用の state パラメータを生成"""
    return secrets.token_urlsafe(32)

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    """ローカルサーバで OAuth コールバックを受信"""
    result = None
    expected_state = None

    def do_GET(self):
        params = urllib.parse.parse_qs(
            urllib.parse.urlparse(self.path).query
        )
        # state の検証（CSRF 防止）
        if params.get("state", [None])[0] != CallbackHandler.expected_state:
            CallbackHandler.result = {"error": "state_mismatch"}
        elif "access_token" in params:
            CallbackHandler.result = {
                "access_token": params["access_token"][0],
                "expires_in": int(params.get("expires_in", ["0"])[0]),
            }
        # レスポンスを返してブラウザタブを閉じてもらう
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>OK</h1><p>Close this window.</p>")

def run_oauth_flow(instance, scope):
    """OAuth2 + PKCE フローを実行"""
    verifier, challenge = generate_pkce()
    state = generate_state()

    # 空きポートを見つけてコールバックサーバを起動
    import socket
    with socket.socket() as s:
        s.bind(("", 0))
        port = s.getsockname()[1]

    redirect_uri = f"http://localhost:{port}/callback"
    CallbackHandler.expected_state = state
    CallbackHandler.result = None

    server = socketserver.TCPServer(("localhost", port), CallbackHandler)
    server_thread = threading.Thread(target=server.handle_request)
    server_thread.start()

    # ブラウザで認可画面を開く
    auth_params = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "code_verifier": verifier,
        "state": state,
        "scope": scope,
    })
    webbrowser.open(f"{GATEWAY_URL}/{instance}/oauth/authorize?{auth_params}")

    server_thread.join(timeout=300)  # 5分でタイムアウト
    server.server_close()
    return CallbackHandler.result

def main():
    result = run_oauth_flow(REDMINE_INSTANCE, "view_issues add_issue_notes")
    print(json.dumps(result))
```

本記事のサンプルコードでは簡略化のため、`code_verifier` をブラウザの URL パラメータ経由でゲートウェイに渡しています。標準的な PKCE（[RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636)）では `code_verifier` はトークンエンドポイントへのバックチャネルリクエストでのみ送信すべきであり、ブラウザ URL に含めると履歴等から漏洩するリスクがあります。

理想的には CLI⇔ゲートウェイ間とゲートウェイ⇔Redmine 間でそれぞれ独立した PKCE を使用し、ゲートウェイが自前の認可コードを中間発行する設計にすべきです。

### `redmine_api.py` - REST API 呼び出し

取得したトークンを使って Redmine REST API を呼び出します。以下は簡易なコードイメージです。

redmine\_api.py（主要部分を抜粋・汎用化）

```
import json, sys, time, urllib.request, urllib.error
from pathlib import Path

CACHE_PATH = Path.home() / ".cache" / "redmine-oauth" / "tokens.json"

def make_request(instance, scope, api_path, method="GET", data=None):
    """キャッシュからトークンを取得し、Redmine API を呼び出す"""
    token = get_cached_token(instance, scope)
    if token is None:
        print(json.dumps({"error": "token_expired", "message": "oauth_cli.py で再認可してください"}))
        sys.exit(1)

    url = f"https://{instance}{api_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(
        url,
        data=data.encode("utf-8") if data else None,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_cached_token(instance, scope):
    """スコープをキーとしてキャッシュからトークンを取得"""
    if not CACHE_PATH.exists():
        return None
    cache = json.loads(CACHE_PATH.read_text())
    key = f"{instance}|{' '.join(sorted(scope.split()))}"
    entry = cache.get(key)
    if entry is None:
        return None
    if time.time() > entry["created_at"] + entry["expires_in"]:
        return None  # 有効期限切れ
    return entry["access_token"]
```

### ポイント: トークンのキャッシュと隠蔽

`oauth_cli.py` はアクセストークンをローカルファイル（`~/.cache/redmine-oauth/tokens.json`）にスコープをキーとしてキャッシュし、有効期限（デフォルト 2 時間）内であれば再利用します。期限が切れた場合はブラウザを開いて再認可を行います。

なお、Redmine の OAuth2（doorkeeper）はリフレッシュトークンも発行しますが、**リフレッシュトークンは無期限で失効しない**ため、本構成ではリフレッシュトークンを保存しない設計としています。長期有効な認証情報をディスクに置くリスクを避け、2時間ごとにブラウザで明示的に再認可する運用のほうが安全です。

重要な点として、**Redmine が返却した OAuth トークンの値は CLI ツール内に隠蔽し、AI エージェントには一切見せません**。`redmine_api.py` はスコープをキーとしてキャッシュ済みトークンを内部で読み込み、API を呼び出して結果だけを返します。AI がトークンの値を知る必要はなく、知ることもできません。

これは AI のコンテキストにアクセストークンが含まれることによるリスクを防ぐためです。

* **プロンプトインジェクション**: 悪意のあるチケット内容により、AI がトークンを外部に送信させられる可能性
* **会話ログからの漏洩**: 会話履歴がログとして保存される場合、トークンも一緒に残る

OAuth2 でスコープを絞っていても、そのスコープ内の操作を悪用される恐れがあります。トークンを CLI ツール内に閉じ込めることで、こうしたリスクを設計レベルで排除しています。

ただし、AI はユーザと同じ OS ユーザ権限で動作するため、`cat` コマンド等でキャッシュファイルを直接読むことは原理的に可能です。これを言うとAWS CLIのSSOプロファイル認証状態なども該当しはじめるので、現状トータルバランスで手打ちとしています。

## AI への統合（スキル定義）

Claude Code のプラグインスキルとして定義すると、AI がRedmineのURL等が出現したタイミングで自動的にこのワークフローを実行します。

SKILL.md（フロントマター部分）

```
---
name: redmine-access
description: >
  Redmine のチケットや Wiki を操作するスキル。
  ユーザが Redmine の URL（例: https://redmine.example.com/issues/123）や
  Redmine インスタンス名（例: "redmine.example.com のチケット"）に言及した場合に使用する。
allowed-tools:
  - Bash(python3 cli/oauth_cli.py*)
  - Bash(python3 cli/redmine_api.py*)
---
```

AI は以下のステップで Redmine を操作します。

Claude Code: 指示出し

```
https://redmine.example.com/issues/123 の内容を取得して
```

AIが実行するコマンド（ステップ1: トークン取得）

```
$ python3 cli/oauth_cli.py --instance redmine.example.com --scope "view_issues add_issue_notes"
{"success": true, "scope": "view_issues add_issue_notes", "expires_in": 7200}
```

AIが実行するコマンド（ステップ2: API呼び出し）

```
$ python3 cli/redmine_api.py \
    --instance redmine.example.com \
    --scope "view_issues" \
    --api /issues/123.json
{"success": true, "data": {"issue": {"id": 123, "subject": "バグ修正"}}}
```

Claude Code: レスポンスメッセージ

```
https://redmine.example.com/issues/123 の内容はバグ修正です
```

ステップ1 でトークンの値は stdout に出力されず、スコープと有効期限のみが返ります。ステップ2 では `--scope` を指定するとキャッシュ済みトークンを内部で自動的に使用するため、AI の会話コンテキストにトークンが露出しません。

## まとめ

本記事で、**AIエージェントに安全にRedmineを操作させるために、ネイティブのOAuth2機能・ゲートウェイサーバ・ローカルのCLIツール・CLIツールを呼ぶためのスキルを用意し、それらが動作することを見てきました。**

ポイントは以下のとおりです。

* Redmine 6.1 の **OAuth2 ネイティブサポート**により、API キーに頼らないスコープ付きの認可が可能になった
* **`client_secret` はゲートウェイに集約し、CLI や AI には渡さない**構成にすることで、複数人での運用も安全に行える
* CLI ツールがトークンを内部に隠蔽することで、**AI の会話コンテキストへのトークン漏洩を防止**できる

今回記事で取り上げた題材に限らず、**短命トークンであってもAIのコンテキストに含まれないよう設計することは重要かもしれません。** みなさんも類似ツールを作る際に参考にしてください。
