---
id: "2026-05-06-個人のローカルmcpサーバーを-claudeai-から呼ぶためのcloudflare-tunnel-01"
title: "個人のローカルMCPサーバーを claude.ai から呼ぶための、Cloudflare Tunnel + 自前OAuth 2.1実装"
url: "https://zenn.dev/hideakitamai/articles/6747c9bd56bd4f"
source: "zenn"
category: "claude-code"
tags: ["claude-code", "MCP", "API", "AI-agent", "zenn"]
date_published: "2026-05-06"
date_collected: "2026-05-07"
summary_by: "auto-rss"
query: ""
---

Mac mini上で動かしているローカルMCPサーバーを、claude.aiのCustom Connectorから呼べるようにしました。Cloudflare Tunnel経由でインターネット公開し、自前で書いたOAuth 2.1プロバイダで保護しています。

実装してみると、claude.ai Custom ConnectorのOAuthフローはRFCに準拠した実装が必要で、claude.ai側の既知バグも複数あり、素直に動かない箇所が多くありました。実装途中の試行錯誤と、最終的に動いた構成を整理します。

**この記事が役に立つ人**

* 個人ローカルで動いているMCPサーバーを claude.ai から呼びたい人
* claude.ai Custom Connector のOAuthフローを実装したいエンジニア
* Cloudflare Tunnel と Tailscale Funnel のどちらを選ぶか迷っている人
* 機微データを扱うMCPサーバーのセキュリティ設計を考えている人

# 結論：Cloudflare Tunnel + 自前OAuth 2.1 が最小構成

claude.ai Custom Connector は **OAuth 2.1 + DCR + PKCE** 前提で、シンプルなBearer tokenでは接続できません。マネージドOAuth Provider（Auth0等）を使う選択肢もありますが、外部依存ゼロを志向するなら **FastAPI + SQLite で200〜300行のミニOAuthサーバーを自前実装する** のが意外と現実的でした。

claude.ai側に既知バグが複数ある（後述）ため、フォールバック設計を最初から組み込むのが安全です。

# アーキテクチャ全体像

claude.ai → Cloudflare Tunnel → ローカルの OAuth Provider または MCP Server というシンプルな構成です。OAuth Provider と MCP Server は同じMac mini内で動き、Bearer tokenの検証情報をSQLiteで共有しています。

# 経路の選定で悩んだ3択

最初に経路選定で時間を使ったので、判断軸を整理しておきます。

## Tailscale Funnel: 個人利用なら最楽だが機微データには不適

セットアップが圧倒的に簡単で、5分で公開できます。ただし以下の機能が欠けています:

* アクセスログなし
* レート制限なし
* IP制限なし
* WAFなし

業務データや健康データのような機微情報を扱うなら、これらの欠落は致命的です。「便利さ」と「機微度」のトレードオフで、機微度が高い側を選ぶならTailscale Funnelは不採用になります。

## Cloudflare Workers + D1 にデータ集約: 個人OS哲学と乖離

Mac miniのSQLiteをCloudflare D1にミラーリングし、Workers経由で公開する案。レイテンシも安定し、認証もWorkersで処理できる。

ただし、今回のデータ規模（DB 2.5GB、426万レコード）で見ると以下の制約があります。

* **1データベースあたり10GB上限**: 今は収まりますが、観測継続で年数百MB増えるペースを考えると、長期で天井に当たる可能性
* **各D1データベースは内部で単一スレッド処理**: 1クエリずつ順次処理されるため、複数の重い集計クエリが並行すると待ち行列になる
* **rows\_readによる課金**: 426万行のテーブルにフルスキャンに近い分析クエリを投げると、1クエリあたり400万行超のrows\_readが計上される。Workers Paid planの無料枠（2,500万行/日）は1日5〜6回の集計クエリで埋まる計算
* **データ二重管理**: Mac mini上のSQLiteとD1の同期処理が常時必要

これに加えて、Mac miniにデータを集約という個人ローカル運用の哲学とも乖離するため、不採用にしました。

## Cloudflare Tunnel: 採用

Mac mini上のサービスにそのまま外部HTTPSアクセスを通せます。アクセスログ・WAF・レート制限すべて揃う。データはMac miniに留まる。

唯一のハードルは、**`*.cfargotunnel.com` ドメインで外部公開はできず、独自ドメインのCNAME設定が必須**な点です。これは事前知識として持っておかないと詰まります。

# Phase 2A: 認証なしでまず通す

最初は認証なしで外部HTTPSを通すフェーズから始めました。

## Cloudflare Tunnel 設定

```
# ~/.cloudflared/config.yml
tunnel: <tunnel-id-placeholder>
credentials-file: /Users/<USER>/.cloudflared/<tunnel-id>.json

ingress:
  # 127.0.0.1:9876 はMac mini内部のローカルループバック。外部からは到達不可
  - hostname: health.<your-domain>
    service: http://127.0.0.1:9876
    originRequest:
      httpHostHeader: 127.0.0.1:9876
  - service: http_status:404
```

## FastMCP を Streamable HTTP transport に切り替える

ローカル運用時は `stdio` transportが楽ですが、claude.aiから呼ぶには `streamable-http` transportが必要です。

```
from fastmcp import FastMCP

mcp = FastMCP("my-mcp-server")

# ツール定義...

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=9876)
```

ここまでで認証なしの状態で `tools/list` が外部HTTPSで通るようになりました。

```
curl -X POST https://health.<your-domain>/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

# 認証なしのまま claude.ai に登録しようとして詰まる

Phase 2A完了でcurlからは叩ける状態でしたが、claude.ai Custom Connectorに登録すると認証エラーで弾かれました。Custom ConnectorはOAuth flow前提のUIで、シンプルなBearer tokenを渡すオプションがありません。

Claude Code CLI なら `--header` で自前ヘッダを渡せますが、claude.ai web UIではOAuth 2.1 + DCR + PKCEを実装するしか道がない、という結論になりました。

# claude.ai Custom Connector の既知バグ調査

OAuth実装に踏み込む前に、claude.ai側の既知バグを調査しました。GitHub Issuesに複数のバグ報告があり、**実装しても動かない可能性**を踏まえる必要があります。

実装時点（2026年5月）で確認できた主な既知バグ:

* about:blank 無限ループ（OAuth flow開始後に画面が止まる）
* Claude Desktopアップデート以降 OAuth flow が起動しない事例
* OAuth discovery 完全スキップで silent failure になる事例
* OAuth flow 成功後に Bearer token が attach されないケース
* Claude Code CLI からは動くが claude.ai web からは動かないケース

これらを踏まえて、**フォールバック設計を最初から組み込む**方針を取りました。「自前OAuth 2.1実装が動かない場合は、別経路で目的を果たす」という二段構えです。具体的には、OAuth経路と並行して、定期的に集計サマリーをNotion等に書き出しておく経路を残しておく形です。

ベータ機能の上に本番運用を作るときの基本ですが、**動かない可能性を前提に設計する**のが安全です。

# claude.ai が要求するOAuthエンドポイント一式

claude.ai Custom ConnectorがOAuthフローで叩くエンドポイントは以下です。

| エンドポイント | RFC | 用途 |
| --- | --- | --- |
| `/.well-known/oauth-authorization-server` | RFC 8414 | Authorization Server Metadata（discovery） |
| `/.well-known/oauth-protected-resource` | RFC 9728 | Protected Resource Metadata |
| `/register` | RFC 7591 | Dynamic Client Registration |
| `/authorize` (GET) | OAuth 2.1 | ログイン画面表示 |
| `/authorize` (POST) | OAuth 2.1 | 認可コード発行 |
| `/token` | OAuth 2.1 | アクセストークン発行（PKCE検証必須） |

加えて、認証が必要なリソースの401レスポンスには `WWW-Authenticate: Bearer resource_metadata="..."` ヘッダーが必須です。

# 自前OAuth 2.1実装

FastAPI + SQLite で200〜300行のミニOAuthサーバーを書きました。

## Discovery エンドポイント

```
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import RedirectResponse
import sqlite3, secrets, hashlib, base64, time, os, json

OAUTH_DB = os.path.expanduser("~/myws/data/oauth.db")
PUBLIC_BASE_URL = os.environ["OAUTH_PUBLIC_BASE_URL"]
OWNER_PASSPHRASE = os.environ["OWNER_PASSPHRASE"]

app = FastAPI()

@app.get("/.well-known/oauth-authorization-server")
async def oauth_metadata():
    return {
        "issuer": PUBLIC_BASE_URL,
        "authorization_endpoint": f"{PUBLIC_BASE_URL}/authorize",
        "token_endpoint": f"{PUBLIC_BASE_URL}/token",
        "registration_endpoint": f"{PUBLIC_BASE_URL}/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "none"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["mcp"],
    }
```

`code_challenge_methods_supported` に `S256` を含めるのが必須。PKCEの code\_challenge 検証に使います。

## Dynamic Client Registration

```
@app.post("/register")
async def register_client(body: dict):
    """RFC 7591 Dynamic Client Registration"""
    client_id = secrets.token_urlsafe(16)
    client_secret = secrets.token_urlsafe(32)
    # SQLiteに永続化
    conn = sqlite3.connect(OAUTH_DB)
    conn.execute(
        "INSERT INTO clients (client_id, client_secret, redirect_uris) VALUES (?, ?, ?)",
        (client_id, client_secret, json.dumps(body.get("redirect_uris", [])))
    )
    conn.commit()
    conn.close()

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uris": body.get("redirect_uris", []),
        "client_secret_expires_at": 0,
        "token_endpoint_auth_method": "client_secret_post",
    }
```

claude.ai は事前登録なしの動的クライアント登録を要求します。

## 認可コード発行

```
@app.get("/authorize")
async def authorize_get(response_type: str, client_id: str, redirect_uri: str,
                        code_challenge: str, code_challenge_method: str,
                        state: str = "", scope: str = "mcp"):
    """ログイン画面（パスフレーズ入力フォーム）を表示"""
    # client_id 検証、HTML フォーム返却
    # フォームのhidden fieldにcode_challenge等を埋め込んでPOSTに引き継ぐ
    ...

@app.post("/authorize")
async def authorize_post(passphrase: str = Form(...),
                         client_id: str = Form(...),
                         redirect_uri: str = Form(...),
                         code_challenge: str = Form(...),
                         state: str = Form("")):
    """パスフレーズ検証 → 認可コード発行 → redirect_uri にリダイレクト"""
    if not secrets.compare_digest(passphrase, OWNER_PASSPHRASE):
        raise HTTPException(401, "Invalid passphrase")

    code = secrets.token_urlsafe(32)
    # auth_codes テーブルに保存（10分TTL、code_challenge記録）
    conn = sqlite3.connect(OAUTH_DB)
    conn.execute("""
        INSERT INTO auth_codes
        (code, client_id, redirect_uri, code_challenge, expires_at)
        VALUES (?, ?, ?, ?, ?)
    """, (code, client_id, redirect_uri, code_challenge,
          int(time.time()) + 600))
    conn.commit()
    conn.close()

    return RedirectResponse(f"{redirect_uri}?code={code}&state={state}", 302)
```

個人利用なので、ユーザー認証はパスフレーズ1つで済ませています。複数ユーザーの場合はここに通常のログイン認証を入れます。

## トークン発行（PKCE検証）

```
@app.post("/token")
async def token_endpoint(grant_type: str = Form(...),
                         code: str = Form(None),
                         client_id: str = Form(...),
                         client_secret: str = Form(None),
                         code_verifier: str = Form(None),
                         refresh_token: str = Form(None)):
    """access_token 発行 (PKCE検証必須)"""
    if grant_type == "authorization_code":
        # PKCE: SHA256(code_verifier) を base64url して code_challenge と比較
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode()

        # auth_codeから code_challenge取得して比較
        conn = sqlite3.connect(OAUTH_DB)
        row = conn.execute(
            "SELECT code_challenge, expires_at FROM auth_codes WHERE code = ?",
            (code,)
        ).fetchone()
        if not row or row[1] < time.time():
            raise HTTPException(400, "Invalid or expired code")
        if not secrets.compare_digest(challenge, row[0]):
            raise HTTPException(400, "PKCE verification failed")

        # 認可コードを使い切り（再利用防止）
        conn.execute("DELETE FROM auth_codes WHERE code = ?", (code,))

        access_token = secrets.token_urlsafe(48)
        refresh_token_val = secrets.token_urlsafe(48)
        # tokens テーブルに保存
        ...
        conn.commit()
        conn.close()

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 28800,
            "refresh_token": refresh_token_val,
            "scope": "mcp",
        }
    elif grant_type == "refresh_token":
        # リフレッシュトークン検証 + ローテーション
        ...
```

PKCE検証部分は地味ですが必須。`code_verifier` を SHA256 してbase64urlエンコードした値が `code_challenge` と一致するか確認します。一致しなければ拒否。

# FastMCPに Bearer token middleware を組み込む

OAuth Providerが発行したBearer tokenを、MCPサーバー側で検証する処理を入れます。

```
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers

class OAuthMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        headers = get_http_headers()
        auth = headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            raise ToolError("Authentication required")
        token = auth.removeprefix("Bearer ").strip()
        if not validate_bearer_token(token):  # SQLite lookup
            raise ToolError("Invalid or expired token")
        return await call_next(context)

mcp.add_middleware(OAuthMiddleware())
```

`validate_bearer_token` は SQLite を見に行って、トークンの有効期限・スコープを確認します。OAuth Provider 側のSQLiteを共有する形にしているので、別プロセスのMCPサーバーから検証できます。

# LaunchAgent 化

cloudflared と OAuth Provider と MCP Server を LaunchAgent で常駐化します。SSHセッションから起動するとMac miniの Keychain ロックで認証エラーになるため、自動ログイン構成 + LaunchAgent経由起動が必須です。

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.myws.cloudflared</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/cloudflared</string>
        <string>tunnel</string>
        <string>run</string>
        <string>my-tunnel-name</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

OAuth Provider と MCP Server も同様にLaunchAgent化します。

# 動作確認

curl で各エンドポイントを順に叩いて確認します。

```
# 1. discovery
curl https://health.<your-domain>/.well-known/oauth-authorization-server | jq

# 2. 認証なしで401確認 + WWW-Authenticate ヘッダー
curl -X POST https://health.<your-domain>/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' -i

# 3. claude.ai Custom Connector 登録
# Settings → Connectors → Add custom connector
#   Name: my-mcp
#   URL: https://health.<your-domain>/mcp
#   Advanced settings は空のまま（DCR対応のため）
```

claude.ai 側で登録後、初回アクセス時にOAuth フローが起動します。パスフレーズを入力してログインすると、Bearer tokenが発行され、以降のMCPツール呼び出しが認証付きで動きます。

# 実運用での所感

claude.ai 経由で複雑な集計クエリを投げて、200ms以内で応答が返ってくる体験は、**集計レイヤーを経由する設計とは質的に違う**と感じます。

* 集計レイヤー経由：あらかじめ用意した指標しか見れない、定型レポート的
* 直接アクセス：その場で問いを変えられる、対話の流れの中で深掘りできる

「個人ローカルにあるデータをclaude.aiから安全に使う」というアーキテクチャは、健康データに限らず、家計、設備管理、業務データなど他のドメインにも転用可能です。今回構築したOAuth providerは別のMCPサーバーにも流用できます（サブドメインを変えるだけ）。

# 経営判断・運用上の整理

実装を通じて固まった判断軸を整理します。

* **Tailscale Funnel の利便性 vs Cloudflare のセキュリティ層**: 個人利用ならTailscale Funnelが圧倒的に楽。ただし機微情報を扱うならアクセスログ・WAF・レート制限のあるCloudflare一択
* **マネージドOAuth Provider vs 自前実装**: Auth0等は30分でセットアップ完了で楽。ただし「外部依存ゼロ」を哲学とするなら、自前最小実装は200〜300行で書けるので意外と現実的
* **ベータ機能の上に本番運用を作る判断**: claude.ai Custom Connector のような新機能の不安定性に対するヘッジとして、フォールバック実装を最初から組み込む。フォールバック自体が独立した価値を持つ形に位置づけ直すと、二度手間にならない

# まとめ

claude.ai Custom Connector に個人ローカルMCPを繋ぐ最小構成は、Cloudflare Tunnel + 自前OAuth 2.1 実装でした。

ハマりどころは、`*.cfargotunnel.com` の外部公開不可、Uvicorn Host header validation、claude.ai 側の既知バグ。OAuth実装はFastAPI + SQLiteで200〜300行。Bearer token middleware は FastMCP の `add_middleware` で組み込めます。

「個人がデータとAI活用環境を自分で持つ」という設計は、SaaS型AIに依存する設計とは別の選択肢として現実的に動かせる時代になっていると思います。

# 参考リンク

---

筆者：玉井秀明（Hide Tamai）

BAIOX取締役CMO / Goaico共同代表。医療AIと中小企業向けAI導入支援の両面でAI事業に関わっています。
