---
id: "2026-05-27-oci-database-tools-mcp-server-を-mcp-remote-で-oauth-01"
title: "OCI Database Tools MCP Server を mcp-remote で OAuth 接続してみた — PAT廃止"
url: "https://qiita.com/asahide/items/9fa8de2196185b56daf0"
source: "qiita"
category: "claude-code"
tags: ["MCP", "qiita"]
date_published: "2026-05-27"
date_collected: "2026-05-28"
summary_by: "auto-rss"
query: ""
---

# 1. はじめに

## 1.1. 前回までのあらすじ

- [第一部前段](https://qiita.com/asahide/items/22a40ea09aed5edbd03e)では OCI Database Tools MCP Server を Claude Desktop に PAT（Personal Access Token）経由で接続しました。
- [第一部](https://qiita.com/asahide/items/a44172a297792ce8440e)では PAT の 60 分ハードリミットに詰まりました。OCI コンソール側で有効期限を延ばしても 60 分で切れるため、PAT での長期運用は困難です。

今回はその解決策として、`mcp-remote` を使ったブラウザ OAuth 認証（Authorization Code + PKCE）に切り替え、PAT ヘッダを完全に廃止しました。

:::note info
**PKCE（Proof Key for Code Exchange / [RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636)）** は、OAuth 2.0 のデスクトップアプリ向け拡張仕様です。クライアントがランダムな `code_verifier` を生成し、そのハッシュ値（`code_challenge`）を認可リクエストに含めます。`client_secret` を持たないパブリック型クライアントでも、認可コードの横取りを防いで安全にトークンを取得できます。
:::

## 1.2. 今回の検証ゴール

| # | 検証項目 | 確認方法 |
|---|---|---|
| 1 | `Authorization: Bearer <PAT>` ヘッダなしで Claude Desktop が OCI MCP Server に接続できるか | Claude Desktop の MCP セクションに接続済み表示 |
| 2 | ブラウザ OAuth フロー（Authorization Code + PKCE）が正常に完了するか | "Authorization successful!" 画面とトークンキャッシュの生成 |
| 3 | MCP ツールが正常に動作するか | `report_list` ツールの呼び出し成功 |

## 1.3. 結論（先出し）

- ✅ `mcp-remote` + OAuth で PAT ヘッダを完全撤廃できました
- ✅ OCI の「MCPクライアントの登録」専用 UI で**パブリック型クライアント**を作成するのが正解です
- ✅ スコープは Identity Domain が自動付与する `mcp` サフィックス込みで指定する必要があります
- ✅ 接続後は `%USERPROFILE%\.mcp-auth\` にトークンがキャッシュされ、次回以降は再ログイン不要です

# 2. 検証環境

| 項目 | 内容 |
|---|---|
| OS | Windows 11 Pro |
| Claude Desktop | 1.8555.2.0 |
| mcp-remote | 0.1.37 |
| OCI リージョン | ap-tokyo-1 |
| Identity Domain | Default（IDCS 形式） |

:::note info
`mcp-remote` のバージョンは `npx -y mcp-remote` で実行時に都度取得されます。本記事の接続ログでは `mcp-remote 0.1.37` を確認しています。
:::

# 3. OCI 側設定 — 「MCPクライアントの登録」専用 UI を使う

## 3.1. なぜ専用 UI を使うのか

OCI Identity Domain には一般的なアプリケーション作成 UI（機密・モバイル・エンタープライズなどの選択画面）とは別に、**「MCPクライアントの登録」という専用ページ**があります。

このページを使うと、MCP 接続に必要な設定がすべてあらかじめ入力された状態で登録できます。

## 3.2. 登録手順

**1. 「MCPクライアントの登録」ページを開く**

OCI コンソールから以下の手順で専用ページに移動します。

**OCI コンソール** → 「Database Tools」→ 「MCP サーバー」→ 対象の MCP サーバーを選択 → 「**クライアント**」タブ → 「**MCPクライアントの登録**」ボタン

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/54fdc6bf-6982-478d-917a-1fd2dcf5e5df.png)



**2. パブリック型を選択して必要項目を入力する**

| 項目 | 設定値 |
|---|---|
| クライアント種別 | **パブリック**（シークレットなし）|
| クライアント名 | 任意（例: `claude-desktop-mcp-public`）|
| スコープ | 自動入力された値をそのまま使用（変更不要）|
| リダイレクト URI | `http://localhost:8080/oauth/callback`（自動入力）|

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/8f579fe7-bada-40d9-931c-f97f1d2c19f8.png)



**3. 登録完了後に Client ID を控える**

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/5f56b30d-5f20-453e-bd31-6c442bfb909f.png)


「クライアント情報」タブに表示される **Client ID** をメモしておきます（次の手順で config に設定します）。

# 4. Claude Desktop 設定

## 4.1. claude_desktop_config.json（After 全文）

`%APPDATA%\Claude\claude_desktop_config.json` を開き、`mcpServers` セクションを以下に更新します。

```json
{
  "mcpServers": {
    "oci-dbtools-mcp": {
      "command": "C:\\PROGRA~1\\nodejs\\npx.cmd",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.dbtools.ap-tokyo-1.oci.oraclecloud.com/20250830/databaseToolsMcpServers/<MCP-Server-OCID>/actions/invoke",
        "8080",
        "--transport",
        "http-only",
        "--static-oauth-client-metadata",
        "{ \"scope\": \"urn:opc:dbtools:mcpserver:<MCP-Server-OCID>mcp:all\" }",
        "--static-oauth-client-info",
        "{ \"client_id\": \"<CLIENT_ID>\" }"
      ]
    }
  }
}
```

`<MCP-Server-OCID>` と `<CLIENT_ID>` を実際の値に置き換えてください。この設定は [Oracle 公式チュートリアル: トークンベース認証を使用したMCPサーバーへの接続](https://docs.oracle.com/ja-jp/iaas/database-tools/doc/tutorial.html#GUID-5EBF793E-CF57-4A4D-B9FC-EA5A2186FF5D) に基づく形式です。

| プレースホルダ | 説明 | 確認場所 |
|---|---|---|
| `<MCP-Server-OCID>` | OCI Database Tools MCP Server の OCID | OCI コンソール → Database Tools → MCP Servers → 対象サーバーの詳細 |
| `<CLIENT_ID>` | 3.2 章で確認した Client ID | 「MCPクライアントの登録」完了画面 |

:::note warn
スコープの書き方に注意してください。`--static-oauth-client-metadata` の `scope` 値は **`<MCP-Server-OCID>mcp:all`** の形式です。`<MCP-Server-OCID>` と `mcp:all` の間にスペースや区切り文字は入りません。詳しくは 6.1 章を参照してください。
:::

## 4.2. 引数の解説

| 引数 | 内容 |
|---|---|
| `-y mcp-remote <URL>` | npx で mcp-remote を起動し、接続先 MCP サーバー URL を渡す |
| `8080` | OAuth コールバックポートを 8080 に固定（リダイレクト URI と一致させる）|
| `--transport http-only` | HTTP ループバックを明示（RFC 8252 §7.3 準拠）|
| `--static-oauth-client-metadata` | DCR（動的クライアント登録）を使わずスコープを静的に指定する |
| `--static-oauth-client-info` | 事前登録済みの `client_id` を静的に渡す |

各引数の詳細仕様は [geelen/mcp-remote（GitHub）](https://github.com/geelen/mcp-remote) の README を参照してください。

:::note info
`C:\\PROGRA~1\\nodejs\\npx.cmd` は `C:\Program Files\nodejs\npx.cmd` の短縮形です。スペースを含むパスで起動エラーが出る場合の回避策として有効です。Node.js のインストール先が異なる場合は `where npx` で実際のパスを確認してください。
:::

# 5. 接続確認

## 5.1. Claude Desktop を再起動する

設定ファイルの保存後、Claude Desktop を完全に終了して再起動します。

## 5.2. ブラウザ OAuth フロー

起動直後にブラウザが自動で開き、OCI Identity Domain のログイン画面が表示されます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/3ba866d5-cba3-4cfa-a331-8c42405b7493.png)



OCI アカウントでサインインして「許可」すると、以下の画面が表示されます。

![スクリーンショット 2026-05-27 094637.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/1df5f0eb-6c9f-432d-9817-0f88ceb3cfbb.png)

このメッセージが出たらブラウザを閉じて Claude Desktop に戻ります。

## 5.3. 接続ログ（抜粋）

Claude Desktop の MCP ログには以下のような出力が記録されます（[実測] `results/oauth_success.log`）。

```
[17856] Discovering OAuth server configuration...
[17856] Discovered authorization server: https://idcs-<REDACTED>.identity.oraclecloud.com:443
[17856] Please authorize this client by visiting: https://idcs-<REDACTED>.../authorize?...
[17856] Browser opened automatically.
[17856] Auth code received, resolving promise
[17856] Completing authorization...
[17856] Connected to remote server using StreamableHTTPClientTransport
[17856] Proxy established successfully between local STDIO and remote StreamableHTTPClientTransport
```

`Connected to remote server using StreamableHTTPClientTransport` と `Proxy established successfully` が出力されれば接続成功です。

## 5.4. ツール一覧の確認

Claude Desktop の MCP セクションに `oci-dbtools-mcp` が接続状態で表示され、登録されているツールが利用可能になります。

![スクリーンショット 2026-05-27 094729.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2313926/2fa6d2a3-8244-47aa-b3a4-e1c3c4a361e2.png)

## 5.5. トークンキャッシュの確認

接続成功後、`%USERPROFILE%\.mcp-auth\mcp-remote-0.1.37\` 配下にトークンがキャッシュされます。

```
%USERPROFILE%\.mcp-auth\mcp-remote-0.1.37\
  <hash>_code_verifier.txt   ← PKCE の code_verifier
  <hash>_lock.json           ← プロセスロック
  <hash>_tokens.json         ← アクセストークン（有効期限付き）
```

`<hash>` は `MD5(MCP サーバー URL)` の値です。`tokens.json` のフィールド構成は以下のとおりです）。

| フィールド | 内容 |
|---|---|
| `access_token` | Bearer トークン本体 |
| `expires_in` | 有効期限（秒） |
| `token_type` | `Bearer` |

本検証の `tokens.json` には `refresh_token` は含まれていませんでした。そのため `access_token` が期限切れになると、Claude Desktop の次回起動時に再度ブラウザ認証が促されます。

offline_access スコープを追加すれば `refresh_token` も発行できます。その場合は `access_token` の有効期限が切れても有効期間内であればバックグラウンドで自動更新され、ブラウザを開かずに継続利用できますが、mcp でも利用できるかは未検証です。

# 6. 設定時の注意点

## 6.1. スコープに `mcp` サフィックスが必要

「MCPクライアントの登録」UI でスコープを確認すると、MCP サーバー OCID の末尾に **`mcp`** が自動付与された形になっています。

```
urn:opc:dbtools:mcpserver:ocid1...iu55hq/actions/invoke の場合:

  urn:opc:dbtools:mcpserver:ocid1...iu55hqmcp:all
                                          ^^^
                               Identity Domain が OCID 末尾に自動付与
```

`claude_desktop_config.json` の `scope` も**この `mcp` サフィックス込みの値をそのまま使用**してください。3.2 章で確認した「MCPクライアントの登録」UI のスコープ欄の値をコピーするのが確実です。`mcp` が欠けていると `invalid_scope` エラーになります。

## 6.2. ポート 8080 の競合（EADDRINUSE）

mcp-remote が異常終了した後もポート 8080 を解放しないプロセスが残ることがあります。その際は以下のコマンドでプロセスを確認・終了してください。（これ良くハマります・・・）

```powershell
# ポート 8080 を使用しているプロセスの PID を確認する
netstat -ano | findstr :8080

# PID を指定してプロセスを終了する（<PID> を実際の値に置き換える）
taskkill /PID <PID> /F
```

Claude Desktop を完全終了してから再起動すると、残留プロセスが自然に終了するケースもあります。


# 7. まとめ

`mcp-remote` + OAuth 認証への切り替えにより、60 分ごとの PAT 更新・再起動が不要になりました。

| 項目 | PAT 運用（変更前） | OAuth 運用（変更後） |
|---|---|---|
| 認証方式 | `Authorization: Bearer <PAT>`（固定ヘッダ） | OAuth 2.0 Authorization Code + PKCE |
| トークン管理 | PAT（60 分ハードリミット） | Identity Domain 発行トークン（キャッシュあり）|
| 再認証 | 60 分ごとに config 更新 + Claude Desktop 再起動 | 期限切れ時にブラウザが自動起動 |
| client_secret | 不要 | 不要（Public Client / PKCE のみ）|
| config への秘密情報 | PAT 本体を直書き | `client_id` のみ（シークレットなし）|


# 参考

- [チュートリアル: データベース・ツールMCPサーバーの設定とMCPクライアントとの統合](https://docs.oracle.com/ja-jp/iaas/database-tools/doc/tutorial.html)
- [データベース・ツール・モデル・コンテキスト・プロトコル(MCP)サーバーの操作](https://docs.oracle.com/ja-jp/iaas/database-tools/doc/working-database-tools-mcp-server.html)
- [MCPサーバーのトラブルシューティング](https://docs.oracle.com/ja-jp/iaas/autonomous-database-serverless/doc/troubleshoot-mcp-server.html)
- [geelen/mcp-remote — GitHub](https://github.com/geelen/mcp-remote)
- [RFC 8252 — OAuth 2.0 for Native Apps](https://datatracker.ietf.org/doc/html/rfc8252)
- [OCI Database Tools MCP Server を Claude Desktop につないでみた（第一部前段）](https://qiita.com/asahide/items/22a40ea09aed5edbd03e)
- [OCI の Personal Access Token は 60 分超を指定しても 60 分で切れる（第一部）](https://qiita.com/asahide/items/a44172a297792ce8440e)
